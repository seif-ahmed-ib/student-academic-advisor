"""Tests for the expert system's core fact model."""

from dataclasses import FrozenInstanceError

import pytest

from student_academic_advisor.expert_system.models import Fact, FactOrigin


def _make_fact(**overrides: object) -> Fact:
    values = {
        "object_id": "POR-0649",
        "attribute": "high_absence",
        "value": 0.25,
        "origin": FactOrigin.INITIAL,
    }
    values.update(overrides)
    return Fact(**values)  # type: ignore[arg-type]


def test_creates_valid_oav_fact() -> None:
    fact = _make_fact()

    assert fact.object_id == "POR-0649"
    assert fact.attribute == "high_absence"
    assert fact.value == 0.25
    assert fact.origin is FactOrigin.INITIAL


def test_normalizes_integer_membership_to_float() -> None:
    fact = _make_fact(value=1)

    assert fact.value == 1.0
    assert isinstance(fact.value, float)


def test_fact_is_immutable() -> None:
    fact = _make_fact()

    with pytest.raises(FrozenInstanceError):
        fact.value = 0.75  # type: ignore[misc]


@pytest.mark.parametrize("value", [-0.01, 1.01, float("inf"), float("nan")])
def test_rejects_membership_outside_finite_unit_interval(value: float) -> None:
    with pytest.raises(ValueError) as error:
        _make_fact(value=value)

    assert "value" in str(error.value)


@pytest.mark.parametrize("value", [True, "0.5", None])
def test_rejects_non_numeric_membership(value: object) -> None:
    with pytest.raises(TypeError) as error:
        _make_fact(value=value)

    assert "value" in str(error.value)


def test_rejects_non_string_object_id() -> None:
    with pytest.raises(TypeError) as error:
        _make_fact(object_id=649)

    assert "object_id" in str(error.value)


def test_rejects_non_string_attribute() -> None:
    with pytest.raises(TypeError) as error:
        _make_fact(attribute=123)

    assert "attribute" in str(error.value)


def test_rejects_untyped_origin_string() -> None:
    with pytest.raises(TypeError) as error:
        _make_fact(origin="INITIAL")

    assert "origin" in str(error.value)
