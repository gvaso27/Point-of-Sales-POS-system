from dataclasses import dataclass, field
from typing import Any, Dict
from uuid import uuid4

import pytest
from faker import Faker
from fastapi.testclient import TestClient

from app.core.Models.campaign import CampaignType
from app.infrastructure.sqlite.inmemory.campaigns_in_memory_db import InMemoryCampaignDb
from app.runner.setup import init_app


@dataclass
class CampaignFake:
    faker: Faker = field(default_factory=Faker)

    def campaign(self) -> Dict[str, Any]:
        return {
            "type": CampaignType.BUY_N_GET_N.value,
            "amount_to_exceed": round(
                self.faker.pyfloat(min_value=100.0, max_value=1000.0), 2
            ),
            "percentage": round(self.faker.pyfloat(min_value=5.0, max_value=30.0), 2),
            "is_active": True,
            "amount": self.faker.random_int(min=50, max=200),
            "gift_amount": self.faker.random_int(min=10, max=50),
            "gift_product_type": self.faker.word(),
            "product_ids": [str(uuid4()), str(uuid4())],
        }


@pytest.fixture
def client() -> TestClient:
    return TestClient(init_app("in_memory"))


def clear_tables() -> None:
    InMemoryCampaignDb().clear()


def test_should_create_campaign(client: TestClient) -> None:
    clear_tables()
    campaign = CampaignFake().campaign()

    response = client.post("/campaigns", json=campaign)

    campaigns = client.get("/campaigns").json()["campaigns"]

    assert response.status_code == 201
    assert "campaign" in response.json()
    assert "id" in response.json()["campaign"]
    assert len(campaigns) > 0
    assert campaigns[0]["type"] == campaign["type"]
    assert campaigns[0]["amount_to_exceed"] == campaign["amount_to_exceed"]
    assert campaigns[0]["percentage"] == campaign["percentage"]


def test_get_all_campaigns_on_empty(client: TestClient) -> None:
    clear_tables()
    response = client.get("/campaigns")

    assert response.status_code == 200
    assert response.json() == {"campaigns": []}


def test_deactivate_campaign(client: TestClient) -> None:
    clear_tables()
    campaign = CampaignFake().campaign()

    # Create a campaign first
    response_create = client.post("/campaigns", json=campaign)
    assert response_create.status_code == 201
    campaign_id = response_create.json()["campaign"]["id"]

    campaigns_before = client.get("/campaigns").json()["campaigns"]
    active_campaign = next(
        (c for c in campaigns_before if c["id"] == campaign_id), None
    )
    assert active_campaign is not None
    assert active_campaign["is_active"] is True

    response_deactivate = client.delete(f"/campaigns/{campaign_id}")
    assert response_deactivate.status_code == 200
    assert response_deactivate.json() == {"status": "success"}

    campaigns_after = client.get("/campaigns").json()["campaigns"]
    deactivated_campaign = next(
        (c for c in campaigns_after if c["id"] == campaign_id), None
    )
    assert deactivated_campaign is not None
    assert deactivated_campaign["is_active"] is False


def test_should_not_deactivate_unknown_campaign(client: TestClient) -> None:
    clear_tables()
    unknown_id = uuid4()

    response = client.delete(f"/campaigns/{unknown_id}")

    assert response.status_code == 404
