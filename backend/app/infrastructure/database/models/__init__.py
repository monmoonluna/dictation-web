"""Every model must be imported here so Alembic can see it."""

from app.infrastructure.database.models.user_model import UserModel

__all__ = ["UserModel"]
