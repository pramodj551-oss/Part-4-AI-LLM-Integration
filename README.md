# Incident Knowledge Assistant (RAG)

**Capstone Project — Part 4: AI / LLM Integration**

An educational Retrieval-Augmented Generation (RAG) prototype that combines Sentence Transformers, FAISS, a Groq-hosted LLM, and Streamlit to answer questions from an incident knowledge base.

## Architecture

```text
User Question
    ↓
SentenceTransformer Embedding
    ↓
FAISS Similarity Search
    ↓
Relevance Guardrail
    ↓
Retrieved Incident Context
    ↓
Bounded Session Conversation Memory
    ↓
Prompt-Grounded Groq LLM
    ↓
Output Safety Guardrail
    ↓
Streamlit UI
```

Retrieved documents are the authoritative source for answers. Previous conversation is session-scoped, bounded, and treated only as untrusted reference material for conversational follow-ups.

## P7 — RAG Quality & Guardrails

P7 adds deterministic safeguards around retrieval and generated output:

- FAISS results are filtered by a configurable maximum L2 distance (`MAX_RETRIEVAL_DISTANCE = 1.50`).
- If no result passes the relevance gate, the LLM is not given an empty knowledge context by the pipeline and the application uses its safe no-information path.
- Generated answers are bounded to the configured response length.
- Empty model output is converted to a stable knowledge-base refusal message.
- Common prompt/system-instruction and secret-disclosure patterns in model output are replaced with the same safe refusal.
- Prompt-override attempts are detected using privacy-safe query fingerprints rather than raw query logging.
- Deterministic P7 tests cover relevance filtering, output bounds, refusal behavior, and disclosure detection.

These controls reduce low-relevance retrieval, prompt disclosure, and unsafe-output failure modes without treating heuristics as a substitute for full security testing.

## P6 — Session Document Upload

P6 adds a secure, ephemeral upload path for **TXT, MD and CSV** documents:

- Maximum 5 uploaded files per indexing operation.
- Maximum 1 MB per file.
- UTF-8 validation and bounded text extraction.
- Uploaded documents are indexed only in the current Streamlit session.
- The persistent FAISS index and `vector_store/documents.json` are never modified by UI uploads.
- Uploaded content is not written to application telemetry.
- Removing uploaded documents returns retrieval to the persistent knowledge base.

This design avoids cross-session mutation of the shared cached production pipeline and keeps user-uploaded knowledge isolated.

## Technology Stack

| Category | Technology |
|---|---|
| Language | Python 3.11+ |
| UI | Streamlit |
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

## Knowledge Base

The application expects the incident dataset at `data/incidents.csv`. The persisted document store is JSON (`vector_store/documents.json`) and is intentionally not loaded with Python pickle deserialization. Build or synchronize the FAISS index and JSON document store before using the application.

## Run

```bash
streamlit run app.py
```

## Test

```bash
pytest -q
```

P0–P7 regression tests cover configuration consistency, safe persistence, input/security validation, retrieval evaluation, privacy-safe telemetry, LLM resilience, runtime readiness, conversation memory, bounded document upload parsing, relevance filtering, and generated-output safety.

## Security Notes

- Secrets are supplied through Streamlit Secrets rather than source code.
- The document store uses JSON instead of executable Python pickle deserialization.
- Vector-store loading validates that FAISS and JSON document counts match.
- Query content is excluded from telemetry logs; only a non-reversible fingerprint is recorded.
- Conversation memory is session-scoped, bounded, non-persistent, and untrusted.
- UI uploads are size/type/encoding validated and remain ephemeral to the active session.
- Retrieval relevance and generated-output guardrails are deterministic, bounded, and covered by regression tests.
- This repository is a prototype and should not be described as production-ready without additional authentication, authorization, rate limiting, deployment hardening, and security testing.

## Project Status

**Current version:** 1.3.0  
**Status:** RAG prototype under security, correctness, evaluation, observability, resilience, session-memory, document-ingestion, and quality-guardrail hardening  
**LLM provider:** Groq  
**Vector search:** FAISS

## Author

**Pramod Prakash Jadhav**  
Security Data Analyst | AI/ML Developer | SOC Automation Specialist

GitHub: `pramodj551-oss`

## License

MIT License.
