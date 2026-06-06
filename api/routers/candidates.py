from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_session
from ..models.candidate import Candidate
from ..schemas.candidate import CandidateRead, CandidateStageUpdate

router = APIRouter(prefix="/candidates", tags=["candidates"])


@router.get("", response_model=list[CandidateRead])
async def list_candidates(job_id: UUID | None = Query(default=None), session: AsyncSession = Depends(get_session)):
    statement = select(Candidate).order_by(Candidate.created_at.desc())
    if job_id:
        statement = statement.where(Candidate.job_id == job_id)
    return list(await session.scalars(statement))


@router.get("/{candidate_id}", response_model=CandidateRead)
async def get_candidate(candidate_id: UUID, session: AsyncSession = Depends(get_session)):
    candidate = await session.get(Candidate, candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate


@router.patch("/{candidate_id}/stage", response_model=CandidateRead)
async def update_candidate_stage(candidate_id: UUID, payload: CandidateStageUpdate, session: AsyncSession = Depends(get_session)):
    candidate = await session.get(Candidate, candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    candidate.stage = payload.stage
    await session.commit()
    await session.refresh(candidate)
    return candidate
