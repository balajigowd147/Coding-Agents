import pytest
from datetime import date
from decimal import Decimal
from pydantic import ValidationError
import database
import crud
from schemas import ExpenseCreate
from llm.helpers import (
    convert_rupees_to_paise,
    get_prompt_with_today,
    get_prompt_c_with_today,
    monthly_summary,
    build_expense,
    IntermediateExpense,
    get_api_key,
    parse_expense_response,
)


def test_convert_rupees_to_paise():
    assert convert_rupees_to_paise(19.99) == 1999
    assert convert_rupees_to_paise(12.50) == 1250
    assert convert_rupees_to_paise(100) == 10000
    assert convert_rupees_to_paise("19.99") == 1999
    assert convert_rupees_to_paise(1.005) == 101
    with pytest.raises(ValueError):
        convert_rupees_to_paise("abc")
    with pytest.raises(ValueError):
        convert_rupees_to_paise(0)
    with pytest.raises(ValueError):
        convert_rupees_to_paise(-5)


def test_build_expense():
    parsed = IntermediateExpense(amount=19.99, category="food", date="2026-03-15", note="test")
    expense = build_expense(parsed)
    assert isinstance(expense, ExpenseCreate)
    assert expense.amount == 1999
    assert expense.category == "food"
    assert expense.date == date(2026, 3, 15)
    assert expense.note == "test"

    with pytest.raises(ValidationError):
        build_expense(IntermediateExpense(amount=19.99, category="food", date="2026-13-45", note="invalid date"))

    with pytest.raises((ValueError, ValidationError)):
        build_expense(IntermediateExpense(amount=0, category="food", date="2026-03-15", note="zero amount"))


def test_get_prompt_with_today():
    prompt = get_prompt_with_today("Add an expense for yesterday")
    today_str = date.today().isoformat()
    assert today_str in prompt
    assert "Add an expense for yesterday" in prompt


def test_get_prompt_c_with_today():
    prompt = get_prompt_c_with_today("What was my spending?")
    today_str = date.today().isoformat()
    assert today_str in prompt
    assert "What was my spending?" in prompt


def test_monthly_summary_tool(capsys):
    database.init_db()
    conn = database.get_db_connection()
    crud.create_expense(conn, ExpenseCreate(amount=1500, category="food", date="2026-03-10", note="lunch"))
    crud.create_expense(conn, ExpenseCreate(amount=2500, category="food", date="2026-03-15", note="dinner"))
    crud.create_expense(conn, ExpenseCreate(amount=10000, category="rent", date="2026-03-01", note="march rent"))
    conn.close()

    summary = monthly_summary(2026, 3)
    assert summary == {"food": 4000, "rent": 10000}


def test_monthly_summary_print_format(capsys):
    database.init_db()
    monthly_summary(2026, 3)
    captured = capsys.readouterr()
    assert captured.out.strip() == "monthly_summary(year=2026, month=3)"


def test_monthly_summary_boundaries_and_empty(capsys):
    database.init_db()
    summary = monthly_summary(2026, 12)
    assert summary == {}

    summary_boundary = monthly_summary(2000, 1)
    assert summary_boundary == {}
    summary_boundary2 = monthly_summary(2100, 12)
    assert summary_boundary2 == {}


def test_monthly_summary_read_only(capsys):
    database.init_db()
    conn = database.get_db_connection()
    crud.create_expense(conn, ExpenseCreate(amount=1000, category="food", date="2026-03-01", note="n"))
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM expenses")
    count_before = cursor.fetchone()[0]
    conn.close()

    monthly_summary(2026, 3)

    conn = database.get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM expenses")
    count_after = cursor.fetchone()[0]
    conn.close()

    assert count_before == count_after


def test_monthly_summary_validation():
    database.init_db()
    with pytest.raises(ValueError):
        monthly_summary(1999, 3)
    with pytest.raises(ValueError):
        monthly_summary(2101, 3)
    with pytest.raises(ValueError):
        monthly_summary(2026, 0)
    with pytest.raises(ValueError):
        monthly_summary(2026, 13)


def test_get_api_key_missing(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    with pytest.raises(ValueError) as exc_info:
        get_api_key()
    assert "GEMINI_API_KEY" in str(exc_info.value)


def test_get_api_key_present(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "fake-test-value")
    assert get_api_key() == "fake-test-value"


def test_get_api_key_empty(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "")
    with pytest.raises(ValueError):
        get_api_key()


def test_parse_expense_response_valid():
    json_text = '{"amount": 19.99, "category": "Food", "date": "2026-11-08", "note": "lunch"}'
    expense = parse_expense_response(json_text)
    assert isinstance(expense, ExpenseCreate)
    assert expense.amount == 1999
    assert expense.category == "food"
    assert expense.date == date(2026, 11, 8)
    assert expense.note == "lunch"


def test_parse_expense_response_code_fence():
    fenced_text = '```json\n{"amount": 12.50, "category": "Travel", "date": "2026-11-08", "note": "bus"}\n```'
    expense = parse_expense_response(fenced_text)
    assert isinstance(expense, ExpenseCreate)
    assert expense.amount == 1250
    assert expense.category == "travel"


def test_parse_expense_response_invalid_date():
    json_text = '{"amount": 19.99, "category": "Food", "date": "2026-13-45", "note": "lunch"}'
    with pytest.raises(ValidationError):
        parse_expense_response(json_text)


def test_parse_expense_response_missing_amount():
    json_text = '{"category": "Food", "date": "2026-11-08", "note": "lunch"}'
    with pytest.raises((ValidationError, ValueError)):
        parse_expense_response(json_text)


def test_parse_expense_response_zero_amount():
    json_text = '{"amount": 0, "category": "Food", "date": "2026-11-08", "note": "lunch"}'
    with pytest.raises((ValidationError, ValueError)):
        parse_expense_response(json_text)


def test_parse_expense_response_negative_amount():
    json_text = '{"amount": -10.00, "category": "Food", "date": "2026-11-08", "note": "refund"}'
    with pytest.raises((ValidationError, ValueError)):
        parse_expense_response(json_text)


def test_parse_expense_response_not_object():
    for non_obj in ['[]', 'null', '"string"', '123']:
        with pytest.raises(ValueError):
            parse_expense_response(non_obj)


def test_parse_expense_response_invalid_json():
    not_json = "this is not json at all"
    with pytest.raises(ValueError) as exc_info:
        parse_expense_response(not_json)
    assert "json" in str(exc_info.value).lower()


def test_parse_expense_response_empty():
    for empty_val in [None, "", "   "]:
        with pytest.raises(ValueError, match="Model response was empty"):
            parse_expense_response(empty_val)





