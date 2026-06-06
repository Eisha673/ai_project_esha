from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class InterviewRead(BaseModel):
    id: UUID
    candidate_id: UUID | None
    calendly_link: str | None
    scheduled_at: datetime | None
    question_bank: list | None
    completed: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
