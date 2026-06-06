from fastapi import APIRouter, Request

router = APIRouter(prefix="/greenhouse", tags=["webhooks"])


@router.post("")
async def greenhouse_webhook(request: Request):
    payload = await request.json()
    return {"status": "received", "event": payload.get("action") or payload.get("event")}
