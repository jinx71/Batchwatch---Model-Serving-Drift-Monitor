# BatchWatch — Model Serving & Drift Monitor

An end-to-end **MLOps** project: a trained machine-learning model served behind a
FastAPI inference API, with a real-time monitoring dashboard that tracks **serving
latency, prediction distribution, and input data drift**. Built around a
pharmaceutical batch quality-control model — predicting whether a manufacturing
batch passes QC from its in-process parameters.

The point isn't the model. The point is everything *around* the model: logging
every inference, measuring how it behaves in production, and detecting when the
live data has drifted away from what the model was trained on. That gap — between
*training a model* and *operating one* — is what most junior portfolios skip.

> **AI/ML Portfolio · Project 5 of 10** — targets the *“MLOps practices and model
> monitoring”* requirement. Domain framing reuses 8+ years of GMP pharmaceutical
> engineering experience.

- 🔗 **Live demo:** _add deployment URL_
- 🖼️ **Screenshot:** _add `docs/dashboard.png`_

---

## What it demonstrates

| Capability | Where |
|---|---|
| Serving a trained sklearn model behind a typed REST API | `backend/app/ml/predictor.py`, `routers/predict.py` |
| Logging every prediction (features, output, confidence, latency) | `models.py`, `services.py` |
| **Data drift detection** — PSI + Kolmogorov–Smirnov, from scratch | `backend/app/ml/drift.py` |
| Serving metrics — throughput, p50/p95 latency, class balance | `routers/monitoring.py` |
| A live observability dashboard with polling | `frontend/src/` |
| Reproducible training + model card | `backend/app/ml/train.py` |
| Containerised, one-command run | `docker-compose.yml` |
| Tested (14 pytest cases, unit + API) | `backend/tests/` |

---

## Architecture

```
┌──────────────────────────┐         ┌───────────────────────────────────────┐
│  React + TS dashboard     │  HTTP   │  FastAPI service                        │
│  (Vite, Recharts)         │ ◄─────► │                                         │
│                           │  CORS   │  /api/predict      run + log inference  │
│  • metric readouts        │         │  /api/simulate     generate traffic     │
│  • latency trace          │         │  /api/monitoring/* metrics · drift      │
│  • outcome distribution   │         │            │                            │
│  • per-feature drift bars │         │   ┌────────▼─────────┐   ┌───────────┐  │
│  • traffic controls       │         │   │ Predictor        │   │ Drift     │  │
│  polls every 4s           │         │   │ (RandomForest)   │   │ PSI + KS  │  │
└──────────────────────────┘         │   └────────┬─────────┘   └─────▲─────┘  │
                                      │            │ log               │        │
                                      │      ┌─────▼──────────────────┐│        │
                                      │      │ SQLAlchemy prediction   ││ window │
                                      │      │ log (SQLite → Postgres) │┘        │
                                      │      └─────────────────────────┘         │
                                      │   reference sample (frozen at train time)│
                                      └───────────────────────────────────────┘
```

**Flow:** each `/predict` call runs the model, times the inference, and writes a
row to the prediction log. The dashboard polls the monitoring endpoints, which
aggregate those rows into metrics and compare the most recent feature values
against the training reference to compute drift.

---

## The monitored model

A `RandomForestClassifier` predicting **batch pass / fail** from six in-process
parameters. Data is fully synthetic and seeded, so the training reference is
reproducible and a process excursion (drift) can be injected on demand.

| Feature | Unit | Set-point |
|---|---|---|
| `temperature_c` | °C | 25.0 |
| `pressure_bar` | bar | 1.50 |
| `ph` | pH | 7.0 |
| `humidity_pct` | % | 45.0 |
| `mixing_time_min` | min | 30.0 |
| `raw_material_purity_pct` | % | 99.0 |

Hold-out metrics (from `train.py`): **accuracy ≈ 0.91, F1 ≈ 0.94, ROC-AUC ≈ 0.97**,
~70% pass rate. The model auto-trains on first startup if no artifacts exist, and
is baked into the Docker image at build time.

---

## Drift detection

For each feature, a *current* window of live inputs is compared against the
*reference* sample frozen at training time:

- **Population Stability Index (PSI)** — the **decision metric**. It bins the
  reference into deciles and measures how much probability mass shifted.
  Rule of thumb: `< 0.1` stable · `0.1–0.2` minor · `> 0.2` significant (flagged).
- **Kolmogorov–Smirnov 2-sample test** — reported alongside as supporting
  evidence. Its p-value collapses toward zero as the window grows, so it’s
  sample-size sensitive; it *informs* rather than *decides*.

**Why hand-rolled instead of Evidently AI?** PSI and KS are ~30 lines of SciPy
and NumPy. Implementing them directly keeps the Docker image lean, keeps the
logic auditable, and demonstrates understanding of *how* drift detection works
rather than which library wraps it. Evidently AI is the production-grade tool
that automates exactly this signal — the right next step at scale, noted here
deliberately.

Try it: hit **Send drifted batch** in the dashboard. The injected excursion
(hotter, lower purity, higher humidity) shifts those feature distributions, the
pass rate craters, and the matching features trip the PSI threshold.

---

## Tech stack

