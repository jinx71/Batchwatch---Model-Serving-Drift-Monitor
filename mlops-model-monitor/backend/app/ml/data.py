"""Synthetic pharmaceutical batch quality-control dataset.

Each "batch" is described by six in-process parameters. A batch passes QC
when its parameters stay close to validated set-points. Data is fully
synthetic and seeded, so the training reference is reproducible and drift can
be injected deterministically for the monitoring demo.
"""
from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class FeatureSpec:
    name: str
    unit: str
    mean: float  # validated set-point (normal operating regime)
    std: float
    # weight applied to this feature's deviation when scoring batch quality
    weight: float


# Order is fixed and used everywhere (training matrix columns, API payloads).
FEATURE_SPECS: tuple[FeatureSpec, ...] = (
    FeatureSpec("temperature_c", "°C", 25.0, 1.6, 1.0),
    FeatureSpec("pressure_bar", "bar", 1.50, 0.18, 0.8),
    FeatureSpec("ph", "pH", 7.0, 0.35, 1.2),
    FeatureSpec("humidity_pct", "%", 45.0, 7.0, 0.6),
    FeatureSpec("mixing_time_min", "min", 30.0, 4.5, 0.7),
    FeatureSpec("raw_material_purity_pct", "%", 99.0, 0.7, 1.4),
)

FEATURE_NAMES: list[str] = [spec.name for spec in FEATURE_SPECS]

# Decision boundary on the latent quality score (calibrated to the score
# distribution for ~72% pass in the normal regime; a drifted regime, which
# centres far higher, fails most batches). Lower score = higher quality.
_PASS_THRESHOLD = 1.17


def _quality_score(x: np.ndarray) -> np.ndarray:
    """Weighted squared standardized deviation from set-points (lower = better)."""
    score = np.zeros(x.shape[0])
    for i, spec in enumerate(FEATURE_SPECS):
        z = (x[:, i] - spec.mean) / spec.std
        score += spec.weight * z**2
    return score / len(FEATURE_SPECS)


def _labels_from_features(x: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """Apply the QC rule with a little label noise (real QC isn't perfectly separable)."""
    score = _quality_score(x)
    noise = rng.normal(0.0, 0.35, size=x.shape[0])
    return (score + noise < _PASS_THRESHOLD).astype(int)


def sample_features(
    n: int, *, drift: bool = False, seed: int | None = None
) -> np.ndarray:
    """Draw `n` batches of feature vectors.

    With drift=True, shift a subset of parameters to mimic a real process
    excursion / sensor recalibration: hotter, lower purity, higher humidity,
    plus inflated variance. This moves the input distribution away from the
    training reference (detectable by the drift checks) and degrades quality.
    """
    rng = np.random.default_rng(seed)
    cols = []
    for spec in FEATURE_SPECS:
        mean, std = spec.mean, spec.std
        if drift:
            if spec.name == "temperature_c":
                mean, std = spec.mean + 2.6, spec.std * 1.6
            elif spec.name == "raw_material_purity_pct":
                mean, std = spec.mean - 1.3, spec.std * 1.5
            elif spec.name == "humidity_pct":
                mean, std = spec.mean + 9.0, spec.std * 1.4
            elif spec.name == "ph":
                std = spec.std * 1.5
        cols.append(rng.normal(mean, std, size=n))
    return np.column_stack(cols)


def generate_dataset(
    n: int = 4000, seed: int = 7
) -> tuple[np.ndarray, np.ndarray]:
    """Build a labelled training set from the normal operating regime."""
    rng = np.random.default_rng(seed)
    x = sample_features(n, drift=False, seed=seed)
    y = _labels_from_features(x, rng)
    return x, y
