"""Per-student Working Memory for initial and derived fuzzy facts."""

from types import MappingProxyType
from typing import Mapping

from student_academic_advisor.expert_system.models import Fact, FactOrigin


class WorkingMemoryError(ValueError):
    """Raised when Working Memory consistency would be violated."""


class WorkingMemory:
    """Hold one student's facts during a single inference run."""

    def __init__(self, initial_facts: tuple[Fact, ...]) -> None:
        if not initial_facts:
            raise WorkingMemoryError("initial facts must not be empty")
        if not all(isinstance(fact, Fact) for fact in initial_facts):
            raise TypeError("initial_facts must be a tuple of Fact objects")

        object_ids = {fact.object_id for fact in initial_facts}
        if len(object_ids) != 1:
            raise WorkingMemoryError(
                "all facts in one inference run must share one object_id"
            )
        if any(fact.origin is not FactOrigin.INITIAL for fact in initial_facts):
            raise WorkingMemoryError("initial facts must have INITIAL origin")

        attributes = [fact.attribute for fact in initial_facts]
        if len(attributes) != len(set(attributes)):
            raise WorkingMemoryError("initial fact attributes must be unique")

        self._object_id = initial_facts[0].object_id
        self._facts = {fact.attribute: fact for fact in initial_facts}

    @property
    def object_id(self) -> str:
        return self._object_id

    def fact_values(self) -> Mapping[str, float]:
        """Return a read-only snapshot of current attribute values."""
        return MappingProxyType(
            {attribute: fact.value for attribute, fact in self._facts.items()}
        )

    def get_fact(self, attribute: str) -> Fact:
        try:
            return self._facts[attribute]
        except KeyError as error:
            raise WorkingMemoryError(
                f"fact {attribute!r} is not available"
            ) from error

    def add_derived_fact(self, attribute: str, value: float) -> Fact:
        """Add one derived fact without replacing any existing fact."""
        if attribute in self._facts:
            raise WorkingMemoryError(
                f"fact {attribute!r} already exists in Working Memory"
            )
        fact = Fact(
            object_id=self._object_id,
            attribute=attribute,
            value=value,
            origin=FactOrigin.DERIVED,
        )
        self._facts[attribute] = fact
        return fact

    def snapshot(self) -> tuple[Fact, ...]:
        """Return facts in their insertion order."""
        return tuple(self._facts.values())
