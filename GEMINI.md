# Project Instructions

## Project
Personal Expense Tracker API built with FastAPI and SQLite to track income and expenses.

## Tech Stack
- Python 3.12
- FastAPI
- SQLite
- pytest

## Engineering Rules & Conventions
- **Test-Driven Development:** Always write tests before implementing features or bug fixes.
- **Modularity:** Keep functions small, focused, and single-responsibility.
- **Environment Protection:** Never edit `.env` files directly or commit secrets.
- **Dependencies:** Always ask the user before installing any new packages.

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
