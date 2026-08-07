"""Extract draft validation — never accept N/A / missing demographics."""

from datetime import date

import pytest
from fastapi import HTTPException

from data_extracting_backend.extract import (
    ExtractCandidate,
    ExtractDraft,
    candidate_to_draft,
    validate_extract_draft,
)


def test_validate_accepts_real_names() -> None:
    draft = validate_extract_draft(
        ExtractDraft(
            first_name="Buffy",
            last_name="Summers",
            date_of_birth=date(1981, 1, 19),
        )
    )
    assert draft.first_name == "Buffy"


@pytest.mark.parametrize("bad", ["N/A", "n/a", "Unknown", "none", "  ", "Patient"])
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


def test_candidate_not_found_rejects() -> None:
    with pytest.raises(HTTPException) as exc:
        candidate_to_draft(
            ExtractCandidate(
                demographics_found=False,
                first_name=None,
                last_name=None,
                date_of_birth=None,
            )
        )
    assert exc.value.status_code == 422


def test_candidate_found_false_even_with_names_rejects() -> None:
    # Model must not sneak invents through with demographics_found=false.
    with pytest.raises(HTTPException) as exc:
        candidate_to_draft(
            ExtractCandidate(
                demographics_found=False,
                first_name="Invented",
                last_name="Person",
                date_of_birth=date(1990, 1, 1),
            )
        )
    assert exc.value.status_code == 422


def test_candidate_found_but_partial_rejects() -> None:
    with pytest.raises(HTTPException) as exc:
        candidate_to_draft(
            ExtractCandidate(
                demographics_found=True,
                first_name="Buffy",
                last_name=None,
                date_of_birth=date(1981, 1, 19),
            )
        )
    assert exc.value.status_code == 422


def test_candidate_found_complete_accepts() -> None:
    draft = candidate_to_draft(
        ExtractCandidate(
            demographics_found=True,
            first_name="Buffy",
            last_name="Summers",
            date_of_birth=date(1981, 1, 19),
        )
    )
    assert draft.last_name == "Summers"
