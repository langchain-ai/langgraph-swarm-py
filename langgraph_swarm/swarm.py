from langgraph.graph import START, MessagesState, StateGraph
from langgraph.pregel import Pregel
from typing_extensions import Any, Literal, Optional, Type, TypeVar, Union, get_args, get_origin

from langgraph_swarm.handoff import get_handoff_destinations


class SwarmState(MessagesState):
    """State schema for the multi-agent swarm."""

    # NOTE: this state field is optional and is not expected to be provided by the user.
    # If a user does provide it, the graph will start from the specified active agent.
    # If active agent is typed as a `str`, we turn it into enum of all active agent names.
    active_agent: Optional[str]


StateSchema = TypeVar("StateSchema", bound=SwarmState)
StateSchemaType = Type[StateSchema]


def _update_state_schema_agent_names(
    state_schema: StateSchemaType, agent_names: list[str]
) -> StateSchemaType:
    """Update the state schema to use Literal with agent names for 'active_agent'."""

    active_agent_annotation = state_schema.__annotations__["active_agent"]

    # Check if the annotation is str or Optional[str]
    is_str_type = active_agent_annotation is str
    is_optional_str = (
        get_origin(active_agent_annotation) is Union and get_args(active_agent_annotation)[0] is str
    )

    # We only update if the 'active_agent' is a str or Optional[str]
    if not (is_str_type or is_optional_str):
        return state_schema

    updated_schema = type(
        f"{state_schema.__name__}",
        (state_schema,),
        {"__annotations__": {**state_schema.__annotations__}},
    )

    # Create the Literal type with agent names
    literal_type = Literal.__getitem__(tuple(agent_names))

    # If it was Optional[str], make it Optional[Literal[...]]
    if is_optional_str:
        updated_schema.__annotations__["active_agent"] = Optional[literal_type]
    else:
        updated_schema.__annotations__["active_agent"] = literal_type

    return updated_schema


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
    agents: list[Pregel],
    *,
    default_active_agent: str,
    state_schema: StateSchemaType = SwarmState,
    config_schema: Type[Any] | None = None,
) -> StateGraph:
    """Create a multi-agent swarm.

    Args:
        agents: List of agents to add to the swarm
        default_active_agent: Name of the agent to route to by default (if no agents are currently active).
        state_schema: State schema to use for the multi-agent graph.
        config_schema: An optional schema for configuration.
            Use this to expose configurable parameters via supervisor.config_specs.

    Returns:
        A multi-agent swarm StateGraph.
    """
    active_agent_annotation = state_schema.__annotations__.get("active_agent")
    if active_agent_annotation is None:
        raise ValueError("Missing required key 'active_agent' in state_schema")

    agent_names = [agent.name for agent in agents]
    state_schema = _update_state_schema_agent_names(state_schema, agent_names)
    builder = StateGraph(state_schema, config_schema)
    add_active_agent_router(
        builder,
        route_to=agent_names,
        default_active_agent=default_active_agent,
    )
    for agent in agents:
        builder.add_node(
            agent.name,
            agent,
            destinations=tuple(get_handoff_destinations(agent)),
        )

    return builder
