# Prompt: Plan post-PR5 roadmap (planning only)

Copy everything below the line into a new agent chat (or `@` this file). **Do not implement code.** Produce a plan the human can review.

---

You are helping plan **post-PR5** work for a GenHealth senior take-home in this repo (`data-extracting`).

## Context (read first)

Read these before proposing anything:

1. `docs/SPEC.md` — MUST/SHOULD/CUT, security MVP vs later, API surface, demo sentence
2. `docs/DECISIONS.md` — locked choices + reasoning (append-only; respect them)
3. `docs/PULL_REQUESTS.md` — PR0–PR5 acceptance criteria and what MVP already committed to
4. `docs/PROGRESS.md` — current gate (may still be mid-assessment)
5. `AGENTS.md` — process rules
6. `docs/assessment.md` — original take-home prompt (what reviewers grade)

**MVP delivery sequence (in flight or done by PR5):** scaffold → Order CRUD + activity log → thin UI + CORS → Gemini PDF extract + confirm-before-save → Render deploy + README.

**Stack (locked):** FastAPI + uv, Vite React TS, SQLite via SQLAlchemy + `DATABASE_URL`, Gemini server-side, Render web + static. Auth cut for MVP. Confirm-before-save is required product behavior.

**Demo sentence:** Reviewer can upload a patient PDF, see editable first/last/DOB draft, confirm to save an Order, and list/edit/delete Orders — with actions logged.

## Your job

Create a **post-PR5 plan only** (no scaffolding, no code, no commits unless the human explicitly asks later). Assume PR5 has shipped a working public MVP that meets assessment MUST items.

Deliver a concise plan document (propose path `docs/ROADMAP.md` or `docs/POST_PR5_PLAN.md`) with:

### 1. Goals after MVP

What “excellent beyond the take-home” looks like for GenHealth-shaped DME intake — without boiling the ocean. Tie goals to assessment “considerations” (validation, security, LLM error handling, testing, scalability, etc.) where relevant.

### 2. Prioritized backlog

Bucket work into waves with **acceptance criteria** each:

| Wave | Intent |
|------|--------|
| **P0 — harden the live demo** | Things that reduce embarrassment/risk on the public unauthenticated deploy within ~1–2 days |
| **P1 — production-shaped MVP+** | Postgres, auth/API key, Alembic, rate limits on `/extract`, better LLM/ops errors, S2 tests |
| **P2 — product depth** | Spec B fields (`status`, `notes`, `equipment_type`), multi-MIME extract boundary, citations/page hints, richer DME fields (insurance/HCPCS/NPI) as optional slices |
| **P3 — scale / platform** | Async jobs, batch, caching, deeper observability — only if P0–P1 solid |

For each item include: **why**, **depends on**, **effort (S/M/L)**, **risk**, **done-when (AC)**.

### 3. Explicit non-goals

What stays out of post-PR5 v1 (and why). Do not silently reintroduce CUT items as P0.

### 4. Security & compliance track

Separate track from features. Start from SPEC “Security later” + accepted MVP risk (open write API). Recommend a minimal hardening path suitable for a demo that still claims production judgment (API key vs full auth, rate limit, upload limits already in MVP, CORS, secrets, logging hygiene). Call out what would be required before **real PHI** (this repo uses fake Buffy data only).

### 5. PR / delivery shape

Propose a **PR sequence after PR5** (PR6+) in the same style as `docs/PULL_REQUESTS.md`: mid-size PRs, ~20-file soft cap, Summary / Test plan / Notes-risks, living log updates. Prefer thin vertical slices over a mega “infra” PR.

### 6. Decision prompts for the human

List **1–5 questions** that materially change the roadmap (e.g. keep SQLite vs Postgres now; shared API key vs real auth; how far toward real DME intake). **Do not assume** — ask.

## Constraints for you (the planning agent)

- **Plan mode only** — no code, no dependency installs, no deploy changes.
- Prefer official docs when recommending tech (uv, FastAPI, Vite, Render, Gemini).
- Do not contradict locked decisions unless you propose a dated decision change with tradeoffs for the human to accept.
- Keep the plan proportional; senior signal is prioritization and tradeoffs, not a 50-item wishlist.
- If repo state shows PR5 not finished yet, still plan *as if* PR5 AC are met, and note any “verify after PR5” checklist.

## Output format

1. Short verdict (3–5 sentences): what to do first after PR5 and what to defer.
2. Wave tables / PR sequence with AC.
3. Security track.
4. Questions for the human.
5. Optional: stub outline for `docs/ROADMAP.md` ready to paste.

Stop when the plan is ready for human review. Do not start implementation.
