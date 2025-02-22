from typing import Annotated

from fastapi import Depends
from fastapi.requests import Request

from app.core.product import ProductRepository


def get_product_repository(request: Request) -> ProductRepository:
    return request.app.state.product  # type: ignore


ProductRepositoryDependable = Annotated[
    ProductRepository, Depends(get_product_repository)
]
