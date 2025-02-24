from fastapi import FastAPI

from app.core.currency import CurrencyService
from app.infrastructure.fastapi.campaign import campaign_api
from app.infrastructure.fastapi.product import product_api
from app.infrastructure.fastapi.receipt import receipt_api
from app.infrastructure.sqlite.campaign_db import CampaignDb
from app.infrastructure.sqlite.inmemory.producs_in_memory_db import InMemoryProductDb
from app.infrastructure.sqlite.inmemory.receipt_in_memory_db import InMemoryReceiptDb
from app.infrastructure.sqlite.inmemory.receipt_item_in_memory_db import (
    InMemoryReceiptItemDb,
)
from app.infrastructure.sqlite.product_db import ProductDb
from app.infrastructure.sqlite.receipt_db import ReceiptDb
from app.infrastructure.sqlite.receipt_item_db import ReceiptItemDb


def init_app(db_type: str = "sqlite") -> FastAPI:
    app = FastAPI()

    # TODO:
    # campaign
    app.include_router(product_api)
    app.include_router(campaign_api)
    app.include_router(receipt_api)

    app.state.currency_service = CurrencyService()

    if db_type == "sqlite":
        app.state.product = ProductDb()
        app.state.campaign = CampaignDb()
        app.state.receipt = ReceiptDb()
        app.state.receipt_items = ReceiptItemDb()
    else:
        app.state.product = InMemoryProductDb()
        app.state.receipt = InMemoryReceiptDb()
        app.state.receipt_items = InMemoryReceiptItemDb()

    return app
