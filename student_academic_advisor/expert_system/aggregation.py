"""Knowledge Base aggregation over structurally Final Conclusions."""

from dataclasses import dataclass
from math import isfinite
from numbers import Real


@dataclass(frozen=True)
class FinalConclusionAggregation:
    """Maximum and fuzzy-union results over final conclusion values."""

    inputs: tuple[float, ...]
    maximum: float
    union: float


def _validated_inputs(values: tuple[float, ...]) -> tuple[float, ...]:
    if not values:
        raise ValueError("final conclusion values must not be empty")

    normalized: list[float] = []
    for value in values:
        if isinstance(value, bool) or not isinstance(value, Real):
            raise TypeError("final conclusion values must be real numbers")
        number = float(value)
        if not isfinite(number) or not 0.0 <= number <= 1.0:
            raise ValueError(
                "final conclusion values must be finite and within [0, 1]"
            )
        normalized.append(number)
    return tuple(normalized)


def aggregate_final_conclusions(
    values: tuple[float, ...],
) -> FinalConclusionAggregation:
    """Calculate Maximum and repeated fuzzy Union without early rounding."""
    inputs = _validated_inputs(values)
    union = 0.0
    for value in inputs:
        union = union + value - (union * value)

    return FinalConclusionAggregation(
        inputs=inputs,
        maximum=max(inputs),
        union=union,
    )
