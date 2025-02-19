from typing import Callable

from langgraph.graph import StateGraph, START
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt.chat_agent_executor import (
    AgentState,
    StateSchemaType,
)

from langgraph_swarm.handoff import get_handoff_destinations


def _make_entrypoint_router(entrypoint: str) -> Callable[[dict], dict]:
    def route_to_active_agent(state: dict):
        return state.get("active_agent", entrypoint)

    return route_to_active_agent


class SwarmState(AgentState):
    """State schema for the multi-agent swarm."""

    active_agent: str


def create_swarm(
    agents: list[CompiledStateGraph],
    *,
    entrypoint: str,
    state_schema: StateSchemaType = SwarmState,
) -> StateGraph:
    """Create a multi-agent swarm.

    Args:
        agents: List of agents to manage
        entrypoint: Name of the entrypoint agent
        state_schema: State schema to use for the multi-agent graph.
    """
    if "active_agent" not in state_schema.__annotations__:
        raise ValueError("Missing required key 'active_agent' in state_schema")

    builder = StateGraph(state_schema)
    builder.add_conditional_edges(
        START,
        _make_entrypoint_router(entrypoint),
        path_map=[agent.name for agent in agents],
    )
    for agent in agents:
        builder.add_node(
            agent.name,
            agent,
            destinations=tuple(get_handoff_destinations(agent)),
        )

    return builder
