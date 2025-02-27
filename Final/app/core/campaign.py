from dataclasses import dataclass, field
from enum import Enum
from typing import List, Protocol
from uuid import UUID, uuid4

from pydantic import BaseModel

class CampaignType(Enum):
    BUY_N_GET_N = "buy_n_get_n"
    COMBO = "combo"
    DISCOUNT = "discount"
    WHOLE_RECEIPT_DISCOUNT = "whole_receipt_discount"


@dataclass
class Campaign:
    type: CampaignType
    amount_to_exceed: float
    percentage: float
    is_active: bool
    amount: int
    gift_amount: int
    gift_product_type: str
    id: UUID = field(default_factory=uuid4)


class CreateCampaignRequest(BaseModel):
    type: CampaignType
    amount_to_exceed: float
    percentage: float
    is_active: bool
    amount: int
    gift_amount: int
    gift_product_type: str


class CampaignRepository(Protocol):
    def read(self, campaign_id: UUID) -> Campaign:
        pass

    def add(self, campaign: Campaign) -> Campaign:
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
        campaign = Campaign(**create_request.model_dump())
        self.campaigns.add(campaign)
        return campaign.id

    def read_all(self) -> List[Campaign]:
        return self.campaigns.read_all()

    def deactivate(self, campaign_id: UUID) -> None:
        self.campaigns.deactivate(campaign_id)