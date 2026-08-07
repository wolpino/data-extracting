# Progress

Agents: read this first; update before pausing. Also update [PULL_REQUESTS.md](./PULL_REQUESTS.md) on PR start/finish (mandatory).

## Current

- **Phase:** PR5 — Deploy + README
- **Status:** `in_progress` — https://github.com/wolpino/data-extracting/pull/7
- **Branch:** `deploy/pr5-render-readme`

## Done

- [x] PR0–PR4 merged (PR4: https://github.com/wolpino/data-extracting/pull/6)
- [x] Extract + confirm API/UI; model `gemini-3.6-flash`
- [x] Confirm UX debt logged for later
- [x] PR5 artifacts: `render.yaml`, `backend/requirements.txt`, README + ROADMAP; GitHub PR opened

## Next

- Human: sign in to Render (dashboard is at login) so API + Static Site can be created
- Set env (`GEMINI_API_KEY`, `CORS_ORIGINS`, `VITE_API_BASE_URL`); smoke prod; fill public URLs in README
- Mark PR5 `ready_for_review`; pause

## Blockers

- Render dashboard requires interactive login (agent cannot complete OAuth/password)

## Known issues

- Confirm banner at top of page is not user-friendly — defer UX improvement (modal near action). See DECISIONS.
