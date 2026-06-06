import httpx

from ..config import settings

BASE_URL = "https://api.calendly.com"


async def _request(method: str, path: str, json: dict | None = None, params: dict | None = None) -> dict:
    async with httpx.AsyncClient(base_url=BASE_URL, headers={"Authorization": f"Bearer {settings.CALENDLY_ACCESS_TOKEN}"}) as client:
        for attempt in range(3):
            try:
                response = await client.request(method, path, json=json, params=params, timeout=20)
                response.raise_for_status()
                return response.json() if response.content else {}
            except httpx.HTTPError:
                if attempt == 2:
                    raise
        return {}


async def create_scheduling_link(candidate_name: str, event_type: str) -> dict:
    return await _request("POST", "/scheduling_links", {"owner": settings.CALENDLY_USER_URI, "owner_type": "User", "event_type": event_type, "max_event_count": 1, "candidate_name": candidate_name})


async def get_scheduled_events(min_start_time: str) -> dict:
    return await _request("GET", "/scheduled_events", params={"user": settings.CALENDLY_USER_URI, "min_start_time": min_start_time})
