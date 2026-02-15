"""Train the batch-QC classifier and persist the serving artifacts.

Run standalone (`python -m app.ml.train`) or let the API auto-train on startup
when artifacts are missing. Three artifacts are written:
  - model.joblib        the fitted sklearn pipeline
  - reference.json      a sample of training features (for drift comparison)
  - metadata.json       model card: type, metrics, feature schema, trained_at
"""
import json
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from ..config import get_settings
from .data import FEATURE_NAMES, FEATURE_SPECS, generate_dataset

MODEL_FILE = "model.joblib"
REFERENCE_FILE = "reference.json"
METADATA_FILE = "metadata.json"


def _build_pipeline() -> Pipeline:
    # Scaler is unnecessary for trees but keeps the pipeline swappable to a
    # linear model later; n_estimators kept modest to keep the artifact small.
    return Pipeline(
        steps=[
            ("scaler", StandardScaler()),
            (
                "clf",
                RandomForestClassifier(
                    n_estimators=120,
                    max_depth=9,
                    min_samples_leaf=12,
                    random_state=7,
                    n_jobs=-1,
                ),
            ),
        ]
    )


def train(artifacts_dir: Path | None = None) -> dict:
    settings = get_settings()
    out = Path(artifacts_dir) if artifacts_dir else settings.artifacts_dir
    out.mkdir(parents=True, exist_ok=True)

    x, y = generate_dataset()
    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=0.2, random_state=7, stratify=y
    )

    pipeline = _build_pipeline()
    pipeline.fit(x_train, y_train)

    proba = pipeline.predict_proba(x_test)[:, 1]
    preds = (proba >= 0.5).astype(int)
    metrics = {
        "accuracy": round(float(accuracy_score(y_test, preds)), 4),
        "f1": round(float(f1_score(y_test, preds)), 4),
        "roc_auc": round(float(roc_auc_score(y_test, proba)), 4),
    }

    joblib.dump(pipeline, out / MODEL_FILE)

    # Persist a reference feature sample for drift comparison.
    rng = np.random.default_rng(11)
    idx = rng.choice(
        x_train.shape[0],
        size=min(settings.reference_sample_size, x_train.shape[0]),
        replace=False,
    )
    reference = {name: x_train[idx, i].tolist() for i, name in enumerate(FEATURE_NAMES)}
    (out / REFERENCE_FILE).write_text(json.dumps(reference))

    metadata = {
        "model_name": "batch-qc-classifier",
        "model_type": "RandomForestClassifier",
        "version": "1.0.0",
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "n_train": int(x_train.shape[0]),
        "n_test": int(x_test.shape[0]),
        "train_pass_rate": round(float(y_train.mean()), 4),
        "metrics": metrics,
        "features": [
            {"name": s.name, "unit": s.unit, "set_point": s.mean} for s in FEATURE_SPECS
        ],
        "classes": {"0": "fail", "1": "pass"},
    }
    (out / METADATA_FILE).write_text(json.dumps(metadata, indent=2))
    return metadata


def artifacts_exist(artifacts_dir: Path | None = None) -> bool:
    settings = get_settings()
    out = Path(artifacts_dir) if artifacts_dir else settings.artifacts_dir
    return all((out / f).exists() for f in (MODEL_FILE, REFERENCE_FILE, METADATA_FILE))


if __name__ == "__main__":
    meta = train()
    print(f"Trained {meta['model_name']} v{meta['version']} -> {meta['metrics']}")
