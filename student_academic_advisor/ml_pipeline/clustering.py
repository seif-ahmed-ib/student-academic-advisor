"""K evaluation, evidence-based selection, and final K-Means fitting."""

from dataclasses import dataclass

import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score


RANDOM_STATE = 42
N_INIT = 20
CANDIDATE_K_VALUES = tuple(range(2, 11))


@dataclass(frozen=True)
class KMetric:
    """Inertia and Silhouette evidence for one candidate K."""

    k: int
    inertia: float
    silhouette: float


@dataclass(frozen=True)
class ClusteringResult:
    """Final fitted K-Means model and deterministic assignments."""

    selected_k: int
    labels: np.ndarray
    centers_scaled: np.ndarray
    model: KMeans


def _validate_matrix(features: np.ndarray) -> None:
    if not isinstance(features, np.ndarray) or features.ndim != 2:
        raise TypeError("features must be a two-dimensional NumPy array")
    if features.shape[0] < 3 or features.shape[1] < 1:
        raise ValueError("features must contain at least three rows and one column")
    if not np.isfinite(features).all():
        raise ValueError("features must contain only finite values")


def evaluate_k_candidates(
    features: np.ndarray,
    candidate_k_values: tuple[int, ...] = CANDIDATE_K_VALUES,
) -> tuple[KMetric, ...]:
    """Fit every candidate and calculate Elbow and Silhouette evidence."""
    _validate_matrix(features)
    if not candidate_k_values:
        raise ValueError("candidate K values must not be empty")
    if len(candidate_k_values) != len(set(candidate_k_values)):
        raise ValueError("candidate K values must be unique")

    metrics: list[KMetric] = []
    for k in candidate_k_values:
        if isinstance(k, bool) or not isinstance(k, int):
            raise TypeError("every candidate K must be an integer")
        if not 2 <= k < features.shape[0]:
            raise ValueError("every candidate K must be between 2 and n_samples - 1")

        model = KMeans(
            n_clusters=k,
            random_state=RANDOM_STATE,
            n_init=N_INIT,
        )
        labels = model.fit_predict(features)
        metrics.append(
            KMetric(
                k=k,
                inertia=float(model.inertia_),
                silhouette=float(silhouette_score(features, labels)),
            )
        )
    return tuple(metrics)


def select_k_by_silhouette(metrics: tuple[KMetric, ...]) -> int:
    """Select the highest Silhouette Score, preferring smaller K on a tie."""
    if not metrics:
        raise ValueError("K metrics must not be empty")
    return min(metrics, key=lambda metric: (-metric.silhouette, metric.k)).k


def fit_final_kmeans(features: np.ndarray, selected_k: int) -> ClusteringResult:
    """Fit the final deterministic model after K has been justified."""
    _validate_matrix(features)
    if isinstance(selected_k, bool) or not isinstance(selected_k, int):
        raise TypeError("selected K must be an integer")
    if not 2 <= selected_k < features.shape[0]:
        raise ValueError("selected K must be between 2 and n_samples - 1")

    model = KMeans(
        n_clusters=selected_k,
        random_state=RANDOM_STATE,
        n_init=N_INIT,
    )
    labels = model.fit_predict(features)
    return ClusteringResult(
        selected_k=selected_k,
        labels=labels,
        centers_scaled=model.cluster_centers_,
        model=model,
    )
