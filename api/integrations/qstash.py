import hmac
from hashlib import sha256

import httpx
from fastapi import Request

from ..config import settings

async def dispatch_agent(agent_name: str, job_id: str, payload: dict) -> dict:
    app_url = settings.VERCEL_URL
    if app_url and not app_url.startswith(("http://", "https://")):
        app_url = f"https://{app_url}"
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
