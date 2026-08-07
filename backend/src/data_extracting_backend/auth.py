"""Shared demo API key for write + extract routes (PR9). Not full user auth."""

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader

from data_extracting_backend.config import Settings, get_settings

# auto_error=False so missing header is allowed when API_KEY env is unset (local open).
_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def require_api_key(
    api_key: str | None = Security(_api_key_header),
    settings: Settings = Depends(get_settings),
) -> None:
    """Reject mutating calls when API_KEY is configured and X-API-Key mismatches."""
    expected = (settings.api_key or "").strip()
    if not expected:
        return
    if not api_key or api_key.strip() != expected:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )
