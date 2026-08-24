"""Tests for the executable Part A demonstration and trace report."""

from student_academic_advisor.expert_system.demo import main
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


def _worked_student() -> RawStudentInput:
    return RawStudentInput(
        object_id="POR-0649",
        g1=10,
        g2=11,
        absences=4,
        studytime=1,
        failures=0,
    )


def test_worked_report_is_derived_from_complete_live_trace() -> None:
    student = _worked_student()
    initial_facts = fuzzify_student(student)
    rules = load_knowledge_base()
    result = run_inference(initial_facts, rules)

    report = render_worked_example(student, initial_facts, rules, result)

    assert "# Part A Worked Fuzzy-Inference Example" in report
    assert "Student: **POR-0649**" in report
    assert "**R1 → R2 → R3 → R4 → R5 → R6**" in report
    assert "`persistent_low_performance` = 0.3" in report
    assert "`core_academic_risk` = 0.255" in report
    assert "`compounded_academic_support_need` = `0.2295`" in report
    assert "Maximum: `max(0.15, 0.216667, 0.2295) = 0.2295`" in report
    assert "Final Union: `0.486975`" in report
    assert report.count("### Step ") == 6


def test_cli_saves_the_same_report_that_it_prints(tmp_path, capsys) -> None:
    output_path = tmp_path / "worked.md"

    exit_code = main(["--output", str(output_path)])

    captured = capsys.readouterr().out
    saved = output_path.read_text(encoding="utf-8")
    assert exit_code == 0
    assert saved in captured
    assert f"Report saved to {output_path}." in captured


def test_cli_accepts_another_valid_student(tmp_path) -> None:
    output_path = tmp_path / "custom.md"

    exit_code = main(
        [
            "--student-id",
            "CUSTOM-001",
            "--g1",
            "15",
            "--g2",
            "14",
            "--absences",
            "2",
            "--studytime",
            "3",
            "--failures",
            "0",
            "--output",
            str(output_path),
        ]
    )

    assert exit_code == 0
    assert "Student: **CUSTOM-001**" in output_path.read_text(encoding="utf-8")
