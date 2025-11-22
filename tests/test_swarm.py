from collections.abc import Callable, Sequence
from typing import TYPE_CHECKING, Any

from langchain.agents import AgentState, create_agent
from langchain.chat_models import BaseChatModel
from langchain.messages import AIMessage
from langchain.tools import BaseTool
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from langchain_core.messages.base import BaseMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langgraph.checkpoint.memory import MemorySaver

from langgraph_swarm import create_handoff_tool, create_swarm

if TYPE_CHECKING:
    from langchain_core.runnables.config import RunnableConfig


class FakeChatModel(BaseChatModel):
    idx: int = 0
    responses: list[BaseMessage]

    @property
    def _llm_type(self) -> str:
        return "fake-tool-call-model"

    def _generate(
        self,
        messages: list[BaseMessage],
        stop: list[str] | None = None,
        run_manager: CallbackManagerForLLMRun | None = None,
        **kwargs: Any,
    ) -> ChatResult:
        generation = ChatGeneration(message=self.responses[self.idx])
        self.idx += 1
        return ChatResult(generations=[generation])

    def bind_tools(
        self,
        tools: Sequence[dict[str, Any] | type | Callable[..., Any] | BaseTool],
        *,
        tool_choice: str | None = None,
        **kwargs: Any,
    ) -> "FakeChatModel":
        return self


def test_basic_swarm() -> None:
    # Create fake responses for the model
    recorded_messages = [
        AIMessage(
            content="",
            name="Alice",
            tool_calls=[
                {
                    "name": "transfer_to_bob",
                    "args": {},
                    "id": "call_1LlFyjm6iIhDjdn7juWuPYr4",
                },
            ],
        ),
        AIMessage(
            content="Ahoy, matey! Bob the pirate be at yer service. What be ye needin' help with today on the high seas? Arrr!",
            name="Bob",
        ),
        AIMessage(
            content="",
            name="Bob",
            tool_calls=[
                {
                    "name": "transfer_to_alice",
                    "args": {},
                    "id": "call_T6pNmo2jTfZEK3a9avQ14f8Q",
                },
            ],
        ),
        AIMessage(
            content="",
            name="Alice",
            tool_calls=[
                {
                    "name": "add",
                    "args": {
                        "a": 5,
                        "b": 7,
                    },
                    "id": "call_4kLYO1amR2NfhAxfECkALCr1",
                },
            ],
        ),
        AIMessage(
            content="The sum of 5 and 7 is 12.",
            name="Alice",
        ),
    ]

    model = FakeChatModel(responses=recorded_messages)  # type: ignore[arg-type]

    def add(a: int, b: int) -> int:
        """Add two numbers."""
        return a + b

    alice: Any = create_agent(
        model,
        tools=[add, create_handoff_tool(agent_name="Bob")],
        system_prompt="You are Alice, an addition expert.",
        name="Alice",
    )

    bob: Any = create_agent(
        model,
        tools=[
            create_handoff_tool(
                agent_name="Alice",
                description="Transfer to Alice, she can help with math",
            ),
        ],
        system_prompt="You are Bob, you speak like a pirate.",
        name="Bob",
    )

    checkpointer = MemorySaver()
    workflow = create_swarm([alice, bob], default_active_agent="Alice")  # type: ignore[list-item]
    app = workflow.compile(checkpointer=checkpointer)

    config: RunnableConfig = {"configurable": {"thread_id": "1"}}
    turn_1 = app.invoke(
        {  # type: ignore[arg-type]
            "messages": [{"role": "user", "content": "i'd like to speak to Bob"}]
        },
        config,
    )

    # Verify turn 1 results
    assert len(turn_1["messages"]) == 4
    assert turn_1["messages"][-2].content == "Successfully transferred to Bob"
    assert turn_1["messages"][-1].content == recorded_messages[1].content
    assert turn_1["active_agent"] == "Bob"

    turn_2 = app.invoke(
        {  # type: ignore[arg-type]
            "messages": [{"role": "user", "content": "what's 5 + 7?"}]
        },
        config,
    )

    # Verify turn 2 results
    assert len(turn_2["messages"]) == 10
    assert turn_2["messages"][-4].content == "Successfully transferred to Alice"
    assert turn_2["messages"][-2].content == "12"
    assert turn_2["messages"][-1].content == recorded_messages[4].content
    assert turn_2["active_agent"] == "Alice"


