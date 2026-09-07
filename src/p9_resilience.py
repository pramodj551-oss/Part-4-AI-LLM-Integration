"""P9 production resilience primitives: readiness, metrics and bounded execution."""

import threading
import time
from collections import defaultdict
from contextlib import contextmanager


class RequestMetrics:
    """Thread-safe process-local counters suitable for a single API worker."""

    def __init__(self):
        self._lock = threading.Lock()
        self._started = 0
        self._completed = 0
        self._errors = 0
        self._latency_total = 0.0

    def record(self, latency_seconds: float, error: bool = False):
        with self._lock:
            self._started += 1
            self._completed += 1
            self._latency_total += max(0.0, float(latency_seconds))
            if error:
                self._errors += 1

    def snapshot(self):
        with self._lock:
            avg = self._latency_total / self._completed if self._completed else 0.0
            return {
                "requests_started": self._started,
                "requests_completed": self._completed,
                "errors": self._errors,
                "average_latency_seconds": round(avg, 6),
            }

    def reset(self):
        with self._lock:
            self._started = self._completed = self._errors = 0
            self._latency_total = 0.0


class CircuitBreaker:
    """Small deterministic circuit breaker for repeated downstream failures."""

    CLOSED = "closed"
    OPEN = "open"

    def __init__(self, failure_threshold=3, recovery_seconds=30):
        if failure_threshold < 1 or recovery_seconds < 1:
            raise ValueError("Circuit-breaker settings must be positive.")
        self.failure_threshold = failure_threshold
        self.recovery_seconds = recovery_seconds
        self.failures = 0
        self.opened_at = None
        self._lock = threading.Lock()

    def allow(self, now=None):
        now = time.monotonic() if now is None else now
        with self._lock:
            if self.opened_at is None:
                return True
            if now - self.opened_at >= self.recovery_seconds:
                self.opened_at = None
                self.failures = 0
                return True
            return False

    def record_success(self):
        with self._lock:
            self.failures = 0
            self.opened_at = None

    def record_failure(self, now=None):
        now = time.monotonic() if now is None else now
        with self._lock:
            self.failures += 1
            if self.failures >= self.failure_threshold:
                self.opened_at = now

    @property
    def state(self):
        return self.OPEN if self.opened_at is not None else self.CLOSED


@contextmanager
def timed_request(metrics: RequestMetrics):
    """Record latency and propagate exceptions without leaking internals."""
    started = time.monotonic()
    error = False
    try:
        yield
    except Exception:
        error = True
        raise
    finally:
        metrics.record(time.monotonic() - started, error=error)
