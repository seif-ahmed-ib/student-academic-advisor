"""Tests for Knowledge Base loading and structural validation."""

import json
from pathlib import Path

import pytest

from student_academic_advisor.expert_system.models import ConditionKind
from student_academic_advisor.expert_system.rule_parser import parse_condition
from student_academic_advisor.expert_system.validation import (
    KnowledgeBaseValidationError,
    collect_fact_references,
    load_knowledge_base,
)


def _valid_rule(**overrides: object) -> dict[str, object]:
    rule: dict[str, object] = {
        "id": "R1",
        "condition": "high_absence OR low_study_time",
        "conclusion": "engagement_concern",
        "cf": 0.70,
        "description": "An engagement-related support signal.",
    }
    rule.update(overrides)
    return rule


def _write_rules(tmp_path: Path, rules: object) -> Path:
    path = tmp_path / "rules.json"
    path.write_text(json.dumps(rules), encoding="utf-8")
    return path


def test_loads_approved_rules_in_declaration_order() -> None:
    rules = load_knowledge_base()

    assert [rule.id for rule in rules] == ["R1", "R2", "R3", "R4", "R5", "R6"]
    assert [rule.declaration_index for rule in rules] == list(range(6))
    assert [rule.cf for rule in rules] == [0.70, 0.90, 0.85, 0.60, 0.65, 0.90]
    assert rules[2].condition_ast.kind is ConditionKind.AND
    assert rules[3].condition_ast.kind is ConditionKind.AND
    assert rules[5].condition_ast.kind is ConditionKind.OR


def test_approved_rules_have_expected_references() -> None:
    rules = load_knowledge_base()
    references = {
        rule.id: collect_fact_references(rule.condition_ast) for rule in rules
    }

    assert references == {
        "R1": ("high_absence", "low_study_time"),
        "R2": (
            "low_first_period_performance",
            "low_second_period_performance",
        ),
        "R3": (
            "persistent_low_performance",
            "high_failure_history",
            "engagement_concern",
        ),
        "R4": (
            "high_absence",
            "low_first_period_performance",
            "low_second_period_performance",
        ),
        "R5": (
            "low_second_period_performance",
            "low_first_period_performance",
        ),
        "R6": (
            "core_academic_risk",
            "high_failure_history",
            "low_study_time",
        ),
    }


def test_fact_reference_collection_removes_duplicates() -> None:
    condition = parse_condition(
        "high_absence OR high_absence OR low_study_time"
    )

    assert collect_fact_references(condition) == (
        "high_absence",
        "low_study_time",
    )


def test_rejects_missing_knowledge_base_file(tmp_path: Path) -> None:
    with pytest.raises(KnowledgeBaseValidationError, match="could not read"):
        load_knowledge_base(tmp_path / "missing.json")


def test_rejects_malformed_json(tmp_path: Path) -> None:
    path = tmp_path / "rules.json"
    path.write_text("[{", encoding="utf-8")

    with pytest.raises(KnowledgeBaseValidationError, match="invalid JSON"):
        load_knowledge_base(path)


def test_rejects_non_array_top_level_value(tmp_path: Path) -> None:
    path = _write_rules(tmp_path, {"rules": [_valid_rule()]})

    with pytest.raises(KnowledgeBaseValidationError, match="top-level JSON array"):
        load_knowledge_base(path)


def test_rejects_empty_knowledge_base(tmp_path: Path) -> None:
    path = _write_rules(tmp_path, [])

    with pytest.raises(KnowledgeBaseValidationError, match="must not be empty"):
        load_knowledge_base(path)


def test_rejects_non_object_rule_entry(tmp_path: Path) -> None:
    path = _write_rules(tmp_path, ["not-a-rule"])

    with pytest.raises(KnowledgeBaseValidationError, match="must be a JSON object"):
        load_knowledge_base(path)


@pytest.mark.parametrize(
    "missing_field",
    ["id", "condition", "conclusion", "cf", "description"],
)
def test_rejects_missing_rule_field(tmp_path: Path, missing_field: str) -> None:
    rule = _valid_rule()
    del rule[missing_field]
    path = _write_rules(tmp_path, [rule])

    with pytest.raises(KnowledgeBaseValidationError, match="missing fields"):
        load_knowledge_base(path)


def test_rejects_unexpected_rule_field(tmp_path: Path) -> None:
    rule = _valid_rule(conclusion_type="FINAL")
    path = _write_rules(tmp_path, [rule])

    with pytest.raises(KnowledgeBaseValidationError, match="unexpected fields"):
        load_knowledge_base(path)


def test_rejects_duplicate_rule_ids(tmp_path: Path) -> None:
    path = _write_rules(
        tmp_path,
        [
            _valid_rule(),
            _valid_rule(conclusion="second_conclusion"),
        ],
    )

    with pytest.raises(KnowledgeBaseValidationError, match="duplicate Rule ID"):
        load_knowledge_base(path)


def test_rejects_duplicate_conclusion_producers(tmp_path: Path) -> None:
    path = _write_rules(
        tmp_path,
        [
            _valid_rule(),
            _valid_rule(id="R2"),
        ],
    )

    with pytest.raises(
        KnowledgeBaseValidationError,
        match="duplicate conclusion producer",
    ):
        load_knowledge_base(path)


def test_rejects_base_and_derived_name_collision(tmp_path: Path) -> None:
    path = _write_rules(
        tmp_path,
        [_valid_rule(conclusion="high_absence")],
    )

    with pytest.raises(KnowledgeBaseValidationError, match="conflict"):
        load_knowledge_base(path)


def test_rejects_unknown_fact_reference(tmp_path: Path) -> None:
    path = _write_rules(
        tmp_path,
        [_valid_rule(condition="unknown_student_fact")],
    )

    with pytest.raises(KnowledgeBaseValidationError, match="unknown facts"):
        load_knowledge_base(path)


def test_rejects_invalid_condition_syntax(tmp_path: Path) -> None:
    path = _write_rules(tmp_path, [_valid_rule(condition="high_absence AND")])

    with pytest.raises(KnowledgeBaseValidationError, match="invalid condition"):
        load_knowledge_base(path)


@pytest.mark.parametrize("cf", [True, -0.01, 1.01])
def test_rejects_invalid_cf(tmp_path: Path, cf: object) -> None:
    path = _write_rules(tmp_path, [_valid_rule(cf=cf)])

    with pytest.raises(KnowledgeBaseValidationError, match="invalid rule"):
        load_knowledge_base(path)


def test_rejects_knowledge_base_without_final_conclusion(tmp_path: Path) -> None:
    path = _write_rules(
        tmp_path,
        [
            _valid_rule(condition="derived_b", conclusion="derived_a"),
            _valid_rule(
                id="R2",
                condition="derived_a",
                conclusion="derived_b",
            ),
        ],
    )

    with pytest.raises(KnowledgeBaseValidationError, match="Final Conclusion"):
        load_knowledge_base(path)
