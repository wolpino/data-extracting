# Progress

Agents: read this first; update before pausing. Also update [PULL_REQUESTS.md](./PULL_REQUESTS.md) on PR start/finish (mandatory).

## Current

- **Phase:** PR9 — Hardening (rate-limit slice)
- **Status:** `ready_for_review` — https://github.com/wolpino/data-extracting/pull/12
- **Branch:** `feature/pr9-extract-rate-limit`
- **API-key:** merged (#11)

## Done

- [x] PR0–PR8 merged (PR8: https://github.com/wolpino/data-extracting/pull/10)
- [x] Public deploy live; pytest suite; opt-in seed
- [x] PR9 API-key merged (#11)
- [x] PR9 rate-limit PR opened (#12)

## Next

- Human reviews/merges #12
- After UI deploy: set Render `API_KEY=demo-reviewer-key` (if not already)
- Do not start PR10 until human says so

## Blockers

- None

## Known issues

- None blocking demo path; Gemini quota 429s remain possible on free tier.
- DOB date picker allows future dates — should block dates after today (`max=today` + validation). Track for small UI follow-up.
- Delete confirm: Confirm delete should stay on the right; Cancel under Edit (possible Edit/Cancel mis-click; rationale otherwise unknown). Track for small UI follow-up.
- In-process extract rate limit is **per Render instance** (not shared across instances).
