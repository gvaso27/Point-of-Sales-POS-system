from dataclasses import dataclass
from typing import List, Protocol
from uuid import UUID, uuid4

from app.core.Models.product import CreateProductRequest, Product, UpdateProductRequest


class ProductRepository(Protocol):
    def read(self, product_id: UUID) -> Product | None:
        pass

    def create(self, create_request: CreateProductRequest) -> UUID:
        pass

    def add(self, product: Product) -> Product:
        pass

    def find_by_name(self, name: str) -> Product | None:
        pass

    def read_all(self) -> List[Product]:
        pass

    def update(self, product: Product) -> None:
        pass


@dataclass
class ProductService:
    products: ProductRepository

    def read(self, product_id: UUID) -> Product:
        existing_product = self.products.read(product_id)
        if existing_product:
            return existing_product

        raise ValueError(f"Product with id '{product_id}' does not exist")

    def create(self, create_request: CreateProductRequest) -> UUID:
        existing_product = self.products.find_by_name(create_request.name)
        if existing_product:
            raise ValueError(
                f"Product with name '{create_request.name}' already exists"
            )

        product = Product(**create_request.model_dump())
        product.id = uuid4()
        self.products.add(product)
        return product.id

    def read_all(self) -> List[Product]:
        return self.products.read_all()

    def update_product(
        self, update_request: UpdateProductRequest, product_id: UUID
    ) -> None:
        existing_product = self.products.read(product_id)
        if not existing_product:
            raise ValueError(f"Product with id '{product_id}' does not exist")

        product = Product(**update_request.model_dump())
        product.id = product_id
        self.products.update(product)
