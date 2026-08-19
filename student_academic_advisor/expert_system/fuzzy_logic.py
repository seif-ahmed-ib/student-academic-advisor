"""Fuzzy operators and AST condition evaluation."""

from dataclasses import dataclass
from math import isfinite
from numbers import Real
from typing import Mapping

from student_academic_advisor.expert_system.models import (
    ConditionKind,
    ConditionNode,
)


class MissingPremiseError(KeyError):
    """Raised when a condition references an unavailable fact."""


@dataclass(frozen=True)
class OperatorStep:
    """One explainable fuzzy-operator calculation."""

    operator: str
    operand_values: tuple[float, ...]
    result: float


@dataclass(frozen=True)
class ConditionEvaluation:
    """Complete result of evaluating one condition AST."""

    value: float
    premise_values: tuple[tuple[str, float], ...]
    operator_steps: tuple[OperatorStep, ...]


def _fuzzy_value(value: float, name: str = "value") -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise TypeError(f"{name} must be a real number")
    normalized = float(value)
    if not isfinite(normalized) or not 0.0 <= normalized <= 1.0:
        raise ValueError(f"{name} must be finite and within [0, 1]")
    return normalized


def fuzzy_and(values: tuple[float, ...]) -> float:
    """Return fuzzy conjunction using minimum."""
    if len(values) < 2:
        raise ValueError("fuzzy AND requires at least two values")
    return min(_fuzzy_value(value) for value in values)


def fuzzy_or(values: tuple[float, ...]) -> float:
    """Return fuzzy disjunction using maximum."""
    if len(values) < 2:
        raise ValueError("fuzzy OR requires at least two values")
    return max(_fuzzy_value(value) for value in values)


def fuzzy_not(value: float) -> float:
    """Return fuzzy negation using one minus the input value."""
    return 1.0 - _fuzzy_value(value)


def evaluate_condition(
    condition: ConditionNode,
    fact_values: Mapping[str, float],
) -> ConditionEvaluation:
    """Evaluate a parsed condition and record its operator calculations."""
    if not isinstance(condition, ConditionNode):
        raise TypeError("condition must be a ConditionNode")

    premise_values: list[tuple[str, float]] = []
    seen_premises: set[str] = set()
    operator_steps: list[OperatorStep] = []

    def evaluate(node: ConditionNode) -> float:
        if node.kind is ConditionKind.FACT_REF:
            attribute = node.fact_attribute
            if attribute is None or attribute not in fact_values:
                raise MissingPremiseError(
                    f"premise {attribute!r} is not available"
                )
            value = _fuzzy_value(
                fact_values[attribute],
                f"fact {attribute!r}",
            )
            if attribute not in seen_premises:
                seen_premises.add(attribute)
                premise_values.append((attribute, value))
            return value

        operand_values = tuple(evaluate(operand) for operand in node.operands)
        if node.kind is ConditionKind.NOT:
            result = fuzzy_not(operand_values[0])
        elif node.kind is ConditionKind.AND:
            result = fuzzy_and(operand_values)
        elif node.kind is ConditionKind.OR:
            result = fuzzy_or(operand_values)
        else:
            raise ValueError(f"unsupported condition kind: {node.kind!r}")

        operator_steps.append(
            OperatorStep(
                operator=node.kind.value,
                operand_values=operand_values,
                result=result,
            )
        )
        return result

    value = evaluate(condition)
    return ConditionEvaluation(
        value=value,
        premise_values=tuple(premise_values),
        operator_steps=tuple(operator_steps),
    )