**Backend** — Python 3.12 · FastAPI · scikit-learn · SciPy · NumPy ·
SQLAlchemy 2 · joblib · Pydantic v2
**Frontend** — React 18 · TypeScript · Vite · Tailwind CSS · Recharts · Axios
**Infra** — Docker · Docker Compose · nginx · pytest

---

## Project structure

```
mlops-model-monitor/
├─ backend/
│  ├─ app/
│  │  ├─ ml/            data (synthetic) · train · predictor · drift
│  │  ├─ routers/       predict · simulate · monitoring
│  │  ├─ config.py      env-driven settings
│  │  ├─ database.py    engine/session (SQLite → Postgres swappable)
│  │  ├─ models.py      PredictionLog ORM model
│  │  ├─ schemas.py     request validation + response envelope
│  │  ├─ services.py    run-and-log inference
│  │  └─ main.py        app, CORS, startup auto-train
│  ├─ tests/            pytest (unit + API)
│  └─ Dockerfile
├─ frontend/
│  ├─ src/              api · hooks · components · App
│  └─ Dockerfile        multi-stage build → nginx
└─ docker-compose.yml
```

---

## Run it

### Option A — Docker Compose (whole stack)

```bash
docker compose up --build
```

- Dashboard → http://localhost:8080
- API docs (Swagger) → http://localhost:8000/docs

The backend trains the model at build time and persists the prediction log on a
named volume.

### Option B — Run locally

**Backend**

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload          # trains on first start, serves :8000
```

**Frontend** (new terminal)

```bash
cd frontend
npm install
cp .env.example .env                   # VITE_API_URL=http://localhost:8000
npm run dev                            # http://localhost:5173
```

> **CORS / env note:** the backend allows the single origin in `CLIENT_URL`
> (no trailing slash). `VITE_API_URL` is inlined into the bundle at build time,
> so changing it requires a rebuild, not just a restart.

---

## API reference

All responses use the envelope `{ "success": bool, "data": ..., "message": str }`.

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Liveness probe |
| `POST` | `/api/predict` | Score one batch (6 features) → prediction, P(pass), latency |
| `POST` | `/api/predict/batch` | Score a list of batches |
| `POST` | `/api/simulate` | Generate `count` predictions; `drift: true` injects an excursion |
| `GET` | `/api/monitoring/model` | Model card: type, version, metrics, feature schema |
| `GET` | `/api/monitoring/metrics` | Totals, pass rate, avg/p50/p95 latency, source breakdown |
| `GET` | `/api/monitoring/timeline` | Recent predictions + bucketed pass/fail counts |
| `GET` | `/api/monitoring/drift` | Per-feature PSI/KS drift report vs reference |
| `DELETE` | `/api/monitoring/logs` | Clear the prediction log |

Example:

```bash
curl -X POST http://localhost:8000/api/predict -H "Content-Type: application/json" -d '{
  "temperature_c": 25, "pressure_bar": 1.5, "ph": 7.0,
  "humidity_pct": 45, "mixing_time_min": 30, "raw_material_purity_pct": 99
}'
```

---

## Tests

```bash
cd backend && source .venv/bin/activate
pip install -r requirements-dev.txt
pytest -q          # 14 passed
```

Coverage spans the inference envelope and validation, metrics aggregation,
timeline bucketing, and drift detection at both unit level (synthetic
distributions) and API level (normal traffic → no drift; injected drift → the
shifted features flagged).

---

## Design notes

- **SQLite by default, Postgres-ready.** The store is wired through SQLAlchemy
  with a `DATABASE_URL` setting — point it at a Postgres DSN and nothing else
  changes. SQLite keeps the service runnable standalone.
- **DB work runs in sync handlers** so FastAPI executes it in a threadpool rather
  than blocking the event loop with synchronous SQLAlchemy calls.
- **Predictor loaded once** at startup (loading joblib per request would dominate
  latency) and reused across requests.
- **Dashboard is an instrument panel**, not a generic SaaS template:
  deep-slate console, monospace readouts, phosphor-teal signal trace, and
  amber/red status lamps. Responsive to mobile, keyboard-focusable, honours
  `prefers-reduced-motion`.

---

## Interview talking points

- **“What’s the difference between deploying a model and operating one?”** — This
  project *is* the answer: serving is one endpoint; the work is logging,
  latency/throughput SLOs, and drift detection so you know when the model has
  silently gone stale.
- **PSI vs KS** — why PSI is the go/no-go metric (binned, window-size robust) and
  why a KS p-value is misleading as a threshold (it shrinks with sample size).
- **Drift ≠ model decay, but it’s the early warning.** Input drift is observable
  immediately; label-based performance decay only shows up once ground truth
  arrives (in pharma, after lab QC). Monitoring inputs buys lead time.
- **Build-vs-buy** — implemented drift from scratch to show the mechanics; named
  Evidently AI as the production tool that automates it.
- **Swappable storage** — SQLite → Postgres via one env var demonstrates
  separating the interface from the implementation.
- **Domain framing** — pharma batch QC is a real ML use case, and the GMP
  background means I can speak to what “a drifted process” actually means on a
  manufacturing floor.

---

## Roadmap

Part of a 10-project AI/ML portfolio. Remember to update the status table in the
[profile README](https://github.com/jinx71) when this project is marked complete.
