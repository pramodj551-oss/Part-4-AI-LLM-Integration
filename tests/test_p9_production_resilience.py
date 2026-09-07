import pytest

from src.p9_resilience import CircuitBreaker, RequestMetrics, timed_request


def test_metrics_records_success_and_error():
    metrics = RequestMetrics()
    with timed_request(metrics):
        pass
    with pytest.raises(RuntimeError):
        with timed_request(metrics):
            raise RuntimeError("boom")
    snapshot = metrics.snapshot()
    assert snapshot["requests_started"] == 2
    assert snapshot["requests_completed"] == 2
    assert snapshot["errors"] == 1
    assert snapshot["average_latency_seconds"] >= 0


def test_circuit_breaker_opens_and_recovers():
    breaker = CircuitBreaker(failure_threshold=2, recovery_seconds=10)
    assert breaker.allow(now=0)
    breaker.record_failure(now=0)
    assert breaker.allow(now=1)
    breaker.record_failure(now=1)
    assert breaker.state == "open"
    assert not breaker.allow(now=5)
    assert breaker.allow(now=11)
    assert breaker.state == "closed"


def test_api_readiness_is_safe_without_secret(monkeypatch):
    monkeypatch.delenv("P8_API_KEY", raising=False)
    from fastapi.testclient import TestClient
    import api

    response = TestClient(api.app).get("/ready")
    assert response.status_code == 503
    assert response.json()["detail"] == "Service is not ready."


def test_dockerfile_uses_non_root_user_and_healthcheck():
    with open("Dockerfile", encoding="utf-8") as handle:
        dockerfile = handle.read()
    assert "USER appuser" in dockerfile
    assert "HEALTHCHECK" in dockerfile
    assert '"--host", "0.0.0.0"' in dockerfile
