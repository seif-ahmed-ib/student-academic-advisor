"""Core data models shared by the expert-system modules."""

from dataclasses import dataclass
from enum import Enum
from math import isfinite
from numbers import Integral, Real


class FactOrigin(str, Enum):
    """Identify whether a fact was fuzzified or produced by a rule."""

    INITIAL = "INITIAL"
    DERIVED = "DERIVED"


class ConditionKind(str, Enum):
    """Supported node types in a parsed rule-condition AST."""

    FACT_REF = "FACT_REF"
    NOT = "NOT"
    AND = "AND"
    OR = "OR"


@dataclass(frozen=True)
class ConditionNode:
    """One immutable node in a rule-condition abstract syntax tree."""

    kind: ConditionKind
    fact_attribute: str | None = None
    operands: tuple["ConditionNode", ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.kind, ConditionKind):
            raise TypeError(
                "kind must be a ConditionKind; "
                f"received {self.kind!r} ({type(self.kind).__name__})"
            )

        if not isinstance(self.operands, tuple) or not all(
            isinstance(operand, ConditionNode) for operand in self.operands
        ):
            raise TypeError("operands must be a tuple of ConditionNode objects")

        if self.kind is ConditionKind.FACT_REF:
            if not isinstance(self.fact_attribute, str) or not self.fact_attribute:
                raise ValueError(
                    "a FACT_REF node requires a non-empty fact_attribute"
                )
            if self.operands:
                raise ValueError("a FACT_REF node cannot contain operands")
            return

        if self.fact_attribute is not None:
            raise ValueError(
                f"a {self.kind.value} node cannot contain fact_attribute"
            )

        if self.kind is ConditionKind.NOT and len(self.operands) != 1:
            raise ValueError("a NOT node requires exactly one operand")

        if self.kind in (ConditionKind.AND, ConditionKind.OR) and len(
            self.operands
        ) < 2:
            raise ValueError(
                f"a {self.kind.value} node requires at least two operands"
            )


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


def _validate_required_text(field_name: str, value: str) -> None:
    """Validate a required non-empty text field."""
    if not isinstance(value, str):
        raise TypeError(
            f"{field_name} must be a string; "
            f"received {value!r} ({type(value).__name__})"
        )
    if not value.strip():
        raise ValueError(f"{field_name} must not be empty")


def _normalize_cf(value: float) -> float:
    """Validate and normalize one author-assigned confidence factor."""
    if isinstance(value, bool) or not isinstance(value, Real):
        raise TypeError(
            "cf must be a real number; "
            f"received {value!r} ({type(value).__name__})"
        )

    normalized_value = float(value)
    if not isfinite(normalized_value) or not 0.0 <= normalized_value <= 1.0:
        raise ValueError(
            "cf must be finite and between 0 and 1 inclusive; "
            f"received {value!r}"
        )
    return normalized_value


@dataclass(frozen=True)
class RuleSource:
    """Human-authored production-rule data before condition parsing."""

    id: str
    condition: str
    conclusion: str
    cf: float
    description: str

    def __post_init__(self) -> None:
        _validate_required_text("id", self.id)
        _validate_required_text("condition", self.condition)
        _validate_required_text("conclusion", self.conclusion)
        _validate_required_text("description", self.description)
        object.__setattr__(self, "cf", _normalize_cf(self.cf))


@dataclass(frozen=True)
class LoadedRule:
    """Validated production rule with its parsed condition AST."""

    id: str
    declaration_index: int
    condition_source: str
    condition_ast: ConditionNode
    conclusion: str
    cf: float
    description: str

    def __post_init__(self) -> None:
        _validate_required_text("id", self.id)
        _validate_required_text("condition_source", self.condition_source)
        _validate_required_text("conclusion", self.conclusion)
        _validate_required_text("description", self.description)

        if (
            isinstance(self.declaration_index, bool)
            or not isinstance(self.declaration_index, Integral)
        ):
            raise TypeError(
                "declaration_index must be an integer; "
                f"received {self.declaration_index!r} "
                f"({type(self.declaration_index).__name__})"
            )

        if self.declaration_index < 0:
            raise ValueError(
                "declaration_index must be zero or greater; "
                f"received {self.declaration_index!r}"
            )

        if not isinstance(self.condition_ast, ConditionNode):
            raise TypeError("condition_ast must be a ConditionNode")

        object.__setattr__(
            self,
            "declaration_index",
            int(self.declaration_index),
        )
        object.__setattr__(self, "cf", _normalize_cf(self.cf))