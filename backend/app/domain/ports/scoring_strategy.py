"""Port for comparing what the learner typed against the reference text."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass(frozen=True)
class ScoringResult:
    score: float
    details: dict[str, float] = field(default_factory=dict)


class ScoringStrategy(ABC):
    """Strategy pattern: one implementation per scoring algorithm."""

    @abstractmethod
    async def calculate(self, reference: str, hypothesis: str) -> ScoringResult:
        """Return a score in [0, 1] plus algorithm-specific details."""
