"""Application settings, loaded from environment variables (.env supported)."""
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Where model + reference artifacts are written/read.
    artifacts_dir: Path = Path(__file__).resolve().parent / "artifacts"

    # Prediction log store. Defaults to local SQLite so the service runs
    # standalone; point at a Postgres URL to swap with zero code changes.
    database_url: str = "sqlite:///./monitor.db"

    # CORS origin for the React dashboard (no trailing slash).
    client_url: str = "http://localhost:5173"

    # Drift thresholds. A feature is flagged if EITHER test trips.
    drift_psi_threshold: float = 0.2  # PSI > 0.2 = moderate population shift
    drift_pvalue_threshold: float = 0.05  # KS p < 0.05 = distributions differ

    # Reference sample size persisted at train time for drift comparison.
    reference_sample_size: int = 600

    # Default window (most recent N logged inputs) used for drift checks.
    default_drift_window: int = 200


@lru_cache
def get_settings() -> Settings:
    return Settings()
