"""Extract draft validation — never accept N/A / placeholder demographics."""

from datetime import date

import pytest
from fastapi import HTTPException

from data_extracting_backend.extract import ExtractDraft, validate_extract_draft


def test_validate_accepts_real_names() -> None:
    draft = validate_extract_draft(
        ExtractDraft(
            first_name="Buffy",
            last_name="Summers",
            date_of_birth=date(1981, 1, 19),
        )
    )
    assert draft.first_name == "Buffy"


@pytest.mark.parametrize("bad", ["N/A", "n/a", "Unknown", "none", "  "])
def test_validate_rejects_placeholder_names(bad: str) -> None:
    with pytest.raises(HTTPException) as exc:
        validate_extract_draft(
            ExtractDraft.model_construct(
                first_name=bad,
                last_name="Summers",
                date_of_birth=date(1981, 1, 19),
            )
        )
    assert exc.value.status_code == 422


def test_extract_draft_model_rejects_na() -> None:
    with pytest.raises(Exception):
        ExtractDraft(
            first_name="N/A",
            last_name="Summers",
            date_of_birth=date(1981, 1, 19),
        )
