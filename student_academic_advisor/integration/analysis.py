"""Compare independent Expert System and K-Means outputs post-hoc."""

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from student_academic_advisor.expert_system.fuzzification import (
    fuzzify_student,
)
from student_academic_advisor.expert_system.inference_engine import (
    run_inference,
)
from student_academic_advisor.expert_system.raw_input import RawStudentInput
from student_academic_advisor.expert_system.validation import (
    load_knowledge_base,
)
from student_academic_advisor.ml_pipeline.data_preparation import (
    FEATURE_COLUMNS,
    prepare_student_data,
)


FINAL_CONCLUSIONS = (
    "attendance_based_support_need",
    "emerging_performance_support_need",
    "compounded_academic_support_need",
)
ASSIGNMENT_COLUMNS = ("source_row", "cluster", "profile_label")


class IntegrationValidationError(ValueError):
    """Raised when Part A and Part B records cannot be joined safely."""


@dataclass(frozen=True)
class IntegrationResult:
    """Student-level and cluster-level post-hoc comparison results."""

    student_comparison: pd.DataFrame
    cluster_summary: pd.DataFrame
    g3_maximum_correlation: float
    g3_union_correlation: float


def load_cluster_assignments(
    path: str | Path,
    expected_source_rows: set[int],
) -> pd.DataFrame:
    """Load and validate the approved Part B cluster assignments."""
    try:
        assignments = pd.read_csv(path)
    except (OSError, pd.errors.ParserError) as error:
        raise IntegrationValidationError(
            f"could not load cluster assignments {path}: {error}"
        ) from error

    missing = set(ASSIGNMENT_COLUMNS) - set(assignments.columns)
    if missing:
        missing_text = ", ".join(sorted(missing))
        raise IntegrationValidationError(
            f"cluster assignments are missing columns: {missing_text}"
        )

    assignments = assignments.loc[:, ASSIGNMENT_COLUMNS].copy()
    if assignments.isna().any().any():
        raise IntegrationValidationError(
            "cluster assignments cannot contain missing values"
        )
    if assignments["source_row"].duplicated().any():
        raise IntegrationValidationError(
            "cluster assignments must contain one row per source_row"
        )

    try:
        source_rows = pd.to_numeric(
            assignments["source_row"], errors="raise"
        )
        clusters = pd.to_numeric(assignments["cluster"], errors="raise")
    except (TypeError, ValueError) as error:
        raise IntegrationValidationError(
            "source_row and cluster must contain integer values"
        ) from error

    if not source_rows.mod(1).eq(0).all() or not clusters.mod(1).eq(0).all():
        raise IntegrationValidationError(
            "source_row and cluster must contain integer values"
        )
    assignments["source_row"] = source_rows.astype(int)
    assignments["cluster"] = clusters.astype(int)

    if not assignments["profile_label"].map(
        lambda value: isinstance(value, str) and bool(value.strip())
    ).all():
        raise IntegrationValidationError(
            "profile_label must contain non-empty strings"
        )

    actual_source_rows = set(assignments["source_row"].tolist())
    if actual_source_rows != expected_source_rows:
        missing_rows = sorted(expected_source_rows - actual_source_rows)
        unexpected_rows = sorted(actual_source_rows - expected_source_rows)
        raise IntegrationValidationError(
            "cluster assignments do not match the cleaned dataset; "
            f"missing={missing_rows}, unexpected={unexpected_rows}"
        )

    label_counts = assignments.groupby("cluster")["profile_label"].nunique()
    if not (label_counts == 1).all():
        raise IntegrationValidationError(
            "each cluster must have exactly one profile_label"
        )
    return assignments.sort_values("source_row").reset_index(drop=True)


