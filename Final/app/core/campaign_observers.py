from typing import Protocol

from app.core.Models.receipt import Receipt


class ICampaign(Protocol):
    def update(self, receipt: Receipt) -> None:
        pass


class BuyNGetNCampaign(ICampaign):
    def update(self, receipt: Receipt) -> None:
        pass


class DiscountCampaign(ICampaign):
    def update(self, receipt: Receipt) -> None:
        pass


class ComboCampaign(ICampaign):
    def update(self, receipt: Receipt) -> None:
        pass


class WholeReceiptDiscountCampaign(ICampaign):
    def update(self, receipt: Receipt) -> None:
        pass
