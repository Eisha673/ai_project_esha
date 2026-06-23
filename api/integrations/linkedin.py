import httpx

from ..config import settings

BASE_URL = "https://api.linkedin.com/v2"


async def _request(method: str, path: str, json: dict | None = None, params: dict | None = None) -> dict:
    if not settings.LINKEDIN_ACCESS_TOKEN:
        raise RuntimeError("LinkedIn access token is not configured")
    async with httpx.AsyncClient(base_url=BASE_URL, headers={"Authorization": f"Bearer {settings.LINKEDIN_ACCESS_TOKEN}"}) as client:
        for attempt in range(3):
            try:
                response = await client.request(method, path, json=json, params=params, timeout=5)
                response.raise_for_status()
                return response.json() if response.content else {}
            except httpx.HTTPError:
                if attempt == 2:
                    raise
        return {}


async def post_job(title: str, description: str, location: str) -> dict:
    return await _request("POST", "/jobPostings", {"title": title, "description": description, "location": location})


async def search_profiles(query: str, filters: dict) -> dict:
    return await _request("GET", "/peopleSearch", params={"q": query, **filters})
