from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class JobCreate(BaseModel):
    title: str
    department: str | None = None
    seniority: str | None = None
    notes: str | None = None


class JobUpdate(BaseModel):
    title: str | None = None
    department: str | None = None
    seniority: str | None = None
    jd_text: str | None = None
    status: str | None = None


class JobRead(BaseModel):
    id: UUID
    title: str
    department: str | None
    seniority: str | None
    greenhouse_id: str | None
    linkedin_job_url: str | None
    jd_text: str | None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
