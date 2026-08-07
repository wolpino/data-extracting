# Decision log

Append-only. When a decision changes, add a new entry; do not rewrite history.

## Format

```
### YYYY-MM-DD — Title
- **Decision:** …
- **Reasoning:** …
- **Alternatives considered:** …
- **Revisit when:** …
```

---

### 2026-08-07 — Extract LLM schema allows “not found” (no forced invent)

- **Decision:** Gemini returns `ExtractCandidate` with `demographics_found` + optional name/DOB fields. API returns a draft only when `demographics_found=true` and all three fields pass placeholder checks; otherwise **422** and the UI must not fill the form. Do not use a required-only draft schema for the LLM (it encouraged hallucinated demographics on unrelated PDFs).
- **Reasoning:** Regression: non-medical PDFs still got invented first/last/DOB when the response schema required those fields.
- **Alternatives considered:** Post-filter only (misses plausible invents); always trust the model.
- **Revisit when:** Citations/page evidence or confidence scores are added.

### 2026-08-07 — PR8 UI functionality testing adjustments

- **Decision:** After human UI testing on PR8: (1) no second confirm modal — extract/create/save use one labeled primary button (`Confirm & save Order` / `Create Order` / `Save changes`); delete uses inline **Confirm delete** / **Cancel** on the row (no `Delete #N?` label). (2) Activity sits in a scrollable aside beside the form with load-more and human-readable summaries + absolute times (naive UTC timestamps parsed as UTC). (3) Incomplete extracts return 422 and do not fill the form; N/A / Unknown placeholders rejected — all three of first name, last name, DOB are mandatory.
- **Reasoning:** Double-confirm fought the extract review flow; activity needed to be reference-sized and readable; placeholder drafts undermined trust in extract.
- **Alternatives considered:** Keep modal for all mutations; browser `window.confirm` for delete; leave raw action codes in the activity panel.
- **Revisit when:** Auth lands — **the audit log would be stronger with user names / actor identity, but there is no auth yet** (accepted MVP cut; track under PR9+ hardening / auth).

### 2026-08-07 — Confirm is the primary button (no double modal)

- **Decision:** Extract/create/save use a clearly labeled primary button (`Confirm & save Order` / `Create Order` / `Save changes`) with no second modal. Delete keeps a single `window.confirm`. Incomplete extracts return 422 and do not populate the form; N/A placeholders are rejected.
- **Reasoning:** Human check for extract is reviewing fields then confirming once; a modal after “review” was a double confirm. Activity sits beside the form as a scrollable aside with load-more.
- **Alternatives considered:** Custom modal for all mutations; always show extract placeholders.
- **Revisit when:** Stronger delete UX (inline undo) if needed. **Superseded/refined by “PR8 UI functionality testing adjustments” above** (inline Confirm delete; readable activity times).

### 2026-08-07 — Confirm UI: modal dialog (PR8)

- **Decision:** Replace top-of-page confirm banner with a modal `alertdialog` focused on Confirm; keep confirm-before-save. Extract results use an explicit draft mode + “Confirm save Order…”.
- **Reasoning:** Banner was easy to miss and froze the page awkwardly; modal keeps the invariant while making the action obvious.
- **Alternatives considered:** Inline confirm only in each section; `window.confirm`.
- **Revisit when:** Further a11y polish (focus trap / Esc) if reviewers need it. **Superseded by “Confirm is the primary button” above.**

### 2026-08-07 — Demo seed opt-in via SEED_DEMO_DATA

- **Decision:** Startup Buffy Order seed runs only when `SEED_DEMO_DATA=true` (default `false`). Enable in local `.env`; keep false on Render/submission.
- **Reasoning:** Public demo should not look pre-populated; local smoke still benefits from an optional seed.
- **Alternatives considered:** Always seed; environment-name heuristics (`ENV=production`).
- **Revisit when:** Fixtures replace seed entirely for local demos.

### 2026-08-07 — Post-MVP: written tests (PR7) before UI (PR8)

- **Decision:** After PR6 docs, sequence is PR7 written tests → PR8 UI functionality → PR9 harden → PR10 Postgres.
- **Reasoning:** Existing API surface can be covered without UI work (SPEC S2); gives a regression net before confirm/activity UI changes. Activity endpoint tests ship with PR8.
- **Alternatives considered:** UI before tests (earlier ROADMAP); bundle tests into hardening only.
- **Revisit when:** Human wants durability (Postgres) earlier.

### 2026-08-07 — Post-MVP: docs (PR6) before UI; tests before harden

