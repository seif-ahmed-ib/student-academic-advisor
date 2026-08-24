"""Tests for the post-hoc Part A / Part B integration analysis."""

import json
from pathlib import Path

import pandas as pd
import pytest

from student_academic_advisor.integration.analysis import (
    IntegrationValidationError,
    analyze_integration,
    build_cluster_summary,
    load_cluster_assignments,
)
from student_academic_advisor.integration.run_analysis import run_analysis


DATASET = Path("data/raw/uci_student_performance/student-por.csv")
ASSIGNMENTS = Path("outputs/ml/cluster_assignments.csv")


def test_approved_dataset_integration_results() -> None:
    result = analyze_integration(DATASET, ASSIGNMENTS)
    summary = result.cluster_summary.set_index("cluster")

    assert len(result.student_comparison) == 649
    assert summary.loc[0, "student_count"] == 332
    assert summary.loc[1, "student_count"] == 317
    assert summary.loc[0, "profile_label"] == "stronger_academic_profile"
    assert (
        summary.loc[1, "profile_label"]
        == "higher_academic_support_need_profile"
    )
    assert summary.loc[0, "union_mean"] == pytest.approx(
        0.128029, abs=1e-6
    )
    assert summary.loc[1, "union_mean"] == pytest.approx(
        0.459942, abs=1e-6
    )
    assert summary.loc[1, "maximum_mean"] == pytest.approx(
        0.386468, abs=1e-6
    )
    assert result.g3_maximum_correlation == pytest.approx(
        -0.536862, abs=1e-6
    )
    assert result.g3_union_correlation == pytest.approx(
        -0.536041, abs=1e-6
    )


def test_every_student_has_independent_outputs_and_post_hoc_g3() -> None:
    comparison = analyze_integration(DATASET, ASSIGNMENTS).student_comparison

    assert comparison["object_id"].is_unique
    assert comparison["source_row"].is_unique
    assert comparison["cluster"].nunique() == 2
    assert comparison["G3_post_hoc"].notna().all()
    assert comparison["maximum"].between(0.0, 1.0).all()
    assert comparison["union"].between(0.0, 1.0).all()


def test_contribution_rate_uses_cv_greater_than_zero_without_cutoff() -> None:
    comparison = pd.DataFrame(
        {
            "cluster": [0, 0],
            "profile_label": ["test", "test"],
            "G1": [10, 10],
            "G2": [10, 10],
            "absences": [0, 0],
            "studytime": [2, 2],
            "failures": [0, 0],
            "G3_post_hoc": [10, 10],
            "attendance_based_support_need": [0.0, 0.000001],
            "emerging_performance_support_need": [0.0, 0.0],
            "compounded_academic_support_need": [0.0, 0.0],
            "maximum": [0.0, 0.000001],
            "union": [0.0, 0.000001],
        }
    )

    summary = build_cluster_summary(comparison)

    assert (
        summary.loc[0, "attendance_based_support_need_contribution_rate"]
        == 0.5
    )


def test_rejects_assignment_rows_that_do_not_match_dataset() -> None:
    with pytest.raises(
        IntegrationValidationError,
        match="do not match the cleaned dataset",
    ):
        load_cluster_assignments(ASSIGNMENTS, {0, 1})


def test_rejects_fractional_assignment_identifiers(tmp_path: Path) -> None:
    assignments = pd.DataFrame(
        {
            "source_row": [0.5],
            "cluster": [0],
            "profile_label": ["test_profile"],
        }
    )
    path = tmp_path / "assignments.csv"
    assignments.to_csv(path, index=False)

    with pytest.raises(
        IntegrationValidationError,
        match="must contain integer values",
    ):
        load_cluster_assignments(path, {0})


def test_run_analysis_saves_reproducible_artifacts(tmp_path: Path) -> None:
    output = tmp_path / "outputs"
    report = tmp_path / "integration.md"

    run_analysis(DATASET, ASSIGNMENTS, output, report)

    assert {path.name for path in output.iterdir()} == {
        "student_level_comparison.csv",
        "cluster_expert_summary.csv",
        "summary.json",
        "mean_conclusion_cv_by_cluster.png",
    }
    metadata = json.loads(
        (output / "summary.json").read_text(encoding="utf-8")
    )
    assert metadata["student_count"] == 649
    assert metadata["part_a_used_for_kmeans_training"] is False
    assert metadata["clusters_treated_as_ground_truth"] is False
    assert report.is_file()
    assert "Status: **Proposed for approval**" in report.read_text(
        encoding="utf-8"
    )
