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
| [PR3](#pr3--thin-ui--cors) | Thin UI + CORS | `ready_for_review` |
| [PR4](#pr4--gemini-extract--confirm) | Gemini extract + confirm | `planned` |
| [PR5](#pr5--deploy--readme) | Deploy + README | `planned` |

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

- **Status:** `ready_for_review`
- **Branch:** `feature/pr3-ui-cors`
- **GitHub:** _(filled after open)_
- **Started:** 2026-08-07
- **Opened:** 2026-08-07
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
- [ ] Living PR log + PROGRESS updated; GitHub PR opened; pause for review

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

- **Status:** `planned`
- **Branch:** _(set on start)_
- **GitHub:** _(set when opened)_
- **Depends on:** PR3 merged/approved
- **Split rule:** If change set approaches ~20 files, ship **PR4a** (API) then **PR4b** (UI) with separate sections/AC and a midpoint pause

### Scope

- Extract service: `bytes + content_type → draft` (PDF-only branch in MVP)
- `POST /api/v1/extract` → draft JSON; **does not** persist Order
- `POST /api/v1/orders/confirm` → creates Order + activity
- Gemini server-side only; LLM error handling (timeouts/empty/non-PDF)
- Upload max size limit; PDF type/extension validation
- UI: upload PDF → editable draft → Confirm → refresh list

### Acceptance criteria

- [ ] `POST /extract` accepts PDF and returns `{first_name, last_name, date_of_birth}` draft
- [ ] Non-PDF rejected with 400/415; oversize rejected with clear error
- [ ] Extract alone creates **zero** Order rows
- [ ] `POST /orders/confirm` persists Order after human-approved fields (+ optional sanitized filename)
- [ ] Gemini API key used only on server; not present in frontend bundle/env for browser
- [ ] LLM/network failures return structured errors (no secret leakage)
- [ ] UI supports upload → edit draft → Confirm; list updates after confirm
- [ ] Works against sample PDF in `docs/testdata/`; prompt is generic (unseen-PDF ready)
- [ ] Activity logged for extract attempt and confirm (metadata only)
- [ ] If split: PR4a and PR4b each meet their subset of AC and each pause for review
- [ ] Living PR log + PROGRESS updated; GitHub PR opened; pause for review

### Summary

_(fill on finish)_

### Test plan

- [ ] Extract sample PDF; verify draft fields
- [ ] Confirm creates Order; re-extract without confirm does not
- [ ] Reject `.txt` / oversize upload
- [ ] UI confirm path end-to-end locally

### Notes / risks

_(fill on finish)_

---

## PR5 — Deploy + README

- **Status:** `planned`
- **Branch:** _(set on start)_
- **GitHub:** _(set when opened)_
- **Depends on:** PR4 merged/approved (or minimal API+extract path live)

### Scope

- Render Web Service for FastAPI (public URL); env: `GEMINI_API_KEY`, `DATABASE_URL`, `CORS_ORIGINS`
- Render Static Site for frontend; `VITE_API_BASE_URL` → API URL
- README: architecture, decisions link, limitations, Known issues, with-more-time / short future roadmap
- S3 extras only if deploy already green and time remains; otherwise document under with-more-time

### Acceptance criteria

- [ ] Public API health endpoint reachable
- [ ] Public `POST /api/v1/extract` works with a PDF (reviewer-usable)
- [ ] Confirm + Order CRUD work against deployed API
- [ ] Deployed UI talks to deployed API (CORS + `VITE_API_BASE_URL` correct)
- [ ] Secrets set in Render only; not in git
- [ ] README covers architecture, decisions, limitations (incl. unauthenticated API risk), Known issues, with-more-time / roadmap
- [ ] Living PR log + PROGRESS updated; GitHub PR opened; pause for review / submission packaging

### Summary

_(fill on finish)_

### Test plan

- [ ] Hit public health URL
- [ ] Upload + extract + confirm on production
- [ ] UI list/create path on production
- [ ] Confirm README lists public URLs

### Notes / risks

_(fill on finish; call out SQLite ephemeral disk on free tier if applicable)_
