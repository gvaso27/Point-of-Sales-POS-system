from dataclasses import dataclass, field
from typing import Any, Dict
from uuid import uuid4

import pytest
from faker import Faker
from fastapi.testclient import TestClient

from app.core.product import Product
from app.infrastructure.sqlite.producs_in_memory_db import InMemoryProductDb
from app.runner.setup import init_app


@dataclass
class ProductFake:
    faker: Faker = field(default_factory=Faker)

    def product(self) -> Dict[str, Any]:
        return {
            "id": str(uuid4()),
            "name": self.faker.word(),
            "price": self.faker.random_number(),
        }

    def get_model(self) -> Product:
        return Product(
            name=self.faker.word(), id=uuid4(), price=self.faker.random_number()
        )

    def price(self) -> Dict[str, Any]:
        return {"price": self.faker.random_int()}


@pytest.fixture
def client() -> TestClient:
    return TestClient(init_app("in_memory"))


def clear_tables() -> None:
    InMemoryProductDb().clear()


def test_should_not_read_unknown_product(client: TestClient) -> None:
    clear_tables()
    unknown_id = uuid4()

    response = client.get(f"/products/{unknown_id}")

    assert response.status_code == 404
    assert response.json() == {
        "error": {"message": f"Product with id '{unknown_id}' does not exist"}
    }


def test_should_create_product(client: TestClient) -> None:
    clear_tables()
    product = ProductFake().product()

    response = client.post("/products", json=product)

    products = client.get("/products").json()["products"]

    assert response.status_code == 201
    assert len(products) > 0
    assert products[0]["name"] == product["name"]


def test_get_all_products_on_empty(client: TestClient) -> None:
    clear_tables()
    response = client.get("/products")

    assert response.status_code == 200
    assert response.json() == {"products": []}


def test_update_product(client: TestClient) -> None:
    clear_tables()
    product = ProductFake().product()

    response_create = client.post("/products", json=product)
    assert response_create.status_code == 201
    product_id = response_create.json()["product"]

    new_product = ProductFake().get_model()
    new_product_json = {
        "name": new_product.name,
        "price": new_product.price,
    }
    client.patch(f"/products/{product_id}", json=new_product_json)

    response_get = client.get(f"/products/{product_id}")

    assert response_get.status_code == 200
    assert response_get.json()["product"]["id"] == product_id
    assert response_get.json()["product"]["name"] == new_product.name
    assert response_get.json()["product"]["price"] == new_product.price
