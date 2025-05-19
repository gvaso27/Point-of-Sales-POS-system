from dataclasses import dataclass, field
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


class UpdateProductRequest(BaseModel):
    name: str
    price: float
