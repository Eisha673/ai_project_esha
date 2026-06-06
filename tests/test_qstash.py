import hmac
from hashlib import sha256

import pytest
from starlette.requests import Request

from api.config import settings
from api.integrations.qstash import verify_signature


def make_request(body: bytes, signature: str):
    async def receive():
        return {"type": "http.request", "body": body, "more_body": False}

    return Request({"type": "http", "method": "POST", "path": "/", "headers": [(b"upstash-signature", signature.encode())]}, receive)


@pytest.mark.asyncio
async def test_verify_signature(monkeypatch):
    monkeypatch.setattr(settings, "QSTASH_CURRENT_SIGNING_KEY", "secret")
    body = b'{"job_id":"1"}'
    signature = hmac.new(b"secret", body, sha256).hexdigest()
    assert await verify_signature(make_request(body, signature)) is True


@pytest.mark.asyncio
async def test_verify_signature_rejects_invalid(monkeypatch):
    monkeypatch.setattr(settings, "QSTASH_CURRENT_SIGNING_KEY", "secret")
    assert await verify_signature(make_request(b"{}", "bad")) is False
