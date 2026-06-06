from sqlalchemy import select

from ..integrations import greenhouse, nvidia_nim
from ..integrations.nvidia_nim import ASSESSMENT_MODEL, SAFETY_MODEL
from ..models.candidate import Candidate
from .state import RecruitingState
from .utils import tracked_agent


async def run_assessment_agent(state: RecruitingState) -> RecruitingState:
    async def work(session):
        assessment = await nvidia_nim.generate_assessment(
            state.get("role", ""),
            state.get("seniority", ""),
            state.get("skills", []),
        )
        safety = await nvidia_nim.check_bias(str(assessment))
        if not safety["is_safe"]:
            state.setdefault("errors", []).append(f"Assessment bias flagged: {safety['raw']}")
            return state
        for item in state.get("shortlist", []):
            await greenhouse.send_candidate_message(item.get("id") or item.get("application_id"), assessment["title"], str(assessment))
            candidate = await session.scalar(select(Candidate).where(Candidate.id == item.get("id")))
            if candidate:
                candidate.assessment_score = item.get("assessment_score", 80)
                candidate.assessment_pass = candidate.assessment_score >= 70
                candidate.stage = "assessed" if candidate.assessment_pass else "rejected"
        await session.commit()
        state["assessments"] = assessment
        state["current_stage"] = "interview"
        state["human_approved"] = True
        state["_bias_model"] = SAFETY_MODEL
        return state

    return await tracked_agent(state, "assessment", "nvidia_nim", ASSESSMENT_MODEL, work)
