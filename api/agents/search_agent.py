from ..integrations import greenhouse, nvidia_nim
from ..integrations.nvidia_nim import RESUME_MODEL, SAFETY_MODEL
from ..models.candidate import Candidate
from .state import RecruitingState
from .utils import tracked_agent


async def run_search_agent(state: RecruitingState) -> RecruitingState:
    async def work(session):
        applications = await greenhouse.get_applications(state.get("greenhouse_job_id") or state["job_id"])
        shortlist = []
        candidates = []
        for app in applications:
            resume_text = app.get("resume_text") or app.get("resume") or ""
            score = await nvidia_nim.score_resume(resume_text, state.get("job_requirements") or state.get("jd_text", ""))
            safety = await nvidia_nim.check_bias(score["reasoning"])
            bias_flagged = not safety["is_safe"]
            candidate = Candidate(
                job_id=state["job_id"],
                full_name=app.get("full_name") or app.get("candidate", {}).get("name"),
                email=app.get("email") or app.get("candidate", {}).get("email"),
                greenhouse_application_id=str(app.get("id", "")),
                resume_text=resume_text,
                nim_screen_score=score["score"],
                nim_screen_reasoning=score["reasoning"],
                nim_screen_strengths=score["strengths"],
                nim_screen_gaps=score["gaps"],
                nim_bias_flagged=bias_flagged,
                stage="shortlisted" if score["score"] >= 60 else "rejected",
            )
            session.add(candidate)
            await session.flush()
            record = {
                "id": str(candidate.id),
                "full_name": candidate.full_name,
                "email": candidate.email,
                "score": score["score"],
                "reasoning": score["reasoning"],
                "bias_flagged": bias_flagged,
                "application_id": candidate.greenhouse_application_id,
            }
            candidates.append(record)
            if score["score"] >= 60:
                await greenhouse.advance_candidate(candidate.greenhouse_application_id)
                shortlist.append(record)
            else:
                await greenhouse.reject_candidate(candidate.greenhouse_application_id)
        await session.commit()
        state["candidates"] = candidates
        state["shortlist"] = shortlist
        state["current_stage"] = "assessment"
        state["human_approved"] = False
        state["_bias_model"] = SAFETY_MODEL
        return state

    return await tracked_agent(state, "search", "nvidia_nim", RESUME_MODEL, work)
