"""PDF extract endpoint — returns a draft only; never persists an Order."""

from fastapi import APIRouter, Depends, File, Request, UploadFile, status
from sqlalchemy.orm import Session

from data_extracting_backend.activity import log_activity
from data_extracting_backend.config import Settings, get_settings
from data_extracting_backend.db import get_db
from data_extracting_backend.extract import ExtractDraft, extract_patient_draft

router = APIRouter(tags=["extract"])


@router.post(
    "/extract",
    response_model=ExtractDraft,
    status_code=status.HTTP_200_OK,
)
async def extract_document(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> ExtractDraft:
    data = await file.read()
    draft = extract_patient_draft(
        data,
        content_type=file.content_type,
        filename=file.filename,
        settings=settings,
    )
    # Metadata only — never log PDF bytes.
    log_activity(
        db,
        action="extract",
        entity_type="document",
        method=request.method,
        path=str(request.url.path),
        detail=f"filename={file.filename or 'unknown'}; bytes={len(data)}",
    )
    db.commit()
    return draft
