import uuid

import pytest

from api.agents import assessment_agent, interview_agent, jd_agent, offer_agent, search_agent


@pytest.fixture
def state():
    return {
        "job_id": str(uuid.uuid4()),
        "role": "Backend Engineer",
        "department": "Engineering",
        "seniority": "Senior",
        "skills": ["Python"],
        "location": "Remote",
        "jd_text": "Build APIs",
        "greenhouse_job_id": "gh-job",
        "current_stage": "jd",
        "human_approved": True,
        "errors": [],
    }


@pytest.mark.asyncio
async def test_jd_agent_bias_gate(monkeypatch, state):
    async def generate_jd(*args):
        return "Inclusive JD"

    async def check_bias(text):
        return {"is_safe": True, "raw": "safe"}

    async def validate_jd(text):
        return {"is_valid": True, "suggestions": []}

    async def create_job(title, department):
        return {"id": "gh-job"}

    async def post_job(title, description, location):
        return {"url": "https://linkedin/jobs/1"}

    monkeypatch.setattr(jd_agent.anthropic_client, "generate_jd", generate_jd)
    monkeypatch.setattr(jd_agent.nvidia_nim, "check_bias", check_bias)
    monkeypatch.setattr(jd_agent.nvidia_nim, "validate_jd", validate_jd)
    monkeypatch.setattr(jd_agent.greenhouse, "create_job", create_job)
    monkeypatch.setattr(jd_agent.linkedin, "post_job", post_job)
    updated = await jd_agent.run_jd_agent(state)
    assert updated["current_stage"] == "search"
    assert updated["human_approved"] is False


@pytest.mark.asyncio
async def test_search_agent_calls_bias(monkeypatch, state):
    calls = {"bias": 0}

    async def get_applications(job_id):
        return [{"id": "app-1", "full_name": "A Candidate", "email": "a@example.com", "resume_text": "Python"}]

    async def score_resume(resume, requirements):
        return {"score": 90, "strengths": ["Python"], "gaps": [], "recommendation": "advance", "reasoning": "Strong"}

    async def check_bias(text):
        calls["bias"] += 1
        return {"is_safe": True, "raw": "safe"}

    async def ok(*args):
        return {}

    monkeypatch.setattr(search_agent.greenhouse, "get_applications", get_applications)
    monkeypatch.setattr(search_agent.nvidia_nim, "score_resume", score_resume)
    monkeypatch.setattr(search_agent.nvidia_nim, "check_bias", check_bias)
    monkeypatch.setattr(search_agent.greenhouse, "advance_candidate", ok)
    monkeypatch.setattr(search_agent.greenhouse, "reject_candidate", ok)
    updated = await search_agent.run_search_agent(state)
    assert calls["bias"] == 1
    assert updated["human_approved"] is False


def test_all_agent_modules_call_check_bias():
    for module in (jd_agent, search_agent, assessment_agent, interview_agent, offer_agent):
        assert "check_bias" in getattr(module, "__loader__").get_source(module.__name__)
