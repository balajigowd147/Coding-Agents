import pytest
from pathlib import Path


@pytest.fixture(autouse=True)
def set_env_db(monkeypatch, tmp_path):
    db_file = tmp_path / "test_expenses.db"
    monkeypatch.setenv("EXPENSES_DB", str(db_file))


@pytest.fixture(autouse=True, scope="session")
def check_no_default_db_created():
    yield
    db_path = Path("expenses.db")
    assert not db_path.exists(), f"Found {db_path.name} in project root after test run!"
