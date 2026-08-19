"""Tests for Part B loading, cleaning, selection, and scaling."""

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from student_academic_advisor.ml_pipeline.data_preparation import (
    FEATURE_COLUMNS,
    DatasetValidationError,
    prepare_student_data,
)


DATASET = Path("data/raw/uci_student_performance/student-por.csv")


def test_prepares_approved_uci_dataset() -> None:
    prepared = prepare_student_data(DATASET)

    assert prepared.audit.original_rows == 649
    assert prepared.audit.cleaned_rows == 649
    assert prepared.audit.duplicate_rows_removed == 0
    assert prepared.audit.missing_rows_removed == 0
    assert tuple(prepared.raw_features.columns) == FEATURE_COLUMNS
    assert "G3" not in prepared.raw_features.columns
    assert prepared.scaled_features.shape == (649, 5)
    assert prepared.scaled_features.mean(axis=0) == pytest.approx(
        np.zeros(5), abs=1e-12
    )
    assert prepared.scaled_features.std(axis=0) == pytest.approx(
        np.ones(5), abs=1e-12
    )


def test_records_explicit_duplicate_and_missing_value_cleaning(
    tmp_path: Path,
) -> None:
    data = pd.DataFrame(
        [
            {"G1": 10, "G2": 11, "absences": 2, "studytime": 2,
             "failures": 0, "G3": 12},
            {"G1": 10, "G2": 11, "absences": 2, "studytime": 2,
             "failures": 0, "G3": 12},
            {"G1": 8, "G2": None, "absences": 4, "studytime": 1,
             "failures": 1, "G3": 9},
            {"G1": 14, "G2": 15, "absences": 0, "studytime": 3,
             "failures": 0, "G3": 15},
        ]
    )
    path = tmp_path / "students.csv"
    data.to_csv(path, sep=";", index=False)

    prepared = prepare_student_data(path)

    assert prepared.audit.original_rows == 4
    assert prepared.audit.duplicate_rows_removed == 1
    assert prepared.audit.missing_rows_removed == 1
    assert prepared.audit.cleaned_rows == 2


def test_rejects_missing_required_column(tmp_path: Path) -> None:
    path = tmp_path / "students.csv"
    pd.DataFrame({"G1": [10, 11]}).to_csv(path, sep=";", index=False)

    with pytest.raises(DatasetValidationError, match="missing required columns"):
        prepare_student_data(path)
