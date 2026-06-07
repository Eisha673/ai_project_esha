import hmac
from hashlib import sha256

import httpx
from fastapi import Request

from ..config import settings


async def dispatch_agent(agent_name: str, job_id: str, payload: dict) -> dict:
    app_url = settings.VERCEL_URL
    if app_url and not app_url.startswith(("http://", "https://")):
        app_url = f"https://{app_url}"
    token = settings.QSTASH_TOKEN.strip()
    is_placeholder = token.startswith("your_") or token in {"", "xxx"}
    is_local_url = not app_url or "localhost" in app_url or "127.0.0.1" in app_url

    if is_placeholder or is_local_url:
        # Run agent locally instead of via QStash
        await _run_agent_locally(agent_name, job_id, payload)
        return {"status": "skipped", "reason": "QStash not configured — ran locally"}

    target_url = f"{app_url.rstrip('/')}/api/v1/agents/{agent_name}"
    qstash_url = settings.QSTASH_URL.rstrip("/")
    async with httpx.AsyncClient() as client:
        for attempt in range(3):
            try:
                response = await client.post(
                    f"{qstash_url}/v2/publish/{target_url}",
                    headers={
                        "Authorization": f"Bearer {settings.QSTASH_TOKEN}",
                        "Content-Type": "application/json",
                        "Upstash-Retries": "3",
                        "Upstash-Delay": "0s",
                    },
                    json={"job_id": job_id, **payload},
                    timeout=20,
                )
                response.raise_for_status()
                return response.json() if response.content else {"status": "queued"}
            except httpx.HTTPError:
                if attempt == 2:
                    raise
    return {"status": "queued"}


async def _run_agent_locally(agent_name: str, job_id: str, payload: dict):
    """Run agent directly in local/demo mode without QStash."""
    try:
        from ..agents.jd_agent import run_jd_agent
        from ..agents.search_agent import run_search_agent
        from ..agents.assessment_agent import run_assessment_agent
        from ..agents.interview_agent import run_interview_agent
        from ..agents.offer_agent import run_offer_agent
        from ..database import get_session
        from ..models.pipeline_state import PipelineState
        from uuid import UUID

        AGENTS = {
            "jd": run_jd_agent,
            "search": run_search_agent,
            "assessment": run_assessment_agent,
            "interview": run_interview_agent,
            "offer": run_offer_agent,
        }

        NEXT_AGENT = {
            "jd": "search",
            "search": "assessment",
            "assessment": "interview",
            "interview": "offer",
            "offer": None,
        }

        agent_fn = AGENTS.get(agent_name)
        if not agent_fn:
            return

        async for session in get_session():
            row = await session.get(PipelineState, UUID(job_id))
            if not row:
                return
            state = dict(row.state_json)
            state["job_id"] = job_id
            updated = await agent_fn(state)
            row.current_stage = updated.get("current_stage")
            row.human_approved = updated.get("human_approved", False)
            row.errors = updated.get("errors", [])
            row.state_json = updated
            await session.commit()

            # If no human approval needed, continue to next agent
            if updated.get("human_approved") is not False:
                next_agent = NEXT_AGENT.get(updated.get("current_stage", ""))
                if next_agent:
                    await _run_agent_locally(next_agent, job_id, {})
    except Exception as e:
        print(f"[local agent error] {agent_name}: {e}")


async def verify_signature(request: Request) -> bool:
    signature = request.headers.get("Upstash-Signature")
    if not signature:
        return False
    body = await request.body()
    for key in (settings.QSTASH_CURRENT_SIGNING_KEY, settings.QSTASH_NEXT_SIGNING_KEY):
        if key:
            digest = hmac.new(key.encode(), body, sha256).hexdigest()
            if hmac.compare_digest(signature, digest):
                return True
    return False