from datetime import date
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

@tool
def execute_sql(query: str) -> str:
    """
    Execute a SQL query against the SQLite database.

    Use this tool only after generating a valid SQL query. 
    The tool is used to insert data to the database.
    """

    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute(query)

        conn.commit()
        result = f"Inserted the inventory data successfully. Rows affected: {cursor.rowcount}"

        conn.close()

        return str(result)
    except Exception as e:
        return f"Error executing SQL query: {str(e)}"
    

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
6. For INSERT requests, generate an INSERT INTO query.
7. Execute the generated SQL using the database tool.
8. Return the SQL query that was executed.
9. Return the result of the SQL execution.
10. Do not perform calculations in Python.
11. Do not ask the user for the date if it is not provided;
    automatically use today's date.
"""

Inventory_agent = create_agent(
    model=llm,
    tools=[execute_sql],
    system_prompt=system_prompt,
)


# ---------------------------------------------------------
# 4. Run agent
# -------------------------------------------

question = HumanMessage(content="""
I want to add 5 apples of $1.50.
""")


response = Inventory_agent.invoke(
{"messages": [question]}
)
print(response['messages'][-1].content)

# @tool
# def add_inventory(
#     item: str,
#     count: int,
#     price_per_item: float,
#     date: str | None = None
# ) -> str:
#     """
#     Add inventory or increase the existing inventory count.
#     """

#     if date is None:
#         date = datetime.now().strftime("%Y-%m-%d")

#     item = item.lower().strip()

#     conn = sqlite3.connect(DB_NAME)
#     cursor = conn.cursor()

#     cursor.execute("""
#         INSERT INTO inventory
#         (item, count, price_per_item, date)
#         VALUES (?, ?, ?, ?)

#         ON CONFLICT(item)
#         DO UPDATE SET
#             count = inventory.count + excluded.count,
#             price_per_item = excluded.price_per_item,
#             date = excluded.date
#     """, (
#         item,
#         count,
#         price_per_item,
#         date
#     ))

#     conn.commit()
#     conn.close()

#     return (
#         f"Inventory updated: "
#         f"{item}, +{count} units, "
#         f"${price_per_item:.2f}/unit"
#     )


def get_inventory() -> str:
    """
    Get current inventory for an item.
    """

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT item, count, price_per_item, date
        FROM inventory
    """)

    results = cursor.fetchall()

    conn.close()

    if results is None:
        return f"Item not available in inventory."

    return (
        f"Item: {result[0]}, "
        f"Stock: {result[1]}, "
        f"Price: ${result[2]:.2f}, "
        f"Last Updated: {result[3]}\n" for result in results
    )

print(get_inventory())
# inventory_tools = [
#     add_inventory,
#     get_inventory
# ]

# inventory_agent = create_agent(
#     model=llm,
#     tools=inventory_tools,
#     system_prompt="""
#     You are the Inventory Agent for EcommerceHelper.

#     Your responsibility is managing product inventory.

#     You can:
#     - Add inventory.
#     - Update inventory.
#     - Check inventory.

#     Use your tools when database operations are required.

#     Do not perform sales recording or manager analytics tasks.
#     """
# )