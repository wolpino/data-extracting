"""Pydantic request/response models. Filename fields run through basename sanitization."""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from data_extracting_backend.filenames import sanitize_source_filename


class OrderCreate(BaseModel):
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    date_of_birth: date
    source_filename: str | None = Field(default=None, max_length=255)

    @field_validator("first_name", "last_name")
    @classmethod
    def strip_names(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("must not be blank")
        return cleaned

    @field_validator("source_filename")
    @classmethod
    def clean_filename(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return sanitize_source_filename(value)


class OrderUpdate(BaseModel):
    """Full replacement body for PUT."""

    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    date_of_birth: date
    source_filename: str | None = Field(default=None, max_length=255)

    @field_validator("first_name", "last_name")
    @classmethod
    def strip_names(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("must not be blank")
        return cleaned

    @field_validator("source_filename")
    @classmethod
    def clean_filename(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return sanitize_source_filename(value)


class OrderPatch(BaseModel):
    first_name: str | None = Field(default=None, min_length=1, max_length=100)
    last_name: str | None = Field(default=None, min_length=1, max_length=100)
    date_of_birth: date | None = None
    source_filename: str | None = Field(default=None, max_length=255)

    @field_validator("first_name", "last_name")
    @classmethod
    def strip_names(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("must not be blank")
        return cleaned

    @field_validator("source_filename")
    @classmethod
    def clean_filename(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return sanitize_source_filename(value)


class OrderRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    first_name: str
    last_name: str
    date_of_birth: date
    source_filename: str | None
    created_at: datetime
    updated_at: datetime


class ActivityRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    action: str
    entity_type: str
    entity_id: int | None
    method: str | None
    path: str | None
    # Short metadata only — never PDF bytes.
    detail: str | None
    created_at: datetime


class ErrorResponse(BaseModel):
    detail: str
