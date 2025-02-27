from dataclasses import dataclass
from uuid import UUID

from app.core.currency import Currency
from app.core.receipt import ReceiptRepository
from app.core.receipt_item import ReceiptItemRepository
from app.core.shift import ShiftService


@dataclass
class XReportItem:
    product_id: UUID
    sold_amount: int


@dataclass
class ReportRevenue:
    currency: Currency | None
    amount: float


@dataclass
class XReport:
    receipt_number: int
    items_sold: list[XReportItem]
    revenue: list[ReportRevenue]


@dataclass
class ReportService:
    receipts: ReceiptRepository
    receipt_items: ReceiptItemRepository
    shift_service: ShiftService

    def generate_x_report(self) -> XReport:
        shift_id = self.shift_service.get_open_shift()
        if not shift_id:
            raise ValueError("Shift is not open")

        receipts = self.receipts.read_by_shift(shift_id.shift_id)
        item_sales = {}
        revenue_by_currency = {}

        for receipt in receipts:
            receipt_items = self.receipt_items.read_by_receipt(receipt.id)
            if receipt.payment_currency not in revenue_by_currency:
                revenue_by_currency[receipt.payment_currency] = 0.0
            revenue_by_currency[receipt.payment_currency] += receipt.payment_amount

            for item in receipt_items:
                if item.product_id not in item_sales:
                    item_sales[item.product_id] = 0
                item_sales[item.product_id] += item.quantity

        items_sold = [
            XReportItem(product_id=product_id, sold_amount=amount)
            for product_id, amount in item_sales.items()
        ]

        revenue = [
            ReportRevenue(currency=currency, amount=amount)
            for currency, amount in revenue_by_currency.items()
        ]

        return XReport(
            receipt_number=len(receipts),
            items_sold=items_sold,
            revenue=revenue
        )

    def generate_z_report(self) -> list[ReportRevenue]:
        receipts = self.receipts.get_all()
        revenue_by_currency = {}

        for receipt in receipts:
            if receipt.payment_currency not in revenue_by_currency:
                revenue_by_currency[receipt.payment_currency] = 0.0
            revenue_by_currency[receipt.payment_currency] += receipt.payment_amount

        return [
            ReportRevenue(currency=currency, amount=amount)
            for currency, amount in revenue_by_currency.items()
        ]
