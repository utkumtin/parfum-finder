"""Perfume matching: brand and concentration are mandatory; fuzzy matching only
applies to the name.

Raw title similarity alone can't tell 'Sauvage' apart from 'Sauvage Elixir' or
'Eau Sauvage', or 'Bleu de Chanel EDT' from 'EDP'. So brand and concentration
(EDT/EDP/EDC/Parfum/Extrait/Elixir) are checked as mandatory exact tokens first;
fuzzy matching only runs on whatever's left of the name.

A low-confidence match must never be added to the basket silently. The UI has to
ask for confirmation first.

A wrong match that scores high is worse than no match at all: it reads as a cheap
price and puts the wrong bottle in the basket. That is why the two mandatory
checks come before the fuzzy one and can only reject, never contribute a score.

The brand is checked by looking for the searched brand in the title, rather than
by cutting a brand out of the title and comparing the two. Cutting one out needs
a list of every brand that exists, and a brand missing from that list would
quietly stop being a brand. Looking for the one brand that was actually asked for
needs no list and cannot go stale.

Shops write brands out more fully than people type them. "Christian Dior
Sauvage" for a search of "Dior Sauvage", "Jean Paul Gaultier Le Male" for "Le
Male". Every extra word costs score, so perfect matches were coming back in the
forties and the number on screen stopped meaning anything. A title whose last
words are the whole query, in order, is therefore treated as an exact match:
whatever a shop puts in front of the searched words is the rest of the brand.
Contiguous and at the end, both, because that is what keeps the guards intact.

Some shops sell clones next to originals and name the original in parentheses:
"Armaf - Club De Nuit Untold (Maison Francis Kurkdjian - Baccarat Rouge 540)".
That parenthesis is a reference, not part of what the bottle is, and reading it
as part of the name broke matching in both directions at once. Searching for the
original matched the clone, because the original's brand really was somewhere in
the title. Searching for the clone scored the right bottle below the wrong one,
because the referenced perfume's words counted against the name it was scored on.
So the parenthesis is split off before anything is matched, and the query is
tried against the two halves separately: the bottle's own name decides what this
product is, the reference only decides what it imitates.
"""

import re
from dataclasses import dataclass, replace

from rapidfuzz import fuzz

from parfum_finder.normalize import casefold_tr

# A run of letters or a run of digits, never a mix. Anything else, punctuation
# included, is a separator.
_WORD_PATTERN = re.compile(r"[^\W\d_]+|\d+")

# A size, however a shop writes it: a number with an optional comma or dot
# decimal, optional space, then "ml" or "cc" glued right onto the next letters
# ("30mldekant") or standing alone. Matched and cut out of the text before
# tokenizing, not filtered out token by token afterward, because a token-level
# filter cannot see that the unit was ever there once punctuation and spacing
# have already split the number away from it.
_SIZE_SPAN = re.compile(r"\d+(?:[.,]\d+)?\s*(?:ml|cc)")

# The parenthesis a clone shop puts the imitated original in. Not nested, since
# no shop writes one that way, and a greedy pattern would swallow everything
# between two unrelated parentheses on the same line.
_PARENTHESIS = re.compile(r"\(([^()]*)\)")

# What separates one perfume from the next in a typed line. Whitespace on both
# sides is required, so a hyphenated word stays one word.
_QUERY_SEPARATOR = re.compile(r"\s+-\s+")

# The concentration a title names, in the spellings sites actually use. Longer
# forms come first so "eau de parfum" is read as EDP instead of leaving "eau de"
# behind and matching the bare "parfum" entry.
_CONCENTRATIONS: tuple[tuple[tuple[str, ...], str], ...] = (
    (("extrait", "de", "parfum"), "Extrait"),
    (("eau", "de", "parfum"), "EDP"),
    (("eau", "de", "toilette"), "EDT"),
    (("eau", "de", "cologne"), "EDC"),
    (("extrait",), "Extrait"),
    (("elixir",), "Elixir"),
    (("parfum",), "Parfum"),
    (("edp",), "EDP"),
    (("edt",), "EDT"),
    (("edc",), "EDC"),
)

# Words every decant shop puts in its titles, which say nothing about which
# perfume it is. Turkish "parfüm" is noise; English "parfum" is a concentration,
# and the two stay distinct after folding because the ü survives it.
_NOISE = frozenset(
    {
        "dekant",
        "decant",
        # Both foldings of the Turkish suffixed form. Shops write "DEKANTI",
        # whose capital I folds to a dotted i here, and "dekantı" with the
        # dotless letter, and the two never meet as the same string.
        "dekanti",
        "dekantı",
        "parfüm",
        "orijinal",
        "original",
        "tester",
        "ml",
        "cc",
    }
)

