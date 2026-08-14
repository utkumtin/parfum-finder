"""Tests for parfum_finder.matcher.

The thing being defended here is not "does it score well". It is that a wrong
perfume can never come back looking right: another brand, or another
concentration, is rejected outright however similar the words are, and anything
the name score is unsure about is handed over flagged rather than dropped or
quietly accepted.
"""

import pytest

from parfum_finder.matcher import (
    DEFAULT_THRESHOLD,
    Match,
    PerfumeQuery,
    match_title,
    parse_query,
    product_label,
    split_queries,
    title_could_match,
)


def test_a_shop_title_with_all_its_noise_matches_the_perfume() -> None:
    # What a real listing looks like: brand, name, concentration, size and three
    # words of shop vocabulary, in whatever order the shop felt like.
    match = match_title(
        "Creed Aventus EDP 5 ml Dekant Orijinal",
        PerfumeQuery("Creed", "Aventus", "EDP"),
    )

    assert match == Match(score=100, concentration="EDP", confident=True)


def test_another_brands_bottle_is_rejected_however_close_the_name_is() -> None:
    # The names are the same word. Only the brand says these are different
    # bottles at different prices, so the brand cannot be a matter of degree.
    assert match_title("Creed Sauvage 5 ml", PerfumeQuery("Dior", "Sauvage")) is None


def test_a_different_concentration_is_rejected_not_scored_down() -> None:
    # Bleu de Chanel EDT and EDP are separate products with separate prices.
    # Scoring this one 95 would put the wrong one in the basket.
    assert (
        match_title(
            "Chanel Bleu de Chanel EDP Dekant",
            PerfumeQuery("Chanel", "Bleu de Chanel", "EDT"),
        )
        is None
    )


def test_elixir_is_a_concentration_so_it_cannot_be_matched_away() -> None:
    # Sauvage Elixir is its own product. Treated as one more word in the name it
    # would be shrugged off by the fuzzy score and sold as plain Sauvage.
    assert (
        match_title("Dior Sauvage Elixir 5 ml", PerfumeQuery("Dior", "Sauvage", "EDT"))
        is None
    )


def test_an_unasked_concentration_comes_back_named_instead_of_hidden() -> None:
    # A query that names no concentration deliberately matches all of them, so
    # someone can search without knowing what a shop stocks. What keeps that
    # honest is that the match says which one it found, so the caller can show
    # Sauvage and Sauvage Elixir as the two different products they are.
    plain = match_title("Dior Sauvage 5 ml Dekant", PerfumeQuery("Dior", "Sauvage"))
    elixir = match_title("Dior Sauvage Elixir 5 ml", PerfumeQuery("Dior", "Sauvage"))

    assert plain is not None and elixir is not None
    assert (plain.concentration, elixir.concentration) == ("", "Elixir")


def test_an_extra_word_in_the_name_is_flagged_rather_than_accepted() -> None:
    # Eau Sauvage is not Sauvage. A subset-forgiving score would call this a
    # perfect match; it has to come back doubtful instead.
    match = match_title("Dior Eau Sauvage EDT", PerfumeQuery("Dior", "Sauvage", "EDT"))

    assert match is not None
    assert match.confident is False
    assert match.score < DEFAULT_THRESHOLD


def test_a_doubtful_match_is_still_returned_to_be_confirmed() -> None:
    # Right brand, unrelated name. Dropping it would hide a title someone may
    # still recognize; accepting it silently is what must not happen.
    match = match_title("Dior Homme Intense EDP", PerfumeQuery("Dior", "Sauvage"))

    assert match is not None and match.confident is False


def test_turkish_capitals_do_not_break_the_brand_check() -> None:
    # A shop writing its titles in capitals produces "DİOR", and Python folds
    # that İ to an i with a separate combining dot. Compared naively the brand
    # simply would not be there, and the whole shop would drop out silently.
    match = match_title(
        "DİOR SAUVAGE EDT 5 ML DEKANTI", PerfumeQuery("Dior", "Sauvage")
    )

    assert match is not None and match.confident is True