def test_basic_swarm_pydantic() -> None:
    """Test a basic swarm with Pydantic state schema."""

    class SwarmState(AgentState):
        """State schema for the multi-agent swarm."""

        # NOTE: this state field is optional and is not expected to be provided by the
        # user.
        # If a user does provide it, the graph will start from the specified active
        # agent.
        # If active agent is typed as a `str`, we turn it into enum of all active agent
        # names.
        active_agent: str | None = None  # type: ignore[misc]

    recorded_messages = [
        AIMessage(
            content="",
            name="Alice",
            tool_calls=[
                {
                    "name": "transfer_to_bob",
                    "args": {},
                    "id": "call_1LlFyjm6iIhDjdn7juWuPYr4",
                },
            ],
        ),
        AIMessage(
            content="Ahoy, matey! Bob the pirate be at yer service. What be ye needin' "
            "help with today on the high seas? Arrr!",
            name="Bob",
        ),
        AIMessage(
            content="",
            name="Bob",
            tool_calls=[
                {
                    "name": "transfer_to_alice",
                    "args": {},
                    "id": "call_T6pNmo2jTfZEK3a9avQ14f8Q",
                },
            ],
        ),
        AIMessage(
            content="",
            name="Alice",
            tool_calls=[
                {
                    "name": "add",
                    "args": {
                        "a": 5,
                        "b": 7,
                    },
                    "id": "call_4kLYO1amR2NfhAxfECkALCr1",
                },
            ],
        ),
        AIMessage(
            content="The sum of 5 and 7 is 12.",
            name="Alice",
        ),
    ]

    model = FakeChatModel(responses=recorded_messages)  # type: ignore[arg-type]

    def add(a: int, b: int) -> int:
        """Add two numbers."""
        return a + b

    alice = create_agent(
        model,
        tools=[add, create_handoff_tool(agent_name="Bob")],
        system_prompt="You are Alice, an addition expert.",
        name="Alice",
        state_schema=SwarmState,
    )

    bob = create_agent(
        model,
        tools=[
            create_handoff_tool(
                agent_name="Alice",
                description="Transfer to Alice, she can help with math",
            ),
        ],
        system_prompt="You are Bob, you speak like a pirate.",
        name="Bob",
        state_schema=SwarmState,
    )

    checkpointer = MemorySaver()
    workflow = create_swarm([alice, bob], default_active_agent="Alice")  # type: ignore[list-item]
    app = workflow.compile(checkpointer=checkpointer)

    config: RunnableConfig = {"configurable": {"thread_id": "1"}}
    turn_1 = app.invoke(
        {  # type: ignore[arg-type]
            "messages": [{"role": "user", "content": "i'd like to speak to Bob"}]
        },
        config,
    )

    # Verify turn 1 results
    assert len(turn_1["messages"]) == 4
    assert turn_1["messages"][-2].content == "Successfully transferred to Bob"
    assert turn_1["messages"][-1].content == recorded_messages[1].content
    assert turn_1["active_agent"] == "Bob"

    turn_2 = app.invoke(
        {  # type: ignore[arg-type]
            "messages": [{"role": "user", "content": "what's 5 + 7?"}]
        },
        config,
    )

    # Verify turn 2 results
    assert len(turn_2["messages"]) == 10
    assert turn_2["messages"][-4].content == "Successfully transferred to Alice"
    assert turn_2["messages"][-2].content == "12"
    assert turn_2["messages"][-1].content == recorded_messages[4].content
    assert turn_2["active_agent"] == "Alice"
