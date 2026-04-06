import time
from collections import defaultdict, deque
from threading import Lock
from typing import Deque, Dict, Tuple

from fastapi import HTTPException, Request, status

from .config import settings


class InMemoryRateLimiter:
    def __init__(self):
        self._buckets: Dict[Tuple[str, str], Deque[float]] = defaultdict(deque)
        self._lock = Lock()

    def check(self, key: str, scope: str, max_requests: int, window_seconds: int) -> None:
        if not settings.rate_limit_enabled:
            return

        now = time.time()
        bucket_key = (scope, key)

        with self._lock:
            bucket = self._buckets[bucket_key]
            while bucket and (now - bucket[0]) > window_seconds:
                bucket.popleft()

            if len(bucket) >= max_requests:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Too many requests. Please retry later.",
                )

            bucket.append(now)


rate_limiter = InMemoryRateLimiter()


def _client_key(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client and request.client.host:
        return request.client.host
    return "unknown"


def auth_rate_limit(request: Request) -> None:
    rate_limiter.check(
        key=_client_key(request),
        scope="auth",
        max_requests=settings.auth_rate_limit_requests,
        window_seconds=settings.auth_rate_limit_window_seconds,
    )


def simulation_rate_limit(request: Request) -> None:
    rate_limiter.check(
        key=_client_key(request),
        scope="simulation",
        max_requests=settings.simulation_rate_limit_requests,
        window_seconds=settings.simulation_rate_limit_window_seconds,
    )
