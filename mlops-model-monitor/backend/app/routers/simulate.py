"""Traffic generator: populate the monitor with normal or drifted predictions."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..ml.data import FEATURE_NAMES, sample_features
from ..schemas import ApiResponse, SimulateRequest, ok
from ..services import run_and_log

router = APIRouter(prefix="/api/simulate", tags=["simulate"])


@router.post("", response_model=ApiResponse, summary="Generate inference traffic")
def simulate(req: SimulateRequest, db: Session = Depends(get_db)) -> dict:
    x = sample_features(req.count, drift=req.drift, seed=req.seed)
    source = "drift" if req.drift else "simulated"

    passed = 0
    total_latency = 0.0
    for row in x:
        features = {name: float(row[i]) for i, name in enumerate(FEATURE_NAMES)}
        result = run_and_log(db, features, source=source)
        passed += result["prediction"]
        total_latency += result["latency_ms"]

    return ok(
        {
            "count": req.count,
            "drift_injected": req.drift,
            "pass_rate": round(passed / req.count, 4),
            "avg_latency_ms": round(total_latency / req.count, 3),
        },
        f"Generated {req.count} {'drifted' if req.drift else 'normal'} predictions",
    )
