# Roadmap (post-MVP)

Prioritized after a green public deploy. Aligns with SPEC SHOULD/CUT and [DECISIONS.md](./DECISIONS.md).

## Verdict

1. **Explain the demo** (PR6) — live URLs, reviewer checklist, Buffy fixtures.
2. **Written tests** (PR7) — schema + API `TestClient` on the existing surface (SPEC S2), before UI churn.
3. **UI functionality** (PR8) — make confirm/draft/activity obvious (not visual polish); extend tests for new activity endpoint.
4. **Harden** (PR9) then **Postgres** (PR10). Defer Spec B / multi-MIME / queues until then.

## PR sequence

| PR | Intent |
|----|--------|
| **PR6** | Docs + Buffy PDF testdata + manual demo checklist |
| **PR7** | Written automated tests (SPEC S2 schemas + API paths; mock Gemini in CI) |
| **PR8** | UI functionality: near-action confirm, draft vs saved, activity list, extract feedback |
| **PR9** | Hardening: shared API key (or equivalent) on write + `/extract`; rate limit `/extract` |
| **PR10** | Postgres + Alembic (durable DB on Render) |

## PR7 — Written automated tests

| Kind | What |
|------|------|
| Schema/unit | Order + extract draft validation; bad DOB; pathy `source_filename` |
| API TestClient | CRUD smoke; non-PDF → 415; extract does **not** persist; confirm persists |
| Gemini | Mock by default; optional live-key test marked local-only |
| Fixtures | Use `docs/testdata/` where useful |

**Done-when:** `pytest` (via uv) green without `GEMINI_API_KEY`.

## PR8 — UI functionality (not polish)

| Item | Why | Effort | Done-when |
|------|-----|--------|-----------|
| Near-action confirm | Top banner in `frontend/src/App.tsx` is easy to miss | S | Dialog near initiating action; Cancel/Confirm; keep confirm-before-save |
| Clear draft vs saved | Extract + manual create share one form | S | Explicit draft state after extract; clear primary CTA to save Order |
| Show activity | Logged in DB but invisible in UI | M | `GET /api/v1/activity` + “Recent activity” panel (metadata only) + tests for the new endpoint |
| Extract feedback | Long Gemini calls feel stuck | S | Busy/error copy for 415/429/502 |

**Out of scope:** design system, theme, animation, Spec B fields, auth.

## Testing track

| Kind | When | What |
|------|------|------|
| Manual checklist | PR6 (README); extend every PR | Health → upload → confirm → CRUD |
| Buffy PDF fixtures | PR6 (`docs/testdata/`) | Small fake charts + expected name/DOB table |
| Shell smokes | Already shipped; keep green | `smoke_orders.sh`, `smoke_extract.sh` |
| Written automated | **PR7** (extend in PR8 for activity) | Schemas + TestClient; mock Gemini; see [TESTING.md](./TESTING.md) |
| Demo seed | Local opt-in | `SEED_DEMO_DATA=true` locally; default/off on Render |

## Security track

Accepted MVP risk: public unauthenticated write + `/extract`. Next hardening is **PR9** (API key + extract rate limit), after tests + UI. Before **real PHI**: auth, durable DB, retention policy, malware scanning — this repo uses fake Buffy data only.

**Note:** The activity / audit log would be stronger with **user names (actor identity)**, but there is **no auth yet** — see DECISIONS (PR8 UI testing adjustments). Revisit when auth/API key lands.

## Later (after PR10)

- Spec B Order fields: `status`, `notes`, `equipment_type`
- Multi-MIME extract (images, DOCX) via `bytes + content_type → draft`
- Citation / page hints; broader DME fields
- Caching / batch / async queues (SPEC S3)
- Dependency scanning CI; CSP beyond platform defaults

## Explicit non-goals (near term)

Full auth/RBAC as P0, real PHI program, malware scanning in MVP+, design-system polish, second ORM/LLM client, parallel apps.

## Small follow-ups (known bugs)

- DOB `<input type="date">` should disallow dates after today (`max` attribute + API validation).

Planning prompt: [prompts/post-pr5-planning-agent.md](./prompts/post-pr5-planning-agent.md).  
**Next (after PR8):** hardening plan prompt — [prompts/plan-pr9-hardening.md](./prompts/plan-pr9-hardening.md) (plan only; get human approval before implementing PR9).
