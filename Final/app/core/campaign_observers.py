from abc import ABC, abstractmethod

from app.core.Models.receipt import Receipt


class ICampaign(ABC):
    @abstractmethod
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
