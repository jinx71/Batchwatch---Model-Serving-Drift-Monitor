"""ORM models for the monitoring store."""
from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class PredictionLog(Base):
    """One row per served inference.

    Stores the raw feature payload (for drift analysis), the model output,
    confidence, measured latency, and a source tag (api/simulated) so traffic
    origin can be distinguished in the dashboard.
    """

    __tablename__ = "prediction_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, index=True, nullable=False
    )
    # Feature payload as submitted, kept as JSON for per-feature drift checks.
    features: Mapped[dict] = mapped_column(JSON, nullable=False)
    prediction: Mapped[int] = mapped_column(Integer, nullable=False)  # 1 = pass
    label: Mapped[str] = mapped_column(String(16), nullable=False)  # "pass"/"fail"
    probability: Mapped[float] = mapped_column(Float, nullable=False)  # P(pass)
    latency_ms: Mapped[float] = mapped_column(Float, nullable=False)
    source: Mapped[str] = mapped_column(String(16), default="api", nullable=False)
