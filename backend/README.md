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

Orders API (OpenAPI at `/docs`):

- `GET/POST /api/v1/orders`
- `GET/PUT/PATCH/DELETE /api/v1/orders/{id}`

On startup the API creates SQLite tables and seeds a Buffy Summers demo order if missing.

Copy env placeholders from the repo root `.env.example`. Do not commit real secrets.
