"""SQLAlchemy engine/session. Bound at import from DATABASE_URL — restart after env changes."""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from data_extracting_backend.config import get_settings


class Base(DeclarativeBase):
    pass


def _engine_kwargs(url: str) -> dict:
    if url.startswith("sqlite"):
        # SQLite: allow FastAPI's multi-thread request handling on one connection.
        return {"connect_args": {"check_same_thread": False}}
    return {}


settings = get_settings()
engine = create_engine(settings.database_url, **_engine_kwargs(settings.database_url))
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    # Import models so metadata is registered before create_all.
    from data_extracting_backend import models  # noqa: F401

    # MVP: create_all only; Alembic is a later roadmap item.
    Base.metadata.create_all(bind=engine)
