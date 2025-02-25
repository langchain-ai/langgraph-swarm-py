def test_import() -> None:
    """Test that the code can be imported"""
    from langgraph_swarm import (  # noqa: F401
        add_active_agent_router,
        create_handoff_tool,
        create_swarm,
    )
