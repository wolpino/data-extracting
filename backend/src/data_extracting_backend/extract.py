"""Document → draft fields. PDF-only in MVP; boundary is bytes + content_type."""

from __future__ import annotations

from datetime import date

from fastapi import HTTPException, status
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

from data_extracting_backend.config import Settings


class ExtractDraft(BaseModel):
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    date_of_birth: date


_EXTRACT_PROMPT = """Extract the patient's demographics from this document.
Return only the patient's first name, last name, and date of birth.
If a field is missing or unclear, use your best reading of the document;
prefer empty string for names and 1900-01-01 for DOB only if truly absent.
This may be any PDF (fax, form, chart) — do not assume a specific template.
"""


def _is_pdf(filename: str | None, content_type: str | None) -> bool:
    name = (filename or "").lower()
    ctype = (content_type or "").lower()
    return name.endswith(".pdf") or ctype in {"application/pdf", "application/x-pdf"}


def extract_patient_draft(
    data: bytes,
    *,
    content_type: str | None,
    filename: str | None,
    settings: Settings,
) -> ExtractDraft:
    if not _is_pdf(filename, content_type):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Only PDF uploads are supported in MVP",
        )
    if len(data) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty",
        )
    if len(data) > settings.max_upload_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"PDF exceeds max size of {settings.max_upload_bytes} bytes",
        )
    if not settings.gemini_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="GEMINI_API_KEY is not configured",
        )

    client = genai.Client(api_key=settings.gemini_api_key)
    try:
        # Inline PDF bytes — no Files API round-trip for MVP sizes.
        response = client.models.generate_content(
            model=settings.gemini_model,
            contents=[
                types.Part.from_bytes(data=data, mime_type="application/pdf"),
                _EXTRACT_PROMPT,
            ],
            config={
                "response_mime_type": "application/json",
                "response_schema": ExtractDraft,
            },
        )
    except Exception as exc:  # noqa: BLE001 — surface clean 502 to clients
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Gemini extraction failed",
        ) from exc

    parsed = response.parsed
    if isinstance(parsed, ExtractDraft):
        return parsed
    if parsed is not None:
        return ExtractDraft.model_validate(parsed)
    if response.text:
        return ExtractDraft.model_validate_json(response.text)
    raise HTTPException(
        status_code=status.HTTP_502_BAD_GATEWAY,
        detail="Gemini returned an empty extract result",
    )
