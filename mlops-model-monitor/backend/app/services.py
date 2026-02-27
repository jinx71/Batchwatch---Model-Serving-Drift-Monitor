"""Inference + logging service shared by the predict and simulate routers."""
from sqlalchemy.orm import Session

from .ml.predictor import get_predictor
from .models import PredictionLog


def run_and_log(db: Session, features: dict[str, float], source: str) -> dict:
    """Score one batch, persist the log row, and return the prediction result."""
    result = get_predictor().predict_one(features)
    db.add(
        PredictionLog(
            features=features,
            prediction=result["prediction"],
            label=result["label"],
            probability=result["probability"],
            latency_ms=result["latency_ms"],
            source=source,
        )
    )
    db.commit()
    return result
