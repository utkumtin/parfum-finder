"""Tests for parfum_finder.basket: single-site scenario scoring.

Money is INTEGER kurus everywhere. The point of most of these tests is that a
boundary comparison (free shipping) or a multiplication (qty into subtotal)
stays exact -- a float anywhere in this path would make a total that looks
right print wrong by one kurus, and nobody would notice until a receipt did.
"""

from parfum_finder.basket import (
    BasketItem,
    ShippingConfig,
    single_site_scenarios,
    site_scenario,
)

_A = BasketItem(item_id=1, label="Dior Sauvage EDP 5.0 ml", qty=1)
_B = BasketItem(item_id=2, label="Bleu de Chanel EDP 3.0 ml", qty=1)


def _site(
    site_id: str = "site-a",
    threshold: int | None = 50000,
    shipping_cost: int = 3000,
) -> ShippingConfig:
    return ShippingConfig(
        site_id=site_id,
        name=site_id,
        free_shipping_threshold_kurus=threshold,
        shipping_cost_kurus=shipping_cost,
        notes=None,
    )


def test_subtotal_one_kurus_under_threshold_still_charges_shipping() -> None:
    # 49999 is one kurus short of the 50000 threshold, which only means something
    # if the comparison is an exact integer >=, not a float that could round up.
    item = BasketItem(item_id=1, label="x", qty=1)
    prices = {(1, "site-a"): 49999}

    scenario = site_scenario([item], prices, _site(threshold=50000, shipping_cost=3000))

    assert scenario.subtotal_kurus == 49999
    assert scenario.shipping_kurus == 3000
    assert scenario.free_shipping_met is False
    assert scenario.free_shipping_gap_kurus == 1
    assert scenario.total_kurus == 52999


def test_subtotal_exactly_at_threshold_gets_free_shipping() -> None:
    # The contract says the comparison is inclusive: hitting the threshold on
    # the nose has to waive shipping, not just clearing it.
    item = BasketItem(item_id=1, label="x", qty=1)
    prices = {(1, "site-a"): 50000}

    scenario = site_scenario([item], prices, _site(threshold=50000, shipping_cost=3000))

    assert scenario.shipping_kurus == 0
    assert scenario.free_shipping_met is True
    assert scenario.free_shipping_gap_kurus is None
    assert scenario.total_kurus == 50000


def test_quantity_multiplies_into_subtotal_and_can_cross_the_threshold() -> None:
    # The price stored per line is a unit price. A qty of 2 at 25000 crosses a
    # 50000 threshold that a single unit alone would not reach.
    item = BasketItem(item_id=1, label="x", qty=2)
    prices = {(1, "site-a"): 25000}

    scenario = site_scenario([item], prices, _site(threshold=50000, shipping_cost=3000))

    assert scenario.subtotal_kurus == 50000
    assert scenario.free_shipping_met is True


def test_site_with_no_free_shipping_charges_it_even_on_a_huge_subtotal() -> None:
    # threshold=None means "this site never waives shipping", which is a
    # different fact than "the threshold is unreachably high". The gap must
    # stay None so a UI never prints a fake "X kaldı" line for it.
    item = BasketItem(item_id=1, label="x", qty=1)
    prices = {(1, "site-a"): 10_000_000}

    scenario = site_scenario([item], prices, _site(threshold=None, shipping_cost=3000))

    assert scenario.shipping_kurus == 3000
    assert scenario.free_shipping_gap_kurus is None
    assert scenario.free_shipping_met is False


def test_missing_price_and_absent_key_are_both_treated_as_not_covered() -> None:
    items = [_A, _B]
    prices = {(1, "site-a"): 20000, (2, "site-a"): None}  # B: explicit None

    scenario = site_scenario(items, prices, _site())

    assert scenario.covered == 1
    assert scenario.missing == (_B.label,)
    assert scenario.subtotal_kurus == 20000


def test_partial_site_never_outranks_a_full_site_even_when_cheaper() -> None:
    # A site missing a line is a different offer than one that covers the whole
    # basket, no matter which total is lower -- they belong in separate tuples,
    # not one list ordered purely by price.
    items = [_A, _B]
    prices = {
        (1, "site-cheap"): 10000,
        # site-cheap has no price for B at all: partial, low total.
        (1, "site-full"): 40000,
        (2, "site-full"): 40000,  # site-full covers both: full, higher total.
    }
    sites = [
        _site("site-cheap", threshold=None, shipping_cost=0),
        _site("site-full", threshold=None, shipping_cost=0),
    ]

    report = single_site_scenarios(items, prices, sites)

    assert [s.site_id for s in report.full] == ["site-full"]
    assert [s.site_id for s in report.partial] == ["site-cheap"]
    assert report.partial[0].total_kurus < report.full[0].total_kurus
    assert report.partial[0].missing == (_B.label,)


def test_scenarios_within_a_tuple_are_sorted_cheapest_total_first() -> None:
    items = [_A]
    prices = {(1, "site-b"): 20000, (1, "site-a"): 10000}
    sites = [
        _site("site-b", threshold=None, shipping_cost=0),
        _site("site-a", threshold=None, shipping_cost=0),
    ]

    report = single_site_scenarios(items, prices, sites)

    assert [s.site_id for s in report.full] == ["site-a", "site-b"]


def test_tied_totals_break_ties_by_site_id_for_deterministic_order() -> None:
    items = [_A]
    prices = {(1, "site-z"): 10000, (1, "site-a"): 10000}
    sites = [
        _site("site-z", threshold=None, shipping_cost=0),
        _site("site-a", threshold=None, shipping_cost=0),
    ]

    report = single_site_scenarios(items, prices, sites)

    assert [s.site_id for s in report.full] == ["site-a", "site-z"]


def test_line_no_site_prices_is_reported_as_unavailable() -> None:
    items = [_A, _B]
    prices = {(1, "site-a"): 10000}  # nobody prices B at all
    sites = [_site("site-a", threshold=None, shipping_cost=0)]

    report = single_site_scenarios(items, prices, sites)

    assert report.unavailable == (_B.label,)


def test_site_covering_nothing_is_absent_from_both_full_and_partial() -> None:
    # A site with no priced lines is not a "0-line partial scenario" -- printing
    # one would show a shipping charge on top of a subtotal of zero, an offer
    # nobody actually made.
    items = [_A]
    prices: dict[tuple[int, str], int | None] = {}
    sites = [_site("site-a", threshold=None, shipping_cost=3000)]

    report = single_site_scenarios(items, prices, sites)

    assert report.full == ()
    assert report.partial == ()
    assert report.unavailable == (_A.label,)


def test_item_ids_restricts_the_scenario_so_excluded_items_are_not_missing() -> None:
    # item_ids is the hook M9's subset search will use: an item outside the
    # given set is not part of this scenario at all, not a line this site
    # failed to cover.
    items = [_A, _B]
    prices = {(1, "site-a"): 10000}  # B has no price anywhere

    scenario = site_scenario(items, prices, _site(), item_ids={1})

    assert scenario.total_items == 1
    assert scenario.covered == 1
    assert scenario.missing == ()
    assert scenario.is_full is True


def test_empty_basket_yields_an_empty_report() -> None:
    report = single_site_scenarios([], {}, [_site()])

    assert report.full == ()
    assert report.partial == ()
    assert report.unavailable == ()
