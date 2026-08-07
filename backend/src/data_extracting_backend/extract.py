"""Document → draft fields. PDF-only in MVP; boundary is bytes + content_type."""

from __future__ import annotations

from datetime import date

from fastapi import HTTPException, status
from google import genai
from google.genai import types
from pydantic import BaseModel, Field, field_validator

from data_extracting_backend.config import Settings

# Placeholders models sometimes invent — treat as missing, never accept as draft.
_BAD_NAME_TOKENS = frozenset(
    {
        "n/a",
        "na",
        "n.a.",
        "none",
        "null",
        "unknown",
        "missing",
        "not available",
        "not found",
        "-",
        "--",
        "tbd",
    }
)


class ExtractDraft(BaseModel):
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    date_of_birth: date

    @field_validator("first_name", "last_name")
    @classmethod
    def names_must_be_real(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned or cleaned.casefold() in _BAD_NAME_TOKENS:
            raise ValueError("name is missing or placeholder")
        return cleaned


_EXTRACT_PROMPT = """Extract the patient's demographics from this document.
Return JSON with first_name, last_name, and date_of_birth only when all three
are clearly present in the document.
Do NOT invent values. Do NOT use N/A, Unknown, None, or placeholder dates.
If any of the three fields cannot be read with confidence, respond with an error
by omitting a valid complete result (the API will reject incomplete extracts).
This may be any PDF (fax, form, chart) — do not assume a specific template.
"""


def _is_pdf(filename: str | None, content_type: str | None) -> bool:
    name = (filename or "").lower()
    ctype = (content_type or "").lower()
    return name.endswith(".pdf") or ctype in {"application/pdf", "application/x-pdf"}


def _reject_incomplete(detail: str) -> None:
    raise HTTPException(
        status_code=422,
        detail=detail,
    )


def validate_extract_draft(draft: ExtractDraft) -> ExtractDraft:
    """All three fields required; reject N/A-style placeholders (never return a partial draft)."""
    try:
        return ExtractDraft.model_validate(draft.model_dump())
    except Exception as exc:
        raise HTTPException(
            status_code=422,
            detail=(
                "Could not extract first name, last name, and date of birth from this PDF. "
                "All three fields are required — try a clearer document."
            ),
        ) from exc


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
    draft: ExtractDraft | None = None
    try:
        if isinstance(parsed, ExtractDraft):
            draft = parsed
        elif parsed is not None:
            draft = ExtractDraft.model_validate(parsed)
        elif response.text:
            draft = ExtractDraft.model_validate_json(response.text)
    except Exception:
        raise HTTPException(
            status_code=422,
            detail=(
                "Could not extract first name, last name, and date of birth from this PDF. "
                "All three fields are required — try a clearer document."
            ),
        ) from None

    if draft is None:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Gemini returned an empty extract result",
        )

    return validate_extract_draft(draft)
