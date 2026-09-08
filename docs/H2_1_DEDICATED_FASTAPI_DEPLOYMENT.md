# H2.1 — Dedicated FastAPI Deployment

## Decision

Use **Render Web Service + Docker** as the dedicated deployment target for the Part-4 FastAPI API.

The repository already contains a production-oriented Dockerfile and `api.py`. Render is used only for the API service; the existing Streamlit deployment remains the UI service.

## Target architecture

```text
GitHub: Part-4
│
├── Streamlit deployment
│   └── app.py → UI
│
└── Render Web Service
    └── Dockerfile → uvicorn api:app
        │
        ├── GET  /health
        ├── GET  /ready
        ├── GET  /metrics
        └── POST /v1/query
```

## Version-controlled deployment contract

`render.yaml` defines:

- Render Web Service type
- Docker runtime
- Singapore region
- Dockerfile/build context
- `/health` HTTP health check
- deploy only after CI checks pass
- non-secret `PORT=10000`
- secret variable names only, with `sync: false`

Render Blueprints are infrastructure-as-code and support Docker services and HTTP health checks. Secret values must not be committed to the Blueprint; Render expects `sync: false` placeholders to be populated outside source control. See the Render documentation for [Web Services](https://render.com/docs/web-services), [Blueprints](https://render.com/docs/infrastructure-as-code), [Health Checks](https://render.com/docs/health-checks), and [Environment Variables and Secrets](https://render.com/docs/configure-environment-variables).

## Runtime configuration

Required runtime secrets:

- `P8_API_KEY` — user API credential; required by `/ready` and `/v1/query`.
- `GROQ_API_KEY` — required by the RAG/LLM pipeline for functional query execution.

Optional privileged credential:

- `P8_ADMIN_API_KEY` — admin credential for `/v1/admin/info`.

No secret values belong in Git, `render.yaml`, Dockerfile, README, CI logs, screenshots, or PR comments.

## Port contract

Render supplies a web-service `PORT`; the container command uses `${PORT:-8000}` so local Docker continues to support port 8000 while Render can use its assigned port. Render web services must bind to `0.0.0.0`.

## Acceptance gates

H2.1 is implementation-complete when:

- `render.yaml` is version-controlled.
- Docker starts `api:app` independently of Streamlit.
- `/health` returns HTTP 2xx.
- `/ready` returns HTTP 200 only when required runtime configuration is present.
- authenticated `POST /v1/query` succeeds against the deployed API.
- `/metrics` is reachable and does not expose secrets or raw query content.
- deployment logs contain no credentials.
- a deployment/release identifier is recorded for the live target.
- rollback target and rollback smoke test are recorded.

Source-code CI success is not treated as live deployment evidence. Live H2 evidence must come from the deployed Render service and be recorded separately in the H2 evidence PR.

## Operational notes

The API rate limiter and metrics are process-local. If the Render service is later scaled to multiple workers/instances, shared infrastructure such as Redis and centralized metrics/tracing should be evaluated.

The Render free web-service plan may spin down after inactivity; this is acceptable for development/demo evidence but should not be treated as a production availability SLO.
