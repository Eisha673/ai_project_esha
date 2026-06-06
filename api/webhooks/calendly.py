import hmac
from datetime import datetime
from hashlib import sha256

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import settings
from ..database import get_session
from ..integrations import qstash
from ..models.interview import Interview

router = APIRouter(prefix="/calendly", tags=["webhooks"])


def _verify(signature: str | None, body: bytes) -> bool:
    if not settings.CALENDLY_WEBHOOK_SIGNING_KEY:
        return False
    digest = hmac.new(settings.CALENDLY_WEBHOOK_SIGNING_KEY.encode(), body, sha256).hexdigest()
    expected = f"v1={digest}"
    return bool(signature) and (hmac.compare_digest(signature, digest) or hmac.compare_digest(signature, expected))


@router.post("")
async def calendly_webhook(request: Request, session: AsyncSession = Depends(get_session)):
    body = await request.body()
    if not _verify(request.headers.get("Calendly-Webhook-Signature"), body):
        raise HTTPException(status_code=401, detail="Invalid Calendly signature")
    payload = await request.json()
    event = payload.get("event")
    resource = payload.get("payload", {})
    link = resource.get("scheduling_url") or resource.get("event")
    interview = await session.scalar(select(Interview).where(Interview.calendly_link == link))
    if interview and event == "invitee.created":
        interview.scheduled_at = datetime.fromisoformat(resource.get("scheduled_event", {}).get("start_time").replace("Z", "+00:00"))
    elif interview and event == "invitee.canceled":
        interview.scheduled_at = None
        if interview.candidate_id:
            await qstash.dispatch_agent("interview", str(interview.candidate_id), {})
    await session.commit()
    return {"status": "ok"}
