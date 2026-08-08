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
"""

import re
from dataclasses import dataclass

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
    """

    score: int
    concentration: str
    confident: bool


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
    """
    title_tokens = _tokenize(raw_title)
    brand_tokens = _tokenize(query.brand)
    if not _covers(title_tokens, brand_tokens):
        return None
    title_tokens = _without(title_tokens, brand_tokens)

    found, title_tokens = _split_concentration(title_tokens)
    wanted, name_tokens = _split_concentration(_tokenize(query.name))
    if query.concentration:
        wanted = _canonical(query.concentration)
    if wanted and found != wanted:
        return None

    score = _similarity(name_tokens, title_tokens)
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
