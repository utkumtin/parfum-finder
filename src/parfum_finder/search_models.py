"""Dependency-free models shared by search, persistence, and presentation."""

from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class ProductCandidate:
    """One hit on a search results page, before its product page is opened.

    `raw_title` is the listing's own wording, kept verbatim: it is what makes a
    wrong match visible to a person reading the results table, so nothing here
    tidies it up.
    """

    raw_title: str | None
    url: str
    # The URL used for comparison, caching and de-duplication. `url` remains
    # the response URL because it is the page whose markup and redirects a
    # browser can actually open.
    identity: str | None = None
    metadata_source: str | None = None
    # A single page may be opened only to prove the extractor still works when
    # every listing failed the prefilter. Its rows must never become results.
    diagnostic: bool = False


@dataclass(frozen=True)
class Variant:
    """One decant size of one product, in the units the database stores.

    Tenths of a millilitre and kuruş, both as integers, because both are compared
    and joined on: a basket matches sizes across sites by this number, and a free
    shipping threshold is a comparison that binary floats lose at the boundary.

    `price_kurus` may be None. A size that is sold out often shows no price at
    all, and dropping it would erase the difference between "this shop never sells
    that size" and "that size is out of stock right now", which is exactly what
    the stock column is for.
    """

    size_ml_x10: int
    raw_title: str | None
    product_url: str | None
    price_kurus: int | None
    in_stock: bool | None


@dataclass(frozen=True)
class SearchHit:
    """A candidate together with the decant sizes its product page offers."""

    candidate: ProductCandidate
    variants: tuple[Variant, ...]


SiteStatus = Literal["ok", "empty", "suspect", "error"]


@dataclass(frozen=True)
class SiteResult:
    """What one site had to say about one query, and how much to trust it.

    Four states, and the whole point of the type is the difference between the
    middle two:

    `ok` means hits came back. `empty` means the site answered fine and
    genuinely has nothing, either no search results at all or nothing but full
    bottles and testers. `suspect` means the site answered and the profile
    could not read it, so what it has is unknown. `error` means the request or
    profile failed before an answer existed.

    `empty` and `suspect` both carry no rows, and collapsing them is the bug
    this type exists to make impossible: one means "not sold here" and the other
    means "we stopped being able to see it". Downstream they part ways too, a
    suspect site is left out of basket totals as unknown rather than counted as
    expensive.

    `detail` is the line a person reads. It is filled in for every status
    including `ok`, because a result that says what it saw is how someone
    notices a site quietly returning one row where it used to return ten.
    """

    site_id: str
    status: SiteStatus
    hits: tuple[SearchHit, ...]
    detail: str | None
