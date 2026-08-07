# Frontend

Vite + React + TypeScript thin UI.

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

`VITE_API_BASE_URL` must point at the FastAPI origin (default `http://localhost:8000`).

Orders UI (PR3): list / create / edit / delete with an explicit **Confirm** step before any mutating API call.

Backend must allow the Vite origin via `CORS_ORIGINS` (default `http://localhost:5173`).
