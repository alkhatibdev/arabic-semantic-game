"""Main FastAPI application."""

import logging
from contextlib import asynccontextmanager

import redis.asyncio as redis
import sentry_sdk
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.logging import configure_logging
from app.core.ml_model import model_loader
from app.core.rate_limiter import FastAPILimiter, RateLimiter, get_identifier

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup and shutdown events."""
    configure_logging()
    logger.info(
        "Starting %s v%s (%s)", settings.PROJECT_NAME, settings.VERSION, settings.ENVIRONMENT
    )

    # Load the embedding model up front so the first request isn't the one that waits.
    model_loader.load_model()

    if settings.RATE_LIMIT_ENABLED:
        redis_connection = redis.from_url(
            settings.RATE_LIMIT_STORAGE_URI,
            encoding="utf-8",
            decode_responses=True,
        )
        await FastAPILimiter.init(redis_connection, identifier=get_identifier)
        # Deliberately not logging the URI itself - it can carry a password.
        logger.info("Rate limiting enabled (Redis backend)")
    else:
        logger.warning("Rate limiting is DISABLED - do not run a public deployment this way")

    if settings.SENTRY_DSN:
        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            # Players are anonymous and there is no privacy policy, so don't ship
            # IPs, headers or request bodies.
            send_default_pii=False,
            environment=settings.ENVIRONMENT,
            release=settings.VERSION,
        )
        logger.info("Sentry enabled")

    yield

    if settings.RATE_LIMIT_ENABLED:
        await FastAPILimiter.close()
    logger.info("Shutting down")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Arabic word similarity game API",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    # No cookies and no auth headers are used, so credentialed requests are
    # pure attack surface.
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/health", tags=["meta"])
async def health():
    """Liveness probe. Deliberately unmetered so load balancers can poll it."""
    return {"status": "healthy", "version": settings.VERSION}


@app.get("/", tags=["meta"], dependencies=[Depends(RateLimiter(times=60, seconds=60))])
async def root():
    """Root endpoint."""
    return {"version": settings.VERSION, "status": "healthy"}
