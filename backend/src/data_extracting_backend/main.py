from fastapi import FastAPI

from data_extracting_backend.config import get_settings

app = FastAPI(
    title="Data Extracting API",
    version="0.1.0",
    description="Order CRUD + document extract MVP (scaffold).",
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/v1/health")
def api_health() -> dict[str, str]:
    settings = get_settings()
    return {
        "status": "ok",
        "database_configured": "true" if settings.database_url else "false",
    }
