"""P8 API authentication, authorization and in-memory rate limiting."""

import hashlib
import hmac
import os
import threading
import time
from collections import defaultdict, deque

from src.security import redact_secret

RATE_LIMIT_REQUESTS = int(os.getenv("P8_RATE_LIMIT_REQUESTS", "30"))
RATE_LIMIT_WINDOW_SECONDS = int(os.getenv("P8_RATE_LIMIT_WINDOW_SECONDS", "60"))


class AuthenticationError(Exception):
    """Raised when an API credential is missing or invalid."""


class AuthorizationError(Exception):
    """Raised when a credential lacks the requested role."""


def _configured_keys():
    user_key = os.getenv("P8_API_KEY", "").strip()
    admin_key = os.getenv("P8_ADMIN_API_KEY", "").strip()
    return user_key, admin_key


def authenticate(api_key: str):
    """Authenticate an API key without leaking the configured secret."""
    if not isinstance(api_key, str) or not api_key:
        raise AuthenticationError("Authentication required.")
    user_key, admin_key = _configured_keys()
    if admin_key and hmac.compare_digest(api_key, admin_key):
        return "admin"
    if user_key and hmac.compare_digest(api_key, user_key):
        return "user"
    raise AuthenticationError("Invalid authentication credentials.")


def authorize(role: str, required_role: str = "user"):
    """Enforce the minimal role required by an endpoint."""
    if required_role == "admin" and role != "admin":
        raise AuthorizationError("Insufficient permissions.")
    return True


class RateLimiter:
    """Small process-local fixed-window limiter suitable for a single API worker."""

    def __init__(self, max_requests=RATE_LIMIT_REQUESTS, window_seconds=RATE_LIMIT_WINDOW_SECONDS):
        if max_requests < 1 or window_seconds < 1:
            raise ValueError("Rate-limit settings must be positive.")
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._events = defaultdict(deque)
        self._lock = threading.Lock()

    def allow(self, client_id: str, now=None):
        """Return whether this client is within its request budget."""
        now = time.monotonic() if now is None else now
        cutoff = now - self.window_seconds
        with self._lock:
            events = self._events[client_id]
            while events and events[0] <= cutoff:
                events.popleft()
            if len(events) >= self.max_requests:
                return False
            events.append(now)
            return True

    def reset(self):
        with self._lock:
            self._events.clear()


def credential_fingerprint(api_key: str):
    """Return a short non-reversible credential identifier for audit logs."""
    return hashlib.sha256(api_key.encode("utf-8")).hexdigest()[:16]


def safe_credential_for_log(api_key: str):
    """Redact credentials before diagnostic output."""
    return redact_secret(api_key)
