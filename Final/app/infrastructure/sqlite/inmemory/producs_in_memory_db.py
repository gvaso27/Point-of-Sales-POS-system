from typing import Dict, List
from uuid import UUID

from app.core.product import Product


class InMemoryProductDb:
    def __init__(self) -> None:
        self.products: Dict[str, Product] = {}

    def up(self) -> None:
        # No setup needed for in-memory database
        pass

    def clear(self) -> None:
        self.products.clear()

    def read(self, product_id: UUID) -> Product | None:
        return self.products.get(str(product_id))

    def add(self, product: Product) -> Product:
        self.products[str(product.id)] = product
        return product

    def find_by_name(self, name: str) -> Product | None:
        for product in self.products.values():
            if product.name == name:
                return product
        return None

    def read_all(self) -> List[Product]:
        return list(self.products.values())

    def update(self, product: Product) -> None:
        if str(product.id) not in self.products:
            raise KeyError(f"Product with id {product.id} not found")
        self.products[str(product.id)] = product
