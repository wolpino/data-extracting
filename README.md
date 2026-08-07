# data-extracting

GenHealth take-home MVP: upload a patient PDF → Gemini draft (first/last/DOB) → **Confirm** to save an Order → list/edit/delete Orders, with activity logging.

**Demo sentence:** Reviewer can upload a patient document (PDF), see extracted first/last/DOB as an editable draft, confirm to save an Order, and list/edit/delete Orders — with all actions logged.

## Public URLs

| Surface | URL |
|---------|-----|
| UI | https://data-extracting-ui.onrender.com |
| API | https://data-extracting-api.onrender.com |
| API health | https://data-extracting-api.onrender.com/health |
| OpenAPI | https://data-extracting-api.onrender.com/docs |

Secrets (`GEMINI_API_KEY`, etc.) live only in Render env / local `backend/.env` — never in git.

## For reviewers

- **Happy path:** open the [UI](https://data-extracting-ui.onrender.com) → paste the **demo API key** (below) into the UI field if the server has `API_KEY` set → upload a PDF from [docs/testdata/](docs/testdata/) → edit the draft fields if needed → **Confirm** to save → list/edit/delete Orders (each mutation asks for Confirm).
- **Demo API key:** when the API has `API_KEY` configured, writes and `/extract` require header `X-API-Key` (same value). Paste it into the UI “Demo API key” field (stored in `sessionStorage` only — **not** a `VITE_*` build secret). Suggested shared value for this take-home: `demo-reviewer-key` (set the same string as `API_KEY` on Render).
- **Confirm-before-save:** `POST /extract` returns a draft only; Orders persist only after confirm (API + UI).
- **Fake data only:** Buffy-themed names/fixtures — not real PHI. Expected fields for the small charts are listed in [docs/testdata/README.md](docs/testdata/README.md).
- **API access:** `GET` list/activity/health stay open for browsing. Mutating Orders + `/extract` require the demo key when `API_KEY` is set. Still not full auth — harden further before real PHI.
- **SQLite on Render free tier** is ephemeral across deploys (Orders may reset after redeploy).
- Decisions and tradeoffs: [docs/DECISIONS.md](docs/DECISIONS.md). Post-MVP sequence: [docs/ROADMAP.md](docs/ROADMAP.md).

### Manual demo checklist

- [ ] `GET https://data-extracting-api.onrender.com/health` returns ok
- [ ] UI loads Orders from the deployed API (CORS OK)
- [ ] Upload `docs/testdata/buffy-summers-chart.pdf` (or the CPAP sample) → draft shows first/last/DOB
- [ ] Edit draft → Confirm → new Order appears in the list
- [ ] Manual create / edit / delete each requires Confirm
- [ ] Optional: try a second Buffy PDF (`willow-…`, `xander-…`, `spike-…`)

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
| Auth | Shared demo `API_KEY` on writes + `/extract` (`X-API-Key`); GETs open |

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
# against prod:
BASE=https://data-extracting-api.onrender.com ./backend/scripts/smoke_orders.sh
```

### Automated tests

```bash
cd backend && uv sync --group dev && uv run pytest
```

See [docs/TESTING.md](docs/TESTING.md). Default suite mocks Gemini (no API key).

Testdata: [docs/testdata/](docs/testdata/) (Buffy charts + assessment CPAP sample).

Local API may set `SEED_DEMO_DATA=true` in `backend/.env` for a Buffy starter Order; leave **unset/false on Render** so the public demo starts empty.

More curl notes: [backend/README.md](backend/README.md).

## Deploy (Render)

Blueprint: [render.yaml](render.yaml) (Web Service + Static Site). Deploy from branch **`main`**.

1. **API** — root `backend/` (must include `uv.lock`)  
   - Build: `uv sync --frozen`  
   - Start: `uv run uvicorn data_extracting_backend.main:app --host 0.0.0.0 --port $PORT`  
   - Env: `GEMINI_API_KEY`, `GEMINI_MODEL=gemini-3.6-flash`, `DATABASE_URL=sqlite:///./app.db`, `CORS_ORIGINS=https://data-extracting-ui.onrender.com`, optional `MAX_UPLOAD_BYTES`, **`API_KEY`** (shared demo key — match README), optional extract rate-limit vars
2. **UI** — root `frontend/`  
   - Build: `npm ci && npm run build`  
   - Publish: `dist`  
   - Env (build-time): `VITE_API_BASE_URL=https://data-extracting-api.onrender.com`  
   - Do **not** set the demo key as `VITE_*` — reviewers paste it in the UI (sessionStorage).

Free-tier note: SQLite lives on the instance filesystem and is **ephemeral across deploys** unless you attach a disk or move to Postgres.

## Limitations

- **Shared demo API key (not full auth)** — when `API_KEY` is set on the server, writes + `/extract` require `X-API-Key`. GETs stay open. The demo key is intentional for reviewers (README + UI paste); do not treat as production auth or put it in `VITE_*`.
- SQLite on Render free tier is not durable across deploys.
- PDF-only uploads; no malware scanning.
- Extract rate limiting is on sibling branch `feature/pr9-extract-rate-limit` (merge into PR9).
- Confirm UI uses a modal dialog (confirm-before-save intact).

## Known issues

- Gemini free-tier quota can 429; override model with `GEMINI_MODEL` or raise billing limits.
- Activity log has no actor/user name yet (no auth in MVP) — see [docs/DECISIONS.md](docs/DECISIONS.md).
- **DOB date picker** allows selecting dates after today — should set `max` to the current day (and ideally validate server-side). Known bug; fix in a small follow-up.
- **Delete confirm layout:** Confirm delete currently shifts left when Delete is replaced. Preferred: Confirm delete stays on the right (Delete’s place); Cancel stacks under Edit. Cancel-under-Edit may be easy to mis-click; fuller rationale unknown beyond UI testing preference. Track for small UI follow-up.

## With more time / short roadmap

See [docs/ROADMAP.md](docs/ROADMAP.md): written tests → UI functionality → hardening → Postgres, then Spec B / multi-MIME / etc.

## Agent / process

[AGENTS.md](AGENTS.md) · living PR log [docs/PULL_REQUESTS.md](docs/PULL_REQUESTS.md) · commenting [docs/COMMENTING.md](docs/COMMENTING.md)
