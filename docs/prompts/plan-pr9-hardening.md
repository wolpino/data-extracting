# Prompt: Plan PR9 hardening (planning only)

Copy everything below the line into a new agent chat (or `@` this file). **Do not implement code.** Produce a plan the human can review **before** any hardening work starts.

Human context: **PR8 is being merged** (UI functionality). Next numbered work is **PR9 — Hardening**. Do **not** start PR10 (Postgres) or product features unless the plan explicitly recommends splitting and the human agrees.

---

You are planning **PR9 hardening** for the GenHealth take-home repo `data-extracting` (GitHub: `wolpino/data-extracting`).

## Read first (source of truth)

1. `docs/SPEC.md` — security MVP vs later, SHOULD S3 (rate limit), CUT auth, API surface  
2. `docs/DECISIONS.md` — especially auth cut, security baseline, PR8 UI testing adjustments, extract `demographics_found`, audit-log actor note  
3. `docs/ROADMAP.md` — PR9 / PR10 sequence and security track  
4. `docs/PULL_REQUESTS.md` — **PR9** section (planned AC); also PR7/PR8 for test expectations  
5. `docs/TESTING.md` — how tests must be written (mock Gemini, isolated DB)  
6. `docs/PROGRESS.md` — current gate after PR8 merge  
7. `AGENTS.md` + `.cursor/rules/*`  
8. `docs/assessment.md` — what graders care about  
9. Live deploy notes in root `README.md` (public URLs, unauthenticated API risk)

Official docs preference: [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/), [Render env vars](https://render.com/docs/configure-environment-variables), Gemini / uv as already used in-repo.

**Ask the human when unclear. Do not assume.**

## Where things stand (as of handoff)

| Item | State |
|------|--------|
| PR0–PR7 | Merged |
| PR8 | Merging / merged — UI: Confirm & save (no double modal), activity aside, incomplete extract → 422, human-readable activity |
| Public API | https://data-extracting-api.onrender.com |
| Public UI | https://data-extracting-ui.onrender.com |
| Auth | Still **none** (MVP cut). Activity log has **no actor/user name** — noted in DECISIONS/ROADMAP as stronger with auth later |
| Tests | pytest + TestClient; Gemini mocked; see `docs/TESTING.md` |
| Seed | `SEED_DEMO_DATA` opt-in; false on Render |

### Product already shipped

- Order CRUD + activity logging (metadata only)  
- PDF extract → editable draft → **Confirm & save Order** (confirm-before-save)  
- Incomplete / non-demographic PDFs must **not** invent fields (`ExtractCandidate.demographics_found`)  
- CORS allowlist, upload size limit, PDF-only, filename sanitize  
- Thin UI + activity panel  

### Known debt (do not expand PR9 into these unless human asks)

- Full user auth / RBAC / actor names on activity (needs identity; API key is not full auth)  
- Postgres + Alembic (**PR10**)  
- Spec B fields, multi-MIME, citations, async queues  

## Your mission: plan PR9 only, then pause

Assume PR8 is merged onto `main`. Deliver a **hardening plan** the human can approve or reshape **before** implementation.

### PR9 intent (from living docs — refine, don’t ignore)

Current stub scope:

- Shared API key (or equivalent) on **write** + `/extract`  
- Rate limit `/extract`  
- Document client header / UI wiring  
- Keep the **demo reviewer-usable** (how to pass the key must be obvious in README)

Planned AC (refine if needed):

- [ ] Unauthenticated writes rejected when key configured  
- [ ] Extract rate-limited with clear errors  
- [ ] README / Render env updated; living PR log; pause  

### What the plan must cover

#### 1. Verdict (3–5 sentences)

What PR9 should ship for a public take-home that currently has an open write API + expensive `/extract`, and what must wait for PR10 / later.

#### 2. Threat model (short)

What we are mitigating on the live `*.onrender.com` demo (abuse of Orders write, Gemini quota burn, casual scraping) vs what we are **not** claiming (real PHI, full authN/Z).

#### 3. Recommended design (pick defaults; list tradeoffs)

For each, recommend one approach and note alternatives:

| Topic | Questions to resolve |
|-------|----------------------|
| API key | Header name? Env var? Protect which methods/paths (`GET` list open vs locked)? Optional key when unset (local) vs required in prod? |
| UI wiring | How does the static site send the key without baking secrets into git? (`VITE_*` is public — call this out.) Reviewer UX for demo. |
| Rate limit | In-process vs Redis? Scope (IP / key)? Limits for `/extract` only vs all writes? 429 body shape. Render multi-instance caveats on free tier. |
| Activity / actor | With only a shared key, can we log `actor=api-key` or a key id — **not** a user name? Align with DECISIONS note that real names need auth. |
| Tests | Extend pytest per `TESTING.md`; what fails closed vs open when `API_KEY` unset. |
| Render / README | Exact env vars; redeploy steps; how reviewers call curl + UI. |
| Non-goals | Explicitly exclude full OAuth, RBAC, Postgres (PR10), malware scan, etc. |

#### 4. Implementation sketch (no code)

- Backend modules / middleware touch points (`main.py`, routers, settings)  
- Frontend touch points (`api.ts`, maybe a local-only key field — **warn if `VITE_` exposes the secret**)  
- Smoke script updates  
- File budget (~20 soft cap); suggest PR9a/PR9b split only if needed  

#### 5. Acceptance criteria + test plan

Rewrite PR9 AC as checkboxes suitable to paste into `docs/PULL_REQUESTS.md`. Include automated + manual/prod checks.

#### 6. Decision questions for the human (1–5)

Material forks only, e.g.:

- Shared demo key vs “key required only on Render”  
- Lock **reads** too, or only writes + extract?  
- In-memory rate limit acceptable on free Render?  
- Is “API key as actor” enough for activity, or defer actor until real auth?  

**Do not assume answers — ask.**

#### 7. Optional: update outline

Short stub for `docs/ROADMAP.md` PR9 section and/or a `docs/PR9_HARDENING_PLAN.md` outline ready to paste **after** human approval (do not write/commit those files unless the human asks).

## Process constraints

- **Plan mode only** — no code, no commits, no Render changes, no dependency installs.  
- Prefer official FastAPI / Render docs over inventing a framework.  
- Do not contradict SPEC/DECISIONS without proposing a dated decision change + tradeoffs.  
- Do not start PR10 or UI polish in this plan’s “do now” list.  
- Keep it proportional — senior signal is prioritization and demo-safe security, not an enterprise IAM design.

## Output format

1. Verdict  
2. Threat model  
3. Recommended design (tables OK)  
4. Implementation sketch + AC / test plan  
5. Questions for the human  
6. Optional paste-ready ROADMAP / PULL_REQUESTS stub  

**Stop** when the plan is ready for human review. Do **not** implement until the human explicitly says to execute PR9.
