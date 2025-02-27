from dataclasses import dataclass
from uuid import UUID

from app.core.currency import Currency


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

