# 🤖 LangGraph Multi-Agent Swarm 

A Python library for creating swarm-style multi-agent systems using [LangGraph](https://github.com/langchain-ai/langgraph). A swarm is a type of [multi-agent](https://langchain-ai.github.io/langgraph/concepts/multi_agent) architecture where agents dynamically hand off control to one another based on their specializations. The system remembers which agent was last active, ensuring that on subsequent interactions, the conversation resumes with that agent.

## Features

- 🤖 **Multi-agent collaboration** - Enable specialized agents to work together and hand off context to each other
- 🛠️ **Customizable handoff tools** - Built-in tools for communication between agents

This library is built on top of [LangGraph](https://github.com/langchain-ai/langgraph), a powerful framework for building agent applications, and comes with out-of-box support for [streaming](https://langchain-ai.github.io/langgraph/how-tos/#streaming), [short-term and long-term memory](https://langchain-ai.github.io/langgraph/concepts/memory/) and [human-in-the-loop](https://langchain-ai.github.io/langgraph/concepts/human_in_the_loop/)

## Installation

```bash
pip install langgraph-swarm
```

## Quickstart

```bash
pip install langgraph-swarm langchain-openai

export OPENAI_API_KEY=<your_api_key>
```

```python
from collections import defaultdict
import datetime
from typing_extensions import Annotated, Literal

from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from langgraph_swarm import create_handoff_tool, create_swarm

model = ChatOpenAI(model="gpt-4o")

# Mock data for tools
RESERVATIONS = defaultdict(lambda: {"flight_info": {}, "hotel_info": {}})

TOMORROW = (datetime.date.today() + datetime.timedelta(days=1)).isoformat()
FLIGHTS = [{"departure_airport": "BOS", "arrival_airport": "JFK", "airline": "Jet Blue", "date": TOMORROW, "id": "1"}]
HOTELS = [{"location": "New York", "name": "McKittrick Hotel", "neighborhood": "Chelsea", "id": "1"}]

# Flight tools
def search_flights(
    departure_airport: str,
    arrival_airport: str,
    date: str,
):
    """Search flights.

    Args:
        departure_airport: 3-letter airport code for the departure airport. If unsure, use the biggest airport in the area
        arrival_airport: 3-letter airport code for the arrival airport. If unsure, use the biggest airport in the area
        date: YYYY-MM-DD date
    """
    # return all flights for simplicity
    return FLIGHTS

def book_flight(
    flight_id: str,
    config: RunnableConfig,
):
    """Book a flight."""
    user_id = config["configurable"].get("user_id")
    flight = [flight for flight in FLIGHTS if flight["id"] == flight_id][0]
    RESERVATIONS[user_id]["flight_info"] = flight
    return "Successfully booked flight"

# Hotel tools
def search_hotels(
    location: str
):
    """Search hotels.

    Args:
        location: offical, legal city name (proper noun)
    """
    # return all hotels for simplicity
    return HOTELS

def book_hotel(
    hotel_id: str,
    config: RunnableConfig,
):
    """Book a hotel"""
    user_id = config["configurable"].get("user_id")
    hotel = [hotel for hotel in HOTELS if hotel["id"] == hotel_id][0]
    RESERVATIONS[user_id]["hotel_info"] = hotel
    return "Successfully booked hotel"

# Define handoff tools
transfer_to_hotel_assistant = create_handoff_tool(
    agent_name="hotel_assistant",
    description="Transfer user to the hotel-booking assistant that can search for and book hotels."
)
transfer_to_flight_assistant = create_handoff_tool(
    agent_name="flight_assistant",
    description="Transfer user to the flight-booking assistant that can search for and book flights."
)

# Define agent prompt
def make_prompt(base_system_prompt: str):
    def prompt(state, config):
        user_id = config["configurable"].get("user_id")
        current_reservation = RESERVATIONS[user_id]
        system_prompt = (
            base_system_prompt
            + f"\n\nUser's active reservation: {current_reservation}"
            + f"Today is: {datetime.datetime.now()}"
        )
        return [{"role": "system", "content": system_prompt}] + state["messages"]

    return prompt

# Define agents
flight_assistant_tools = [search_flights, book_flight, transfer_to_hotel_assistant]
flight_assistant = create_react_agent(
    model.bind_tools(flight_assistant_tools, parallel_tool_calls=False),
    flight_assistant_tools,
    prompt=make_prompt("You are a flight booking assistant"),
    name="flight_assistant"
)

hotel_assistant_tools = [search_hotels, book_hotel, transfer_to_flight_assistant]
hotel_assistant = create_react_agent(
    model.bind_tools(hotel_assistant_tools, parallel_tool_calls=False),
    hotel_assistant_tools,
    prompt=make_prompt("You are a hotel booking assistant"),
    name="hotel_assistant"
)

# Compile and run!
checkpointer = MemorySaver()
builder = create_swarm(
    [flight_assistant, hotel_assistant],
    default_active_agent="flight_assistant"
)

# Important: compile the swarm with a checkpointer to remember
# previous interactions and last active agent
app = builder.compile(checkpointer=checkpointer)
config = {"configurable": {"thread_id": "1", "user_id": "1"}}
result = app.invoke({
    "messages": [
        {
            "role": "user",
            "content": "i am looking for a flight from boston to ny tomorrow"
        }
    ],
}, config)
```

> [!IMPORTANT]
> Adding [persistence](https://langchain-ai.github.io/langgraph/concepts/persistence/) is crucial for maintaining conversation state across multiple interactions. Without it, the swarm would "forget" which agent was last active and lose the conversation history. Make sure to always compile the swarm with a checkpointer, e.g., `workflow.compile(checkpointer=checkpointer)`