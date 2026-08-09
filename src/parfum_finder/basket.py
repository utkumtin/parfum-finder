"""Basket scenario evaluation. A pure function, no network access, no sqlite.

Input: the shopping list, a price matrix per (item, site) where a missing price
means out of stock or unavailable, and each site's shipping config (free-shipping
threshold and cost). Output: a per-site scenario (subtotal, shipping, grand total,
how many lines are covered).

Why "cheapest site per item" isn't good enough: shipping cost isn't linear. It
drops to zero once a site's subtotal crosses its free-shipping threshold. Paying a
bit more for one item on a given site can lower the grand total overall by
unlocking free shipping there. `optimize` searches for the best split of the
basket across several sites, and it reuses `site_scenario` as its per-site
primitive so a leg of a split and a plain single-site scenario are priced by the
same code.

Money is INTEGER kurus throughout, never float, never Decimal. A price matrix
built from anything else would let two prices that print the same disagree in a
comparison, and a basket total is exactly the kind of number nobody should have
to double check.
"""

from collections.abc import Collection, Mapping, Sequence
from dataclasses import dataclass

Prices = Mapping[tuple[int, str], int | None]

# The subset enumeration is 2**M, so the site list has to be bounded somewhere.
# Ten sites is 1024 subsets, which is instant, and it is also more shops than
# anyone is realistically going to order the same basket from.
MAX_ENUMERATED_SITES = 10


@dataclass(frozen=True)
class BasketItem:
    """One line of the shopping list: a basket row, not a unit count.

    `item_id` is basket_items.basket_item_id, so a scenario's `missing` and a
    caller's basket screen can point at the same row without re-deriving it.
    """

    item_id: int
    label: str
    qty: int


@dataclass(frozen=True)
class ShippingConfig:
    """One site's shipping terms, read once and reused for every scenario.

    `free_shipping_threshold_kurus` being None is not "a threshold of zero" --
    it means the site never waives shipping at all, and a scenario built from it
    must always charge `shipping_cost_kurus` and never print a "X kaldı" gap that
    would promise a discount that doesn't exist.
    """

    site_id: str
    name: str
    free_shipping_threshold_kurus: int | None
    shipping_cost_kurus: int
    notes: str | None


@dataclass(frozen=True)
class SiteScenario:
    """What it would cost to buy some or all of the basket from one site.

    `covered` and `total_items` count basket lines, not units, because a
    scenario answers "does this site carry what I asked for", and a qty of 3
    on a line this site can't supply is still one missing line, not three.
    """

    site_id: str
    name: str
    subtotal_kurus: int
    shipping_kurus: int
    total_kurus: int
    covered: int
    total_items: int
    missing: tuple[str, ...]
    free_shipping_gap_kurus: int | None
    free_shipping_met: bool
    notes: str | None

    @property
    def is_full(self) -> bool:
        return self.covered == self.total_items


@dataclass(frozen=True)
class BasketReport:
    """Every site's single-site scenario, split by whether it covers everything.

    A site that covers nothing is left out of both tuples entirely: it isn't a
    third kind of scenario, it's not a scenario at all, and printing one would
    put a shipping charge next to a subtotal of zero.
    """

    full: tuple[SiteScenario, ...]
    partial: tuple[SiteScenario, ...]
    unavailable: tuple[str, ...]


@dataclass(frozen=True)
class SplitLeg:
    """One site's share of a split basket: what to buy there and what it costs.

    `scenario` is a `site_scenario` scored over `item_ids` only, so its
    `total_items` counts the lines assigned to this leg rather than the whole
    basket, and its shipping already reflects this leg's subtotal against the
    site's own threshold.
    """

    scenario: SiteScenario
    item_ids: tuple[int, ...]


@dataclass(frozen=True)
class SplitPlan:
    """The cheapest basket split the search found. A heuristic, not a proof.

    Every line of the basket is assigned to exactly one leg, so a plan is
    always full coverage. There is no partial plan: a split that skips a line
    is not a cheaper way to buy the basket, it is a different basket.

    `omitted_sites` names the sites that were left out of the search because
    the list was longer than `MAX_ENUMERATED_SITES`. It is on the plan rather
    than swallowed so the screen can say the search was narrowed instead of
    presenting a truncated answer as the whole picture.
    """

    legs: tuple[SplitLeg, ...]
    total_kurus: int
    omitted_sites: tuple[str, ...]


def site_scenario(
    items: Sequence[BasketItem],
    prices: Prices,
    shipping: ShippingConfig,
    *,
    item_ids: Collection[int] | None = None,
) -> SiteScenario:
    """Score one site against the basket, or against a subset of it.

    `item_ids` is how M9's subset search will reuse this function per candidate
    split: an item outside `item_ids` is treated as not part of the basket being
    scored at all, so it never counts toward `total_items` or shows up in
    `missing`. Passing None scores the whole basket, which is what a plain
    single-site scenario needs.
    """
    considered = (
        items if item_ids is None else [i for i in items if i.item_id in item_ids]
    )

    subtotal = 0
    missing: list[str] = []
    covered = 0
    for item in considered:
        price = prices.get((item.item_id, shipping.site_id))
        if price is None:
            missing.append(item.label)
            continue
        covered += 1
        subtotal += price * item.qty

    threshold = shipping.free_shipping_threshold_kurus
    if threshold is not None and subtotal >= threshold:
        shipping_kurus = 0
        gap: int | None = None
        met = True
    else:
        shipping_kurus = shipping.shipping_cost_kurus
        gap = None if threshold is None else threshold - subtotal
        met = False

    return SiteScenario(
        site_id=shipping.site_id,
        name=shipping.name,
        subtotal_kurus=subtotal,
        shipping_kurus=shipping_kurus,
        total_kurus=subtotal + shipping_kurus,
        covered=covered,
        total_items=len(considered),
        missing=tuple(missing),
        free_shipping_gap_kurus=gap,
        free_shipping_met=met,
        notes=shipping.notes,
    )


