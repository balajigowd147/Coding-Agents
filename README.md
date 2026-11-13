# Personal Expense Tracker API
![CI](https://github.com/balajigowd147/expense-tracker-api/actions/workflows/ci.yml/badge.svg)

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

## Run with Docker
- Build image: `docker build -t expense-api .`
- Run container: `docker run -d --name expense-api -p 8000:8000 -v expense-data:/data expense-api`
- API Docs: `http://127.0.0.1:8000/docs`
- Stop and remove: `docker rm -f expense-api`
- The database lives in the named volume `expense-data` and survives container removal.
- The image contains no API keys and does not include the `llm/` script.

## Run Tests
- Run test suite: `.venv\Scripts\pytest`

## CI and Security
- **CI Jobs:** Test suite (`pytest`), Security (`pip-audit`, `bandit`), Docker smoke test (builds image, checks non-root execution, executes POST and GET).
- **Dependabot:** Weekly dependency updates.

## Endpoints
| Method | Endpoint | Description |
|---|---|---|
| POST | `/expenses/` | Create a new expense |
| GET | `/expenses/` | List expenses (optional category, date filters) |
| GET | `/expenses/{id}` | Get expense by ID |
| PATCH | `/expenses/{id}` | Partially update an expense |
| DELETE | `/expenses/{id}` | Delete an expense |
| GET | `/expenses/summary/monthly` | Get monthly category breakdown |

## LLM Script (`llm/ask.py`)
- **Install:** `.venv\Scripts\python -m pip install -r llm/requirements.txt`
- **Config:** Set `GEMINI_API_KEY` as an environment variable (never in a file).
- **Commands:**
  - `a`: `python -m llm.ask a "Hello"` (query LLM)
  - `b`: `python -m llm.ask b "Spent 500 on food"` (parses expense to JSON, prints only and never saves)
  - `c`: `python -m llm.ask c "Show monthly summary"` (uses one read-only tool: `monthly_summary`)
- **Design Decisions:** Model output is untrusted and validated; rupees converted to paise in code.

## Design Decisions
- Amounts stored as integer paise (smallest currency unit) to avoid floating-point errors.
- Plain `sqlite3` with raw SQL queries and parameterized `?` placeholders (no ORM).
- Use `PATCH` for partial updates (rejecting explicit nulls for required fields, allowing null to clear notes).
- Test suite utilizes temporary SQLite databases (`tmp_path`, test client isolation).
