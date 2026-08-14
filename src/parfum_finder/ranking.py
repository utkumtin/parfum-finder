"""Pure sorting and grouping rules for the results table.

No I/O, no Textual state: every function here takes rows (and, once a column
has been picked, the active sort key) and returns a sort key tuple. The
screen owns painting; this module owns what order the rows come out in.
"""

from __future__ import annotations

from decimal import Decimal

from parfum_finder.viewmodels import ResultRow

# The sizes a decant buyer actually chooses between. Site blocks are ordered by
# the cheapest ₺/ml a site offers inside this band, so a shop whose smallest
# bottle is 10 ml cannot take the top of the list on the structural ₺/ml
# advantage a bigger bottle always has.
_BAND_MAX_ML_X10 = 30

# Where a site with nothing in the band goes: after every site that has one,
# ordered among themselves by their own cheapest ₺/ml. Comparing a 10 ml-only
# shop against the band would be comparing two different purchases.
_OUT_OF_BAND = 1

# And where a site whose every price failed to read goes: last, since there is
# no number to place it by at all.
_UNPRICED: tuple[int, Decimal] = (2, Decimal(0))


def site_ranks(
    rows: list[ResultRow],
) -> dict[tuple[int, str, str], tuple[int, Decimal]]:
    """What each site charges for the product a block is about.

    One entry per site per product block, not per site: a shop that is
    cheapest on one bottle is not automatically cheapest on the next, and
    ranking it once for the whole scan would let its bargain on one perfume
    carry it to the top of a block where it is the dearest.

    Only rows whose price could be read count. A size with no price says
    nothing about what a shop charges, and letting it in would make the
    block order depend on which rows happen to be on screen.
    """
    band: dict[tuple[int, str, str], Decimal] = {}
    overall: dict[tuple[int, str, str], Decimal] = {}
    for row in rows:
        per_ml = row.price_per_ml_kurus
        if per_ml is None:
            continue
        key = (row.query_index, row.product, row.site_id)
        overall[key] = min(overall.get(key, per_ml), per_ml)
        if row.size_ml_x10 <= _BAND_MAX_ML_X10:
            band[key] = min(band.get(key, per_ml), per_ml)
    return {
        key: (0, band[key]) if key in band else (_OUT_OF_BAND, cheapest)
        for key, cheapest in overall.items()
    }


def grouped_value(
    row: ResultRow, ranks: dict[tuple[int, str, str], tuple[int, Decimal]]
) -> tuple[int, str, int, Decimal, str, Decimal]:
    """The default order: typed order, product, site, size.

    The typed order comes first and is never shown. Sorting several perfumes
    into one ₺/ml list interleaves them, and a table where consecutive rows
    are different bottles cannot be read as a comparison of anything.

    Sizes go up inside a site's block, every block the same way, so the eye
    can move down a column instead of re-reading each one.
    """
    band, cheapest = ranks.get((row.query_index, row.product, row.site_id), _UNPRICED)
    return (
        row.query_index,
        row.product,
        band,
        cheapest,
        row.site_label,
        Decimal(row.size_ml_x10),
    )


def sorted_value(
    row: ResultRow, sort_key: str | None
) -> tuple[int, str, bool, Decimal]:
    """The order once a column has been picked: the site layer drops out.

    Asking for the cheapest ₺/ml and getting an answer still cut into site
    blocks is not an answer. The product blocks stay, for the same reason
    they always do.
    """
    return (row.query_index, row.product, *within_query(row, sort_key))


def within_query(row: ResultRow, sort_key: str | None) -> tuple[bool, Decimal]:
    if sort_key == "ml":
        return (False, Decimal(row.size_ml_x10))
    if sort_key == "price":
        return (row.price_kurus is None, Decimal(row.price_kurus or 0))
    return (
        row.price_per_ml_kurus is None,
        row.price_per_ml_kurus if row.price_per_ml_kurus is not None else Decimal(0),
    )
