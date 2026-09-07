# Changelog

All notable changes to this project are documented in this file.

The format follows the principles of Keep a Changelog and uses Semantic Versioning.

---

## [1.2.0] - 2026-09-07

### Added

- P6 secure session document upload for TXT, MD and CSV files.
- Bounded upload count, file size and extracted document length.
- UTF-8 and file-type validation.
- Ephemeral session-only FAISS indexing for uploaded documents.
- Persistent knowledge-base files are not modified by UI uploads.
- Deterministic P6 regression tests for upload validation and bounds.

### Security

- Uploaded documents are isolated to the active Streamlit session.
- Uploaded content is not persisted to the repository vector store or telemetry.
- Unsupported extensions, oversized payloads, empty files and invalid UTF-8 are rejected.

---

## [1.1.0] - 2026-09-07

### Added

- Bounded, session-scoped conversation memory for Streamlit.
- Maximum 5 retained conversation turns by default.
- Per-field memory limits to prevent unbounded prompt growth.
- Safe prompt integration where prior conversation is explicitly treated as untrusted reference material.
- Clear Chat now resets both visible history and conversation memory.
- Deterministic P5 regression tests for bounds, truncation, ordering, clearing, and validation.

### Security

- Conversation memory is not persisted to disk.
- Conversation memory is not written to telemetry logs.
- Retrieved knowledge-base context remains authoritative over previous conversation.
- Previous conversation cannot override system instructions.

---

## [1.0.0] - 2026-08-01

### Added

- Initial project structure and Streamlit application.
- Dataset loader, SentenceTransformer embeddings, FAISS vector database, semantic retriever, Groq LLM integration, and RAG orchestration.
- Home, Incident Search, Knowledge Base, and Analytics pages.
- RAG evaluation and privacy-safe observability.
- Security, resilience, runtime readiness, and regression hardening through P0–P4.
