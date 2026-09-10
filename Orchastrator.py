import Insight
#from Sales import Sales_agent
from Inventory import Inventory_agent
#from Insight import Insight_agent

import os
from langchain.messages import HumanMessage

from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
    
@tool
def sales_agent(x: float) -> float:
    """Call sales agent in order to to insert sales data into the database in Sales table"""
    response = Sales_agent.invoke({"messages": [HumanMessage(content=f"Insert sales data for {x}")]})
    return response["messages"][-1].content

@tool
def inventory_agent(x: float) -> float:
    """Call inventory agent in order to insert inventory data into the database in Inventory table"""
    response = Inventory_agent.invoke({"messages": [HumanMessage(content=f"Insert inventory data for {x}")]})
    return response["messages"][-1].content

@tool
def insight_agent(x: float) -> float:
    """Call insight agent in order to provide insights about the sales and inventory data in the database"""
    response = Insight_agent.invoke({"messages": [HumanMessage(content=f"Provide insights about {x}")]})
    return response["messages"][-1].content

## Creating the main agent
system_prompt = """
You are an E-commerce Assistant system managing SQLite tables: `sales` and `inventory`.

Database Schema:
1. `sales` table: sales_id (INTEGER PK), item (TEXT), count (INTEGER), total_price (REAL), date (TEXT)
2. `inventory` table: item_id (INTEGER PK), item (TEXT UNIQUE), count (INTEGER), price_per_item (REAL), date (TEXT)

Rules based on User Role:
- **Sales Agent / Customer**: Call `record_sale_tool`. Calculate `total_price = count * unit_price` if needed.
- **Inventory Agent / Supply**: Call `add_inventory_tool`.
- **Manager / Admin**: Call `execute_sql_analytics_tool`. You MUST construct a valid SELECT SQL query AND provide standalone Matplotlib python plotting code to visualize the data.

Always pick the correct tool based on user role and query context.
"""

main_agent = create_agent(
    model='gpt-5-nano',
    tools=[sales_agent, inventory_agent, insight_agent],
    system_prompt=system_prompt)

question = HumanMessage(content="""
I want to add 5 apples of $1.50.
""")

response = main_agent.invoke(
{"messages": [question]}
)
print(response['messages'][-1].content)
