import sqlite3
from datetime import date
from typing import Optional, List, Dict, Any
from schemas import ExpenseCreate, ExpenseUpdate


def create_expense(conn: sqlite3.Connection, expense: ExpenseCreate) -> dict:
    cursor = conn.cursor()
    date_str = expense.date.isoformat() if isinstance(expense.date, date) else str(expense.date)
    cursor.execute(
        "INSERT INTO expenses (amount, category, date, note) VALUES (?, ?, ?, ?)",
        (expense.amount, expense.category, date_str, expense.note),
    )
    conn.commit()
    expense_id = cursor.lastrowid
    return get_expense(conn, expense_id)


UPDATABLE_COLUMNS = ("amount", "category", "date", "note")


def build_update_sql(update_data: Dict[str, Any]) -> tuple[str, List[Any]]:
    set_clauses = []
    params: List[Any] = []
    for field, value in update_data.items():
        if field not in UPDATABLE_COLUMNS:
            raise ValueError(f"Unknown column: {field}")
        if field == "date" and isinstance(value, date):
            value = value.isoformat()
        set_clauses.append(f"{field} = ?")
        params.append(value)
    return ", ".join(set_clauses), params


def get_expense(conn: sqlite3.Connection, expense_id: int) -> Optional[dict]:
    cursor = conn.cursor()
    cursor.execute("SELECT id, amount, category, date, note FROM expenses WHERE id = ?", (expense_id,))
    row = cursor.fetchone()
    if row is None:
        return None
    return dict(row)


def list_expenses(
    conn: sqlite3.Connection,
    category: Optional[str] = None,
    start_date: Optional[date | str] = None,
    end_date: Optional[date | str] = None,
) -> List[dict]:
    cursor = conn.cursor()
    query = "SELECT id, amount, category, date, note FROM expenses WHERE 1=1"
    params: List[Any] = []

    if category is not None:
        query += " AND category = ?"
        params.append(category.strip().lower() if isinstance(category, str) else category)

    if start_date is not None:
        start_str = start_date.isoformat() if isinstance(start_date, date) else str(start_date)
        query += " AND date >= ?"
        params.append(start_str)

    if end_date is not None:
        end_str = end_date.isoformat() if isinstance(end_date, date) else str(end_date)
        query += " AND date <= ?"
        params.append(end_str)

    query += " ORDER BY date DESC, id DESC"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    return [dict(row) for row in rows]


def update_expense(
    conn: sqlite3.Connection, expense_id: int, payload: ExpenseUpdate
) -> Optional[dict]:
    existing = get_expense(conn, expense_id)
    if existing is None:
        return None

    update_data = payload.model_dump(exclude_unset=True)
    if not update_data:
        return existing

    set_clause, params = build_update_sql(update_data)
    params.append(expense_id)
    # Column names come from an allowlist and the values use ? placeholders
    query = f"UPDATE expenses SET {set_clause} WHERE id = ?"  # nosec B608

    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()

    return get_expense(conn, expense_id)


def delete_expense(conn: sqlite3.Connection, expense_id: int) -> bool:
    cursor = conn.cursor()
    cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    conn.commit()
    return cursor.rowcount > 0


def monthly_summary(conn: sqlite3.Connection, year: int, month: int) -> Dict[str, int]:
    cursor = conn.cursor()
    month_prefix = f"{year:04d}-{month:02d}"
    cursor.execute(
        """
        SELECT LOWER(category) as cat_lower, SUM(amount) as total
        FROM expenses
        WHERE substr(date, 1, 7) = ?
        GROUP BY category
        """,
        (month_prefix,),
    )
    rows = cursor.fetchall()
    summary = {}
    for row in rows:
        cat = row["cat_lower"] if isinstance(row, sqlite3.Row) else row[0]
        tot = row["total"] if isinstance(row, sqlite3.Row) else row[1]
        summary[cat] = int(tot) if tot is not None else 0
    return summary
