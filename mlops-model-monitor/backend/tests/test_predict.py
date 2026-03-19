"""Inference + service-health tests."""
from tests.conftest import NORMAL_BATCH


def test_health(client):
    res = client.get("/health")
    assert res.status_code == 200
    body = res.json()
    assert body["success"] is True
    assert body["data"]["status"] == "healthy"


def test_model_card(client):
    data = client.get("/api/monitoring/model").json()["data"]
    assert data["model_type"] == "RandomForestClassifier"
    assert {"accuracy", "f1", "roc_auc"} <= data["metrics"].keys()
    assert len(data["features"]) == 6


def test_predict_envelope_and_fields(client):
    body = client.post("/api/predict", json=NORMAL_BATCH).json()
    assert body["success"] is True
    data = body["data"]
    assert data["label"] in {"pass", "fail"}
    assert 0.0 <= data["probability"] <= 1.0
    assert data["latency_ms"] >= 0.0


def test_predict_validation_error(client):
    bad = dict(NORMAL_BATCH)
    del bad["ph"]  # missing required feature
    assert client.post("/api/predict", json=bad).status_code == 422


def test_predict_batch(client):
    payload = [NORMAL_BATCH, NORMAL_BATCH, NORMAL_BATCH]
    data = client.post("/api/predict/batch", json=payload).json()["data"]
    assert data["count"] == 3
    assert len(data["results"]) == 3
