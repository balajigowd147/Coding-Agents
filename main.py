from fastapi import FastAPI, Depends, HTTPException, status, Query
import sqlite3
from datetime import date
from typing import Optional, List
from database import get_db_connection, init_db
from schemas import ExpenseCreate, ExpenseUpdate
from crud import (
    create_expense,
    get_expense,
    list_expenses,
    update_expense,
    delete_expense,
    monthly_summary,
)

app = FastAPI(title="Personal Expense Tracker API")


@app.on_event("startup")
def startup_event():
    init_db()


def get_db():
    conn = get_db_connection()
    try:
        yield conn
    finally:
        conn.close()


@app.post("/expenses/", status_code=status.HTTP_201_CREATED, response_model=dict)
def create_new_expense(expense: ExpenseCreate, db: sqlite3.Connection = Depends(get_db)):
    return create_expense(db, expense)


@app.get("/expenses/", response_model=List[dict])
def read_expenses(
    category: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: sqlite3.Connection = Depends(get_db),
):
    return list_expenses(db, category=category, start_date=start_date, end_date=end_date)


@app.get("/expenses/{expense_id}", response_model=dict)
def read_expense(expense_id: int, db: sqlite3.Connection = Depends(get_db)):
    expense = get_expense(db, expense_id)
    if expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense


@app.patch("/expenses/{expense_id}", response_model=dict)
def patch_expense(
    expense_id: int,
    payload: ExpenseUpdate,
    db: sqlite3.Connection = Depends(get_db),
):
    expense = update_expense(db, expense_id, payload)
    if expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense


@app.delete("/expenses/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_expense(expense_id: int, db: sqlite3.Connection = Depends(get_db)):
    success = delete_expense(db, expense_id)
    if not success:
        raise HTTPException(status_code=404, detail="Expense not found")
    return None


@app.get("/expenses/summary/monthly", response_model=dict)
def get_monthly_summary(
    year: int = Query(..., ge=2000, le=2100),
    month: int = Query(..., ge=1, le=12),
    db: sqlite3.Connection = Depends(get_db),
):
    breakdown = monthly_summary(db, year=year, month=month)
    total = sum(breakdown.values())
    count_items = list_expenses(
        db,
        start_date=date(year, month, 1),
        end_date=date(
            year + 1, 1, 1
        ) if month == 12 else date(year, month + 1, 1),
    )
    # Filter count items strictly for the given month/year
    # Actually, list_expenses returns items matching start/end date.
    # Let's count expenses whose date starts with year-month prefix or matching month.
    # Or count from breakdown sum of counts? Wait, let's query db or count list items.
    all_in_month = [
        item for item in list_expenses(db)
        if item["date"].startswith(f"{year:04d}-{month:02d}")
    ]
    total_amount = sum(item["amount"] for item in all_in_month)
    count = len(all_in_month)

    return {
        "year": year,
        "month": month,
        "total": total_amount,
        "count": count,
        "by_category": breakdown,
    }
