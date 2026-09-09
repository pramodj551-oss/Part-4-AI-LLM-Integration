# H2.1 Memory Optimization

This change reduces the dedicated FastAPI container footprint without removing the RAG/FAISS query path.

## Changes

- Use a dedicated `requirements-api.txt` for the FastAPI production image so Streamlit/UI-only packages are not installed in the API container.
- Lazy-load the RAG pipeline only when `/v1/query` is used; `/health` and `/ready` do not instantiate the embedding stack.
- Reuse the `SentenceTransformer` instance inside `Retriever` during index construction instead of creating a second embedding model.
- Keep the existing embedding model, FAISS, Torch, and Transformers dependencies because they are required by the RAG path.
- Remove the Streamlit dependency from the LLM runtime module and read `GROQ_API_KEY` directly from the environment.

## Validation

- GitHub Actions runs 34340747754, 34340760380, and 34340778971 are GREEN.
- Latest run 34340778971 is for commit `365c46397468d8f6e61475f3a114a8bf31452912`.

## Runtime gate

The Render 512 MiB OOM has **not** been claimed as fixed by CI alone. A successful Render deployment and runtime smoke test remain required before merge.
