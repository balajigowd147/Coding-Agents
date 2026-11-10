import sys
import json
import pytest
from unittest.mock import patch
from pydantic import ValidationError
from google.genai import errors
import llm.ask
from llm.helpers import parse_expense_response
from schemas import ExpenseCreate


def test_command_b_handler(monkeypatch, capsys):
    canned_json = '{"amount": 150.0, "category": "Food", "date": "2026-11-10", "note": "lunch"}'
    monkeypatch.setattr(llm.ask, "call_gemini", lambda prompt, schema: canned_json)

    llm.ask.handle_b("lunch 150 rupees")

    captured = capsys.readouterr()
    data = json.loads(captured.out.strip())
    assert data["amount"] == 15000
    assert data["category"] == "Food"
    assert data["date"] == "2026-11-10"
    assert data["note"] == "lunch"


def test_main_missing_key(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.setattr(sys, "argv", ["llm.ask", "b", "lunch 150 rupees"])
    with pytest.raises(SystemExit) as exc_info:
        llm.ask.main()
    assert exc_info.value.code == 1


def test_main_validation_error(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "fake-key")
    canned_invalid_json = '{"amount": -50, "category": "Food", "date": "2026-11-10"}'
    monkeypatch.setattr(llm.ask, "call_gemini", lambda prompt, schema: canned_invalid_json)
    monkeypatch.setattr(sys, "argv", ["llm.ask", "b", "lunch -50 rupees"])

    with pytest.raises(SystemExit) as exc_info:
        llm.ask.main()
    assert exc_info.value.code == 1


def test_parse_expense_response_empty_none():
    with pytest.raises(ValueError, match="Model response was empty"):
        parse_expense_response(None)
    with pytest.raises(ValueError, match="Model response was empty"):
        parse_expense_response("")


def test_main_gemini_api_error(monkeypatch, capsys):
    monkeypatch.setenv("GEMINI_API_KEY", "super-secret-key-12345")
    def mock_call_gemini(prompt, schema):
        raise errors.APIError(code=400, response_json={"error": {"message": "Bad request super-secret-key-12345"}})
    monkeypatch.setattr(llm.ask, "call_gemini", mock_call_gemini)
    monkeypatch.setattr(sys, "argv", ["llm.ask", "b", "lunch 150 rupees"])

    with pytest.raises(SystemExit) as exc_info:
        llm.ask.main()
    assert exc_info.value.code == 1
    captured = capsys.readouterr()
    assert "Gemini request failed:" in captured.out
    assert "super-secret-key-12345" not in captured.out
    assert len(captured.out.strip().splitlines()) == 1


def test_main_validation_error_short_message(monkeypatch, capsys):
    monkeypatch.setenv("GEMINI_API_KEY", "fake-key")
    canned_invalid_json = '{"amount": "abc", "category": "Food", "date": "2026-11-10"}'
    monkeypatch.setattr(llm.ask, "call_gemini", lambda prompt, schema: canned_invalid_json)
    monkeypatch.setattr(sys, "argv", ["llm.ask", "b", "lunch invalid rupees"])

    with pytest.raises(SystemExit) as exc_info:
        llm.ask.main()
    assert exc_info.value.code == 1
    captured = capsys.readouterr()
    output = captured.out.strip()
    assert output.startswith("Invalid expense:")
    assert len(output.splitlines()) == 1
