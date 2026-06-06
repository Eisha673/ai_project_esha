from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class CandidateCreate(BaseModel):
    job_id: UUID
    full_name: str
    email: str | None = None
    linkedin_url: str | None = None
    greenhouse_application_id: str | None = None
    resume_text: str | None = None


class CandidateStageUpdate(BaseModel):
    stage: str


class CandidateRead(BaseModel):
    id: UUID
    job_id: UUID | None
    full_name: str | None
    email: str | None
    linkedin_url: str | None
    greenhouse_application_id: str | None
    resume_text: str | None
    nim_screen_score: int | None
    nim_screen_reasoning: str | None
    nim_screen_strengths: list | None
    nim_screen_gaps: list | None
    nim_bias_flagged: bool
    assessment_score: int | None
    assessment_pass: bool | None
    stage: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
