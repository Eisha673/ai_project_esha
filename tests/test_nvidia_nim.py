import pytest

from api.integrations import nvidia_nim


class Message:
    content = '{"score": 87, "strengths": ["Python"], "gaps": ["None"], "recommendation": "advance", "reasoning": "Strong fit."}'


class Choice:
    message = Message()


class Response:
    choices = [Choice()]


class Completion:
    async def create(self, **kwargs):
        if kwargs["model"] == nvidia_nim.ASSESSMENT_MODEL:
            Message.content = '{"title": "Backend Assessment", "duration_minutes": 60, "sections": [{"type": "technical", "question": "Build an API", "evaluation_criteria": "Correctness"}]}'
        elif kwargs["model"] == nvidia_nim.SAFETY_MODEL:
            Message.content = "safe"
        else:
            Message.content = '{"score": 87, "strengths": ["Python"], "gaps": ["None"], "recommendation": "advance", "reasoning": "Strong fit."}'
        return Response()


class Chat:
    completions = Completion()


class Client:
    chat = Chat()


@pytest.fixture(autouse=True)
def mock_nim(monkeypatch):
    monkeypatch.setattr(nvidia_nim, "_client", lambda: Client())


@pytest.mark.asyncio
async def test_score_resume_validates_json():
    result = await nvidia_nim.score_resume("resume", "requirements")
    assert result["score"] == 87
    assert result["recommendation"] == "advance"


@pytest.mark.asyncio
async def test_generate_assessment_validates_json():
    result = await nvidia_nim.generate_assessment("Engineer", "Senior", ["Python"])
    assert result["duration_minutes"] == 60
    assert result["sections"][0]["type"] == "technical"


@pytest.mark.asyncio
async def test_check_bias_returns_safety_result():
    result = await nvidia_nim.check_bias("neutral text")
    assert result == {"is_safe": True, "raw": "safe"}


@pytest.mark.asyncio
async def test_parse_error_attaches_raw(monkeypatch):
    Message.content = "not json"

    class BadCompletion(Completion):
        async def create(self, **kwargs):
            return Response()

    class BadChat:
        completions = BadCompletion()

    class BadClient:
        chat = BadChat()

    monkeypatch.setattr(nvidia_nim, "_client", lambda: BadClient())
    with pytest.raises(nvidia_nim.NIMParseError) as exc:
        await nvidia_nim.score_resume("resume", "requirements")
    assert exc.value.raw_response == "not json"
