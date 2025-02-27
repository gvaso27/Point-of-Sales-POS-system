from dataclasses import dataclass
from typing import List, Protocol
from uuid import UUID

from pydantic import BaseModel


@dataclass
class ReceiptItem:
    receipt_id: UUID
    product_id: UUID
    quantity: int


class AddItemRequest(BaseModel):
    product_id: UUID
    quantity: int


class ReceiptItemRepository(Protocol):
    def create(self, item: ReceiptItem) -> ReceiptItem:
        pass

    def update(self, item: ReceiptItem) -> None:
        pass

    def read(self, receipt_id: UUID, item_id: UUID) -> ReceiptItem | None:
        pass

    def read_by_receipt(self, receipt_id: UUID) -> List[ReceiptItem]:
        pass
