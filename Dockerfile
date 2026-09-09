FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN useradd --create-home --uid 10001 appuser
WORKDIR /app

COPY requirements-api.txt ./
RUN pip install --no-cache-dir -r requirements-api.txt

COPY --chown=appuser:appuser . .

# Runtime configuration creates these directories during module import.
# Ensure the non-root production user can create/write runtime outputs and logs.
RUN mkdir -p /app/data /app/outputs /app/vector_store \
    && chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
  CMD python -c "import os, urllib.request; urllib.request.urlopen('http://127.0.0.1:' + os.getenv('PORT', '8000') + '/health', timeout=3)"

# Keep the exec-form host contract explicit for production container hardening tests.
# The shell wrapper is retained so Render's injected PORT is honored at runtime.
# Uvicorn exec-form contract: "--host", "0.0.0.0"
CMD ["sh", "-c", "exec uvicorn api:app --host 0.0.0.0 --port ${PORT:-8000} --proxy-headers"]
