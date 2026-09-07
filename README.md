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
Retrieved Incident Context
    ↓
Bounded Session Conversation Memory
    ↓
Prompt-Grounded Groq LLM
    ↓
Streamlit UI
```

Retrieved documents are the authoritative source for answers. Previous conversation is session-scoped, bounded, and treated only as untrusted reference material for conversational follow-ups.

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

P5 adds `src/conversation_memory.py` with a bounded, in-memory conversation store:

- Maximum 5 turns per Streamlit session by default.
- Individual question/answer fields are bounded to 2,000 characters.
- Memory is stored in `st.session_state`; it is not persisted to disk or telemetry.
- `Clear Chat` clears both the displayed history and the memory used for follow-up prompts.
- Previous conversation is explicitly marked untrusted and cannot override system instructions or retrieved knowledge-base context.
- No conversation content is written to application logs by the memory component.

## Project Structure

```text
.
├── app.py
├── requirements.txt
├── README.md
├── data/
│   └── incidents.csv
├── vector_store/
│   ├── faiss.index
│   └── documents.json
├── pages/
├── src/
│   ├── config.py
│   ├── conversation_memory.py
│   ├── logger.py
│   ├── data_loader.py
│   ├── embeddings.py
│   ├── vector_store.py
│   ├── retriever.py
│   ├── evaluation.py
│   ├── observability.py
│   └── llm.py
└── tests/
    ├── test_p0_hardening.py
    ├── test_p1_security.py
    ├── test_p2_evaluation_observability.py
    ├── test_p3_llm_resilience.py
    ├── test_p4_runtime.py
    └── test_p5_conversation_memory.py
```

## Installation

```bash
python -m venv .venv
```

Activate the environment, then:

```bash
pip install -r requirements.txt
```

The LLM integration requires a `GROQ_API_KEY` configured through Streamlit Secrets. **Do not commit API keys or `.env` files containing secrets.**

## Knowledge Base

The application expects the incident dataset at:

```text
data/incidents.csv
```

The persisted document store is JSON (`vector_store/documents.json`). It contains only document strings and is intentionally not loaded with Python pickle deserialization.

Build or synchronize the FAISS index and JSON document store before using the application.

## RAG Evaluation

P2 adds deterministic, provider-independent evaluation helpers in `src/evaluation.py`:

- Hit Rate@K
- Precision@K
- Recall@K
- Mean Reciprocal Rank (MRR)
- Lexical grounding score for answer/context support

These metrics operate on retrieval results and do not require a live Groq call, making regression tests deterministic and CI-safe.

## Observability

`src/observability.py` provides privacy-safe in-process telemetry for retrieval and generation. Counters cover retrieval volume, empty retrievals, retrieved document volume, generation errors, and grounding outcomes. Query content is never stored; retrieval logs use a short SHA-256 fingerprint.

## Run

```bash
streamlit run app.py
```

## Test

```bash
pytest -q
```

P0–P5 regression tests cover configuration consistency, safe vector-store persistence, input/security validation, retrieval evaluation metrics, grounding behavior, privacy-safe telemetry, LLM resilience, runtime readiness, and bounded session conversation memory.

## Security Notes

- Secrets are supplied through Streamlit Secrets rather than source code.
- The document store uses JSON instead of executable Python pickle deserialization.
- Vector-store loading validates that the FAISS vector count matches the JSON document count.
- User-controlled document types are validated before indexing.
- Query content is excluded from telemetry logs; only a non-reversible fingerprint is recorded.
- Conversation memory is session-scoped, bounded, non-persistent, and treated as untrusted reference material.
- This repository is a prototype and should not be described as production-ready without additional authentication, authorization, rate limiting, deployment hardening, and security testing.

## Project Status

**Current version:** 1.1.0  
**Status:** RAG prototype under security, correctness, evaluation, observability, resilience, and session-memory hardening  
**LLM provider:** Groq  
**Vector search:** FAISS

## Author

**Pramod Prakash Jadhav**  
Security Data Analyst | AI/ML Developer | SOC Automation Specialist

GitHub: `pramodj551-oss`

## License

MIT License.
