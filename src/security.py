"""Security helpers for production RAG input and log privacy."""

import hashlib
import re

MAX_QUERY_LENGTH = 2000
MAX_CONTEXT_LENGTH = 12000
MAX_TOP_K = 10


def validate_text(value, field_name, max_length):
    """Validate and normalize externally supplied text."""
    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be a string.")
    value = value.strip()
    if not value:
        raise ValueError(f"{field_name} cannot be empty.")
    if len(value) > max_length:
        raise ValueError(f"{field_name} exceeds the maximum allowed length.")
    if any(ord(char) < 32 and char not in "\n\t\r" for char in value):
        raise ValueError(f"{field_name} contains invalid control characters.")
    return value


def validate_query(query):
    """Validate a user query before embedding or LLM processing."""
    return validate_text(query, "Query", MAX_QUERY_LENGTH)


def validate_context(context):
    """Validate retrieved context before sending it to the LLM."""
    return validate_text(context, "Context", MAX_CONTEXT_LENGTH)


def validate_top_k(top_k):
    """Bound retrieval fan-out to prevent excessive resource use."""
    if not isinstance(top_k, int) or isinstance(top_k, bool):
        raise ValueError("top_k must be a positive integer.")
    if top_k < 1 or top_k > MAX_TOP_K:
        raise ValueError(f"top_k must be between 1 and {MAX_TOP_K}.")
    return top_k


def query_fingerprint(query):
    """Return a non-reversible identifier for privacy-safe query logging."""
    normalized = validate_query(query)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:16]


def redact_secret(value):
    """Return a safe representation for logs and diagnostics."""
    if not value:
        return "<missing>"
    if len(value) <= 8:
        return "<redacted>"
    return f"{value[:4]}...{value[-4:]}"


def contains_prompt_override(text):
    """Detect common instruction-override phrases for telemetry/guardrails."""
    normalized = text.lower()
    patterns = (
        r"ignore\s+(all\s+)?previous\s+instructions",
        r"system\s+prompt",
        r"developer\s+message",
        r"reveal\s+(your|the)\s+(prompt|instructions)",
    )
    return any(re.search(pattern, normalized) for pattern in patterns)
