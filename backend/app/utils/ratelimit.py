"""
Lightweight in-memory rate limiter (no external dependencies).

Suitable for a single-process backend. Counts hits per (bucket, client IP)
within a sliding time window and raises HTTP 429 when the limit is exceeded.
"""

import time
from collections import defaultdict, deque

from fastapi import HTTPException, Request, status

_hits = defaultdict(deque)


def rate_limit(request: Request, bucket: str, max_hits: int, window_seconds: int) -> None:
    """
    Enforce a rate limit for the given logical bucket and the request's client IP.

    Raises HTTP 429 if more than `max_hits` calls happen within `window_seconds`.
    """
    now = time.monotonic()
    client_ip = request.client.host if request.client else "unknown"
    key = (bucket, client_ip)
    timestamps = _hits[key]

    # Drop timestamps outside the window.
    cutoff = now - window_seconds
    while timestamps and timestamps[0] <= cutoff:
        timestamps.popleft()

    if len(timestamps) >= max_hits:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests. Please try again later.",
        )

    timestamps.append(now)
