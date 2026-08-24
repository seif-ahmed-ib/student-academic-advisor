"""Dataset loading, cleaning, feature selection, and scaling."""

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler


FEATURE_COLUMNS = ("G1", "G2", "absences", "studytime", "failures")
POST_HOC_COLUMN = "G3"
REQUIRED_COLUMNS = FEATURE_COLUMNS + (POST_HOC_COLUMN,)


class DatasetValidationError(ValueError):
    """Raised when the student dataset cannot support the approved pipeline."""


@dataclass(frozen=True)
class DataAudit:
    """Observable cleaning decisions for one loaded dataset."""

    original_rows: int
    cleaned_rows: int
    duplicate_rows_removed: int
    missing_rows_removed: int
    selected_features: tuple[str, ...]


@dataclass(frozen=True)
class PreparedData:
    """Clean raw records plus independently standardized ML features."""

    cleaned_data: pd.DataFrame
    raw_features: pd.DataFrame
    scaled_features: np.ndarray
    scaler: StandardScaler
    audit: DataAudit


def prepare_student_data(path: str | Path) -> PreparedData:
    """Load the UCI file and prepare the approved K-Means feature matrix."""
    dataset_path = Path(path)
    try:
        data = pd.read_csv(dataset_path, sep=";")
    except (OSError, pd.errors.ParserError) as error:
        raise DatasetValidationError(
            f"could not load student dataset {dataset_path}: {error}"
        ) from error

    missing_columns = set(REQUIRED_COLUMNS) - set(data.columns)
    if missing_columns:
        missing_text = ", ".join(sorted(missing_columns))
        raise DatasetValidationError(
            f"dataset is missing required columns: {missing_text}"
        )

    original_rows = len(data)
    data = data.copy()
    data.insert(0, "source_row", data.index)

    duplicate_mask = data.drop(columns="source_row").duplicated(keep="first")
    duplicate_rows_removed = int(duplicate_mask.sum())
    data = data.loc[~duplicate_mask].copy()

    try:
        for column in REQUIRED_COLUMNS:
            data[column] = pd.to_numeric(data[column], errors="raise")
    except (TypeError, ValueError) as error:
        raise DatasetValidationError(
            "selected features and G3 must contain numeric values"
        ) from error

    missing_mask = data.loc[:, REQUIRED_COLUMNS].isna().any(axis=1)
    missing_rows_removed = int(missing_mask.sum())
    data = data.loc[~missing_mask].reset_index(drop=True)
    if len(data) < 2:
        raise DatasetValidationError(
            "at least two complete student records are required"
        )

    raw_features = data.loc[:, FEATURE_COLUMNS].copy()
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(raw_features)

    return PreparedData(
        cleaned_data=data,
        raw_features=raw_features,
        scaled_features=scaled_features,
        scaler=scaler,
        audit=DataAudit(
            original_rows=original_rows,
            cleaned_rows=len(data),
            duplicate_rows_removed=duplicate_rows_removed,
            missing_rows_removed=missing_rows_removed,
            selected_features=FEATURE_COLUMNS,
        ),
    )
