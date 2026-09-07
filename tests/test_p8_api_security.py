"""Deterministic P8 API authentication, authorization and rate-limit tests."""

import os

import pytest
from fastapi.testclient import TestClient

os.environ["P8_API_KEY"] = "user-test-key"
os.environ["P8_ADMIN_API_KEY"] = "admin-test-key"

from api import app, limiter  # noqa: E402
from src.api_security import AuthenticationError, RateLimiter, authenticate  # noqa: E402


@pytest.fixture(autouse=True)
def reset_limiter():
    limiter.reset()
    yield
    limiter.reset()


def test_authentication_uses_roles_and_rejects_invalid_key():
    assert authenticate("user-test-key") == "user"
    assert authenticate("admin-test-key") == "admin"
    with pytest.raises(AuthenticationError):
        authenticate("wrong-key")


def test_health_is_public_and_query_requires_authentication():
    client = TestClient(app)
    assert client.get("/health").status_code == 200
    assert client.post("/v1/query", json={"question": "hello"}).status_code == 401


def test_query_accepts_authenticated_request_without_initializing_real_pipeline(monkeypatch):
    class FakePipeline:
        def ask(self, question, top_k=None, conversation_history=None):
            return {"question": question, "answer": "safe answer", "document_count": 1}

    monkeypatch.setattr("api.get_pipeline", lambda: FakePipeline())
    client = TestClient(app)
    response = client.post("/v1/query", headers={"X-API-Key": "user-test-key"}, json={"question": "What happened?"})
    assert response.status_code == 200
    assert response.json()["answer"] == "safe answer"
    assert response.json()["request_id"]


def test_admin_endpoint_denies_user_and_allows_admin():
    client = TestClient(app)
    assert client.get("/v1/admin/info", headers={"X-API-Key": "user-test-key"}).status_code == 403
    assert client.get("/v1/admin/info", headers={"X-API-Key": "admin-test-key"}).status_code == 200


def test_rate_limiter_blocks_after_budget():
    limiter = RateLimiter(max_requests=2, window_seconds=60)
    assert limiter.allow("client", now=100.0)
    assert limiter.allow("client", now=101.0)
    assert not limiter.allow("client", now=102.0)
    assert limiter.allow("other-client", now=102.0)


def test_rate_limit_endpoint_returns_429(monkeypatch):
    class FakePipeline:
        def ask(self, question, top_k=None, conversation_history=None):
            return {"question": question, "answer": "safe", "document_count": 0}

    monkeypatch.setattr("api.get_pipeline", lambda: FakePipeline())
    monkeypatch.setattr("api.limiter", RateLimiter(max_requests=1, window_seconds=60))
    client = TestClient(app)
    headers = {"X-API-Key": "user-test-key"}
    assert client.post("/v1/query", headers=headers, json={"question": "one"}).status_code == 200
    assert client.post("/v1/query", headers=headers, json={"question": "two"}).status_code == 429


def test_invalid_payload_does_not_leak_internal_details():
    client = TestClient(app)
    response = client.post("/v1/query", headers={"X-API-Key": "user-test-key"}, json={"question": "x" * 2001})
    assert response.status_code == 422
    assert "Traceback" not in response.text
    assert "user-test-key" not in response.text
