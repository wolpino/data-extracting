# Testing standard (PR7+)

**Mandate:** Automated tests follow this matrix. Agents must not invent coverage that requires network, a live Gemini key, or the developer’s `app.db`.

## How to run

```bash
cd backend
uv sync --all-groups   # or uv sync --dev
uv run pytest
```

Default suite must pass **without** `GEMINI_API_KEY` and without network.

Optional live extract (local only):

```bash
uv run pytest -m integration   # skipped unless GEMINI_API_KEY is set
```

Shell smokes remain for quick manual/prod checks: `./backend/scripts/smoke_orders.sh`, `smoke_extract.sh`.

## Setup constraints

1. **Isolated DB** — temp SQLite per test session/fixture; never use `backend/app.db` or Render.
2. **Rebind engine** — after setting `DATABASE_URL`, call `get_settings.cache_clear()` and `setup_engine()` (see `db.py`).
3. **`SEED_DEMO_DATA=false` in tests** — demo Buffy seed is opt-in for local `.env` only; production/Render defaults off.
4. **Mock Gemini** — patch `extract_patient_draft` (or the genai client) in default tests; do not assert specific LLM name/DOB output unless `@pytest.mark.integration`.
5. **No PDF bytes in activity assertions** — metadata only.
6. **Dev dependency** — `pytest` (+ `httpx` for TestClient) via uv; not a runtime dep.

## Required matrix (happy + edge)

| Area | Happy path | Edge / negative |
|------|------------|-----------------|
| Orders CRUD | create → get → list → put/patch → delete | 404; blank names → 422; invalid DOB → 422 |
| Filename sanitize | basename `chart.pdf` accepted | `../evil.pdf`, `a/b.pdf` → validation error (exact behavior of `filenames.py`) |
| Extract | mocked PDF → 200 draft JSON | non-PDF → 415; empty → 400; oversize → 413; missing key → 503; Gemini error → 502 |
| Confirm-before-save | extract leaves order count unchanged; confirm → +1 | confirm bad body → 422; confirm does not call Gemini |
| Seed | with `SEED_DEMO_DATA=false`, list does not require a Buffy row | optional: `true` seeds Buffy Summers once |

Name tests after invariants (`test_extract_does_not_persist_order`). Prefer status + one field / count delta over full JSON dumps. Parametrize edges.

## Explicit non-goals (PR7)

- No Playwright / UI tests (PR8 manual).
- No load/perf; no prompt snapshot tests.
- Do not assert Buffy PDF → exact Gemini fields in the default suite.
- Activity **list** covered in PR8 (`test_activity_api.py`).

## Before writing tests

Read: `schemas.py`, `filenames.py`, `extract.py`, `api/v1/orders.py`, `api/v1/extract.py`, `smoke_*.sh`. Match real status codes. Append decisions to `DECISIONS.md` if behavior changes.
