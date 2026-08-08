"""Basket scenario evaluation. A pure function, no network access, no sqlite.

Input: the shopping list, a price matrix per (item, site) where a missing price
means out of stock or unavailable, and each site's shipping config (free-shipping
threshold and cost). Output: a per-site scenario (subtotal, shipping, grand total,
how many lines are covered).

Why "cheapest site per item" isn't good enough: shipping cost isn't linear. It
drops to zero once a site's subtotal crosses its free-shipping threshold. Paying a
bit more for one item on a given site can lower the grand total overall by
unlocking free shipping there. This module only scores one site against the whole
basket (or a subset of it, via `item_ids`) -- it does not search for the best split
across sites. That search is a later milestone and reuses `site_scenario` as its
per-site primitive.

Money is INTEGER kurus throughout, never float, never Decimal. A price matrix
built from anything else would let two prices that print the same disagree in a
comparison, and a basket total is exactly the kind of number nobody should have
to double check.
"""

from collections.abc import Collection, Mapping, Sequence
from dataclasses import dataclass

Prices = Mapping[tuple[int, str], int | None]


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
