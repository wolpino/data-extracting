"""In-process extract rate limiting (PR9). Per-instance only — not shared across Render replicas."""

from __future__ import annotations

import time
from collections import defaultdict, deque
from threading import Lock

from fastapi import Depends, HTTPException, Request, status

from data_extracting_backend.config import Settings, get_settings

_WINDOW_SECONDS = 60.0


class ExtractRateLimiter:
    """Sliding-window counter keyed by client IP (or later API-key id)."""

    def __init__(self) -> None:
        self._hits: dict[str, deque[float]] = defaultdict(deque)
        self._lock = Lock()

    def reset(self) -> None:
        """Clear all buckets — used by tests so cases do not bleed across."""
        with self._lock:
            self._hits.clear()

    def check(self, key: str, limit: int, window_seconds: float = _WINDOW_SECONDS) -> tuple[bool, int]:
        """Return (allowed, retry_after_seconds). Records a hit when allowed."""
        now = time.monotonic()
        with self._lock:
            bucket = self._hits[key]
            cutoff = now - window_seconds
            while bucket and bucket[0] <= cutoff:
                bucket.popleft()
            if len(bucket) >= limit:
                retry_after = max(1, int(bucket[0] + window_seconds - now) + 1)
                return False, retry_after
            bucket.append(now)
            return True, 0


# Process-wide store: fine for single Render free-tier instance; not multi-instance safe.
extract_limiter = ExtractRateLimiter()


def enforce_extract_rate_limit(
    request: Request,
    settings: Settings = Depends(get_settings),
) -> None:
    """Reject over-quota extract calls before reading the upload / calling Gemini."""
    if not settings.extract_rate_limit_enabled:
        return
    limit = settings.extract_rate_limit_per_minute
    if limit <= 0:
        return
    # IP-only for now; API-key scoping can layer on later without changing this call site.
    host = request.client.host if request.client else "unknown"
    allowed, retry_after = extract_limiter.check(host, limit)
    if allowed:
        return
    raise HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail={
            "error": "rate_limit_exceeded",
            "message": (
                f"Too many extract requests from this client "
                f"(limit {limit} per minute). Try again later."
            ),
        },
        headers={"Retry-After": str(retry_after)},
    )