def test_the_turkish_word_for_perfume_is_noise_but_parfum_is_a_concentration() -> None:
    # "parfüm" is what the shop calls its wares; "Parfum" is what the bottle is.
    # The two survive folding as different words, and the difference is load
    # bearing: read as noise, Parfum would stop separating from Extrait or EDP.
    noise = match_title(
        "Tom Ford Oud Wood parfüm 5ml", PerfumeQuery("Tom Ford", "Oud Wood")
    )
    real = match_title(
        "Tom Ford Oud Wood Parfum 5ml", PerfumeQuery("Tom Ford", "Oud Wood")
    )

    assert noise is not None and noise.concentration == ""
    assert real is not None and real.concentration == "Parfum"


def test_a_spelled_out_concentration_reads_as_its_short_label() -> None:
    # Sites write both. Read as separate labels they would split one product's
    # price history in two.
    match = match_title(
        "Chanel Bleu de Chanel Eau de Parfum",
        PerfumeQuery("Chanel", "Bleu de Chanel", "EDP"),
    )

    assert match is not None and match.concentration == "EDP"


def test_extrait_de_parfum_is_not_read_as_parfum() -> None:
    # The longer name contains the shorter one. Matched in the wrong order this
    # would file an Extrait under Parfum, which is a different bottle again.
    match = match_title(
        "Tom Ford Tobacco Vanille Extrait de Parfum",
        PerfumeQuery("Tom Ford", "Tobacco Vanille"),
    )

    assert match is not None and match.concentration == "Extrait"


def test_a_concentration_typed_into_the_name_still_counts() -> None:
    # Someone typing one line into a search box puts everything in the name. It
    # has to behave like the field-by-field query, or the same search would mean
    # two different things depending on where it was typed.
    assert (
        match_title("Dior Sauvage EDP 5 ml", PerfumeQuery("Dior", "Sauvage EDT"))
        is None
    )


def test_a_brand_needs_all_of_its_words_not_one() -> None:
    # "Maison" alone is shared by houses that have nothing to do with each other,
    # and the names here are close enough for a fuzzy score to be fooled.
    assert (
        match_title(
            "Maison Margiela Replica Jazz Club",
            PerfumeQuery("Maison Francis Kurkdjian", "Jazz Club"),
        )
        is None
    )


def test_word_order_does_not_decide_the_score() -> None:
    # Shops write the brand last as often as first, and the size wherever it
    # fits. None of that says anything about which perfume it is.
    match = match_title(
        "Baccarat Rouge Maison Francis Kurkdjian 5ml",
        PerfumeQuery("Maison Francis Kurkdjian", "Baccarat Rouge"),
    )

    assert match == Match(score=100, concentration="", confident=True)


def test_the_confidence_threshold_can_be_moved_by_the_caller() -> None:
    # The same score has to be able to mean different things in different places:
    # a bulk scan can afford to be strict, a person searching by hand cannot.
    title, query = "Dior Eau Sauvage EDT", PerfumeQuery("Dior", "Sauvage", "EDT")

    strict = match_title(title, query, threshold=100)
    lenient = match_title(title, query, threshold=50)

    assert strict is not None and lenient is not None
    assert strict.score == lenient.score
    assert (strict.confident, lenient.confident) == (False, True)


def test_a_brand_only_query_matches_a_title_that_is_only_that_brand() -> None:
    # Someone browsing one house rather than one perfume. Once the brand and the
    # shop's own words are taken out both sides are empty, and empty against
    # empty is agreement, not a score of zero.
    match = match_title("Creed 5ml dekant", PerfumeQuery("Creed", ""))

    assert match == Match(score=100, concentration="", confident=True)


def test_an_unrecognized_concentration_matches_nothing_instead_of_everything() -> None:
    # A typo or a spelling nobody uses. Treated as "unspecified" it would widen
    # the search instead of narrowing it, which is the opposite of what someone
    # typing a concentration is asking for.
    assert (
        match_title("Dior Sauvage EDP", PerfumeQuery("Dior", "Sauvage", "EDPP")) is None
    )


