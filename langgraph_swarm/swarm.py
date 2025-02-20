from typing import Callable, Type, TypeVar

from langgraph.graph import StateGraph, MessagesState, START
from langgraph.graph.state import CompiledStateGraph
from langgraph.utils.runnable import RunnableLike

from langgraph_swarm.handoff import get_handoff_destinations


class SwarmState(MessagesState):
    """State schema for the multi-agent swarm."""

    active_agent: str


StateSchema = TypeVar("StateSchema", bound=SwarmState)
StateSchemaType = Type[StateSchema]


def add_active_agent_router(
    builder: StateGraph,
    *,
    route_from: str,
    route_to: list[str],
    default_active_agent: str,
) -> StateGraph:
    """Add a router to the currently active agent to the StateGraph.

    Args:
        builder: The graph builder (StateGraph) to add the router to.
        route_from: Name of the node to route from.
        route_to: A list of agent (node) names to route to.
        default_active_agent: Name of the agent to route to by default (if no agents are currently active).

    Returns:
        StateGraph with the router added.
    """
    channels = builder.schemas[builder.schema]
    if "active_agent" not in channels:
        raise ValueError(
            "Missing required key 'active_agent' in in builder's state_schema"
        )

    if default_active_agent not in route_to:
        raise ValueError(
            f"Default active agent '{default_active_agent}' not found in routes {route_to}"
        )

    def route_to_active_agent(state: dict):
        return state.get("active_agent", default_active_agent)

    builder.add_conditional_edges(route_from, route_to_active_agent, path_map=route_to)
    return builder


def create_swarm(
    agents: list[CompiledStateGraph],
    *,
    default_active_agent: str,
    start_from: str = START,
    state_schema: StateSchemaType = SwarmState,
) -> StateGraph:
    """Create a multi-agent swarm.

    Args:
        agents: List of agents to add to the swarm
        default_active_agent: Name of the agent to route to by default (if no agents are currently active).
        start_from: Name of the node to route to the active agent from (defaults to start of the graph).
            Useful if you need to add non-agent nodes to the beginning of the graph and
            route to the active agent after those nodes.
        state_schema: State schema to use for the multi-agent graph.

    Returns:
        A multi-agent swarm StateGraph.
    """
    if "active_agent" not in state_schema.__annotations__:
        raise ValueError("Missing required key 'active_agent' in state_schema")

    builder = StateGraph(state_schema)
    add_active_agent_router(
        builder,
        route_from=start_from,
        route_to=[agent.name for agent in agents],
        default_active_agent=default_active_agent,
    )
    for agent in agents:
        builder.add_node(
            agent.name,
            agent,
            destinations=tuple(get_handoff_destinations(agent)),
        )

    return builder
