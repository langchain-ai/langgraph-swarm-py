from langchain.chat_models import init_chat_model
from langgraph.prebuilt import create_react_agent
from langgraph_swarm import create_handoff_tool, create_swarm

# from swarm_researcher.configuration import Configuration
from swarm_researcher.prompts import planner_prompt, researcher_prompt
from swarm_researcher.utils import fetch_doc

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
llms_txt = "LangGraph:https://langchain-ai.github.io/langgraph/llms.txt"
num_urls = 3
planner_prompt_formatted = planner_prompt.format(llms_txt=llms_txt, num_urls=num_urls)

# Planner agent
planner_agent = create_react_agent(
    model,
    prompt=planner_prompt_formatted,
    tools=[fetch_doc, transfer_to_researcher_agent],
    name="planner_agent",
)

# Researcher agent
researcher_agent = create_react_agent(
    model,
    prompt=researcher_prompt,
    tools=[fetch_doc, transfer_to_planner_agent],
    name="researcher_agent",
)

# Swarm
agent_swarm = create_swarm(
    [planner_agent, researcher_agent], default_active_agent="planner_agent"
)
app = agent_swarm.compile()