def test_a_number_in_the_name_stays_part_of_the_name() -> None:
    # 212 and 212 VIP are different products sold by the same brand, and the
    # number is the only thing that says so. A query for plain "212" still has
    # to land squarely on the plain product...
    exact = match_title(
        "Carolina Herrera 212 EDT", PerfumeQuery("Carolina Herrera", "212")
    )
    assert exact == Match(score=100, concentration="EDT", confident=True)

    # ...and come back doubtful, not silently perfect, against the VIP one.
    # Confident would put the wrong bottle in the basket; rejecting it outright
    # would hide a title someone may still recognize as what they meant.
    vip = match_title(
        "Carolina Herrera 212 VIP EDT", PerfumeQuery("Carolina Herrera", "212")
    )
    assert vip is not None and vip.confident is False


def test_a_numeric_brand_still_gates_out_a_different_brand() -> None:
    # A brand written only in digits used to tokenize to nothing at all, which
    # made the mandatory brand check pass for every title, numeric brand or not.
    # "212" has to be absent-or-present like any other brand.
    assert match_title("Chanel No 5 EDP", PerfumeQuery("212", "")) is None


def test_every_plain_size_label_form_disappears_completely() -> None:
    # Real shops write a size more ways than "5 ml": a comma decimal, a
    # trailing space, an uppercase unit, or jammed against the next word with
    # no space at all. Each has to vanish without a trace, or the leftover
    # digit or unit would read as an extra word in the name and turn a perfect
    # match into a merely doubtful one.
    for label in ("3 ml", "3ml", "10 ml ", "1 ML", "30mldekant"):
        match = match_title(
            f"Dior Sauvage EDT {label}", PerfumeQuery("Dior", "Sauvage", "EDT")
        )
        assert match == Match(score=100, concentration="EDT", confident=True), label


def test_a_comma_decimal_size_with_trailing_text_leaves_no_stray_digit() -> None:
    # "2,7 ml - metal sprey" pairs a comma decimal with a note after the unit.
    # The size still has to disappear completely and leave only the note
    # behind; an orphaned "2" surviving the cut would read as part of the name
    # and drag the score down for a reason that has nothing to do with the name.
    with_size = match_title(
        "Dior Sauvage EDT 2,7 ml - metal sprey",
        PerfumeQuery("Dior", "Sauvage", "EDT"),
    )
    without_size = match_title(
        "Dior Sauvage EDT - metal sprey", PerfumeQuery("Dior", "Sauvage", "EDT")
    )

    assert with_size == without_size


def test_parse_query_files_the_same_perfume_under_one_identity() -> None:
    # The three parts become a UNIQUE key in the perfumes table. If the
    # concentration stayed inside the name, "Dior Sauvage EDP" and a later
    # "Dior Sauvage Eau de Parfum" would open two rows for one bottle and cut
    # its price history in half.
    assert parse_query("Dior Sauvage EDP") == parse_query("dior sauvage eau de parfum")
    assert parse_query("Dior Sauvage EDP").concentration == "EDP"
    assert parse_query("Dior Sauvage EDP").name == "sauvage"


def test_parse_query_keeps_two_concentrations_of_one_perfume_apart() -> None:
    # The other half of the same rule: separating the concentration must not
    # merge them. These are two products at two prices.
    assert parse_query("Dior Sauvage EDT") != parse_query("Dior Sauvage EDP")


def test_parse_query_leaves_a_multi_word_brand_in_the_name() -> None:
    # Only the first word is the brand, so the rest goes on scoring in the name
    # rather than being thrown away. The brand check gets weaker, not wrong.
    query = parse_query("Yves Saint Laurent Libre")

    assert query.brand == "yves"
    assert query.name == "saint laurent libre"


