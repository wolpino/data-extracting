# AGENTS

Instructions for any coding agent working in this repo. Human reviews; agent implements.

## Source of truth

| Doc | Purpose |
|-----|---------|
| [docs/SPEC.md](docs/SPEC.md) | MUST / SHOULD / CUT, demo sentence, API surface, security baseline |
| [docs/DECISIONS.md](docs/DECISIONS.md) | Append-only decision log + reasoning |
| [docs/PROGRESS.md](docs/PROGRESS.md) | Current PR, done/next, blockers — **update every session** |
| [docs/PULL_REQUESTS.md](docs/PULL_REQUESTS.md) | Living PR log — **mandatory update on PR start/finish** |
| [docs/COMMENTING.md](docs/COMMENTING.md) | Concise comment standard — **required in every PR** |
| [docs/TESTING.md](docs/TESTING.md) | Automated test matrix + constraints — **required for PR7+** |
| Official docs | uv, FastAPI, Vite, Render, Gemini — prefer over memory |

Do **not** invent requirements that contradict SPEC. If unclear: **ask the human**. Do not assume.

## Pull request log (mandatory)

**Any agent must update [docs/PULL_REQUESTS.md](docs/PULL_REQUESTS.md) when a PR starts or finishes.** Skipping the log is a **process failure**, not optional polish. Keep it living as work progresses.

## Work order (never skip ahead)

1. Scaffold  
2. CRUD API  
3. Code comments hygiene (PR2b) + ongoing comment standard  
4. Thin UI + CORS  
5. LLM extract  
6. Confirm  
7. Deploy  
8. README  

## Comments (mandatory going forward)

- Follow [docs/COMMENTING.md](docs/COMMENTING.md): clear, concise **why**/constraint comments — not noise.
- Every feature PR must comment non-obvious logic (security, persistence boundaries, env quirks).
- Do not ship uncommented tricky blocks; reviewers should not reverse-engineer intent.

## Testing (mandatory for PR7+)

- Follow [docs/TESTING.md](docs/TESTING.md): isolated DB, mock Gemini by default, required happy/edge matrix.
- Default `uv run pytest` must pass without `GEMINI_API_KEY` / network.
- Demo seed (`SEED_DEMO_DATA`) is opt-in for local only — never rely on it in tests or production.

## PR rules

- Small commits; mid-size PRs.
- If a PR would exceed ~20 files, stop at a mid-checkpoint for human review.
- Every PR description: **Summary**, **Test plan**, **Notes / risks** (mirror into `docs/PULL_REQUESTS.md`).
- **Pause** when a PR is ready (or checkpoint hit). Do not start the next PR until human says so.
- PR cadence: PR0 → PR1 → PR2 → **PR2b comments** → PR3 UI → PR4 extract+confirm → PR5 deploy+README.
- On PR start/finish: update `docs/PULL_REQUESTS.md` **before** pausing.

## Anti-duplication

- Do not re-scaffold `backend/` or `frontend/` if they already exist.
- Do not add a second ORM, second LLM client, or parallel Order models.
- Do not create alternate “v2” apps; extend the monorepo.
- Before starting work: read `docs/PROGRESS.md` and continue from **Next**.

## Stuck protocol

- Stuck >10 minutes on a SHOULD: note under README **Known issues** (or PROGRESS), ship next MUST.
- Prefer working public deploy over polish.

## Stack (locked)

- Backend: Python, FastAPI, uv, SQLAlchemy, SQLite (`DATABASE_URL`)
- Frontend: Vite, React, TypeScript (thin UI)
- LLM: Gemini, key only on server
- Deploy: Render Web Service + Static Site
- Auth: not in MVP

## Confirm-before-save

- Extract never persists an Order.
- Confirm (API + UI) is required before save.
- Manual create/update/delete: UI confirm dialogs required.

## Demo data

- Fake sample data only; Buffy naming for seeds/fixtures.
- Test PDFs under `docs/testdata/`.
- Startup Buffy Order seed only when `SEED_DEMO_DATA=true` (local `.env`); default/off on Render.

## Security (MVP)

Follow SPEC security baseline: secrets in env only; Gemini server-side; CORS allowlist; PDF-only + size limit; sanitize filenames; no secrets in errors; do not log PDF bytes. Auth/rate-limit are later unless S3 time remains. See SPEC.

## When making decisions

1. Ask if it changes SPEC MUST/SHOULD/CUT.
2. Otherwise pick the SPEC default, implement, append to `docs/DECISIONS.md`.
3. Update `docs/PROGRESS.md` and `docs/PULL_REQUESTS.md` as applicable.
