from typing import Dict, List
from uuid import UUID

from app.core.receipt_item import ReceiptItem, ReceiptItemRepository


class InMemoryReceiptItemDb(ReceiptItemRepository):
    def __init__(self) -> None:
        self.receipt_items: Dict[str, ReceiptItem] = {}

    def up(self) -> None:
        pass

    def create(self, item: ReceiptItem) -> ReceiptItem:
        self.receipt_items[str(item.id)] = item
        return item

    def read(self, item_id: UUID) -> ReceiptItem | None:
        return self.receipt_items.get(str(item_id))

    def read_by_receipt(self, receipt_id: UUID) -> List[ReceiptItem]:
        return [
            item
            for item in self.receipt_items.values()
            if item.receipt_id == receipt_id
        ]

    def delete_by_receipt(self, receipt_id: UUID) -> None:
        self.receipt_items = {
            key: item
            for key, item in self.receipt_items.items()
            if item.receipt_id != receipt_id
        }
