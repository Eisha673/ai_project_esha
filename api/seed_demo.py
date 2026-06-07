import asyncio
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy import select

from api.database import AsyncSessionLocal, Base, get_engine
from api.models.agent_run import AgentRun
from api.models.candidate import Candidate
from api.models.interview import Interview
from api.models.job import Job
from api.models.offer import Offer
from api.models.pipeline_state import PipelineState


async def seed() -> None:
    engine = get_engine()
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        existing = await session.scalar(select(Job.id).limit(1))
        if existing:
            return

        jobs = [
            Job(
                title="Senior Backend Engineer",
                department="Engineering",
                seniority="Senior",
                status="pipeline_started",
                jd_text="Build reliable APIs, own integrations, and improve hiring automation workflows.",
            ),
            Job(
                title="Product Designer",
                department="Design",
                seniority="Mid-level",
                status="screening",
                jd_text="Design thoughtful recruiter and candidate experiences across the pipeline.",
            ),
            Job(
                title="People Operations Manager",
                department="People",
                seniority="Lead",
                status="offer",
                jd_text="Lead people operations programs and improve hiring process quality.",
            ),
        ]
        session.add_all(jobs)
        await session.flush()

        candidates = [
            Candidate(
                job_id=jobs[0].id,
                full_name="Ayesha Khan",
                email="ayesha@example.com",
                resume_text="Python, FastAPI, Postgres, distributed systems.",
                nim_screen_score=91,
                nim_screen_reasoning="Strong backend and API ownership experience.",
                nim_screen_strengths=["FastAPI", "Postgres", "API design"],
                nim_screen_gaps=["Limited HR tech domain exposure"],
                stage="shortlisted",
            ),
            Candidate(
                job_id=jobs[0].id,
                full_name="Hamza Ali",
                email="hamza@example.com",
                resume_text="Node, Python, cloud deployments.",
                nim_screen_score=76,
                nim_screen_reasoning="Solid platform background with good deployment experience.",
                nim_screen_strengths=["Cloud", "Automation"],
                nim_screen_gaps=["Less SQLAlchemy experience"],
                stage="assessment",
            ),
            Candidate(
                job_id=jobs[1].id,
                full_name="Sara Malik",
                email="sara@example.com",
                resume_text="Product design, research, design systems.",
                nim_screen_score=84,
                nim_screen_reasoning="Good portfolio and strong research process.",
                nim_screen_strengths=["Research", "Design systems"],
                nim_screen_gaps=[],
                stage="interview",
            ),
            Candidate(
                job_id=jobs[2].id,
                full_name="Bilal Ahmed",
                email="bilal@example.com",
                resume_text="People operations, onboarding, HR analytics.",
                nim_screen_score=88,
                nim_screen_reasoning="Strong operations and stakeholder management experience.",
                nim_screen_strengths=["HR analytics", "Onboarding"],
                nim_screen_gaps=[],
                stage="offer",
            ),
        ]
        session.add_all(candidates)
        await session.flush()

        now = datetime.now(timezone.utc)
        session.add_all(
            [
                Interview(
                    candidate_id=candidates[2].id,
                    calendly_link="https://calendly.com/demo/product-designer",
                    scheduled_at=now + timedelta(days=2),
                    question_bank=["Walk through a complex design decision.", "How do you validate recruiter workflows?"],
                ),
                Interview(
                    candidate_id=candidates[1].id,
                    calendly_link="https://calendly.com/demo/backend-engineer",
                    scheduled_at=now + timedelta(days=3),
                    question_bank=["Design an async API integration.", "How would you debug a failed webhook?"],
                ),
                Offer(
                    candidate_id=candidates[3].id,
                    base_salary=Decimal("145000.00"),
                    equity_percentage=Decimal("1.25"),
                    bonus_percentage=Decimal("10.00"),
                    offer_letter_text="Demo offer letter for People Operations Manager.",
                    greenhouse_offer_id="demo-offer-001",
                    status="sent",
                    expires_at=now + timedelta(days=7),
                ),
            ]
        )

        stages = ["search", "assessment", "interview"]
        for job, stage in zip(jobs, stages, strict=False):
            state = {
                "job_id": str(job.id),
                "role": job.title,
                "department": job.department or "",
                "seniority": job.seniority or "",
                "skills": ["Python", "Automation"] if job.department == "Engineering" else ["Communication", "Process"],
                "location": "Remote",
                "current_stage": stage,
                "human_approved": stage in {"assessment", "interview"},
                "errors": [],
            }
            session.add(PipelineState(job_id=job.id, current_stage=stage, state_json=state, human_approved=state["human_approved"], errors=[]))

        session.add_all(
            [
                AgentRun(job_id=jobs[0].id, agent_name="jd", llm_provider="anthropic+nvidia_nim", nim_model="nvidia/llama-3.1-nemotron-safety-guard-8b-v3", status="done", output_summary="JD generated and posted"),
                AgentRun(job_id=jobs[0].id, agent_name="search", llm_provider="nvidia_nim", nim_model="nvidia/nemotron-4-340b-instruct", status="done", output_summary="2 candidates screened"),
                AgentRun(job_id=jobs[1].id, agent_name="interview", llm_provider="openai+nvidia_nim", nim_model="nvidia/llama-3.1-nemotron-safety-guard-8b-v3", status="done", output_summary="Interview scheduled"),
                AgentRun(job_id=jobs[2].id, agent_name="offer", llm_provider="anthropic+nvidia_nim", nim_model="nvidia/llama-3.1-nemotron-safety-guard-8b-v3", status="done", output_summary="Offer sent"),
            ]
        )
        await session.commit()


if __name__ == "__main__":
    asyncio.run(seed())
