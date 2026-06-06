import httpx

from ..config import settings


async def _request(method: str, path: str, json: dict | None = None) -> dict:
    async with httpx.AsyncClient(base_url=settings.GREENHOUSE_BASE_URL, auth=(settings.GREENHOUSE_API_KEY, "")) as client:
        for attempt in range(3):
            try:
                response = await client.request(method, path, json=json, timeout=20)
                response.raise_for_status()
                return response.json() if response.content else {}
            except httpx.HTTPError:
                if attempt == 2:
                    raise
        return {}


async def create_job(title: str, department: str | None) -> dict:
    return await _request("POST", "/jobs", {"title": title, "department": department})


async def get_applications(job_id: str) -> list[dict]:
    result = await _request("GET", f"/applications?job_id={job_id}")
    return result if isinstance(result, list) else result.get("applications", [])


async def advance_candidate(application_id: str) -> dict:
    return await _request("PATCH", f"/applications/{application_id}/advance")


async def reject_candidate(application_id: str) -> dict:
    return await _request("PATCH", f"/applications/{application_id}/reject")


async def create_offer(candidate_id: str, compensation: dict) -> dict:
    return await _request("POST", "/offers", {"candidate_id": candidate_id, "compensation": compensation})


async def send_candidate_message(candidate_id: str, subject: str, body: str) -> dict:
    return await _request("POST", f"/candidates/{candidate_id}/emails", {"subject": subject, "body": body})
