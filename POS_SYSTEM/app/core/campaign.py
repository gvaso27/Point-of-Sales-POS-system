from dataclasses import dataclass
from typing import List, Protocol
from uuid import UUID

from app.core.Models.campaign import Campaign, CreateCampaignRequest


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
