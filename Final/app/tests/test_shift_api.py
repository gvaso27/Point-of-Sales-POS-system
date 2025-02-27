import pytest
from fastapi.testclient import TestClient

from app.infrastructure.sqlite.inmemory.shift_in_memory_db import InMemoryShiftDb
from app.runner.setup import init_app


def clear_tables() -> None:
    InMemoryShiftDb().shifts.clear()


@pytest.fixture
def client() -> TestClient:
    app = init_app("in_memory")
    return TestClient(app)


def test_should_open_shift(client: TestClient) -> None:
    clear_tables()
    response = client.post("/shifts/open")
    assert response.status_code == 201
    assert "shift_id" in response.json()


def test_shift_not_open_error(client: TestClient) -> None:
    clear_tables()
    response = client.post("/newReceipt")
    assert response.status_code == 400
    assert "Shift is not open" in response.json()["detail"]["error"]["message"]


def test_should_get_shift_state(client: TestClient) -> None:
    clear_tables()
    shift_response = client.post("/shifts/open")
    shift_id = shift_response.json()["shift_id"]
    response = client.get(f"/shifts/state/{shift_id}")
    assert response.status_code == 200
    assert "shift_id" in response.json()
    assert response.json()["state"] == "OPEN"


def test_should_close_shift(client: TestClient) -> None:
    clear_tables()
    shift_response = client.post("/shifts/open")
    shift_id = shift_response.json()["shift_id"]
    response = client.post(f"/shifts/close/{shift_id}")
    assert response.status_code == 200

    response = client.get(f"/shifts/state/{shift_id}")
    assert response.status_code == 200
    assert response.json()["state"] == "CLOSED"


def test_should_generate_x_report(client: TestClient) -> None:
    clear_tables()
    client.post("/shifts/open")
    response = client.get("/shifts/x-reports")
    assert response.status_code == 200
    assert "receipt_number" in response.json()


def test_should_generate_z_report(client: TestClient) -> None:
    clear_tables()
    client.post("/shifts/open")
    response = client.get("/shifts/z-reports")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
