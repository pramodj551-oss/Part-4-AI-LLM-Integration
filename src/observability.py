"""Privacy-safe in-process telemetry for RAG operations."""

from collections import Counter
from time import perf_counter

from src.logger import get_logger
from src.security import query_fingerprint

logger = get_logger()


class RAGTelemetry:
    """Track bounded RAG counters without storing prompts or answers."""

    def __init__(self):
        self._counters = Counter()

    def record_retrieval(self, query, document_count, latency_ms):
        """Record retrieval outcome using only a query fingerprint."""
        fingerprint = query_fingerprint(query)
        self._counters["retrieval_requests"] += 1
        self._counters["retrieved_documents"] += max(0, int(document_count))
        if document_count == 0:
            self._counters["empty_retrievals"] += 1
        logger.info(
            "RAG retrieval event fingerprint=%s documents=%d latency_ms=%.2f",
            fingerprint,
            int(document_count),
            float(latency_ms),
        )

    def record_generation(self, grounded=None, error=False):
        self._counters["generation_requests"] += 1
        if error:
            self._counters["generation_errors"] += 1
        if grounded is True:
            self._counters["grounded_answers"] += 1
        elif grounded is False:
            self._counters["ungrounded_answers"] += 1

    def snapshot(self):
        return dict(self._counters)

    def timed_retrieval(self):
        """Return a timer context that records elapsed milliseconds."""
        return _Timer()


class _Timer:
    def __enter__(self):
        self.started = perf_counter()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.elapsed_ms = (perf_counter() - self.started) * 1000
        return False
