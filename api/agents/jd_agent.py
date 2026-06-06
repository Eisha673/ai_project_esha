from ..integrations import anthropic_client, greenhouse, linkedin, nvidia_nim
from ..integrations.nvidia_nim import JD_VALIDATION_MODEL, SAFETY_MODEL
from .state import RecruitingState
from .utils import tracked_agent


async def run_jd_agent(state: RecruitingState) -> RecruitingState:
    async def work(session):
        jd_text = await anthropic_client.generate_jd(
            state.get("role", ""),
            state.get("department"),
            state.get("seniority"),
            state.get("notes"),
        )
        safety = await nvidia_nim.check_bias(jd_text)
        if not safety["is_safe"]:
            state.setdefault("errors", []).append(f"JD bias flagged: {safety['raw']}")
            return state
        validation = await nvidia_nim.validate_jd(jd_text)
        if not validation["is_valid"]:
            state["jd_validation_suggestions"] = validation["suggestions"]
        gh_job = await greenhouse.create_job(state.get("role", ""), state.get("department"))
        li_job = await linkedin.post_job(state.get("role", ""), jd_text, state.get("location", "Remote"))
        state["jd_text"] = jd_text
        state["greenhouse_job_id"] = str(gh_job.get("id", ""))
        state["linkedin_job_url"] = li_job.get("url") or li_job.get("jobPostingUrl", "")
        state["current_stage"] = "search"
        state["human_approved"] = False
        state["_bias_model"] = SAFETY_MODEL
        state["_validation_model"] = JD_VALIDATION_MODEL
        return state

    return await tracked_agent(state, "jd", "anthropic+nvidia_nim", SAFETY_MODEL, work)
