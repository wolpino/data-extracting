# Progress

Agents: read this first; update before pausing. Also update [PULL_REQUESTS.md](./PULL_REQUESTS.md) on PR start/finish (mandatory).

## Current

- **Phase:** PR9 — Hardening (API-key slice)
- **Status:** `ready_for_review` — https://github.com/wolpino/data-extracting/pull/11
- **Branch:** `feature/pr9-api-key`
- **Sibling:** rate-limit on `feature/pr9-extract-rate-limit`

## Done

- [x] PR0–PR8 merged (PR8: https://github.com/wolpino/data-extracting/pull/10)
- [x] Public deploy live; pytest suite; opt-in seed
- [x] PR9 API-key PR opened (#11)

## Next

- Human reviews/merges #11
- After UI deploy: set Render `API_KEY=demo-reviewer-key`
- Merge rate-limit sibling when ready
- Do not start PR10 until human says so

## Blockers

- None

## Known issues

- None blocking demo path; Gemini quota 429s remain possible on free tier.
- DOB date picker allows future dates — should block dates after today (`max=today` + validation). Track for small UI follow-up.
- Delete confirm: Confirm delete should stay on the right; Cancel under Edit (possible Edit/Cancel mis-click; rationale otherwise unknown). Track for small UI follow-up.
