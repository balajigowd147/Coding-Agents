# Personal Expense Tracker API

## Overview
A lightweight REST API built with FastAPI and SQLite for tracking personal expenses.

## Features
- Create, read, update (PATCH), and delete expenses
- Filter expenses by category and date range
- Monthly expense summary breakdown by category

## Tech Stack
- Python 3.13, FastAPI, Pydantic v2, SQLite, pytest

## Setup
1. Create virtual environment: `python -m venv .venv`
2. Activate virtual environment: `.venv\Scripts\activate` (Windows) or `source .venv/bin/activate` (Unix)
3. Install dependencies: `pip install -r requirements.txt`

## Run
- Start server: `uvicorn main:app --reload`
- Interactive API Docs: `http://127.0.0.1:8000/docs`

## Run Tests
- Run test suite: `.venv\Scripts\pytest`

## Endpoints
| Method | Endpoint | Description |
|---|---|---|
| POST | `/expenses/` | Create a new expense |
| GET | `/expenses/` | List expenses (optional category, date filters) |
| GET | `/expenses/{id}` | Get expense by ID |
| PATCH | `/expenses/{id}` | Partially update an expense |
| DELETE | `/expenses/{id}` | Delete an expense |
| GET | `/expenses/summary/monthly` | Get monthly category breakdown |

## Design Decisions
- Amounts stored as integer paise (smallest currency unit) to avoid floating-point errors.
- Plain `sqlite3` with raw SQL queries and parameterized `?` placeholders (no ORM).
- Use `PATCH` for partial updates (rejecting explicit nulls for required fields, allowing null to clear notes).
- Test suite utilizes temporary SQLite databases (`tmp_path`, test client isolation).
