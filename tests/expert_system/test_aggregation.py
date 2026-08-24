"""Tests for final-conclusion Maximum and fuzzy Union aggregation."""

import pytest

from student_academic_advisor.expert_system.aggregation import (
    aggregate_final_conclusions,
)


def test_calculates_maximum_and_repeated_fuzzy_union() -> None:
    result = aggregate_final_conclusions((0.15, 0.2, 0.25))

    expected_union = 1.0 - ((1.0 - 0.15) * (1.0 - 0.2) * (1.0 - 0.25))
    assert result.inputs == (0.15, 0.2, 0.25)
    assert result.maximum == pytest.approx(0.25)
    assert result.union == pytest.approx(expected_union)


def test_preserves_zero_inputs() -> None:
    result = aggregate_final_conclusions((0.0, 0.0))

    assert result.maximum == 0.0
    assert result.union == 0.0


@pytest.mark.parametrize(
    "values",
    [(), (True,), (-0.1,), (1.1,), (float("inf"),)],
)
def test_rejects_invalid_aggregation_inputs(values: tuple[object, ...]) -> None:
    with pytest.raises((TypeError, ValueError)):
        aggregate_final_conclusions(values)  # type: ignore[arg-type]
