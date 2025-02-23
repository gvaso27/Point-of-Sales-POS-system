from typing import Any
from uuid import UUID

from fastapi import APIRouter, HTTPException

from app.core.campaign import CampaignService, CreateCampaignRequest
from app.infrastructure.fastapi.dependables import CampaignRepositoryDependable

campaign_api: APIRouter = APIRouter()


@campaign_api.post("/campaigns", status_code=201, response_model=dict[str, Any])
async def create_campaign(
    request: CreateCampaignRequest, campaigns: CampaignRepositoryDependable
) -> dict[str, Any]:
    try:
        return {"campaign": {"id": str(CampaignService(campaigns).create(request))}}
    except ValueError as e:
        raise HTTPException(status_code=400, detail={"error": {"message": str(e)}})


@campaign_api.get("/campaigns", response_model=dict[str, Any])
async def list_campaigns(
    campaigns: CampaignRepositoryDependable,
) -> dict[str, Any]:
    return {"campaigns": campaigns.read_all()}


@campaign_api.delete("/campaigns/{campaign_id}", status_code=200)
async def deactivate_campaign(
    campaign_id: UUID, campaigns: CampaignRepositoryDependable
) -> dict[str, Any]:
    try:
        campaigns.deactivate(campaign_id)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=404, detail={"error": {"message": str(e)}})
