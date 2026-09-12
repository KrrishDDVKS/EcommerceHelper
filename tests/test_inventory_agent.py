import re
import pytest
from langsmith import testing as t

from agents.Inventory import Inventory_agent



def run_agent(user_input: str):
    t.log_inputs({"user_query": user_input})
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

@pytest.mark.langsmith
# EVALUATOR 1: SQL should contain the inventory table
def test_sql_uses_inventory_table():

    response = run_agent(
        "Add 10 apple at $25 each"
    )

    sql = extract_sql(response)
    t.log_outputs({"sql": sql})
    t.log_feedback(key="valid_sql", score="inventory" in sql.lower())


# EVALUATOR 2: SQL should be an INSERT statement
@pytest.mark.langsmith
def test_sql_is_insert_statement():

    response = run_agent(
        "Add 10 apple at $25 each"
    )

    sql = extract_sql(response)
    t.log_outputs({"sql": sql})
    t.log_feedback(key="valid_sql", score="inventory" in sql.lower())

#EVALUATOR 3: SQL should use valid columns
@pytest.mark.langsmith
def test_sql_uses_valid_columns():

    response = run_agent(
        "Add 10 apple at $25 each"
    )

    sql = extract_sql(response)
    t.log_outputs({"sql": sql})
    t.log_feedback(key="valid_columns", score=all(column in sql for column in ["item", "date", "count", "price_per_item"]))
    

@pytest.mark.langsmith
def test_no_hallucinated_columns():

#EVALUATOR 4: No hallucinated columns
    response = run_agent(
        "Add 20 apple at $900 each"
    )

    sql = extract_sql(response).lower()
    t.log_outputs({"sql": sql})
    t.log_feedback(key="no_hallucinated_columns", score=all(column not in sql for column in ["total_price", "stock", "quantity", "product_name"]))
    forbidden_columns = [
        "total_price",
        "stock",
        "quantity",
        "product_name",
        "inventory_date"
    ]


#EVALUATOR 5: Date should be included when omitted
@pytest.mark.langsmith
def test_missing_date_is_filled():

    response = run_agent(
        "Add 5 apple at $30 each"
    )

    sql = extract_sql(response)
    t.log_outputs({"sql": sql})
    t.log_feedback(key="missing_date_is_filled", score="date" in sql.lower())

#EVALUATOR 6: Explicit date should be preserved
@pytest.mark.langsmith
def test_explicit_date_is_preserved():

    response = run_agent(
        "Add 10 apple at $200 each on 2026-09-15"
    )

    sql = extract_sql(response)
    t.log_outputs({"sql": sql})
    t.log_feedback(key="explicit_date_is_preserved", score="2026-09-15" in sql)

#EVALUATOR 7: Item should appear in SQL

@pytest.mark.langsmith
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
    t.log_outputs({"sql": sql})
    t.log_feedback(key="correct_item", score=item.lower() in sql)

#EVALUATOR 8: Count should be correct

@pytest.mark.langsmith
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
    t.log_outputs({"sql": sql})
    t.log_feedback(key="correct_count", score=str(count) in sql)

#EVALUATOR 9:  Price should be correct

@pytest.mark.langsmith
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
    t.log_outputs({"sql": sql})
    t.log_feedback(key="correct_price", score=str(price) in sql)

#EVALUATOR 10: Agent should not crash
@pytest.mark.langsmith
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
    t.log_outputs({"sql":extract_sql(response)})
    t.log_feedback(key="agent_execution", score=response is not None and "messages" in response and len(response["messages"]) > 0)