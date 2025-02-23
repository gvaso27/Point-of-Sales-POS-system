from fastapi import FastAPI

from app.infrastructure.fastapi.campaign import campaign_api
from app.infrastructure.fastapi.product import product_api
from app.infrastructure.sqlite.campaign_db import CampaignDb
from app.infrastructure.sqlite.product_db import ProductDb


def init_app() -> FastAPI:
    app = FastAPI()

    # TODO:
    # receipt
    app.include_router(product_api)
    app.include_router(campaign_api)

    app.state.product = ProductDb()
    app.state.campaign = CampaignDb()

    return app
