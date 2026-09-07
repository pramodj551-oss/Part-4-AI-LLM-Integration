"""P8 authenticated API facade for the production RAG pipeline."""

import uuid

from fastapi import Depends, FastAPI, Header, HTTPException, Request, status
from pydantic import BaseModel, Field

from src.api_security import AuthenticationError, AuthorizationError, RateLimiter, authenticate, authorize, credential_fingerprint
from src.config import APPLICATION_VERSION
from src.logger import get_logger
from src.rag_pipeline import RAGPipeline
from src.security import validate_query, validate_top_k

logger = get_logger()
app = FastAPI(title="Incident Knowledge Assistant API", version=APPLICATION_VERSION)
limiter = RateLimiter()
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
    global _pipeline
    if _pipeline is None:
        _pipeline = RAGPipeline()
    return _pipeline


def require_api_key(x_api_key: str | None = Header(default=None)):
    try:
        role = authenticate(x_api_key or "")
        return role, x_api_key or ""
    except AuthenticationError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc), headers={"WWW-Authenticate": "ApiKey"}) from None


@app.get("/health")
def health():
    return {"status": "healthy", "version": APPLICATION_VERSION}


@app.get("/v1/info")
def info(auth=Depends(require_api_key)):
    role, _ = auth
    return {"service": "incident-knowledge-assistant", "version": APPLICATION_VERSION, "role": role}


@app.get("/v1/admin/info")
def admin_info(auth=Depends(require_api_key)):
    role, _ = auth
    try:
        authorize(role, "admin")
    except AuthorizationError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from None
    return {"service": "incident-knowledge-assistant", "version": APPLICATION_VERSION, "security": "admin"}


@app.post("/v1/query", response_model=QueryResponse)
def query(payload: QueryRequest, request: Request, auth=Depends(require_api_key)):
    role, api_key = auth
    client_id = request.client.host if request.client else "unknown"
    if not limiter.allow(client_id):
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Rate limit exceeded. Please retry later.")

    request_id = str(uuid.uuid4())
    fingerprint = credential_fingerprint(api_key)
    logger.info("API request accepted request_id=%s role=%s credential=%s", request_id, role, fingerprint)
    try:
        question = validate_query(payload.question)
        top_k = validate_top_k(payload.top_k)
        result = get_pipeline().ask(question=question, top_k=top_k, conversation_history=payload.conversation_history)
        return QueryResponse(question=result["question"], answer=result["answer"], document_count=result["document_count"], request_id=request_id)
    except (TypeError, ValueError) as exc:
        logger.warning("API validation rejected request_id=%s error_type=%s", request_id, type(exc).__name__)
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid request payload.") from None
    except Exception:
        logger.exception("API request failed request_id=%s", request_id)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unable to process the request.") from None
