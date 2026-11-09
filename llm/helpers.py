from datetime import date
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from typing import Optional
from pydantic import BaseModel
import database
from crud import monthly_summary as crud_monthly_summary
from schemas import ExpenseCreate


class IntermediateExpense(BaseModel):
    amount: float
    category: str
    date: str
    note: Optional[str] = None


def convert_rupees_to_paise(amount: float | str | int) -> int:
    try:
        d = Decimal(str(amount))
    except (InvalidOperation, ValueError, TypeError):
        raise ValueError("Invalid amount")
    if d <= 0:
        raise ValueError("Amount must be positive")
    paise_d = (d * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    return int(paise_d)


def build_expense(parsed: IntermediateExpense) -> ExpenseCreate:
    paise = convert_rupees_to_paise(parsed.amount)
    return ExpenseCreate(
        amount=paise,
        category=parsed.category,
        date=parsed.date,
        note=parsed.note,
    )


def monthly_summary(year: int, month: int) -> dict:
    """
    Get monthly summary of expenses by category.

    Args:
        year (int): The 4-digit year (2000-2100).
        month (int): The month (1-12).

    Returns:
        dict: Mapping of category names to total amount in paise.
    """
    if not (isinstance(year, int) and 2000 <= year <= 2100):
        raise ValueError("Year must be between 2000 and 2100")
    if not (isinstance(month, int) and 1 <= month <= 12):
        raise ValueError("Month must be between 1 and 12")

    print(f"monthly_summary(year={year}, month={month})")

    conn = database.get_db_connection()
    try:
        return crud_monthly_summary(conn, year, month)
    finally:
        conn.close()


def get_prompt_with_today(text: str) -> str:
    today_str = date.today().isoformat()
    return f"Today's date is {today_str}.\n\n{text}"


def get_prompt_c_with_today(text: str) -> str:
    today_str = date.today().isoformat()
    return f"Today's date is {today_str}.\n\n{text}"