# Below this a match is shown but flagged, never acted on by itself. Chosen so
# that a missing or extra word in a long name still passes while a different
# perfume does not.
DEFAULT_THRESHOLD = 85

# Below this a search result is not worth opening its product page for. Well
# under DEFAULT_THRESHOLD on purpose: everything between the two scores still
# gets fetched and still reaches the table flagged, so the only rows this loses
# are the ones nobody was going to act on. It buys back most of a scan, since
# every candidate kept costs one more request with a rate-limit gap in front
# of it.
PREFILTER_THRESHOLD = 60

# How many perfumes one search may ask for at once. Six shops times ten
# perfumes is already sixty site scans, and the number exists to keep a
# mispasted list from turning into half an hour of traffic against small shops.
MAX_QUERIES = 10


@dataclass(frozen=True)
class PerfumeQuery:
    """The perfume being looked for, split into its three identity parts.

    `concentration` may be left empty to mean "any". It is also read out of
    `name` when it was typed there, so a query built from one text field behaves
    the same as one filled in field by field.
    """

    brand: str
    name: str
    concentration: str = ""


@dataclass(frozen=True)
class Match:
    """One site title judged against the query.

    `concentration` is what the title itself named, not what was asked for. It is
    part of a perfume's identity, so it travels with the match: two titles that
    differ only there are two products with two price histories, and the results
    table has to be able to show which is which.

    `confident` is the only thing separating a match that may be acted on from
    one a person has to confirm first.

    `clone_of` is empty for the normal case. It is filled when the title is not
    the perfume that was searched for but a clone naming it in parentheses, and
    then it holds that parenthesis as the shop wrote it. A row carrying it is
    worth seeing, since a good clone can be worth buying instead, but it is not
    that perfume and must never be priced as it.
    """

    score: int
    concentration: str
    confident: bool
    clone_of: str = ""


def split_queries(text: str) -> list[str]:
    """Split one typed line into the perfumes it asks for, on " - ".

    The separator has to have whitespace on both sides. A hyphen inside a word
    is part of the word, "Jean-Paul Gaultier Le Male" is one perfume, and a shop
    that writes "Armaf - Club De Nuit" is why the spaced form is the one that
    means "and also".

    Nothing that works today changes meaning. The tokenizer never emits a
    hyphen, so a spaced one is already thrown away: "Dior Sauvage - Chanel Bleu"
    currently parses to the single query brand "dior", name "sauvage chanel
    bleu", which is nobody's search. This gives that line the reading a person
    typing it meant.

    Empty pieces are dropped, so a trailing separator or a double one is not an
    error worth stopping for. Repeats are dropped too, by the words they
    tokenize to rather than by their text, because scanning the same perfume
    twice costs a full second round of requests and adds nothing.

    A piece that tokenizes to nothing is kept, not dropped: parse_query is what
    explains why "dekant" is not a perfume, and swallowing it here would leave
    someone with a search that quietly ignored part of what they typed.
    """
    # Separators left over at either edge of a piece go too: a doubled "-  -"
    # leaves one behind, and it would travel into the URL the site is searched
    # with.
    parts = [part.strip(" \t-") for part in _QUERY_SEPARATOR.split(text)]
    queries: list[str] = []
    seen: set[tuple[str, ...] | str] = set()
    for part in parts:
        if not part:
            continue
        key = _tokenize(part) or part
        if key in seen:
            continue
        seen.add(key)
        queries.append(part)
    return queries


def parse_query(text: str) -> PerfumeQuery:
    """Split one typed line, "Dior Sauvage EDP", into the three identity parts.

    The first word is taken as the brand. Multi-word brands lose the rest of
    their name to the name field, which weakens the brand check rather than
    breaking it: "Yves" is still absent from every other house's titles, and the
    leftover words go on scoring inside the name.

    The concentration is pulled out even though match_title would find it
    anyway, because this is also what the perfume gets stored under. Leaving
    "EDP" inside the name would file the same bottle under two rows depending on
    how the person happened to type the search, and split its price history down
    the middle.

    The parts come back folded and normalized, since they are a database key and
    not something anyone reads. What the results table shows is the site's own
    raw_title.
    """
    tokens = _tokenize(text)
    if not tokens:
        raise ValueError("a search needs a perfume to look for, not an empty line")
    concentration, tokens = _split_concentration(tokens)
    brand, name_tokens = tokens[0], tokens[1:]
    if not name_tokens:
        raise ValueError(
            f"{text!r} names only a brand. A search needs the perfume too, "
            f"because a brand on its own matches everything that house sells."
        )
    return PerfumeQuery(
        brand=brand, name=" ".join(name_tokens), concentration=concentration
    )


