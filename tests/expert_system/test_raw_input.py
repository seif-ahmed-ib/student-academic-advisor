"""Tests for validated raw student input."""

from dataclasses import FrozenInstanceError

import pytest

from student_academic_advisor.expert_system.raw_input import RawStudentInput


def _make_input(**overrides: object) -> RawStudentInput:
    values = {
        "object_id": "POR-0649",
        "g1": 10,
        "g2": 11,
        "absences": 4,
        "studytime": 1,
        "failures": 0,
    }
    values.update(overrides)
    return RawStudentInput(**values)  # type: ignore[arg-type]


def test_creates_valid_raw_student_input() -> None:
    student = _make_input()

    assert student.object_id == "POR-0649"
    assert student.g1 == 10
    assert student.g2 == 11
    assert student.absences == 4
    assert student.studytime == 1
    assert student.failures == 0


def test_raw_student_input_is_immutable_after_validation() -> None:
    student = _make_input()

    with pytest.raises(FrozenInstanceError):
        student.g1 = 21  # type: ignore[misc]


@pytest.mark.parametrize(
    ("field_name", "value"),
    [
        ("g1", 0),
        ("g1", 20),
        ("g2", 0),
        ("g2", 20),
        ("absences", 0),
        ("absences", 93),
        ("studytime", 1),
        ("studytime", 2),
        ("studytime", 3),
        ("studytime", 4),
        ("failures", 0),
        ("failures", 1),
        ("failures", 2),
        ("failures", 3),
    ],
)
def test_accepts_every_approved_boundary_or_discrete_value(
    field_name: str,
    value: int,
) -> None:
    student = _make_input(**{field_name: value})

    assert getattr(student, field_name) == value


@pytest.mark.parametrize(
    ("field_name", "value"),
    [
        ("g1", -1),
        ("g1", 21),
        ("g2", -1),
        ("g2", 21),
        ("absences", -1),
        ("absences", 94),
        ("studytime", 0),
        ("studytime", 5),
        ("failures", -1),
        ("failures", 4),
    ],
)
def test_rejects_values_outside_the_approved_domain(
    field_name: str,
    value: int,
) -> None:
    with pytest.raises(ValueError) as error:
        _make_input(**{field_name: value})

    message = str(error.value)
    assert field_name in message
    assert repr(value) in message


@pytest.mark.parametrize(
    ("field_name", "value"),
    [
        ("g1", 10.0),
        ("g2", "11"),
        ("absences", None),
        ("studytime", True),
        ("failures", False),
    ],
)
def test_rejects_non_integer_numeric_fields(
    field_name: str,
    value: object,
) -> None:
    with pytest.raises(TypeError) as error:
        _make_input(**{field_name: value})

    message = str(error.value)
    assert field_name in message
    assert repr(value) in message


def test_rejects_non_string_object_id() -> None:
    with pytest.raises(TypeError) as error:
        _make_input(object_id=649)

    message = str(error.value)
    assert "object_id" in message
    assert "649" in message


def test_requires_every_field() -> None:
    with pytest.raises(TypeError):
        RawStudentInput(
            object_id="POR-0649",
            g1=10,
            g2=11,
            absences=4,
            studytime=1,
        )  # type: ignore[call-arg]
