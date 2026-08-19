"""Core data models shared by the expert-system modules."""

from dataclasses import dataclass
from enum import Enum
from math import isfinite
from numbers import Real


class FactOrigin(str, Enum):
    """Identify whether a fact was fuzzified or produced by a rule."""

    INITIAL = "INITIAL"
    DERIVED = "DERIVED"


@dataclass(frozen=True)
class Fact:
    """One immutable O-A-V fuzzy fact for a student."""

    object_id: str
    attribute: str
    value: float
    origin: FactOrigin

    def __post_init__(self) -> None:
        if not isinstance(self.object_id, str):
            raise TypeError(
                "object_id must be a string; "
                f"received {self.object_id!r} "
                f"({type(self.object_id).__name__})"
            )

        if not isinstance(self.attribute, str):
            raise TypeError(
                "attribute must be a string; "
                f"received {self.attribute!r} "
                f"({type(self.attribute).__name__})"
            )

        if isinstance(self.value, bool) or not isinstance(self.value, Real):
            raise TypeError(
                "value must be a real number; "
                f"received {self.value!r} ({type(self.value).__name__})"
            )

        normalized_value = float(self.value)
        if not isfinite(normalized_value) or not 0.0 <= normalized_value <= 1.0:
            raise ValueError(
                "value must be finite and between 0 and 1 inclusive; "
                f"received {self.value!r}"
            )

        if not isinstance(self.origin, FactOrigin):
            raise TypeError(
                "origin must be a FactOrigin; "
                f"received {self.origin!r} ({type(self.origin).__name__})"
            )

        object.__setattr__(self, "value", normalized_value)
