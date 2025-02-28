from dataclasses import dataclass, field
from typing import List, Protocol
from uuid import UUID, uuid4

from app.core.currency import Currency, CurrencyService
from app.core.Models.product import Product
from app.core.Models.receipt import (
    AddItemRequest,
    PaymentRequest,
    QuoteResponse,
    Receipt,
    ReceiptItem,
    ReceiptState,
)
from app.core.receipt_item import ReceiptItemRepository
from app.core.shift import ShiftService


class ReceiptRepository(Protocol):
    def create(self, receipt: Receipt) -> Receipt:
        pass

    def read(self, receipt_id: UUID) -> Receipt | None:
        pass

    def update(self, receipt: Receipt) -> None:
        pass

    def read_by_shift(self, shift_id: UUID) -> List[Receipt]:
        pass

    def get_all(self) -> List[Receipt]:
        pass


@dataclass
class ReceiptService:
    from app.core.campaign_observers import ICampaign

    receipts: ReceiptRepository
    receipt_items: ReceiptItemRepository
    shift_service: ShiftService
    currency_service: CurrencyService
    observers: List[ICampaign] = field(default_factory=list)

    def create(self) -> UUID:
        shift_id = self.shift_service.get_open_shift()
        if not shift_id:
            raise ValueError("Shift is not open")
        receipt = Receipt(id=uuid4(), shift_id=shift_id.shift_id)
        self.receipts.create(receipt)
        return receipt.id

    def add_item(
        self, receipt_id: UUID, add_request: AddItemRequest, product: Product
    ) -> None:
        receipt = self.receipts.read(receipt_id)
        if not receipt:
            raise ValueError(f"Receipt with id '{receipt_id}' does not exist")

        if receipt.state != ReceiptState.OPEN:
            raise ValueError(f"Cannot add items to receipt in {receipt.state} state")

        item = ReceiptItem(
            product_id=add_request.product_id,
            quantity=add_request.quantity,
            receipt_id=receipt_id,
        )

        current_item = self.receipt_items.read(receipt_id, add_request.product_id)
        if current_item:
            item.quantity += current_item.quantity
            self.receipt_items.update(item)
        else:
            self.receipt_items.create(item)

        receipt.subtotal += item.quantity * product.price
        for observer in self.observers:
            observer.update(receipt)

    def calculate_total(self, receipt_id: UUID) -> float:
        receipt = self.receipts.read(receipt_id)
        if not receipt:
            raise ValueError(f"Receipt with id '{receipt_id}' does not exist")

        if receipt.state != ReceiptState.OPEN:
            raise ValueError(
                f"Cannot calculate total for receipt in {receipt.state} state"
            )

        self.receipts.update(receipt)

        return receipt.subtotal - receipt.total_discount

    def close_receipt(self, receipt_id: UUID) -> None:
        receipt = self.receipts.read(receipt_id)
        if not receipt:
            raise ValueError(f"Receipt with id '{receipt_id}' does not exist")

        if receipt.state != ReceiptState.PAYED:
            raise ValueError(f"Cannot close receipt that is in {receipt.state} state")

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
            currency=currency,
        )

    def get_receipt(
        self, receipt_id: UUID, currency: Currency = Currency.GEL
    ) -> Receipt:
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
                payment_currency=receipt.payment_currency,
            )

            if receipt.payment_currency and receipt.payment_currency != currency:
                converted_receipt.payment_amount = self.currency_service.convert(
                    receipt.payment_amount, receipt.payment_currency, currency
                )
                converted_receipt.payment_currency = currency

            return converted_receipt
        return receipt

    def get_receipt_items(
        self, receipt_id: UUID, currency: Currency = Currency.GEL
    ) -> List[ReceiptItem]:
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

        return items

    def process_payment(self, receipt_id: UUID, payment: PaymentRequest) -> None:
        receipt = self.receipts.read(receipt_id)
        if not receipt:
            raise ValueError(f"Receipt with id '{receipt_id}' does not exist")

        payment_in_gel = self._convert_to_gel(payment.amount, payment.currency)

        if payment_in_gel != receipt.payment_amount:
            raise ValueError("Payment amount is not correct")

        receipt.state = ReceiptState.PAYED
        receipt.payment_amount = payment.amount
        receipt.payment_currency = payment.currency
        self.receipts.update(receipt)

    def add_observer(self, observer: ICampaign) -> None:
        self.observers.append(observer)

    def _convert_currency(self, amount: float, target_currency: Currency) -> float:
        if target_currency == Currency.GEL:
            return amount
        return self.currency_service.convert(amount, Currency.GEL, target_currency)

    def _convert_to_gel(self, amount: float, from_currency: Currency) -> float:
        if from_currency == Currency.GEL:
            return amount
        return self.currency_service.convert(amount, from_currency, Currency.GEL)
