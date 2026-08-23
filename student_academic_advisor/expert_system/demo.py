"""Command-line demonstration for one complete Part A inference run."""

import argparse
from pathlib import Path
from typing import Sequence

from student_academic_advisor.expert_system.fuzzification import (
    fuzzify_student,
)
from student_academic_advisor.expert_system.inference_engine import (
    run_inference,
)
from student_academic_advisor.expert_system.raw_input import RawStudentInput
from student_academic_advisor.expert_system.trace_report import (
    render_worked_example,
)
from student_academic_advisor.expert_system.validation import (
    load_knowledge_base,
)


DEFAULT_OUTPUT_PATH = Path("outputs/part-a/worked_example_por_0649.md")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run and explain one Student Academic Advisor inference.",
    )
    parser.add_argument("--student-id", default="POR-0649")
    parser.add_argument("--g1", type=int, default=10)
    parser.add_argument("--g2", type=int, default=11)
    parser.add_argument("--absences", type=int, default=4)
    parser.add_argument("--studytime", type=int, default=1)
    parser.add_argument("--failures", type=int, default=0)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the validated pipeline, print its trace, and save Markdown."""
    arguments = _parser().parse_args(argv)
    student = RawStudentInput(
        object_id=arguments.student_id,
        g1=arguments.g1,
        g2=arguments.g2,
        absences=arguments.absences,
        studytime=arguments.studytime,
        failures=arguments.failures,
    )
    initial_facts = fuzzify_student(student)
    rules = load_knowledge_base()
    result = run_inference(initial_facts, rules)
    report = render_worked_example(student, initial_facts, rules, result)

    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(report, encoding="utf-8")
    print(report)
    print(f"Report saved to {arguments.output}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
