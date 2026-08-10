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

# The pair sweep is quadratic in basket lines and dominates the search, so it
# gets its own ceiling. Measured on 10 sites with a dense price matrix and
# thresholds straddling the leg subtotals, which is the worst case because it
# keeps every subset alive: 15 lines is ~130 ms, 20 lines is ~230 ms, 25 lines
# is ~410 ms, 30 lines is ~720 ms. The budget is 500 ms, so 25 is where the
# pair sweep stops. Past it the search still runs, with single moves only.
MAX_PAIR_MOVE_ITEMS = 25


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


@dataclass
class _ClimbState:
    """The hill-climb's working assignment plus the running per-site figures.

    `subtotals` and `lines` are kept in step with `assignment` so scoring a
    trial move only has to reprice the sites that move touches. `reachable`
    lists the sites one line could move to at all, with what it would cost
    there, so the move loops never look up a price that isn't in this subset.
    All of it is cached derived data, so nothing outside the search should ever
    see any of it.
    """

    assignment: dict[int, str]
    subtotals: dict[str, int]
    lines: dict[str, int]
    reachable: dict[int, tuple[tuple[str, int], ...]]


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
    ordered_items = sorted(items, key=lambda i: i.item_id)
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

    # What one basket line costs on one site, quantity included, keyed by line
    # and then by site. The search scores hundreds of thousands of trial moves,
    # so this is derived once and `prices` is never touched inside the climb.
    cost_of: dict[int, dict[str, int]] = {}
    for item in ordered_items:
        per_site: dict[str, int] = {}
        for config in candidates:
            price = prices.get((item.item_id, config.site_id))
            if price is not None:
                per_site[config.site_id] = price * item.qty
        cost_of[item.item_id] = per_site

    def leg_cost(site_id: str, subtotal: int, lines: int) -> int:
        """One leg's total from its subtotal. No lines means no leg, so no shipping."""
        if lines == 0:
            return 0
        config = site_by_id[site_id]
        threshold = config.free_shipping_threshold_kurus
        if threshold is not None and subtotal >= threshold:
            return subtotal
        return subtotal + config.shipping_cost_kurus

    def apply_moves(state: _ClimbState, moves: Sequence[tuple[int, str]]) -> None:
        for item_id, target in moves:
            source = state.assignment[item_id]
            state.subtotals[source] -= cost_of[item_id][source]
            state.lines[source] -= 1
            state.assignment[item_id] = target
            state.subtotals[target] = (
                state.subtotals.get(target, 0) + cost_of[item_id][target]
            )
            state.lines[target] = state.lines.get(target, 0) + 1

    def best_single_move(state: _ClimbState, item_id: int) -> str | None:
        """The site that cuts the total most by taking over one line, or None.

        A move only changes what the two sites it touches charge, so the rest of
        the plan never gets repriced. The source side does not depend on the
        target either, so it is priced once and reused across the candidates.
        """
        source = state.assignment[item_id]
        source_subtotal = state.subtotals[source]
        source_lines = state.lines[source]
        leaving = leg_cost(
            source, source_subtotal - cost_of[item_id][source], source_lines - 1
        ) - leg_cost(source, source_subtotal, source_lines)

        best_delta = 0
        best_site: str | None = None
        for site_id, cost in state.reachable[item_id]:
            if site_id == source:
                continue
            subtotal = state.subtotals.get(site_id, 0)
            lines = state.lines.get(site_id, 0)
            delta = (
                leaving
                + leg_cost(site_id, subtotal + cost, lines + 1)
                - leg_cost(site_id, subtotal, lines)
            )
            if delta < best_delta:
                best_delta = delta
                best_site = site_id
        return best_site

    def first_pair_move(state: _ClimbState) -> tuple[tuple[int, str], ...] | None:
        """The first strictly cheaper two-line move, or None if there isn't one.

        Single moves get stuck when two lines only pay off together, which is
        exactly what happens when neither one alone clears a site's free
        shipping threshold but both together do. Two move shapes cover that:
        send both lines to the same site, or swap the two lines' sites. The
        first improvement wins rather than the best one, because the caller goes
        straight back to single moves afterwards and would re-find anything
        better from the new position anyway.
        """
        assignment = state.assignment
        subtotals = state.subtotals
        lines = state.lines

        for index, first in enumerate(ordered_items):
            a = first.item_id
            site_a = assignment[a]
            a_out = cost_of[a][site_a]
            for second in ordered_items[index + 1 :]:
                b = second.item_id
                site_b = assignment[b]
                b_out = cost_of[b][site_b]
                b_costs = cost_of[b]

                # Both lines onto one site. What the sources give up is the same
                # whichever site takes them, so it is priced once per pair.
                if site_a == site_b:
                    subtotal = subtotals[site_a]
                    count = lines[site_a]
                    leaving = leg_cost(
                        site_a, subtotal - a_out - b_out, count - 2
                    ) - leg_cost(site_a, subtotal, count)
                else:
                    leaving = (
                        leg_cost(site_a, subtotals[site_a] - a_out, lines[site_a] - 1)
                        - leg_cost(site_a, subtotals[site_a], lines[site_a])
                        + leg_cost(site_b, subtotals[site_b] - b_out, lines[site_b] - 1)
                        - leg_cost(site_b, subtotals[site_b], lines[site_b])
                    )
                for site_id, a_in in state.reachable[a]:
                    if site_id == site_a or site_id == site_b:
                        continue
                    b_in = b_costs.get(site_id)
                    if b_in is None:
                        continue
                    subtotal = subtotals.get(site_id, 0)
                    count = lines.get(site_id, 0)
                    delta = (
                        leaving
                        + leg_cost(site_id, subtotal + a_in + b_in, count + 2)
                        - leg_cost(site_id, subtotal, count)
                    )
                    if delta < 0:
                        return ((a, site_id), (b, site_id))

                # Trade sites. Neither leg gains or loses a line here, only what
                # it is paying for, so the line counts stay put.
                if site_a == site_b:
                    continue
                a_traded = cost_of[a].get(site_b)
                b_traded = b_costs.get(site_a)
                if a_traded is None or b_traded is None:
                    continue
                delta = (
                    leg_cost(
                        site_a, subtotals[site_a] - a_out + b_traded, lines[site_a]
                    )
                    - leg_cost(site_a, subtotals[site_a], lines[site_a])
                    + leg_cost(
                        site_b, subtotals[site_b] - b_out + a_traded, lines[site_b]
                    )
                    - leg_cost(site_b, subtotals[site_b], lines[site_b])
                )
                if delta < 0:
                    return ((a, site_b), (b, site_a))
        return None

    best_total: int | None = None
    best_key: tuple[int, int, tuple[str, ...]] | None = None
    best_assignment: dict[int, str] | None = None

    for mask in range(1, 1 << site_count):
        subset_ids = {
            candidates[i].site_id for i in range(site_count) if mask & (1 << i)
        }
        reachable = {
            item.item_id: tuple(
                (site_id, cost)
                for site_id, cost in cost_of[item.item_id].items()
                if site_id in subset_ids
            )
            for item in ordered_items
        }

        assignment: dict[int, str] = {}
        covers_all = True
        for item in ordered_items:
            options = reachable[item.item_id]
            if not options:
                covers_all = False
                break
            best_site_id, best_cost = options[0]
            for site_id, cost in options[1:]:
                if cost < best_cost:
                    best_cost = cost
                    best_site_id = site_id
            assignment[item.item_id] = best_site_id
        if not covers_all:
            continue

        # Hill-climb: an item bought from a pricier site can still cut the
        # total by pushing that site's subtotal over its free-shipping
        # threshold, so the cheapest-unit-price assignment above is only a
        # starting point. The total is an integer that strictly decreases on
        # every accepted move, so this always terminates on its own and needs
        # no separate round limit.
        state = _ClimbState(
            assignment=assignment, subtotals={}, lines={}, reachable=reachable
        )
        for item_id, site_id in assignment.items():
            state.subtotals[site_id] = (
                state.subtotals.get(site_id, 0) + cost_of[item_id][site_id]
            )
            state.lines[site_id] = state.lines.get(site_id, 0) + 1

        while True:
            moved = False
            for item in ordered_items:
                target = best_single_move(state, item.item_id)
                if target is not None:
                    apply_moves(state, ((item.item_id, target),))
                    moved = True
            if moved:
                continue
            # Single moves are exhausted, so try the two-line moves they can't
            # reach. One improvement is enough to go back to single moves,
            # which are cheaper and may now have somewhere to go.
            if len(ordered_items) > MAX_PAIR_MOVE_ITEMS:
                break
            pair = first_pair_move(state)
            if pair is None:
                break
            apply_moves(state, pair)

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
