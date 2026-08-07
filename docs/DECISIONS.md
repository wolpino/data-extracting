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

### 2026-08-07 — Living PULL_REQUESTS log (mandatory)

- **Decision:** Keep `docs/PULL_REQUESTS.md` living; agents must update on every PR start/finish. Skipping is a process failure.
- **Reasoning:** Prevents agents from losing PR context across sessions; mirrors GitHub PR bodies for offline review.
- **Alternatives considered:** Rely only on GitHub PR descriptions; update PROGRESS only.
- **Revisit when:** Never during assessment — this is process law.

### 2026-08-07 — Security MVP baseline vs later

- **Decision:** Ship a small security baseline with the features that need it (env secrets, server-side Gemini key, CORS allowlist, PDF-only + size limit, filename sanitize, no PDF bytes in logs, structured errors). Keep auth, LLM rate limits, malware scan, and PHI program as later. Document unauthenticated public API as accepted take-home risk.
- **Reasoning:** Assessment grades a working public MVP; open write endpoints are expected for a demo unless time for a key. Cheap upload/CORS/secret controls prevent easy foot-guns without burning the clock on auth.
- **Alternatives considered:** Shared API key in MVP; treat rate limiting as MUST before deploy.
- **Revisit when:** Post-deploy S3 time, or if reviewers require a gated endpoint.
