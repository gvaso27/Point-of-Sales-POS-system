from dataclasses import dataclass, field
from typing import Any, Dict
from uuid import UUID, uuid4

import pytest
from faker import Faker
from fastapi.testclient import TestClient

from app.core.currency import Currency
from app.core.receipt import ReceiptState
from app.infrastructure.sqlite.inmemory.producs_in_memory_db import InMemoryProductDb
from app.runner.setup import init_app


@dataclass
class ReceiptFake:
    faker: Faker = field(default_factory=Faker)

    def product(self) -> Dict[str, Any]:
        return {
            "id": str(uuid4()),
            "name": self.faker.word(),
            "price": self.faker.random_number(digits=3)
        }

    def add_item_request(self, product_id: UUID) -> Dict[str, Any]:
        return {
            "product_id": str(product_id),
            "quantity": self.faker.random_int(min=1, max=10)
        }

    def quote_request(self, currency: Currency = Currency.USD) -> Dict[str, Any]:
        return {
            "currency": currency.value
        }

    def payment_request(self,
                        amount: float,
                        currency: Currency = Currency.GEL) -> Dict[str, Any]:
        return {
            "amount": amount,
            "currency": currency.value
        }


@pytest.fixture
def client() -> TestClient:
    return TestClient(init_app("in_memory"))


def clear_tables() -> None:
    InMemoryProductDb().clear()


def create_product(client: TestClient) -> UUID:
    product = ReceiptFake().product()
    response = client.post("/products", json=product)
    assert response.status_code == 201
    return UUID(response.json()["product"])


def test_create_receipt(client: TestClient) -> None:
    clear_tables()

    response = client.post("/receipts")

    assert response.status_code == 201
    assert "receipt_id" in response.json()
    receipt_id = response.json()["receipt_id"]

    response = client.get(f"/receipts/{receipt_id}")
    assert response.status_code == 200
    assert response.json()["receipt"]["id"] == receipt_id
    assert response.json()["receipt"]["state"] == ReceiptState.OPEN.value
    assert response.json()["receipt"]["items"] == []


def test_add_item_to_receipt(client: TestClient) -> None:
    clear_tables()

    product_id = create_product(client)
    response = client.post("/receipts")
    receipt_id = response.json()["receipt_id"]

    add_item_request = ReceiptFake().add_item_request(product_id)
    response = client.post(f"/receipts/{receipt_id}/products", json=add_item_request)
    assert response.status_code == 200

    response = client.get(f"/receipts/{receipt_id}")
    assert response.status_code == 200
    assert len(response.json()["receipt"]["items"]) == 1
    assert (response.json()["receipt"]["items"][0]["quantity"]
            == add_item_request["quantity"])


def test_calculate_total(client: TestClient) -> None:
    clear_tables()

    product_id = create_product(client)
    response = client.post("/receipts")
    receipt_id = response.json()["receipt_id"]

    add_item_request = ReceiptFake().add_item_request(product_id)
    client.post(f"/receipts/{receipt_id}/products", json=add_item_request)

    response = client.post(f"/receipts/{receipt_id}/calculate")
    assert response.status_code == 200
    assert "total" in response.json()
    assert isinstance(response.json()["total"], float)


def test_get_quote(client: TestClient) -> None:
    clear_tables()

    product_id = create_product(client)
    response = client.post("/receipts")
    receipt_id = response.json()["receipt_id"]

    add_item_request = ReceiptFake().add_item_request(product_id)
    client.post(f"/receipts/{receipt_id}/products", json=add_item_request)

    quote_request = ReceiptFake().quote_request(Currency.USD)
    response = client.post(f"/receipts/{receipt_id}/quotes", json=quote_request)

    assert response.status_code == 200
    assert "subtotal" in response.json()
    assert "total_discount" in response.json()
    assert "total" in response.json()
    assert response.json()["currency"] == Currency.USD.value


