"""Drift detection tests (unit + API)."""
import numpy as np

from app.ml.drift import compute_drift


def _make(reference_seed: int, current_seed: int, shift: float, n: int = 400):
    rng_ref = np.random.default_rng(reference_seed)
    rng_cur = np.random.default_rng(current_seed)
    reference = {"x": rng_ref.normal(0, 1, n).tolist()}
    current = {"x": rng_cur.normal(shift, 1, n).tolist()}
    return reference, current


def test_no_drift_when_same_distribution():
    reference, current = _make(1, 2, shift=0.0)
    report = compute_drift(reference, current)
    assert report["status"] == "ok"
    assert report["dataset_drift"] is False
    assert report["features"][0]["psi"] < 0.2


def test_drift_detected_on_large_shift():
    reference, current = _make(1, 2, shift=2.0)
    report = compute_drift(reference, current)
    assert report["dataset_drift"] is True
    assert report["features"][0]["drifted"] is True
    assert report["features"][0]["psi"] > 0.2


def test_insufficient_data_status():
    reference, current = _make(1, 2, shift=0.0, n=5)
    report = compute_drift(reference, current)
    assert report["status"] == "insufficient_data"
    assert report["dataset_drift"] is False


def test_api_normal_traffic_no_dataset_drift(client):
    client.post("/api/simulate", json={"count": 200, "seed": 1})
    report = client.get("/api/monitoring/drift?window=200").json()["data"]
    assert report["status"] == "ok"
    assert report["dataset_drift"] is False


def test_api_drift_traffic_flags_shifted_features(client):
    client.post("/api/simulate", json={"count": 200, "drift": True, "seed": 2})
    report = client.get("/api/monitoring/drift?window=200").json()["data"]
    assert report["dataset_drift"] is True
    flagged = {f["feature"] for f in report["features"] if f["drifted"]}
    # The simulator shifts temperature, pH, humidity, and raw-material purity.
    assert {"temperature_c", "humidity_pct", "raw_material_purity_pct"} <= flagged
