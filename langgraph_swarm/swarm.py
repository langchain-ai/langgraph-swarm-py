from types import UnionType
from typing import Literal, Union, cast, get_args, get_origin
from warnings import warn

from langgraph._internal._typing import DeprecatedKwargs
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.pregel import Pregel
from typing_extensions import Any, TypeVar, Unpack

from langgraph_swarm.handoff import get_handoff_destinations


class SwarmState(MessagesState):
    """State schema for the multi-agent swarm."""

    # NOTE: this state field is optional and is not expected to be provided by the user.
    # If a user does provide it, the graph will start from the specified active agent.
    # If active agent is typed as a `str`, we turn it into enum of all active agent names.
    active_agent: str | None


StateSchema = TypeVar("StateSchema", bound=SwarmState)
StateSchemaType = type[StateSchema]


def _update_state_schema_agent_names(
    state_schema: StateSchemaType,
    agent_names: list[str],
) -> StateSchemaType:
    """Update the state schema to use Literal with agent names for 'active_agent'."""
    active_agent_annotation = state_schema.__annotations__.get("active_agent")
    if active_agent_annotation is None:
        msg = "Missing required key 'active_agent' in state_schema"
        raise ValueError(msg)

    # Check if the annotation is str or Optional[str]
    is_str_type = active_agent_annotation is str
    is_optional_str = (
        get_origin(active_agent_annotation) is Union
        and len(get_args(active_agent_annotation)) == 2
        and str in get_args(active_agent_annotation)
        and type(None) in get_args(active_agent_annotation)
    ) or (
        get_origin(active_agent_annotation) is UnionType
        and len(get_args(active_agent_annotation)) == 2
        and str in get_args(active_agent_annotation)
        and type(None) in get_args(active_agent_annotation)
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
    literal_type = cast("type", Literal.__getitem__(tuple(agent_names)))

    # If it was Optional[str], make it Optional[Literal[...]]
    if is_optional_str:
        updated_schema.__annotations__["active_agent"] = literal_type | None
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

    Example:
        ```python
        from langchain.checkpoint.memory import InMemorySaver
        from langchain.agents import create_agent
        from langgraph.graph import StateGraph
        from langgraph_swarm import SwarmState, create_handoff_tool, add_active_agent_router

        def add(a: int, b: int) -> int:
            '''Add two numbers'''
            return a + b

        alice = create_agent(
            "openai:gpt-4o",
            tools=[
                add,
                create_handoff_tool(
                    agent_name="Bob",
                    description="Transfer to Bob",
                ),
            ],
            system_prompt="You are Alice, an addition expert.",
            name="Alice",
        )

        bob = create_agent(
            "openai:gpt-4o",
            tools=[
                create_handoff_tool(
                    agent_name="Alice",
                    description="Transfer to Alice, she can help with math",
                ),
            ],
            system_prompt="You are Bob, you speak like a pirate.",
            name="Bob",
        )

        checkpointer = InMemorySaver()
        workflow = (
            StateGraph(SwarmState)
            .add_node(alice, destinations=("Bob",))
            .add_node(bob, destinations=("Alice",))
        )
        # this is the router that enables us to keep track of the last active agent
        workflow = add_active_agent_router(
            builder=workflow,
            route_to=["Alice", "Bob"],
            default_active_agent="Alice",
        )

        # compile the workflow
        app = workflow.compile(checkpointer=checkpointer)

        config = {"configurable": {"thread_id": "1"}}
        turn_1 = app.invoke(
            {"messages": [{"role": "user", "content": "i'd like to speak to Bob"}]},
            config,
        )
        turn_2 = app.invoke(
            {"messages": [{"role": "user", "content": "what's 5 + 7?"}]},
            config,
        )
        ```

    """
    channels = builder.schemas[builder.state_schema]
    if "active_agent" not in channels:
        msg = "Missing required key 'active_agent' in in builder's state_schema"
        raise ValueError(msg)

    if default_active_agent not in route_to:
        msg = f"Default active agent '{default_active_agent}' not found in routes {route_to}"
        raise ValueError(
            msg,
        )

    def route_to_active_agent(state: dict) -> str:
        return cast("str", state.get("active_agent", default_active_agent))

    builder.add_conditional_edges(START, route_to_active_agent, path_map=route_to)
    return builder


def create_swarm(  # noqa: D417
    agents: list[Pregel],
    *,
    default_active_agent: str,
    state_schema: StateSchemaType = SwarmState,
    context_schema: type[Any] | None = None,
    **deprecated_kwargs: Unpack[DeprecatedKwargs],
) -> StateGraph:
    """Create a multi-agent swarm.

    Args:
        agents: List of agents to add to the swarm
            An agent can be a LangGraph [CompiledStateGraph](https://langchain-ai.github.io/langgraph/reference/graphs/#langgraph.graph.state.CompiledStateGraph),
            a functional API [workflow](https://langchain-ai.github.io/langgraph/reference/func/#langgraph.func.entrypoint),
            or any other [Pregel](https://langchain-ai.github.io/langgraph/reference/pregel/#langgraph.pregel.Pregel) object.
        default_active_agent: Name of the agent to route to by default (if no agents are currently active).
        state_schema: State schema to use for the multi-agent graph.
        context_schema: Specifies the schema for the context object that will be passed to the workflow.

    Returns:
        A multi-agent swarm StateGraph.

    Example:
        ```python
        from langgraph.checkpoint.memory import InMemorySaver
        from langchain.agents import create_agent
        from langgraph_swarm import create_handoff_tool, create_swarm

        def add(a: int, b: int) -> int:
            '''Add two numbers'''
            return a + b

        alice = create_agent(
            "openai:gpt-4o",
            tools=[
                add,
                create_handoff_tool(
                    agent_name="Bob",
                    description="Transfer to Bob",
                ),
            ],
            system_prompt="You are Alice, an addition expert.",
            name="Alice",
        )

        bob = create_agent(
            "openai:gpt-4o",
            tools=[
                create_handoff_tool(
                    agent_name="Alice",
                    description="Transfer to Alice, she can help with math",
                ),
            ],
            system_prompt="You are Bob, you speak like a pirate.",
            name="Bob",
        )

        checkpointer = InMemorySaver()
        workflow = create_swarm(
            [alice, bob],
            default_active_agent="Alice"
        )
        app = workflow.compile(checkpointer=checkpointer)

        config = {"configurable": {"thread_id": "1"}}
        turn_1 = app.invoke(
            {"messages": [{"role": "user", "content": "i'd like to speak to Bob"}]},
            config,
        )
        turn_2 = app.invoke(
            {"messages": [{"role": "user", "content": "what's 5 + 7?"}]},
            config,
        )
        ```

    """
    if (config_schema := deprecated_kwargs.get("config_schema")) is not None:
        warn(
            "`config_schema` is deprecated. Please use `context_schema` instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        context_schema = cast("type[Any] | None", config_schema)

    active_agent_annotation = state_schema.__annotations__.get("active_agent")
    if active_agent_annotation is None:
        msg = "Missing required key 'active_agent' in state_schema"
        raise ValueError(msg)

    if not agents:
        msg = "agents list cannot be empty"
        raise ValueError(msg)

    agent_names = [agent.name for agent in agents]

    if default_active_agent not in agent_names:
        msg = f"Default active agent '{default_active_agent}' not found in agent names {agent_names}"
        raise ValueError(msg)

    state_schema = _update_state_schema_agent_names(state_schema, agent_names)
    builder = StateGraph(state_schema, context_schema)
    add_active_agent_router(
        builder,
        route_to=agent_names,
        default_active_agent=default_active_agent,
    )
    for agent in agents:
        builder.add_node(
            agent.name,
            # We need to update the type signatures in add_node to match
            # the fact that more flexible Pregel objects are allowed.
            agent,
            destinations=tuple(
                # Need to update implementation to support Pregel objects
                get_handoff_destinations(agent)  # type: ignore[arg-type]
            ),
        )

    return builder
