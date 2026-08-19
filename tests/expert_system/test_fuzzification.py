"""Tests for the five approved membership functions and fuzzification."""

import csv
from pathlib import Path

import pytest

from student_academic_advisor.expert_system.fuzzification import (
    HIGH_ABSENCE,
    HIGH_FAILURE_HISTORY,
    INITIAL_FACT_ATTRIBUTES,
    LOW_FIRST_PERIOD_PERFORMANCE,
    LOW_SECOND_PERIOD_PERFORMANCE,
    LOW_STUDY_TIME,
    fuzzify_student,
    high_absence,
    high_failure_history,
    low_first_period_performance,
    low_second_period_performance,
    low_study_time,
)
from student_academic_advisor.expert_system.models import FactOrigin
from student_academic_advisor.expert_system.raw_input import RawStudentInput


@pytest.mark.parametrize(
    ("grade", "expected"),
    [
        (0, 1.0),
        (9, 1.0),
        (10, 2 / 3),
        (11, 1 / 3),
        (12, 0.0),
        (20, 0.0),
    ],
)
def test_low_first_period_performance_boundaries(
    grade: int,
    expected: float,
) -> None:
    assert low_first_period_performance(grade) == pytest.approx(expected)


@pytest.mark.parametrize(
    ("grade", "expected"),
    [
        (0, 1.0),
        (9, 1.0),
        (10, 2 / 3),
        (11, 1 / 3),
        (12, 0.0),
        (20, 0.0),
    ],
)
def test_low_second_period_performance_boundaries(
    grade: int,
    expected: float,
) -> None:
    assert low_second_period_performance(grade) == pytest.approx(expected)


@pytest.mark.parametrize(
    ("absences", "expected"),
    [
        (0, 0.0),
        (2, 0.0),
        (4, 0.25),
        (6, 0.5),
        (8, 0.75),
        (10, 1.0),
        (93, 1.0),
    ],
)
def test_high_absence_boundaries(absences: int, expected: float) -> None:
    assert high_absence(absences) == pytest.approx(expected)


@pytest.mark.parametrize(
    ("studytime", "expected"),
    [(1, 1.0), (2, 0.5), (3, 0.0), (4, 0.0)],
)
def test_low_study_time_lookup(studytime: int, expected: float) -> None:
    assert low_study_time(studytime) == pytest.approx(expected)


@pytest.mark.parametrize(
    ("failures", "expected"),
    [(0, 0.0), (1, 1 / 3), (2, 2 / 3), (3, 1.0)],
)
def test_high_failure_history_mapping(failures: int, expected: float) -> None:
    assert high_failure_history(failures) == pytest.approx(expected)


def test_fuzzifies_por_0649_without_early_rounding() -> None:
    student = RawStudentInput(
        object_id="POR-0649",
        g1=10,
        g2=11,
        absences=4,
        studytime=1,
        failures=0,
    )

    facts = fuzzify_student(student)
    values = {fact.attribute: fact.value for fact in facts}

    assert len(facts) == 5
    assert tuple(fact.attribute for fact in facts) == INITIAL_FACT_ATTRIBUTES
    assert values[LOW_FIRST_PERIOD_PERFORMANCE] == pytest.approx(2 / 3)
    assert values[LOW_SECOND_PERIOD_PERFORMANCE] == pytest.approx(1 / 3)
    assert values[HIGH_ABSENCE] == pytest.approx(0.25)
    assert values[LOW_STUDY_TIME] == pytest.approx(1.0)
    assert values[HIGH_FAILURE_HISTORY] == pytest.approx(0.0)
    assert all(fact.object_id == "POR-0649" for fact in facts)
    assert all(fact.origin is FactOrigin.INITIAL for fact in facts)


def test_zero_valued_initial_facts_are_preserved() -> None:
    student = RawStudentInput(
        object_id="ZERO-CHECK",
        g1=20,
        g2=20,
        absences=0,
        studytime=4,
        failures=0,
    )

    facts = fuzzify_student(student)

    assert len(facts) == 5
    assert all(fact.value == 0.0 for fact in facts)


def test_all_approved_dataset_rows_produce_valid_initial_facts() -> None:
    dataset_path = (
        Path(__file__).resolve().parents[2]
        / "data"
        / "raw"
        / "uci_student_performance"
        / "student-por.csv"
    )
    coverage = {
        attribute: {"zero": 0, "partial": 0, "one": 0}
        for attribute in INITIAL_FACT_ATTRIBUTES
    }

    row_count = 0
    with dataset_path.open(encoding="utf-8", newline="") as dataset_file:
        reader = csv.DictReader(dataset_file, delimiter=";")
        for row_count, row in enumerate(reader, start=1):
            student = RawStudentInput(
                object_id=f"POR-{row_count:04d}",
                g1=int(row["G1"]),
                g2=int(row["G2"]),
                absences=int(row["absences"]),
                studytime=int(row["studytime"]),
                failures=int(row["failures"]),
            )
            facts = fuzzify_student(student)

            assert len(facts) == 5
            assert tuple(fact.attribute for fact in facts) == INITIAL_FACT_ATTRIBUTES
            assert all(0.0 <= fact.value <= 1.0 for fact in facts)
            assert all(fact.object_id == student.object_id for fact in facts)
            assert all(fact.origin is FactOrigin.INITIAL for fact in facts)

            for fact in facts:
                if fact.value == 0.0:
                    coverage[fact.attribute]["zero"] += 1
                elif fact.value == 1.0:
                    coverage[fact.attribute]["one"] += 1
                else:
                    coverage[fact.attribute]["partial"] += 1

    assert row_count == 649
    assert coverage == {
        LOW_FIRST_PERIOD_PERFORMANCE: {
            "zero": 306,
            "partial": 186,
            "one": 157,
        },
        LOW_SECOND_PERIOD_PERFORMANCE: {
            "zero": 318,
            "partial": 186,
            "one": 145,
        },
        HIGH_ABSENCE: {"zero": 366, "partial": 213, "one": 70},
        LOW_STUDY_TIME: {"zero": 132, "partial": 305, "one": 212},
        HIGH_FAILURE_HISTORY: {"zero": 549, "partial": 86, "one": 14},
    }
