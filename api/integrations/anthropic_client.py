from anthropic import AsyncAnthropic

from ..config import settings

CLAUDE_MODEL = "claude-sonnet-4-20250514"


def _client() -> AsyncAnthropic:
    return AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)


async def generate_jd(role: str, department: str | None, seniority: str | None, notes: str | None) -> str:
    response = await _client().messages.create(
        model=CLAUDE_MODEL,
        max_tokens=1400,
        messages=[
            {
                "role": "user",
                "content": (
                    "Write a complete, inclusive job description.\n"
                    f"Role: {role}\nDepartment: {department or 'General'}\nSeniority: {seniority or 'Unspecified'}\nNotes: {notes or ''}"
                ),
            }
        ],
    )
    return "".join(block.text for block in response.content if getattr(block, "type", "") == "text")


async def draft_offer_letter(candidate: dict, compensation: dict) -> str:
    response = await _client().messages.create(
        model=CLAUDE_MODEL,
        max_tokens=1200,
        messages=[
            {
                "role": "user",
                "content": f"Draft a formatted offer letter for candidate={candidate} compensation={compensation}.",
            }
        ],
    )
    return "".join(block.text for block in response.content if getattr(block, "type", "") == "text")