def test_parse_query_rejects_a_line_naming_only_a_brand() -> None:
    # "Dior" alone would match every bottle Dior sells, and each of them would
    # be stored as the perfume that was asked for.
    with pytest.raises(ValueError, match="names only a brand"):
        parse_query("Dior Parfum")


def test_parse_query_rejects_an_empty_search() -> None:
    with pytest.raises(ValueError):
        parse_query("   ")


# The clone shop titles below are copied from fixtures/luxurydekant/search.html.
# That shop sells both originals and imitations, and names the imitated perfume
# in parentheses.

_CLONE_TITLE = (
    "Armaf – Club De Nuit Untold (Maison Francis Kurkdjian – Baccarat Rouge 540)"
)
_CLONE_SIBLING = "Armaf – Club De Nuit Woman (Chanel – Coco Mademoiselle)"
_PLAIN_SIBLING = "Armaf – Club De Nuit Bling"


def test_the_original_being_searched_never_comes_back_as_the_clone_itself() -> None:
    # The imitation carries the original's brand and full name inside its
    # parentheses, so before the split it passed the brand check and matched.
    # A cheap clone landing in a list sorted by price per ml sorts straight to
    # the top and reads as the bargain the original never was.
    match = match_title(
        _CLONE_TITLE, parse_query("Maison Francis Kurkdjian Baccarat Rouge 540")
    )

    assert match is not None
    assert match.clone_of == "Maison Francis Kurkdjian – Baccarat Rouge 540"
    assert not match.confident


def test_a_clone_is_still_shown_because_it_may_be_worth_buying() -> None:
    # Hiding it would answer a question nobody asked. A good imitation is a
    # real option, so the row stays visible and says what it copies; whether it
    # is a good one is a judgement made outside this program.
    match = match_title(
        _CLONE_TITLE, parse_query("Maison Francis Kurkdjian Baccarat Rouge 540")
    )

    assert match is not None
    assert match.clone_of


def test_a_clone_carries_the_identity_read_off_its_own_title() -> None:
    # This is what the clone gets stored and basketed under. Reading it off the
    # part outside the parentheses is the whole reason a clone can be bought on
    # purpose: filed under the original it would be priced from other shops'
    # listings of the original, and somebody would pay for the wrong bottle.
    match = match_title(
        _CLONE_TITLE, parse_query("Maison Francis Kurkdjian Baccarat Rouge 540")
    )

    assert match is not None
    assert match.clone_identity == PerfumeQuery(
        brand="armaf", name="club de nuit untold", concentration=""
    )


def test_a_clone_whose_own_title_names_one_word_has_no_identity_to_store() -> None:
    # A brand and a perfume is the least an identity can be. "Untold" alone
    # cannot be split into both, and inventing the missing half would put a
    # made-up perfume in the database. None is what keeps such a row on screen
    # and out of the store, which is the only case left that cannot be bought.
    match = match_title(
        "Untold (Maison Francis Kurkdjian – Baccarat Rouge 540)",
        parse_query("Maison Francis Kurkdjian Baccarat Rouge 540"),
    )

    assert match is not None
    assert match.clone_of
    assert match.clone_identity is None


def test_a_low_score_non_clone_match_carries_its_own_identity() -> None:
    # "Layton" finding "Layton Exclusif" is the matcher doing its job, not a
    # bug: no concentration or clone parenthesis separates them, only a low
    # score does. own_identity is what lets the caller file the two as
    # different bottles instead of one shared price history.
    match = match_title(
        "Parfums De Marly Layton Exclusif", parse_query("Parfums de Marly Layton")
    )

    assert match is not None
    assert not match.confident
    assert not match.clone_of
    assert match.own_identity == PerfumeQuery(
        brand="parfums", name="de marly layton exclusif", concentration=""
    )


def test_a_confident_match_carries_no_own_identity() -> None:
    # A confident match is being treated as the searched perfume on purpose,
    # so there is nothing for the caller to file it under but the query.
    match = match_title(
        "Parfums De Marly Layton", parse_query("Parfums de Marly Layton")
    )

    assert match is not None
    assert match.confident
    assert match.own_identity is None


