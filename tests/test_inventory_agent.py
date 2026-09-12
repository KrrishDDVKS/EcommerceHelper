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
        "Add 10 apple at $25 each"
    )

    sql = extract_sql(response)

    assert "inventory" in sql.lower()

# EVALUATOR 2: SQL should be an INSERT statement
def test_sql_is_insert_statement():

    response = run_agent(
        "Add 10 apple at $25 each"
    )

    sql = extract_sql(response)

    assert sql.startswith("INSERT")

#EVALUATOR 3: SQL should use valid columns
def test_sql_uses_valid_columns():

    response = run_agent(
        "Add 10 apple at $25 each"
    )

    sql = extract_sql(response)

    assert "item" in sql
    assert "date" in sql
    assert "count" in sql
    assert "price_per_item" in sql

def test_no_hallucinated_columns():

#EVALUATOR 4: No hallucinated columns
    response = run_agent(
        "Add 20 apple at $900 each"
    )

    sql = extract_sql(response).lower()

    forbidden_columns = [
        "total_price",
        "stock",
        "quantity",
        "product_name",
        "inventory_date"
    ]

    for column in forbidden_columns:
        assert column not in sql

#EVALUATOR 5: Date should be included when omitted
def test_missing_date_is_filled():

    response = run_agent(
        "Add 5 apple at $30 each"
    )

    sql = extract_sql(response)

    assert "date" in sql.lower()

#EVALUATOR 6: Explicit date should be preserved

def test_explicit_date_is_preserved():

    response = run_agent(
        "Add 10 apple at $200 each on 2026-09-15"
    )

    sql = extract_sql(response)

    assert "2026-09-15" in sql

#EVALUATOR 7: Item should appear in SQL

@pytest.mark.parametrize(
"user_input,item",
[
("Add 10 apple at $25 each", "apple"),
("Add 20 banana at $200 each", "banana"),
("Add 5 orange at $900 each", "orange"),
]
)
def test_item_is_correct(user_input, item):

    response = run_agent(user_input)

    sql = extract_sql(response).lower()

    assert item.lower() in sql

#EVALUATOR 8: Count should be correct

@pytest.mark.parametrize(
"user_input,count",
[
("Add 10 apple at $25 each", 10),
("Add 20 banana at $200 each", 20),
("Add 5 orange at $900 each", 5),
]
)
def test_inventory_count(user_input, count):

    response = run_agent(user_input)

    sql = extract_sql(response)

    assert str(count) in sql

#EVALUATOR 9:  Price should be correct


@pytest.mark.parametrize(
"user_input,price",
[
("Add 10 apple at $25 each", 25),
("Add 20 banana at $200 each", 200),
("Add 5 orange at $900 each", 900),
]
)

def test_price_per_item(user_input, price):

    response = run_agent(user_input)

    sql = extract_sql(response)

    assert str(price) in sql

#EVALUATOR 10: Agent should not crash

@pytest.mark.parametrize(
"user_input",
[
"Add 10 apple at $25 each",
"Add 20 banana at $200 each",
"Add 5 orange at $900 each",
"Add 100 grapes at $15 each",
]
)
def test_agent_execution(user_input):

    response = run_agent(user_input)

    assert response is not None
    assert "messages" in response
    assert len(response["messages"]) > 0