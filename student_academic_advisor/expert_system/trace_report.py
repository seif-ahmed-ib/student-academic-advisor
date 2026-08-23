"""Render one real inference run as an explainable Markdown report."""

from collections.abc import Iterable

from student_academic_advisor.expert_system.inference_engine import (
    InferenceResult,
)
from student_academic_advisor.expert_system.models import Fact, LoadedRule
from student_academic_advisor.expert_system.raw_input import RawStudentInput
from student_academic_advisor.expert_system.trace import RuleTraceEntry


def format_value(value: float) -> str:
    """Format a calculated value for display without changing stored precision."""
    formatted = f"{value:.6f}".rstrip("0").rstrip(".")
    return formatted if formatted else "0"


def _yes_no(value: bool) -> str:
    return "Yes" if value else "No"


def _premise_text(entry: RuleTraceEntry) -> str:
    return ", ".join(
        f"`{name}` = {format_value(value)}"
        for name, value in entry.premise_values
    )


def _operator_lines(entry: RuleTraceEntry) -> list[str]:
    if not entry.operator_steps:
        return ["- No composite operator: FV is the referenced fact value."]

    lines: list[str] = []
    for index, step in enumerate(entry.operator_steps, start=1):
        operands = ", ".join(format_value(value) for value in step.operand_values)
        lines.append(
            f"{index}. `{step.operator}({operands}) = "
            f"{format_value(step.result)}`"
        )
    return lines


def _trace_summary_row(entry: RuleTraceEntry) -> str:
    premise_text = _premise_text(entry).replace("|", "\\|")
    return (
        f"| {entry.evaluation_order} | {entry.rule_id} | "
        f"{premise_text} | {format_value(entry.fv)} | "
        f"{format_value(entry.cf)} | {format_value(entry.cv)} | "
        f"{_yes_no(entry.fired)} | {_yes_no(entry.contributes)} | "
        f"`{entry.conclusion_attribute}` = "
        f"{format_value(entry.conclusion_value)} |"
    )


def _aggregation_lines(result: InferenceResult) -> list[str]:
    values = result.aggregation.inputs
    value_text = ", ".join(format_value(value) for value in values)
    lines = [
        f"- Maximum: `max({value_text}) = "
        f"{format_value(result.aggregation.maximum)}`",
        "- Fuzzy Union uses `U(a, b) = a + b - a × b`:",
    ]

    running = values[0]
    lines.append(f"  1. Start with `{format_value(running)}`.")
    for index, value in enumerate(values[1:], start=2):
        previous = running
        running = previous + value - (previous * value)
        lines.append(
            f"  {index}. `U({format_value(previous)}, "
            f"{format_value(value)}) = {format_value(running)}`"
        )
    lines.append(
        f"- Final Union: `{format_value(result.aggregation.union)}`"
    )
    return lines


def _name_list(values: Iterable[str]) -> str:
    return ", ".join(f"`{value}`" for value in values)


def render_worked_example(
    student: RawStudentInput,
    initial_facts: tuple[Fact, ...],
    rules: tuple[LoadedRule, ...],
    result: InferenceResult,
) -> str:
    """Build the complete report from captured runtime objects."""
    rule_by_id = {rule.id: rule for rule in rules}
    lines = [
        "# Part A Worked Fuzzy-Inference Example",
        "",
        "Course: **Basic of AI Programming Skills (DSC 311)**",
        "Project: **Student Academic Advisor**",
        f"Student: **{student.object_id}**",
        "",
        "> All values below are rendered from the validated input, the loaded "
        "Knowledge Base, and the live inference trace. Calculations retain full "
        "precision internally and are rounded only for display.",
        "",
        "## 1. Raw Input",
        "",
        "| Field | Value |",
        "|---|---:|",
        f"| G1 | {student.g1} |",
        f"| G2 | {student.g2} |",
        f"| Absences | {student.absences} |",
        f"| Study time code | {student.studytime} |",
        f"| Previous failures | {student.failures} |",
        "",
        "## 2. Initial O-A-V Fuzzy Facts",
        "",
        "| Object | Attribute | Value | Origin |",
        "|---|---|---:|---|",
    ]

    for fact in initial_facts:
        lines.append(
            f"| {fact.object_id} | `{fact.attribute}` | "
            f"{format_value(fact.value)} | {fact.origin.value} |"
        )

    resolution = result.dependency_resolution
    order_text = " → ".join(rule.id for rule in resolution.ordered_rules)
    edge_text = (
        ", ".join(f"{source} → {target}" for source, target in resolution.edges)
        if resolution.edges
        else "None"
    )
    lines.extend(
        [
            "",
            "## 3. Structural Dependency Resolution",
            "",
            f"- Rule edges: {edge_text}.",
            f"- Deterministic evaluation order: **{order_text}**.",
            "- Intermediate Conclusions: "
            f"{_name_list(resolution.intermediate_conclusions)}.",
            "- Final Conclusions: "
            f"{_name_list(resolution.final_conclusions)}.",
            "",
            "## 4. Live Rule Trace Summary",
            "",
            "A rule is evaluated when its premises are available, fired when "
            "`FV > 0`, and contributes when `CV > 0`. No configurable firing "
            "threshold is used.",
            "",
            "| Order | Rule | Premise values | FV | CF | CV | Fired | "
            "Contributes | Derived conclusion |",
            "|---:|---|---|---:|---:|---:|---|---|---|",
        ]
    )
    lines.extend(_trace_summary_row(entry) for entry in result.trace.entries)

    lines.extend(["", "## 5. Detailed FV, CF, and CV Calculations", ""])
    for entry in result.trace.entries:
        rule = rule_by_id[entry.rule_id]
        lines.extend(
            [
                f"### Step {entry.evaluation_order} — {entry.rule_id}",
                "",
                f"- Description: {rule.description}",
                f"- Condition: `{entry.condition_text}`",
                f"- Premises: {_premise_text(entry)}",
                "- Operator calculations:",
            ]
        )
        lines.extend(_operator_lines(entry))
        lines.extend(
            [
                f"- Activation degree / FV: `{format_value(entry.fv)}`",
                f"- Author-assigned CF: `{format_value(entry.cf)}`",
                f"- CV: `FV × CF = {format_value(entry.fv)} × "
                f"{format_value(entry.cf)} = {format_value(entry.cv)}`",
                f"- Evaluated: **{_yes_no(entry.evaluated)}**; "
                f"Fired: **{_yes_no(entry.fired)}**; "
                f"Contributes: **{_yes_no(entry.contributes)}**.",
                f"- Conclusion: `{entry.conclusion_attribute}` = "
                f"`{format_value(entry.conclusion_value)}`.",
                "",
            ]
        )

    lines.extend(
        [
            "## 6. Final Conclusions",
            "",
            "| Final conclusion | CV |",
            "|---|---:|",
        ]
    )
    for fact in result.final_conclusions:
        lines.append(f"| `{fact.attribute}` | {format_value(fact.value)} |")

    lines.extend(["", "## 7. Final Knowledge Base Aggregation", ""])
    lines.extend(_aggregation_lines(result))
    lines.extend(
        [
            "",
            "## 8. Interpretation",
            "",
            "The strongest Final Conclusion is the conclusion whose CV equals "
            "the Maximum aggregation result. The Union value summarizes the "
            "combined support across all structurally Final Conclusions; it is "
            "not a replacement for their individual meanings.",
            "",
        ]
    )
    return "\n".join(lines)
