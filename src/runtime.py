"""Runtime health/readiness helpers for production-facing application code."""

from dataclasses import dataclass


@dataclass(frozen=True)
class RuntimeStatus:
    """Small, JSON-friendly runtime status contract."""

    status: str
    component: str
    version: str

    def as_dict(self):
        return {
            "status": self.status,
            "component": self.component,
            "version": self.version,
        }


def safe_user_error(message: str = "The request could not be completed.") -> str:
    """Return a stable user-facing error without exposing internal details."""
    return message


def readiness_status(pipeline) -> RuntimeStatus:
    """Report readiness without returning credentials or internal exceptions."""
    try:
        pipeline.health_check()
    except Exception:
        return RuntimeStatus("not_ready", "rag_pipeline", "unknown")
    return RuntimeStatus("ready", "rag_pipeline", "unknown")
