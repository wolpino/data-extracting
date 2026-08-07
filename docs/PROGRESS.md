# Progress

Agents: read this first; update before pausing. Also update [PULL_REQUESTS.md](./PULL_REQUESTS.md) on PR start/finish (mandatory).

## Current

- **Phase:** PR5 — Deploy + README
- **Status:** `in_progress` — branch `deploy/pr5-render-readme`

## Done

- [x] PR0–PR4 merged (PR4: https://github.com/wolpino/data-extracting/pull/6)
- [x] Extract + confirm API/UI; model `gemini-3.6-flash`
- [x] Confirm UX debt logged for later

## Next

- Render Web Service (API) + Static Site (UI)
- README (architecture, limitations, Known issues, with-more-time)
- Open GitHub PR5; pause for review

## Blockers

- GitHub `gh` auth token invalid locally (need `gh auth refresh` to push/open PR)
- Render CLI/API key not available yet — deploy via dashboard or API key

## Known issues

- Confirm banner at top of page is not user-friendly — defer UX improvement (modal near action). See DECISIONS.
