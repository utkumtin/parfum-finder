"""Tests for parfum_finder.basket: single-site scenario scoring.

Money is INTEGER kurus everywhere. The point of most of these tests is that a
boundary comparison (free shipping) or a multiplication (qty into subtotal)
stays exact -- a float anywhere in this path would make a total that looks
right print wrong by one kurus, and nobody would notice until a receipt did.
"""

from parfum_finder.basket import (
    BasketItem,
    ShippingConfig,
    optimize,
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


def test_optimize_boundary_kurus_below_threshold_still_pays_shipping() -> None:
    # optimize scores legs through site_scenario, so the exact-integer boundary
    # that matters for a single site has to survive the split search too.
    item = BasketItem(item_id=1, label="x", qty=1)
    sites = [_site("site-a", threshold=50000, shipping_cost=3000)]

    under = optimize([item], {(1, "site-a"): 49999}, sites)
    at = optimize([item], {(1, "site-a"): 50000}, sites)

    assert under is not None and at is not None
    assert under.legs[0].scenario.free_shipping_met is False
    assert under.total_kurus == 52999
    assert at.legs[0].scenario.free_shipping_met is True
    assert at.total_kurus == 50000


def test_optimize_ignores_a_site_with_no_prices_at_all() -> None:
    # A site absent from the price matrix must never end up as a leg, or the
    # plan would charge shipping against a subtotal nobody can actually buy.
    prices = {(1, "site-a"): 10000}
    sites = [_site("site-a", threshold=None, shipping_cost=1000), _site("site-ghost")]

    plan = optimize([_A], prices, sites)

    assert plan is not None
    assert [leg.scenario.site_id for leg in plan.legs] == ["site-a"]
    assert plan.omitted_sites == ()


def test_optimize_single_item_basket_is_one_leg() -> None:
    prices = {(1, "site-a"): 5000}
    sites = [_site("site-a", threshold=None, shipping_cost=1000)]

    plan = optimize([_A], prices, sites)

    assert plan is not None
    assert len(plan.legs) == 1
    assert plan.legs[0].item_ids == (1,)
    assert plan.total_kurus == 6000


def test_optimize_buys_one_item_from_the_pricier_site_to_unlock_free_shipping() -> None:
    # _A only prices on site-y and _C only prices on site-x, so both sites are
    # forced into every valid plan -- no singleton subset can win this one, the
    # split has to happen. _B is the contested item: 50 on site-x, 80 on site-y.
    # Assigning every item to its cheapest site (the naive starting point) puts
    # _B on site-x, leaving site-y with only _A's 100 against its 180 threshold:
    # 100+100(ship) on site-y, plus 50+50+20(ship) on site-x = 320. Moving _B to
    # site-y costs 30 kurus more for the item, but it brings site-y's subtotal to
    # 180 and clears the threshold, saving its 100 shipping fee outright -- a net
    # drop to 250. The cheapest-unit-price assignment is not the answer; the
    # threshold crossing is.
    item_c = BasketItem(item_id=3, label="c", qty=1)
    prices = {
        (1, "site-y"): 100,
        (2, "site-x"): 50,
        (2, "site-y"): 80,
        (3, "site-x"): 50,
    }
    sites = [
        _site("site-x", threshold=None, shipping_cost=20),
        _site("site-y", threshold=180, shipping_cost=100),
    ]

    plan = optimize([_A, _B, item_c], prices, sites)

    assert plan is not None
    assert plan.total_kurus == 250
    by_site = {leg.scenario.site_id: leg.item_ids for leg in plan.legs}
    assert by_site == {"site-y": (1, 2), "site-x": (3,)}
    y_leg = next(leg for leg in plan.legs if leg.scenario.site_id == "site-y")
    assert y_leg.scenario.free_shipping_met is True


def test_optimize_splits_the_basket_when_no_single_site_covers_it_all() -> None:
    # Neither site alone prices both lines, so a single-site scenario would
    # always be partial. A plan must still exist -- this is not the None case.
    prices = {(1, "site-only-a"): 1000, (2, "site-only-b"): 1200}
    sites = [
        _site("site-only-a", threshold=None, shipping_cost=0),
        _site("site-only-b", threshold=None, shipping_cost=0),
    ]

    plan = optimize([_A, _B], prices, sites)

    assert plan is not None
    covered_ids = {item_id for leg in plan.legs for item_id in leg.item_ids}
    assert covered_ids == {1, 2}
    assert plan.total_kurus == 2200


def test_optimize_returns_none_when_a_line_is_priced_nowhere() -> None:
    prices = {(1, "site-a"): 1000}  # _B has no price on any site
    sites = [_site("site-a", threshold=None, shipping_cost=0)]

    plan = optimize([_A, _B], prices, sites)

    assert plan is None


def test_optimize_is_deterministic_across_repeated_calls() -> None:
    # Two runs over the same inputs must return the identical plan, not just an
    # equally-cheap one, or a screen re-rendering the same basket could flicker
    # between two different splits. Reuses the threshold-crossing fixture above,
    # since that is the plan a wobble in the local-improvement pass would show up in.
    item_c = BasketItem(item_id=3, label="c", qty=1)
    prices = {
        (1, "site-y"): 100,
        (2, "site-x"): 50,
        (2, "site-y"): 80,
        (3, "site-x"): 50,
    }
    sites = [
        _site("site-x", threshold=None, shipping_cost=20),
        _site("site-y", threshold=180, shipping_cost=100),
    ]

    first = optimize([_A, _B, item_c], prices, sites)
    second = optimize([_A, _B, item_c], prices, sites)

    assert first == second


def test_optimize_breaks_a_tied_total_by_site_id_deterministically() -> None:
    # site-a and site-b price the only item identically, so the singleton plan
    # on either site costs the same. The tie-break has to land on the same
    # site every time, not whichever subset happened to be enumerated first.
    prices = {(1, "site-a"): 1000, (1, "site-b"): 1000}
    sites = [
        _site("site-a", threshold=None, shipping_cost=0),
        _site("site-b", threshold=None, shipping_cost=0),
    ]

    first = optimize([_A], prices, sites)
    second = optimize([_A], prices, sites)

    assert first is not None and second is not None
    assert first == second
    assert [leg.scenario.site_id for leg in first.legs] == ["site-a"]


def test_optimize_omits_low_ranked_sites_past_the_enumeration_cap() -> None:
    # 12 sites price at least one line: 3 price both (_A and _B) and 9 price
    # only _A. Ranking by coverage first means all 3 full sites are always
    # kept regardless of their total, and only the cheapest of the partial
    # ones fill the remaining cap slots -- the two priciest partial sites are
    # the ones left out.
    full_sites = [_site(f"f{n}", threshold=None, shipping_cost=0) for n in (1, 2, 3)]
    partial_sites = [
        _site(f"p{n}", threshold=None, shipping_cost=0) for n in range(1, 10)
    ]
    prices: dict[tuple[int, str], int | None] = {}
    for n, cost in zip((1, 2, 3), (1000, 1500, 2000), strict=True):
        prices[(1, f"f{n}")] = cost
        prices[(2, f"f{n}")] = cost
    for n in range(1, 10):
        prices[(1, f"p{n}")] = n * 100

    plan = optimize([_A, _B], prices, full_sites + partial_sites)

    assert plan is not None
    assert plan.omitted_sites == ("p8", "p9")
    assert plan.total_kurus == 1100
