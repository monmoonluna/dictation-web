"""Liveness and readiness endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.config.settings import Settings, get_settings
from app.infrastructure.database.session import get_db

router = APIRouter(tags=["health"])


@router.get("/health")
async def health(settings: Settings = Depends(get_settings)) -> dict[str, str]:
    """Cheap check that the process is up."""
    return {"status": "ok", "app": settings.app_name, "env": settings.app_env}


@router.get("/health/db")
async def health_db(session: AsyncSession = Depends(get_db)) -> dict[str, str]:
    """Check that the database accepts queries."""
    await session.execute(text("SELECT 1"))
    return {"status": "ok", "database": "reachable"}
