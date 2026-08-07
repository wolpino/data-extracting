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

## Quick test (PR2)

One command — starts an ephemeral server on `:8010` with a temp DB, runs CRUD + validation + activity checks, then stops:

```bash
# from repo root
./backend/scripts/smoke_orders.sh
```

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

Copy env placeholders from the repo root `.env.example`. Do not commit real secrets.
