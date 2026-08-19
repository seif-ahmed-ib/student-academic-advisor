"""Command-line entry point for the reproducible K-Means pipeline."""

import argparse
from pathlib import Path

from student_academic_advisor.ml_pipeline.clustering import (
    evaluate_k_candidates,
    fit_final_kmeans,
    select_k_by_silhouette,
)
from student_academic_advisor.ml_pipeline.data_preparation import (
    prepare_student_data,
)
from student_academic_advisor.ml_pipeline.reporting import (
    build_cluster_profiles,
    derive_profile_labels,
    save_pipeline_outputs,
)


DEFAULT_DATASET = Path("data/raw/uci_student_performance/student-por.csv")
DEFAULT_OUTPUT_DIRECTORY = Path("outputs/ml")


def run_pipeline(dataset: str | Path, output_directory: str | Path) -> int:
    """Run all Part B stages and return the evidence-selected K."""
    prepared = prepare_student_data(dataset)
    metrics = evaluate_k_candidates(prepared.scaled_features)
    selected_k = select_k_by_silhouette(metrics)
    clustering = fit_final_kmeans(prepared.scaled_features, selected_k)
    profile_labels = derive_profile_labels(clustering.centers_scaled)
    profiles = build_cluster_profiles(
        prepared.cleaned_data,
        clustering.labels,
        profile_labels,
    )
    save_pipeline_outputs(
        output_directory=output_directory,
        cleaned_data=prepared.cleaned_data,
        labels=clustering.labels,
        metrics=metrics,
        selected_k=selected_k,
        profiles=profiles,
        profile_labels=profile_labels,
        audit=prepared.audit,
    )
    return selected_k


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Student Advisor K-Means")
    parser.add_argument("--data", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_DIRECTORY)
    arguments = parser.parse_args()

    selected_k = run_pipeline(arguments.data, arguments.output)
    print(f"K-Means pipeline completed successfully with K={selected_k}.")
    print(f"Outputs saved to {arguments.output}.")


if __name__ == "__main__":
    main()
