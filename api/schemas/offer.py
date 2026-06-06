from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class OfferCreate(BaseModel):
    candidate_id: UUID
    base_salary: Decimal | None = None
    equity_percentage: Decimal | None = None
    bonus_percentage: Decimal | None = None
    expires_at: datetime | None = None


class OfferStatusUpdate(BaseModel):
    status: str


class OfferRead(BaseModel):
    id: UUID
    candidate_id: UUID | None
    base_salary: Decimal | None
    equity_percentage: Decimal | None
    bonus_percentage: Decimal | None
    offer_letter_text: str | None
    greenhouse_offer_id: str | None
    status: str
    expires_at: datetime | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
