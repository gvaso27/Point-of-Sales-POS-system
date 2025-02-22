from dataclasses import dataclass, field
from typing import Protocol
from uuid import UUID, uuid4


@dataclass
class Product:
    name: str
    price: float
    id: UUID = field(default_factory=uuid4)


class ProductRepository(Protocol):
    def read(self, product_id: UUID) -> Product:
        pass


@dataclass
class ProductService:
    products: ProductRepository

    def read(self, product_id: UUID) -> Product:
        return self.products.read(product_id)
