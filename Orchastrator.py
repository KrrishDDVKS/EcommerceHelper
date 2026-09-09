from langchain.schema import HumanMessage
from openai import AsyncOpenAI
from langsmith import traceable
from langsmith.wrappers import wrap_openai
from langchain.tools import tool
import os
from Sales import sales_agent
from Inventory import inventory_agent
from Insight import insight_agent

# Initialize OpenAI client with LangSmith wrapper
client = wrap_openai(AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY")))
    
@tool
def sales_agent(x: float) -> float:
    """Call subagent 1 in order to calculate the square root of a number"""
    response = SalesAgent.invoke({"messages": [HumanMessage(content=f"Calculate the square root of {x}")]})
    return response["messages"][-1].content

@tool
def inventory_agent(x: float) -> float:
    """Call subagent 2 in order to calculate the square of a number"""
    response = InventoryAgent.invoke({"messages": [HumanMessage(content=f"Calculate the square of {x}")]})
    return response["messages"][-1].content

@tool
def insight_agent(x: float) -> float:
    """Call subagent 3 in order to provide insights about a number"""
    response = InsightAgent.invoke({"messages": [HumanMessage(content=f"Provide insights about {x}")]})
    return response["messages"][-1].content

## Creating the main agent

main_agent = create_agent(
    model='gpt-5-nano',
    tools=[sales_agent, inventory_agent, insight_agent],
    system_prompt="You are a helpful assistant who can call subagents to calculate the square root or square of a number.")