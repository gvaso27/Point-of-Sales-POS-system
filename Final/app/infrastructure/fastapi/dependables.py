from typing import Annotated

from fastapi import Depends
from fastapi.requests import Request

from app.core.campaign import CampaignRepository
from app.core.currency import CurrencyService
from app.core.product import ProductRepository
from app.core.receipt import ReceiptRepository
from app.core.receipt_item import ReceiptItemRepository


def get_product_repository(request: Request) -> ProductRepository:
    return request.app.state.product  # type: ignore


def get_campaign_repository(request: Request) -> CampaignRepository:
    return request.app.state.campaign  # type: ignore


def get_receipt_repository(request: Request) -> ReceiptRepository:
    return request.app.state.receipt  # type: ignore


def get_receipt_item_repository(request: Request) -> ReceiptItemRepository:
    return request.app.state.receipt_items  # type: ignore


def get_currency_service(request: Request) -> CurrencyService:
    return request.app.state.currency_service


CurrencyServiceDependable = Annotated[
    CurrencyService, Depends(get_currency_service)
]

ProductRepositoryDependable = Annotated[
    ProductRepository, Depends(get_product_repository)
]

CampaignRepositoryDependable = Annotated[
    CampaignRepository, Depends(get_campaign_repository)
]

ReceiptRepositoryDependable = Annotated[
    ReceiptRepository, Depends(get_receipt_repository)
]

ReceiptItemRepositoryDependable = Annotated[
    ReceiptItemRepository, Depends(get_receipt_item_repository)
]
