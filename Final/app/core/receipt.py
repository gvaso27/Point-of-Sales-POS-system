from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Protocol
from uuid import UUID, uuid4

from pydantic import BaseModel

from app.core.currency import Currency, CurrencyService
from app.core.product import Product
from app.core.receipt_item import AddItemRequest, ReceiptItem, ReceiptItemRepository


class ReceiptState(str, Enum):
    OPEN = "OPEN"
    CALCULATING = "CALCULATING"
    CLOSED = "CLOSED"


@dataclass
class Receipt:
    shift_id: UUID
    state: ReceiptState = ReceiptState.OPEN
    created_at: datetime = field(default_factory=datetime.now)
    id: UUID = field(default_factory=uuid4)
    subtotal: float = 0.0
    total_discount: float = 0.0

    # payment_currency: Currency | None = None
    # TODO: currencies

    @property
    def total(self) -> float:
        return self.subtotal - self.total_discount

    @property
    def savings(self) -> float:
        return self.total_discount


class CreateReceiptRequest(BaseModel):
    shift_id: UUID


class PaymentRequest(BaseModel):
    amount: float
    currency: Currency


class ReceiptRepository(Protocol):
    def create(self, receipt: Receipt) -> Receipt:
        pass

    def read(self, receipt_id: UUID) -> Receipt | None:
        pass

    def update(self, receipt: Receipt) -> None:
        pass

    def read_by_shift(self, shift_id: UUID) -> List[Receipt]:
        pass


@dataclass
class ReceiptService:
    receipts: ReceiptRepository
    receipt_items: ReceiptItemRepository
    currency_service: CurrencyService

    def add_item(self,
                 receipt_id: UUID,
                 add_request: AddItemRequest,
                 product: Product) -> None:
        receipt = self.receipts.read(receipt_id)
        if not receipt:
            raise ValueError(f"Receipt with id '{receipt_id}' does not exist")

        if receipt.state != ReceiptState.OPEN:
            raise ValueError(f"Cannot add items to receipt in {receipt.state} state")

        item = ReceiptItem(
            product_id=add_request.product_id,
            product_name=product.name,  # Store product name
            quantity=add_request.quantity,
            unit_price=product.price,
            receipt_id=receipt_id
        )

        self.receipt_items.create(item)
        receipt.subtotal += item.total
        self.receipts.update(receipt)

    def get_receipt(self,
                    receipt_id: UUID,
                    currency: Currency = Currency.GEL) -> Receipt:
        receipt = self.receipts.read(receipt_id)
        if not receipt:
            raise ValueError(f"Receipt with id '{receipt_id}' does not exist")

        # If requesting in a different currency, convert the amounts
        if currency != Currency.GEL:
            receipt.subtotal = self._convert_currency(receipt.subtotal, currency)
            receipt.total_discount = self._convert_currency(receipt.total_discount,
                                                            currency)

        return receipt

    def get_receipt_items(self,
                          receipt_id: UUID,
                          currency: Currency = Currency.GEL) -> List[ReceiptItem]:
        items = self.receipt_items.read_by_receipt(receipt_id)

        # If requesting in a different currency, convert the amounts
        if currency != Currency.GEL:
            for item in items:
                item.unit_price = self._convert_currency(item.unit_price, currency)
                item.discount = self._convert_currency(item.discount, currency)

        return items

    def process_payment(self, receipt_id: UUID, payment: PaymentRequest) -> None:
        receipt = self.receipts.read(receipt_id)
        if not receipt:
            raise ValueError(f"Receipt with id '{receipt_id}' does not exist")

        if receipt.state != ReceiptState.CALCULATING:
            raise ValueError(f"Cannot process payment for receipt"
                             f" in {receipt.state} state")

        # Convert payment amount to GEL for comparison
        payment_in_gel = self._convert_to_gel(payment.amount, payment.currency)

        if payment_in_gel < receipt.total:
            raise ValueError("Payment amount is insufficient")

        receipt.state = ReceiptState.CLOSED
        receipt.payment_amount = payment.amount
        receipt.payment_currency = payment.currency
        self.receipts.update(receipt)

    def _convert_currency(self, amount: float, target_currency: Currency) -> float:
        if target_currency == Currency.GEL:
            return amount
        return self.currency_service.convert(amount, Currency.GEL, target_currency)

    def _convert_to_gel(self, amount: float, from_currency: Currency) -> float:
        if from_currency == Currency.GEL:
            return amount
        return self.currency_service.convert(amount, from_currency, Currency.GEL)
