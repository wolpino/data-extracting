# Pull requests (living log)

**Mandate:** Any agent working this repo **must** update this file when a PR **starts** or **finishes**. Skipping the log is a **process failure**, not optional polish.

Also update [PROGRESS.md](./PROGRESS.md) each session. PR descriptions on GitHub still need Summary / Test plan / Notes-risks.

## How to update

When **starting** a PR: add a section with status `in_progress`, scope, and empty checklist.

When **finishing** (PR opened or ready for review): set status `ready_for_review` or `merged`, fill Summary / Test plan / Notes-risks, link the GitHub URL.

Statuses: `planned` | `in_progress` | `ready_for_review` | `merged` | `closed`

---

## PR0 — Spec, decisions, agent process

- **Status:** `ready_for_review`
- **Branch:** `docs/pr0-spec-process`
- **GitHub:** https://github.com/wolpino/data-extracting/pull/1
- **Started:** 2026-08-07
- **Opened:** 2026-08-07

### Scope

- Living SPEC, DECISIONS, PROGRESS, PULL_REQUESTS
- AGENTS.md + Cursor rules (including PR-log mandate)
- Security baseline (MVP vs later) documented in SPEC/DECISIONS
- Assessment prompt + sample testdata retained under `docs/`

### Summary

Establish product/process source of truth before scaffolding so agents do not duplicate work or skip MUST order. Documents locked stack, confirm-before-save, SHOULD tiers, and security minimums for a public unauthenticated demo.

### Test plan

- [ ] `docs/SPEC.md` matches approved demo sentence and MUST/SHOULD/CUT
- [ ] `docs/PULL_REQUESTS.md` mandate appears in AGENTS.md and always-on Cursor rule
- [ ] Security MVP baseline vs later is explicit (no auth required for MVP; upload/CORS/secrets called out)
- [ ] No secrets or `.env` files in the tree

### Notes / risks

- Public API without auth is an accepted take-home tradeoff; must be called out at deploy/README time.
- Sample PDF is fake demo data (~2MB); not real PHI.
- Scaffolding (PR1) must not start until this PR is reviewed / human says go.

### Checklist

- [x] SPEC / DECISIONS / PROGRESS written
- [x] AGENTS + Cursor rules
- [x] PULL_REQUESTS living log + mandate
- [x] Security review folded into SPEC/DECISIONS
- [x] GitHub PR opened
