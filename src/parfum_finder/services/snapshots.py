"""Map search results into persistence rows."""

from parfum_finder.matcher import PerfumeQuery, match_title, result_identity
from parfum_finder.search_models import SiteResult
from parfum_finder.store import SnapshotRow


def snapshot_rows(result: SiteResult, query: PerfumeQuery) -> list[SnapshotRow]:
    """Turn one site's hits into the rows persistence is ready to store.

    Shared by every interface so they cannot diverge on which titles get stored
    as the searched perfume.
    """
    rows: list[SnapshotRow] = []
    for hit in result.hits:
        if hit.candidate.raw_title is None:
            continue
        match = match_title(hit.candidate.raw_title, query)
        if match is None:
            # A rejection, not a weak score: the title names another brand or
            # concentration. Storing it would corrupt this perfume's history.
            continue
        # A clone is a different bottle that happens to have been found by this
        # search, so it is filed under what its own title says it is. Using the
        # query here would put an imitation's price into the searched perfume's
        # history, and the concentration would be wrong too: match.concentration
        # is the one read off the parenthesis, which belongs to the original.
        #
        # A non-clone match that missed `confident` gets the same treatment.
        # "Layton" matching "Layton Exclusif" at a low score is the matcher
        # working as intended, not a mistake, but the two are different bottles
        # with different prices. Filing the low-score one under the searched
        # perfume's identity would give both one shared price history and one
        # shared basket line, so adding "Layton" to the basket would light up
        # "Layton Exclusif" rows too and hand its price to "Layton".
        identity = (
            match.clone_identity
            if match.clone_of
            else match.own_identity
            if not match.confident
            else result_identity(hit.candidate.raw_title, query, match)
        )
        rows.extend(
            SnapshotRow(
                site_id=result.site_id,
                brand=identity.brand if identity else query.brand,
                name=identity.name if identity else query.name,
                # What the title named, not what was asked for. An EDT and an
                # EDP are two products with two prices, and a query that named
                # neither would otherwise merge them into one perfume row.
                concentration=(
                    identity.concentration if identity else match.concentration
                ),
                match_score=match.score,
                variant=variant,
                clone_of=match.clone_of,
                own_identity=not match.clone_of or identity is not None,
            )
            for variant in hit.variants
            if variant.raw_title is not None
        )
    return rows
