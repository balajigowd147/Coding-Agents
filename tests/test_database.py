
import sqlite3
import pytest
from database import get_db_connection, init_db


def test_init_db(tmp_path):
    db_file = tmp_path / "test_expenses.db"
    init_db(db_path=str(db_file))
    conn = get_db_connection(db_path=str(db_file))
    cursor = conn.cursor()
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='expenses';"
    )
    table = cursor.fetchone()
    conn.close()
    assert table is not None
    assert table["name"] == "expenses"


def test_db_connection_insert_and_query(tmp_path):
    db_file = tmp_path / "test_expenses.db"
    init_db(db_path=str(db_file))
    conn = get_db_connection(db_path=str(db_file))
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO expenses (amount, category, date, note) VALUES (?, ?, ?, ?)",
        (1500, "Food", "2026-03-30", "Lunch"),
    )
    conn.commit()

    cursor.execute("SELECT * FROM expenses WHERE category = ?", ("Food",))
    row = cursor.fetchone()
    conn.close()

    assert row is not None
    assert row["amount"] == 1500
    assert row["category"] == "Food"
    assert row["date"] == "2026-03-30"
    assert row["note"] == "Lunch"
