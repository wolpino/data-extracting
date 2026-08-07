# Pull requests (living log)

**Mandate:** Any agent working this repo **must** update this file when a PR **starts** or **finishes**. Skipping the log is a **process failure**, not optional polish.

All planned PRs are listed below with **acceptance criteria** up front. Agents update status, branch, GitHub link, Summary / Test plan / Notes-risks as work progresses — do not delete planned sections.

Also update [PROGRESS.md](./PROGRESS.md) each session. GitHub PR bodies still need Summary / Test plan / Notes-risks (mirror from here).

## How to update

| Event | Required updates |
|-------|------------------|
| **Start** | Status → `in_progress`; set branch + started date; leave AC checkboxes for the implementer |
| **Finish / PR opened** | Status → `ready_for_review`; fill GitHub URL, Summary, Test plan, Notes/risks; tick AC that are met |
| **Merged** | Status → `merged` |

Statuses: `planned` | `in_progress` | `ready_for_review` | `merged` | `closed`

If a PR would exceed ~20 files, split (e.g. PR4a/PR4b), add a new section with its own AC, and pause at the midpoint.

## Index

| PR | Title | Status |
|----|-------|--------|
| [PR0](#pr0--spec-decisions-agent-process) | Spec, decisions, agent process | `merged` |
| [PR1](#pr1--scaffold) | Backend + frontend scaffold | `merged` |
| [PR2](#pr2--order-crud--activity-log) | Order CRUD + activity log | `merged` |
| [PR2b](#pr2b--code-comments--agent-mandate) | Code comments + agent mandate | `merged` |
| [PR3](#pr3--thin-ui--cors) | Thin UI + CORS | `merged` |
| [PR4](#pr4--gemini-extract--confirm) | Gemini extract + confirm | `merged` |
| [PR5](#pr5--deploy--readme) | Deploy + README | `merged` |
| [PR6](#pr6--docs-testdata--manual-checklist) | Docs, Buffy testdata, manual checklist | `merged` |
| [PR7](#pr7--written-automated-tests) | Written automated tests | `merged` |
| [PR8](#pr8--ui-functionality) | UI functionality (not polish) | `ready_for_review` |
| [PR9](#pr9--hardening) | API key + extract rate limit | `planned` |
| [PR10](#pr10--postgres--alembic) | Postgres + Alembic | `planned` |

---

## PR0 — Spec, decisions, agent process

- **Status:** `merged`
- **Branch:** `docs/pr0-spec-process`
- **GitHub:** https://github.com/wolpino/data-extracting/pull/1
- **Started:** 2026-08-07
- **Opened:** 2026-08-07
- **Merged:** 2026-08-07

### Scope

- Living SPEC, DECISIONS, PROGRESS, PULL_REQUESTS (all planned PRs + AC)
- AGENTS.md + Cursor rules (including PR-log mandate)
- Security baseline (MVP vs later) documented in SPEC/DECISIONS
- Assessment prompt + sample testdata under `docs/`
- Root `.gitignore`

### Acceptance criteria

- [x] `docs/SPEC.md` has demo sentence, MUST/SHOULD/CUT, security MVP vs later, API surface, work order
- [x] `docs/DECISIONS.md` seeded with locked decisions + reasoning
- [x] `docs/PROGRESS.md` tracks current gate
- [x] `docs/PULL_REQUESTS.md` lists **all** planned PRs with acceptance criteria + update mandate
- [x] `AGENTS.md` + always-on Cursor rule mandate living PR log and no-skip work order
- [x] Backend/frontend Cursor rules exist for stack conventions
- [x] No secrets or `.env` committed; `.gitignore` covers env/venv/node_modules/db
- [x] GitHub PR opened for human review
- [x] Human approves before PR1 starts

### Summary

Establish product/process source of truth before scaffolding so agents do not duplicate work or skip MUST order. Documents locked stack, confirm-before-save, SHOULD tiers, security minimums, and the full PR plan with AC.

### Test plan

- [ ] SPEC matches approved demo sentence and MUST/SHOULD/CUT
- [ ] PR-log mandate appears in AGENTS.md and `.cursor/rules/genhealth-assessment.mdc`
- [ ] Index above lists PR0–PR5 with AC
- [ ] No secrets in the tree

### Notes / risks

- Public unauthenticated API is an accepted take-home risk; call out at deploy/README.
- Sample PDF is fake demo data (~2MB), not real PHI.
- Do not start PR1 until human says go.

---

## PR1 — Scaffold

- **Status:** `merged`
- **Branch:** `scaffold/pr1`
- **GitHub:** https://github.com/wolpino/data-extracting/pull/2
- **Started:** 2026-08-07
- **Opened:** 2026-08-07
- **Merged:** 2026-08-07
- **Depends on:** PR0 approved

### Scope

- `backend/` via uv + FastAPI; `GET /health` + `GET /api/v1/health`
- `frontend/` via Vite + React + TypeScript; placeholder page only (no Order UI)
- Root `.env.example` (`DATABASE_URL`, `GEMINI_API_KEY`, `CORS_ORIGINS`, `VITE_API_BASE_URL`)
- Settings stub; minimal run instructions (root + package READMEs)
- Deps ready for later: sqlalchemy, pydantic-settings (Gemini client deferred to PR4)

### Acceptance criteria

- [x] `backend/` installs with uv; `uvicorn` serves health **200**
- [x] `frontend/` installs and `npm run build` succeeds (placeholder UI)
- [x] `.env.example` present with placeholders only (no real secrets)
- [x] Env-driven settings stub exists on backend; frontend can read `VITE_API_BASE_URL`
- [x] `.gitignore` still excludes `.env`, venvs, `node_modules`, `dist`, `*.db`
- [x] No Order CRUD, extract, or Gemini code yet
- [x] `docs/PULL_REQUESTS.md` + `docs/PROGRESS.md` updated; GitHub PR opened; pause for review

### Summary

Scaffold monorepo shells: uv-managed FastAPI backend with health routes and pydantic-settings, Vite React TS frontend placeholder that reads `VITE_API_BASE_URL`, plus `.env.example` and run docs. No business logic yet.

### Test plan

- [x] `uv run uvicorn …` → `GET /health` and `/api/v1/health` return 200
- [x] `npm run build` in `frontend/` succeeds
- [ ] `npm run dev` loads placeholder (reviewer)
- [x] No committed secrets / `.env`

### Notes / risks

- Soft ~20-file PR budget exceeded (~28) due to Vite template + `package-lock.json` + `uv.lock`; kept as one cohesive scaffold PR rather than splitting API/UI.
- Browser health fetch may fail until CORS in PR3; curl works now.
- Backend package path is `data_extracting_backend` (uv app layout), not top-level `app/`.

---

## PR2 — Order CRUD + activity log

- **Status:** `merged`
- **Branch:** `feature/pr2-order-crud`
- **GitHub:** https://github.com/wolpino/data-extracting/pull/3
- **Started:** 2026-08-07
- **Opened:** 2026-08-07
- **Merged:** 2026-08-07
- **Depends on:** PR1 merged/approved

### Scope

- SQLAlchemy + SQLite via `DATABASE_URL`; `create_all` on startup
- Minimal Order model + Pydantic schemas; full CRUD under `/api/v1/orders`
- Activity log model + writes on demo routes (metadata only; never PDF bytes)
- Filename sanitization for `source_filename` when provided
- Buffy Summers demo seed on startup (idempotent)

### Acceptance criteria

- [x] Order fields: `id`, `first_name`, `last_name`, `date_of_birth`, optional `source_filename`, timestamps
- [x] `GET/POST /api/v1/orders` and `GET/PUT/PATCH/DELETE /api/v1/orders/{id}` work with Pydantic validation
- [x] Invalid payloads return clear 4xx (structured errors preferred)
- [x] Activity rows recorded for list/get/create/update/delete (action, entity, timestamp, request metadata)
- [x] Activity log does **not** store file/PDF bytes
- [x] `source_filename` sanitized (basename only; path segments rejected)
- [x] DB created via SQLAlchemy `create_all`; default SQLite works locally
- [x] OpenAPI/curl smoke of full CRUD succeeds
- [x] Living PR log + PROGRESS updated; GitHub PR opened; pause for review

### Summary

Add SQLAlchemy Order + ActivityLog models, Pydantic validation, and full `/api/v1/orders` CRUD with activity logging and basename-only filename sanitization. Seeds Buffy Summers for local smoke.

### Test plan

- [x] Create/read/update/delete Order via curl
- [x] Confirm activity rows in DB after list/get/create/update/delete
- [x] Reject path-style `source_filename` and missing required fields (422)
- [ ] Reviewer: `./backend/scripts/smoke_orders.sh` (or see backend README cheatsheet)

### Notes / risks

- Activity logging on every list/get may be noisy; acceptable for assessment demo.
- Engine binds at import from `DATABASE_URL`; restart process after env changes.
- `GET /api/v1/activity` deferred (S2).
- Quick smoke: `./backend/scripts/smoke_orders.sh`
- Post-PR5 planning prompt added: `docs/prompts/post-pr5-planning-agent.md` (planning only; not MVP scope).

---

## PR2b — Code comments + agent mandate

- **Status:** `merged`
- **Branch:** `docs/pr2b-code-comments`
- **GitHub:** https://github.com/wolpino/data-extracting/pull/4
- **Started:** 2026-08-07
- **Opened:** 2026-08-07
- **Merged:** 2026-08-07
- **Depends on:** PR2 merged

### Scope

- Add `docs/COMMENTING.md` standard (why/constraints, no noise)
- Mandate ongoing comments in AGENTS.md, Cursor rules, SPEC, DECISIONS
- Catch-up: concise module/constraint comments on existing backend + thin frontend note
- Insert PR2b into living PR index / work order (before PR3)

### Acceptance criteria

- [x] `docs/COMMENTING.md` exists with do/don’t guidance
- [x] AGENTS + always-on Cursor rule require comments in every future PR
- [x] Backend non-obvious paths commented (SQLite threading, activity metadata-only, filename sanitize, `updated_at` touch, flush-before-log)
- [x] Frontend notes API base / CORS expectation
- [x] SPEC / DECISIONS / PULL_REQUESTS updated; no behavior changes
- [x] GitHub PR opened; pause for review

### Summary

Catch up concise comments on the current codebase and lock an agent mandate so later PRs keep explaining non-obvious why/constraints.

### Test plan

- [x] `./backend/scripts/smoke_orders.sh` still passes (comments-only; no logic change intended)
- [ ] Skim commented modules for noise vs signal (reviewer)

### Notes / risks

- Style is intentionally sparse — prefer why over narrating CRUD.
- Ongoing enforcement is process/rules; reviewers should bounce PRs that omit needed comments.

---

## PR3 — Thin UI + CORS

- **Status:** `merged`
- **Branch:** `feature/pr3-ui-cors`
- **GitHub:** https://github.com/wolpino/data-extracting/pull/5
- **Started:** 2026-08-07
- **Opened:** 2026-08-07
- **Merged:** 2026-08-07
- **Depends on:** PR2b merged/approved

### Scope

- Backend CORS middleware from `CORS_ORIGINS` allowlist (not `*` for production intent)
- Thin React UI: Order list, create, edit, delete
- **Confirm dialogs** before create/update/delete (no silent saves)
- Simple error display; **no** upload/extract UI yet

### Acceptance criteria

- [x] Browser UI lists Orders from API
- [x] Create and edit require explicit Confirm before calling API
- [x] Delete requires confirm dialog
- [x] CORS allows configured Vite origin; disallowed origins fail as expected
- [x] `CORS_ORIGINS` documented in `.env.example`
- [x] UI remains thin (no design-system chase)
- [x] Living PR log + PROGRESS updated; GitHub PR opened; pause for review

### Summary

Add CORS allowlist middleware and a thin Orders UI where create/update/delete only hit the API after an explicit Confirm step.

### Test plan

- [x] `npm run build` succeeds
- [x] CORS: `Origin: http://localhost:5173` gets `access-control-allow-origin`; evil origin does not
- [x] `./backend/scripts/smoke_orders.sh` still passes
- [ ] Manual: `npm run dev` + API on :8000 — create/edit/delete with Confirm (reviewer)

### Notes / risks

- Confirm UI is an in-page dialog (not `window.confirm`) so Cancel is obvious.
- Upload/extract UI intentionally deferred to PR4.
- CORS origins are read at process start; restart API after changing `CORS_ORIGINS`.

---

## PR4 — Gemini extract + confirm

- **Status:** `merged`
- **Branch:** `feature/pr4-extract-confirm`
- **GitHub:** https://github.com/wolpino/data-extracting/pull/6
- **Started:** 2026-08-07
- **Opened:** 2026-08-07
- **Merged:** 2026-08-07
- **Depends on:** PR3 merged/approved

### Scope

- Extract service: `bytes + content_type → draft` (PDF-only); default model `gemini-3.6-flash`
- `POST /api/v1/extract` → draft JSON; **does not** persist Order
- `POST /api/v1/orders/confirm` → creates Order + activity
- Gemini server-side only; LLM error handling; upload size + PDF validation
- UI: upload PDF → editable draft → Confirm → refresh list
- Note confirm-banner UX debt for later

### Acceptance criteria

- [x] `POST /extract` accepts PDF and returns `{first_name, last_name, date_of_birth}` draft
- [x] Non-PDF rejected with 415; oversize rejected with clear error
- [x] Extract alone creates **zero** Order rows
- [x] `POST /orders/confirm` persists Order after human-approved fields (+ optional sanitized filename)
- [x] Gemini API key used only on server; not present in frontend bundle/env for browser
- [x] LLM/network failures return structured errors (no secret leakage)
- [x] UI supports upload → edit draft → Confirm; list updates after confirm
- [x] Works against sample PDF in `docs/testdata/`; prompt is generic (unseen-PDF ready)
- [x] Activity logged for extract attempt and confirm (metadata only)
- [x] Living PR log + PROGRESS updated; GitHub PR opened; pause for review

### Summary

Add Gemini PDF extract (draft-only) and `/orders/confirm`, wire thin UI upload → edit → Confirm, default model `gemini-3.6-flash`.

### Test plan

- [x] `./backend/scripts/smoke_extract.sh` (415 non-PDF; extract sample; confirm; extract does not persist)
- [x] `./backend/scripts/smoke_orders.sh`
- [x] `cd frontend && npm run build`
- [ ] Manual UI extract path (reviewer): set `GEMINI_API_KEY` in `backend/.env`

### Notes / risks

- Confirm banner UX remains clunky (known debt) — improve after deploy.
- Keep secrets in `backend/.env` only — never commit keys (`.env.example` stays empty).
- Free-tier quota varies by model; override with `GEMINI_MODEL` if needed.

---

## PR5 — Deploy + README

- **Status:** `merged`
- **Branch:** `deploy/pr5-render-readme`
- **GitHub:** https://github.com/wolpino/data-extracting/pull/7
- **Started:** 2026-08-07
- **Opened:** 2026-08-07
- **Merged:** 2026-08-07
- **Depends on:** PR4 merged/approved (or minimal API+extract path live)

### Scope

- Render Web Service for FastAPI (public URL); env: `GEMINI_API_KEY`, `DATABASE_URL`, `CORS_ORIGINS`
- Render Static Site for frontend; `VITE_API_BASE_URL` → API URL
- README: architecture, decisions link, limitations, Known issues, with-more-time / short future roadmap
- S3 extras only if deploy already green and time remains; otherwise document under with-more-time

### Acceptance criteria

- [x] Public API health endpoint reachable
- [x] Public `POST /api/v1/extract` works with a PDF (reviewer-usable)
- [x] Confirm + Order CRUD work against deployed API
- [x] Deployed UI talks to deployed API (CORS + `VITE_API_BASE_URL` correct)
- [x] Secrets set in Render only; not in git
- [x] README covers architecture, decisions, limitations (incl. unauthenticated API risk), Known issues, with-more-time / roadmap
- [x] Living PR log + PROGRESS updated; GitHub PR opened; pause for review / submission packaging

### Summary

Deploy FastAPI + Vite static site on Render (`uv sync` build), ship Blueprint/`render.yaml`, and document architecture and limitations for reviewers.

### Test plan

- [x] Hit public health URL (`https://data-extracting-api.onrender.com/health`)
- [x] Upload + extract + confirm on production (CORS allow-origin verified)
- [x] UI list path on production
- [ ] Confirm README lists public URLs (completed in PR6)

### Notes / risks

- Live: API https://data-extracting-api.onrender.com · UI https://data-extracting-ui.onrender.com
- SQLite on free tier is ephemeral across deploys.
- Point Render services at branch `main` after merge.
- Unauthenticated public write + `/extract` is an accepted take-home risk.

---

## PR6 — Docs, testdata + manual checklist

- **Status:** `merged`
- **Branch:** `docs/pr6-reviewer-readme-roadmap`
- **GitHub:** https://github.com/wolpino/data-extracting/pull/8
- **Started:** 2026-08-07
- **Opened:** 2026-08-07
- **Merged:** 2026-08-07
- **Depends on:** PR5 merged + public URLs known

### Scope

- Fill README public URLs + **For reviewers** + manual demo checklist
- Expand `docs/ROADMAP.md` (PR7–PR10 sequence, testing track)
- Close PR5 in living log; plan PR6–PR10
- Buffy-themed PDF fixtures under `docs/testdata/` + expected name/DOB table
- No application feature code

### Acceptance criteria

- [x] README lists live UI/API/health/docs URLs
- [x] For reviewers + manual checklist present
- [x] Buffy PDF fixtures + `docs/testdata/README.md` with expected fields
- [x] ROADMAP documents PR7 tests → PR8 UI → PR9 harden → PR10 Postgres
- [x] PR5 marked `merged`; PR6 opened for review; pause

### Summary

Ship reviewer-facing README (live URLs + manual checklist), expand post-MVP ROADMAP/PR log through PR10, and add Buffy-themed PDF fixtures for extract practice.

### Test plan

- [ ] Spot-check README links open
- [ ] Open a Buffy PDF; confirm expected name/DOB table matches file text
- [ ] ROADMAP PR sequence matches living PULL_REQUESTS index

### Notes / risks

- Docs-only; does not change deploy behavior.
- Small PDFs are synthetic text charts (not fax-quality); CPAP sample remains the large assessment fixture.

---

## PR7 — Written automated tests

- **Status:** `merged`
- **Branch:** `test/pr7-written-tests`
- **GitHub:** https://github.com/wolpino/data-extracting/pull/9
- **Started:** 2026-08-07
- **Opened:** 2026-08-07
- **Merged:** 2026-08-07
- **Depends on:** PR6 merged/approved

### Scope

- `docs/TESTING.md` + AGENTS testing mandate
- Schema/unit + FastAPI TestClient suite (CRUD, extract edges, confirm-before-save)
- Mock Gemini by default; live extract via smoke scripts
- `SEED_DEMO_DATA` opt-in (default off for Render/submission)
- `setup_engine()` for temp DB in tests

### Acceptance criteria

- [x] `uv run pytest` green without `GEMINI_API_KEY`
- [x] Extract non-persist + confirm persist covered
- [x] Filename sanitize / validation covered
- [x] Demo seed disabled by default; documented for local vs Render
- [x] Living PR log updated; pause

### Summary

Add pytest suite per TESTING.md, gate Buffy startup seed behind `SEED_DEMO_DATA`, and document constraints so agents do not hit live Gemini or shared DBs in default tests.

### Test plan

- [x] `cd backend && uv run pytest` (25 passed)
- [ ] Optional: `./backend/scripts/smoke_extract.sh` with key
- [ ] Confirm Render env leaves `SEED_DEMO_DATA` false/unset after deploy

### Notes / risks

- Do not call real Gemini in default CI.
- Activity list endpoint tests land with PR8.
- Existing local `app.db` may still contain an old Buffy row until deleted; new processes won’t re-seed unless `SEED_DEMO_DATA=true`.

---

## PR8 — UI functionality

- **Status:** `ready_for_review`
- **Branch:** `feature/pr8-ui-functionality`
- **GitHub:** https://github.com/wolpino/data-extracting/pull/10
- **Started:** 2026-08-07
- **Opened:** 2026-08-07
- **Depends on:** PR7 merged/approved

### Scope

- Near-action confirm (replace top banner)
- Clear draft vs manual-create CTAs
- `GET /api/v1/activity` + thin Recent activity panel
- Extract busy/error feedback (415/429/502)
- Extend automated tests for the new activity endpoint

### Acceptance criteria

- [x] Confirm & save is a single clear primary button (no second modal); delete uses browser confirm
- [x] After PDF extract, draft state is obvious; incomplete extract errors without filling the form
- [x] Activity list visible beside the form (scroll + load more; metadata only)
- [x] Extract shows clear progress/error states
- [x] Living PR log + PROGRESS updated; GitHub PR opened; pause

### Summary

Primary **Confirm & save Order** button (no second modal), draft badge for extracts, activity aside with scroll + load more, and 422 on incomplete extracts (no N/A drafts).

### Test plan

- [x] `cd backend && uv run pytest`
- [x] `cd frontend && npm run build`
- [ ] Manual: upload Buffy PDF → edit draft → **Confirm & save Order** (one step)
- [ ] Manual: incomplete PDF shows error and does not fill the form
- [ ] Manual: activity aside scrolls; Load more works
- [ ] Manual: create / edit / delete (delete uses browser confirm)

### Notes / risks

- Confirm-before-save for extract = labeled button after reviewing fields (not a modal).
- `GET /activity` does not write activity (avoids feedback loops).
- Gemini may still return junk; server rejects N/A-style names with 422.

---

## PR9 — Hardening

- **Status:** `planned`
- **Branch:** _(set on start)_
- **GitHub:** _(set when opened)_
- **Depends on:** PR8 merged/approved

### Scope

- Shared API key (or equivalent) on write + `/extract`
- Rate limit `/extract`
- Document client header / UI wiring

### Acceptance criteria

- [ ] Unauthenticated writes rejected when key configured
- [ ] Extract rate-limited with clear errors
- [ ] README updated; living log; pause

### Summary

_(fill on finish)_

### Test plan

- [ ] Tests from PR7/PR8 updated for auth/rate-limit behavior
- [ ] Manual prod check with key

### Notes / risks

- Keep demo usable for reviewers (document how to pass the key).

---

## PR10 — Postgres + Alembic

- **Status:** `planned`
- **Branch:** _(set on start)_
- **GitHub:** _(set when opened)_
- **Depends on:** PR9 merged/approved (or human prioritizes durability earlier)

### Scope

- Render Postgres; `DATABASE_URL` swap
- Alembic migrations replacing reliance on `create_all` for prod

### Acceptance criteria

- [ ] Deployed API uses Postgres; data survives redeploy
- [ ] Migrations documented; living log; pause

### Summary

_(fill on finish)_

### Test plan

- [ ] CRUD + extract/confirm against Postgres locally and on Render

### Notes / risks

- Free-tier Postgres limits; backup story still light.