def single_site_scenarios(
    items: Sequence[BasketItem],
    prices: Prices,
    shipping: Sequence[ShippingConfig],
) -> BasketReport:
    """Score every enabled site against the whole basket and sort the results.

    Sites that price zero lines are dropped rather than scored: a shipping fee
    on top of a zero subtotal is not a scenario anyone would pick, it's a
    formatting bug waiting to be shown on screen. `full` and `partial` are each
    sorted by total ascending, tie-broken by site_id so two runs over the same
    data always print in the same order.
    """
    full: list[SiteScenario] = []
    partial: list[SiteScenario] = []

    for config in shipping:
        scenario = site_scenario(items, prices, config)
        if scenario.covered == 0:
            continue
        if scenario.is_full:
            full.append(scenario)
        else:
            partial.append(scenario)

    full.sort(key=lambda s: (s.total_kurus, s.site_id))
    partial.sort(key=lambda s: (s.total_kurus, s.site_id))
    unavailable = tuple(
        item.label
        for item in items
        if all(
            prices.get((item.item_id, config.site_id)) is None for config in shipping
        )
    )

    return BasketReport(
        full=tuple(full), partial=tuple(partial), unavailable=unavailable
    )


def optimize(
    items: Sequence[BasketItem],
    prices: Prices,
    shipping: Sequence[ShippingConfig],
) -> SplitPlan | None:
    """Search for the cheapest way to split the basket across several sites.

    Returns None when no combination of sites covers every line, which happens
    exactly when some line has no price anywhere. A basket nobody can fill has
    no split worth showing.
    """
    site_by_id = {s.site_id: s for s in shipping}
    full_scenarios = {s.site_id: site_scenario(items, prices, s) for s in shipping}
    candidates = [s for s in shipping if full_scenarios[s.site_id].covered > 0]

    omitted: tuple[str, ...] = ()
    if len(candidates) > MAX_ENUMERATED_SITES:
        ranked = sorted(
            candidates,
            key=lambda s: (
                -full_scenarios[s.site_id].covered,
                full_scenarios[s.site_id].total_kurus,
                s.site_id,
            ),
        )
        omitted = tuple(sorted(s.site_id for s in ranked[MAX_ENUMERATED_SITES:]))
        candidates = ranked[:MAX_ENUMERATED_SITES]

    candidates = sorted(candidates, key=lambda s: s.site_id)
    site_count = len(candidates)

    def plan_total(assignment: dict[int, str]) -> int:
        by_site: dict[str, list[int]] = {}
        for item_id, site_id in assignment.items():
            by_site.setdefault(site_id, []).append(item_id)
        return sum(
            site_scenario(items, prices, site_by_id[site_id], item_ids=ids).total_kurus
            for site_id, ids in by_site.items()
        )

    best_total: int | None = None
    best_key: tuple[int, int, tuple[str, ...]] | None = None
    best_assignment: dict[int, str] | None = None

    for mask in range(1, 1 << site_count):
        subset_sites = [candidates[i] for i in range(site_count) if mask & (1 << i)]

        assignment: dict[int, str] = {}
        covers_all = True
        for item in items:
            best_price: int | None = None
            best_site_id: str | None = None
            for site in subset_sites:
                price = prices.get((item.item_id, site.site_id))
                if price is None:
                    continue
                if best_price is None or price < best_price:
                    best_price = price
                    best_site_id = site.site_id
            if best_site_id is None:
                covers_all = False
                break
            assignment[item.item_id] = best_site_id
        if not covers_all:
            continue

        # Hill-climb: an item bought from a pricier site can still cut the
        # total by pushing that site's subtotal over its free-shipping
        # threshold, so the cheapest-unit-price assignment above is only a
        # starting point. The total is an integer that strictly decreases on
        # every accepted move, so this always terminates on its own.
        moved = True
        while moved:
            moved = False
            for item in sorted(items, key=lambda i: i.item_id):
                current_total = plan_total(assignment)
                current_site = assignment[item.item_id]
                best_move_site = current_site
                best_move_total = current_total
                for site in subset_sites:
                    if site.site_id == current_site:
                        continue
                    if prices.get((item.item_id, site.site_id)) is None:
                        continue
                    trial = dict(assignment)
                    trial[item.item_id] = site.site_id
                    trial_total = plan_total(trial)
                    if trial_total < best_move_total:
                        best_move_total = trial_total
                        best_move_site = site.site_id
                if best_move_site != current_site:
                    assignment[item.item_id] = best_move_site
                    moved = True

        total = plan_total(assignment)
        sites_used = tuple(sorted(set(assignment.values())))
        key = (total, len(sites_used), sites_used)

        if best_key is None or key < best_key:
            best_key = key
            best_total = total
            best_assignment = assignment

    if best_assignment is None or best_total is None:
        return None

    by_site: dict[str, list[int]] = {}
    for item_id, site_id in best_assignment.items():
        by_site.setdefault(site_id, []).append(item_id)

    legs = [
        SplitLeg(
            scenario=site_scenario(
                items,
                prices,
                site_by_id[site_id],
                item_ids=tuple(sorted(assigned_ids)),
            ),
            item_ids=tuple(sorted(assigned_ids)),
        )
        for site_id, assigned_ids in by_site.items()
    ]
    legs.sort(key=lambda leg: (leg.scenario.total_kurus, leg.scenario.site_id))

    return SplitPlan(legs=tuple(legs), total_kurus=best_total, omitted_sites=omitted)
