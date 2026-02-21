"""Inference endpoints."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas import ApiResponse, BatchFeatures, ok
from ..services import run_and_log

router = APIRouter(prefix="/api/predict", tags=["predict"])


@router.post("", response_model=ApiResponse, summary="Score a single batch")
def predict(features: BatchFeatures, db: Session = Depends(get_db)) -> dict:
    result = run_and_log(db, features.model_dump(), source="api")
    return ok(result, "Prediction served")


@router.post("/batch", response_model=ApiResponse, summary="Score a list of batches")
def predict_batch(
    batches: list[BatchFeatures], db: Session = Depends(get_db)
) -> dict:
    results = [run_and_log(db, b.model_dump(), source="api") for b in batches]
    return ok({"count": len(results), "results": results}, "Batch scored")
