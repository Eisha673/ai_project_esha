from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_session
from ..models.job import Job
from ..schemas.job import JobCreate, JobRead, JobUpdate

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("", response_model=JobRead)
async def create_job(payload: JobCreate, session: AsyncSession = Depends(get_session)):
    job = Job(title=payload.title, department=payload.department, seniority=payload.seniority)
    session.add(job)
    await session.commit()
    await session.refresh(job)
    return job


@router.get("", response_model=list[JobRead])
async def list_jobs(session: AsyncSession = Depends(get_session)):
    return list(await session.scalars(select(Job).order_by(Job.created_at.desc())))


@router.get("/{job_id}", response_model=JobRead)
async def get_job(job_id: UUID, session: AsyncSession = Depends(get_session)):
    job = await session.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.patch("/{job_id}", response_model=JobRead)
async def update_job(job_id: UUID, payload: JobUpdate, session: AsyncSession = Depends(get_session)):
    job = await session.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(job, key, value)
    await session.commit()
    await session.refresh(job)
    return job
