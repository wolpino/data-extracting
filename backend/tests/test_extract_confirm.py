"""Extract + confirm invariants (Gemini mocked by default)."""

from __future__ import annotations

import pytest
from fastapi import HTTPException

from data_extracting_backend.extract import ExtractDraft


def _order_count(client) -> int:
    return len(client.get("/api/v1/orders").json())


def test_extract_rejects_non_pdf(client) -> None:
    res = client.post(
        "/api/v1/extract",
        files={"file": ("notes.txt", b"not a pdf", "text/plain")},
    )
    assert res.status_code == 415


def test_extract_rejects_empty_pdf(client) -> None:
    res = client.post(
        "/api/v1/extract",
        files={"file": ("empty.pdf", b"", "application/pdf")},
    )
    assert res.status_code == 400


def test_extract_rejects_oversize(client, monkeypatch: pytest.MonkeyPatch) -> None:
    from data_extracting_backend.config import get_settings

    monkeypatch.setenv("MAX_UPLOAD_BYTES", "10")
    get_settings.cache_clear()
    res = client.post(
        "/api/v1/extract",
        files={"file": ("big.pdf", b"0123456789ABCDEF", "application/pdf")},
    )
    assert res.status_code == 413
    get_settings.cache_clear()


def test_extract_requires_gemini_key_when_not_mocked(client) -> None:
    # Fixture clears GEMINI_API_KEY; no mock → 503 before calling Google.
    res = client.post(
        "/api/v1/extract",
        files={"file": ("chart.pdf", b"%PDF-1.4 fake", "application/pdf")},
    )
    assert res.status_code == 503


def test_extract_does_not_persist_order(client, mock_extract_draft: ExtractDraft) -> None:
    before = _order_count(client)
    res = client.post(
        "/api/v1/extract",
        files={"file": ("chart.pdf", b"%PDF-1.4 fake", "application/pdf")},
    )
    assert res.status_code == 200
    assert res.json()["first_name"] == mock_extract_draft.first_name
    assert _order_count(client) == before


def test_confirm_persists_order(client) -> None:
    before = _order_count(client)
    res = client.post(
        "/api/v1/orders/confirm",
        json={
            "first_name": "Buffy",
            "last_name": "Summers",
            "date_of_birth": "1981-01-19",
            "source_filename": "buffy-summers-chart.pdf",
        },
    )
    assert res.status_code == 201
    assert _order_count(client) == before + 1


def test_confirm_rejects_pathy_filename(client) -> None:
    res = client.post(
        "/api/v1/orders/confirm",
        json={
            "first_name": "Spike",
            "last_name": "Pratt",
            "date_of_birth": "1970-06-06",
            "source_filename": "a/b.pdf",
        },
    )
    assert res.status_code == 422


def test_extract_surfaces_gemini_failure(
    client, monkeypatch: pytest.MonkeyPatch
) -> None:
    def _boom(*_a, **_k):
        raise HTTPException(status_code=502, detail="Gemini extraction failed")

    monkeypatch.setattr(
        "data_extracting_backend.api.v1.extract.extract_patient_draft",
        _boom,
    )
    res = client.post(
        "/api/v1/extract",
        files={"file": ("chart.pdf", b"%PDF-1.4 fake", "application/pdf")},
    )
    assert res.status_code == 502
