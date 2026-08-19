"""End-to-end tests for reproducible Part B output artifacts."""

import json
from pathlib import Path

import pandas as pd

from student_academic_advisor.ml_pipeline.run_pipeline import run_pipeline


DATASET = Path("data/raw/uci_student_performance/student-por.csv")


def test_pipeline_writes_all_required_outputs(tmp_path: Path) -> None:
    selected_k = run_pipeline(DATASET, tmp_path)

    assert selected_k == 2
    expected_files = {
        "k_evaluation.csv",
        "cluster_profiles.csv",
        "cluster_assignments.csv",
        "k_selection.png",
        "summary.json",
    }
    assert {path.name for path in tmp_path.iterdir()} == expected_files

    summary = json.loads((tmp_path / "summary.json").read_text())
    assignments = pd.read_csv(tmp_path / "cluster_assignments.csv")
    profiles = pd.read_csv(tmp_path / "cluster_profiles.csv")
    assert summary["selected_k"] == 2
    assert summary["training_features"] == [
        "G1", "G2", "absences", "studytime", "failures"
    ]
    assert summary["post_hoc_only"] == "G3"
    assert len(assignments) == 649
    assert len(profiles) == 2
