from __future__ import annotations

from typing import Any, no_type_check
from uuid import UUID

from fastapi import APIRouter
from starlette.responses import JSONResponse

from app.core.product import ProductService
from app.infrastructure.fastapi.dependables import ProductRepositoryDependable

product_api: APIRouter = APIRouter()

@product_api.get(
    "/products/{product_id}",
    status_code=200,
    response_model=dict[str, Any]
)
@no_type_check
def read_product(
    product_id: UUID, products: ProductRepositoryDependable
) -> dict[str, Any] | JSONResponse:
    try:
        return {"product": ProductService(products).read(product_id)}
    except Exception as e:
        return JSONResponse(
            status_code=404,
            content={"error": {"message": str(e)}},
        )
