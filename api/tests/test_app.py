"""Application wiring smoke tests - no database or model required."""

from fastapi.testclient import TestClient

from app.main import app


def test_health_endpoint():
    # Constructed without the context manager on purpose: entering it runs the
    # lifespan, which downloads the embedding model.
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_removed_endpoints_are_gone():
    """
    Two endpoints were deleted before open-sourcing and must not come back:

    - /api/v1/challenges/next-challenge/without-hints returned an unplayed
      target word to anonymous callers.
    - /populate-daily-words was an unauthenticated admin stub.
    """
    paths = {route.path for route in app.routes}
    assert "/api/v1/challenges/next-challenge/without-hints" not in paths
    assert "/populate-daily-words" not in paths


def test_cors_is_not_wildcard_and_not_credentialed():
    from starlette.middleware.cors import CORSMiddleware

    cors = [m for m in app.user_middleware if m.cls is CORSMiddleware]
    assert len(cors) == 1
    options = cors[0].kwargs
    assert "*" not in options["allow_origins"]
    assert options["allow_credentials"] is False


async def test_rate_limit_identifier_ignores_forwarded_header():
    """
    The bucket key must come from the connection, not from a header.

    get_identifier used to return X-Forwarded-For verbatim, so any client could
    pick its own bucket and a fresh value per request meant no limit at all.
    Rate limiting is the only thing bounding an API with no authentication, so
    this must not regress. Behind a proxy, uvicorn rewrites request.client for
    trusted peers (--proxy-headers / FORWARDED_ALLOW_IPS) and this still holds.
    """
    from app.core.rate_limiter import get_identifier

    class _Request:
        def __init__(self, headers):
            self.headers = headers
            self.client = type("C", (), {"host": "203.0.113.9"})()

    spoofed = await get_identifier(_Request({"X-Forwarded-For": "1.2.3.4"}))
    assert spoofed == "203.0.113.9", "X-Forwarded-For must not choose the bucket"
    assert await get_identifier(_Request({})) == "203.0.113.9"


def test_rate_limiter_is_a_noop_when_disabled():
    """
    Every route declares a rate-limit dependency unconditionally, so disabling
    rate limiting used to make all of them return 500.
    """
    from app.core.rate_limiter import RateLimiter, _NoOpRateLimiter

    assert isinstance(RateLimiter(times=1, seconds=1), _NoOpRateLimiter)
