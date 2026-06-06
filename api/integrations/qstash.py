import hmac
from hashlib import sha256

import httpx
from fastapi import Request

from ..config import settings

QSTASH_URL = "https://qstash.upstash.io/v2/publish"


async def dispatch_agent(agent_name: str, job_id: str, payload: dict) -> dict:
    target_url = f"{settings.VERCEL_URL}/api/v1/agents/{agent_name}"
    async with httpx.AsyncClient() as client:
        for attempt in range(3):
            try:
                response = await client.post(
                    f"{QSTASH_URL}/{target_url}",
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
