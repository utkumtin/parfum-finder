"""Pure sorting and grouping rules: ranking.py takes rows in, sort keys out.

No Textual, no rendering -- these exercise the same rules the results table
sorts by, at the level where the band logic and the tie-break order can be
read straight off the assertion.
"""

from __future__ import annotations

from decimal import Decimal

from parfum_finder.ranking import grouped_value, site_ranks, sorted_value, within_query
from parfum_finder.viewmodels import ResultRow


def _row(
    site_id: str,
    site_label: str,
    size_ml_x10: int,
    price_kurus: int | None,
    *,
    query_index: int = 0,
    product: str = "Dior Sauvage EDP",
) -> ResultRow:
    return ResultRow(
        site_id=site_id,
        site_label=site_label,
        raw_title=product,
        size_ml_x10=size_ml_x10,
        price_kurus=price_kurus,
        in_stock=True,
        match_score=100,
        confident=True,
        brand="dior",
        name="sauvage",
        concentration="edp",
        product_url=None,
        query_index=query_index,
        product=product,
    )


def test_site_blocks_are_ordered_by_what_the_small_bottles_cost() -> None:
    """A shop that only sells big bottles cannot win on ₺/ml alone.

    ₺/ml always falls as the bottle grows, so ranking sites on their best ₺/ml
    would hand the top of every block to whoever sells the largest decant. The
    band is what a decant buyer is actually choosing between, and a site with
    nothing in it is not cheaper, it is answering a different question.
    """
    rows = [
        _row("site-a", "Site A", 30, 60000),  # 3 ml at 200 ₺/ml
        _row("site-b", "Site B", 30, 30000),  # 3 ml at 100 ₺/ml, cheapest small bottle
        _row("site-c", "Site C", 100, 50000),  # 10 ml at 50 ₺/ml, cheapest overall
    ]
    ranks = site_ranks(rows)
    ordered = sorted(rows, key=lambda row: grouped_value(row, ranks))
    assert [row.site_label for row in ordered] == ["Site B", "Site A", "Site C"]


def test_a_site_with_no_price_at_all_goes_last() -> None:
    rows = [
        _row("site-a", "Site A", 30, 60000),
        _row("site-b", "Site B", 30, None),
    ]
    ranks = site_ranks(rows)
    ordered = sorted(rows, key=lambda row: grouped_value(row, ranks))
    assert [row.site_label for row in ordered] == ["Site A", "Site B"]


def test_ranking_stays_per_product_block() -> None:
    """Being cheap on one perfume does not carry a site to the top of another."""
    rows = [
        _row("site-a", "Site A", 30, 30000, product="Dior Sauvage EDP"),
        _row("site-b", "Site B", 30, 60000, product="Dior Sauvage EDP"),
        _row("site-a", "Site A", 30, 90000, product="Chanel Bleu EDP"),
        _row("site-b", "Site B", 30, 45000, product="Chanel Bleu EDP"),
    ]
    ranks = site_ranks(rows)
    ordered = sorted(rows, key=lambda row: grouped_value(row, ranks))
    assert [(row.product, row.site_label) for row in ordered] == [
        ("Chanel Bleu EDP", "Site B"),
        ("Chanel Bleu EDP", "Site A"),
        ("Dior Sauvage EDP", "Site A"),
        ("Dior Sauvage EDP", "Site B"),
    ]


def test_typed_order_keeps_two_perfumes_from_interleaving() -> None:
    rows = [
        _row("site-a", "Site A", 30, 90000, query_index=1, product="Chanel Bleu EDP"),
        _row("site-a", "Site A", 30, 30000, query_index=0, product="Dior Sauvage EDP"),
    ]
    ranks = site_ranks(rows)
    ordered = sorted(rows, key=lambda row: grouped_value(row, ranks))
    assert [row.product for row in ordered] == ["Dior Sauvage EDP", "Chanel Bleu EDP"]


def test_sorted_value_by_ml_ignores_site_and_orders_by_size() -> None:
    rows = [
        _row("site-a", "Site A", 100, 90000),
        _row("site-b", "Site B", 30, 30000),
    ]
    ordered = sorted(rows, key=lambda row: sorted_value(row, "ml"))
    assert [row.size_ml_x10 for row in ordered] == [30, 100]


def test_sorted_value_by_price_puts_unpriced_rows_last() -> None:
    rows = [
        _row("site-a", "Site A", 30, None),
        _row("site-b", "Site B", 30, 30000),
    ]
    ordered = sorted(rows, key=lambda row: sorted_value(row, "price"))
    assert [row.site_label for row in ordered] == ["Site B", "Site A"]


def test_within_query_default_sorts_by_price_per_ml() -> None:
    row = _row("site-a", "Site A", 20, 30000)
    assert within_query(row, None) == (False, Decimal(15000))
