
# Imports
from contextlib import asynccontextmanager

from langchain_anthropic import ChatAnthropic
from langchain_mcp_adapters.client import MultiServerMCPClient

from langgraph.prebuilt import create_react_agent
from langgraph_swarm import create_handoff_tool, create_swarm

# from swarm_researcher.configuration import Configuration
from swarm_researcher.prompts import planner_prompt, researcher_prompt

# LLM
model = ChatAnthropic(model="claude-3-7-sonnet-latest")

# Handoff tools
transfer_to_planner_agent = create_handoff_tool(
    agent_name="planner_agent",
    description="Transfer user to the planner_agent to address clarifying questions or help them plan the steps to complete the user's request."
)
transfer_to_researcher_agent = create_handoff_tool(
    agent_name="researcher_agent",
    description="Transfer user to researcher_agent to perform research on the user's request."
)

# TODO: Move to configuration
llms_txt_urls = "LangGraph:https://langchain-ai.github.io/langgraph/llms.txt"

@asynccontextmanager
async def make_graph():
    async with MultiServerMCPClient(
    {
        "research-server": {
            "command": "npx",
            "args": ["@playwright/mcp"],
            "transport": "stdio",
            },
        "planning-server": {
            "command": "uvx",
            "args": [
            "--from",
            "mcpdoc",
            "mcpdoc",
            "--urls",
            llms_txt_urls,
            "--transport",
            "stdio",
            "--port",
            "8081",
            "--host",
            "localhost"
            ],
            "transport": "stdio",
        }
    }

) as client:
        
        # Planner agent
        planner_agent = create_react_agent(model,
                                        prompt=planner_prompt, 
                                        tools=client.server_name_to_tools["planning-server"].append(transfer_to_researcher_agent),
                                        name="planner_agent") 

        # Researcher agent
        researcher_agent = create_react_agent(model, 
                                            prompt=researcher_prompt, 
                                            tools=client.server_name_to_tools["research-server"].append(transfer_to_planner_agent),
                                            name="researcher_agent") 

        # Swarm
        agent_swarm = create_swarm([planner_agent, researcher_agent], default_active_agent="planner_agent")

        # app = agent_swarm.compile(config_schema=Configuration)
        agent = agent_swarm.compile()
        
        yield agent
