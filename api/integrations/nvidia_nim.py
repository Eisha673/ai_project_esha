import json
from typing import Any

from openai import AsyncOpenAI
from pydantic import ValidationError

from ..config import settings
from ..schemas.llm import AssessmentOutput, BiasCheckOutput, JDValidationOutput, ResumeScoreOutput

NIM_BASE_URL = "https://integrate.api.nvidia.com/v1"
RESUME_MODEL = "nvidia/llama-3.3-nemotron-super-49b-v1"
ASSESSMENT_MODEL = "mistralai/mistral-nemotron"
SAFETY_MODEL = "nvidia/llama-3.1-nemotron-safety-guard-8b-v3"
JD_VALIDATION_MODEL = "nvidia/nvidia-nemotron-nano-9b-v2"


class NIMParseError(Exception):
    def __init__(self, message: str, raw_response: str):
        super().__init__(message)
        self.raw_response = raw_response


def _client() -> AsyncOpenAI:
    return AsyncOpenAI(base_url=NIM_BASE_URL, api_key=settings.NVIDIA_API_KEY)


def _content(response: Any) -> str:
    return (response.choices[0].message.content or "").strip()


def _json_model(raw: str, schema):
    try:
        return schema.model_validate(json.loads(raw)).model_dump()
    except (json.JSONDecodeError, ValidationError) as exc:
        raise NIMParseError(str(exc), raw) from exc


async def _chat_json(model: str, messages: list[dict], schema, max_tokens: int = 800, temperature: float = 0.1):
    last_error = None
    for attempt in range(3):
        try:
            response = await _client().chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return _json_model(_content(response), schema)
        except NIMParseError:
            raise
        except Exception as exc:
            last_error = exc
            if attempt == 2:
                raise
    raise last_error


async def score_resume(resume_text: str, job_requirements: str) -> dict:
    return await _chat_json(
        RESUME_MODEL,
        [
            {"role": "system", "content": "Evaluate resumes objectively. Respond only with valid JSON."},
            {
                "role": "user",
                "content": (
                    f"Job Requirements:\n{job_requirements}\n\nResume:\n{resume_text}\n\n"
                    'Return {"score":0-100,"strengths":[],"gaps":[],"recommendation":"advance|reject|review","reasoning":"..."}'
                ),
            },
        ],
        ResumeScoreOutput,
        max_tokens=512,
    )


async def generate_assessment(role: str, seniority: str, skills: list[str]) -> dict:
    return await _chat_json(
        ASSESSMENT_MODEL,
        [
            {"role": "system", "content": "Generate role-specific hiring assessments. JSON only."},
            {
                "role": "user",
                "content": (
                    f"Role: {role}\nSeniority: {seniority}\nSkills: {', '.join(skills)}\n"
                    'Return {"title":"...","duration_minutes":60,"sections":[{"type":"technical","question":"...","evaluation_criteria":"..."}]}'
                ),
            },
        ],
        AssessmentOutput,
        max_tokens=1024,
        temperature=0.3,
    )


async def check_bias(text: str) -> dict:
    response = None
    for attempt in range(3):
        try:
            response = await _client().chat.completions.create(
                model=SAFETY_MODEL,
                messages=[{"role": "user", "content": text}],
                max_tokens=200,
            )
            break
        except Exception:
            if attempt == 2:
                raise
    raw = _content(response)
    lowered = raw.lower()
    result = {"is_safe": "unsafe" not in lowered and ("safe" in lowered or "no violation" in lowered), "raw": raw}
    return BiasCheckOutput.model_validate(result).model_dump()


async def validate_jd(jd_text: str) -> dict:
    return await _chat_json(
        JD_VALIDATION_MODEL,
        [
            {"role": "system", "content": "Validate job descriptions for clarity and completeness. JSON only."},
            {"role": "user", "content": f'Review this JD:\n{jd_text}\nReturn {{"is_valid":true,"suggestions":[]}}'},
        ],
        JDValidationOutput,
        max_tokens=512,
    )
