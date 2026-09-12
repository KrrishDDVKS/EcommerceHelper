import re
import pytest

from agents.Inventory import Inventory_agent


def run_agent(user_input: str):
    response = Inventory_agent.invoke({
    "messages": [{"role": "user","content": user_input}]})

    return response

def extract_sql(response):
    """
    Extract SQL from the agent's final response.
    """

    messages = response.get("messages", [])

    for message in reversed(messages):

        content = getattr(message, "content", "")

        if not content:
            continue

        match = re.search(
            r"(INSERT\s+INTO.*?;)",
            content,
            re.IGNORECASE | re.DOTALL
        )

        if match:
            return match.group(1).strip()

    return ""

# EVALUATOR 1: SQL should contain the inventory table
def test_sql_uses_inventory_table():

    response = run_agent(
        "Add 10 keyboards at $25 each"
    )

    sql = extract_sql(response)

    assert "inventory" in sql.lower()

# EVALUATOR 2: SQL should be an INSERT statement
def test_sql_is_insert_statement():

    response = run_agent(
        "Add 10 keyboards at $25 each"
    )

    sql = extract_sql(response)

    assert sql.startswith("INSERT")

#EVALUATOR 3: SQL should use valid columns
def test_sql_uses_valid_columns():

    response = run_agent(
        "Add 10 keyboards at $25 each"
    )

    sql = extract_sql(response)

    assert "item" in sql
    assert "date" in sql
    assert "count" in sql
    assert "price_per_item" in sql