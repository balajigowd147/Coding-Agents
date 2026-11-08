import os
import sqlite3

DATABASE_NAME = "expenses.db"


def get_db_connection(db_path: str = DATABASE_NAME):
    resolved_path = os.environ.get("EXPENSES_DB", "expenses.db") if (db_path is None or db_path == DATABASE_NAME) else db_path
    conn = sqlite3.connect(resolved_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str = DATABASE_NAME):
    resolved_path = os.environ.get("EXPENSES_DB", "expenses.db") if (db_path is None or db_path == DATABASE_NAME) else db_path
    conn = get_db_connection(resolved_path)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount INTEGER NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL,
            note TEXT
        )
    """
    )
    conn.commit()
    conn.close()
