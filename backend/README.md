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

## Quick test

Orders CRUD:

```bash
# from repo root
./backend/scripts/smoke_orders.sh
```

Extract + confirm (needs `GEMINI_API_KEY` in `backend/.env`):

```bash
./backend/scripts/smoke_extract.sh
```

Default model: `gemini-3.6-flash` (`GEMINI_MODEL` to override).

Against an already-running API:

```bash
# terminal A
cd backend && uv run uvicorn data_extracting_backend.main:app --reload --port 8000

# terminal B
BASE=http://127.0.0.1:8000 ./backend/scripts/smoke_orders.sh
```

Manual curl cheatsheet (server already up):

```bash
BASE=http://127.0.0.1:8000

curl -s "$BASE/health"
curl -s "$BASE/api/v1/orders" | python3 -m json.tool

curl -s -X POST "$BASE/api/v1/orders" -H 'Content-Type: application/json' \
  -d '{"first_name":"Willow","last_name":"Rosenberg","date_of_birth":"1981-05-01","source_filename":"willow-chart.pdf"}' \
  | python3 -m json.tool

# expect 422
curl -s -w '\n%{http_code}\n' -X POST "$BASE/api/v1/orders" -H 'Content-Type: application/json' \
  -d '{"first_name":"Xander","last_name":"Harris","date_of_birth":"1981-01-01","source_filename":"../evil.pdf"}'
```

Interactive: open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

## Endpoints

Health:

- `GET /health`
- `GET /api/v1/health`

Orders:

- `GET/POST /api/v1/orders`
- `GET/PUT/PATCH/DELETE /api/v1/orders/{id}`

On startup the API creates SQLite tables and seeds a Buffy Summers demo order if missing.

CORS: set `CORS_ORIGINS` to a comma-separated allowlist (default `http://localhost:5173`). Do not use `*` for production demos.

Deploy: see root [render.yaml](../render.yaml) and [README.md](../README.md). On Render, root directory is `backend/` (needs `uv.lock`); build with `uv sync --frozen`, start with `uv run uvicorn …`.

Copy env placeholders from the repo root `.env.example`. Do not commit real secrets.
