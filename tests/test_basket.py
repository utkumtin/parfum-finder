"""Tests for parfum_finder.basket: single-site scenario scoring.

Money is INTEGER kurus everywhere. The point of most of these tests is that a
boundary comparison (free shipping) or a multiplication (qty into subtotal)
stays exact -- a float anywhere in this path would make a total that looks
right print wrong by one kurus, and nobody would notice until a receipt did.
"""

from datetime import UTC, datetime, timedelta

from parfum_finder.basket import (
    MAX_PAIR_MOVE_ITEMS,
    BasketItem,
    BasketReport,
    ShippingConfig,
    SiteScenario,
    SplitLeg,
    SplitPlan,
    basket_inputs,
    build_basket_rows,
    compare_split_to_best_full,
    optimize,
    single_site_scenarios,
    site_scenario,
)
from parfum_finder.store import (
    BasketLine,
    BasketPrice,
    BasketSite,
    now_iso,
    snapshot_age_days,
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


def test_optimize_moves_two_lines_together_to_clear_a_threshold() -> None:
    # The case single moves cannot reach. site-x carries item c for 30000, which
    # leaves it 30000 short of its own free-shipping threshold, and site-y is a
    # kurus cheaper per unit on _A and _B so the cheapest-unit start puts both
    # there. Moving either one alone to site-x pays site-x's 9000 shipping and
    # loses; moving both at once lands site-x exactly on 60000, so its shipping
    # goes away and the basket gets 7000 cheaper. Only site-y prices item d and
    # only site-x prices item c, so this split is the single viable subset and
    # the enumeration cannot rescue the answer on its own.
    item_c = BasketItem(item_id=3, label="c", qty=1)
    item_d = BasketItem(item_id=4, label="d", qty=1)
    prices: dict[tuple[int, str], int | None] = {
        (1, "site-x"): 15000,
        (1, "site-y"): 14000,
        (2, "site-x"): 15000,
        (2, "site-y"): 14000,
        (3, "site-x"): 30000,
        (4, "site-y"): 8000,
    }
    sites = [
        _site("site-x", threshold=60000, shipping_cost=9000),
        _site("site-y", threshold=100000, shipping_cost=5000),
    ]

    plan = optimize([_A, _B, item_c, item_d], prices, sites)

    assert plan is not None
    # 80000 is what the single-move-only climb settles for: _A and _B left on
    # site-y, site-x paying shipping on item c alone.
    assert plan.total_kurus == 73000
    by_site = {leg.scenario.site_id: leg.item_ids for leg in plan.legs}
    assert by_site == {"site-x": (1, 2, 3), "site-y": (4,)}


def test_optimize_trades_two_lines_between_sites_to_keep_both_free() -> None:
    # The other pair shape: neither line moves to a new site, they trade. site-p
    # starts 2000 short of its threshold and site-q starts over its own. Sending
    # _B to site-p alone clears site-p but drops site-q under its threshold, so
    # it loses; sending _A to site-q alone just pays 1000 more for the same
    # shipping. Trading them lands both sites free at once and saves 2000. Item
    # c is only on site-p and item d only on site-q, so neither site can be
    # dropped and the enumeration cannot reach this on its own.
    item_c = BasketItem(item_id=3, label="c", qty=1)
    item_d = BasketItem(item_id=4, label="d", qty=1)
    prices: dict[tuple[int, str], int | None] = {
        (1, "site-p"): 9000,
        (1, "site-q"): 10000,
        (2, "site-p"): 11000,
        (2, "site-q"): 8000,
        (3, "site-p"): 30000,
        (4, "site-q"): 30000,
    }
    sites = [
        _site("site-p", threshold=41000, shipping_cost=6000),
        _site("site-q", threshold=35000, shipping_cost=9000),
    ]

    plan = optimize([_A, _B, item_c, item_d], prices, sites)

    assert plan is not None
    # 83000 is where the single-move-only climb stops: site-p still paying 6000.
    assert plan.total_kurus == 81000
    by_site = {leg.scenario.site_id: leg.item_ids for leg in plan.legs}
    assert by_site == {"site-p": (2, 3), "site-q": (1, 4)}
    assert all(leg.scenario.free_shipping_met for leg in plan.legs)


def test_optimize_still_covers_the_basket_past_the_pair_move_cap() -> None:
    # Past MAX_PAIR_MOVE_ITEMS the pair sweep is switched off to stay inside the
    # time budget. That is a quality cut, never a correctness one: the plan must
    # still assign every single line to exactly one site.
    items = [
        BasketItem(item_id=n, label=f"line-{n}", qty=1)
        for n in range(1, MAX_PAIR_MOVE_ITEMS + 2)
    ]
    prices: dict[tuple[int, str], int | None] = {}
    for item in items:
        prices[(item.item_id, "site-a")] = 1000 + item.item_id * 10
        prices[(item.item_id, "site-b")] = 1200 - item.item_id * 10
    sites = [
        _site("site-a", threshold=20000, shipping_cost=3000),
        _site("site-b", threshold=25000, shipping_cost=4000),
    ]

    plan = optimize(items, prices, sites)

    assert plan is not None
    assigned = sorted(item_id for leg in plan.legs for item_id in leg.item_ids)
    assert assigned == [item.item_id for item in items]
    assert plan.total_kurus == sum(leg.scenario.total_kurus for leg in plan.legs)


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


# -- build_basket_rows / basket_inputs --------------------------------------


def _line(basket_item_id: int, *, size_ml_x10: int = 50, qty: int = 1) -> BasketLine:
    return BasketLine(
        basket_item_id=basket_item_id,
        perfume_id=1,
        brand="dior",
        name="sauvage",
        concentration="EDP",
        size_ml_x10=size_ml_x10,
        qty=qty,
        added_at="2026-08-01T00:00:00Z",
    )


def _days_ago(days: int) -> str:
    stamp = datetime.now(UTC) - timedelta(days=days, hours=1)
    return stamp.strftime("%Y-%m-%dT%H:%M:%SZ")


def _basket_price(
    basket_item_id: int,
    site_id: str,
    price_kurus: int,
    *,
    in_stock: bool = True,
    fetched_at: str = "2026-08-01T00:00:00Z",
) -> BasketPrice:
    return BasketPrice(
        basket_item_id=basket_item_id,
        site_id=site_id,
        price_kurus=price_kurus,
        in_stock=in_stock,
        fetched_at=fetched_at,
    )


def test_build_basket_rows_drops_out_of_stock_and_excluded_prices() -> None:
    line = _line(1)
    prices = [
        _basket_price(1, "site-a", 25000, in_stock=False),
        _basket_price(1, "site-b", 26000),
        _basket_price(1, "site-c", 27000),
    ]

    rows = build_basket_rows([line], prices, excluded={("site-c", 1)})

    assert rows[0].prices == {"site-b": 26000}


def test_a_rows_age_is_its_stalest_cell() -> None:
    """A row is only as fresh as the oldest price it is comparing.

    Reporting the newest would let one just-scanned column hide a column that
    has not been checked in weeks, which is precisely the state the refresh
    warning in the basket screen is supposed to catch.
    """
    line = _line(1)
    fresh = _basket_price(1, "site-a", 25000, fetched_at=now_iso())
    stale = _basket_price(1, "site-b", 26000, fetched_at=_days_ago(20))

    rows = build_basket_rows([line], [fresh, stale])

    assert rows[0].age_days == snapshot_age_days(stale.fetched_at)


def test_basket_inputs_builds_the_price_matrix_from_row_data() -> None:
    line = _line(1, size_ml_x10=50, qty=2)
    rows = build_basket_rows([line], [_basket_price(1, "site-a", 25000)])
    sites = [
        BasketSite(
            site_id="site-a",
            name="Site A",
            free_shipping_threshold_kurus=None,
            shipping_cost_kurus=3000,
            notes=None,
        )
    ]

    items, prices, shipping = basket_inputs(rows, sites)

    assert items == [BasketItem(item_id=1, label=rows[0].label, qty=2)]
    assert prices == {(1, "site-a"): 25000}
    assert shipping == [
        ShippingConfig(
            site_id="site-a",
            name="Site A",
            free_shipping_threshold_kurus=None,
            shipping_cost_kurus=3000,
            notes=None,
        )
    ]


# -- compare_split_to_best_full ----------------------------------------------


def _full_scenario(site_id: str, total_kurus: int) -> SiteScenario:
    return SiteScenario(
        site_id=site_id,
        name=site_id,
        subtotal_kurus=total_kurus,
        shipping_kurus=0,
        total_kurus=total_kurus,
        covered=1,
        total_items=1,
        missing=(),
        free_shipping_gap_kurus=None,
        free_shipping_met=True,
        notes=None,
    )


def _plan(total_kurus: int) -> SplitPlan:
    scenario = _full_scenario("site-a", total_kurus)
    leg = SplitLeg(scenario=scenario, item_ids=(1,))
    return SplitPlan(legs=(leg,), total_kurus=total_kurus, omitted_sites=())


def test_compare_split_to_best_full_reports_the_cheaper_side() -> None:
    best = _full_scenario("site-b", 30000)
    report = BasketReport(full=(best,), partial=(), unavailable=())

    verdict = compare_split_to_best_full(_plan(25000), report)

    assert verdict.best_full == best
    assert verdict.diff_kurus == -5000


def test_compare_split_to_best_full_with_no_full_coverage_site() -> None:
    report = BasketReport(full=(), partial=(), unavailable=())

    verdict = compare_split_to_best_full(_plan(25000), report)

    assert verdict.best_full is None
    assert verdict.diff_kurus is None
