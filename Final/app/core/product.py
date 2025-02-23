from dataclasses import dataclass, field
from typing import List, Protocol
from uuid import UUID, uuid4

from pydantic import BaseModel


@dataclass
class Product:
    name: str
    price: float
    id: UUID = field(default_factory=uuid4)


class CreateProductRequest(BaseModel):
    name: str
    price: float


class ProductRepository(Protocol):
    def read(self, product_id: UUID) -> Product:
        pass

    def create(self, create_request: CreateProductRequest) -> UUID:
        pass

    def add(self, product: Product) -> Product:
        pass

    def find_by_name(self, name: str) -> Product | None:
        pass

    def read_all(self) -> List[Product]:
        pass


@dataclass
class ProductService:
    products: ProductRepository

    def read(self, product_id: UUID) -> Product:
        return self.products.read(product_id)

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
