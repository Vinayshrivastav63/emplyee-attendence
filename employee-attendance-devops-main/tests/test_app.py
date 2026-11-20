
import pytest
from unittest.mock import patch
from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_homepage(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Attendify" in response.data


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json["status"] == "OK"


@patch("app.get_employees")
def test_get_employees(mock_get, client):
    mock_get.return_value = [
        {"id": 1, "name": "Rahul", "email": "rahul@example.com",
         "department": "IT"}
    ]

    response = client.get("/api/employees")

    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]["name"] == "Rahul"


@patch("app.add_employee")
def test_add_employee(mock_add, client):
    mock_add.return_value = {
        "id": 1,
        "name": "Rahul",
        "email": "rahul@example.com",
        "department": "IT"
    }

    response = client.post("/api/employees", json={
        "name": "Rahul",
        "email": "rahul@example.com",
        "department": "IT"
    })

    assert response.status_code in (200, 201)
    mock_add.assert_called_once()


def test_add_employee_invalid_data(client):
    response = client.post("/api/employees", json={
        "name": "",
        "email": "",
        "department": ""
    })

    assert response.status_code == 400


@patch("app.get_attendance")
def test_get_attendance(mock_get, client):
    mock_get.return_value = []

    response = client.get("/api/attendance")

    assert response.status_code == 200
    assert response.json == []


def test_mark_attendance_invalid_status(client):
    response = client.post("/api/attendance", json={
        "employee_id": 1,
        "status": "Holiday"
    })

    assert response.status_code == 400


@patch("app.mark_attendance")
def test_mark_attendance(mock_mark, client):
    mock_mark.return_value = {"message": "Attendance marked successfully"}

    response = client.post("/api/attendance", json={
        "employee_id": 1,
        "status": "Present"
    })

    assert response.status_code in (200, 201)
    mock_mark.assert_called_once()
