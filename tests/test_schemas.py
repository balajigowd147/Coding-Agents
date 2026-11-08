import pytest
from datetime import date
from pydantic import ValidationError
from schemas import ExpenseCreate, ExpenseUpdate


def test_expense_create_valid():
    expense = ExpenseCreate(
        amount=1000,
        category="Food",
        date=date(2026, 3, 30),
        note="Dinner"
    )
    assert expense.amount == 1000
    assert expense.category == "Food"
    assert expense.date == date(2026, 3, 30)
    assert expense.note == "Dinner"


def test_expense_create_valid_no_note():
    expense = ExpenseCreate(
        amount=500,
        category="Transport",
        date="2026-03-31"
    )
    assert expense.amount == 500
    assert expense.category == "Transport"
    assert expense.date == date(2026, 3, 31)
    assert expense.note is None


@pytest.mark.parametrize("amount", [0, -100, -1])
def test_expense_create_invalid_amount(amount):
    with pytest.raises(ValidationError):
        ExpenseCreate(amount=amount, category="Food", date="2026-03-30")


def test_expense_create_missing_amount():
    with pytest.raises(ValidationError):
        ExpenseCreate(category="Food", date="2026-03-30")


@pytest.mark.parametrize("amount", [10.5, "abc"])
def test_expense_create_non_integer_amount(amount):
    with pytest.raises(ValidationError):
        ExpenseCreate(amount=amount, category="Food", date="2026-03-30")


@pytest.mark.parametrize("category", ["", "   "])
def test_expense_create_invalid_category(category):
    with pytest.raises(ValidationError):
        ExpenseCreate(amount=100, category=category, date="2026-03-30")


@pytest.mark.parametrize("bad_date", ["not-a-date", "2026-13-40", "2026/03/30"])
def test_expense_create_invalid_date(bad_date):
    with pytest.raises(ValidationError):
        ExpenseCreate(amount=100, category="Food", date=bad_date)


def test_expense_update_empty():
    update_data = ExpenseUpdate()
    assert update_data.amount is None
    assert update_data.category is None
    assert update_data.date is None
    assert update_data.note is None


def test_expense_update_partial():
    update_data = ExpenseUpdate(amount=2000)
    assert update_data.amount == 2000
    assert update_data.category is None


@pytest.mark.parametrize("amount", [0, -50])
def test_expense_update_invalid_amount(amount):
    with pytest.raises(ValidationError):
        ExpenseUpdate(amount=amount)


@pytest.mark.parametrize("category", ["", "   "])
def test_expense_update_invalid_category(category):
    with pytest.raises(ValidationError):
        ExpenseUpdate(category=category)


def test_expense_update_invalid_date():
    with pytest.raises(ValidationError):
        ExpenseUpdate(date="bad-date")


def test_expense_update_valid_date_string():
    update_data = ExpenseUpdate(date="2026-03-31")
    assert update_data.date == date(2026, 3, 31)


def test_expense_update_valid_date_object():
    update_data = ExpenseUpdate(date=date(2026, 3, 31))
    assert update_data.date == date(2026, 3, 31)
