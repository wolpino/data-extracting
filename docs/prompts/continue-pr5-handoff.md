# Prompt: Continue GenHealth take-home from PR5

Copy everything below the line into a new agent chat (or `@` this file). Human reviews; you implement. Follow repo process strictly.

---

You are continuing a **timed GenHealth senior take-home** in repo `data-extracting` (GitHub: `wolpino/data-extracting`).

## Read first (source of truth)

1. `docs/SPEC.md` — MUST/SHOULD/CUT, security baseline, API surface, demo sentence  
2. `docs/DECISIONS.md` — locked decisions (append-only)  
3. `docs/PULL_REQUESTS.md` — **mandatory living PR log** (update on PR start/finish)  
4. `docs/PROGRESS.md` — current gate  
5. `docs/COMMENTING.md` — concise why/constraint comments required  
6. `AGENTS.md` + `.cursor/rules/*`  
7. `docs/assessment.md` — original grader prompt  

Official docs preference: [uv](https://docs.astral.sh/uv/), [FastAPI](https://fastapi.tiangolo.com/), [Vite](https://vitejs.dev/guide/), [Render FastAPI](https://render.com/docs/deploy-fastapi), [Render static sites](https://render.com/docs/static-sites), [Gemini quickstart](https://ai.google.dev/gemini-api/docs/quickstart).

**Ask the human when unclear. Do not assume.**

## Where things stand (as of handoff)

| Item | State |
|------|--------|
| PR0–PR4 | **Merged** (PR4 = https://github.com/wolpino/data-extracting/pull/6) |
| PR5 | **Next / in progress locally** — branch `deploy/pr5-render-readme` exists but may have **no commits ahead of main** yet |
| Untracked | `backend/requirements.txt` (from `uv export`) — useful for Render pip install; commit if you use it |
| Default model | `gemini-3.6-flash` via `GEMINI_MODEL` / `Settings.gemini_model` (human requested this; keep it) |
| Living docs lag | `docs/PULL_REQUESTS.md` index may still show PR4 as `ready_for_review` — **mark PR4 `merged`**, start PR5 properly in the log |

### Product already shipped locally

- FastAPI + uv backend: Order CRUD, activity log, CORS allowlist, PDF extract, confirm-before-save  
- Vite React TS thin UI: Orders CRUD + PDF upload → draft → Confirm  
- Smoke scripts: `./backend/scripts/smoke_orders.sh`, `./backend/scripts/smoke_extract.sh`  
- Secrets: `backend/.env` (gitignored). **Never commit keys.** `.env.example` placeholders only.

### Known debt (do not block PR5)

- **Confirm UI UX:** top-of-page confirm banner is not user-friendly. Logged in DECISIONS / Known issues. Improve **after** public deploy (or tiny follow-up), not instead of PR5.  
- SQLite on Render free tier is ephemeral across deploys unless a disk is added — document in README limitations.  
- Earlier `gemini-2.0-flash` hit free-tier **429 RESOURCE_EXHAUSTED** on this account; model is now `gemini-3.6-flash`. If extract still 429s, surface clear 502/429 handling and ask human about quota/billing — do not invent fake extract success.

## Your mission: finish PR5, then pause

Work order remaining: **Deploy → README** (then stop for human review).

### PR5 acceptance criteria (from `docs/PULL_REQUESTS.md`)

- [ ] Public API health endpoint reachable  
- [ ] Public `POST /api/v1/extract` works with a PDF  
- [ ] Confirm + Order CRUD work against deployed API  
- [ ] Deployed UI talks to deployed API (`CORS_ORIGINS` + `VITE_API_BASE_URL`)  
- [ ] Secrets set in Render only; not in git  
- [ ] README: architecture, decisions link, limitations (incl. **unauthenticated public API** risk), Known issues, with-more-time / short roadmap  
- [ ] Update `docs/PULL_REQUESTS.md` + `docs/PROGRESS.md`; open GitHub PR; **pause for review**

### Suggested implementation steps

1. Sync `main`, ensure you’re on `deploy/pr5-render-readme` (or recreate from latest `main`).  
2. Update living docs: PR4 → `merged`; PR5 → `in_progress` with branch/date.  
3. Render **Web Service** for backend:
   - Prefer official Render FastAPI guidance.  
   - Build: if using pip, commit `backend/requirements.txt` from `uv export --no-dev --no-hashes -o requirements.txt` (already generated untracked) **or** document `uv` build if Render supports it.  
   - Start: `uvicorn data_extracting_backend.main:app --host 0.0.0.0 --port $PORT` (from `backend/` with `PYTHONPATH`/package install as needed).  
   - Env: `GEMINI_API_KEY`, `GEMINI_MODEL=gemini-3.6-flash`, `DATABASE_URL`, `CORS_ORIGINS` (include the static site origin), `MAX_UPLOAD_BYTES` optional.  
4. Render **Static Site** for `frontend/dist`:
   - Build: `npm ci && npm run build`  
   - `VITE_API_BASE_URL` = public API URL (must be available at **build** time for Vite).  
5. Smoke production: health, extract sample PDF (`docs/testdata/…`), confirm, UI path.  
6. Rewrite root `README.md` for reviewers (architecture, how to run, public URLs, decisions pointer, limitations, Known issues, with-more-time). Optional short `docs/ROADMAP.md` if time.  
7. Open PR5 with Summary / Test plan / Notes-risks; mirror into `docs/PULL_REQUESTS.md`; pause.

### Process rules (non-negotiable)

- Small commits; mid-size PRs; pause when PR ready.  
- Soft ~20-file budget — mid-checkpoint if exceeded.  
- Update `docs/PULL_REQUESTS.md` on start/finish — skipping is a **process failure**.  
- Concise comments on non-obvious code (`docs/COMMENTING.md`).  
- Stuck >10m on SHOULD → Known issues + next MUST.  
- **Do not** start post-PR5 features (auth, Postgres, confirm UX redesign) unless deploy is green and human asks.

### Security reminders

- Never commit `.env` / API keys.  
- CORS allowlist only (no `*` in prod).  
- Gemini key server-side only.  
- If a key was ever pasted into `.env.example` locally, ensure git history on `main` is clean (it should be); tell human to rotate if the key leaked in chat/logs.

### Useful local commands

```bash
# API
cd backend && uv sync && uv run uvicorn data_extracting_backend.main:app --reload --port 8000

# UI
cd frontend && npm install && npm run dev

# Smokes
./backend/scripts/smoke_orders.sh
./backend/scripts/smoke_extract.sh   # needs GEMINI_API_KEY in backend/.env
```

### Demo sentence (still the bar)

**Reviewer can upload a patient document (PDF), see extracted first/last/DOB as an editable draft, confirm to save an Order, and list/edit/delete Orders — with all actions logged.**

## Output / stop condition

Ship a reviewable **PR5** (deployed public URLs + README). Update living docs. **Pause** for human review. Do not proceed to post-MVP roadmap implementation unless asked (planning prompt exists at `docs/prompts/post-pr5-planning-agent.md`).
