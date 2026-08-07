# Backend

FastAPI API served with uvicorn, managed by [uv](https://docs.astral.sh/uv/).

## Setup

```bash
cd backend
uv sync
```

## Run

```bash
cd backend
uv run uvicorn data_extracting_backend.main:app --reload --host 0.0.0.0 --port 8000
```

Health checks:

- `GET /health`
- `GET /api/v1/health`

Copy env placeholders from the repo root `.env.example`. Do not commit real secrets.
