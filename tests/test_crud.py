import pytest
from datetime import date
from database import get_db_connection, init_db
from schemas import ExpenseCreate, ExpenseUpdate
from crud import (
    create_expense,
    get_expense,
    list_expenses,
    update_expense,
    delete_expense,
    monthly_summary,
    build_update_sql,
)


@pytest.fixture
def db_conn(tmp_path):
    db_file = tmp_path / "test_expenses.db"
    init_db(db_path=str(db_file))
    conn = get_db_connection(db_path=str(db_file))
    yield conn
    conn.close()
    

def test_create_and_get_expense(db_conn):
    payload = ExpenseCreate(
        amount=1200,
        category="Food",
        date=date(2026, 3, 10),
        note="Lunch",
    )
    expense = create_expense(db_conn, payload)
    assert expense is not None
    assert expense["amount"] == 1200
    assert expense["category"] == "food"
    assert expense["date"] == "2026-03-10"
    assert expense["note"] == "Lunch"
    assert "id" in expense

    fetched = get_expense(db_conn, expense["id"])
    assert fetched is not None
    assert fetched["id"] == expense["id"]
    assert fetched["amount"] == 1200
    assert fetched["category"] == "food"


def test_get_expense_missing(db_conn):
    fetched = get_expense(db_conn, 9999)
    assert fetched is None


def test_list_expenses_with_filters(db_conn):
    create_expense(db_conn, ExpenseCreate(amount=500, category="Food", date=date(2026, 3, 1)))
    create_expense(db_conn, ExpenseCreate(amount=1500, category="Transport", date=date(2026, 3, 15)))
    create_expense(db_conn, ExpenseCreate(amount=300, category="Food", date=date(2026, 4, 1)))

    # List all
    all_expenses = list_expenses(db_conn)
    assert len(all_expenses) == 3

    # Filter by category
    food_expenses = list_expenses(db_conn, category="Food")
    assert len(food_expenses) == 2
    assert all(e["category"] == "food" for e in food_expenses)

    # Filter by date range
    range_expenses = list_expenses(db_conn, start_date=date(2026, 3, 1), end_date=date(2026, 3, 10))
    assert len(range_expenses) == 1
    assert range_expenses[0]["amount"] == 500


def test_update_expense(db_conn):
    expense = create_expense(db_conn, ExpenseCreate(amount=1000, category="Groceries", date=date(2026, 3, 5)))
    expense_id = expense["id"]

    update_payload = ExpenseUpdate(amount=1250, note="Weekly shop")
    updated = update_expense(db_conn, expense_id, update_payload)
    assert updated is not None
    assert updated["amount"] == 1250
    assert updated["category"] == "groceries"
    assert updated["note"] == "Weekly shop"
    assert updated["date"] == "2026-03-05"


def test_update_expense_empty(db_conn):
    expense = create_expense(db_conn, ExpenseCreate(amount=1000, category="Groceries", date=date(2026, 3, 5), note="Original"))
    expense_id = expense["id"]

    updated = update_expense(db_conn, expense_id, ExpenseUpdate())
    assert updated is not None
    assert updated["amount"] == 1000
    assert updated["category"] == "groceries"
    assert updated["note"] == "Original"
    assert updated["date"] == "2026-03-05"


def test_update_expense_missing(db_conn):
    update_payload = ExpenseUpdate(amount=100)
    updated = update_expense(db_conn, 9999, update_payload)
    assert updated is None


def test_delete_expense(db_conn):
    expense = create_expense(db_conn, ExpenseCreate(amount=400, category="Misc", date=date(2026, 3, 20)))
    expense_id = expense["id"]

    result = delete_expense(db_conn, expense_id)
    assert result is True

    assert get_expense(db_conn, expense_id) is None


def test_delete_expense_missing(db_conn):
    result = delete_expense(db_conn, 9999)
    assert result is False


def test_list_expenses_end_date_inclusive(db_conn):
    create_expense(db_conn, ExpenseCreate(amount=100, category="Food", date=date(2026, 3, 10)))
    results = list_expenses(db_conn, start_date=date(2026, 3, 1), end_date=date(2026, 3, 10))
    assert len(results) == 1
    assert results[0]["amount"] == 100


def test_list_expenses_category_and_date_range(db_conn):
    create_expense(db_conn, ExpenseCreate(amount=100, category="Food", date=date(2026, 3, 5)))
    create_expense(db_conn, ExpenseCreate(amount=200, category="Transport", date=date(2026, 3, 5)))
    create_expense(db_conn, ExpenseCreate(amount=300, category="Food", date=date(2026, 3, 20)))

    results = list_expenses(db_conn, category="Food", start_date=date(2026, 3, 1), end_date=date(2026, 3, 10))
    assert len(results) == 1
    assert results[0]["amount"] == 100


def test_monthly_summary(db_conn):
    create_expense(db_conn, ExpenseCreate(amount=1000, category="Food", date=date(2026, 3, 2)))
    create_expense(db_conn, ExpenseCreate(amount=500, category="Food", date=date(2026, 3, 12)))
    create_expense(db_conn, ExpenseCreate(amount=2000, category="Utilities", date=date(2026, 3, 25)))
    # Different month
    create_expense(db_conn, ExpenseCreate(amount=3000, category="Food", date=date(2026, 4, 1)))

    summary = monthly_summary(db_conn, year=2026, month=3)
    assert summary == {"food": 1500, "utilities": 2000}


def test_monthly_summary_boundary_dates(db_conn):
    create_expense(db_conn, ExpenseCreate(amount=111, category="Food", date=date(2026, 12, 31)))
    create_expense(db_conn, ExpenseCreate(amount=222, category="Food", date=date(2027, 1, 1)))

    summary_dec = monthly_summary(db_conn, year=2026, month=12)
    assert summary_dec == {"food": 111}

    summary_jan = monthly_summary(db_conn, year=2027, month=1)
    assert summary_jan == {"food": 222}

def test_monthly_summary_no_expenses(db_conn):
    summary = monthly_summary(db_conn, year=2026, month=12)
    assert summary == {}

def test_monthly_summary_groups_case_variants(db_conn):
    create_expense(db_conn, ExpenseCreate(amount=100, category="Food", date=date(2026, 3, 2)))
    create_expense(db_conn, ExpenseCreate(amount=200, category="food", date=date(2026, 3, 5)))
    create_expense(db_conn, ExpenseCreate(amount=300, category=" FOOD ", date=date(2026, 3, 10)))

    summary = monthly_summary(db_conn, year=2026, month=3)
    assert summary == {"food": 600}


def test_build_update_sql_valid():
    data = {"amount": 500, "category": "Food"}
    set_clause, values = build_update_sql(data)
    assert "amount = ?" in set_clause
    assert "category = ?" in set_clause
    assert values == [500, "Food"]


def test_build_update_sql_invalid_column_id():
    data = {"id": 1, "amount": 500}
    with pytest.raises(ValueError, match="Unknown column: id"):
        build_update_sql(data)


def test_build_update_sql_invalid_column_injection():
    data = {"amount = 0, category": 500}
    with pytest.raises(ValueError, match="Unknown column: amount = 0, category"):
        build_update_sql(data)

