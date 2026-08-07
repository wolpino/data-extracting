# Progress

Agents: read this first; update before pausing. Also update [PULL_REQUESTS.md](./PULL_REQUESTS.md) on PR start/finish (mandatory).

## Current

- **Phase:** PR9 — Hardening
- **Status:** `merged` (#11 API key + #12 rate limit)
- **Next gate:** PR10 (Postgres + Alembic) — wait for human go-ahead

## Done

- [x] PR0–PR8 merged (PR8: https://github.com/wolpino/data-extracting/pull/10)
- [x] Public deploy live; pytest suite; opt-in seed
- [x] PR9 API key: https://github.com/wolpino/data-extracting/pull/11
- [x] PR9 extract rate limit: https://github.com/wolpino/data-extracting/pull/12

## Next

- After UI deploy: set Render `API_KEY=demo-reviewer-key` (if not already) and smoke keyed extract
- On human go-ahead: PR10 Postgres + Alembic
- Do not start PR10 until human says so

## Blockers

- None

## Known issues

- None blocking demo path; Gemini quota 429s remain possible on free tier.
- DOB date picker allows future dates — should block dates after today (`max=today` + validation). Track for small UI follow-up.
- Delete confirm: Confirm delete should stay on the right; Cancel under Edit (possible Edit/Cancel mis-click; rationale otherwise unknown). Track for small UI follow-up.
- In-process extract rate limit is **per Render instance** (not shared across instances).
