"""Rate limiting configuration using fastapi-limiter."""

from fastapi import Request, Response
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter as _RedisRateLimiter

from app.core.config import settings


async def get_identifier(request: Request) -> str:
    """
    Get the identifier for rate limiting.

    Uses the client's IP address as the identifier.
    Can be extended to use user_id from headers or other identifiers.
    """
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


class _NoOpRateLimiter:
    """Stand-in dependency used when rate limiting is disabled."""

    def __init__(self, *args, **kwargs) -> None:
        pass

    async def __call__(self, request: Request, response: Response) -> None:
        return None


def RateLimiter(*args, **kwargs):  # noqa: N802 - mirrors the upstream class name
    """
    Build a rate-limit dependency.

    Every route declares this unconditionally, so when RATE_LIMIT_ENABLED is
    false we have to hand back a working no-op: fastapi-limiter's own dependency
    raises on every request when FastAPILimiter.init() was never called, which
    would otherwise turn "rate limiting off" into "every endpoint returns 500".
    """
    if not settings.RATE_LIMIT_ENABLED:
        return _NoOpRateLimiter()
    return _RedisRateLimiter(*args, **kwargs)


__all__ = ["FastAPILimiter", "RateLimiter", "get_identifier"]