def match_title(
    raw_title: str, query: PerfumeQuery, *, threshold: int = DEFAULT_THRESHOLD
) -> Match | None:
    """Judge one site title against a query, or None if it is not that perfume.

    None means a mandatory check failed: the brand is absent from the title, or
    the title names a different concentration than the one asked for. Those are
    rejections, not low scores, because no amount of name similarity makes
    another brand's bottle the right bottle.

    A returned Match may still be a poor one. Anything below `threshold` comes
    back with `confident` False so the caller can show it and ask, which is the
    behavior the basket depends on: a doubtful row must never be priced in
    silently.

    A query naming no concentration matches every concentration, which is what
    lets someone search without knowing whether a shop stocks the EDT or the EDP.
    The trade is that "Sauvage" then matches "Sauvage Elixir" too, a different
    product at a different price. Each match carries the concentration it found
    for exactly that reason: the caller keeps them apart and shows the difference
    instead of merging them.

    A title naming another perfume in parentheses is judged on the part outside
    them first. Only when that part is not the perfume asked for is the
    parenthesis tried, and a hit there comes back with `clone_of` set: this shop
    sells an imitation of what was searched for, not the thing itself.
    """
    own_title, reference = _split_clone_reference(raw_title)
    match = _match_text(own_title, query, threshold=threshold)
    if match is not None:
        return match
    if not reference:
        return None
    match = _match_text(reference, query, threshold=threshold)
    if match is None:
        return None
    # Never confident, whatever the reference scored. The score says how surely
    # this title points at the searched perfume, and the answer here is "surely,
    # as a copy of it". Leaving it confident would let the row be acted on as if
    # it were the real bottle.
    return replace(match, confident=False, clone_of=reference)


def title_could_match(
    raw_title: str | None, query: PerfumeQuery, *, threshold: int = PREFILTER_THRESHOLD
) -> bool:
    """Whether a search result's own listing text is worth opening the page for.

    Judged with match_title, at a much lower bar, so there is no second notion
    of similarity that can drift away from the real one. What this decides is
    only whether to spend a request; whether the product is the searched perfume
    is still decided later, on the product page, by match_title at its own
    threshold.

    A title with no text at all passes. There is nothing to judge it on, and a
    listing whose title selector reads nothing is exactly the case where
    guessing would hide a working product behind a profile gap.

    The cost of the low bar is deliberate and one-directional: a same-brand
    title scoring under `threshold` no longer reaches the results table, where
    today it appears flagged. Those are the rows nobody acts on, and every one
    of them is a request with a rate-limit gap in front of it.
    """
    if not raw_title:
        return True
    match = match_title(raw_title, query, threshold=threshold)
    return match is not None and match.score >= threshold


def _split_clone_reference(raw_title: str) -> tuple[str, str]:
    """Split a title into what the bottle is and what it says it imitates.

    The second half is empty for the ordinary title with no parentheses. Several
    parentheses join into one reference rather than only the last being kept, so
    a shop that splits the brand and the perfume across two of them still ends up
    with both.
    """
    references = _PARENTHESIS.findall(raw_title)
    if not references:
        return raw_title, ""
    own = _PARENTHESIS.sub(" ", raw_title)
    return own, " ".join(part.strip() for part in references if part.strip())


def _match_text(raw_title: str, query: PerfumeQuery, *, threshold: int) -> Match | None:
    """Judge one piece of title text, with no clone handling of its own."""
    title_tokens = _tokenize(raw_title)
    brand_tokens = _tokenize(query.brand)
    if not _covers(title_tokens, brand_tokens):
        return None

    found, title_rest = _split_concentration(title_tokens)
    wanted, query_rest = _split_concentration(brand_tokens + _tokenize(query.name))
    if query.concentration:
        wanted = _canonical(query.concentration)
    if wanted and found != wanted:
        return None

    if _ends_with(title_rest, query_rest):
        return Match(score=100, concentration=found, confident=True)

    # Both sides lose the brand's words, not just the title's. Dropping them
    # from one side only made a query whose brand word also appears later in
    # the name ("Le Male Le Parfum") score its own perfect match badly.
    score = _similarity(
        _without(query_rest, brand_tokens), _without(title_rest, brand_tokens)
    )
    return Match(score=score, concentration=found, confident=score >= threshold)


