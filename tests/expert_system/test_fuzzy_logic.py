"""Tests for fuzzy operators and condition-tree evaluation."""

import pytest

from student_academic_advisor.expert_system.fuzzy_logic import (
    MissingPremiseError,
    evaluate_condition,
    fuzzy_and,
    fuzzy_not,
    fuzzy_or,
)
from student_academic_advisor.expert_system.rule_parser import parse_condition


def test_approved_fuzzy_operators() -> None:
    assert fuzzy_and((0.8, 0.3, 0.6)) == pytest.approx(0.3)
    assert fuzzy_or((0.8, 0.3, 0.6)) == pytest.approx(0.8)
    assert fuzzy_not(0.3) == pytest.approx(0.7)


def test_evaluates_nested_condition_and_records_postorder_steps() -> None:
    condition = parse_condition("a AND NOT (b OR c)")

    evaluation = evaluate_condition(
        condition,
        {"a": 0.8, "b": 0.2, "c": 0.4},
    )

    assert evaluation.value == pytest.approx(0.6)
    assert evaluation.premise_values == (("a", 0.8), ("b", 0.2), ("c", 0.4))
    assert [step.operator for step in evaluation.operator_steps] == [
        "OR",
        "NOT",
        "AND",
    ]
    assert evaluation.operator_steps[-1].operand_values == pytest.approx(
        (0.8, 0.6)
    )


def test_repeated_fact_is_reported_once_but_evaluated_normally() -> None:
    condition = parse_condition("a OR a")

    evaluation = evaluate_condition(condition, {"a": 0.25})

    assert evaluation.value == pytest.approx(0.25)
    assert evaluation.premise_values == (("a", 0.25),)
    assert evaluation.operator_steps[0].operand_values == (0.25, 0.25)


def test_rejects_missing_premise() -> None:
    condition = parse_condition("a AND b")

    with pytest.raises(MissingPremiseError, match="'b'"):
        evaluate_condition(condition, {"a": 0.5})


@pytest.mark.parametrize("value", [True, -0.01, 1.01, float("nan")])
def test_rejects_invalid_fuzzy_values(value: object) -> None:
    with pytest.raises((TypeError, ValueError)):
        fuzzy_not(value)  # type: ignore[arg-type]


def test_rejects_operator_with_too_few_values() -> None:
    with pytest.raises(ValueError, match="at least two"):
        fuzzy_and((0.5,))
    with pytest.raises(ValueError, match="at least two"):
        fuzzy_or(())
