"""Production resilience helpers for the Groq-backed LLM client."""

import time


class LLMResponseError(RuntimeError):
    """Raised when an LLM response violates the output contract."""


def validate_llm_response(response, max_length):
    """Validate a provider response without exposing provider internals."""
    try:
        choices = response.choices
        if not choices:
            raise LLMResponseError("The language model returned no choices.")
        answer = choices[0].message.content
    except (AttributeError, IndexError, TypeError) as exc:
        raise LLMResponseError("The language model returned an invalid response.") from exc

    if not isinstance(answer, str) or not answer.strip():
        raise LLMResponseError("The language model returned an empty response.")
    answer = answer.strip()
    if len(answer) > max_length:
        raise LLMResponseError("The language model response exceeded the allowed size.")
    return answer


def retry_delay(attempt, base_delay, max_delay):
    """Return bounded exponential backoff delay for a retry attempt."""
    if attempt < 1:
        raise ValueError("attempt must be >= 1")
    return min(max_delay, base_delay * (2 ** (attempt - 1)))


def sleep_before_retry(attempt, base_delay, max_delay, sleep=time.sleep):
    """Sleep using bounded exponential backoff; injectable for deterministic tests."""
    delay = retry_delay(attempt, base_delay, max_delay)
    sleep(delay)
    return delay
