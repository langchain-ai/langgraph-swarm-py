from typing import Optional

from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

from langgraph_swarm import create_handoff_tool, create_swarm


class FakeChatModel(BaseChatModel):
    idx: int = 0
    responses: list[BaseMessage]

    @property
    def _llm_type(self) -> str:
        return "fake-tool-call-model"

    def _generate(
        self,
        messages: list[BaseMessage],
        stop: Optional[list[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs,
    ) -> ChatResult:
        generation = ChatGeneration(message=self.responses[self.idx])
        self.idx += 1
        return ChatResult(generations=[generation])

    def bind_tools(self, tools: list[any]) -> "FakeChatModel":
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
                }
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
                }
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
                }
            ],
        ),
        AIMessage(
            content="The sum of 5 and 7 is 12.",
            name="Alice",
        ),
    ]

    model = FakeChatModel(responses=recorded_messages)

    def add(a: int, b: int) -> int:
        """Add two numbers"""
        return a + b

    alice = create_react_agent(
        model,
        [add, create_handoff_tool(agent_name="Bob")],
        prompt="You are Alice, an addition expert.",
        name="Alice",
    )

    bob = create_react_agent(
        model,
        [
            create_handoff_tool(
                agent_name="Alice", description="Transfer to Alice, she can help with math"
            )
        ],
        prompt="You are Bob, you speak like a pirate.",
        name="Bob",
    )

    checkpointer = MemorySaver()
    workflow = create_swarm([alice, bob], default_active_agent="Alice")
    app = workflow.compile(checkpointer=checkpointer)

    config = {"configurable": {"thread_id": "1"}}
    turn_1 = app.invoke(
        {"messages": [{"role": "user", "content": "i'd like to speak to Bob"}]},
        config,
    )

    # Verify turn 1 results
    assert len(turn_1["messages"]) == 4
    assert turn_1["messages"][-2].content == "Successfully transferred to Bob"
    assert turn_1["messages"][-1].content == recorded_messages[1].content
    assert turn_1["active_agent"] == "Bob"

    turn_2 = app.invoke(
        {"messages": [{"role": "user", "content": "what's 5 + 7?"}]},
        config,
    )

    # Verify turn 2 results
    assert len(turn_2["messages"]) == 10
    assert turn_2["messages"][-4].content == "Successfully transferred to Alice"
    assert turn_2["messages"][-2].content == "12"
    assert turn_2["messages"][-1].content == recorded_messages[4].content
    assert turn_2["active_agent"] == "Alice"
