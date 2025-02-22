from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter
from starlette.responses import JSONResponse

from app.infrastructure.fastapi.dependables import ProductRepositoryDependable

product_api = APIRouter(tags=["Products"])


@product_api.get(
    "/products/{product_id}", status_code=200, response_model=dict[str, Any]
)
def read_product(
    product_id: UUID, products: ProductRepositoryDependable
) -> dict[str, Any] | JSONResponse:
    try:
        return {"product": products.read(product_id)}
    except Exception as e:
        return JSONResponse(
            status_code=404,
            content={"error": {"message": str(e)}},
        )
