from dataclasses import dataclass
from datetime import date
import pandas as pd
from langchain_core.tools import tool
import os
import sqlite3
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain.messages import HumanMessage

from dotenv import load_dotenv

load_dotenv()
DB_NAME = 'ecommerce.db'
llm = ChatOpenAI(model='gpt-5-nano', api_key=os.getenv("OPENAI_API_KEY"), temperature=0)

from typing import TypedDict

@dataclass
class AgentState(TypedDict):
    messages: list
    insert_count: int

state = {
    "messages": [],
    "insert_count": 0
}

def get_inventory():
    conn = sqlite3.connect(DB_NAME)
    print("Connected to the database successfully.")

    df = pd.read_sql_query("SELECT * FROM inventory",conn)
    df1 = df.groupby('item').agg({'count':'sum','price_per_item':'max'}).reset_index()    
    df.to_sql("lookup_items",conn,if_exists="replace",index=False)  # append / replace / fail
    conn.close()
    df['date'] = pd.to_datetime(df['date']).dt.date
    df = df.sort_values(by='date', ascending=False)    

    print(
        df.to_string(index=False) + "\n" + df1.to_string(index=False)
    )


@tool
def execute_sql(query: str, state: AgentState) -> str:
    """
    Execute a SQL query against the SQLite database.

    Use this tool only after generating a valid SQL query. 
    The tool is used to insert data to the database.
    """
    if state["insert_count"] >= 1:
        return "INSERT BLOCKED: Only one inventory insertion is allowed per request."
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(query)

    conn.commit()
    result = f"Inserted the inventory data successfully.\n Rows affected: {cursor.rowcount}"
    conn.close()
    state["insert_count"] += 1
    print(get_inventory())
    # lookup()  # Update the lookup_items table after executing the query
    return str(result)

          # Update the lookup_items table after executing the query

today = date.today().isoformat()

system_prompt = f"""
You are a SQL generation agent.

Your job is to convert the user's natural-language request
into a valid SQLite SQL query.

Database schema:

inventory(
    inventory_id INTEGER PRIMARY KEY,
    item TEXT,
    date TEXT,
    count INTEGER,
    price_per_item REAL
)

Today's date is: {today}

Rules:

1. Understand the user's request.
2. Generate the appropriate SQL query.
3. Use only tables and columns that exist in the schema.
4. Do not invent columns.
5. If the user does not provide a date, use today's date:
   {today}
6. The SQL query should be an INSERT statement to add data to the inventory table.
"""
f=0
Inventory_agent = create_agent(
    model=llm,
    tools=[execute_sql],
    system_prompt=system_prompt,
)


# ---------------------------------------------------------
# 4. Run agent
# -------------------------------------------

question = HumanMessage(content="""
 I want to add 5 apple of $1.50.
 """)


response = Inventory_agent.invoke(
{"messages": [question]}
)
print(response['messages'][-1].content)
#_____________________________________________________________
