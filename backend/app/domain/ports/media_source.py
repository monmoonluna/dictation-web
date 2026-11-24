"""Port for fetching media (uploaded file, URL, podcast feed, ...)."""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class MediaFile:
    buffer: bytes
    mime_type: str
    filename: str


@dataclass(frozen=True)
class MediaMetadata:
    duration_seconds: float
    size_bytes: int
    format: str


class MediaSource(ABC):
    """One implementation per media origin, all behind the same contract."""

    @abstractmethod
    async def get_media(self) -> MediaFile:
        """Download or read the media bytes."""

    @abstractmethod
    async def get_metadata(self) -> MediaMetadata:
        """Return duration, size and container format without full download."""
