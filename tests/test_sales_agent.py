import re
import pytest
from datetime import date
from langsmith import testing as t

from agents.Sales import sales_agent


today = date.today().isoformat()

    
def run_agent(user_input: str):
    t.log_inputs({"user_query": user_input})
    response = sales_agent.invoke({
        "messages": [{"role": "user", "content": user_input}]
    })
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
# EVALUATOR 1: Generate exactly ONE SQL statement.
def test_only_one_statment():

    response = run_agent(
        "Buy 3 apples for $9.00."
    )

    sql = extract_sql(response)
    t.log_outputs({"sql": sql})

    statements = [s.strip() for s in sql.split(";") if s.strip()]
    t.log_feedback(key="only_one_statement", score=len(statements) == 1)


@pytest.mark.langsmith
# EVALUATOR 2: The SQL statement must be an INSERT statement.
def test_sql_insert_statment():

    response = run_agent(
        "Buy 5 bananas for $10.00."
    )

    sql = extract_sql(response)
    t.log_outputs({"sql": sql})
    t.log_feedback(key="is_insert_statement", score=sql.upper().startswith("INSERT"))


@pytest.mark.langsmith
# EVALUATOR 3: Insert into the sales table.
def test_sql_uses_sales_table():

    response = run_agent(
        "Buy 2 oranges for $6.00."
    )

    sql = extract_sql(response)
    t.log_outputs({"sql": sql})
    t.log_feedback(key="uses_sales_table", score="sales" in sql.lower())


@pytest.mark.langsmith
# EVALUATOR 4: If the user requests one item, generate one sales row.
def test_sql_oneitem_onerow():

    response = run_agent(
        "Buy 10 apples for $25.00."
    )

    sql = extract_sql(response)
    t.log_outputs({"sql": sql})

    # One row means one VALUES clause
    values_count = len(re.findall(r"\bVALUES\b", sql, re.IGNORECASE))
    t.log_feedback(key="one_item_one_row", score=values_count == 1)


@pytest.mark.langsmith
# EVALUATOR 5: Do not invent columns.
def test_no_hallucination_columns():

    response = run_agent(
        "Buy 20 apples for $900.00."
    )

    sql = extract_sql(response).lower()
    t.log_outputs({"sql": sql})

    forbidden_columns = [
        "stock",
        "quantity",
        "product_name",
        "inventory_date",
        "price_per_item",
        "unit_price",
    ]

    t.log_feedback(
        key="no_hallucinated_columns",
        score=all(col not in sql for col in forbidden_columns)
    )


@pytest.mark.langsmith
# EVALUATOR 6: If a date is not provided, use today's date.
def test_sql_not_provide_day():

    response = run_agent(
        "Buy 4 bananas for $8.00."
    )

    sql = extract_sql(response)
    t.log_outputs({"sql": sql})
    t.log_feedback(key="default_date_is_today", score=today in sql)


@pytest.mark.langsmith
# EVALUATOR 7: The total_price must be the total cost supplied by the calling agent.
@pytest.mark.parametrize(
    "user_input,expected_total",
    [
        ("Buy 2 apples for $6.00.", "6.0"),
        ("Buy 5 bananas for $15.00.", "15.0"),
        ("Buy 10 oranges for $30.00.", "30.0"),
    ]
)
def test_sql_total_price(user_input, expected_total):

    response = run_agent(user_input)

    sql = extract_sql(response)
    t.log_outputs({"sql": sql})
    t.log_feedback(key="correct_total_price", score=expected_total in sql)


@pytest.mark.langsmith
# EVALUATOR 8: Item name should appear in the generated SQL.
@pytest.mark.parametrize(
    "user_input,item",
    [
        ("Buy 3 apples for $9.00.", "apple"),
        ("Buy 7 bananas for $14.00.", "banana"),
        ("Buy 1 orange for $2.50.", "orange"),
    ]
)
def test_item_exist(user_input, item):

    response = run_agent(user_input)

    sql = extract_sql(response).lower()
    t.log_outputs({"sql": sql})
    t.log_feedback(key="item_in_sql", score=item.lower() in sql)


@pytest.mark.langsmith
# EVALUATOR 9: An explicit date provided by the user should be preserved in the SQL.
@pytest.mark.parametrize(
    "user_input,expected_date",
    [
        ("Buy 3 apples for $9.00 on 2026-01-15.", "2026-01-15"),
        ("Buy 5 bananas for $10.00 on 2025-12-31.", "2025-12-31"),
    ]
)
def test_explicit_date_is_preserved(user_input, expected_date):

    response = run_agent(user_input)

    sql = extract_sql(response)
    t.log_outputs({"sql": sql})
    t.log_feedback(key="explicit_date_preserved", score=expected_date in sql)


@pytest.mark.langsmith
# EVALUATOR 10: Agent should not crash on valid inputs.
@pytest.mark.parametrize(
    "user_input",
    [
        "Buy 3 apples for $9.00.",
        "Buy 10 bananas for $20.00.",
        "Buy 5 oranges for $12.50.",
        "Buy 100 grapes for $150.00.",
    ]
)
def test_agent_execution(user_input):

    response = run_agent(user_input)
    t.log_outputs({"sql": extract_sql(response)})
    t.log_feedback(
        key="agent_execution",
        score=(
            response is not None
            and "messages" in response
            and len(response["messages"]) > 0
        )
    )