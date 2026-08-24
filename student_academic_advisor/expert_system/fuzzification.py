"""Approved raw-to-fuzzy mappings for the Student Academic Advisor."""

from student_academic_advisor.expert_system.models import Fact, FactOrigin
from student_academic_advisor.expert_system.raw_input import RawStudentInput


LOW_FIRST_PERIOD_PERFORMANCE = "low_first_period_performance"
LOW_SECOND_PERIOD_PERFORMANCE = "low_second_period_performance"
HIGH_ABSENCE = "high_absence"
LOW_STUDY_TIME = "low_study_time"
HIGH_FAILURE_HISTORY = "high_failure_history"

INITIAL_FACT_ATTRIBUTES = (
    LOW_FIRST_PERIOD_PERFORMANCE,
    LOW_SECOND_PERIOD_PERFORMANCE,
    HIGH_ABSENCE,
    LOW_STUDY_TIME,
    HIGH_FAILURE_HISTORY,
)

_LOW_STUDY_TIME_BY_CODE = {
    1: 1.0,
    2: 0.5,
    3: 0.0,
    4: 0.0,
}


def _low_performance_membership(grade: int) -> float:
    """Calculate the shared approved low-performance membership mapping."""
    if grade <= 9:
        return 1.0
    if grade < 12:
        return (12 - grade) / 3
    return 0.0


def low_first_period_performance(g1: int) -> float:
    """Return low-performance concern membership for the first period."""
    return _low_performance_membership(g1)


def low_second_period_performance(g2: int) -> float:
    """Return low-performance concern membership for the second period."""
    return _low_performance_membership(g2)


def high_absence(absences: int) -> float:
    """Return high-absence concern membership."""
    if absences <= 2:
        return 0.0
    if absences < 10:
        return (absences - 2) / 8
    return 1.0


def low_study_time(studytime: int) -> float:
    """Return low-study-time concern membership for an approved category."""
    return _LOW_STUDY_TIME_BY_CODE[studytime]


def high_failure_history(failures: int) -> float:
    """Return previous-failure concern membership."""
    return failures / 3


def fuzzify_student(student: RawStudentInput) -> tuple[Fact, ...]:
    """Convert one validated raw student record into five initial facts."""
    return (
        Fact(
            object_id=student.object_id,
            attribute=LOW_FIRST_PERIOD_PERFORMANCE,
            value=low_first_period_performance(student.g1),
            origin=FactOrigin.INITIAL,
        ),
        Fact(
            object_id=student.object_id,
            attribute=LOW_SECOND_PERIOD_PERFORMANCE,
            value=low_second_period_performance(student.g2),
            origin=FactOrigin.INITIAL,
        ),
        Fact(
            object_id=student.object_id,
            attribute=HIGH_ABSENCE,
            value=high_absence(student.absences),
            origin=FactOrigin.INITIAL,
        ),
        Fact(
            object_id=student.object_id,
            attribute=LOW_STUDY_TIME,
            value=low_study_time(student.studytime),
            origin=FactOrigin.INITIAL,
        ),
        Fact(
            object_id=student.object_id,
            attribute=HIGH_FAILURE_HISTORY,
            value=high_failure_history(student.failures),
            origin=FactOrigin.INITIAL,
        ),
    )
