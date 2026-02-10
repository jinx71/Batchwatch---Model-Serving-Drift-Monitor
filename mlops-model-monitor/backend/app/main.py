"""FastAPI application entrypoint.

On startup it ensures the DB schema exists and that model artifacts are
present (auto-training if the container/dev machine has none yet), then warms
the predictor so the first real request isn't penalised by cold loading.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .database import init_db
from .ml.predictor import get_predictor
from .ml.train import artifacts_exist, train
from .routers import monitoring, predict, simulate
from .schemas import ok

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    if not artifacts_exist():
        train()
    get_predictor()  # warm the model into memory
    yield


app = FastAPI(
    title="MLOps Model Monitor — Batch QC",
    description=(
        "Serves a pharmaceutical batch quality-control classifier and monitors "
        "serving latency, prediction distribution, and input data drift."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.client_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(predict.router)
app.include_router(simulate.router)
app.include_router(monitoring.router)


@app.get("/health", tags=["health"], summary="Liveness probe")
def health() -> dict:
    return ok({"status": "healthy"}, "Service is up")
