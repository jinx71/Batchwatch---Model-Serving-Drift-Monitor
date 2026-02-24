"""Pydantic schemas for request validation and the shared response envelope."""
from typing import Any

from pydantic import BaseModel, Field

from .ml.data import FEATURE_SPECS


def _field(spec) -> Any:
    return Field(..., description=f"{spec.name} ({spec.unit})", examples=[spec.mean])


class BatchFeatures(BaseModel):
    """The six in-process parameters describing one batch."""

    temperature_c: float = _field(FEATURE_SPECS[0])
    pressure_bar: float = _field(FEATURE_SPECS[1])
    ph: float = _field(FEATURE_SPECS[2])
    humidity_pct: float = _field(FEATURE_SPECS[3])
    mixing_time_min: float = _field(FEATURE_SPECS[4])
    raw_material_purity_pct: float = _field(FEATURE_SPECS[5])


class SimulateRequest(BaseModel):
    count: int = Field(50, ge=1, le=2000, description="Number of batches to score")
    drift: bool = Field(
        False, description="Inject a process excursion to shift the input distribution"
    )
    seed: int | None = Field(None, description="Optional seed for reproducible traffic")


class ApiResponse(BaseModel):
    """Uniform envelope returned by every endpoint."""

    success: bool
    data: Any | None = None
    message: str = ""


def ok(data: Any = None, message: str = "") -> dict:
    return {"success": True, "data": data, "message": message}
