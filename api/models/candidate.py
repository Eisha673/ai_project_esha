import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class Candidate(Base):
    __tablename__ = "candidates"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    job_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("jobs.id"))
    full_name: Mapped[str | None] = mapped_column(String(255))
    email: Mapped[str | None] = mapped_column(String(255))
    linkedin_url: Mapped[str | None] = mapped_column(Text)
    greenhouse_application_id: Mapped[str | None] = mapped_column(String(100))
    resume_text: Mapped[str | None] = mapped_column(Text)
    nim_screen_score: Mapped[int | None] = mapped_column(Integer)
    nim_screen_reasoning: Mapped[str | None] = mapped_column(Text)
    nim_screen_strengths: Mapped[list | None] = mapped_column(JSON)
    nim_screen_gaps: Mapped[list | None] = mapped_column(JSON)
    nim_bias_flagged: Mapped[bool] = mapped_column(Boolean, default=False)
    assessment_score: Mapped[int | None] = mapped_column(Integer)
    assessment_pass: Mapped[bool | None] = mapped_column(Boolean)
    stage: Mapped[str] = mapped_column(String(50), default="applied")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    job = relationship("Job", back_populates="candidates")
    interviews = relationship("Interview", back_populates="candidate")
    offers = relationship("Offer", back_populates="candidate")
