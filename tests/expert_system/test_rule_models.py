"""Tests for production-rule and condition-AST models."""

import pytest

from student_academic_advisor.expert_system.models import (
    ConditionKind,
    ConditionNode,
    LoadedRule,
    RuleSource,
)


def _fact(attribute: str = "high_absence") -> ConditionNode:
    return ConditionNode(ConditionKind.FACT_REF, fact_attribute=attribute)


def _rule_source(**overrides: object) -> RuleSource:
    values = {
        "id": "R1",
        "condition": "high_absence OR low_study_time",
        "conclusion": "engagement_concern",
        "cf": 0.70,
        "description": "An engagement-related support signal.",
    }
    values.update(overrides)
    return RuleSource(**values)  # type: ignore[arg-type]


def test_creates_valid_fact_reference_node() -> None:
    node = _fact()

    assert node.kind is ConditionKind.FACT_REF
    assert node.fact_attribute == "high_absence"
    assert node.operands == ()


@pytest.mark.parametrize(
    ("kind", "operands"),
    [
        (ConditionKind.NOT, (_fact(),)),
        (ConditionKind.AND, (_fact("a"), _fact("b"))),
        (ConditionKind.OR, (_fact("a"), _fact("b"))),
    ],
)
def test_creates_valid_operator_nodes(
    kind: ConditionKind,
    operands: tuple[ConditionNode, ...],
) -> None:
    node = ConditionNode(kind, operands=operands)

    assert node.kind is kind
    assert node.operands == operands


@pytest.mark.parametrize("attribute", [None, ""])
def test_fact_reference_requires_non_empty_attribute(
    attribute: str | None,
) -> None:
    with pytest.raises(ValueError):
        ConditionNode(ConditionKind.FACT_REF, fact_attribute=attribute)


def test_fact_reference_rejects_operands() -> None:
    with pytest.raises(ValueError):
        ConditionNode(
            ConditionKind.FACT_REF,
            fact_attribute="high_absence",
            operands=(_fact(),),
        )


def test_operator_rejects_fact_attribute() -> None:
    with pytest.raises(ValueError):
        ConditionNode(
            ConditionKind.NOT,
            fact_attribute="high_absence",
            operands=(_fact(),),
        )


@pytest.mark.parametrize("operands", [(), (_fact("a"), _fact("b"))])
def test_not_requires_exactly_one_operand(
    operands: tuple[ConditionNode, ...],
) -> None:
    with pytest.raises(ValueError):
        ConditionNode(ConditionKind.NOT, operands=operands)


@pytest.mark.parametrize("kind", [ConditionKind.AND, ConditionKind.OR])
def test_and_or_require_at_least_two_operands(kind: ConditionKind) -> None:
    with pytest.raises(ValueError):
        ConditionNode(kind, operands=(_fact(),))


def test_rejects_non_tuple_or_non_node_operands() -> None:
    with pytest.raises(TypeError):
        ConditionNode(ConditionKind.NOT, operands=[_fact()])  # type: ignore[arg-type]

    with pytest.raises(TypeError):
        ConditionNode(
            ConditionKind.NOT,
            operands=("high_absence",),  # type: ignore[arg-type]
        )


def test_creates_valid_rule_source_with_separate_fields() -> None:
    rule = _rule_source(cf=1)

    assert rule.id == "R1"
    assert rule.condition == "high_absence OR low_study_time"
    assert rule.conclusion == "engagement_concern"
    assert rule.cf == 1.0
    assert isinstance(rule.cf, float)


@pytest.mark.parametrize("field_name", ["id", "condition", "conclusion", "description"])
@pytest.mark.parametrize("value", ["", "   ", None])
def test_rule_source_rejects_missing_or_invalid_text(
    field_name: str,
    value: object,
) -> None:
    expected_error = TypeError if value is None else ValueError
    with pytest.raises(expected_error):
        _rule_source(**{field_name: value})


@pytest.mark.parametrize("cf", [True, "0.7", None])
def test_rule_source_rejects_non_numeric_cf(cf: object) -> None:
    with pytest.raises(TypeError):
        _rule_source(cf=cf)


@pytest.mark.parametrize("cf", [-0.01, 1.01, float("inf"), float("nan")])
def test_rule_source_rejects_cf_outside_finite_unit_interval(cf: float) -> None:
    with pytest.raises(ValueError):
        _rule_source(cf=cf)


def test_creates_valid_loaded_rule() -> None:
    ast = _fact()
    rule = LoadedRule(
        id="R1",
        declaration_index=0,
        condition_source="high_absence",
        condition_ast=ast,
        conclusion="attendance_based_support_need",
        cf=0.60,
        description="Attendance-based support need.",
    )

    assert rule.declaration_index == 0
    assert rule.condition_ast is ast
    assert rule.cf == 0.60


@pytest.mark.parametrize("declaration_index", [-1, True, 1.5])
def test_loaded_rule_rejects_invalid_declaration_index(
    declaration_index: object,
) -> None:
    expected_error = ValueError if declaration_index == -1 else TypeError
    with pytest.raises(expected_error):
        LoadedRule(
            id="R1",
            declaration_index=declaration_index,  # type: ignore[arg-type]
            condition_source="high_absence",
            condition_ast=_fact(),
            conclusion="attendance_based_support_need",
            cf=0.60,
            description="Attendance-based support need.",
        )


def test_loaded_rule_requires_condition_ast() -> None:
    with pytest.raises(TypeError):
        LoadedRule(
            id="R1",
            declaration_index=0,
            condition_source="high_absence",
            condition_ast="high_absence",  # type: ignore[arg-type]
            conclusion="attendance_based_support_need",
            cf=0.60,
            description="Attendance-based support need.",
        )
