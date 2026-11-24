"""Root API router. Each module registers its own sub-router here."""

from fastapi import APIRouter

from app.api.endpoints import health

api_router = APIRouter()
api_router.include_router(health.router)
