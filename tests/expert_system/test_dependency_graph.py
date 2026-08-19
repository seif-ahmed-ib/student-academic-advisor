"""Tests for rule dependency resolution and structural classification."""

import pytest

from student_academic_advisor.expert_system.dependency_graph import (
    CircularDependencyError,
    resolve_dependencies,
)
from student_academic_advisor.expert_system.models import LoadedRule, RuleSource
from student_academic_advisor.expert_system.rule_parser import parse_condition
from student_academic_advisor.expert_system.validation import load_knowledge_base


def _loaded_rule(
    rule_id: str,
    declaration_index: int,
    condition: str,
    conclusion: str,
) -> LoadedRule:
    source = RuleSource(
        id=rule_id,
        condition=condition,
        conclusion=conclusion,
        cf=0.8,
        description=f"Test rule {rule_id}.",
    )
    return LoadedRule(
        id=source.id,
        declaration_index=declaration_index,
        condition_source=source.condition,
        condition_ast=parse_condition(source.condition),
        conclusion=source.conclusion,
        cf=source.cf,
        description=source.description,
    )


def test_resolves_approved_knowledge_base() -> None:
    resolution = resolve_dependencies(load_knowledge_base())

    assert resolution.edges == (
        ("R1", "R3"),
        ("R2", "R3"),
        ("R3", "R6"),
    )
    assert [rule.id for rule in resolution.ordered_rules] == [
        "R1",
        "R2",
        "R3",
        "R4",
        "R5",
        "R6",
    ]
    assert resolution.intermediate_conclusions == (
        "engagement_concern",
        "persistent_low_performance",
        "core_academic_risk",
    )
    assert resolution.final_conclusions == (
        "attendance_based_support_need",
        "emerging_performance_support_need",
        "compounded_academic_support_need",
    )


def test_independent_rules_use_declaration_order_not_rule_id_order() -> None:
    rules = (
        _loaded_rule("Z_RULE", 0, "high_absence", "z_result"),
        _loaded_rule("A_RULE", 1, "low_study_time", "a_result"),
    )

    resolution = resolve_dependencies(rules)

    assert [rule.id for rule in resolution.ordered_rules] == [
        "Z_RULE",
        "A_RULE",
    ]


def test_newly_available_rule_competes_by_declaration_order() -> None:
    rules = (
        _loaded_rule("R1", 0, "high_absence", "derived_one"),
        _loaded_rule("R2", 1, "derived_one", "derived_two"),
        _loaded_rule("R3", 2, "low_study_time", "derived_three"),
    )

    resolution = resolve_dependencies(rules)

    assert [rule.id for rule in resolution.ordered_rules] == ["R1", "R2", "R3"]


def test_repeated_reference_creates_only_one_edge() -> None:
    rules = (
        _loaded_rule("R1", 0, "high_absence", "derived_one"),
        _loaded_rule(
            "R2",
            1,
            "derived_one OR derived_one",
            "final_result",
        ),
    )

    resolution = resolve_dependencies(rules)

    assert resolution.edges == (("R1", "R2"),)


def test_reports_exact_cycle_without_downstream_rule() -> None:
    rules = (
        _loaded_rule("R1", 0, "derived_two", "derived_one"),
        _loaded_rule("R2", 1, "derived_one", "derived_two"),
        _loaded_rule("R3", 2, "derived_two", "downstream_result"),
    )

    with pytest.raises(CircularDependencyError) as error_info:
        resolve_dependencies(rules)

    assert error_info.value.cycle_rule_ids == ("R1", "R2", "R1")
    assert "R3" not in str(error_info.value)


def test_rejects_self_dependency_as_a_cycle() -> None:
    rules = (
        _loaded_rule("R1", 0, "same_result", "same_result"),
    )

    with pytest.raises(CircularDependencyError) as error_info:
        resolve_dependencies(rules)

    assert error_info.value.cycle_rule_ids == ("R1", "R1")


def test_rejects_empty_rule_set() -> None:
    with pytest.raises(ValueError, match="at least one rule"):
        resolve_dependencies(())


def test_rejects_duplicate_declaration_indexes() -> None:
    rules = (
        _loaded_rule("R1", 0, "high_absence", "result_one"),
        _loaded_rule("R2", 0, "low_study_time", "result_two"),
    )

    with pytest.raises(ValueError, match="declaration indexes must be unique"):
        resolve_dependencies(rules)


def test_rejects_duplicate_rule_ids() -> None:
    rules = (
        _loaded_rule("R1", 0, "high_absence", "result_one"),
        _loaded_rule("R1", 1, "low_study_time", "result_two"),
    )

    with pytest.raises(ValueError, match="Rule IDs must be unique"):
        resolve_dependencies(rules)


def test_rejects_duplicate_conclusion_producers() -> None:
    rules = (
        _loaded_rule("R1", 0, "high_absence", "same_result"),
        _loaded_rule("R2", 1, "low_study_time", "same_result"),
    )

    with pytest.raises(ValueError, match="one producer each"):
        resolve_dependencies(rules)
