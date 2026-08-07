"""Activity log list — metadata only (no PDF bytes). Does not log itself (avoids feedback loops)."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from data_extracting_backend.db import get_db
from data_extracting_backend.models import ActivityLog
from data_extracting_backend.schemas import ActivityRead

router = APIRouter(prefix="/activity", tags=["activity"])


@router.get("", response_model=list[ActivityRead])
def list_activity(
    db: Session = Depends(get_db),
    limit: int = Query(default=50, ge=1, le=200),
) -> list[ActivityLog]:
    return list(
        db.scalars(
            select(ActivityLog).order_by(ActivityLog.id.desc()).limit(limit)
        ).all()
    )
