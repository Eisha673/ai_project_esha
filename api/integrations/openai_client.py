import json

from openai import AsyncOpenAI

from ..config import settings
from ..schemas.llm import InterviewQuestionsOutput


def _client() -> AsyncOpenAI:
    return AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


async def generate_interview_questions(candidate_profile: dict, role: str) -> list[str]:
    response = await _client().chat.completions.create(
        model="gpt-4o",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": 'Return JSON only: {"questions":["..."]}.'},
            {"role": "user", "content": f"Role: {role}\nCandidate: {candidate_profile}"},
        ],
        temperature=0.2,
    )
    raw = response.choices[0].message.content or '{"questions":[]}'
    return InterviewQuestionsOutput.model_validate(json.loads(raw)).questions
