from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..agents.assessment_agent import run_assessment_agent
from ..agents.interview_agent import run_interview_agent
from ..agents.jd_agent import run_jd_agent
from ..agents.offer_agent import run_offer_agent
from ..agents.search_agent import run_search_agent
from ..database import get_session
from ..integrations import qstash
from ..models.agent_run import AgentRun
from ..models.job import Job
from ..models.pipeline_state import PipelineState

router = APIRouter(tags=["pipeline"])

AGENTS = {
    "jd": run_jd_agent,
    "search": run_search_agent,
    "assessment": run_assessment_agent,
    "interview": run_interview_agent,
    "offer": run_offer_agent,
}

NEXT_AGENT = {
    "search": "search",
    "assessment": "assessment",
    "interview": "interview",
    "offer": "offer",
}


class PipelineStart(BaseModel):
    title: str
    department: str | None = None
    seniority: str | None = None
    notes: str | None = None
    skills: list[str] = []
    location: str = "Remote"


async def _save_state(session: AsyncSession, row: PipelineState, state: dict):
    row.current_stage = state.get("current_stage")
    row.human_approved = state.get("human_approved", False)
    row.errors = state.get("errors", [])
    row.state_json = state
    await session.commit()


@router.post("/pipeline/start")
async def start_pipeline(payload: PipelineStart, session: AsyncSession = Depends(get_session)):
    job = Job(title=payload.title, department=payload.department, seniority=payload.seniority, status="pipeline_started")
    session.add(job)
    await session.flush()
    state = {
        "job_id": str(job.id),
        "role": payload.title,
        "department": payload.department or "",
        "seniority": payload.seniority or "",
        "notes": payload.notes or "",
        "skills": payload.skills,
        "location": payload.location,
        "current_stage": "jd",
        "human_approved": True,
        "errors": [],
    }
    pipeline_state = PipelineState(job_id=job.id, current_stage="jd", state_json=state, human_approved=True, errors=[])
    session.add(pipeline_state)
    await session.commit()
    await qstash.dispatch_agent("jd", str(job.id), {})
    return {"job_id": str(job.id), "status": "started"}


@router.get("/pipeline/{job_id}/status")
async def pipeline_status(job_id: UUID, session: AsyncSession = Depends(get_session)):
    row = await session.get(PipelineState, job_id)
    if not row:
        raise HTTPException(status_code=404, detail="Pipeline state not found")
    return {
        **row.state_json,
        "current_stage": row.current_stage,
        "human_approved": row.human_approved,
        "errors": row.errors,
    }


@router.get("/pipeline/activity/recent")
async def recent_activity(session: AsyncSession = Depends(get_session)):
    rows = await session.scalars(select(AgentRun).order_by(AgentRun.created_at.desc()).limit(10))
    return [
        {
            "agent_name": row.agent_name,
            "llm_provider": row.llm_provider,
            "nim_model": row.nim_model,
            "status": row.status,
            "output_summary": row.output_summary,
            "created_at": row.created_at.isoformat() if row.created_at else None,
        }
        for row in rows
    ]


@router.post("/pipeline/{job_id}/approve")
async def approve_pipeline(job_id: UUID, session: AsyncSession = Depends(get_session)):
    row = await session.get(PipelineState, job_id)
    if not row:
        raise HTTPException(status_code=404, detail="Pipeline state not found")
    state = dict(row.state_json)
    state["human_approved"] = True
    row.human_approved = True
    row.state_json = state
    await session.commit()
    next_agent = NEXT_AGENT.get(row.current_stage or "")
    if next_agent:
        await qstash.dispatch_agent(next_agent, str(job_id), {})
    return {"job_id": str(job_id), "status": "approved", "dispatched": next_agent}


@router.post("/agents/{agent_name}")
async def run_agent(agent_name: str, request: Request, session: AsyncSession = Depends(get_session)):
    if not await qstash.verify_signature(request):
        raise HTTPException(status_code=401, detail="Invalid QStash signature")
    if agent_name not in AGENTS:
        raise HTTPException(status_code=404, detail="Unknown agent")
    payload = await request.json()
    job_id = UUID(payload["job_id"])
    row = await session.get(PipelineState, job_id)
    if not row:
        raise HTTPException(status_code=404, detail="Pipeline state not found")
    state = dict(row.state_json)
    state["job_id"] = str(job_id)
    updated = await AGENTS[agent_name](state)
    await _save_state(session, row, updated)
    if updated.get("errors"):
        return {"status": "stopped", "errors": updated["errors"]}
    if updated.get("human_approved") is False:
        return {"status": "waiting_for_approval", "stage": updated.get("current_stage")}
    next_agent = NEXT_AGENT.get(updated.get("current_stage", ""))
    if next_agent:
        await qstash.dispatch_agent(next_agent, str(job_id), {})
    return {"status": "ok", "next_agent": next_agent}
