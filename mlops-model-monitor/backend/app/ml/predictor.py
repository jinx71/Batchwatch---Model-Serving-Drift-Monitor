"""Model loading and inference.

A single Predictor instance is loaded once at startup and reused across
requests (loading joblib per request would dominate latency). Inference is
timed with perf_counter so the dashboard reports real serving latency.
"""
import json
import time
from pathlib import Path

import joblib
import numpy as np

from ..config import get_settings
from .data import FEATURE_NAMES
from .train import METADATA_FILE, MODEL_FILE, REFERENCE_FILE


class Predictor:
    def __init__(self, artifacts_dir: Path | None = None) -> None:
        settings = get_settings()
        self._dir = Path(artifacts_dir) if artifacts_dir else settings.artifacts_dir
        self._pipeline = joblib.load(self._dir / MODEL_FILE)
        self.metadata: dict = json.loads((self._dir / METADATA_FILE).read_text())
        self.reference: dict[str, list[float]] = json.loads(
            (self._dir / REFERENCE_FILE).read_text()
        )

    def predict_one(self, features: dict[str, float]) -> dict:
        """Run inference on a single feature dict and measure latency."""
        row = np.array([[features[name] for name in FEATURE_NAMES]], dtype=float)
        start = time.perf_counter()
        proba_pass = float(self._pipeline.predict_proba(row)[0, 1])
        latency_ms = (time.perf_counter() - start) * 1000.0
        prediction = int(proba_pass >= 0.5)
        return {
            "prediction": prediction,
            "label": "pass" if prediction else "fail",
            "probability": round(proba_pass, 4),
            "latency_ms": round(latency_ms, 3),
        }


_predictor: Predictor | None = None


def get_predictor() -> Predictor:
    """Lazily construct and cache the process-wide Predictor."""
    global _predictor
    if _predictor is None:
        _predictor = Predictor()
    return _predictor


def reset_predictor() -> None:
    """Drop the cached predictor (used by tests after re-training)."""
    global _predictor
    _predictor = None
