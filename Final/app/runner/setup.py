from fastapi import FastAPI

from app.infrastructure.fastapi.product import product_api
from app.infrastructure.sqlite.producs_in_memory_db import InMemoryProductDb
from app.infrastructure.sqlite.product_db import ProductDb


def init_app(db_type: str = "sqlite") -> FastAPI:
    app = FastAPI()

    # TODO:
    # campaign
    # receipt
    app.include_router(product_api)

    if db_type == "sqlite":
        app.state.product = ProductDb()
    else:
        app.state.product = InMemoryProductDb()

    return app
