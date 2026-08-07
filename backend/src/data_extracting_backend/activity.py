"""Activity logging helpers — metadata only; never store PDF/file bytes."""

from sqlalchemy.orm import Session

from data_extracting_backend.models import ActivityLog


def log_activity(
    db: Session,
    *,
    action: str,
    entity_type: str,
    entity_id: int | None = None,
    method: str | None = None,
    path: str | None = None,
    detail: str | None = None,
) -> None:
    db.add(
        ActivityLog(
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            method=method,
            path=path,
            detail=detail,
        )
    )