- **Decision:** PR6 = reviewer docs + Buffy PDF fixtures + manual checklist; PR7 = UI functionality; PR8 = written tests; PR9 = API key + extract rate limit; PR10 = Postgres/Alembic.
- **Reasoning:** Explain the live demo first; fix confirm/activity usability next; land automated tests before security changes so regressions are caught.
- **Alternatives considered:** Bundle written tests into hardening; skip extra Buffy PDFs; UI polish before docs.
- **Revisit when:** Human reprioritizes durability (Postgres) ahead of harden. **Superseded for PR7/PR8 order by “written tests before UI” entry above.**

### 2026-08-07 — Render deploy via Blueprint + uv sync

- **Decision:** Ship `render.yaml` (API web service + static UI) using Render’s native uv support: rootDir `backend/` (with `uv.lock`), build `uv sync --frozen`, start `uv run uvicorn …`.
- **Reasoning:** Project is uv-first; Render enables uv when `uv.lock` is present ([uv-version](https://render.com/docs/uv-version)). Avoids a parallel pip/`requirements.txt` install path.
- **Alternatives considered:** `pip install -r requirements.txt` from `uv export`; Docker; single combined service serving API + static files.
- **Revisit when:** Need durable Postgres disk or custom Docker for native deps.

### 2026-08-07 — Stack lock

- **Decision:** FastAPI + uv; Vite + React + TypeScript; Gemini server-side; Render (web service + static site).
- **Reasoning:** Matches assessment (Python API, TS/JS FE) and candidate preference; official deploy docs exist for this path.
- **Alternatives considered:** Django/Flask; Next.js full-stack; OpenAI instead of Gemini; Railway/Fly.
- **Revisit when:** Never during 4h window unless a hard blocker.

### 2026-08-07 — Minimal Order schema (Spec A)

- **Decision:** Order fields: `id`, `first_name`, `last_name`, `date_of_birth`, optional `source_filename`, `created_at`, `updated_at`.
- **Reasoning:** Assessment grades CRUD + name/DOB extract, not full DME intake. Spec B (`status`, `notes`, `equipment_type`) deferred.
- **Alternatives considered:** Richer DME order (insurance, HCPCS, NPI) in MVP.
- **Revisit when:** Spec B / post-MVP roadmap.

### 2026-08-07 — Confirm-before-save

- **Decision:** `POST /extract` returns a draft only; `POST /orders/confirm` creates the Order. UI requires explicit confirm for create/update/delete.
- **Reasoning:** Human-in-the-loop matches GenHealth approve-then-write pattern and explicit product requirement.
- **Alternatives considered:** Extract creates Order immediately; soft-delete drafts as Order rows with status=draft.
- **Revisit when:** Adding draft persistence or status workflow (Spec B).

### 2026-08-07 — SQLite first via SQLAlchemy

- **Decision:** SQLite for MVP; SQLAlchemy + `DATABASE_URL` so Postgres is a config swap later.
- **Reasoning:** Fastest path in 4h; avoid dual migration work. Postgres on Render is ~15–30+ min and not required.
- **Alternatives considered:** Render Postgres from day one; raw sqlite3 without ORM.
- **Revisit when:** Need durable multi-instance storage or after deploy if time remains.

### 2026-08-07 — Auth cut for MVP

- **Decision:** No authentication in MVP.
- **Reasoning:** Not required by assessment; can add API key middleware later without rewriting CRUD.
- **Alternatives considered:** Shared API key, basic auth.
- **Revisit when:** Post-MVP hardening or if reviewers flag open write endpoints.

### 2026-08-07 — PDF-only extract with extensible boundary

- **Decision:** Accept any PDF in MVP; reject other types. Implement extract as `bytes + content_type → draft`.
- **Reasoning:** Reviewers will use unseen PDFs; future MIME types must not force Order/UI rewrite.
- **Alternatives considered:** DME-fax-specific parsing; multi-format in MVP.
- **Revisit when:** Adding images/DOCX on the roadmap.

### 2026-08-07 — SHOULD tiering (S1 / S2 / S3)

- **Decision:** S3 (rate limit, cache, batch, async queues) only after public deploy; else document under with-more-time.
- **Reasoning:** Public URL is a hard fail; S3 must not block MUST.
- **Alternatives considered:** Treat rate limiting as MUST; attempt S3 before deploy.
- **Revisit when:** MUST deployed with time left.

### 2026-08-07 — Future roadmap as nice-to-have

- **Decision:** Maintain a short future roadmap (README “with more time” and/or `docs/ROADMAP.md` if time) listing Spec B, Postgres, auth, multi-MIME, S3 extras — not built in MVP unless spare time.
- **Reasoning:** Shows prioritization and production thinking without burning the clock.
- **Alternatives considered:** Skip roadmap entirely; build roadmap doc before code.
- **Revisit when:** Writing final README (PR5).

### 2026-08-07 — Gemini model gemini-3.6-flash

- **Decision:** Default `GEMINI_MODEL=gemini-3.6-flash` (overridable via env).
- **Reasoning:** Available quota / works for PDF structured extract in this account; `gemini-2.0-flash` returned free-tier RESOURCE_EXHAUSTED.
- **Alternatives considered:** gemini-2.0-flash, gemini-2.5-flash.
- **Revisit when:** Model deprecation or better latency/cost option.

### 2026-08-07 — Confirm UI UX debt (post-PR3)

- **Decision:** Keep the working top-of-page confirm banner for MVP; improve UX later (modal near action, focus trap, clearer hierarchy).
- **Reasoning:** Confirm-before-save is REQUIRED; placement/polish is not. User feedback: current alert is not user-friendly.
- **Alternatives considered:** Fix UX in PR4 (risks scope creep before extract/deploy).
- **Revisit when:** After PR5 / with-more-time, or a small PR3.1 if clock allows.

### 2026-08-07 — Concise commenting mandate (PR2b)

- **Decision:** Require clear, concise why/constraint comments on non-obvious code in every PR; catch up existing code in PR2b; document standard in `docs/COMMENTING.md`.
- **Reasoning:** Speeds human review and keeps agents from shipping unexplained persistence/security boundaries.
- **Alternatives considered:** Docs-only with no code comments; heavy docstrings on every function.
- **Revisit when:** Never drop the mandate; tune style if comments get noisy.

### 2026-08-07 — Living PULL_REQUESTS log (mandatory)

- **Decision:** Keep `docs/PULL_REQUESTS.md` living; agents must update on every PR start/finish. Skipping is a process failure.
- **Reasoning:** Prevents agents from losing PR context across sessions; mirrors GitHub PR bodies for offline review.
- **Alternatives considered:** Rely only on GitHub PR descriptions; update PROGRESS only.
- **Revisit when:** Never during assessment — this is process law.

### 2026-08-07 — Backend package layout (uv app)

- **Decision:** Use uv `--app` layout `backend/src/data_extracting_backend/` with `main.py` + `config.py` (not a top-level `app/` folder).
- **Reasoning:** Matches official uv project defaults; avoids fighting the tool. Uvicorn target: `data_extracting_backend.main:app`.
- **Alternatives considered:** Flat `backend/app/` without src layout.
- **Revisit when:** Never required for MVP.

### 2026-08-07 — Security MVP baseline vs later

- **Decision:** Ship a small security baseline with the features that need it (env secrets, server-side Gemini key, CORS allowlist, PDF-only + size limit, filename sanitize, no PDF bytes in logs, structured errors). Keep auth, LLM rate limits, malware scan, and PHI program as later. Document unauthenticated public API as accepted take-home risk.
- **Reasoning:** Assessment grades a working public MVP; open write endpoints are expected for a demo unless time for a key. Cheap upload/CORS/secret controls prevent easy foot-guns without burning the clock on auth.
- **Alternatives considered:** Shared API key in MVP; treat rate limiting as MUST before deploy.
- **Revisit when:** Post-deploy S3 time, or if reviewers require a gated endpoint.

### 2026-08-07 — PR9 extract in-process rate limit

- **Decision:** Rate-limit `POST /api/v1/extract` only with an in-memory sliding window keyed by `request.client.host`. Env: `EXTRACT_RATE_LIMIT_PER_MINUTE` (default 15), `EXTRACT_RATE_LIMIT_ENABLED` (default true). Over-limit → 429 + structured `{error, message}` + `Retry-After`. No Redis/shared store for this take-home.
- **Reasoning:** Cheap Gemini-quota guard that works on free Render without new infra; IP keying works with or without the parallel API-key slice (key-scoped buckets can layer later).
- **Alternatives considered:** Redis; limit all writes; require API key before shipping limiter.
- **Revisit when:** Multi-instance deploy needs a shared store, or API key lands and we want key+IP composite keys.

### 2026-08-07 — PR9 shared demo API key

- **Decision:** Optional `API_KEY` env; when set, require `X-API-Key` on Order writes + `/extract` + confirm. GETs/`/health` stay open. Empty `API_KEY` keeps local open. UI stores the demo key in `sessionStorage` (never `VITE_*`). Shared README value `demo-reviewer-key` for this take-home.
- **Reasoning:** Blocks casual write/Gemini abuse on the public demo without full auth; reviewers can still browse lists and paste one key.
- **Alternatives considered:** Lock all routes; bake key into Vite env; require key even when unset locally.
- **Revisit when:** Real user auth / per-reviewer keys / PHI.
