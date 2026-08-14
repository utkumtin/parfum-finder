"""Row shapes shared between the TUI screens and, later, other frontends.

These are plain data, not Textual widgets: what a scan or a basket read
produces and what ranking.py and basket.py sort and group.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from parfum_finder.store import BasketLine


@dataclass(frozen=True)
class ResultRow:
    """One priced size, exactly as the table shows it and as a keypress needs it.

    `product` is what the site's own title reduces to, and it is both the block
    heading and the second sort layer. It is not the search text: a search for
    "Parfums de Marly Layton" also finds "Layton Exclusif", and those two are
    different bottles that must not share a block.

    `age_days` is how old the reading behind the row is. It defaults to 0, which
    is what a row this scan just fetched is, so only the rows repainted from
    storage have to fill it in.
    """

    site_id: str
    site_label: str
    raw_title: str
    size_ml_x10: int
    price_kurus: int | None
    in_stock: bool | None
    match_score: int
    confident: bool
    brand: str
    name: str
    concentration: str
    product_url: str | None
    query_index: int = 0
    product: str = ""
    clone_of: str = ""
    own_identity: bool = True
    age_days: int = 0

    @property
    def price_per_ml_kurus(self) -> Decimal | None:
        # Decimal, not floor division: latest_prices computes this as a real
        # division too, and truncating to an int here would round two rows
        # that actually differ into a tie and quietly change the sort order.
        if self.price_kurus is None:
            return None
        return Decimal(self.price_kurus * 10) / Decimal(self.size_ml_x10)


@dataclass(frozen=True)
class BasketRow:
    """One basket line as the table shows it, with the keys a keypress needs."""

    line: BasketLine
    label: str
    # Unit price per site, only for the sites that can actually supply this line.
    prices: dict[str, int]
    age_days: int | None
