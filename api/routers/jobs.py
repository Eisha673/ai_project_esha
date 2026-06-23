from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_session
from ..models.job import Job
from ..models.pipeline_state import PipelineState
from ..schemas.job import JobCreate, JobRead, JobUpdate

router = APIRouter(prefix="/jobs", tags=["jobs"])


def _serialize_job(job: Job, pipeline_state: PipelineState | None = None) -> dict:
    state = {}
    if pipeline_state:
        state = pipeline_state.state_json or {}
    status = job.status
    if pipeline_state:
        status = state.get("current_stage") or pipeline_state.current_stage or job.status
    return {
        "id": job.id,
        "title": job.title,
        "department": job.department,
        "seniority": job.seniority,
        "greenhouse_id": state.get("greenhouse_job_id") or job.greenhouse_id,
        "linkedin_job_url": state.get("linkedin_job_url") or job.linkedin_job_url,
        "jd_text": state.get("jd_text") or job.jd_text,
        "status": status,
        "created_at": job.created_at,
        "updated_at": job.updated_at,
    }


@router.post("", response_model=JobRead)
async def create_job(payload: JobCreate, session: AsyncSession = Depends(get_session)):
    job = Job(title=payload.title, department=payload.department, seniority=payload.seniority)
    session.add(job)
    await session.commit()
    await session.refresh(job)
    return job


@router.get("", response_model=list[JobRead])
async def list_jobs(session: AsyncSession = Depends(get_session)):
    rows = await session.execute(
        select(Job, PipelineState)
        .outerjoin(PipelineState, PipelineState.job_id == Job.id)
        .order_by(Job.created_at.desc())
    )
    return [_serialize_job(job, pipeline_state) for job, pipeline_state in rows]


@router.get("/{job_id}", response_model=JobRead)
async def get_job(job_id: UUID, session: AsyncSession = Depends(get_session)):
    row = await session.execute(
        select(Job, PipelineState)
        .outerjoin(PipelineState, PipelineState.job_id == Job.id)
        .where(Job.id == job_id)
    )
    result = row.one_or_none()
    if not result:
        raise HTTPException(status_code=404, detail="Job not found")
    job, pipeline_state = result
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return _serialize_job(job, pipeline_state)


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
