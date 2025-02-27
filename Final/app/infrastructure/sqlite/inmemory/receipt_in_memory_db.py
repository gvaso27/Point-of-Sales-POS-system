from typing import Dict, List
from uuid import UUID

from app.core.receipt import Receipt, ReceiptRepository


class InMemoryReceiptDb(ReceiptRepository):
    def __init__(self) -> None:
        self.receipts: Dict[str, Receipt] = {}

    def up(self) -> None:
        # No setup needed for in-memory storage
        pass

    def create(self, receipt: Receipt) -> Receipt:
        self.receipts[str(receipt.id)] = receipt
        return receipt

    def read(self, receipt_id: UUID) -> Receipt | None:
        return self.receipts.get(str(receipt_id))

    def update(self, receipt: Receipt) -> None:
        if str(receipt.id) in self.receipts:
            self.receipts[str(receipt.id)] = receipt

    def read_by_shift(self, shift_id: UUID) -> List[Receipt]:
        return [
            receipt for receipt in self.receipts.values()
            if receipt.shift_id == shift_id
        ]
