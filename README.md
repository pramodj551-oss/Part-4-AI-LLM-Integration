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
Prompt-Grounded Groq LLM
    ↓
Streamlit UI
```

Retrieved documents are supplied as context to the LLM. The application instructs the model to avoid answers that are not supported by the supplied context.

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
│   ├── Incident_Search.py
│   ├── Knowledge_Base.py
│   └── Analytics.py
├── src/
│   ├── config.py
│   ├── logger.py
│   ├── data_loader.py
│   ├── embeddings.py
│   ├── vector_store.py
│   ├── retriever.py
│   └── llm.py
└── tests/
    └── test_p0_hardening.py
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

## Run

```bash
streamlit run app.py
```

## Test

```bash
pytest -q
```

The P0 tests verify configuration consistency and safe JSON vector-store persistence, including index/document count validation and document type validation.

## Security Notes

- Secrets are supplied through Streamlit Secrets rather than source code.
- The document store uses JSON instead of executable Python pickle deserialization.
- Vector-store loading validates that the FAISS vector count matches the JSON document count.
- User-controlled document types are validated before indexing.
- This repository is a prototype and should not be described as production-ready without additional authentication, authorization, rate limiting, RAG evaluation, deployment hardening, and security testing.

## Project Status

**Current version:** 1.0.1  
**Status:** RAG prototype under security and correctness hardening  
**LLM provider:** Groq  
**Vector search:** FAISS

## Author

**Pramod Prakash Jadhav**  
Security Data Analyst | AI/ML Developer | SOC Automation Specialist

GitHub: `pramodj551-oss`

## License

MIT License.
