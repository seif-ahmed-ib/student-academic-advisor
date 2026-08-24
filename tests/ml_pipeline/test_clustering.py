"""Tests for evidence-based K selection and final clustering."""

from pathlib import Path

import pandas as pd
import pytest

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
)


DATASET = Path("data/raw/uci_student_performance/student-por.csv")


@pytest.fixture(scope="module")
def actual_results():
    prepared = prepare_student_data(DATASET)
    metrics = evaluate_k_candidates(prepared.scaled_features)
    selected_k = select_k_by_silhouette(metrics)
    clustering = fit_final_kmeans(prepared.scaled_features, selected_k)
    return prepared, metrics, clustering


def test_actual_metrics_select_k_two(actual_results) -> None:
    _, metrics, clustering = actual_results
    by_k = {metric.k: metric for metric in metrics}

    assert clustering.selected_k == 2
    assert by_k[2].inertia == pytest.approx(2302.167, abs=0.01)
    assert by_k[2].silhouette == pytest.approx(0.2717, abs=0.0001)
    assert by_k[2].silhouette == max(metric.silhouette for metric in metrics)


def test_final_clusters_are_balanced_and_reproducible(actual_results) -> None:
    prepared, _, clustering = actual_results
    counts = pd.Series(clustering.labels).value_counts().sort_values().tolist()
    repeated = fit_final_kmeans(prepared.scaled_features, 2)

    assert counts == [317, 332]
    assert repeated.labels.tolist() == clustering.labels.tolist()


def test_profiles_are_interpreted_only_after_training(actual_results) -> None:
    prepared, _, clustering = actual_results
    labels = derive_profile_labels(clustering.centers_scaled)
    profiles = build_cluster_profiles(
        prepared.cleaned_data,
        clustering.labels,
        labels,
    ).set_index("profile_label")

    stronger = profiles.loc["stronger_academic_profile"]
    support = profiles.loc["higher_academic_support_need_profile"]
    assert stronger["G1"] == pytest.approx(13.380, abs=0.001)
    assert stronger["G2"] == pytest.approx(13.593, abs=0.001)
    assert support["G1"] == pytest.approx(9.325, abs=0.001)
    assert support["G2"] == pytest.approx(9.451, abs=0.001)
    assert stronger["g3_mean"] == pytest.approx(14.033, abs=0.001)
    assert support["g3_mean"] == pytest.approx(9.678, abs=0.001)
