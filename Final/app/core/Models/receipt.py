from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List
from uuid import UUID, uuid4

from pydantic import BaseModel

from app.core.currency import Currency


class ReceiptState(str, Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    PAYED = "PAYED"


@dataclass
class Receipt:
    shift_id: UUID
    state: ReceiptState = ReceiptState.OPEN
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.now)
    subtotal: float = 0.0
    total_discount: float = 0.0
    payment_amount: float = 0.0
    payment_currency: Currency | None = Currency.GEL

    @property
    def total(self) -> float:
        return self.subtotal - self.total_discount

    @property
    def savings(self) -> float:
        return self.total_discount


class PaymentRequest(BaseModel):
    amount: float
    currency: Currency


class QuoteRequest(BaseModel):
    currency: Currency


class QuoteResponse(BaseModel):
    subtotal: float
    total_discount: float
    total: float
    currency: Currency


class ReceiptProduct(BaseModel):
    id: UUID
    name: str
    price: float
    quantity: int


class GetReceiptResponse(BaseModel):
    id: UUID
    state: ReceiptState
    items: List[ReceiptProduct]
    subtotal: float
    total_discount: float
    total: float
    savings: float
    currency: Currency

@dataclass
class ReceiptItem:
    receipt_id: UUID
    product_id: UUID
    quantity: int


class AddItemRequest(BaseModel):
    product_id: UUID
    quantity: int
