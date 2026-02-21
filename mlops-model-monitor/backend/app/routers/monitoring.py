"""Read-only monitoring endpoints powering the dashboard (+ a log reset)."""
import numpy as np
from fastapi import APIRouter, Depends, Query
from sqlalchemy import delete, func
from sqlalchemy.orm import Session

from ..database import get_db
from ..ml.data import FEATURE_NAMES
from ..ml.drift import compute_drift
from ..ml.predictor import get_predictor
from ..models import PredictionLog
from ..schemas import ApiResponse, ok

router = APIRouter(prefix="/api/monitoring", tags=["monitoring"])


@router.get("/model", response_model=ApiResponse, summary="Model card / metadata")
def model_info() -> dict:
    return ok(get_predictor().metadata, "Model metadata")


@router.get("/metrics", response_model=ApiResponse, summary="Serving metrics summary")
def metrics(db: Session = Depends(get_db)) -> dict:
    total = db.query(func.count(PredictionLog.id)).scalar() or 0
    if total == 0:
        return ok(
            {
                "total": 0,
                "passed": 0,
                "failed": 0,
                "pass_rate": 0.0,
                "avg_latency_ms": 0.0,
                "p50_latency_ms": 0.0,
                "p95_latency_ms": 0.0,
                "sources": {},
            },
            "No predictions logged yet",
        )

    rows = (
        db.query(PredictionLog.prediction, PredictionLog.latency_ms, PredictionLog.source)
        .order_by(PredictionLog.id.desc())
        .limit(10000)
        .all()
    )
    preds = np.array([r[0] for r in rows])
    lat = np.array([r[1] for r in rows], dtype=float)
    sources: dict[str, int] = {}
    for _, _, src in rows:
        sources[src] = sources.get(src, 0) + 1

    passed = int(preds.sum())
    return ok(
        {
            "total": int(total),
            "passed": passed,
            "failed": int(len(preds) - passed),
            "pass_rate": round(float(preds.mean()), 4),
            "avg_latency_ms": round(float(lat.mean()), 3),
            "p50_latency_ms": round(float(np.percentile(lat, 50)), 3),
            "p95_latency_ms": round(float(np.percentile(lat, 95)), 3),
            "sources": sources,
        },
        "Serving metrics",
    )


@router.get("/timeline", response_model=ApiResponse, summary="Recent predictions + buckets")
def timeline(
    limit: int = Query(120, ge=1, le=1000),
    buckets: int = Query(12, ge=2, le=48),
    db: Session = Depends(get_db),
) -> dict:
    rows = (
        db.query(
            PredictionLog.created_at,
            PredictionLog.latency_ms,
            PredictionLog.prediction,
            PredictionLog.label,
            PredictionLog.probability,
            PredictionLog.source,
        )
        .order_by(PredictionLog.id.desc())
        .limit(limit)
        .all()
    )
    rows = list(reversed(rows))  # oldest -> newest for left-to-right charts

    points = [
        {
            "index": i + 1,
            "created_at": r[0].isoformat(),
            "latency_ms": round(float(r[1]), 3),
            "prediction": int(r[2]),
            "label": r[3],
            "probability": float(r[4]),
            "source": r[5],
        }
        for i, r in enumerate(rows)
    ]

    # Bucket the sequence into equal slices to show how the pass/fail mix
    # shifts over recent traffic (a drift burst stands out clearly here).
    bucketed: list[dict] = []
    if points:
        preds = np.array([p["prediction"] for p in points])
        splits = np.array_split(preds, min(buckets, len(preds)))
        cursor = 1
        for b in splits:
            passed = int(b.sum())
            bucketed.append(
                {
                    "bucket": f"{cursor}-{cursor + len(b) - 1}",
                    "passed": passed,
                    "failed": int(len(b) - passed),
                    "pass_rate": round(float(b.mean()), 3),
                }
            )
            cursor += len(b)

    return ok({"points": points, "buckets": bucketed}, "Prediction timeline")


@router.get("/drift", response_model=ApiResponse, summary="Feature drift vs reference")
def drift(
    window: int = Query(200, ge=20, le=2000),
    db: Session = Depends(get_db),
) -> dict:
    rows = (
        db.query(PredictionLog.features)
        .order_by(PredictionLog.id.desc())
        .limit(window)
        .all()
    )
    current: dict[str, list[float]] = {name: [] for name in FEATURE_NAMES}
    for (feats,) in rows:
        if not feats:
            continue
        for name in FEATURE_NAMES:
            if name in feats:
                current[name].append(float(feats[name]))

    report = compute_drift(get_predictor().reference, current)
    return ok(report, "Drift report")


@router.delete("/logs", response_model=ApiResponse, summary="Clear the prediction log")
def clear_logs(db: Session = Depends(get_db)) -> dict:
    db.execute(delete(PredictionLog))
    db.commit()
    return ok(None, "Prediction log cleared")
