from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel


class CampaignType(Enum):
    BUY_N_GET_N = "buy_n_get_n"
    COMBO = "combo"
    DISCOUNT = "discount"
    WHOLE_RECEIPT_DISCOUNT = "whole_receipt_discount"


@dataclass
class Campaign:
    type: CampaignType
    amount_to_exceed: float
    percentage: float
    is_active: bool
    amount: int
    gift_amount: int
    gift_product_type: str
    id: UUID = field(default_factory=uuid4)
    product_ids: List[str] = field(default_factory=list)


class CreateCampaignRequest(BaseModel):
    type: CampaignType
    amount_to_exceed: float
    percentage: float
    is_active: bool
    amount: int
    gift_amount: int
    gift_product_type: str
    product_ids: Optional[List[str]] = None