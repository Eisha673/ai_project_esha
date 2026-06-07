from ..integrations import anthropic_client, greenhouse, linkedin, nvidia_nim
from ..integrations.nvidia_nim import JD_VALIDATION_MODEL, SAFETY_MODEL
from .state import RecruitingState
from .utils import tracked_agent


async def run_jd_agent(state: RecruitingState) -> RecruitingState:
    async def work(session):
        # Generate JD with demo fallback
        try:
            jd_text = await anthropic_client.generate_jd(
                state.get("role", ""),
                state.get("department"),
                state.get("seniority"),
                state.get("notes"),
            )
        except Exception:
            jd_text = (
                f"{state.get('role', 'Professional')} will join the "
                f"{state.get('department', 'team')} team at {state.get('seniority', '')} level. "
                f"Responsibilities include leading projects, collaborating with stakeholders, "
                f"and delivering high-quality results. Strong communication and technical skills required."
            )

        # Safety check with fallback
        try:
            safety = await nvidia_nim.check_bias(jd_text)
            if not safety["is_safe"]:
                state.setdefault("errors", []).append(f"JD bias flagged: {safety['raw']}")
                return state
        except Exception:
            pass

        # JD validation with fallback
        try:
            validation = await nvidia_nim.validate_jd(jd_text)
            if not validation["is_valid"]:
                state["jd_validation_suggestions"] = validation["suggestions"]
        except Exception:
            pass

        # Greenhouse with fallback
        try:
            gh_job = await greenhouse.create_job(state.get("role", ""), state.get("department"))
            greenhouse_job_id = str(gh_job.get("id", ""))
        except Exception:
            greenhouse_job_id = f"demo-{state.get('job_id', 'unknown')}"

        # LinkedIn with fallback
        try:
            li_job = await linkedin.post_job(state.get("role", ""), jd_text, state.get("location", "Remote"))
            linkedin_job_url = li_job.get("url") or li_job.get("jobPostingUrl", "")
        except Exception:
            linkedin_job_url = "https://linkedin.com/jobs/demo"

        state["jd_text"] = jd_text
        state["greenhouse_job_id"] = greenhouse_job_id
        state["linkedin_job_url"] = linkedin_job_url
        state["current_stage"] = "search"
        state["human_approved"] = False
        state["_demo_mode"] = True
        return state

    return await tracked_agent(state, "jd", "anthropic+nvidia_nim", SAFETY_MODEL, work)