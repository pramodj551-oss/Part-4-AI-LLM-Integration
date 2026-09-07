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
```

Retrieved documents are the authoritative source for answers. Previous conversation is session-scoped, bounded, and treated only as untrusted reference material for conversational follow-ups.

## P8 — Secure API & Access Control

P8 adds an authenticated FastAPI facade for controlled programmatic access to the RAG pipeline:

- `GET /health` is a minimal public health endpoint.
- `GET /v1/info` requires a valid `X-API-Key` credential.
- `GET /v1/admin/info` requires the admin credential.
- `POST /v1/query` requires authentication, validates question/top-k/history bounds, and returns a request ID.
- Credentials are read from `P8_API_KEY` and `P8_ADMIN_API_KEY`; secrets are never embedded in source code.
- API-key comparison uses constant-time `hmac.compare_digest`.
- Requests are rate limited per client using a process-local bounded window.
- Raw questions and credentials are excluded from API audit logs; only role and a short credential fingerprint are recorded.
- Authentication, authorization, validation, rate-limit and server errors use stable responses without internal exception details.

The built-in rate limiter is intentionally process-local. Distributed deployments should use a shared rate-limit store such as Redis.

### API Run

```bash
uvicorn api:app --host 0.0.0.0 --port 8000
```

Example authenticated request:

```bash
curl -X POST http://localhost:8000/v1/query \
  -H 'Content-Type: application/json' \
  -H 'X-API-Key: <configured-key>' \
  -d '{"question":"What happened in the incident?","top_k":5}'
```

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

The LLM integration requires a `GROQ_API_KEY` configured through Streamlit Secrets. **Do not commit API keys or `.env` files containing secrets.**

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

P0–P8 regression tests cover configuration consistency, safe persistence, input/security validation, retrieval evaluation, privacy-safe telemetry, LLM resilience, runtime readiness, conversation memory, bounded document upload parsing, relevance filtering, generated-output safety, API authentication, authorization, rate limiting, and secure error handling.

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

## Project Status

**Current version:** 1.4.0  
**Status:** RAG prototype under security, correctness, evaluation, observability, resilience, session-memory, document-ingestion, quality-guardrail, and API-access hardening  
**LLM provider:** Groq  
**Vector search:** FAISS

## Author

**Pramod Prakash Jadhav**  
Security Data Analyst | AI/ML Developer | SOC Automation Specialist

GitHub: `pramodj551-oss`

## License

MIT License.
