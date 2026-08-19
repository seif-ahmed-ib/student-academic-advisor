"""Tests for per-student Working Memory."""

import pytest

from student_academic_advisor.expert_system.models import Fact, FactOrigin
from student_academic_advisor.expert_system.working_memory import (
    WorkingMemory,
    WorkingMemoryError,
)


def _fact(
    attribute: str,
    value: float,
    object_id: str = "S1",
    origin: FactOrigin = FactOrigin.INITIAL,
) -> Fact:
    return Fact(object_id, attribute, value, origin)


def test_stores_initial_and_zero_valued_derived_facts() -> None:
    memory = WorkingMemory((_fact("a", 0.4), _fact("b", 0.0)))

    derived = memory.add_derived_fact("c", 0.0)

    assert derived.origin is FactOrigin.DERIVED
    assert memory.get_fact("c").value == 0.0
    assert [fact.attribute for fact in memory.snapshot()] == ["a", "b", "c"]


def test_fact_values_snapshot_is_read_only() -> None:
    memory = WorkingMemory((_fact("a", 0.4),))
    values = memory.fact_values()

    with pytest.raises(TypeError):
        values["a"] = 0.9  # type: ignore[index]


def test_rejects_duplicate_attribute() -> None:
    with pytest.raises(WorkingMemoryError, match="unique"):
        WorkingMemory((_fact("a", 0.4), _fact("a", 0.6)))


def test_rejects_mixed_students() -> None:
    with pytest.raises(WorkingMemoryError, match="one object_id"):
        WorkingMemory((_fact("a", 0.4, "S1"), _fact("b", 0.6, "S2")))


def test_rejects_derived_fact_as_initial_input() -> None:
    with pytest.raises(WorkingMemoryError, match="INITIAL origin"):
        WorkingMemory((_fact("a", 0.4, origin=FactOrigin.DERIVED),))


def test_does_not_overwrite_existing_fact() -> None:
    memory = WorkingMemory((_fact("a", 0.4),))

    with pytest.raises(WorkingMemoryError, match="already exists"):
        memory.add_derived_fact("a", 0.7)


def test_rejects_empty_initial_fact_set() -> None:
    with pytest.raises(WorkingMemoryError, match="must not be empty"):
        WorkingMemory(())
