"""Shared fixtures: temp SQLite, no demo seed, TestClient with lifespan."""

from __future__ import annotations

from collections.abc import Generator
from datetime import date
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from data_extracting_backend.config import get_settings
from data_extracting_backend.db import setup_engine
from data_extracting_backend.extract import ExtractDraft


@pytest.fixture()
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Generator[TestClient, None, None]:
    db_path = tmp_path / "test.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    monkeypatch.setenv("SEED_DEMO_DATA", "false")
    monkeypatch.setenv("GEMINI_API_KEY", "")
    monkeypatch.setenv("MAX_UPLOAD_BYTES", "1048576")
    get_settings.cache_clear()
    setup_engine()

    # Import after env + engine bind so lifespan uses the temp DB.
    from data_extracting_backend.main import app

    with TestClient(app) as test_client:
        yield test_client

    get_settings.cache_clear()


@pytest.fixture()
def mock_extract_draft(monkeypatch: pytest.MonkeyPatch) -> ExtractDraft:
    draft = ExtractDraft(
        first_name="Willow",
        last_name="Rosenberg",
        date_of_birth=date(1981, 5, 1),
    )

    def _fake(*_args, **_kwargs) -> ExtractDraft:
        return draft

    monkeypatch.setattr(
        "data_extracting_backend.api.v1.extract.extract_patient_draft",
        _fake,
    )
    return draft
