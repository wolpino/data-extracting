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
        "patient",
        "name",
        "first name",
        "last name",
        "-",
        "--",
        "tbd",
    }
)

_INCOMPLETE_DETAIL = (
    "Could not extract first name, last name, and date of birth from this PDF. "
    "All three fields are required and must appear in the document — try a clearer chart."
)


class ExtractDraft(BaseModel):
    """API draft — only returned when all three demographics are present and real."""

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


class ExtractCandidate(BaseModel):
    """LLM schema — optional fields + flag so missing data does not force invented names.

    A required-only schema made Gemini invent demographics for unrelated PDFs.
    """

    demographics_found: bool = False
    first_name: str | None = None
    last_name: str | None = None
    date_of_birth: date | None = None


_EXTRACT_PROMPT = """You extract patient demographics from a document for a medical intake tool.

Set demographics_found=true ONLY if the document clearly contains ALL of:
  - patient first name
  - patient last name
  - patient date of birth
and you can read each from the document text (not from guesses).

If this is not a patient chart / intake / clinical document with those fields
(for example a random PDF, invoice, or resume without DOB), set
demographics_found=false and set first_name, last_name, and date_of_birth to null.

Never invent names or dates. Never use N/A, Unknown, None, or placeholder values.
Do not assume a Buffy demo patient or any template.
"""


def _is_pdf(filename: str | None, content_type: str | None) -> bool:
    name = (filename or "").lower()
    ctype = (content_type or "").lower()
    return name.endswith(".pdf") or ctype in {"application/pdf", "application/x-pdf"}


def _reject_incomplete() -> None:
    raise HTTPException(status_code=422, detail=_INCOMPLETE_DETAIL)


def candidate_to_draft(candidate: ExtractCandidate) -> ExtractDraft:
    """Promote an LLM candidate to an API draft, or 422 if incomplete / placeholder."""
    if not candidate.demographics_found:
        _reject_incomplete()
    if (
        candidate.first_name is None
        or candidate.last_name is None
        or candidate.date_of_birth is None
    ):
        _reject_incomplete()
    try:
        return ExtractDraft(
            first_name=candidate.first_name,
            last_name=candidate.last_name,
            date_of_birth=candidate.date_of_birth,
        )
    except Exception as exc:
        raise HTTPException(status_code=422, detail=_INCOMPLETE_DETAIL) from exc


def validate_extract_draft(draft: ExtractDraft) -> ExtractDraft:
    """Re-validate a draft (placeholders → 422)."""
    try:
        return ExtractDraft.model_validate(draft.model_dump())
    except Exception as exc:
        raise HTTPException(status_code=422, detail=_INCOMPLETE_DETAIL) from exc


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
        # Optional-field schema — required-only schemas encouraged hallucinated names.
        response = client.models.generate_content(
            model=settings.gemini_model,
            contents=[
                types.Part.from_bytes(data=data, mime_type="application/pdf"),
                _EXTRACT_PROMPT,
            ],
            config={
                "response_mime_type": "application/json",
                "response_schema": ExtractCandidate,
            },
        )
    except Exception as exc:  # noqa: BLE001 — surface clean 502 to clients
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Gemini extraction failed",
        ) from exc

    parsed = response.parsed
    candidate: ExtractCandidate | None = None
    try:
        if isinstance(parsed, ExtractCandidate):
            candidate = parsed
        elif parsed is not None:
            candidate = ExtractCandidate.model_validate(parsed)
        elif response.text:
            candidate = ExtractCandidate.model_validate_json(response.text)
    except Exception:
        _reject_incomplete()

    if candidate is None:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Gemini returned an empty extract result",
        )

    return candidate_to_draft(candidate)