def test_a_clones_own_name_is_scored_without_what_it_imitates() -> None:
    # Searching for the imitation itself. Before the split, the referenced
    # perfume's words counted against the name, and the right bottle scored 59
    # while a different Club de Nuit scored 67, so the wrong one sorted above
    # the one asked for.
    query = parse_query("Armaf Club de Nuit Woman")
    wanted = match_title(_CLONE_SIBLING, query)
    other = match_title(_PLAIN_SIBLING, query)

    assert wanted is not None and other is not None
    assert wanted.score == 100
    assert wanted.confident
    assert wanted.clone_of == ""
    assert wanted.score > other.score


def test_a_parenthesis_naming_neither_perfume_matches_nothing() -> None:
    # The reference half is matched with the same mandatory brand check as the
    # name half, so a parenthesis holding a size or a note cannot turn a title
    # into a clone of whatever was searched for.
    assert match_title("Dior Sauvage EDP (100 ml)", parse_query("Chanel Bleu")) is None


def test_a_parenthesis_holding_only_a_note_leaves_a_normal_match_alone() -> None:
    # Most parentheses are not clone references at all. Splitting one off must
    # not cost an ordinary title its match.
    match = match_title("Dior Sauvage EDP (Tester)", parse_query("Dior Sauvage EDP"))

    assert match is not None
    assert match.confident
    assert match.clone_of == ""


def test_a_brand_the_shop_writes_out_in_full_does_not_cost_the_match() -> None:
    # A shop writes "Christian Dior" where the search said "Dior". Every word of
    # the query is there, in order, at the end of the title, and the only extra
    # is the rest of the house's own name. Scored as an extra name word this came
    # back at 58, which flagged a perfect match and made every score on screen
    # untrustworthy.
    match = match_title(
        "Christian Dior Sauvage EDP 5 ml Dekant", parse_query("Dior Sauvage EDP")
    )

    assert match is not None
    assert match.score == 100
    assert match.confident


def test_a_search_that_names_no_brand_still_matches_the_full_title() -> None:
    # Typed without a brand at all. The first word becomes the "brand", and its
    # second appearance inside the name used to be stripped from the title but
    # not from the query, so the right bottle scored 47.
    match = match_title(
        "Jean Paul Gaultier Le Male Le Parfum 5 ml", parse_query("Le Male Le Parfum")
    )

    assert match is not None
    assert match.score == 100
    assert match.confident


def test_an_extra_word_inside_the_name_is_still_a_different_perfume() -> None:
    # The guard the full-title rule must not break. Dior Eau Sauvage is not Dior
    # Sauvage, and the query's words are not contiguous in the title, so this
    # stays flagged instead of being lifted to a perfect score.
    match = match_title("Dior Eau Sauvage EDP 5 ml", parse_query("Dior Sauvage EDP"))

    assert match is not None
    assert not match.confident


def test_words_after_the_searched_name_still_count_against_it() -> None:
    # 212 VIP is its own product. The query is contiguous here but not at the
    # end of the title, and what follows is exactly what makes it another
    # bottle, so it must not be lifted to a perfect score.
    match = match_title(
        "Carolina Herrera 212 VIP 5 ml", parse_query("Carolina Herrera 212")
    )

    assert match is not None
    assert match.score < 100


def test_a_line_naming_three_perfumes_is_read_as_three_searches() -> None:
    # The whole point of the separator: one line, three scans, in the order
    # they were typed.
    assert split_queries(
        "Xerjoff Naxos - Dior Sauvage - Louis Vuitton Ombre Nomade"
    ) == ["Xerjoff Naxos", "Dior Sauvage", "Louis Vuitton Ombre Nomade"]


