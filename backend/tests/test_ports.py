"""The shared ports must stay real abstractions.

This is the guard that keeps the Repository pattern honest: if someone turns a
port back into a plain class or a dataclass, these tests fail.
"""

import inspect
from abc import ABC

import pytest

from app.domain.ports import (
    BaseRepository,
    MediaSource,
    ScoringStrategy,
    TranscriberPort,
)

PORTS = [BaseRepository, MediaSource, ScoringStrategy, TranscriberPort]


@pytest.mark.parametrize("port", PORTS, ids=lambda p: p.__name__)
def test_port_is_abstract(port: type) -> None:
    assert issubclass(port, ABC)
    assert port.__abstractmethods__, f"{port.__name__} declares no abstract method"


@pytest.mark.parametrize("port", PORTS, ids=lambda p: p.__name__)
def test_port_cannot_be_instantiated(port: type) -> None:
    with pytest.raises(TypeError):
        port()


@pytest.mark.parametrize("port", PORTS, ids=lambda p: p.__name__)
def test_port_methods_are_async(port: type) -> None:
    for name in port.__abstractmethods__:
        method = getattr(port, name)
        assert inspect.iscoroutinefunction(method), f"{port.__name__}.{name} must be async"


def test_fake_repository_satisfies_the_contract() -> None:
    """A use case can run against an in-memory double, with no database."""

    class FakeRepository(BaseRepository[str, int]):
        def __init__(self) -> None:
            self._rows: dict[int, str] = {}
            self._next_id = 1

        async def find_by_id(self, entity_id: int) -> str | None:
            return self._rows.get(entity_id)

        async def find_all(self) -> list[str]:
            return list(self._rows.values())

        async def save(self, entity: str) -> str:
            self._rows[self._next_id] = entity
            self._next_id += 1
            return entity

        async def update(self, entity_id: int, changes: dict[str, object]) -> str:
            self._rows[entity_id] = str(changes["value"])
            return self._rows[entity_id]

        async def delete(self, entity_id: int) -> None:
            self._rows.pop(entity_id, None)

    repo = FakeRepository()
    assert isinstance(repo, BaseRepository)


async def test_fake_repository_round_trip() -> None:
    class FakeRepository(BaseRepository[str, int]):
        def __init__(self) -> None:
            self._rows: dict[int, str] = {}

        async def find_by_id(self, entity_id: int) -> str | None:
            return self._rows.get(entity_id)

        async def find_all(self) -> list[str]:
            return list(self._rows.values())

        async def save(self, entity: str) -> str:
            self._rows[1] = entity
            return entity

        async def update(self, entity_id: int, changes: dict[str, object]) -> str:
            self._rows[entity_id] = str(changes["value"])
            return self._rows[entity_id]

        async def delete(self, entity_id: int) -> None:
            self._rows.pop(entity_id, None)

    repo = FakeRepository()
    await repo.save("lesson-1")

    assert await repo.find_by_id(1) == "lesson-1"
    assert await repo.find_all() == ["lesson-1"]

    await repo.delete(1)
    assert await repo.find_by_id(1) is None
