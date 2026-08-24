"""End-to-end tests for deterministic fuzzy forward chaining."""

import pytest

from student_academic_advisor.expert_system.fuzzification import fuzzify_student
from student_academic_advisor.expert_system.inference_engine import (
    InferenceError,
    run_inference,
)
from student_academic_advisor.expert_system.models import (
    Fact,
    FactOrigin,
    LoadedRule,
    RuleSource,
)
from student_academic_advisor.expert_system.raw_input import RawStudentInput
from student_academic_advisor.expert_system.rule_parser import parse_condition
from student_academic_advisor.expert_system.validation import load_knowledge_base


def _rule(condition: str, conclusion: str, cf: float = 0.8) -> LoadedRule:
    source = RuleSource("T1", condition, conclusion, cf, "Test rule.")
    return LoadedRule(
        id=source.id,
        declaration_index=0,
        condition_source=source.condition,
        condition_ast=parse_condition(source.condition),
        conclusion=source.conclusion,
        cf=source.cf,
        description=source.description,
    )


def _initial_fact(attribute: str, value: float) -> Fact:
    return Fact("S1", attribute, value, FactOrigin.INITIAL)


def test_por_0649_complete_inference_and_cv_propagation() -> None:
    student = RawStudentInput(
        object_id="POR-0649",
        g1=10,
        g2=11,
        absences=4,
        studytime=1,
        failures=0,
    )
    initial_facts = fuzzify_student(student)

    result = run_inference(initial_facts, load_knowledge_base())
    entries = {entry.rule_id: entry for entry in result.trace.entries}
    facts = {fact.attribute: fact.value for fact in result.facts}

    assert result.object_id == "POR-0649"
    assert [entry.rule_id for entry in result.trace.entries] == [
        "R1",
        "R2",
        "R3",
        "R4",
        "R5",
        "R6",
    ]
    assert entries["R1"].fv == pytest.approx(1.0)
    assert entries["R1"].cv == pytest.approx(0.7)
    assert entries["R2"].fv == pytest.approx(1.0 / 3.0)
    assert entries["R2"].cv == pytest.approx(0.3)

    assert [name for name, _ in entries["R3"].premise_values] == [
        "persistent_low_performance",
        "high_failure_history",
        "engagement_concern",
    ]
    assert [value for _, value in entries["R3"].premise_values] == pytest.approx(
        [0.3, 0.0, 0.7]
    )
    assert entries["R3"].fv == pytest.approx(0.3)
    assert entries["R3"].cv == pytest.approx(0.255)
    assert entries["R6"].premise_values[0][0] == "core_academic_risk"
    assert entries["R6"].premise_values[0][1] == pytest.approx(0.255)
    assert entries["R6"].cv == pytest.approx(0.2295)

    assert facts["attendance_based_support_need"] == pytest.approx(0.15)
    assert facts["emerging_performance_support_need"] == pytest.approx(
        (1.0 / 3.0) * 0.65
    )
    assert facts["compounded_academic_support_need"] == pytest.approx(0.2295)

    expected_final_values = (
        0.15,
        (1.0 / 3.0) * 0.65,
        0.2295,
    )
    assert result.aggregation.inputs == pytest.approx(expected_final_values)
    assert result.aggregation.maximum == pytest.approx(0.2295)
    expected_union = 1.0
    for value in expected_final_values:
        expected_union *= 1.0 - value
    assert result.aggregation.union == pytest.approx(1.0 - expected_union)


def test_trace_contains_required_explainability_fields() -> None:
    result = run_inference(
        (_initial_fact("high_absence", 0.5),),
        (_rule("high_absence", "support_need"),),
    )
    entry = result.trace.entries[0]

    assert entry.condition_text == "high_absence"
    assert entry.premise_values == (("high_absence", 0.5),)
    assert entry.operator_steps == ()
    assert entry.fv == pytest.approx(0.5)
    assert entry.cf == pytest.approx(0.8)
    assert entry.cv == pytest.approx(0.4)
    assert entry.conclusion_attribute == "support_need"
    assert entry.conclusion_value == pytest.approx(0.4)
    assert entry.evaluation_order == 1
    assert entry.evaluated is True
    assert entry.fired is True
    assert entry.contributes is True


def test_fired_and_contributes_are_distinct_without_threshold() -> None:
    result = run_inference(
        (_initial_fact("high_absence", 0.6),),
        (_rule("high_absence", "support_need", cf=0.0),),
    )
    entry = result.trace.entries[0]

    assert entry.fv == pytest.approx(0.6)
    assert entry.cv == 0.0
    assert entry.fired is True
    assert entry.contributes is False
    assert result.final_conclusions[0].value == 0.0


def test_zero_activation_is_evaluated_stored_and_not_fired() -> None:
    result = run_inference(
        (_initial_fact("high_absence", 0.0),),
        (_rule("high_absence", "support_need"),),
    )
    entry = result.trace.entries[0]

    assert entry.evaluated is True
    assert entry.fv == 0.0
    assert entry.fired is False
    assert entry.contributes is False
    assert result.final_conclusions[0].value == 0.0


def test_not_can_activate_from_a_zero_valued_defined_fact() -> None:
    result = run_inference(
        (_initial_fact("high_absence", 0.0),),
        (_rule("NOT high_absence", "support_need"),),
    )

    assert result.trace.entries[0].fv == pytest.approx(1.0)
    assert result.final_conclusions[0].value == pytest.approx(0.8)


def test_initial_fact_tuple_is_not_modified() -> None:
    initial_facts = (_initial_fact("high_absence", 0.5),)

    run_inference(initial_facts, (_rule("high_absence", "support_need"),))

    assert len(initial_facts) == 1
    assert initial_facts[0].origin is FactOrigin.INITIAL


def test_reports_unavailable_runtime_premise_with_rule_id() -> None:
    rule = _rule("high_absence", "support_need")

    with pytest.raises(InferenceError, match="T1"):
        run_inference(
            (_initial_fact("low_study_time", 0.5),),
            (rule,),
        )
