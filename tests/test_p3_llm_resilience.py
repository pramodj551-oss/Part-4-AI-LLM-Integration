"""P3 production LLM resilience regression tests."""

from types import SimpleNamespace

import pytest

from src.llm_resilience import LLMResponseError, retry_delay, validate_llm_response


def response_with(content):
    return SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content=content))]
    )


def test_valid_response_is_trimmed_and_bounded():
    assert validate_llm_response(response_with("  safe answer  "), 100) == "safe answer"


def test_empty_or_missing_response_is_rejected():
    with pytest.raises(LLMResponseError):
        validate_llm_response(response_with("   "), 100)
    with pytest.raises(LLMResponseError):
        validate_llm_response(SimpleNamespace(choices=[]), 100)


def test_oversized_response_is_rejected():
    with pytest.raises(LLMResponseError):
        validate_llm_response(response_with("x" * 101), 100)


def test_retry_backoff_is_bounded():
    assert retry_delay(1, 1.0, 8.0) == 1.0
    assert retry_delay(2, 1.0, 8.0) == 2.0
    assert retry_delay(4, 1.0, 8.0) == 8.0
    assert retry_delay(10, 1.0, 8.0) == 8.0

    with pytest.raises(ValueError):
        retry_delay(0, 1.0, 8.0)
