"""Post-training cluster profiling, interpretation, plots, and outputs."""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from student_academic_advisor.ml_pipeline.clustering import KMetric
from student_academic_advisor.ml_pipeline.data_preparation import (
    FEATURE_COLUMNS,
    POST_HOC_COLUMN,
    DataAudit,
)


def derive_profile_labels(
    centers_scaled: np.ndarray,
) -> dict[int, str]:
    """Interpret two trained centroids using concern-oriented directions."""
    if centers_scaled.shape != (2, len(FEATURE_COLUMNS)):
        raise ValueError("the approved interpretation expects exactly two clusters")

    concern_directions = np.array([-1.0, -1.0, 1.0, -1.0, 1.0])
    concern_scores = (centers_scaled * concern_directions).mean(axis=1)
    stronger_cluster = int(np.argmin(concern_scores))
    support_cluster = int(np.argmax(concern_scores))
    return {
        stronger_cluster: "stronger_academic_profile",
        support_cluster: "higher_academic_support_need_profile",
    }


def build_cluster_profiles(
    cleaned_data: pd.DataFrame,
    labels: np.ndarray,
    profile_labels: dict[int, str],
) -> pd.DataFrame:
    """Create centroid-style profiles and post-hoc G3 summaries."""
    if len(cleaned_data) != len(labels):
        raise ValueError("cluster labels must match the number of cleaned rows")

    profiled = cleaned_data.copy()
    profiled["cluster"] = labels
    feature_means = profiled.groupby("cluster")[list(FEATURE_COLUMNS)].mean()
    post_hoc = profiled.groupby("cluster")[POST_HOC_COLUMN].agg(
        student_count="count",
        g3_mean="mean",
        g3_median="median",
    )
    profiles = feature_means.join(post_hoc).reset_index()
    profiles.insert(
        1,
        "profile_label",
        profiles["cluster"].map(profile_labels),
    )
    return profiles


def save_evaluation_plot(metrics: tuple[KMetric, ...], path: Path) -> None:
    """Save Elbow and Silhouette charts in one report-ready image."""
    k_values = [metric.k for metric in metrics]
    inertias = [metric.inertia for metric in metrics]
    silhouettes = [metric.silhouette for metric in metrics]

    figure, axes = plt.subplots(1, 2, figsize=(11, 4.5))
    axes[0].plot(k_values, inertias, marker="o")
    axes[0].set(title="Elbow Method", xlabel="Number of clusters (K)", ylabel="Inertia")
    axes[0].grid(alpha=0.3)

    axes[1].plot(k_values, silhouettes, marker="o", color="darkorange")
    axes[1].set(
        title="Silhouette Scores",
        xlabel="Number of clusters (K)",
        ylabel="Silhouette Score",
    )
    axes[1].grid(alpha=0.3)
    figure.tight_layout()
    figure.savefig(path, dpi=180)
    plt.close(figure)


def save_pipeline_outputs(
    output_directory: str | Path,
    cleaned_data: pd.DataFrame,
    labels: np.ndarray,
    metrics: tuple[KMetric, ...],
    selected_k: int,
    profiles: pd.DataFrame,
    profile_labels: dict[int, str],
    audit: DataAudit,
) -> None:
    """Persist reproducible tables, assignments, plot, and JSON summary."""
    output_path = Path(output_directory)
    output_path.mkdir(parents=True, exist_ok=True)

    pd.DataFrame(
        [
            {
                "k": metric.k,
                "inertia": metric.inertia,
                "silhouette": metric.silhouette,
            }
            for metric in metrics
        ]
    ).to_csv(output_path / "k_evaluation.csv", index=False)

    profiles.to_csv(output_path / "cluster_profiles.csv", index=False)
    assignments = cleaned_data[["source_row", POST_HOC_COLUMN]].copy()
    assignments["cluster"] = labels
    assignments["profile_label"] = assignments["cluster"].map(profile_labels)
    assignments.to_csv(output_path / "cluster_assignments.csv", index=False)
    save_evaluation_plot(metrics, output_path / "k_selection.png")

    selected_metric = next(metric for metric in metrics if metric.k == selected_k)
    summary = {
        "selected_k": selected_k,
        "selection_method": "highest silhouette score; smaller K breaks exact ties",
        "selected_silhouette": selected_metric.silhouette,
        "selected_inertia": selected_metric.inertia,
        "random_state": 42,
        "n_init": 20,
        "training_features": list(FEATURE_COLUMNS),
        "post_hoc_only": POST_HOC_COLUMN,
        "data_audit": {
            "original_rows": audit.original_rows,
            "cleaned_rows": audit.cleaned_rows,
            "duplicate_rows_removed": audit.duplicate_rows_removed,
            "missing_rows_removed": audit.missing_rows_removed,
        },
    }
    (output_path / "summary.json").write_text(
        json.dumps(summary, indent=2) + "\n",
        encoding="utf-8",
    )
