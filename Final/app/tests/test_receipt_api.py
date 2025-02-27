from dataclasses import dataclass, field
from typing import Any, Dict
from uuid import UUID, uuid4

import pytest
from faker import Faker
from fastapi.testclient import TestClient

from app.core.currency import Currency
from app.core.Models.product import Product
from app.core.Models.receipt import ReceiptState
from app.infrastructure.sqlite.inmemory.producs_in_memory_db import InMemoryProductDb
from app.infrastructure.sqlite.inmemory.receipt_in_memory_db import InMemoryReceiptDb
from app.infrastructure.sqlite.inmemory.receipt_item_in_memory_db import (
    InMemoryReceiptItemDb,
)
from app.runner.setup import init_app


@dataclass
class ReceiptFake:
    faker: Faker = field(default_factory=Faker)

    def add_item_request(self, product_id: UUID) -> Dict[str, Any]:
        return {
            "product_id": str(product_id),
            "quantity": self.faker.random_int(min=1, max=10)
        }

    def payment_request(self, amount: float) -> Dict[str, Any]:
        return {
            "amount": amount,
            "currency": Currency.GEL.value
        }

    def quote_request(self) -> Dict[str, Any]:
        return {
            "currency": Currency.USD.value
        }


@dataclass
class ProductFake:
    faker: Faker = field(default_factory=Faker)

    def product(self) -> Dict[str, Any]:
        return {
            "name": self.faker.word(),
            "price": self.faker.random_int(min=10, max=1000)
        }

    def get_model(self) -> Product:
        return Product(
            name=self.faker.word(),
            id=uuid4(),
            price=self.faker.random_int(min=10, max=1000)
        )


@pytest.fixture
def client() -> TestClient:
    app = init_app("in_memory")
    return TestClient(app)


def clear_tables() -> None:
    InMemoryProductDb().clear()
    InMemoryReceiptDb().receipts.clear()
    InMemoryReceiptItemDb().receipt_items.clear()


def create_product(client: TestClient) -> Any:
    product = ProductFake().product()
    response = client.post("/products", json=product)
    product_id = response.json()["product"]
    response = client.get(f"/products/{product_id}")
    return response.json()["product"]


def test_should_create_receipt(client: TestClient) -> None:
    clear_tables()
    client.post("/shifts/open")
    response = client.post("/newReceipt")

    assert response.status_code == 201
    assert "receipt_id" in response.json()


def test_shift_not_open_error(client: TestClient) -> None:
    clear_tables()
    response = client.post("/newReceipt")

    assert response.status_code == 400
    assert "Shift is not open" in response.json()["detail"]["error"]["message"]


def test_should_not_add_item_to_unknown_receipt(client: TestClient) -> None:
    clear_tables()
    product = create_product(client)
    unknown_receipt_id = uuid4()
    add_request = ReceiptFake().add_item_request(UUID(product["id"]))

    response = client.post(f"/receipts/addItem/{unknown_receipt_id}", json=add_request)

    assert response.status_code == 400
    assert "does not exist" in response.json()["detail"]["error"]["message"]


def test_should_add_item_to_receipt(client: TestClient) -> None:
    clear_tables()
    product = create_product(client)
    client.post("/shifts/open")

    receipt_response = client.post("/newReceipt")
    receipt_id = receipt_response.json()["receipt_id"]

    add_request = ReceiptFake().add_item_request(UUID(product["id"]))
    response = client.post(f"/receipts/addItem/{receipt_id}", json=add_request)

    assert response.status_code == 200

    get_response = client.get(f"/receipts/{receipt_id}")
    assert get_response.status_code == 200
    assert len(get_response.json()["items"]) == 1
    assert get_response.json()["items"][0]["id"] == product["id"]
    assert get_response.json()["items"][0]["quantity"] == add_request["quantity"]


def test_should_calculate_total(client: TestClient) -> None:
    clear_tables()
    product = create_product(client)
    client.post("/shifts/open")
    receipt_response = client.post("/newReceipt")
    receipt_id = receipt_response.json()["receipt_id"]

    add_request = ReceiptFake().add_item_request(UUID(product["id"]))
    add_request["quantity"] = 2  # Ensure we know the quantity
    client.post(f"/receipts/addItem/{receipt_id}", json=add_request)

    response = client.get(f"/receipts/calculate/{receipt_id}")

    assert response.status_code == 200
    assert "total" in response.json()


def test_payment_processing(client: TestClient) -> None:
    clear_tables()
    product = create_product(client)
    client.post("/shifts/open")

    receipt_response = client.post("/newReceipt")
    receipt_id = receipt_response.json()["receipt_id"]

    add_request = ReceiptFake().add_item_request(UUID(product["id"]))
    add_request["quantity"] = 1
    client.post(f"/receipts/addItem/{receipt_id}", json=add_request)

    get_response = client.get(f"/receipts/{receipt_id}")
    total = get_response.json()["total"]

    payment_request = ReceiptFake().payment_request(total)
    response = client.post(f"/receipts/pay/{receipt_id}", json=payment_request)

    assert response.status_code == 200

    get_response = client.get(f"/receipts/{receipt_id}")
    assert get_response.json()["state"] == ReceiptState.PAYED.value


def test_should_close_receipt(client: TestClient) -> None:
    clear_tables()
    product = create_product(client)
    client.post("/shifts/open")

    receipt_response = client.post("/newReceipt")
    receipt_id = receipt_response.json()["receipt_id"]

    add_request = ReceiptFake().add_item_request(UUID(product["id"]))
    client.post(f"/receipts/addItem/{receipt_id}", json=add_request)

    get_response = client.get(f"/receipts/{receipt_id}")
    total = get_response.json()["total"]

    payment_request = ReceiptFake().payment_request(total)
    client.post(f"/receipts/pay/{receipt_id}", json=payment_request)

    response = client.post(f"/receipts/close/{receipt_id}")

    assert response.status_code == 200

    get_response = client.get(f"/receipts/{receipt_id}")
    assert get_response.json()["state"] == ReceiptState.CLOSED.value


def test_should_not_close_unpaid_receipt(client: TestClient) -> None:
    clear_tables()
    product = create_product(client)
    client.post("/shifts/open")

    receipt_response = client.post("/newReceipt")
    receipt_id = receipt_response.json()["receipt_id"]

    add_request = ReceiptFake().add_item_request(UUID(product["id"]))
    client.post(f"/receipts/addItem/{receipt_id}", json=add_request)

    response = client.post(f"/receipts/close/{receipt_id}")

    assert response.status_code == 400
    assert "state" in response.json()["detail"]["error"]["message"]
