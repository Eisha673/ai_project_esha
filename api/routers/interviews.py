from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_session
from ..models.interview import Interview
from ..schemas.interview import InterviewRead

router = APIRouter(prefix="/interviews", tags=["interviews"])


@router.get("", response_model=list[InterviewRead])
async def list_interviews(session: AsyncSession = Depends(get_session)):
    return list(await session.scalars(select(Interview).order_by(Interview.created_at.desc())))


@router.get("/{interview_id}", response_model=InterviewRead)
async def get_interview(interview_id: UUID, session: AsyncSession = Depends(get_session)):
    interview = await session.get(Interview, interview_id)
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    return interview
