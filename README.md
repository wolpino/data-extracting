# data-extracting

GenHealth take-home MVP: upload a patient PDF → Gemini draft (first/last/DOB) → **Confirm** to save an Order → list/edit/delete Orders, with activity logging.

**Demo sentence:** Reviewer can upload a patient document (PDF), see extracted first/last/DOB as an editable draft, confirm to save an Order, and list/edit/delete Orders — with all actions logged.

## Public URLs

| Surface | URL |
|---------|-----|
| UI | _pending Render Static Site_ |
| API | _pending Render Web Service_ |
| API health | `{API}/health` |
| OpenAPI | `{API}/docs` |

Secrets (`GEMINI_API_KEY`, etc.) live only in Render env / local `backend/.env` — never in git.

## Architecture

```text
Browser (Vite React TS)
  └─ VITE_API_BASE_URL ──► FastAPI (uvicorn) ──► Gemini (server-side key)
                              │
                              └─ SQLAlchemy + SQLite (DATABASE_URL)
```

| Piece | Choice |
|-------|--------|
| Backend | Python 3.12, FastAPI, uv (`uv.lock` + `uv sync` on Render) |
| Frontend | Vite + React + TypeScript |
| LLM | Gemini (`GEMINI_MODEL`, default `gemini-3.6-flash`), key server-side only |
| DB | SQLite via SQLAlchemy; `DATABASE_URL` swap-ready for Postgres |
| Deploy | Render Web Service (`backend/`) + Static Site (`frontend/dist`) |
| Auth | None in MVP (accepted take-home risk) |

Confirm-before-save: `POST /api/v1/extract` returns a **draft only**; Orders persist only via `POST /api/v1/orders/confirm` (or manual CRUD with UI confirm dialogs).

Source of truth: [docs/SPEC.md](docs/SPEC.md) · [docs/DECISIONS.md](docs/DECISIONS.md) · [docs/PROGRESS.md](docs/PROGRESS.md)

## Local quickstart

```bash
# API (from repo root)
cp .env.example backend/.env   # set GEMINI_API_KEY
cd backend && uv sync
uv run uvicorn data_extracting_backend.main:app --reload --port 8000

# UI (separate terminal)
cp frontend/.env.example frontend/.env   # VITE_API_BASE_URL=http://localhost:8000
cd frontend && npm install && npm run dev
```

### Smoke scripts

```bash
./backend/scripts/smoke_orders.sh
./backend/scripts/smoke_extract.sh   # needs GEMINI_API_KEY in backend/.env
```

Sample PDF: [docs/testdata/DME Patient Demo Document CPAP.fax.pdf](docs/testdata/DME%20Patient%20Demo%20Document%20CPAP.fax.pdf).

More curl notes: [backend/README.md](backend/README.md).

## Deploy (Render)

Blueprint: [render.yaml](render.yaml) (Web Service + Static Site).

1. **API** — New → Blueprint (or Web Service), root `backend/` (must include `uv.lock`)  
   - Build: `uv sync --frozen`  
   - Start: `uv run uvicorn data_extracting_backend.main:app --host 0.0.0.0 --port $PORT`  
   - Env: `GEMINI_API_KEY`, `GEMINI_MODEL=gemini-3.6-flash`, `DATABASE_URL=sqlite:///./app.db`, `CORS_ORIGINS` (include the static site `https://…onrender.com`), optional `MAX_UPLOAD_BYTES`
2. **UI** — Static Site, root `frontend/`  
   - Build: `npm ci && npm run build`  
   - Publish: `dist`  
   - Env (build-time): `VITE_API_BASE_URL=https://<api-service>.onrender.com`
3. After both URLs exist, set `CORS_ORIGINS` on the API to the UI origin and redeploy/restart if needed.

Free-tier note: SQLite lives on the instance filesystem and is **ephemeral across deploys** unless you attach a disk or move to Postgres.

## Limitations

- **Unauthenticated public API** — anyone with the URL can read/write Orders and call `/extract` (Gemini cost/quota risk). Accepted for this take-home; gate with auth/API key before real PHI.
- SQLite on Render free tier is not durable across deploys.
- PDF-only uploads; no malware scanning.
- No rate limiting on `/extract` yet (S3 / with-more-time).
- Confirm UI uses a top-of-page banner (works; not polished).

## Known issues

- Confirm banner UX is clunky (placement/focus) — improve with a modal near the action after deploy. See DECISIONS.
- Gemini free-tier quota can 429; override model with `GEMINI_MODEL` or raise billing limits.

## With more time / short roadmap

See [docs/ROADMAP.md](docs/ROADMAP.md): Spec B Order fields, Postgres, auth/API key, rate limits, multi-MIME extract, Alembic, confirm UX polish.

## Agent / process

[AGENTS.md](AGENTS.md) · living PR log [docs/PULL_REQUESTS.md](docs/PULL_REQUESTS.md) · commenting [docs/COMMENTING.md](docs/COMMENTING.md)