def test_a_hyphen_inside_a_brand_name_does_not_split_the_search() -> None:
    # The reason the separator demands whitespace on both sides. Split here and
    # the first half is a brand with no perfume, which cannot be searched at all.
    assert split_queries("Jean-Paul Gaultier Le Male") == ["Jean-Paul Gaultier Le Male"]


def test_one_perfume_is_still_one_search() -> None:
    assert split_queries("Dior Sauvage EDP") == ["Dior Sauvage EDP"]


def test_a_stray_separator_is_not_worth_failing_over() -> None:
    # Someone mid-typing, or one paste too many. Both readings of the line name
    # the same two perfumes, so there is nothing here to stop for.
    assert split_queries("Creed Aventus -  - Dior Sauvage - ") == [
        "Creed Aventus",
        "Dior Sauvage",
    ]


def test_the_same_perfume_typed_twice_is_scanned_once() -> None:
    # Matched on the words, not the text, because the second round of requests
    # costs a full scan and returns rows that are already on the screen.
    assert split_queries("Dior Sauvage EDP - dior   sauvage edp") == [
        "Dior Sauvage EDP"
    ]


def test_a_piece_that_names_no_perfume_survives_to_be_complained_about() -> None:
    # "dekant" tokenizes to nothing. Dropping it here would leave someone with a
    # search that silently ignored a third of what they typed; parse_query is
    # what says why it is not a perfume.
    assert split_queries("Dior Sauvage - dekant") == ["Dior Sauvage", "dekant"]


def test_a_listing_worth_opening_is_the_one_naming_the_searched_perfume() -> None:
    assert title_could_match(
        "Christian Dior Sauvage EDP 5 ml Dekant", parse_query("Dior Sauvage EDP")
    )


def test_another_perfume_from_the_same_house_is_not_opened() -> None:
    # The request this saves. The brand check alone passes here, so without a
    # score floor every bottle Dior makes would cost one product page fetch
    # with a rate-limit gap in front of it.
    assert not title_could_match(
        "Dior Homme Intense EDP 5 ml Dekant", parse_query("Dior Sauvage EDP")
    )


def test_a_listing_with_no_readable_title_is_opened_anyway() -> None:
    # Nothing to judge it on. A profile whose listing-title selector reads
    # nothing must not become a profile that silently stops seeing products.
    assert title_could_match(None, parse_query("Dior Sauvage EDP"))
    assert title_could_match("", parse_query("Dior Sauvage EDP"))


def test_a_doubtful_listing_is_still_opened_because_the_page_decides() -> None:
    # Between the two thresholds: not good enough to act on, good enough to
    # spend a request on. The product page's own title is what gets scored.
    title = "Dior Eau Sauvage EDP 5 ml"
    query = parse_query("Dior Sauvage EDP")
    match = match_title(title, query)

    assert match is not None
    assert not match.confident
    assert title_could_match(title, query)


