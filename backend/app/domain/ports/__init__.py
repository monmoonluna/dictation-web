"""Shared ports. Import from here so call sites stay stable."""

from app.domain.ports.media_source import MediaFile, MediaMetadata, MediaSource
from app.domain.ports.repository import BaseRepository
from app.domain.ports.scoring_strategy import ScoringResult, ScoringStrategy
from app.domain.ports.transcriber import (
    TranscriberPort,
    TranscriptionOptions,
    TranscriptionResult,
    TranscriptSegment,
)

__all__ = [
    "BaseRepository",
    "MediaFile",
    "MediaMetadata",
    "MediaSource",
    "ScoringResult",
    "ScoringStrategy",
    "TranscriberPort",
    "TranscriptSegment",
    "TranscriptionOptions",
    "TranscriptionResult",
]
