"""FastAPI entrypoint: schema init, demo seed, /health + /api/v1 routes."""

from contextlib import asynccontextmanager
from datetime import date

from fastapi import FastAPI
from sqlalchemy import select

from data_extracting_backend.api.v1 import api_router
from data_extracting_backend.config import get_settings
from data_extracting_backend.db import SessionLocal, init_db
from data_extracting_backend.models import Order


def seed_demo_order() -> None:
    """Idempotent Buffy-named demo row for local smoke tests (fake data only)."""
    with SessionLocal() as db:
        existing = db.scalars(
            select(Order).where(
                Order.first_name == "Buffy",
                Order.last_name == "Summers",
            )
        ).first()
        if existing is not None:
            return
        db.add(
            Order(
                first_name="Buffy",
                last_name="Summers",
                date_of_birth=date(1981, 1, 19),
                source_filename=None,
            )
        )
        db.commit()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Create tables then seed once — safe to re-run on reload.
    init_db()
    seed_demo_order()
    yield


app = FastAPI(
    title="Data Extracting API",
    version="0.1.0",
    description="Order CRUD + document extract MVP.",
    lifespan=lifespan,
)

app.include_router(api_router)


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
