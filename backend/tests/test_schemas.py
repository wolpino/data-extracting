"""Unit tests: filename sanitize + Order schema validation."""

from datetime import date

import pytest
from pydantic import ValidationError

from data_extracting_backend.filenames import sanitize_source_filename
from data_extracting_backend.schemas import OrderCreate


def test_sanitize_accepts_basename() -> None:
    assert sanitize_source_filename("chart.pdf") == "chart.pdf"


@pytest.mark.parametrize(
    "bad",
    ["../evil.pdf", "a/b.pdf", r"a\b.pdf", ".", "..", "  ", ""],
)
def test_sanitize_rejects_paths_and_blank(bad: str) -> None:
    with pytest.raises(ValueError):
        sanitize_source_filename(bad)


def test_order_create_happy() -> None:
    order = OrderCreate(
        first_name=" Buffy ",
        last_name="Summers",
        date_of_birth=date(1981, 1, 19),
        source_filename="buffy-summers-chart.pdf",
    )
    assert order.first_name == "Buffy"
    assert order.source_filename == "buffy-summers-chart.pdf"


def test_order_create_rejects_blank_name() -> None:
    with pytest.raises(ValidationError):
        OrderCreate(
            first_name="   ",
            last_name="Summers",
            date_of_birth=date(1981, 1, 19),
        )


def test_order_create_rejects_pathy_filename() -> None:
    with pytest.raises(ValidationError):
        OrderCreate(
            first_name="Buffy",
            last_name="Summers",
            date_of_birth=date(1981, 1, 19),
            source_filename="../evil.pdf",
        )


def test_order_create_rejects_invalid_dob() -> None:
    with pytest.raises(ValidationError):
        OrderCreate(
            first_name="Buffy",
            last_name="Summers",
            date_of_birth="not-a-date",  # type: ignore[arg-type]
        )
