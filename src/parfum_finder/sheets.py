"""Writing a search result onto the user's own Google Sheets wishlist.

The wishlist is theirs, not this app's: it already exists, its columns are
whatever they typed, and the app never adds rows to it. All it does is find
the row a search result is about and fill in two columns they add themselves,
BEST PRICE and WHERE. If it can't find the row with confidence, it says so and
leaves the sheet untouched -- writing a price onto the wrong wishlist row is
worse than not writing one at all.

Import of gspread is deferred into the functions that need it so the rest of
the app runs without the optional `sheets` extra installed.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from parfum_finder.logging_setup import logger
from parfum_finder.matcher import PREFILTER_THRESHOLD, Match, PerfumeQuery, match_title

if TYPE_CHECKING:
    import gspread


class SheetsError(Exception):
    """Something about the sheet itself is wrong: auth, network, missing tab
    or header. Always caught at the call site and shown as a notice, never
    let through to crash the TUI."""


@dataclass(frozen=True)
class WishlistRow:
    """One perfume as it sits in the wishlist: which sheet row it is on, and
    the brand/model text as typed there.

    `row_index` is the real, 1-based Sheets row number, not a position in a
    Python list -- write_result writes straight to this row later, and a
    list-index vs sheet-row mismatch here would silently overwrite the wrong
    line.
    """

    row_index: int
    brand: str
    model: str


def open_worksheet(
    credentials_path: Any, spreadsheet: str, worksheet_name: str
) -> gspread.Worksheet:
    """Authorize with a service account and return the target tab.

    `spreadsheet` may be a full sheet URL or a bare spreadsheet ID; gspread
    only opens by one or the other, so both are tried.
    """
    try:
        import gspread
    except ImportError as exc:
        raise SheetsError(
            "gspread yüklü değil. `uv sync --extra sheets` ile kurun."
        ) from exc

    try:
        client = gspread.service_account(filename=credentials_path)
        if spreadsheet.startswith("http://") or spreadsheet.startswith("https://"):
            book = client.open_by_url(spreadsheet)
        else:
            book = client.open_by_key(spreadsheet)
        return book.worksheet(worksheet_name)
    except FileNotFoundError as exc:
        raise SheetsError(
            f"Servis hesabı anahtarı bulunamadı: {credentials_path}"
        ) from exc
    except Exception as exc:
        # Auth failures (bad/expired key) surface from google-auth, not
        # gspread, and spreadsheet/worksheet-not-found surface from gspread's
        # own exception hierarchy -- caught broadly here so any of them turns
        # into a notice instead of a crash.
        raise SheetsError(f"Sheet açılamadı: {exc}") from exc


def read_sheet(ws: gspread.Worksheet) -> tuple[list[str], list[WishlistRow]]:
    """Read the whole tab in one request: the header row, and every wishlist
    row under it.

    Column A carries the brand, but the sheet shows it as vertically merged
    cells grouping several models under one brand, and the Sheets API only
    returns a value on the merge's top-left cell. Every cell under it comes
    back empty, so the brand for a model row is whatever column A last had
    something in, walking down. A blank column B is a spacer row between
    brand groups: it is skipped without disturbing that running brand, since
    the next model row still belongs to it.
    """
    try:
        all_values = ws.get_all_values()
    except Exception as exc:  # gspread wraps requests/google-auth errors variably
        raise SheetsError(f"Sheet okunamadı: {exc}") from exc

    if not all_values:
        return [], []

    header_row = all_values[0]
    rows: list[WishlistRow] = []
    last_seen_brand: str | None = None
    for row_index, cells in enumerate(all_values[1:], start=2):
        brand_cell = cells[0].strip() if len(cells) > 0 else ""
        model_cell = cells[1].strip() if len(cells) > 1 else ""
        if brand_cell:
            last_seen_brand = brand_cell
        if not model_cell:
            continue
        if last_seen_brand is None:
            # A model with no brand ever seen above it -- a malformed sheet
            # (or a model in row 2 before any brand cell). Nothing to file it
            # under, so it's skipped and logged rather than stored with a
            # blank brand that would never match anything correctly.
            logger.warning(
                "sheets: satır %d ('%s') için marka bulunamadı, atlanıyor",
                row_index,
                model_cell,
            )
            continue
        rows.append(
            WishlistRow(row_index=row_index, brand=last_seen_brand, model=model_cell)
        )
    return header_row, rows


def find_match(
    rows: list[WishlistRow], query: PerfumeQuery
) -> tuple[WishlistRow, Match] | None:
    """The wishlist row that best names the same perfume as `query`, if any
    clears the floor score. Reuses match_title, the same scoring the results
    table itself is built on, so a sheet row and a site title are judged the
    same way."""
    best: tuple[WishlistRow, Match] | None = None
    for row in rows:
        title = f"{row.brand} {row.model}"
        match = match_title(title, query, threshold=PREFILTER_THRESHOLD)
        if match is None:
            continue
        if best is None or match.score > best[1].score:
            best = (row, match)
    return best


def find_header_columns(header_row: list[str]) -> tuple[int, int]:
    """The 1-based columns holding BEST PRICE and WHERE, as the user typed
    them into row 1. Raises if either is missing -- there is nowhere to
    write without them, and guessing a column would risk overwriting a
    column that means something else."""
    price_col = None
    where_col = None
    for index, header in enumerate(header_row, start=1):
        if header == "BEST PRICE":
            price_col = index
        elif header == "WHERE":
            where_col = index
    missing = [
        name
        for name, col in (("BEST PRICE", price_col), ("WHERE", where_col))
        if col is None
    ]
    if missing:
        raise SheetsError(f"Sheet'te şu başlık(lar) bulunamadı: {', '.join(missing)}")
    assert price_col is not None and where_col is not None
    return price_col, where_col


def _sanitized(text: str) -> str:
    """Escape double quotes for use inside a Sheets formula's quoted string
    argument. Without this, a `"` in a site name or URL closes the formula's
    string early and breaks it (or reshapes what the formula does)."""
    return text.replace('"', '""')


def write_result(
    ws: gspread.Worksheet,
    row_index: int,
    price_col: int,
    where_col: int,
    price_text: str,
    site_label: str,
    product_url: str | None,
) -> None:
    """Write the price and the site, in one request.

    WHERE is a HYPERLINK formula when a product URL exists, so the site name
    is clickable straight to the product page; otherwise it's just the site
    name as plain text.
    """
    from gspread.utils import ValueInputOption, rowcol_to_a1

    if product_url:
        safe_url = _sanitized(product_url)
        safe_label = _sanitized(site_label)
        where_value = f'=HYPERLINK("{safe_url}","{safe_label}")'
    else:
        where_value = site_label

    try:
        ws.batch_update(
            [
                {
                    "range": rowcol_to_a1(row_index, price_col),
                    "values": [[price_text]],
                },
                {
                    "range": rowcol_to_a1(row_index, where_col),
                    "values": [[where_value]],
                },
            ],
            value_input_option=ValueInputOption.user_entered,
        )
    except Exception as exc:
        raise SheetsError(f"Sheet'e yazılamadı: {exc}") from exc
