"""Rate limiting configuration using fastapi-limiter."""

from fastapi import Request, Response
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter as _RedisRateLimiter

from app.core.config import settings


async def get_identifier(request: Request) -> str:
    """
    The rate-limit bucket key: the client's IP address.

    This deliberately does NOT read X-Forwarded-For itself. Any client can send
    that header, so trusting it here handed every caller the ability to pick its
    own bucket - a fresh value per request meant no limit at all, and rate
    limiting is the only thing bounding abuse of an API with no authentication.

    Behind a proxy, let uvicorn do it instead: it rewrites request.client from
    the forwarded headers only when the connecting peer is in its trusted list.
    Run with --proxy-headers (on by default) and set FORWARDED_ALLOW_IPS to your
    proxy's address - it defaults to 127.0.0.1, and must never be "*".
    """
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
