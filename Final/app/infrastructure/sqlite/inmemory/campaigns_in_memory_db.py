from typing import Dict, List
from uuid import UUID

from app.core.Models.campaign import Campaign


class InMemoryCampaignDb:
    def __init__(self) -> None:
        self.campaigns: Dict[str, Campaign] = {}
        self.campaign_relations: Dict[str, List[str]] = {}

    def up(self) -> None:
        # No setup needed for in-memory database
        pass

    def clear(self) -> None:
        self.campaigns.clear()
        self.campaign_relations.clear()

    def read(self, campaign_id: UUID) -> Campaign:
        campaign_id_str = str(campaign_id)
        if campaign_id_str not in self.campaigns:
            raise Exception(f"campaign with {campaign_id} does not exist")

        campaign = self.campaigns[campaign_id_str]
        product_ids = self.get_campaign_product_ids(campaign_id)
        campaign.product_ids = product_ids

        return campaign

    def add(self, campaign: Campaign) -> Campaign:
        campaign_id_str = str(campaign.id)
        self.campaigns[campaign_id_str] = campaign

        if hasattr(campaign, "product_ids") and campaign.product_ids:
            self.add_campaign_product_ids(campaign.id, campaign.product_ids)

        return campaign

    def read_all(self) -> List[Campaign]:
        campaigns = []
        for campaign_id_str, campaign in self.campaigns.items():
            campaign_copy = Campaign(
                id=campaign.id,
                type=campaign.type,
                amount_to_exceed=campaign.amount_to_exceed,
                percentage=campaign.percentage,
                is_active=campaign.is_active,
                amount=campaign.amount,
                gift_amount=campaign.gift_amount,
                gift_product_type=campaign.gift_product_type
            )

            campaign_copy.product_ids = self.get_campaign_product_ids(campaign.id)
            campaigns.append(campaign_copy)

        return campaigns

    def deactivate(self, campaign_id: UUID) -> None:
        campaign_id_str = str(campaign_id)
        if campaign_id_str not in self.campaigns:
            raise Exception(f"campaign with {campaign_id} does not exist")

        campaign = self.campaigns[campaign_id_str]
        campaign.is_active = False
        self.campaigns[campaign_id_str] = campaign

    def add_campaign_product_ids(self, campaign_id: UUID, product_ids: List[str]) -> None:
        campaign_id_str = str(campaign_id)
        if campaign_id_str not in self.campaign_relations:
            self.campaign_relations[campaign_id_str] = []

        for product_id in product_ids:
            if product_id not in self.campaign_relations[campaign_id_str]:
                self.campaign_relations[campaign_id_str].append(product_id)

    def get_campaign_product_ids(self, campaign_id: UUID) -> List[str]:
        campaign_id_str = str(campaign_id)
        if campaign_id_str not in self.campaign_relations:
            return []

        return self.campaign_relations[campaign_id_str]