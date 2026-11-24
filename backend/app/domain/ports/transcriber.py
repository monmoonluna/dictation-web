"""Port for speech-to-text. Decorators (cache, logging) wrap this interface."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from app.domain.ports.media_source import MediaFile


@dataclass(frozen=True)
class TranscriptionOptions:
    language: str | None = None
    with_timestamps: bool = False


@dataclass(frozen=True)
class TranscriptSegment:
    text: str
    start_seconds: float
    end_seconds: float


@dataclass(frozen=True)
class TranscriptionResult:
    text: str
    language: str
    duration_seconds: float
    segments: list[TranscriptSegment] = field(default_factory=list)


class TranscriberPort(ABC):
    """Implemented by the real provider and by every decorator around it."""

    @abstractmethod
    async def transcribe(
        self,
        media: MediaFile,
        options: TranscriptionOptions | None = None,
    ) -> TranscriptionResult:
        """Turn audio into text, with optional per-segment timestamps."""