def test_process_payment(client: TestClient) -> None:
    clear_tables()

    product_id = create_product(client)
    response = client.post("/receipts")
    receipt_id = response.json()["receipt_id"]

    add_item_request = ReceiptFake().add_item_request(product_id)
    client.post(f"/receipts/{receipt_id}/products", json=add_item_request)

    response = client.post(f"/receipts/{receipt_id}/calculate")
    total_amount = response.json()["total"]

    payment_request = ReceiptFake().payment_request(total_amount)
    response = client.post(f"/receipts/{receipt_id}/payments", json=payment_request)
    assert response.status_code == 200

    response = client.get(f"/receipts/{receipt_id}")
    assert response.status_code == 200
    assert response.json()["receipt"]["state"] == ReceiptState.CLOSED.value
    assert "payment_amount" in response.json()["receipt"]
    assert response.json()["receipt"]["payment_amount"] == total_amount


def test_get_receipt_with_different_currency(client: TestClient) -> None:
    clear_tables()

    product_id = create_product(client)
    response = client.post("/receipts")
    receipt_id = response.json()["receipt_id"]

    add_item_request = ReceiptFake().add_item_request(product_id)
    client.post(f"/receipts/{receipt_id}/products", json=add_item_request)

    response = client.get(f"/receipts/{receipt_id}")
    gel_total = response.json()["receipt"]["total"]

    response = client.get(f"/receipts/{receipt_id}?currency={Currency.USD.value}")
    usd_total = response.json()["receipt"]["total"]

    assert gel_total != usd_total
    assert response.json()["receipt"]["currency"] == Currency.USD.value


def test_close_receipt(client: TestClient) -> None:
    clear_tables()

    product_id = create_product(client)
    response = client.post("/receipts")
    receipt_id = response.json()["receipt_id"]

    add_item_request = ReceiptFake().add_item_request(product_id)
    client.post(f"/receipts/{receipt_id}/products", json=add_item_request)

    response = client.post(f"/receipts/{receipt_id}/calculate")
    total_amount = response.json()["total"]

    payment_request = ReceiptFake().payment_request(total_amount)
    client.post(f"/receipts/{receipt_id}/payments", json=payment_request)

    response = client.post(f"/receipts/{receipt_id}/close")
    assert response.status_code == 200


def test_get_nonexistent_receipt(client: TestClient) -> None:
    clear_tables()

    unknown_id = uuid4()
    response = client.get(f"/receipts/{unknown_id}")

    assert response.status_code == 404
    assert "detail" in response.json()
    assert "error" in response.json()["detail"]
    assert (f"Receipt with id '{unknown_id}' does not exist"
            in response.json()["detail"]["error"]["message"])


def test_add_item_to_closed_receipt(client: TestClient) -> None:
    clear_tables()

    product_id = create_product(client)
    response = client.post("/receipts")
    receipt_id = response.json()["receipt_id"]

    add_item_request = ReceiptFake().add_item_request(product_id)
    client.post(f"/receipts/{receipt_id}/products", json=add_item_request)

    response = client.post(f"/receipts/{receipt_id}/calculate")
    total_amount = response.json()["total"]
    payment_request = ReceiptFake().payment_request(total_amount)
    client.post(f"/receipts/{receipt_id}/payments", json=payment_request)

    add_item_request = ReceiptFake().add_item_request(product_id)
    response = client.post(f"/receipts/{receipt_id}/products", json=add_item_request)

    assert response.status_code == 400
    assert "detail" in response.json()
    assert "error" in response.json()["detail"]
    assert ("Cannot add items to receipt in ReceiptState.CLOSED state"
            in response.json()["detail"]["error"]["message"])


def test_incorrect_payment_amount(client: TestClient) -> None:
    clear_tables()

    product_id = create_product(client)
    response = client.post("/receipts")
    receipt_id = response.json()["receipt_id"]

    add_item_request = ReceiptFake().add_item_request(product_id)
    client.post(f"/receipts/{receipt_id}/products", json=add_item_request)

    response = client.post(f"/receipts/{receipt_id}/calculate")
    total_amount = response.json()["total"]

    incorrect_amount = total_amount - 1.0
    payment_request = ReceiptFake().payment_request(incorrect_amount)
    response = client.post(f"/receipts/{receipt_id}/payments", json=payment_request)

    assert response.status_code == 400
    assert "detail" in response.json()
    assert "error" in response.json()["detail"]
    assert ("Payment amount is not correct" in
            response.json()["detail"]["error"]["message"])