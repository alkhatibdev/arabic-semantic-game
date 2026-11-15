"""API v1 router configuration."""

from fastapi import APIRouter

from app.api.v1.endpoints import challenges, games

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(challenges.router, prefix="/challenges", tags=["challenges"])
api_router.include_router(games.router, prefix="/game", tags=["games"])
