import asyncio

from ..config import settings
from ..integrations import anthropic_client, greenhouse, linkedin, nvidia_nim
from .state import RecruitingState

LIVE_CALL_TIMEOUT_SECONDS = 0.15


async def run_jd_agent(state: RecruitingState) -> RecruitingState:
    async def work(session):
        # Generate JD with demo fallback
        if settings.ENABLE_LIVE_AGENT_CALLS:
            try:
                jd_text = await asyncio.wait_for(
                    anthropic_client.generate_jd(
                        state.get("role", ""),
                        state.get("department"),
                        state.get("seniority"),
                        state.get("notes"),
                    ),
                    timeout=LIVE_CALL_TIMEOUT_SECONDS,
                )
            except Exception:
                jd_text = (
                    f"{state.get('role', 'Professional')} will join the "
                    f"{state.get('department', 'team')} team at {state.get('seniority', '')} level. "
                    f"Responsibilities include leading projects, collaborating with stakeholders, "
                    f"and delivering high-quality results. Strong communication and technical skills required."
                )
        else:
            jd_text = (
                f"{state.get('role', 'Professional')} will join the "
                f"{state.get('department', 'team')} team at {state.get('seniority', '')} level. "
                f"Responsibilities include leading projects, collaborating with stakeholders, "
                f"and delivering high-quality results. Strong communication and technical skills required."
            )

        # Safety check with fallback
        if settings.ENABLE_LIVE_AGENT_CALLS:
            try:
                safety = await asyncio.wait_for(nvidia_nim.check_bias(jd_text), timeout=LIVE_CALL_TIMEOUT_SECONDS)
                if not safety["is_safe"]:
                    state.setdefault("errors", []).append(f"JD bias flagged: {safety['raw']}")
                    return state
            except Exception:
                pass

        # JD validation with fallback
        if settings.ENABLE_LIVE_AGENT_CALLS:
            try:
                validation = await asyncio.wait_for(nvidia_nim.validate_jd(jd_text), timeout=LIVE_CALL_TIMEOUT_SECONDS)
                if not validation["is_valid"]:
                    state["jd_validation_suggestions"] = validation["suggestions"]
            except Exception:
                pass

        # Greenhouse with fallback
        if settings.ENABLE_LIVE_AGENT_CALLS:
            try:
                gh_job = await asyncio.wait_for(
                    greenhouse.create_job(state.get("role", ""), state.get("department")),
                    timeout=LIVE_CALL_TIMEOUT_SECONDS,
                )
                greenhouse_job_id = str(gh_job.get("id", ""))
            except Exception:
                greenhouse_job_id = f"demo-{state.get('job_id', 'unknown')}"
        else:
            greenhouse_job_id = f"demo-{state.get('job_id', 'unknown')}"

        # LinkedIn with fallback
        if settings.ENABLE_LIVE_AGENT_CALLS:
            try:
                li_job = await asyncio.wait_for(
                    linkedin.post_job(state.get("role", ""), jd_text, state.get("location", "Remote")),
                    timeout=LIVE_CALL_TIMEOUT_SECONDS,
                )
                linkedin_job_url = li_job.get("url") or li_job.get("jobPostingUrl", "")
            except Exception:
                linkedin_job_url = "https://linkedin.com/jobs/demo"
        else:
            linkedin_job_url = "https://linkedin.com/jobs/demo"

        state["jd_text"] = jd_text
        state["greenhouse_job_id"] = greenhouse_job_id
        state["linkedin_job_url"] = linkedin_job_url
        state["current_stage"] = "search"
        state["human_approved"] = False
        state["_demo_mode"] = not settings.ENABLE_LIVE_AGENT_CALLS
        return state

    return await work(None)
