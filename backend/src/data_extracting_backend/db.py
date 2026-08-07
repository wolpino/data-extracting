"""SQLAlchemy engine/session. Bound from DATABASE_URL — call setup_engine() after env changes (tests)."""

from collections.abc import Generator

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from data_extracting_backend.config import get_settings


class Base(DeclarativeBase):
    pass


engine: Engine
SessionLocal: sessionmaker


def _engine_kwargs(url: str) -> dict:
    if url.startswith("sqlite"):
        # SQLite: allow FastAPI's multi-thread request handling on one connection.
        return {"connect_args": {"check_same_thread": False}}
    return {}


def setup_engine(database_url: str | None = None) -> None:
    """(Re)bind global engine/session. Used at import and by tests with a temp DB."""
    global engine, SessionLocal
    url = database_url or get_settings().database_url
    engine = create_engine(url, **_engine_kwargs(url))
    SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


setup_engine()


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
