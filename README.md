# data-extracting

GenHealth take-home MVP: Order CRUD + PDF extract (confirm-before-save).

See [docs/SPEC.md](docs/SPEC.md) for scope and [docs/PROGRESS.md](docs/PROGRESS.md) for current status.

## Local quickstart

```bash
# API
cd backend && uv sync && uv run uvicorn data_extracting_backend.main:app --reload --port 8000

# UI (separate terminal)
cd frontend && npm install && npm run dev
```

### Quick API smoke (Order CRUD)

```bash
./backend/scripts/smoke_orders.sh
```

See [backend/README.md](backend/README.md) for curl cheatsheet and OpenAPI (`/docs`).

Copy `.env.example` values as needed. Full architecture notes land in PR5.

Post-PR5 planning handoff prompt: [docs/prompts/post-pr5-planning-agent.md](docs/prompts/post-pr5-planning-agent.md).
