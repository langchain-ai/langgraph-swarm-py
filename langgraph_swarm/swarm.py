from typing import Type, TypeVar

from langgraph.graph import START, MessagesState, StateGraph
from langgraph.graph.state import CompiledStateGraph

from langgraph_swarm.handoff import get_handoff_destinations


class SwarmState(MessagesState):
    """State schema for the multi-agent swarm."""

    active_agent: str


StateSchema = TypeVar("StateSchema", bound=SwarmState)
StateSchemaType = Type[StateSchema]


def add_active_agent_router(
    builder: StateGraph,
    *,
    route_to: list[str],
    default_active_agent: str,
) -> StateGraph:
    """Add a router to the currently active agent to the StateGraph.

    Args:
        builder: The graph builder (StateGraph) to add the router to.
        route_to: A list of agent (node) names to route to.
        default_active_agent: Name of the agent to route to by default (if no agents are currently active).

    Returns:
        StateGraph with the router added.
    """
    channels = builder.schemas[builder.schema]
    if "active_agent" not in channels:
        raise ValueError("Missing required key 'active_agent' in in builder's state_schema")

    if default_active_agent not in route_to:
        raise ValueError(
            f"Default active agent '{default_active_agent}' not found in routes {route_to}"
        )

    def route_to_active_agent(state: dict):
        return state.get("active_agent", default_active_agent)

    builder.add_conditional_edges(START, route_to_active_agent, path_map=route_to)
    return builder


def create_swarm(
    agents: list[CompiledStateGraph],
    *,
    default_active_agent: str,
    state_schema: StateSchemaType = SwarmState,
) -> StateGraph:
    """Create a multi-agent swarm.

    Args:
        agents: List of agents to add to the swarm
        default_active_agent: Name of the agent to route to by default (if no agents are currently active).
        state_schema: State schema to use for the multi-agent graph.

    Returns:
        A multi-agent swarm StateGraph.
    """
    if "active_agent" not in state_schema.__annotations__:
        raise ValueError("Missing required key 'active_agent' in state_schema")

    builder = StateGraph(state_schema)
    add_active_agent_router(
        builder,
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
