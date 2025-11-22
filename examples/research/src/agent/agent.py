from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from prompts import planner_prompt, researcher_prompt
from utils import fetch_doc

from langgraph_swarm import create_handoff_tool, create_swarm

# LLM
model = init_chat_model(model="gpt-4o", model_provider="openai")

# Handoff tools
transfer_to_planner_agent = create_handoff_tool(
    agent_name="planner_agent",
    description="Transfer the user to the planner_agent for clarifying questions related to the user's request.",
)
transfer_to_researcher_agent = create_handoff_tool(
    agent_name="researcher_agent",
    description="Transfer the user to the researcher_agent to perform research and implement the solution to the user's request.",
)

# LLMS.txt
LLMS_TXT = "LangGraph:https://langchain-ai.github.io/langgraph/llms.txt"
NUM_URLS = 3
PLANNER_PROMPT_FORMATTED = planner_prompt.format(llms_txt=LLMS_TXT, num_urls=NUM_URLS)

# Planner agent
planner_agent = create_agent(
    model,
    system_prompt=PLANNER_PROMPT_FORMATTED,
    tools=[fetch_doc, transfer_to_researcher_agent],
    name="planner_agent",
)

# Researcher agent
researcher_agent = create_agent(
    model,
    system_prompt=researcher_prompt,
    tools=[fetch_doc, transfer_to_planner_agent],
    name="researcher_agent",
)

# Swarm
agent_swarm = create_swarm(
    [planner_agent, researcher_agent], default_active_agent="planner_agent"
)
app = agent_swarm.compile()
