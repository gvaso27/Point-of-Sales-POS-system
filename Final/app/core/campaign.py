from dataclasses import dataclass, field
from typing import Any, Dict, List, Protocol
from uuid import UUID, uuid4

from pydantic import BaseModel

from app.core.product import Product


@dataclass
class Campaign:
    name: str
    campaign_type: str
    conditions: Dict[str, Any]
    rewards: Dict[str, Any]
    active: bool
    id: UUID = field(default_factory=uuid4)


class CreateCampaignRequest(BaseModel):
    name: str
    campaign_type: str
    conditions: Dict[str, Any]
    rewards: Dict[str, Any]
    active: bool


class CampaignRepository(Protocol):
    def read(self, campaign_id: UUID) -> Campaign:
        pass

    def create(self, create_request: CreateCampaignRequest) -> UUID:
        pass

    def add(self, campaign: Campaign) -> Campaign:
        pass

    def find_by_name(self, name: str) -> Campaign | None:
        pass

    def read_all(self) -> List[Campaign]:
        pass

    def deactivate(self, campaign_id: UUID) -> None:
        pass


@dataclass
class CampaignService:
    campaigns: CampaignRepository

    def read(self, campaign_id: UUID) -> Campaign:
        return self.campaigns.read(campaign_id)

    def create(self, create_request: CreateCampaignRequest) -> UUID:
        existing_campaign = self.campaigns.find_by_name(create_request.name)
        if existing_campaign:
            raise ValueError(
                f"Campaign with name '{create_request.name}' already exists"
            )

        campaign = Campaign(**create_request.model_dump())
        campaign.id = uuid4()
        print(campaign)
        self.campaigns.add(campaign)
        return campaign.id

    def read_all(self) -> List[Campaign]:
        return self.campaigns.read_all()

    def deactivate(self, campaign_id: UUID) -> None:
        self.campaigns.deactivate(campaign_id)

    def apply_campaign_discounts(
        self, products: List[Product], receipt_total: float = 0
    ) -> float:
        """
        Calculate total discount based on active campaigns
        """
        total_discount = 0.0
        active_campaigns = self.read_active()

        for campaign in active_campaigns:
            if campaign.campaign_type == "discount":
                # Product-specific or total receipt discount
                if receipt_total >= campaign.conditions.get("minimum_purchase", 0):
                    if "product_categories" in campaign.conditions:
                        # Product category specific discount
                        # Note: You might need to add category field to Product class
                        pass
                    else:
                        # Total receipt discount
                        discount_percentage = campaign.rewards.get(
                            "discount_percentage", 0
                        )
                        total_discount += receipt_total * discount_percentage / 100

            elif campaign.campaign_type == "buy_n_get_n":
                # Count products that match the campaign
                product_counts: dict[str, int] = {}
                for product in products:
                    if str(product.id) == campaign.conditions.get("product_id"):
                        product_counts[str(product.id)] = (
                            product_counts.get(str(product.id), 0) + 1
                        )

                # Apply buy N get N discount
                for product_id, count in product_counts.items():
                    buy_quantity = campaign.conditions.get("buy_quantity", 0)
                    free_quantity = campaign.rewards.get("free_quantity", 0)
                    if count >= buy_quantity:
                        # Calculate how many free items they get
                        sets = count // buy_quantity
                        total_free = min(sets * free_quantity, count - buy_quantity)
                        # Find product price to calculate discount
                        product_price = next(
                            p.price for p in products if str(p.id) == product_id
                        )
                        total_discount += total_free * product_price

            elif campaign.campaign_type == "combo":
                # Check if all required products are present
                required_products = set(
                    campaign.conditions.get("required_products", [])
                )
                present_products = set(str(p.id) for p in products)
                if required_products.issubset(present_products):
                    # Apply combo discount
                    discount_amount = campaign.rewards.get("discount_amount", 0)
                    total_discount += discount_amount

        return total_discount
