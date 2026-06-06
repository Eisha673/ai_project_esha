from fastapi.testclient import TestClient

from api.index import app


client = TestClient(app)


def test_health():
    assert client.get("/health").json() == {"status": "ok"}


def test_agent_endpoint_requires_qstash_signature():
    response = client.post("/api/v1/agents/jd", json={"job_id": "00000000-0000-0000-0000-000000000000"})
    assert response.status_code == 401
