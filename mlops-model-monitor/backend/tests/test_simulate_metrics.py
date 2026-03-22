"""Traffic simulation, metrics, and timeline tests."""


def test_simulate_normal_populates_metrics(client):
    sim = client.post("/api/simulate", json={"count": 60, "seed": 1}).json()["data"]
    assert sim["count"] == 60
    assert sim["drift_injected"] is False

    metrics = client.get("/api/monitoring/metrics").json()["data"]
    assert metrics["total"] == 60
    assert metrics["passed"] + metrics["failed"] == 60
    assert metrics["p95_latency_ms"] >= metrics["p50_latency_ms"]
    assert metrics["sources"].get("simulated") == 60


def test_drift_traffic_lowers_pass_rate(client):
    normal = client.post("/api/simulate", json={"count": 200, "seed": 1}).json()["data"]
    drift = client.post(
        "/api/simulate", json={"count": 200, "drift": True, "seed": 2}
    ).json()["data"]
    # A drifted process should be rejected far more often than a normal one.
    assert drift["pass_rate"] < normal["pass_rate"]


def test_metrics_empty_state(client):
    metrics = client.get("/api/monitoring/metrics").json()["data"]
    assert metrics["total"] == 0
    assert metrics["pass_rate"] == 0.0


def test_timeline_points_and_buckets(client):
    client.post("/api/simulate", json={"count": 48, "seed": 3})
    data = client.get("/api/monitoring/timeline?limit=48&buckets=6").json()["data"]
    assert len(data["points"]) == 48
    assert data["points"][0]["index"] == 1
    assert len(data["buckets"]) == 6
    assert all(0.0 <= b["pass_rate"] <= 1.0 for b in data["buckets"])
