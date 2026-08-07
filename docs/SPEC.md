# GenHealth Take-Home SPEC

Living product/engineering spec. Decisions with rationale live in [DECISIONS.md](./DECISIONS.md). Agent process lives in [AGENTS.md](../AGENTS.md). PR log (mandatory): [PULL_REQUESTS.md](./PULL_REQUESTS.md).

## Demo sentence

**Reviewer can upload a patient document (PDF), see extracted patient first name / last name / DOB as an editable draft, confirm to save an Order, and list/edit/delete Orders — with all actions logged.**

## Hard constraints

- Consecutive **4-hour** timebox; prioritize working public deploy over polish.
- **Python** API; frontend **TypeScript**.
- Stack: **FastAPI + uv**, **Vite + React + TypeScript**, **Gemini** (server-side key), **Render** (API web service + static site).
- Persist Orders to a DB; **log user activity** to DB.
- Upload extracts **first_name, last_name, date_of_birth** from a PDF reviewers may never have seen.
- **Document input:** MVP accepts **any PDF**. Validate PDF only. Extract service boundary: `bytes + content_type → draft fields` so other MIME types can be added later — **do not implement non-PDF in MVP**.
- **Confirm-before-save:** extract returns a draft (not an Order); Order persists only after explicit confirm. Manual create/update also requires UI confirm.
- Public URL required or submission is invalid.
- Demo naming: **Buffy the Vampire Slayer** characters (fake data, no real PHI).
- Test PDF: [testdata/DME Patient Demo Document CPAP.fax.pdf](./testdata/DME%20Patient%20Demo%20Document%20CPAP.fax.pdf).
- Process: small commits; mid-size PRs with summary / test plan / notes-risk; pause at checkpoints; stuck >10 min on SHOULD → Known issues + next MUST.
- **PR log mandate:** keep [PULL_REQUESTS.md](./PULL_REQUESTS.md) living — update on every PR start/finish (process failure if skipped).
- **Commenting mandate:** clear, concise comments on non-obvious code per [COMMENTING.md](./COMMENTING.md); required in every PR going forward.
- Prefer official docs: [uv](https://docs.astral.sh/uv/), [FastAPI](https://fastapi.tiangolo.com/), [Vite](https://vitejs.dev/guide/), [Render FastAPI](https://render.com/docs/deploy-fastapi), [Render static](https://render.com/docs/static-sites), [Gemini quickstart](https://ai.google.dev/gemini-api/docs/quickstart).

## MUST / SHOULD / CUT

### MUST

| Item | Definition of done |
|------|--------------------|
| Scaffold | `backend/` (uv+FastAPI), `frontend/` (Vite React TS), README stubs, `.env.example`, agent/rules files |
| Order CRUD API | Full CRUD; Pydantic validation; SQLAlchemy + SQLite |
| Activity log | Persist action + entity + timestamp (+ request metadata) for demo APIs |
| Extract + confirm | Upload → Gemini draft; confirm → create Order |
| Thin UI + CORS | Upload, edit draft, Confirm; Order list/edit/delete with confirms; CORS for Render |
| Deploy | Public Render API + static frontend; live upload works |
| README | Architecture, decisions, limitations, with-more-time, Known issues |

### Security

**MVP baseline (implement with the feature that needs it — treat as MUST/S1, not optional polish):**

| Control | When |
|---------|------|
| Secrets only via env; never commit `.env` / keys; `.env.example` placeholders only | PR1+ |
| Gemini key server-side only (never in Vite bundle) | PR4 |
| CORS allowlist via `CORS_ORIGINS` (not `*` in production) | PR3 |
| PDF-only upload validation (type/extension) | PR4 |
| Upload **max size** limit | PR4 |
| Sanitize `source_filename` (basename only; reject path segments) | PR2/PR4 |
| Pydantic validation + SQLAlchemy (no raw SQL string concat) | PR2 |
| Structured errors; do not leak secrets or raw stack traces to clients in prod | S1 |
| Activity log: metadata only — **do not** store PDF bytes | PR2/PR4 |
| Confirm-before-save (limits persisting bad/malicious extract output) | PR4 |

**Accepted MVP risk (document in README):** public unauthenticated read/write API for the take-home demo.

**Later (not MVP unless S3 time after deploy):**

- Auth / shared API key / RBAC
- Rate limiting (especially `/extract` + LLM) — already S3
- Malware scanning of uploads
- Postgres, encryption-at-rest, managed backups
- Real PHI retention/redaction policy (this assessment uses fake data only)
- Extra security headers / CSP hardening beyond platform defaults
- Dependency scanning CI

### SHOULD (priority)

**S1 (cheap, when touching that code):** `/api/v1`; structured errors; env config; LLM error handling; `source_filename` on Order; security baseline rows above.

**S2 (after extract+confirm local):** unit tests for Order/extract schemas; activity log list endpoint.

**S3 (only after MUST deployed; else README):** rate limiting, caching, batch processing, async job queues.

### CUT (MVP)

- Auth / user management
- Postgres for v1 (keep `DATABASE_URL` swap-ready)
- Non-PDF upload types
- Rich DME fields (insurance, HCPCS, NPI)
- Heavy UX / design system
- Full Alembic story (`create_all` OK for MVP)
- Upload malware scanning; PHI compliance program (N/A for fake demo data)

### MAYBE LATER / future roadmap (nice-to-have doc)

Not built in the 4h window unless S3 time remains. Capture in README “with more time” and optionally `docs/ROADMAP.md` if time:

- Spec B Order fields: `status`, `notes`, `equipment_type`
- Render Postgres
- Shared API key / auth
- Multi-MIME extract (images, DOCX)
- Citation/page hints from documents
- Alembic migrations
- S3 items if not shipped
- Broader DME intake fields
- Security “later” list above

## Locked decisions

See [DECISIONS.md](./DECISIONS.md). Summary:

| Topic | Choice |
|-------|--------|
| Order schema | Minimal demographics + timestamps (+ optional filename) |
| Confirm flow | Extract draft → Confirm → Order row |
| Documents | Any PDF; isolated extract module |
| DB | SQLite + SQLAlchemy + `DATABASE_URL` |
| Auth | Cut |
| LLM | Gemini, server-side only |
| UI | Thin |
| Deploy | Render Web Service + Static Site |

## API surface (MVP)

- `GET/POST /api/v1/orders`
- `GET/PUT/PATCH/DELETE /api/v1/orders/{id}`
- `POST /api/v1/extract` — multipart PDF → draft JSON (not persisted); non-PDF → 400/415
- `POST /api/v1/orders/confirm` — draft fields (+ optional filename) → Order
- Activity logging in the service layer for these routes

## Work order (do not skip)

1. Scaffold  
2. CRUD API  
3. Code comments hygiene (one-time catch-up) + ongoing comment standard  
4. Thin UI + CORS  
5. LLM extract  
6. Confirm  
7. Deploy  
8. README  

## PR cadence

| PR | Scope | Pause |
|----|-------|-------|
| PR0 | SPEC, DECISIONS, AGENTS, Cursor rules, PULL_REQUESTS, security baseline | After PR open (human review) |
| PR1 | Backend + frontend scaffold, env examples | After PR open |
| PR2 | Order CRUD + activity log | After PR open |
| PR2b | Concise comments on existing code + commenting mandate for agents | After PR open |
| PR3 | Thin UI + CORS | After PR open |
| PR4 | Gemini extract + confirm flow (API + UI) | After PR open; mid-checkpoint if >~20 files |
| PR5 | Render deploy + README | After PR open |

PR body always includes: **Summary**, **Test plan**, **Notes / risks** — also mirrored in [PULL_REQUESTS.md](./PULL_REQUESTS.md). That file lists **all planned PRs with acceptance criteria**; agents update status as work progresses.

## Checkpoint / stuck protocol

- Pause when a PR is ready or at a named checkpoint.
- Stuck >10 minutes on a SHOULD: log under README **Known issues**, ship next MUST.
- Human reviews; agent implements.
