import os
import sqlite3

from langgraph import graph
from openai.types import Image

from Sales import Ext_agent
from Inventory import Inventory_agent
from Insight import Insight_agent

from langchain_openai import ChatOpenAI
from langchain.messages import HumanMessage
from langchain.agents import create_agent
from langchain_core.tools import tool

from IPython.display import Image, display

DB_NAME = "ecommerce.db"

@tool
def sales_agent(x: str) -> str:
    """Call sales agent in order to buy some items and insert sales data to the database in Sales table"""
    response = Ext_agent.invoke({"messages": [HumanMessage(content=f"Insert sales data")]})
    return response["messages"][-1].content

@tool
def inventory_agent(x: str) -> str:
    """Call inventory agent in order to add inventory items like adding stock like items to the database in Inventory table"""
    response = Inventory_agent.invoke({"messages": [HumanMessage(content=f"Insert inventory data")]})
    return response["messages"][-1].content

@tool
def insight_agent(x: str) -> str:
    """Call insight agent in order to provide insights about the sales and inventory data in the database"""
    response = Insight_agent.invoke({"messages": [HumanMessage(content=f"Provide insights")]})
    return response["messages"][-1].content

## Creating the main agent
system_prompt = """
You are an E-commerce Assistant system.

Rules based on User Role:
- **Sales Agent / Customer**: Call `record_sale_tool`. Calculate `total_price = count * unit_price` if needed.
- **Inventory Agent / Supply**: Call `add_inventory_tool`.
- **Manager / Admin**: Call `execute_sql_analytics_tool`. You MUST construct a valid SELECT SQL query AND provide standalone Matplotlib python plotting code to visualize the data.

Always pick the correct tool based on user role and query context.
"""

llm = ChatOpenAI(
    model="gpt-5-nano",
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0
)
    
main_agent = create_agent(
    model=llm,
    tools=[sales_agent, inventory_agent, insight_agent],
    system_prompt=system_prompt)

display(Image(main_agent.get_graph().draw_mermaid_png()))
# question = HumanMessage(content="""
# I want to buy 5 apple of $1.50.
# """)

# response = main_agent.invoke(
# {"messages": [question]}
# )
# print(response['messages'][-1].content)
