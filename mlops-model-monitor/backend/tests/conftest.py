"""Shared pytest fixtures.

Points the app at a throwaway SQLite file (set before any app import so the
engine binds to it) and exposes a session-scoped TestClient. Each test starts
from an empty prediction log.
"""
import os
from pathlib import Path

import pytest

_TEST_DB = Path(__file__).resolve().parent / "test_monitor.db"
os.environ["DATABASE_URL"] = f"sqlite:///{_TEST_DB}"


@pytest.fixture(scope="session")
def client():
    from fastapi.testclient import TestClient

    from app.main import app  # imported here so env is set first

    # Entering the context manager runs lifespan: schema + auto-train + warm.
    with TestClient(app) as c:
        yield c

    if _TEST_DB.exists():
        _TEST_DB.unlink()


@pytest.fixture(autouse=True)
def _clean_logs(client):
    client.delete("/api/monitoring/logs")
    yield


NORMAL_BATCH = {
    "temperature_c": 25.0,
    "pressure_bar": 1.5,
    "ph": 7.0,
    "humidity_pct": 45.0,
    "mixing_time_min": 30.0,
    "raw_material_purity_pct": 99.0,
}
