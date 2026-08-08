"""Tests for parfum_finder.matcher.

The thing being defended here is not "does it score well". It is that a wrong
perfume can never come back looking right: another brand, or another
concentration, is rejected outright however similar the words are, and anything
the name score is unsure about is handed over flagged rather than dropped or
quietly accepted.
"""

from parfum_finder.matcher import DEFAULT_THRESHOLD, Match, PerfumeQuery, match_title


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
