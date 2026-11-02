"""Python home for future sensor analytics. Keep demo values distinct from clinical claims."""

from dataclasses import dataclass


@dataclass(frozen=True)
class SensorMetrics:
    max_strain: float
    gradient: float
    variability: float


def threshold_level(metrics: SensorMetrics) -> int:
    """Return a prototype heuristic level from 1 to 5 for research/demo use."""
    for level, limits in (
        (5, (8.0, 4.0, 1.5)),
        (4, (6.0, 3.0, 1.0)),
        (3, (4.0, 2.0, 0.5)),
        (2, (2.0, 1.0, 0.25)),
    ):
        values = (metrics.max_strain, metrics.gradient, metrics.variability)
        if any(value >= limit for value, limit in zip(values, limits, strict=True)):
            return level
    return 1
