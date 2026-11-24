"""Generic persistence port (Repository pattern).

The domain and the use cases depend on this abstraction only; concrete
SQLAlchemy or in-memory implementations live in the infrastructure layer.
"""

from abc import ABC, abstractmethod


class BaseRepository[T, ID](ABC):
    """Common CRUD contract shared by every repository."""

    @abstractmethod
    async def find_by_id(self, entity_id: ID) -> T | None:
        """Return the entity with this id, or None when it does not exist."""

    @abstractmethod
    async def find_all(self) -> list[T]:
        """Return every entity. Implementations may paginate internally."""

    @abstractmethod
    async def save(self, entity: T) -> T:
        """Insert the entity and return the persisted version."""

    @abstractmethod
    async def update(self, entity_id: ID, changes: dict[str, object]) -> T:
        """Apply a partial update and return the persisted version."""

    @abstractmethod
    async def delete(self, entity_id: ID) -> None:
        """Remove the entity. Must not raise when it is already gone."""
