# PT Coach — Personal AI Trainer

[![Tests](https://img.shields.io/badge/tests-34%20passed-brightgreen)](./backend/tests)
[![Python](https://img.shields.io/badge/python-3.11-blue)](./backend)
[![React](https://img.shields.io/badge/react-18-61DAFB)](./frontend)
[![Docker](https://img.shields.io/badge/docker-compose-2496ED)](./docker-compose.yml)
[![OpenAI](https://img.shields.io/badge/openai-gpt--4o--mini-412991)](./backend/openai_client.py)
[![License](https://img.shields.io/badge/license-MIT-green)](./LICENSE.md)

An intelligent real-time physical therapy and form coaching system. Runs MoveNet pose detection entirely in the browser (no server GPU needed), streams keypoints to a Flask backend for biomechanical analysis, and delivers personalised GPT-4o-mini feedback within milliseconds.

---

## Architecture

```
Browser (React + TensorFlow.js)
  │  MoveNet pose detection @ 640×480, ~4 fps keypoint stream
  │
  ▼  HTTP POST /api/v1/session/<id>/frame
Flask Backend (Gunicorn)
  │  Biomechanical angle calculations
  │  Redis session + LLM response cache
  │
  ▼  openai v1 SDK → gpt-4o-mini
  LLM Feedback (short ≤20 chars, long ≤120 chars, tone)
  │
  ▼  Redis (session frames, metrics, LLM cache)

AWS (optional) — Terraform in infra/terraform/
  ECS Fargate · ElastiCache · RDS · S3 · Secrets Manager
```

---

## Quickstart (Local Docker)

```bash
# 1. Copy and fill in your OpenAI key
cp .env.example .env
# Edit .env → set OPENAI_API_KEY=sk-...

# 2. Build and start all services
docker compose up --build

# 3. Open the app
open http://localhost:3000

# Services:
#   Frontend  → http://localhost:3000
#   Backend   → http://localhost:5000
#   Redis     → localhost:6379
```

> **Note:** The backend waits for Redis's healthcheck before starting. The frontend waits for the backend healthcheck. No race conditions.

---

## Local Development (without Docker)

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export REDIS_URL=redis://localhost:6379/0
export OPENAI_API_KEY=sk-...
python app.py
```

### Frontend

```bash
cd frontend
npm install
npm run dev          # Vite dev server at http://localhost:5173
                     # /api proxied to http://localhost:5000 automatically
```

---

## API Reference

### `POST /api/v1/session/start`
Start a new coaching session.
```json
// Request
{ "exercise": "squat", "user_id": "alice" }

// Response
{ "session_id": "550e8400-e29b-41d4-a716-446655440000" }
```

### `POST /api/v1/session/<id>/frame`
Send a detected pose frame for analysis.
```json
// Request
{
  "keypoints": [
    { "name": "left_knee", "x": 312.4, "y": 401.1, "score": 0.94 },
    ...
  ]
}

// Response
{
  "ok": true,
  "warnings": ["left_knee_bend_too_far"],
  "short": "Ease up left knee",
  "long": "Your left knee is bending past the safe squat depth. Reduce range of motion.",
  "metrics": { "left_knee": 62.3, "right_knee": 88.1 }
}
```

### `POST /api/v1/session/<id>/chat`
Ask the AI coach a question mid-session.
```json
// Request
{ "text": "Why does my knee hurt?" }

// Response
{ "reply": "Knee pain during squats often indicates..." }
```

### `GET /api/v1/session/<id>/metrics`
Retrieve current session state and latest metrics.

### `GET /health`
Returns `{"status": "ok"}` — used by Docker healthchecks.

---

## Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `OPENAI_API_KEY` | ✅ | — | OpenAI API key |
| `REDIS_URL` | No | `redis://redis:6379/0` | Redis connection string |
| `SESSION_FRAME_CAP` | No | `120` | Max frames stored per session |
| `LLM_CACHE_TTL` | No | `30` | Seconds to cache identical LLM responses |
| `LLM_RATE_LIMIT_PER_MIN` | No | `6` | Max LLM calls per minute |
| `PORT` | No | `5000` | Backend port |

---

## Running Tests

```bash
cd backend
pip install -r requirements.txt
pytest tests/ -v

# 34 tests, ~10s, no Redis or OpenAI required (fully mocked)
```

---

## AWS Deployment (Terraform)

Infrastructure is defined in `infra/terraform/`. Provisions: VPC, ECS Fargate cluster, ECR repositories, ElastiCache Redis, RDS PostgreSQL, S3, Secrets Manager.

```bash
cd infra/terraform
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your values

terraform init \
  -backend-config="bucket=YOUR_STATE_BUCKET" \
  -backend-config="key=pt-coach/terraform.tfstate" \
  -backend-config="region=us-east-1" \
  -backend-config="dynamodb_table=YOUR_LOCK_TABLE"

terraform plan
terraform apply
```

> **Important:** Terraform backend variables cannot use `var.*` references. Pass them via `-backend-config` flags or a `backend.hcl` file (never commit secrets).

---

## Project Structure

```
Personal-AI-Trainer/
├── backend/
│   ├── app.py              # Flask API (session, frame, chat, metrics endpoints)
│   ├── form_analysis.py    # Biomechanical angle computation + fault detection
│   ├── openai_client.py    # OpenAI v1 SDK wrapper with Redis caching + retry
│   ├── redis_client.py     # Session storage, frame buffer, LLM cache
│   ├── config.py           # Environment-variable configuration
│   ├── Dockerfile          # python:3.11-slim + gunicorn --timeout 120
│   ├── requirements.txt
│   └── tests/              # 34 pytest tests (no external deps needed)
├── frontend/
│   ├── src/
│   │   ├── App.jsx                 # Root component, session lifecycle
│   │   ├── components/
│   │   │   ├── CameraPose.jsx      # MoveNet pose detection + canvas render
│   │   │   └── FeedbackPanel.jsx   # Real-time coaching feedback display
│   │   ├── services/api.js         # Axios API client
│   │   └── utils/draw.js           # Keypoint + skeleton canvas drawing
│   ├── Dockerfile          # Multi-stage: Vite build → nginx:1.27-alpine
│   ├── nginx.conf          # SPA fallback + /api proxy to backend
│   └── vite.config.js      # Dev proxy for /api → localhost:5000
├── infra/terraform/        # AWS infrastructure (ECS, RDS, ElastiCache, S3)
├── docker-compose.yml      # Redis healthcheck + service_healthy conditions
└── .env.example
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Pose Detection | TensorFlow.js + MoveNet (SinglePose.Lightning) |
| Frontend | React 18, Vite 5, Axios |
| Backend | Python 3.11, Flask 3, Gunicorn |
| AI / LLM | OpenAI GPT-4o-mini (v1 SDK) |
| Caching | Redis 7 (LLM responses + session data) |
| Infra | Docker Compose (local), AWS ECS Fargate (prod) |
| IaC | Terraform ≥ 1.3, AWS provider ~5.0 |
| Testing | pytest 34 tests, fully mocked |
