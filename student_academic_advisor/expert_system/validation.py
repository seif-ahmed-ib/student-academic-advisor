"""Knowledge Base loading and pre-inference structural validation."""

import json
from pathlib import Path
from typing import Any

from student_academic_advisor.expert_system.fuzzification import (
    INITIAL_FACT_ATTRIBUTES,
)
from student_academic_advisor.expert_system.models import (
    ConditionKind,
    ConditionNode,
    LoadedRule,
    RuleSource,
)
from student_academic_advisor.expert_system.rule_parser import (
    ConditionSyntaxError,
    parse_condition,
)


DEFAULT_RULES_PATH = Path(__file__).parent / "knowledge_base" / "rules.json"
_REQUIRED_RULE_FIELDS = frozenset(
    {"id", "condition", "conclusion", "cf", "description"}
)


class KnowledgeBaseValidationError(ValueError):
    """Raised when Knowledge Base data is missing, malformed, or inconsistent."""


def collect_fact_references(condition: ConditionNode) -> tuple[str, ...]:
    """Return referenced fact attributes in first-appearance order."""
    references: list[str] = []
    seen: set[str] = set()

    def visit(node: ConditionNode) -> None:
        if node.kind is ConditionKind.FACT_REF:
            attribute = node.fact_attribute
            if attribute is not None and attribute not in seen:
                seen.add(attribute)
                references.append(attribute)
            return

        for operand in node.operands:
            visit(operand)

    visit(condition)
    return tuple(references)


def _read_json(path: Path) -> Any:
    try:
        source = path.read_text(encoding="utf-8")
    except OSError as error:
        raise KnowledgeBaseValidationError(
            f"could not read Knowledge Base file {path}: {error}"
        ) from error

    try:
        return json.loads(source)
    except json.JSONDecodeError as error:
        raise KnowledgeBaseValidationError(
            f"invalid JSON in Knowledge Base file {path}: "
            f"line {error.lineno}, column {error.colno}"
        ) from error


def _validate_rule_fields(rule_data: dict[str, Any], index: int) -> None:
    actual_fields = set(rule_data)
    missing_fields = _REQUIRED_RULE_FIELDS - actual_fields
    extra_fields = actual_fields - _REQUIRED_RULE_FIELDS

    if missing_fields:
        missing_text = ", ".join(sorted(missing_fields))
        raise KnowledgeBaseValidationError(
            f"rule at declaration index {index} is missing fields: {missing_text}"
        )

    if extra_fields:
        extra_text = ", ".join(sorted(extra_fields))
        raise KnowledgeBaseValidationError(
            f"rule at declaration index {index} has unexpected fields: {extra_text}"
        )


def _load_rule_sources(raw_data: Any) -> tuple[RuleSource, ...]:
    if not isinstance(raw_data, list):
        raise KnowledgeBaseValidationError(
            "Knowledge Base must be a top-level JSON array"
        )
    if not raw_data:
        raise KnowledgeBaseValidationError("Knowledge Base must not be empty")

    sources: list[RuleSource] = []
    seen_ids: set[str] = set()
    seen_conclusions: set[str] = set()

    for index, rule_data in enumerate(raw_data):
        if not isinstance(rule_data, dict):
            raise KnowledgeBaseValidationError(
                f"rule at declaration index {index} must be a JSON object"
            )

        _validate_rule_fields(rule_data, index)

        try:
            source = RuleSource(**rule_data)
        except (TypeError, ValueError) as error:
            raise KnowledgeBaseValidationError(
                f"invalid rule at declaration index {index}: {error}"
            ) from error

        if source.id in seen_ids:
            raise KnowledgeBaseValidationError(
                f"duplicate Rule ID {source.id!r} at declaration index {index}"
            )
        if source.conclusion in seen_conclusions:
            raise KnowledgeBaseValidationError(
                "duplicate conclusion producer for "
                f"{source.conclusion!r} at declaration index {index}"
            )

        seen_ids.add(source.id)
        seen_conclusions.add(source.conclusion)
        sources.append(source)

    return tuple(sources)


def _parse_rules(sources: tuple[RuleSource, ...]) -> tuple[LoadedRule, ...]:
    loaded_rules: list[LoadedRule] = []

    for index, source in enumerate(sources):
        try:
            condition_ast = parse_condition(source.condition)
        except ConditionSyntaxError as error:
            raise KnowledgeBaseValidationError(
                f"invalid condition in rule {source.id!r}: {error}"
            ) from error

        loaded_rules.append(
            LoadedRule(
                id=source.id,
                declaration_index=index,
                condition_source=source.condition,
                condition_ast=condition_ast,
                conclusion=source.conclusion,
                cf=source.cf,
                description=source.description,
            )
        )

    return tuple(loaded_rules)


def _validate_fact_references(rules: tuple[LoadedRule, ...]) -> None:
    initial_attributes = set(INITIAL_FACT_ATTRIBUTES)
    produced_attributes = {rule.conclusion for rule in rules}

    collisions = initial_attributes & produced_attributes
    if collisions:
        collision_text = ", ".join(sorted(collisions))
        raise KnowledgeBaseValidationError(
            "derived conclusions conflict with initial fact names: "
            f"{collision_text}"
        )

    consumed_attributes: set[str] = set()
    known_attributes = initial_attributes | produced_attributes

    for rule in rules:
        references = collect_fact_references(rule.condition_ast)
        unknown_references = set(references) - known_attributes
        if unknown_references:
            unknown_text = ", ".join(sorted(unknown_references))
            raise KnowledgeBaseValidationError(
                f"rule {rule.id!r} references unknown facts: {unknown_text}"
            )
        consumed_attributes.update(references)

    final_conclusions = produced_attributes - consumed_attributes
    if not final_conclusions:
        raise KnowledgeBaseValidationError(
            "Knowledge Base must contain at least one structurally "
            "Final Conclusion"
        )


def load_knowledge_base(
    path: str | Path = DEFAULT_RULES_PATH,
) -> tuple[LoadedRule, ...]:
    """Load, parse, and validate all rules before inference starts."""
    rules_path = Path(path)
    raw_data = _read_json(rules_path)
    sources = _load_rule_sources(raw_data)
    loaded_rules = _parse_rules(sources)
    _validate_fact_references(loaded_rules)
    return loaded_rules
