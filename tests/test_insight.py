import json

import sqlite3

import pytest

from agents import Insight as insight


@pytest.fixture
def test_db(tmp_path, monkeypatch):
    db_path = tmp_path / "test_ecommerce.db"

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE inventory (
            inventory_id INTEGER PRIMARY KEY AUTOINCREMENT,
            item TEXT NOT NULL,
            date TEXT NOT NULL,
            count INTEGER NOT NULL,
            price_per_item REAL NOT NULL
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE sales (
            sales_id INTEGER PRIMARY KEY AUTOINCREMENT,
            item TEXT NOT NULL,
            count INTEGER NOT NULL,
            total_price REAL NOT NULL,
            date TEXT NOT NULL
        )
        """
    )

    cursor.executemany(
        """
        INSERT INTO inventory
        (item, date, count, price_per_item)
        VALUES (?, ?, ?, ?)
        """,
        [
            ("apple", "2026-09-08", 12, 1.50),
            ("apples", "2026-09-09", 8, 1.50),
        ],
    )

    cursor.executemany(
        """
        INSERT INTO sales
        (item, count, total_price, date)
        VALUES (?, ?, ?, ?)
        """,
        [
            ("apple", 10, 15.00, "2026-09-08"),
            ("apple", 7, 10.50, "2026-09-09"),
            ("apple", 14, 21.00, "2026-09-10"),
            ("banana", 5, 5.00, "2026-09-10"),
        ],
    )

    conn.commit()
    conn.close()

    monkeypatch.setattr(
        insight,
        "DB_NAME",
        str(db_path),
    )

    return db_path


def test_customer_cannot_access_sales(test_db):
    result = insight._get_sales_history_for_role(
        role="customer",
        item="apple",
    )

    assert result["authorized"] is False
    assert result["error"] == "not_authorized"


@pytest.mark.parametrize(
    "role",
    ["manager", "owner", "admin"],
)
def test_authorized_roles_can_access_sales(
    test_db,
    role,
):
    result = insight._get_sales_history_for_role(
        role=role,
        item="apple",
    )

    assert result["authorized"] is True
    assert result["record_count"] == 3


def test_sales_summary(test_db):
    result = insight._get_sales_summary_for_role(
        role="manager",
        item="apple",
    )

    assert result["authorized"] is True
    assert result["total_units"] == 31
    assert result["total_revenue"] == pytest.approx(46.50)


def test_sales_graph(test_db, tmp_path, monkeypatch):
    monkeypatch.setattr(
        insight,
        "CHART_DIR",
        tmp_path / "charts",
    )

    result = insight._create_sales_chart_for_role(
        role="manager",
        item="apple",
        metric="units_sold",
    )

    assert result["authorized"] is True

    chart_path = tmp_path / "charts" / "apple-units_sold.png"

    assert chart_path.exists()


# ---------------------------------------------------------
# Authorization tests
# ---------------------------------------------------------

@pytest.mark.parametrize(
    "role",
    ["customer", "employee", "guest"],
)
def test_unauthorized_roles_cannot_access_sales(
    test_db,
    role,
):
    result = insight._get_sales_history_for_role(
        role=role,
        item="apple",
    )

    assert result["authorized"] is False
    assert result["error"] == "not_authorized"


@pytest.mark.parametrize(
    "role",
    ["manager", "owner", "admin"],
)
def test_authorized_roles_can_access_sales(
    test_db,
    role,
):
    result = insight._get_sales_history_for_role(
        role=role,
        item="apple",
    )

    assert result["authorized"] is True
    assert result["record_count"] == 3


# ---------------------------------------------------------
# Inventory tests
# ---------------------------------------------------------

def test_inventory_count_handles_singular_and_plural(
    test_db,
):
    result_json = insight.get_inventory_count.invoke(
        {"item": "apple"}
    )

    result = json.loads(result_json)

    # Fixture contains:
    # apple  = 12
    # apples = 8
    assert result["count"] == 20


def test_inventory_unknown_item_returns_zero(
    test_db,
):
    result_json = insight.get_inventory_count.invoke(
        {"item": "watermelon"}
    )

    result = json.loads(result_json)

    assert result["count"] == 0


# ---------------------------------------------------------
# Sales history tests
# ---------------------------------------------------------

def test_sales_history_filters_by_item(
    test_db,
):
    result = insight._get_sales_history_for_role(
        role="manager",
        item="apple",
    )

    assert result["authorized"] is True
    assert result["record_count"] == 3

    assert all(
        row["item"] == "apple"
        for row in result["records"]
    )


def test_sales_history_filters_by_date_range(
    test_db,
):
    result = insight._get_sales_history_for_role(
        role="manager",
        item="apple",
        start_date="2026-09-09",
        end_date="2026-09-10",
    )

    assert result["authorized"] is True
    assert result["record_count"] == 2

    returned_dates = [
        row["date"]
        for row in result["records"]
    ]

    assert returned_dates == [
        "2026-09-09",
        "2026-09-10",
    ]


# ---------------------------------------------------------
# Analytics tests
# ---------------------------------------------------------

def test_sales_summary(
    test_db,
):
    result = insight._get_sales_summary_for_role(
        role="manager",
        item="apple",
    )

    assert result["authorized"] is True
    assert result["total_units"] == 31
    assert result["total_revenue"] == pytest.approx(46.50)


def test_top_seller_is_apple(
    test_db,
):
    result = insight._get_sales_summary_for_role(
        role="manager",
    )

    assert result["authorized"] is True
    assert result["top_seller"]["item"] == "apple"
    assert result["top_seller"]["units_sold"] == 31


def test_customer_cannot_access_sales_summary(
    test_db,
):
    result = insight._get_sales_summary_for_role(
        role="customer",
    )

    assert result["authorized"] is False
    assert result["error"] == "not_authorized"


# ---------------------------------------------------------
# Graph tests
# ---------------------------------------------------------

def test_sales_graph_is_created(
    test_db,
    tmp_path,
    monkeypatch,
):
    monkeypatch.setattr(
        insight,
        "CHART_DIR",
        tmp_path / "charts",
    )

    result = insight._create_sales_chart_for_role(
        role="manager",
        item="apple",
        metric="units_sold",
    )

    assert result["authorized"] is True

    chart_path = (
        tmp_path
        / "charts"
        / "apple-units_sold.png"
    )

    assert chart_path.exists()


def test_revenue_graph_is_created(
    test_db,
    tmp_path,
    monkeypatch,
):
    monkeypatch.setattr(
        insight,
        "CHART_DIR",
        tmp_path / "charts",
    )

    result = insight._create_sales_chart_for_role(
        role="owner",
        item="apple",
        metric="revenue",
    )

    assert result["authorized"] is True

    chart_path = (
        tmp_path
        / "charts"
        / "apple-revenue.png"
    )

    assert chart_path.exists()


def test_customer_cannot_generate_sales_graph(
    test_db,
):
    result = insight._create_sales_chart_for_role(
        role="customer",
        item="apple",
        metric="units_sold",
    )

    assert result["authorized"] is False
    assert result["error"] == "not_authorized"


def test_invalid_graph_metric_is_rejected(
    test_db,
):
    result = insight._create_sales_chart_for_role(
        role="manager",
        item="apple",
        metric="profit_margin",
    )

    assert result["authorized"] is True
    assert result["error"] == "invalid_metric"