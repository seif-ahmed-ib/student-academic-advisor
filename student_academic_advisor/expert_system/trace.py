"""Immutable explainability records captured during inference."""

from dataclasses import dataclass

from student_academic_advisor.expert_system.fuzzy_logic import OperatorStep


@dataclass(frozen=True)
class RuleTraceEntry:
    """One evaluated production rule and all values needed to explain it."""

    rule_id: str
    condition_text: str
    premise_values: tuple[tuple[str, float], ...]
    operator_steps: tuple[OperatorStep, ...]
    fv: float
    cf: float
    cv: float
    conclusion_attribute: str
    conclusion_value: float
    evaluation_order: int
    evaluated: bool
    fired: bool
    contributes: bool


@dataclass(frozen=True)
class InferenceTrace:
    """Ordered trace entries from one complete inference run."""

    entries: tuple[RuleTraceEntry, ...]
