"""Rule dependency resolution for the forward-chaining expert system."""

from dataclasses import dataclass
import heapq

from student_academic_advisor.expert_system.models import LoadedRule
from student_academic_advisor.expert_system.validation import (
    collect_fact_references,
)


class CircularDependencyError(ValueError):
    """Raised when production rules contain a circular dependency."""

    def __init__(self, cycle_rule_ids: tuple[str, ...]) -> None:
        self.cycle_rule_ids = cycle_rule_ids
        cycle_text = " -> ".join(cycle_rule_ids)
        super().__init__(f"circular dependency detected: {cycle_text}")


@dataclass(frozen=True)
class DependencyResolution:
    """Immutable structural results derived from one validated rule set."""

    edges: tuple[tuple[str, str], ...]
    ordered_rules: tuple[LoadedRule, ...]
    intermediate_conclusions: tuple[str, ...]
    final_conclusions: tuple[str, ...]


def _validate_rules(rules: tuple[LoadedRule, ...]) -> None:
    if not rules:
        raise ValueError("dependency resolution requires at least one rule")
    if not all(isinstance(rule, LoadedRule) for rule in rules):
        raise TypeError("rules must be a tuple of LoadedRule objects")

    declaration_indexes = [rule.declaration_index for rule in rules]
    if len(declaration_indexes) != len(set(declaration_indexes)):
        raise ValueError("rule declaration indexes must be unique")

    rule_ids = [rule.id for rule in rules]
    if len(rule_ids) != len(set(rule_ids)):
        raise ValueError("Rule IDs must be unique")

    conclusions = [rule.conclusion for rule in rules]
    if len(conclusions) != len(set(conclusions)):
        raise ValueError("rule conclusions must have one producer each")


def _build_edges(
    rules: tuple[LoadedRule, ...],
) -> tuple[tuple[str, str], ...]:
    producer_by_conclusion = {rule.conclusion: rule.id for rule in rules}
    consumer_dependencies: dict[str, set[str]] = {
        rule.id: set() for rule in rules
    }

    for consumer in rules:
        for attribute in collect_fact_references(consumer.condition_ast):
            producer_id = producer_by_conclusion.get(attribute)
            if producer_id is not None:
                consumer_dependencies[consumer.id].add(producer_id)

    edges: list[tuple[str, str]] = []
    for producer in rules:
        for consumer in rules:
            if producer.id in consumer_dependencies[consumer.id]:
                edges.append((producer.id, consumer.id))

    return tuple(edges)


def _find_cycle(
    rule_ids: tuple[str, ...],
    dependents: dict[str, list[str]],
) -> tuple[str, ...]:
    state = {rule_id: 0 for rule_id in rule_ids}
    path: list[str] = []
    path_index: dict[str, int] = {}

    def visit(rule_id: str) -> tuple[str, ...] | None:
        state[rule_id] = 1
        path_index[rule_id] = len(path)
        path.append(rule_id)

        for dependent_id in dependents[rule_id]:
            if state[dependent_id] == 0:
                cycle = visit(dependent_id)
                if cycle is not None:
                    return cycle
            elif state[dependent_id] == 1:
                start = path_index[dependent_id]
                return tuple(path[start:] + [dependent_id])

        path.pop()
        path_index.pop(rule_id)
        state[rule_id] = 2
        return None

    for rule_id in rule_ids:
        if state[rule_id] == 0:
            cycle = visit(rule_id)
            if cycle is not None:
                return cycle

    raise RuntimeError("topological ordering failed without locating a cycle")


def _topological_order(
    rules: tuple[LoadedRule, ...],
    edges: tuple[tuple[str, str], ...],
) -> tuple[LoadedRule, ...]:
    rule_by_id = {rule.id: rule for rule in rules}
    input_position = {rule.id: index for index, rule in enumerate(rules)}
    indegree = {rule.id: 0 for rule in rules}
    dependents = {rule.id: [] for rule in rules}

    for producer_id, consumer_id in edges:
        dependents[producer_id].append(consumer_id)
        indegree[consumer_id] += 1

    ready: list[tuple[int, int, str]] = []
    for rule in rules:
        if indegree[rule.id] == 0:
            heapq.heappush(
                ready,
                (rule.declaration_index, input_position[rule.id], rule.id),
            )

    ordered_rules: list[LoadedRule] = []
    while ready:
        _, _, rule_id = heapq.heappop(ready)
        ordered_rules.append(rule_by_id[rule_id])

        for dependent_id in dependents[rule_id]:
            indegree[dependent_id] -= 1
            if indegree[dependent_id] == 0:
                dependent = rule_by_id[dependent_id]
                heapq.heappush(
                    ready,
                    (
                        dependent.declaration_index,
                        input_position[dependent_id],
                        dependent_id,
                    ),
                )

    if len(ordered_rules) != len(rules):
        ordered_ids = {rule.id for rule in ordered_rules}
        unresolved_ids = tuple(
            rule.id for rule in rules if rule.id not in ordered_ids
        )
        cycle = _find_cycle(unresolved_ids, dependents)
        raise CircularDependencyError(cycle)

    return tuple(ordered_rules)


def resolve_dependencies(
    rules: tuple[LoadedRule, ...],
) -> DependencyResolution:
    """Resolve rule order and structural conclusion classifications."""
    _validate_rules(rules)
    edges = _build_edges(rules)
    ordered_rules = _topological_order(rules, edges)

    producer_ids_with_dependents = {
        producer_id for producer_id, _ in edges
    }
    intermediate_conclusions = tuple(
        rule.conclusion
        for rule in rules
        if rule.id in producer_ids_with_dependents
    )
    final_conclusions = tuple(
        rule.conclusion
        for rule in rules
        if rule.id not in producer_ids_with_dependents
    )

    return DependencyResolution(
        edges=edges,
        ordered_rules=ordered_rules,
        intermediate_conclusions=intermediate_conclusions,
        final_conclusions=final_conclusions,
    )
