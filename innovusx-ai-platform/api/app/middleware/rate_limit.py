"""Rate limiting middleware."""

import time
from collections import defaultdict
from typing import Callable, Optional

import structlog
from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = structlog.get_logger()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Simple in-memory rate limiting middleware.

    For production, use Redis-based rate limiting for distributed systems.
    """

    def __init__(
        self,
        app,
        requests_per_minute: int = 60,
        requests_per_hour: int = 500,
        exclude_paths: Optional[list[str]] = None
    ):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.exclude_paths = exclude_paths or ["/health", "/metrics", "/docs", "/redoc", "/openapi.json"]

        # In-memory storage (use Redis for production)
        self.minute_requests: dict[str, list[float]] = defaultdict(list)
        self.hour_requests: dict[str, list[float]] = defaultdict(list)

    def _get_client_key(self, request: Request) -> str:
        """Get unique client identifier."""
        # Check for API key first
        api_key = request.headers.get("X-API-Key")
        if api_key:
            return f"api:{api_key[:16]}"

        # Fall back to IP address
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return f"ip:{forwarded_for.split(',')[0].strip()}"

        if request.client:
            return f"ip:{request.client.host}"

        return "ip:unknown"

    def _is_excluded(self, path: str) -> bool:
        """Check if path is excluded from rate limiting."""
        return any(path.startswith(excluded) for excluded in self.exclude_paths)

    def _clean_old_requests(self, requests: list[float], window_seconds: int) -> list[float]:
        """Remove requests outside the time window."""
        cutoff = time.time() - window_seconds
        return [req_time for req_time in requests if req_time > cutoff]

    def _check_rate_limit(self, client_key: str) -> tuple[bool, Optional[str], Optional[int]]:
        """
        Check if client has exceeded rate limits.

        Returns:
            (is_allowed, limit_type, retry_after_seconds)
        """
        now = time.time()

        # Clean and check minute limit
        self.minute_requests[client_key] = self._clean_old_requests(
            self.minute_requests[client_key], 60
        )
        if len(self.minute_requests[client_key]) >= self.requests_per_minute:
            oldest = min(self.minute_requests[client_key])
            retry_after = int(60 - (now - oldest)) + 1
            return False, "minute", retry_after

        # Clean and check hour limit
        self.hour_requests[client_key] = self._clean_old_requests(
            self.hour_requests[client_key], 3600
        )
        if len(self.hour_requests[client_key]) >= self.requests_per_hour:
            oldest = min(self.hour_requests[client_key])
            retry_after = int(3600 - (now - oldest)) + 1
            return False, "hour", retry_after

        return True, None, None

    def _record_request(self, client_key: str) -> None:
        """Record a request for rate limiting."""
        now = time.time()
        self.minute_requests[client_key].append(now)
        self.hour_requests[client_key].append(now)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with rate limiting."""
        # Skip rate limiting for excluded paths
        if self._is_excluded(request.url.path):
            return await call_next(request)

        client_key = self._get_client_key(request)

        # Check rate limits
        is_allowed, limit_type, retry_after = self._check_rate_limit(client_key)

        if not is_allowed:
            logger.warning(
                "Rate limit exceeded",
                client_key=client_key,
                limit_type=limit_type,
                retry_after=retry_after,
                path=request.url.path
            )

            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "Rate limit exceeded",
                    "detail": f"Too many requests. Please retry after {retry_after} seconds.",
                    "retry_after": retry_after,
                    "limit_type": limit_type
                },
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit": str(
                        self.requests_per_minute if limit_type == "minute"
                        else self.requests_per_hour
                    ),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(time.time()) + retry_after)
                }
            )

        # Record this request
        self._record_request(client_key)

        # Process request
        response = await call_next(request)

        # Add rate limit headers to response
        minute_remaining = self.requests_per_minute - len(self.minute_requests[client_key])
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(max(0, minute_remaining))
        response.headers["X-RateLimit-Reset"] = str(int(time.time()) + 60)

        return response


class RedisRateLimiter:
    """
    Redis-based rate limiter for distributed systems.

    This is a placeholder for production implementation.
    """

    def __init__(self, redis_client, key_prefix: str = "ratelimit"):
        self.redis = redis_client
        self.key_prefix = key_prefix

    async def is_allowed(
        self,
        client_key: str,
        limit: int,
        window_seconds: int
    ) -> tuple[bool, int, int]:
        """
        Check if request is allowed using sliding window counter.

        Returns:
            (is_allowed, remaining, reset_time)
        """
        key = f"{self.key_prefix}:{client_key}:{window_seconds}"
        now = time.time()

        # Use Redis pipeline for atomic operations
        pipe = self.redis.pipeline()

        # Remove old entries
        pipe.zremrangebyscore(key, 0, now - window_seconds)

        # Count current entries
        pipe.zcard(key)

        # Add current request
        pipe.zadd(key, {str(now): now})

        # Set expiry
        pipe.expire(key, window_seconds)

        results = await pipe.execute()
        current_count = results[1]

        if current_count >= limit:
            # Get oldest entry to calculate reset time
            oldest = await self.redis.zrange(key, 0, 0, withscores=True)
            reset_time = int(oldest[0][1] + window_seconds) if oldest else int(now + window_seconds)
            return False, 0, reset_time

        return True, limit - current_count - 1, int(now + window_seconds)
