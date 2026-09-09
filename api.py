"""P9 production API facade with secure access and operational controls."""

import uuid

from fastapi import Depends, FastAPI, Header, HTTPException, Request, status
from pydantic import BaseModel, Field

from src.api_security import AuthenticationError, AuthorizationError, RateLimiter, authenticate, authorize, credential_fingerprint
from src.config import APPLICATION_VERSION
from src.logger import get_logger
from src.p9_resilience import RequestMetrics, timed_request
from src.security import validate_query, validate_top_k

logger = get_logger()
app = FastAPI(title="Incident Knowledge Assistant API", version=APPLICATION_VERSION)
limiter = RateLimiter()
metrics = RequestMetrics()
_pipeline = None


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)
    top_k: int = Field(default=5, ge=1, le=10)
    conversation_history: str | None = Field(default=None, max_length=20000)


class QueryResponse(BaseModel):
    question: str
    answer: str
    document_count: int
    request_id: str


def get_pipeline():
    """Lazy-load the heavyweight RAG stack only when a query actually needs it."""
    global _pipeline
    if _pipeline is None:
        from src.rag_pipeline import RAGPipeline
        _pipeline = RAGPipeline()
    return _pipeline


def require_api_key(x_api_key: str | None = Header(default=None)):
    try:
        role = authenticate(x_api_key or "")
        return role, x_api_key or ""
    except AuthenticationError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required.", headers={"WWW-Authenticate": "ApiKey"}) from None


@app.get("/health")
def health():
    return {"status": "healthy", "version": APPLICATION_VERSION}


@app.get("/ready")
def ready():
    """Liveness/readiness probe that avoids loading the expensive pipeline."""
    try:
        required = ("P8_API_KEY",)
        import os
        configured = all(bool(os.getenv(name, "").strip()) for name in required)
        if not configured:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Service is not ready.")
        return {"status": "ready", "version": APPLICATION_VERSION}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Service is not ready.") from None


@app.get("/metrics")
def service_metrics():
    return metrics.snapshot()


@app.get("/v1/info")
def info(auth=Depends(require_api_key)):
    role, _ = auth
    return {"service": "incident-knowledge-assistant", "version": APPLICATION_VERSION, "role": role}
