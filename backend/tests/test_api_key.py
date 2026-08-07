"""API key gate: open when unset; 401 on writes/extract when configured."""

from __future__ import annotations

from datetime import date

import pytest
from fastapi.testclient import TestClient

from data_extracting_backend.config import get_settings
from data_extracting_backend.db import setup_engine


@pytest.fixture()
def client_with_api_key(
    tmp_path, monkeypatch: pytest.MonkeyPatch
) -> TestClient:
    db_path = tmp_path / "keyed.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    monkeypatch.setenv("SEED_DEMO_DATA", "false")
    monkeypatch.setenv("GEMINI_API_KEY", "")
    monkeypatch.setenv("API_KEY", "test-demo-key")
    get_settings.cache_clear()
    setup_engine()

    from data_extracting_backend.main import app

    with TestClient(app) as test_client:
        yield test_client

    get_settings.cache_clear()


def test_list_orders_open_when_api_key_configured(
    client_with_api_key: TestClient,
) -> None:
    # Reads stay open for reviewer browsing / OpenAPI demos.
    response = client_with_api_key.get("/api/v1/orders")
    assert response.status_code == 200


def test_create_order_rejects_missing_key(
    client_with_api_key: TestClient,
) -> None:
    response = client_with_api_key.post(
        "/api/v1/orders",
        json={
            "first_name": "Buffy",
            "last_name": "Summers",
            "date_of_birth": "1981-01-19",
        },
    )
    assert response.status_code == 401


def test_create_order_accepts_valid_key(
    client_with_api_key: TestClient,
) -> None:
    response = client_with_api_key.post(
        "/api/v1/orders",
        headers={"X-API-Key": "test-demo-key"},
        json={
            "first_name": "Buffy",
            "last_name": "Summers",
            "date_of_birth": "1981-01-19",
        },
    )
    assert response.status_code == 201
    assert response.json()["first_name"] == "Buffy"


def test_extract_rejects_missing_key(
    client_with_api_key: TestClient,
    mock_extract_draft,
) -> None:
    response = client_with_api_key.post(
        "/api/v1/extract",
        files={"file": ("chart.pdf", b"%PDF-1.4 fake", "application/pdf")},
    )
    assert response.status_code == 401


def test_extract_accepts_valid_key(
    client_with_api_key: TestClient,
    mock_extract_draft,
) -> None:
    response = client_with_api_key.post(
        "/api/v1/extract",
        headers={"X-API-Key": "test-demo-key"},
        files={"file": ("chart.pdf", b"%PDF-1.4 fake", "application/pdf")},
    )
    assert response.status_code == 200
    assert response.json()["first_name"] == "Willow"


def test_writes_open_when_api_key_unset(client: TestClient) -> None:
    # Default fixture leaves API_KEY unset — local ergonomics unchanged.
    response = client.post(
        "/api/v1/orders",
        json={
            "first_name": "Xander",
            "last_name": "Harris",
            "date_of_birth": str(date(1981, 3, 1)),
        },
    )
    assert response.status_code == 201
