from src.runtime import RuntimeStatus, readiness_status, safe_user_error


class HealthyPipeline:
    def health_check(self):
        return {"status": "healthy"}


class BrokenPipeline:
    def health_check(self):
        raise RuntimeError("secret internal failure")


def test_runtime_status_serializes_cleanly():
    status = RuntimeStatus("ready", "rag_pipeline", "1.0.2")
    assert status.as_dict() == {
        "status": "ready",
        "component": "rag_pipeline",
        "version": "1.0.2",
    }


def test_readiness_returns_ready_for_healthy_pipeline():
    assert readiness_status(HealthyPipeline(), "1.0.2").as_dict() == {
        "status": "ready",
        "component": "rag_pipeline",
        "version": "1.0.2",
    }


def test_readiness_hides_internal_failure_details():
    status = readiness_status(BrokenPipeline(), "1.0.2")
    assert status.status == "not_ready"
    assert status.version == "1.0.2"
    assert "secret internal failure" not in str(status.as_dict())


def test_safe_user_error_is_stable():
    assert safe_user_error() == "The request could not be completed."
    assert safe_user_error("Please try again.") == "Please try again."
