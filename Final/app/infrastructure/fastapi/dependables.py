from typing import Annotated

from fastapi import Depends
from fastapi.requests import Request

from app.core.campaign import CampaignRepository
from app.core.product import ProductRepository


def get_product_repository(request: Request) -> ProductRepository:
    return request.app.state.product


def get_campaign_repository(request: Request) -> CampaignRepository:
    return request.app.state.campaign


ProductRepositoryDependable = Annotated[
    ProductRepository, Depends(get_product_repository)
]

CampaignRepositoryDependable = Annotated[
    CampaignRepository, Depends(get_campaign_repository)
]
