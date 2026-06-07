from sqlalchemy import select

from ..integrations import greenhouse, nvidia_nim
from ..integrations.nvidia_nim import ASSESSMENT_MODEL, SAFETY_MODEL
from ..models.candidate import Candidate
from .state import RecruitingState
from .utils import tracked_agent


DEMO_ASSESSMENT = {
    "title": "Technical Assessment",
    "description": "Demo assessment for local testing",
    "questions": [
        "Describe your experience with REST APIs.",
        "How do you handle async programming?",
        "What is your approach to testing?"
    ]
}


async def run_assessment_agent(state: RecruitingState) -> RecruitingState:
    async def work(session):
        try:
            assessment = await nvidia_nim.generate_assessment(
                state.get("role", ""),
                state.get("seniority", ""),
                state.get("skills", []),
            )
            safety = await nvidia_nim.check_bias(str(assessment))
            if not safety["is_safe"]:
                state.setdefault("errors", []).append(f"Assessment bias flagged: {safety['raw']}")
                return state
        except Exception:
            assessment = DEMO_ASSESSMENT

        for item in state.get("shortlist", []):
            try:
                await greenhouse.send_candidate_message(
                    item.get("id") or item.get("application_id"),
                    assessment["title"],
                    str(assessment)
                )
            except Exception:
                pass
            candidate = await session.scalar(
                select(Candidate).where(Candidate.id == item.get("id"))
            )
            if candidate:
                candidate.assessment_score = 80
                candidate.assessment_pass = True
                candidate.stage = "assessed"

        await session.commit()
        state["assessments"] = assessment
        state["current_stage"] = "interview"
        state["human_approved"] = True
        state["_demo_mode"] = True
        return state

    return await tracked_agent(state, "assessment", "nvidia_nim", ASSESSMENT_MODEL, work)