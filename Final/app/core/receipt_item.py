from dataclasses import dataclass, field
from typing import List, Protocol
from uuid import UUID, uuid4

from pydantic import BaseModel


@dataclass
class ReceiptItem:
    product_id: UUID
    product_name: str
    quantity: int
    unit_price: float
    receipt_id: UUID
    discount: float = 0.0
    id: UUID = field(default_factory=uuid4)

    @property
    def total(self) -> float:
        # TODO - campains stuff here
        return (self.unit_price * self.quantity) - self.discount


class AddItemRequest(BaseModel):
    product_id: UUID
    quantity: int


class ReceiptItemRepository(Protocol):
    def create(self, item: ReceiptItem) -> ReceiptItem:
        pass

    def read(self, item_id: UUID) -> ReceiptItem | None:
        pass

    def read_by_receipt(self, receipt_id: UUID) -> List[ReceiptItem]:
        pass

    def delete_by_receipt(self, receipt_id: UUID) -> None:
        pass
