"""Deterministic forward-chaining fuzzy inference engine."""

from dataclasses import dataclass

from student_academic_advisor.expert_system.aggregation import (
    FinalConclusionAggregation,
    aggregate_final_conclusions,
)
from student_academic_advisor.expert_system.dependency_graph import (
    DependencyResolution,
    resolve_dependencies,
)
from student_academic_advisor.expert_system.fuzzy_logic import (
    MissingPremiseError,
    evaluate_condition,
)
from student_academic_advisor.expert_system.models import Fact, LoadedRule
from student_academic_advisor.expert_system.trace import (
    InferenceTrace,
    RuleTraceEntry,
)
from student_academic_advisor.expert_system.working_memory import WorkingMemory


class InferenceError(RuntimeError):
    """Raised when a validated rule cannot be evaluated during inference."""


@dataclass(frozen=True)
class InferenceResult:
    """Complete output of one student's forward-chaining inference run."""

    object_id: str
    facts: tuple[Fact, ...]
    final_conclusions: tuple[Fact, ...]
    trace: InferenceTrace
    aggregation: FinalConclusionAggregation
    dependency_resolution: DependencyResolution


def run_inference(
    initial_facts: tuple[Fact, ...],
    rules: tuple[LoadedRule, ...],
) -> InferenceResult:
    """Run rules once in dependency-resolved forward-chaining order."""
    dependency_resolution = resolve_dependencies(rules)
    working_memory = WorkingMemory(initial_facts)
    trace_entries: list[RuleTraceEntry] = []

    for evaluation_order, rule in enumerate(
        dependency_resolution.ordered_rules,
        start=1,
    ):
        try:
            condition = evaluate_condition(
                rule.condition_ast,
                working_memory.fact_values(),
            )
        except MissingPremiseError as error:
            raise InferenceError(
                f"rule {rule.id!r} could not be evaluated: {error}"
            ) from error

        fv = condition.value
        cv = fv * rule.cf
        conclusion_fact = working_memory.add_derived_fact(
            rule.conclusion,
            cv,
        )

        trace_entries.append(
            RuleTraceEntry(
                rule_id=rule.id,
                condition_text=rule.condition_source,
                premise_values=condition.premise_values,
                operator_steps=condition.operator_steps,
                fv=fv,
                cf=rule.cf,
                cv=cv,
                conclusion_attribute=rule.conclusion,
                conclusion_value=conclusion_fact.value,
                evaluation_order=evaluation_order,
                evaluated=True,
                fired=fv > 0.0,
                contributes=cv > 0.0,
            )
        )

    final_conclusions = tuple(
        working_memory.get_fact(attribute)
        for attribute in dependency_resolution.final_conclusions
    )
    aggregation = aggregate_final_conclusions(
        tuple(fact.value for fact in final_conclusions)
    )

    return InferenceResult(
        object_id=working_memory.object_id,
        facts=working_memory.snapshot(),
        final_conclusions=final_conclusions,
        trace=InferenceTrace(entries=tuple(trace_entries)),
        aggregation=aggregation,
        dependency_resolution=dependency_resolution,
    )
