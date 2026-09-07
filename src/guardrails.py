"""Deterministic guardrails for safe RAG answer handling."""

import re

from src.config import MAX_RESPONSE_LENGTH

_REFUSAL = "I could not find that information in the knowledge base."
_SENSITIVE_PATTERNS = (
    re.compile(r"\b(system prompt|developer message|hidden instructions?)\b", re.IGNORECASE),
    re.compile(r"\b(api key|secret|access token|password)\b", re.IGNORECASE),
)


def validate_generated_answer(answer: str) -> str:
    """Normalize an LLM answer and reject empty/oversized output."""
    if not isinstance(answer, str):
        raise TypeError("Generated answer must be a string.")
    normalized = answer.strip()
    if not normalized:
        return _REFUSAL
    if len(normalized) > MAX_RESPONSE_LENGTH:
        return normalized[:MAX_RESPONSE_LENGTH].rstrip() + "…"
    return normalized


def contains_sensitive_disclosure(answer: str) -> bool:
    """Detect common secret/prompt-disclosure patterns in generated text."""
    if not isinstance(answer, str):
        return False
    return any(pattern.search(answer) for pattern in _SENSITIVE_PATTERNS)


def apply_answer_guardrail(answer: str) -> str:
    """Return a safe user-facing answer without exposing internal instructions."""
    normalized = validate_generated_answer(answer)
    if contains_sensitive_disclosure(normalized):
        return _REFUSAL
    return normalized
