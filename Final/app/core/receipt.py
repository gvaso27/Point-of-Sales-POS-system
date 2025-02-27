from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Protocol
from uuid import UUID, uuid4

from pydantic import BaseModel

from app.core.currency import Currency, CurrencyService
from app.core.product import Product
from app.core.receipt_item import AddItemRequest, ReceiptItem, ReceiptItemRepository
from app.core.shift import ShiftService


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
    shift_service: ShiftService
    currency_service: CurrencyService

    def create(self) -> UUID:
        shift_id = self.shift_service.get_open_shift()
        if not shift_id:
            raise ValueError(f"Shift is not open")
        receipt = Receipt(id=uuid4(),
                          shift_id=shift_id.shift_id)
        self.receipts.create(receipt)
        return receipt.id

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
            quantity=add_request.quantity,
            receipt_id=receipt_id
        )

        current_item = self.receipt_items.read(receipt_id, add_request.product_id)
        if current_item:
            item.quantity += current_item.quantity
            self.receipt_items.update(item)
            return None

        self.receipt_items.create(item)
        # todo Zuka price update stuff
        self.receipts.update(receipt)

    def calculate_total(self, receipt_id: UUID) -> float:
        receipt = self.receipts.read(receipt_id)
        if not receipt:
            raise ValueError(f"Receipt with id '{receipt_id}' does not exist")

        if receipt.state != ReceiptState.OPEN:
            raise ValueError(f"Cannot calculate total for "
                             f"receipt in {receipt.state} state")

        # todo Zuka price update stuff
        self.receipts.update(receipt)

        return receipt.total

    def close_receipt(self, receipt_id: UUID) -> None:
        receipt = self.receipts.read(receipt_id)
        if not receipt:
            raise ValueError(f"Receipt with id '{receipt_id}' does not exist")

        if receipt.state != ReceiptState.PAYED:
            raise ValueError(f"Cannot close receipt that is not in {receipt.state} state")

        receipt.state = ReceiptState.CLOSED
        self.receipts.update(receipt)

    def get_quote(self, receipt_id: UUID, currency: Currency) -> QuoteResponse:
        receipt = self.receipts.read(receipt_id)
        if not receipt:
            raise ValueError(f"Receipt with id '{receipt_id}' does not exist")

        subtotal_converted = self._convert_currency(receipt.subtotal, currency)
        discount_converted = self._convert_currency(receipt.total_discount, currency)
        total_converted = subtotal_converted - discount_converted

        return QuoteResponse(
            subtotal=subtotal_converted,
            total_discount=discount_converted,
            total=total_converted,
            currency=currency
        )

    def get_receipt(self,
                    receipt_id: UUID,
                    currency: Currency = Currency.GEL) -> Receipt:
        receipt = self.receipts.read(receipt_id)
        if not receipt:
            raise ValueError(f"Receipt with id '{receipt_id}' does not exist")

        if currency != Currency.GEL:
            converted_receipt = Receipt(
                id=receipt.id,
                shift_id=receipt.shift_id,
                state=receipt.state,
                created_at=receipt.created_at,
                subtotal=self._convert_currency(receipt.subtotal, currency),
                total_discount=self._convert_currency(receipt.total_discount, currency),
                payment_amount=receipt.payment_amount,
                payment_currency=receipt.payment_currency
            )

            if receipt.payment_currency and receipt.payment_currency != currency:
                converted_receipt.payment_amount = self.currency_service.convert(
                    receipt.payment_amount,
                    receipt.payment_currency,
                    currency
                )
                converted_receipt.payment_currency = currency

            return converted_receipt
        return receipt

    def get_receipt_items(self,
                          receipt_id: UUID,
                          currency: Currency = Currency.GEL) -> List[ReceiptItem]:
        items = self.receipt_items.read_by_receipt(receipt_id)
        if currency != Currency.GEL:
            converted_items = []
            for item in items:
                converted_item = ReceiptItem(
                    receipt_id=item.receipt_id,
                    product_id=item.product_id,
                    quantity=item.quantity,
                )
                converted_items.append(converted_item)
            return converted_items

        # todo
        return items

    def process_payment(self, receipt_id: UUID, payment: PaymentRequest) -> None:
        receipt = self.receipts.read(receipt_id)
        if not receipt:
            raise ValueError(f"Receipt with id '{receipt_id}' does not exist")

        payment_in_gel = self._convert_to_gel(payment.amount, payment.currency)

        if payment_in_gel != receipt.total:
            raise ValueError("Payment amount is not correct")

        receipt.state = ReceiptState.PAYED
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
