from fastapi import FastAPI

from app.core.currency import CurrencyService
from app.infrastructure.fastapi.product import product_api
from app.infrastructure.fastapi.receipt import receipt_api
from app.infrastructure.sqlite.product_db import ProductDb
from app.infrastructure.sqlite.receipt_db import ReceiptDb
from app.infrastructure.sqlite.receipt_item_db import ReceiptItemDb


def init_app() -> FastAPI:
    app = FastAPI()

    # TODO:
    # campaign
    app.include_router(receipt_api)
    app.include_router(product_api)

    app.state.product = ProductDb()
    app.state.receipt = ReceiptDb()
    app.state.receipt_items = ReceiptItemDb()
    app.state.currency_service = CurrencyService()



    return app
