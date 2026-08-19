"""Validated raw input for one Student Academic Advisor inference run."""

from dataclasses import dataclass
from numbers import Integral


_VALID_STUDY_TIME_CODES = (1, 2, 3, 4)
_VALID_FAILURE_CODES = (0, 1, 2, 3)


def _validate_integer(field_name: str, value: int) -> None:
    """Reject non-integer values, including booleans."""
    if isinstance(value, bool) or not isinstance(value, Integral):
        raise TypeError(
            f"{field_name} must be an integer; "
            f"received {value!r} ({type(value).__name__})"
        )


def _validate_integer_range(
    field_name: str,
    value: int,
    minimum: int,
    maximum: int,
) -> None:
    """Validate an integer against an inclusive range."""
    _validate_integer(field_name, value)

    if not minimum <= value <= maximum:
        raise ValueError(
            f"{field_name} must be between {minimum} and {maximum} inclusive; "
            f"received {value!r}"
        )


def _validate_integer_choice(
    field_name: str,
    value: int,
    accepted_values: tuple[int, ...],
) -> None:
    """Validate an integer against an approved discrete domain."""
    _validate_integer(field_name, value)

    if value not in accepted_values:
        accepted_text = ", ".join(str(item) for item in accepted_values)
        raise ValueError(
            f"{field_name} must be one of {accepted_text}; received {value!r}"
        )


@dataclass(frozen=True)
class RawStudentInput:
    """One validated student record before fuzzification.

    The object is immutable after construction so a validated record cannot be
    changed into an invalid state before the inference run starts.
    """

    object_id: str
    g1: int
    g2: int
    absences: int
    studytime: int
    failures: int

    def __post_init__(self) -> None:
        if not isinstance(self.object_id, str):
            raise TypeError(
                "object_id must be a string; "
                f"received {self.object_id!r} "
                f"({type(self.object_id).__name__})"
            )

        _validate_integer_range("g1", self.g1, 0, 20)
        _validate_integer_range("g2", self.g2, 0, 20)
        _validate_integer_range("absences", self.absences, 0, 93)
        _validate_integer_choice(
            "studytime",
            self.studytime,
            _VALID_STUDY_TIME_CODES,
        )
        _validate_integer_choice(
            "failures",
            self.failures,
            _VALID_FAILURE_CODES,
        )
