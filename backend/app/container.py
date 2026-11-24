"""Composition root.

Every shared resource is resolved here and injected into the API layer, so
nothing in `domain/` or `application/` reaches for a global object.
"""

from collections.abc import AsyncIterator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.config.settings import Settings, get_settings
from app.infrastructure.database.session import get_db

SettingsDep = Depends(get_settings)
DbSessionDep = Depends(get_db)

__all__ = [
    "AsyncIterator",
    "AsyncSession",
    "DbSessionDep",
    "Settings",
    "SettingsDep",
    "get_db",
    "get_settings",
]
