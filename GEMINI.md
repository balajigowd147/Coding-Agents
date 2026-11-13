# Project Instructions

## Project
Personal Expense Tracker API built with FastAPI and SQLite to track income and expenses.

## Tech Stack
- Python 3.13
- FastAPI
- SQLite
- pytest

## Decisions
- Use plain sqlite3 with raw SQL. No SQLAlchemy, no ORM, no sessions.
- Store amount as an integer in paise (smallest currency unit).
- Use PATCH for partial updates, not PUT.
- Use Pydantic v2.
- Validation: amount > 0, category non-empty, valid date. Return 404 for missing expenses, 422 for invalid input.

## Engineering Rules & Conventions
- **Virtual Environment (.venv):** Always use the project's `.venv` virtual environment for running python, pytest, and uvicorn (`.venv\Scripts\python`, `.venv\Scripts\pytest`, `.venv\Scripts\uvicorn`).
- **Test-Driven Development:** Always write tests before implementing features or bug fixes.
- **Modularity:** Keep functions small, focused, and single-responsibility.
- **Environment Protection:** Never edit `.env` files directly or commit secrets.
- **Dependencies:** Always ask the user before installing any new packages.
- **Targeted Edits:** Prefer small targeted edits over rewriting whole files. Do exactly the step requested, then stop and wait.
- **Git & File Safety:** Never run `git checkout`, `git restore`, `git reset`, or `git clean` without asking the user first. Never delete files without asking.

## Commands
- **Create Virtual Environment:**
  - Windows: `python -m venv venv`
  - Unix/macOS: `python3 -m venv venv`
- **Activate Virtual Environment:**
  - Windows: `venv\Scripts\activate`
  - Unix/macOS: `source venv/bin/activate`
- **Install Dependencies:**
  - `pip install -r requirements.txt`
- **Run Application:**
  - `uvicorn main:app --reload`
- **Run Tests:**
  - `pytest`