def _tokenize(text: str) -> tuple[str, ...]:
    """Fold, cut a size out, split into words and numbers, and drop noise.

    A size span ("5 ml", "2,7 ml", "30mldekant") is cut out of the folded text
    first, before the text is split into words at all, because by the time "ml"
    has become its own token there is no way to tell it apart from a number that
    is simply part of the name.

    A bare number that survives that cut stays as its own token instead of being
    dropped. The 540 of Baccarat Rouge 540 and the 212 of Carolina Herrera 212
    are not noise, they are the only thing distinguishing that product from
    every other one sharing the rest of its words; treating every digit as size
    noise made "212" and "212 VIP" tokenize to the same leftover words and
    stopped the matcher telling them apart.
    """
    folded = casefold_tr(text)
    folded = _SIZE_SPAN.sub(" ", folded)
    words = _WORD_PATTERN.findall(folded)
    return tuple(word for word in words if word not in _NOISE)


def _covers(title_tokens: tuple[str, ...], brand_tokens: tuple[str, ...]) -> bool:
    """Whether every word of the searched brand appears in the title.

    Every word, because a brand like "Maison Francis Kurkdjian" shares a word
    with plenty of houses it has nothing to do with. An empty brand covers
    everything, which is how a query with no brand stays possible at all.
    """
    return all(token in title_tokens for token in brand_tokens)


def _ends_with(title_tokens: tuple[str, ...], query_tokens: tuple[str, ...]) -> bool:
    """Whether the whole query sits at the end of the title, word for word.

    This is the one shape where extra title words are certainly not part of the
    perfume: everything a shop puts in front of the searched words is the rest
    of the brand it wrote out in full. "Dior Sauvage" typed against "Christian
    Dior Sauvage", or "Le Male Le Parfum" against "Jean Paul Gaultier Le Male Le
    Parfum", is the same bottle, and scoring those in the forties made every
    score on the screen mean nothing.

    Contiguous and at the end, both. Contiguity keeps "Dior Sauvage" away from
    "Dior Eau Sauvage", where the extra word is what makes it another perfume.
    The end position keeps "Carolina Herrera 212" away from "Carolina Herrera
    212 VIP", where the words that follow are the ones that matter.

    What it cannot tell apart is a longer name ending in the searched one, like
    "Ultra Le Male" against a search for "Le Male" with no brand typed. A search
    that names no brand cannot separate those anyway, and the results table
    shows every title in full for exactly this reason.
    """
    if not query_tokens:
        return False
    return title_tokens[-len(query_tokens) :] == query_tokens


def _without(tokens: tuple[str, ...], remove: tuple[str, ...]) -> tuple[str, ...]:
    """Drop the brand's words so only the name is left to score.

    Leaving them in would let a matching brand carry a mismatched name over the
    threshold, which is the wrong-match-scores-high failure this module exists
    to prevent.
    """
    dropped = set(remove)
    return tuple(token for token in tokens if token not in dropped)


def _split_concentration(tokens: tuple[str, ...]) -> tuple[str, tuple[str, ...]]:
    """Cut the concentration out and return it next to the remaining words.

    Separating it is what keeps "Sauvage" and "Sauvage Elixir" apart. Left in the
    name, "elixir" would just be one more word for the fuzzy score to shrug off,
    and the two would match each other at a high score despite being different
    products with different prices.
    """
    for phrase, label in _CONCENTRATIONS:
        index = _index_of(tokens, phrase)
        if index is not None:
            return label, tokens[:index] + tokens[index + len(phrase) :]
    return "", tokens


def _index_of(tokens: tuple[str, ...], phrase: tuple[str, ...]) -> int | None:
    for start in range(len(tokens) - len(phrase) + 1):
        if tokens[start : start + len(phrase)] == phrase:
            return start
    return None


def _canonical(concentration: str) -> str:
    """Read a written concentration back as one of the canonical labels.

    Returns it unchanged when nothing is recognized, so an unexpected spelling
    fails to match loudly instead of being silently treated as "any".
    """
    label, _ = _split_concentration(_tokenize(concentration))
    return label or concentration.strip()


def _similarity(name_tokens: tuple[str, ...], title_tokens: tuple[str, ...]) -> int:
    """Score what is left of the two names against each other, 0-100.

    Sorted rather than set-based, though both ignore word order. A set ratio
    scores a subset as a perfect match, so searching "Sauvage" would rate a title
    reading "Eau Sauvage" 100 out of 100 and hand back a different perfume with
    full confidence. Sorting instead makes the extra word cost something, and the
    title still appears in the list, just flagged for a person to confirm.

    That trade is deliberate: nothing is ever dropped for a low score, so an
    over-cautious score costs one confirmation, while an over-generous one puts
    the wrong bottle in the basket at a price that looks like a bargain.

    Two empty remainders score 100. That is the case where the query is nothing
    but a brand and the title is nothing but that brand, so the two really do say
    the same thing; scoring it 0 would reject a title that matched completely.
    """
    if not name_tokens and not title_tokens:
        return 100
    return int(
        round(fuzz.token_sort_ratio(" ".join(name_tokens), " ".join(title_tokens)))
    )