def _run_student_inference(row: object, rules: tuple) -> dict[str, object]:
    source_row = int(row.source_row)
    object_id = f"POR-{source_row + 1:04d}"
    student = RawStudentInput(
        object_id=object_id,
        g1=int(row.G1),
        g2=int(row.G2),
        absences=int(row.absences),
        studytime=int(row.studytime),
        failures=int(row.failures),
    )
    result = run_inference(fuzzify_student(student), rules)
    final_values = {
        fact.attribute: fact.value for fact in result.final_conclusions
    }
    return {
        "object_id": object_id,
        "source_row": source_row,
        "cluster": int(row.cluster),
        "profile_label": row.profile_label,
        "G1": student.g1,
        "G2": student.g2,
        "absences": student.absences,
        "studytime": student.studytime,
        "failures": student.failures,
        "G3_post_hoc": float(row.G3),
        **final_values,
        "maximum": result.aggregation.maximum,
        "union": result.aggregation.union,
    }


def build_student_comparison(
    dataset_path: str | Path,
    assignments_path: str | Path,
) -> pd.DataFrame:
    """Run Part A for every cleaned record and join approved Part B labels."""
    prepared = prepare_student_data(dataset_path)
    expected_rows = set(prepared.cleaned_data["source_row"].astype(int))
    assignments = load_cluster_assignments(assignments_path, expected_rows)
    joined = prepared.cleaned_data.merge(
        assignments,
        on="source_row",
        how="inner",
        validate="one_to_one",
    ).sort_values("source_row")

    rules = load_knowledge_base()
    rows = [
        _run_student_inference(row, rules)
        for row in joined.itertuples(index=False)
    ]
    return pd.DataFrame(rows)


def build_cluster_summary(comparison: pd.DataFrame) -> pd.DataFrame:
    """Summarize raw profiles and fuzzy conclusions without a cutoff."""
    required = {
        "cluster",
        "profile_label",
        "G3_post_hoc",
        "maximum",
        "union",
        *FEATURE_COLUMNS,
        *FINAL_CONCLUSIONS,
    }
    missing = required - set(comparison.columns)
    if missing:
        raise IntegrationValidationError(
            "student comparison is missing columns: "
            + ", ".join(sorted(missing))
        )

    rows: list[dict[str, object]] = []
    for (cluster, profile_label), group in comparison.groupby(
        ["cluster", "profile_label"], sort=True
    ):
        row: dict[str, object] = {
            "cluster": int(cluster),
            "profile_label": profile_label,
            "student_count": len(group),
        }
        for feature in FEATURE_COLUMNS:
            row[f"{feature}_mean"] = float(group[feature].mean())
        row["g3_mean_post_hoc"] = float(group["G3_post_hoc"].mean())
        row["g3_median_post_hoc"] = float(group["G3_post_hoc"].median())
        for conclusion in FINAL_CONCLUSIONS:
            row[f"{conclusion}_mean_cv"] = float(group[conclusion].mean())
            row[f"{conclusion}_contribution_rate"] = float(
                (group[conclusion] > 0.0).mean()
            )
        row["maximum_mean"] = float(group["maximum"].mean())
        row["maximum_median"] = float(group["maximum"].median())
        row["union_mean"] = float(group["union"].mean())
        row["union_median"] = float(group["union"].median())
        rows.append(row)
    return pd.DataFrame(rows).sort_values("cluster").reset_index(drop=True)


def analyze_integration(
    dataset_path: str | Path,
    assignments_path: str | Path,
) -> IntegrationResult:
    """Run the complete post-hoc Part A / Part B comparison."""
    comparison = build_student_comparison(dataset_path, assignments_path)
    cluster_summary = build_cluster_summary(comparison)
    correlations = comparison[
        ["G3_post_hoc", "maximum", "union"]
    ].corr()
    return IntegrationResult(
        student_comparison=comparison,
        cluster_summary=cluster_summary,
        g3_maximum_correlation=float(
            correlations.loc["G3_post_hoc", "maximum"]
        ),
        g3_union_correlation=float(
            correlations.loc["G3_post_hoc", "union"]
        ),
    )
