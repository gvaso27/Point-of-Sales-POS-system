from typing import Dict, List
from uuid import UUID

from app.core.Models.receipt import ReceiptItem
from app.core.receipt_item import ReceiptItemRepository


class InMemoryReceiptItemDb(ReceiptItemRepository):
    def __init__(self) -> None:
        self.receipt_items: Dict[str, List[ReceiptItem]] = {}

    def up(self) -> None:
        pass

    def create(self, item: ReceiptItem) -> ReceiptItem:
        key = str(item.receipt_id)
        if key not in self.receipt_items:
            self.receipt_items[key] = []
        self.receipt_items[key].append(item)
        return item

    def update(self, item: ReceiptItem) -> None:
        key = str(item.receipt_id)
        if key in self.receipt_items:
            # Find and replace item with matching product_id
            for i, existing_item in enumerate(self.receipt_items[key]):
                if existing_item.product_id == item.product_id:
                    self.receipt_items[key][i] = item
                    break

    def read(self, receipt_id: UUID, product_id: UUID) -> ReceiptItem | None:
        key = str(receipt_id)
        if key not in self.receipt_items:
            return None

        for item in self.receipt_items[key]:
            if item.product_id == product_id:
                return item
        return None

    def read_by_receipt(self, receipt_id: UUID) -> List[ReceiptItem]:
        key = str(receipt_id)
        return self.receipt_items.get(key, [])
