from __future__ import annotations

from dataclasses import dataclass


@dataclass
class MetricAccumulator:
    numerator: int = 0
    denominator: int = 0

    def add(self, correct: int, total: int = 1) -> None:
        self.numerator += correct
        self.denominator += total

    @property
    def value(self) -> float:
        return self.numerator / self.denominator if self.denominator else 0.0
