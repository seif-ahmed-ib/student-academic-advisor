"""Tests for restricted condition tokenization and AST parsing."""

import pytest

from student_academic_advisor.expert_system.models import (
    ConditionKind,
    ConditionNode,
)
from student_academic_advisor.expert_system.rule_parser import (
    ConditionSyntaxError,
    parse_condition,
)


def _fact(attribute: str) -> ConditionNode:
    return ConditionNode(ConditionKind.FACT_REF, fact_attribute=attribute)


def test_parses_single_fact_reference() -> None:
    assert parse_condition("high_absence") == _fact("high_absence")


def test_ignores_surrounding_and_internal_whitespace() -> None:
    assert parse_condition("  high_absence\tAND\nlow_study_time  ") == ConditionNode(
        ConditionKind.AND,
        operands=(_fact("high_absence"), _fact("low_study_time")),
    )


def test_not_has_higher_precedence_than_and() -> None:
    assert parse_condition("NOT a AND b") == ConditionNode(
        ConditionKind.AND,
        operands=(
            ConditionNode(ConditionKind.NOT, operands=(_fact("a"),)),
            _fact("b"),
        ),
    )


def test_and_has_higher_precedence_than_or() -> None:
    assert parse_condition("a OR b AND c") == ConditionNode(
        ConditionKind.OR,
        operands=(
            _fact("a"),
            ConditionNode(
                ConditionKind.AND,
                operands=(_fact("b"), _fact("c")),
            ),
        ),
    )


def test_parentheses_override_normal_precedence() -> None:
    assert parse_condition("a AND (b OR c)") == ConditionNode(
        ConditionKind.AND,
        operands=(
            _fact("a"),
            ConditionNode(
                ConditionKind.OR,
                operands=(_fact("b"), _fact("c")),
            ),
        ),
    )


@pytest.mark.parametrize("operator", ["AND", "OR"])
def test_groups_repeated_same_operator(operator: str) -> None:
    kind = ConditionKind(operator)

    assert parse_condition(f"a {operator} b {operator} c") == ConditionNode(
        kind,
        operands=(_fact("a"), _fact("b"), _fact("c")),
    )


def test_parses_repeated_not_from_right_to_left() -> None:
    assert parse_condition("NOT NOT a") == ConditionNode(
        ConditionKind.NOT,
        operands=(
            ConditionNode(ConditionKind.NOT, operands=(_fact("a"),)),
        ),
    )


def test_parses_approved_r3_nested_condition() -> None:
    source = (
        "persistent_low_performance AND "
        "(high_failure_history OR engagement_concern)"
    )

    ast = parse_condition(source)

    assert ast.kind is ConditionKind.AND
    assert ast.operands[0] == _fact("persistent_low_performance")
    assert ast.operands[1].kind is ConditionKind.OR
    assert ast.operands[1].operands == (
        _fact("high_failure_history"),
        _fact("engagement_concern"),
    )


def test_parses_approved_r4_nested_not_condition() -> None:
    source = (
        "high_absence AND NOT "
        "(low_first_period_performance OR low_second_period_performance)"
    )

    ast = parse_condition(source)

    assert ast.kind is ConditionKind.AND
    not_node = ast.operands[1]
    assert not_node.kind is ConditionKind.NOT
    assert not_node.operands[0].kind is ConditionKind.OR


def test_rejects_non_string_source() -> None:
    with pytest.raises(TypeError):
        parse_condition(None)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "source",
    [
        "",
        "   ",
        "a AND",
        "AND a",
        "a OR OR b",
        "a b",
        "(a OR b",
        "a OR b)",
        "()",
        "NOT",
        "a AND ()",
        "a >= b",
        "a-b",
    ],
)
def test_rejects_invalid_condition_syntax(source: str) -> None:
    with pytest.raises(ConditionSyntaxError):
        parse_condition(source)


@pytest.mark.parametrize("source", ["IF a", "a THEN b"])
def test_rejects_if_then_inside_condition(source: str) -> None:
    with pytest.raises(ConditionSyntaxError):
        parse_condition(source)
