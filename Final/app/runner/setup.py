from fastapi import FastAPI

from app.infrastructure.fastapi.product import product_api
from app.infrastructure.sqlite.product_db import ProductDb


def init_app() -> FastAPI:
    app = FastAPI()

    # TODO:
    # campaign
    # receipt
    app.include_router(product_api)

    app.state.product = ProductDb()

    return app
