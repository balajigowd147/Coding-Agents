import pytest
from fastapi.testclient import TestClient
from datetime import date
from database import init_db, get_db_connection
from main import app, get_db


@pytest.fixture
def client(tmp_path):
    db_file = tmp_path / "test_expenses.db"
    init_db(db_path=str(db_file))

    def override_get_db():
        conn = get_db_connection(db_path=str(db_file))
        try:
            yield conn
        finally:
            conn.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def test_create_expense(client):
    response = client.post(
        "/expenses/",
        json={
            "amount": 1500,
            "category": "Food",
            "date": "2026-03-10",
            "note": "Lunch",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["amount"] == 1500
    assert data["category"] == "Food"
    assert data["date"] == "2026-03-10"
    assert data["note"] == "Lunch"
    assert "id" in data


def test_create_expense_invalid_data(client):
    # amount <= 0 should fail validation (422)
    response = client.post(
        "/expenses/",
        json={
            "amount": 0,
            "category": "Food",
            "date": "2026-03-10",
        },
    )
    assert response.status_code == 422


def test_get_expense(client):
    create_res = client.post(
        "/expenses/",
        json={
            "amount": 2000,
            "category": "Transport",
            "date": "2026-03-11",
        },
    )
    expense_id = create_res.json()["id"]

    response = client.get(f"/expenses/{expense_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == expense_id
    assert data["amount"] == 2000


def test_get_expense_not_found(client):
    response = client.get("/expenses/9999")
    assert response.status_code == 404


def test_list_expenses_with_category_filter(client):
    client.post(
        "/expenses/",
        json={"amount": 100, "category": "Food", "date": "2026-03-01"},
    )
    client.post(
        "/expenses/",
        json={"amount": 200, "category": "Bills", "date": "2026-03-02"},
    )

    response = client.get("/expenses/?category=Food")
    assert response.status_code == 200
    items = response.json()
    assert len(items) == 1
    assert items[0]["category"] == "Food"


def test_patch_expense(client):
    create_res = client.post(
        "/expenses/",
        json={"amount": 500, "category": "Food", "date": "2026-03-01"},
    )
    expense_id = create_res.json()["id"]

    response = client.patch(
        f"/expenses/{expense_id}",
        json={"amount": 600},
    )
    assert response.status_code == 200
    assert response.json()["amount"] == 600


def test_patch_expense_not_found(client):
    response = client.patch(
        "/expenses/9999",
        json={"amount": 600},
    )
    assert response.status_code == 404


def test_patch_expense_invalid_amount(client):
    create_res = client.post(
        "/expenses/",
        json={"amount": 500, "category": "Food", "date": "2026-03-01"},
    )
    expense_id = create_res.json()["id"]

    response = client.patch(
        f"/expenses/{expense_id}",
        json={"amount": 0},
    )
    assert response.status_code == 422


def test_delete_expense(client):
    create_res = client.post(
        "/expenses/",
        json={"amount": 500, "category": "Food", "date": "2026-03-01"},
    )
    expense_id = create_res.json()["id"]

    response = client.delete(f"/expenses/{expense_id}")
    assert response.status_code == 204

    get_res = client.get(f"/expenses/{expense_id}")
    assert get_res.status_code == 404


def test_delete_expense_not_found(client):
    response = client.delete("/expenses/9999")
    assert response.status_code == 404


def test_monthly_summary(client):
    client.post(
        "/expenses/",
        json={"amount": 1000, "category": "Food", "date": "2026-03-05"},
    )
    client.post(
        "/expenses/",
        json={"amount": 2500, "category": "Rent", "date": "2026-03-15"},
    )
    client.post(
        "/expenses/",
        json={"amount": 500, "category": "Food", "date": "2026-04-01"},
    )

    response = client.get("/expenses/summary/monthly?year=2026&month=3")
    assert response.status_code == 200
    summary = response.json()
    assert summary["year"] == 2026
    assert summary["month"] == 3
    assert summary["total"] == 3500
    assert summary["count"] == 2