# Every one of these is a title a real shop actually served, pulled out of the
# database this app filled on a live scan. Invented titles would only prove the
# function agrees with whoever wrote them; the whole risk here is what six shops
# do to one bottle's name, and that is not something to guess at.
REAL_TITLES = [
    # One bottle, six shops. A hyphen glued to the brand, an en dash in the
    # middle, a size in seven different places, and one shop's packaging suffix.
    ("Jean Paul Gaultier Le Male Le Parfum", "Jean Paul Gaultier Le Male Le Parfum"),
    (
        "Jean Paul Gaultier Le Male Le Parfum 2,7 ml - metal sprey",
        "Jean Paul Gaultier Le Male Le Parfum",
    ),
    (
        "Jean Paul Gaultier Le Male Le Parfum 3 ml - plastik sprey",
        "Jean Paul Gaultier Le Male Le Parfum",
    ),
    (
        "Jean Paul Gaultier Le Male Le Parfum 15 ml",
        "Jean Paul Gaultier Le Male Le Parfum",
    ),
    ("Jean Paul Gaultier- Le Male Le Parfum", "Jean Paul Gaultier Le Male Le Parfum"),
    ("Parfums de Marly Layton", "Parfums De Marly Layton"),
    ("Parfums de Marly Layton 3 ml", "Parfums De Marly Layton"),
    ("Parfums De Marly Layton 2,7 ml - metal sprey", "Parfums De Marly Layton"),
    ("Parfums de Marly – Layton", "Parfums De Marly Layton"),
    # The split that has to happen. Same query, same shop, different bottle.
    ("Parfums de Marly Layton Exclusif", "Parfums De Marly Layton Exclusif"),
    ("Amouage Interlude Black Iris", "Amouage Interlude Black Iris"),
    ("Amouage Interlude Black Iris 20 ml", "Amouage Interlude Black Iris"),
    # One shop lower-cases a word mid-title, which is why the label is rebuilt
    # instead of being taken as written.
    ("Amouage Interlude Black iris", "Amouage Interlude Black Iris"),
    # The concentration is part of what the bottle is, so the EDP listing is its
    # own block rather than joining the three lines above.
    (
        "Amouage Interlude Black Iris EDP 2,7 ml - metal sprey",
        "Amouage Interlude Black Iris EDP",
    ),
    ("Amouage Interlude Black Iris EDP 12 ml", "Amouage Interlude Black Iris EDP"),
    ("Louis Vuitton Afternoon Swim", "Louis Vuitton Afternoon Swim"),
    (
        "Louis Vuitton Afternoon Swim 3 ml - plastik sprey",
        "Louis Vuitton Afternoon Swim",
    ),
    ("Louis Vuitton Afternoon Swim 15 ml", "Louis Vuitton Afternoon Swim"),
    ("Hugo Boss Bottled Absolute", "Hugo Boss Bottled Absolute"),
    ("Hugo Boss Bottled Absolute 5 ml", "Hugo Boss Bottled Absolute"),
    ("Hugo – Boss Bottled Absolu", "Hugo Boss Bottled Absolu"),
    ("Hugo Boss Bottled Absolu Edp 3 ml", "Hugo Boss Bottled Absolu EDP"),
    ("Hugo Boss Bottled Absolu EDP 2024 8 ml", "Hugo Boss Bottled Absolu 2024 EDP"),
]


@pytest.mark.parametrize(("raw_title", "expected"), REAL_TITLES)
def test_real_shop_titles_reduce_to_the_product_they_are_about(
    raw_title: str, expected: str
) -> None:
    assert product_label(raw_title) == expected


def test_every_shops_spelling_of_one_bottle_lands_in_one_block() -> None:
    # The reason the function exists. Five shops, five spellings, five sizes,
    # one heading -- a table that split these into five blocks of one row each
    # would be unreadable and would compare nothing.
    labels = {
        product_label(title)
        for title, _ in REAL_TITLES
        if title.startswith("Parfums") and "Exclusif" not in title
    }
    assert labels == {"Parfums De Marly Layton"}


def test_a_longer_named_bottle_does_not_join_the_shorter_ones_block() -> None:
    # "Layton Exclusif" comes back on a search for "Layton" at 77%, and it is a
    # different perfume at a different price. Sharing a block with Layton is the
    # failure this whole layer is meant to prevent.
    assert product_label("Parfums de Marly Layton Exclusif") != product_label(
        "Parfums de Marly Layton"
    )


def test_a_clone_is_labelled_by_the_bottle_it_is_and_not_what_it_imitates() -> None:
    # The parenthesis names the original, so reading it as part of the name
    # would file the clone under the original's heading, right next to real
    # bottles at a fraction of the price.
    assert (
        product_label(
            "Armaf - Club De Nuit Untold "
            "(Maison Francis Kurkdjian - Baccarat Rouge 540)"
        )
        == "Armaf Club De Nuit Untold"
    )


def test_a_title_with_no_product_words_left_has_no_label() -> None:
    # Nothing to head a block with. The caller has to fall back to the raw
    # title rather than open a block named "".
    assert product_label("5 ml dekant") == ""
    assert product_label("") == ""
