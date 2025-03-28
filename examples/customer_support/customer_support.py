import datetime
from collections import defaultdict
from typing import Callable, Union

from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import create_react_agent

from langgraph_swarm import create_handoff_tool, create_swarm

model = ChatOpenAI(model="gpt-4o", temperature=0.0)
# model = ChatOllama(model="qwen2.5:14b-instruct", temperature=0.0)

# Mock data for tools
RESERVATIONS = defaultdict(lambda: {"flight_info": {}, "hotel_info": {}})

TOMORROW = (datetime.date.today() + datetime.timedelta(days=1)).isoformat()
FLIGHTS = [
    {
        "departure_airport": "BOS",
        "arrival_airport": "JFK",
        "airline": "Jet Blue",
        "date": TOMORROW,
        "id": "1",
    }
]
HOTELS = [
    {
        "location": "New York",
        "name": "McKittrick Hotel",
        "neighborhood": "Chelsea",
        "id": "1",
    }
]


# Flight tools
def search_flights(
    departure_airport: str,
    arrival_airport: str,
    date: str,
) -> list[dict]:
    """Search flights.

    Args:
        departure_airport (str): 3-letter airport code for the departure airport. If unsure, use the biggest airport in the area
        arrival_airport (str): 3-letter airport code for the arrival airport. If unsure, use the biggest airport in the area
        date (str): YYYY-MM-DD date
    """
    # return all flights for simplicity
    return FLIGHTS


def book_flight(
    flight_id: Union[str, int],
    config: RunnableConfig,
) -> str:
    """Book a flight.
    
    Args:
        flight_id (Union[str, int]): ID of the flight to book (will be converted to string automatically if an integer is provided)
    """
    user_id = config["configurable"].get("user_id")
    # Convert flight_id to string if it's an integer
    flight_id_str = str(flight_id)
    flight = [flight for flight in FLIGHTS if flight["id"] == flight_id_str][0]
    RESERVATIONS[user_id]["flight_info"] = flight
    return "Successfully booked flight"

# Hotel tools
def search_hotels(location: str) -> list[dict]:
    """Search hotels.

    Args:
        location (str): legal city name (proper noun)
    """
    # return all hotels for simplicity
    return HOTELS


def book_hotel(
    hotel_id: Union[str, int],
    config: RunnableConfig,
) -> str:
    """Book a hotel
    
    Args:
        hotel_id (Union[str, int]): ID of the hotel to book (will be converted to string automatically if an integer is provided)
    """
    user_id = config["configurable"].get("user_id")
    # Convert hotel_id to string if it's an integer
    hotel_id_str = str(hotel_id)
    hotel = [hotel for hotel in HOTELS if hotel["id"] == hotel_id_str][0]
    RESERVATIONS[user_id]["hotel_info"] = hotel
    return "Successfully booked hotel"


# Define handoff tools
transfer_to_hotel_assistant = create_handoff_tool(
    agent_name="hotel_assistant",
    description="Transfer user to the hotel-booking assistant that can search for and book hotels.",
)

transfer_to_flight_assistant = create_handoff_tool(
    agent_name="flight_assistant",
    description="Transfer user to the flight-booking assistant that can search for and book flights.",
)


# Define agent prompt
def make_prompt(base_system_prompt: str) -> Callable[[dict, RunnableConfig], list]:
    def prompt(state: dict, config: RunnableConfig) -> list:
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
flight_assistant = create_react_agent(
    model,
    [search_flights, book_flight, transfer_to_hotel_assistant],
    prompt=make_prompt("You are a flight booking assistant. You have access to 3 tools: search_flights, book_flight, and transfer_to_hotel_assistant."
                       "use search_flights to find a flight, use book_flight to book a flight, and use transfer_to_hotel_assistant to transfer the user to the hotel-booking assistant for any hotel-related queries."
                       "search_flights arguments: departure_airport (str), arrival_airport (str), date (str)"
                       "book_flight arguments: flight_id (str) - IMPORTANT: flight_id must be passed as a string, not an integer"
                       "transfer_to_hotel_assistant arguments: None"
                       ),
    name="flight_assistant",
)

hotel_assistant = create_react_agent(
    model,  
    [search_hotels, book_hotel, transfer_to_flight_assistant],
    prompt=make_prompt("You are a hotel booking assistant. You have access to 3 tools: search_hotels, book_hotel, and transfer_to_flight_assistant."
                       "use search_hotels to find a hotel, use book_hotel to book a hotel, and use transfer_to_flight_assistant to transfer the user to the flight-booking assistant for any flight-related queries."
                       "search_hotels arguments: legal city name as a proper noun (str)"
                       "book_hotel arguments: hotel_id (str) - IMPORTANT: hotel_id must be passed as a string, not an integer"
                       "transfer_to_flight_assistant arguments: None"
                       ),
    name="hotel_assistant",
)

# Compile and run!
checkpointer = InMemorySaver()
builder = create_swarm([flight_assistant, hotel_assistant], default_active_agent="flight_assistant")

# Important: compile the swarm with a checkpointer to remember
# previous interactions and last active agent
app = builder.compile(checkpointer=checkpointer)
# config = {"configurable": {"thread_id": "1", "user_id": "1"}}
# result = app.invoke({
#     "messages": [
#         {
#             "role": "user",
#             "content": "i am looking for a flight from boston to ny tomorrow"
#         }
#     ],
# }, config)
