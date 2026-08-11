"""Tests for the Google Sheets wishlist module: forward-fill reading, matching,
header lookup, and the write path's formula sanitization.

No real network or gspread client is involved -- a fake worksheet object
stands in, exposing only the surface the module actually calls.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from parfum_finder.matcher import parse_query
from parfum_finder.sheets import (
    SheetsError,
    WishlistRow,
    find_header_columns,
    find_match,
    open_worksheet,
    read_sheet,
    write_result,
)


class _FakeWorksheet:
    """Records batch_update calls; get_all_values returns canned rows."""

    def __init__(self, values: list[list[str]]) -> None:
        self._values = values
        self.batch_update_calls: list[Any] = []

    def get_all_values(self) -> list[list[str]]:
        return self._values

    def batch_update(self, data: Any, value_input_option: Any = None) -> None:
        self.batch_update_calls.append((data, value_input_option))


def test_open_worksheet_expands_a_tilde_in_the_credentials_path(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # A path read from .env never passes through a shell, so "~" arrives
    # literally -- gspread would look for a file named "~" and raise
    # FileNotFoundError if this isn't expanded first.
    import gspread

    seen: list[Any] = []

    def fake_service_account(*, filename: Any) -> Any:
        seen.append(filename)
        raise RuntimeError("stop before any real auth/network call")

    monkeypatch.setattr(gspread, "service_account", fake_service_account)

    with pytest.raises(SheetsError):
        open_worksheet("~/creds.json", "sheet-id", "Sheet1")

    assert seen == [Path("~/creds.json").expanduser()]


def test_read_sheet_forward_fills_the_merged_brand_across_its_models() -> None:
    ws = _FakeWorksheet(
        [
            ["BRAND", "PARFUM"],
            ["Dior", "Sauvage EDP"],
            ["", "Sauvage EDT"],
            ["", ""],  # spacer row between brand groups
            ["Chanel", "Bleu de Chanel EDP"],
        ]
    )
    header, rows = read_sheet(ws)
    assert header == ["BRAND", "PARFUM"]
    assert rows == [
        WishlistRow(row_index=2, brand="Dior", model="Sauvage EDP"),
        WishlistRow(row_index=3, brand="Dior", model="Sauvage EDT"),
        WishlistRow(row_index=5, brand="Chanel", model="Bleu de Chanel EDP"),
    ]


def test_read_sheet_row_index_is_the_real_sheet_row_not_a_list_position() -> None:
    # Row 1 is the header; the first data row must come back as sheet row 2,
    # not 0 or 1, or a later write would land one row off from where it read.
    ws = _FakeWorksheet([["BRAND", "PARFUM"], ["Dior", "Sauvage EDP"]])
    _, rows = read_sheet(ws)
    assert rows[0].row_index == 2


def test_read_sheet_skips_a_model_with_no_brand_ever_seen_above_it(
    caplog: pytest.LogCaptureFixture,
) -> None:
    ws = _FakeWorksheet([["BRAND", "PARFUM"], ["", "Orphan Model"]])
    with caplog.at_level("WARNING"):
        _, rows = read_sheet(ws)
    assert rows == []


def test_read_sheet_on_an_empty_sheet_returns_nothing() -> None:
    header, rows = read_sheet(_FakeWorksheet([]))
    assert header == []
    assert rows == []


def test_find_header_columns_locates_both_by_name() -> None:
    header = ["BRAND", "PARFUM", "BEST PRICE", "WHERE"]
    price_col, where_col = find_header_columns(header)
    assert (price_col, where_col) == (3, 4)


def test_find_header_columns_raises_naming_the_missing_header() -> None:
    with pytest.raises(SheetsError, match="WHERE"):
        find_header_columns(["BRAND", "PARFUM", "BEST PRICE"])


def test_find_match_picks_the_best_scoring_wishlist_row() -> None:
    rows = [
        WishlistRow(row_index=2, brand="Dior", model="Sauvage EDT"),
        WishlistRow(row_index=3, brand="Dior", model="Sauvage EDP"),
    ]
    query = parse_query("Dior Sauvage EDP")
    found = find_match(rows, query)
    assert found is not None
    matched_row, match = found
    assert matched_row.row_index == 3
    assert match.confident


def test_find_match_returns_none_when_nothing_clears_the_floor_score() -> None:
    rows = [WishlistRow(row_index=2, brand="Chanel", model="Bleu de Chanel EDP")]
    query = parse_query("Dior Sauvage EDP")
    assert find_match(rows, query) is None


def test_write_result_batches_both_cells_into_one_request() -> None:
    ws = _FakeWorksheet([])
    write_result(
        ws, 5, 3, 4, "150.00 ₺ (3 ml)", "Dekant Doktoru", "https://example.com/p"
    )
    assert len(ws.batch_update_calls) == 1
    data, _ = ws.batch_update_calls[0]
    assert len(data) == 2


def test_write_result_sanitizes_a_quote_so_the_formula_stays_valid() -> None:
    ws = _FakeWorksheet([])
    write_result(ws, 5, 3, 4, "150.00 ₺", 'Site "Deals" Co', "https://example.com/p")
    data, _ = ws.batch_update_calls[0]
    where_value = data[1]["values"][0][0]
    assert where_value == '=HYPERLINK("https://example.com/p","Site ""Deals"" Co")'


def test_write_result_writes_plain_site_label_when_there_is_no_product_url() -> None:
    ws = _FakeWorksheet([])
    write_result(ws, 5, 3, 4, "150.00 ₺", "Dekant Doktoru", None)
    data, _ = ws.batch_update_calls[0]
    assert data[1]["values"][0][0] == "Dekant Doktoru"
