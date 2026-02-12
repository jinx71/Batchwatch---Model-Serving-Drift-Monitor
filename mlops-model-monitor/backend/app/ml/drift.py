"""Data drift detection (hand-rolled, no heavyweight monitoring dependency).

Two complementary per-feature tests compare a *current* window of live inputs
against the *reference* sample frozen at training time:

  - Population Stability Index (PSI): binned mass shift, used as the drift
        decision metric. Rule of thumb: < 0.1 stable | 0.1-0.2 minor |
        > 0.2 significant shift (flagged).
  - Kolmogorov-Smirnov 2-sample test: reported alongside as supporting
        evidence on distribution shape (its p-value is sample-size sensitive,
        so it informs rather than decides).

This is the same signal Evidently AI automates; computing it directly keeps
the image lean and the logic auditable.
"""
import numpy as np
from scipy import stats

from ..config import get_settings

_EPS = 1e-6
_MIN_SAMPLE = 20  # below this, current window is too small to judge


def _psi(reference: np.ndarray, current: np.ndarray, bins: int = 10) -> float:
    """Population Stability Index using reference-quantile bin edges."""
    quantiles = np.linspace(0, 1, bins + 1)
    edges = np.quantile(reference, quantiles)
    edges[0], edges[-1] = -np.inf, np.inf  # absorb out-of-range current values
    edges = np.unique(edges)
    if edges.size < 3:  # degenerate (constant) reference feature
        return 0.0

    ref_counts, _ = np.histogram(reference, bins=edges)
    cur_counts, _ = np.histogram(current, bins=edges)
    ref_pct = np.clip(ref_counts / max(ref_counts.sum(), 1), _EPS, None)
    cur_pct = np.clip(cur_counts / max(cur_counts.sum(), 1), _EPS, None)
    return float(np.sum((cur_pct - ref_pct) * np.log(cur_pct / ref_pct)))


def compute_drift(
    reference: dict[str, list[float]],
    current: dict[str, list[float]],
) -> dict:
    """Return a per-feature drift report plus a dataset-level summary."""
    settings = get_settings()
    feature_names = list(reference.keys())

    sample_size = len(next(iter(current.values()))) if current else 0
    if sample_size < _MIN_SAMPLE:
        return {
            "status": "insufficient_data",
            "sample_size": sample_size,
            "min_sample": _MIN_SAMPLE,
            "dataset_drift": False,
            "n_drifted": 0,
            "drift_share": 0.0,
            "features": [],
        }

    features = []
    n_drifted = 0
    for name in feature_names:
        ref = np.asarray(reference[name], dtype=float)
        cur = np.asarray(current[name], dtype=float)

        ks_stat, ks_p = stats.ks_2samp(ref, cur)
        psi = _psi(ref, cur)
        # PSI is the decision metric: it bins mass and is far less sensitive to
        # window size than a KS p-value (which collapses toward 0 as n grows).
        # The KS statistic/p-value travel alongside as supporting evidence.
        drifted = bool(psi > settings.drift_psi_threshold)
        n_drifted += int(drifted)
        features.append(
            {
                "feature": name,
                "ks_statistic": round(float(ks_stat), 4),
                "ks_pvalue": round(float(ks_p), 4),
                "psi": round(float(psi), 4),
                "drifted": drifted,
                "reference_mean": round(float(ref.mean()), 3),
                "current_mean": round(float(cur.mean()), 3),
            }
        )

    return {
        "status": "ok",
        "sample_size": sample_size,
        "psi_threshold": settings.drift_psi_threshold,
        "pvalue_threshold": settings.drift_pvalue_threshold,
        "n_drifted": n_drifted,
        "drift_share": round(n_drifted / len(feature_names), 3),
        # Dataset-level flag: any feature drifting warrants attention.
        "dataset_drift": n_drifted > 0,
        "features": features,
    }
