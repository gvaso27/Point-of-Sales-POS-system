from abc import ABC, abstractmethod
from typing import List

from app.core.campaign import Campaign, CampaignType


class ICampaign(ABC):
    @abstractmethod
    def update(self, receipt: dict):
        pass


class BuyNGetNCampaign(ICampaign):
    def __init__(self, campaigns: List[Campaign]):
        self.campaigns = [c for c in campaigns if c.type == CampaignType.BUY_N_GET_N]

    def update(self, receipt: dict):
        print("Applying Buy N Get N Campaign...")
        for campaign in self.campaigns:
            for item in receipt["items"]:
                if (
                    item["product_id"] in campaign.product_ids
                    and item["quantity"] >= campaign.amount
                ):
                    item["bonus"] = (
                        item["quantity"] // campaign.amount
                    ) * campaign.gift_amount
        print("Buy N Get N Campaign applied:", receipt)


class DiscountCampaign(ICampaign):
    def __init__(self, campaigns: List[Campaign]):
        self.campaigns = [
            c
            for c in campaigns
            if c.type in [CampaignType.DISCOUNT, CampaignType.WHOLE_RECEIPT_DISCOUNT]
        ]

    def update(self, receipt: dict):
        print("Applying Discount Campaign...")
        for campaign in self.campaigns:
            if (
                campaign.type == CampaignType.WHOLE_RECEIPT_DISCOUNT
                and receipt["subtotal"] > campaign.amount_to_exceed
            ):
                discount = receipt["subtotal"] * (campaign.percentage / 100)
                receipt["total_discount"] += discount
            elif campaign.type == CampaignType.DISCOUNT:
                for item in receipt["items"]:
                    if item["product_id"] in campaign.product_ids:
                        discount = (
                            item["unit_price"]
                            * (campaign.percentage / 100)
                            * item["quantity"]
                        )
                        item["discount"] = discount
                        receipt["total_discount"] += discount
        print("Discount Campaign applied:", receipt)
