import sys
import json
import pytest
from unittest.mock import patch
from pydantic import ValidationError
import llm.ask
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
