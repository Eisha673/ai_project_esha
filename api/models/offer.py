import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class Offer(Base):
    __tablename__ = "offers"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    candidate_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("candidates.id"))
    base_salary: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    equity_percentage: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    bonus_percentage: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    offer_letter_text: Mapped[str | None] = mapped_column(Text)
    greenhouse_offer_id: Mapped[str | None] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(50), default="pending")
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    candidate = relationship("Candidate", back_populates="offers")
