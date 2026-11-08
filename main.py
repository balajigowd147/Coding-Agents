from fastapi import FastAPI, Depends, HTTPException, status, Query
import sqlite3
from datetime import date
from typing import Optional, List
from contextlib import asynccontextmanager
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


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Personal Expense Tracker API", lifespan=lifespan)


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
    return monthly_summary(db, year=year, month=month)
