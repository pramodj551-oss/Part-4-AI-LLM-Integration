# Incident Knowledge Assistant (RAG)

**Capstone Project — Part 4: AI / LLM Integration**

An educational Retrieval-Augmented Generation (RAG) prototype that combines Sentence Transformers, FAISS, a Groq-hosted LLM, and Streamlit to answer questions from an incident knowledge base.

## Architecture

```text
Client
    ↓
API Authentication / Authorization
    ↓
Rate Limiter
    ↓
Request Validation
    ↓
RAG Pipeline
    ↓
FAISS Similarity Search
    ↓
Relevance Guardrail
    ↓
Bounded Session Conversation Memory
    ↓
Prompt-Grounded Groq LLM
    ↓
Output Safety Guardrail
    ↓
Secure API Response / Streamlit UI
    ↓
Operational Metrics / Health Probes
```

Retrieved documents are the authoritative source for answers. Previous conversation is session-scoped, bounded, and treated only as untrusted reference material for conversational follow-ups.

## P9 — Production Deployment & Operational Resilience

P9 adds deployment and runtime safeguards for the FastAPI service:

- Hardened Python 3.11 slim container with a dedicated non-root `appuser`.
- Docker `HEALTHCHECK` probes the public `/health` endpoint.
- `/ready` provides a stable readiness response and returns HTTP 503 when required deployment configuration is absent.
- `/metrics` exposes process-local request count, error count and average latency without request payloads.
- Thread-safe request metrics cover completed API calls and failures.
- A deterministic circuit-breaker primitive supports bounded downstream-failure handling and recovery.
- `.dockerignore` excludes Git metadata, virtual environments, environment files and runtime logs from the build context.
- Runtime configuration continues to come from deployment environment/secrets; no API credentials are stored in source.

The metrics and circuit breaker are intentionally process-local. Multi-worker or distributed deployments should use shared observability and coordination infrastructure where required.

### Production API Container

```bash
docker build -t incident-knowledge-assistant:1.5.0 .
docker run --rm -p 8000:8000 \
  -e P8_API_KEY='<configured-key>' \
  -e GROQ_API_KEY='<configured-groq-key>' \
  incident-knowledge-assistant:1.5.0
```

Never commit real credentials or `.env` files. Use the deployment platform's secret manager/environment configuration.

## P8 — Secure API & Access Control

P8 adds an authenticated FastAPI facade for controlled programmatic access to the RAG pipeline:

- `GET /health` is a minimal public health endpoint.
- `GET /ready` is a deployment readiness probe.
- `GET /metrics` returns privacy-safe process-local operational counters.
- `GET /v1/info` requires a valid `X-API-Key` credential.
- `GET /v1/admin/info` requires the admin credential.
- `POST /v1/query` requires authentication, validates question/top-k/history bounds, and returns a request ID.
- Credentials are read from `P8_API_KEY` and `P8_ADMIN_API_KEY`; secrets are never embedded in source code.
- API-key comparison uses constant-time `hmac.compare_digest`.
- Requests are rate limited per client using a process-local bounded window.
- Raw questions and credentials are excluded from API audit logs; only role and a short credential fingerprint are recorded.
- Authentication, authorization, validation, rate-limit and server errors use stable responses without internal exception details.

The built-in rate limiter is intentionally process-local. Distributed deployments should use a shared rate-limit store such as Redis.

## P7 — RAG Quality & Guardrails

P7 adds deterministic safeguards around retrieval and generated output:

- FAISS results are filtered by a configurable maximum L2 distance (`MAX_RETRIEVAL_DISTANCE = 1.50`).
- Generated answers are bounded to the configured response length.
- Empty model output is converted to a stable knowledge-base refusal message.
- Common prompt/system-instruction and secret-disclosure patterns in model output are replaced with the same safe refusal.
- Prompt-override attempts are detected using privacy-safe query fingerprints rather than raw query logging.
- Deterministic P7 tests cover relevance filtering, output bounds, refusal behavior, and disclosure detection.

## P6 — Session Document Upload

P6 adds a secure, ephemeral upload path for **TXT, MD and CSV** documents:

- Maximum 5 uploaded files per indexing operation.
- Maximum 1 MB per file.
- UTF-8 validation and bounded text extraction.
- Uploaded documents are indexed only in the current Streamlit session.
- The persistent FAISS index and `vector_store/documents.json` are never modified by UI uploads.
- Uploaded content is not written to application telemetry.
- Removing uploaded documents returns retrieval to the persistent knowledge base.

## Technology Stack

| Category | Technology |
|---|---|
| Language | Python 3.11+ |
| UI | Streamlit |
| API | FastAPI + Uvicorn |
| Embeddings | Sentence Transformers (`all-MiniLM-L6-v2`) |
| Vector Search | FAISS (`IndexFlatL2`) |
| LLM Provider | Groq API |
| LLM Model | `llama-3.1-8b-instant` |
| Data | Pandas / NumPy |
| Visualization | Plotly |
| Testing | pytest |

## Conversation Memory

P5 adds bounded, in-memory conversation context for Streamlit sessions. Maximum 5 turns are retained by default, individual question/answer fields are bounded to 2,000 characters, and previous conversation is explicitly treated as untrusted reference material.

## Installation

```bash
python -m venv .venv
pip install -r requirements.txt
```

The LLM integration requires a `GROQ_API_KEY` configured through Streamlit Secrets or deployment secrets. **Do not commit API keys or `.env` files containing secrets.**

For the API, configure `P8_API_KEY` and optionally `P8_ADMIN_API_KEY` as deployment secrets.

## Knowledge Base

The application expects the incident dataset at `data/incidents.csv`. The persisted document store is JSON (`vector_store/documents.json`) and is intentionally not loaded with Python pickle deserialization. Build or synchronize the FAISS index and JSON document store before using the application.

## Run

```bash
streamlit run app.py
```

For the API:

```bash
uvicorn api:app --host 0.0.0.0 --port 8000
```

## Test

```bash
pytest -q
```

P0–P9 regression tests cover configuration consistency, safe persistence, input/security validation, retrieval evaluation, privacy-safe telemetry, LLM resilience, runtime readiness, conversation memory, bounded document upload parsing, relevance filtering, generated-output safety, API authentication, authorization, rate limiting, secure error handling, deployment health probes, metrics and circuit-breaker behavior.

## Security Notes

- Secrets are supplied through Streamlit Secrets or deployment environment configuration rather than source code.
- The document store uses JSON instead of executable Python pickle deserialization.
- Vector-store loading validates that FAISS and JSON document counts match.
- Query content is excluded from telemetry logs; only a non-reversible fingerprint is recorded.
- Conversation memory is session-scoped, bounded, non-persistent, and untrusted.
- UI uploads are size/type/encoding validated and remain ephemeral to the active session.
- Retrieval relevance and generated-output guardrails are deterministic, bounded, and covered by regression tests.
- API authentication uses constant-time API-key comparison and role-based endpoint authorization.
- API rate limiting is process-local and should be replaced with shared infrastructure for multi-worker deployments.
- API logs contain no raw questions or API credentials.
- Production containers run as a non-root user and exclude local secrets/runtime logs from the Docker build context.

## Project Status

**Current version:** 1.5.0  
**Status:** RAG prototype under security, correctness, evaluation, observability, resilience, session-memory, document-ingestion, quality-guardrail, API-access, and production-deployment hardening  
**LLM provider:** Groq  
**Vector search:** FAISS

## Author

**Pramod Prakash Jadhav**  
Security Data Analyst | AI/ML Developer | SOC Automation Specialist

GitHub: `pramodj551-oss`

## License

MIT License.
