"""Tests for parfum_finder.normalize.

These cover the required test cases from the module docstring, plus a couple
of formatting round-trips. Getting a price or volume parsed wrong here means
every downstream ranking and basket total is wrong too, so each case is
checked against an exact expected value rather than a rough approximation.
"""

from decimal import Decimal

import pytest

from parfum_finder.normalize import (
    format_ml,
    format_price,
    parse_price,
    parse_size_ml,
)


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("1.250,00 TL", Decimal("1250.00")),
        ("1,250.00", Decimal("1250.00")),
        ("250 TL", Decimal("250")),
        ("₺1.250", Decimal("1250")),
        ("250,50", Decimal("250.50")),
    ],
)
def test_parse_price(raw: str, expected: Decimal) -> None:
    assert parse_price(raw) == expected


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("0,5 ml", Decimal("0.5")),
        ("1.5ml", Decimal("1.5")),
        ("5 ML", Decimal("5")),
        ("5cc", Decimal("5")),
        ("5 cc", Decimal("5")),
    ],
)
def test_parse_size_ml(raw: str, expected: Decimal) -> None:
    assert parse_size_ml(raw) == expected


def test_parse_price_rejects_text_with_no_digits() -> None:
    with pytest.raises(ValueError):
        parse_price("stokta yok")


def test_format_price() -> None:
    assert format_price(Decimal("1250")) == "1,250.00 ₺"
    assert format_price(Decimal("250.5")) == "250.50 ₺"


def test_format_ml() -> None:
    assert format_ml(Decimal("1.5")) == "1.5 ml"
    assert format_ml(Decimal("5")) == "5 ml"
    assert format_ml(Decimal("0.50")) == "0.5 ml"
