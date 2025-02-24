from typing import Dict, List
from uuid import UUID

from app.core.receipt import Receipt, ReceiptRepository


class InMemoryReceiptDb(ReceiptRepository):
    def __init__(self) -> None:
        self.receipts: Dict[str, Receipt] = {}

    def up(self) -> None:
        pass

    def create(self, receipt: Receipt) -> Receipt:
        self.receipts[str(receipt.id)] = receipt
        return receipt

    def read(self, receipt_id: UUID) -> Receipt | None:
        return self.receipts.get(str(receipt_id))

    def read_all(self) -> List[Receipt]:
        return list(self.receipts.values())

    def delete(self, receipt_id: UUID) -> None:
        self.receipts.pop(str(receipt_id), None)
