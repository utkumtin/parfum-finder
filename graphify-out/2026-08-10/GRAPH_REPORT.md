# Graph Report - parfum-finder  (2026-08-10)

## Corpus Check
- 68 files · ~255,842 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1744 nodes · 4759 edges · 73 communities (71 shown, 2 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 190 edges (avg confidence: 0.57)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `5456b5f3`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- TUI App & Screens
- Site Profiles & Templates
- Title Matcher
- HTTP/Browser Fetching
- Search/Basket Domain Models
- Search Engine per Site
- Platform Discovery Flow
- CLI Entry Points
- Architecture Rationale Docs
- Search Engine Core
- Basket Optimizer Core
- Basket Store & Pricing
- JSON-LD Product Extraction
- Basket TUI Screen
- Platform Schema
- Product Extraction
- Schema Field Patterns
- Offline Profile Validation
- Playwright Errors
- Search TUI Screen
- Snapshot Writing
- Candidate Filtering
- Basket Site Scenarios
- Price/Size Normalization
- JSON Schema Primitives
- SQLite Store
- Site Profile Fields
- Site Schema Validation Tests
- Variant Rule Fields
- Discovery CLI Reporting
- Store Timestamp Tests
- Live Profile Validation
- Variant Extraction Fields
- _ResultRow
- Fetch Strategy Probing
- Platform Field Mapping
- Shipping Config Schema
- Discovery Report Model
- TUI Confirm Dialog
- TUI App Shell
- Fetch Backends
- HTTP Request Schema
- Fixture Fetcher (Tests)
- Validation Reporting
- Decant Variant Rules
- Multi-Site Search Run
- Offline Validation Fixtures
- Basket Domain Logic
- ._build_rows
- test_engine.py
- Profile Age Checks
- ._refresh_table
- ._cells
- conftest.py
- Endpoint Schema Fields
- tui/__init__.py
- Request Schema Fields
- _FixtureFetcher
- ComposeResult
- _named_profile
- _NoRootParser
- Price History
- SiteValidation
- enum
- .__call__
- rate_limit_ms
- format_age
- _resolve_platform
- extract_css_variants
- Variant Pattern A
- Project Root
- basket_prices
- ComposeResult

## God Nodes (most connected - your core abstractions)
1. `search_site()` - 66 edges
2. `SearchScreen` - 58 edges
3. `_profile()` - 58 edges
4. `discover()` - 56 edges
5. `SiteResult` - 53 edges
6. `BasketScreen` - 53 edges
7. `PerfumeQuery` - 52 edges
8. `_app()` - 44 edges
9. `match_title()` - 43 edges
10. `Fetcher` - 42 edges

## Surprising Connections (you probably didn't know these)
- `Shipping Non-linearity Rationale (why cheapest-per-item is wrong)` --semantically_similar_to--> `sites/ Site Profile Directory`  [INFERRED] [semantically similar]
  ARCHITECTURE.md → sites/README.md
- `Variant Pattern B (dropdown + AJAX price)` --semantically_similar_to--> `Variant Selector Detector Fix (WooCommerce 'variation' vs 'variant')`  [INFERRED] [semantically similar]
  ARCHITECTURE.md → docs/discovery-report.md
- `test_real_measurement_picks_httpx_for_a_plain_page()` --indirect_call--> `DiscoveryReport`  [INFERRED]
  tests/test_discover.py → src/parfum_finder/discover.py
- `test_a_hook_that_reads_nothing_is_named_as_the_culprit()` --indirect_call--> `ExtractionFailed`  [INFERRED]
  tests/test_engine.py → src/parfum_finder/engine.py
- `_NoRootParser` --uses--> `RawVariant`  [INFERRED]
  tests/test_engine.py → src/parfum_finder/extract.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Sites Implementing Variant Pattern C (embedded JSON)** — docs_discovery_report_venco_site, docs_discovery_report_decantall_site, docs_discovery_report_luxurydekant_site, docs_discovery_report_ruxangroup_site, architecture_md_variant_pattern_c [EXTRACTED 1.00]
- **İdeasoft Platform Sites and Endpoint** — docs_discovery_report_dekantparfum_site, docs_discovery_report_dekantdoktoru_site, docs_discovery_report_ideasoft_related_options_endpoint, platforms_readme_ideasoft_json [EXTRACTED 1.00]
- **discover Command Output Artifacts (profile + fixtures + CI validation)** — architecture_md_discover_flow, sites_readme_sites_dir, fixtures_readme_fixtures_dir, github_workflows_ci_validate_profiles_step, architecture_md_validate_command [INFERRED 0.85]

## Communities (73 total, 2 thin omitted)

### Community 0 - "TUI App & Screens"
Cohesion: 0.09
Nodes (100): One site's share of a split basket: what to buy there and what it costs.      `s, SplitLeg, The Textual-based terminal UI: search and basket screens., _app(), _basket(), _cells(), _days_ago(), _leg() (+92 more)

### Community 1 - "Site Profiles & Templates"
Cohesion: 0.06
Nodes (81): _check_hook_kinds(), deep_merge(), _load_json(), load_platform_template(), load_platform_templates(), load_site_hooks(), load_site_profile(), Any (+73 more)

### Community 2 - "Title Matcher"
Cohesion: 0.16
Nodes (22): parse_query(), Split one typed line, "Dior Sauvage EDP", into the three identity parts.      Th, Tests for parfum_finder.matcher.  The thing being defended here is not "does it, test_a_brand_the_shop_writes_out_in_full_does_not_cost_the_match(), test_a_clone_carries_the_identity_read_off_its_own_title(), test_a_clone_is_still_shown_because_it_may_be_worth_buying(), test_a_clone_whose_own_title_names_one_word_has_no_identity_to_store(), test_a_clones_own_name_is_scored_without_what_it_imitates() (+14 more)

### Community 3 - "HTTP/Browser Fetching"
Cohesion: 0.11
Nodes (19): browser_session(), PlaywrightNotInstalled, RuntimeError, Yield a fetcher that keeps one browser for every playwright page it reads., The "playwright" strategy was requested but cannot run at all.      Covers both, _fake_launch(), _FakeBrowser, _FakePage (+11 more)

### Community 4 - "Search/Basket Domain Models"
Cohesion: 0.08
Nodes (105): LogCaptureFixture, ProductCandidate, One hit on a search results page, before its product page is opened.      `raw_t, One decant size of one product, in the units the database stores.      Tenths of, A candidate together with the decant sizes its product page offers., What one site had to say about one query, and how much to trust it.      Four st, SearchHit, SiteResult (+97 more)

### Community 5 - "Search Engine per Site"
Cohesion: 0.12
Nodes (26): _check_empty_search(), ExtractionFailed, RuntimeError, A page answered but gave up nothing, where something was expected.      This is, Run one query against one site and read every hit's sizes.      Everything site-, Fail when a search yielded no rows off a page that plainly lists products., search_site(), FetchResult (+18 more)

### Community 6 - "Platform Discovery Flow"
Cohesion: 0.15
Nodes (59): PlatformChooser, _ask_chooser(), discover(), Put the question only when there is one, and hold the answer to it.      An answ, Measure the strategies a site needs, then read its JSON-LD with the winner., _attempt(), _fake_probe(), Any (+51 more)

### Community 7 - "CLI Entry Points"
Cohesion: 0.09
Nodes (55): CaptureFixture, ask_which_platform(), main(), Path, Scan every site for the perfumes named, store what came back, print it.      One, Ask at the terminal which of several matching templates to apply.      Asked whi, run_search(), A multi-site price and stock comparison tool for perfume decants.  Includes a sh (+47 more)

### Community 8 - "Architecture Rationale Docs"
Cohesion: 0.05
Nodes (53): basket Subset Enumeration + Local Improvement Algorithm, basket Optimizer (optimize function), Clone/Original Distinction (KLON ← <orijinal>), discover Discovery Flow, engine Concurrency Model (parallel sites, serial within site), Extraction Ladder (jsonld/endpoint/embedded/css), Fail-loud / status=suspect policy, hooks/<id>.py Escape Hatch (+45 more)

### Community 9 - "Search Engine Core"
Cohesion: 0.08
Nodes (47): HTMLParser, _check_variant_control(), _fetch_page(), _headers(), _is_excluded(), _paced_fetcher(), _page_offers_sizes(), _page_says_sold_out() (+39 more)

### Community 10 - "Basket Optimizer Core"
Cohesion: 0.05
Nodes (65): Collection, Prices, BasketItem, BasketReport, _ClimbState, optimize(), Basket scenario evaluation. A pure function, no network access, no sqlite.  Inpu, The cheapest basket split the search found. A heuristic, not a proof.      Every (+57 more)

### Community 11 - "Basket Store & Pricing"
Cohesion: 0.08
Nodes (48): add_basket_item(), Add a size of a perfume to the basket, and return the basket_item_id.      The p, Connection, Tests for parfum_finder.store: the timestamp helper and the schema.  The one har, An update aimed at a row that isn't there means the caller is out of sync., A snapshot pointing at a variant that doesn't exist has to be rejected.      SQL, Two snapshots written in the same second must resolve to the newer one.      A s, 5 ml at 125,00 TL is 25,00 TL per ml. Stored as kurus, ml as tenths. (+40 more)

### Community 12 - "JSON-LD Product Extraction"
Cohesion: 0.15
Nodes (30): extract_jsonld_products(), Read every JSON-LD Product declared on the page, in document order.      A block, _one_product_html(), Tests for parfum_finder.extract.  Every case here is a shape a real store actual, Wrap a JSON-LD product body in a page, for the one-field-at-a-time cases., test_a_broken_block_does_not_lose_the_valid_one(), test_availability_spellings_all_land_in_the_same_bucket(), test_boolean_values_are_never_read_as_price_or_text() (+22 more)

### Community 13 - "Basket TUI Screen"
Cohesion: 0.17
Nodes (20): fetch(), _fetch_curl_cffi(), _fetch_httpx(), FormData, Headers, Method, Strategy, Fetch one URL using exactly the given strategy.      `method`/`data` exist for t (+12 more)

### Community 14 - "Platform Schema"
Cohesion: 0.06
Nodes (31): any, defaults, fingerprint, additionalProperties, items, minItems, type, description (+23 more)

### Community 15 - "Product Extraction"
Cohesion: 0.10
Nodes (35): _as_str(), _build_offer(), _build_product(), _coerce_in_stock(), _collect_offers(), _collect_variants(), _css_variant(), JsonLdOffer (+27 more)

### Community 16 - "Schema Field Patterns"
Cohesion: 0.05
Nodes (39): css, embedded_json, endpoint, jsonld, format, pattern, type, pattern (+31 more)

### Community 17 - "Offline Profile Validation"
Cohesion: 0.13
Nodes (17): Check, _count_result_cards(), _first_result_url(), _no_results_check(), _probe_layer(), _probe_other_layers(), Any, Path (+9 more)

### Community 18 - "Playwright Errors"
Cohesion: 0.15
Nodes (21): _attempt(), _count_jsonld(), _count_product_objects(), _detect_platforms(), format_report(), _label_platform(), _one_line(), ProbeAttempt (+13 more)

### Community 19 - "Search TUI Screen"
Cohesion: 0.33
Nodes (10): Path, Attach the rotating file handler and return where it writes.      Safe to call m, setup_logging(), Path, The file logger's two promises: it writes to the file, and it stays silent.  Bot, _teardown(), test_an_error_lands_in_the_given_file(), test_setting_up_twice_does_not_double_the_lines() (+2 more)

### Community 20 - "Snapshot Writing"
Cohesion: 0.14
Nodes (15): _balanced_value(), _embedded_documents(), extract_endpoint_variants(), _loads_or_skip(), Any, Rung 2: read the variant list out of a platform's JSON response.      `document`, Yield every JSON document the page hides, in document order., Parse `text` as JSON, yielding nothing when it isn't JSON.      Pages are full o (+7 more)

### Community 21 - "Candidate Filtering"
Cohesion: 0.19
Nodes (27): format_report(), Check one site's profile against that site's saved fixtures.      Never raises f, Validate every site, or just the ones named.      Serial rather than concurrent:, Render the validations as the offline half of the report in APP_FLOW §6.      A, validate_all_offline(), validate_offline(), _corrupted_sites_dir(), _iso_days_ago() (+19 more)

### Community 22 - "Basket Site Scenarios"
Cohesion: 0.15
Nodes (20): _canonical(), _covers(), _ends_with(), _index_of(), _match_text(), _own_identity(), Perfume matching: brand and concentration are mandatory; fuzzy matching only app, What a clone's own title says the bottle is, in the shape a query has.      Buil (+12 more)

### Community 23 - "Price/Size Normalization"
Cohesion: 0.12
Nodes (25): _classify_single_separator(), format_ml(), format_price(), _parse_number(), parse_price(), parse_size_ml(), Decimal, Number parsing and formatting for prices and volumes, plus text folding.  This i (+17 more)

### Community 24 - "JSON Schema Primitives"
Cohesion: 0.11
Nodes (25): integer, null, string, properties, type, type, type, type (+17 more)

### Community 25 - "SQLite Store"
Cohesion: 0.22
Nodes (12): _close_browser(), _fetch_playwright(), _launch_browser(), PlaywrightNoResponse, Any, The fetch escalation ladder: one interface over httpx, curl_cffi, and playwright, Fetch one page in a browser that lives no longer than this call., Start playwright and a chromium, or say which half of the setup is missing. (+4 more)

### Community 26 - "Site Profile Fields"
Cohesion: 0.10
Nodes (20): base_url, discovered_at, extraction, id, needs_review, platform, search, shipping (+12 more)

### Community 27 - "Site Schema Validation Tests"
Cohesion: 0.19
Nodes (17): Draft202012Validator, _load_schema(), _platform_validator(), Any, Tests for schema/site.schema.json and schema/platform.schema.json.  These check, The third copy of the ladder is here, and nothing else would catch it drifting., _site_validator(), test_platform_schema_accepts_the_documented_example() (+9 more)

### Community 28 - "Variant Rule Fields"
Cohesion: 0.11
Nodes (19): exclude_keywords, field, max_size_ml, size_from, size_pattern, title, variant_label, exclusiveMinimum (+11 more)

### Community 29 - "Discovery CLI Reporting"
Cohesion: 0.09
Nodes (40): collect_prices(), DiscoveryReport, FieldConfidence, _flatten_defaults(), _format_choice(), _format_confidence(), _format_defaults(), _format_fingerprint() (+32 more)

### Community 30 - "Store Timestamp Tests"
Cohesion: 0.22
Nodes (6): Decimal, Row, One priced size, exactly as the table shows it and as a keypress needs it., The default order: typed order, product, site, size.          The typed order co, The order once a column has been picked: the site layer drops out.          Aski, _ResultRow

### Community 31 - "Live Profile Validation"
Cohesion: 0.16
Nodes (5): Changed, One perfume of a search, as typed and as parsed.      The index is the outermost, Empty the table for a new scan.          The columns are the same every time now, _Search, Submitted

### Community 32 - "Variant Extraction Fields"
Cohesion: 0.12
Nodes (16): attribute, script, type, additionalProperties, allOf, description, properties, type (+8 more)

### Community 33 - "_ResultRow"
Cohesion: 0.15
Nodes (27): Match, match_title(), PerfumeQuery, The perfume being looked for, split into its three identity parts.      `concent, One site title judged against the query.      `concentration` is what the title, Judge one site title against a query, or None if it is not that perfume.      No, test_a_brand_needs_all_of_its_words_not_one(), test_a_brand_only_query_matches_a_title_that_is_only_that_brand() (+19 more)

### Community 34 - "Fetch Strategy Probing"
Cohesion: 0.17
Nodes (13): _candidates_to_open(), CacheKey, CandidateFilter, Path, VariantsRead, Open one product page and read its sizes on the profile's layer.      A `cache`, Run every site against one query, all at once, and report each separately., Narrow the search results down to the pages worth a request.      The first one (+5 more)

### Community 35 - "Platform Field Mapping"
Cohesion: 0.18
Nodes (11): field_map, product_json, source, variants_path, required, additionalProperties, allOf, description (+3 more)

### Community 36 - "Shipping Config Schema"
Cohesion: 0.14
Nodes (14): free_shipping_threshold_kurus, shipping_cost_kurus, minimum, type, free_shipping_threshold_kurus, notes, shipping, shipping_cost_kurus (+6 more)

### Community 37 - "Discovery Report Model"
Cohesion: 0.27
Nodes (9): Run one site's profile against the real site.      Same contract as offline mode, validate_live(), _FakeSite, _fixture_site(), A stand-in for one live site, answering the search page then the rest.      Live, test_a_broken_layer_reports_which_other_layer_could_take_over(), test_a_working_profile_passes_against_a_site_that_still_answers(), test_zero_results_on_a_full_page_blames_the_result_selector() (+1 more)

### Community 38 - "TUI Confirm Dialog"
Cohesion: 0.17
Nodes (14): One priced size of one perfume on one site, ready to be written.      The perfum, Write a whole scan at once and return how many prices were recorded.      Every, SnapshotRow, write_snapshots(), The drop happens here so no caller can forget it.      Both the CLI and the scre, A slow site must not spread one reading across several timestamps.      Rows wri, The number reported is what landed in the history, not what was offered., Half a site's sizes updated is worse than none of them.      The basket compares (+6 more)

### Community 39 - "TUI App Shell"
Cohesion: 0.25
Nodes (5): Screen, ParfumFinderApp, Path, Root app: pushes the search screen on mount., SystemCommand

### Community 40 - "Fetch Backends"
Cohesion: 0.14
Nodes (14): curl_cffi, httpx, playwright, result_item, result_title, result_url, strategy, url_template (+6 more)

### Community 41 - "HTTP Request Schema"
Cohesion: 0.14
Nodes (14): GET, POST, properties, default, enum, type, type, type (+6 more)

### Community 42 - "Fixture Fetcher (Tests)"
Cohesion: 0.24
Nodes (6): BaseHTTPRequestHandler, _Handler, _playwright_usable(), Shared pytest fixtures.  A local HTTP server used by fetch/probe tests: real req, Whether the playwright rung can actually run here, binary included.      Checkin, server_url()

### Community 43 - "Validation Reporting"
Cohesion: 0.31
Nodes (9): _named_profile(), Any, The real fetcher, with a list of every URL it was asked for., A profile whose search page lists two houses' bottles, as shops do., test_a_listing_from_another_house_costs_no_product_request(), test_one_product_listed_under_two_searches_is_read_once(), test_two_shops_sharing_a_url_do_not_read_each_others_pages(), test_without_a_filter_every_listing_is_still_opened() (+1 more)

### Community 44 - "Decant Variant Rules"
Cohesion: 0.15
Nodes (18): _age_of(), live_query(), _path(), profile_age_days(), datetime, Profile staleness checks. Two modes: offline (against saved fixtures) and live (, A URL's path with no trailing slash, for comparing two spellings of one page., Every site that has a profile, sorted so reports read the same way twice. (+10 more)

### Community 45 - "Multi-Site Search Run"
Cohesion: 0.14
Nodes (20): extract_embedded_variants(), extract_jsonld_variants(), _flatten_jsonld(), Rung 1: read the page's JSON-LD as flat variant rows.      A product that declar, Turn one Product and everything under it into rows., Rung 3: read the JSON blob the page carries but does not display.      Two shape, Run one extraction layer over a product page's bytes., _rows_for_layer() (+12 more)

### Community 46 - "Offline Validation Fixtures"
Cohesion: 0.25
Nodes (8): type, additionalProperties, type, body, request_headers, additionalProperties, description, type

### Community 47 - "Basket Domain Logic"
Cohesion: 0.09
Nodes (49): Run one site and classify what came back instead of raising.      It is also whe, run_site(), _counting_fetcher(), _profile(), Exception, Tests for the profile-driven search in parfum_finder.engine.  What these defend, Answer each call with the next canned result, then repeat the last one., A minimal working profile, with the fields a case cares about swapped in. (+41 more)

### Community 48 - "._build_rows"
Cohesion: 0.29
Nodes (7): in_stock, price, size_raw, additionalProperties, required, type, field_map

### Community 49 - "test_engine.py"
Cohesion: 0.27
Nodes (13): apply_variant_rules(), Turn raw size rows into decant variants, dropping what is not a decant.      Thr, _row(), test_a_keyword_in_the_size_label_excludes_the_row_too(), test_a_literal_zero_price_reads_as_no_price_not_a_free_perfume(), test_a_size_at_the_threshold_is_a_bottle_whatever_it_calls_itself(), test_a_size_that_cannot_be_read_is_dropped(), test_an_uppercase_turkish_keyword_still_matches() (+5 more)

### Community 50 - "Profile Age Checks"
Cohesion: 0.16
Nodes (13): _choose_strategy(), _match_platforms(), Any, Path, Strategy, _qualifies(), The strategy the trials actually ran with., Pick the cheapest strategy that came back with real content, or None.      probe (+5 more)

### Community 51 - "._refresh_table"
Cohesion: 0.14
Nodes (5): HeaderSelected, RowSelected, The initial screen: search bar, streaming results table, notices, footer., What each site charges for the product a block is about.          One entry per, SearchScreen

### Community 52 - "._cells"
Cohesion: 0.50
Nodes (4): _collect_products(), _has_type(), Walk a parsed JSON-LD block and append every Product found, depth first.      De, Whether a node's "@type" names `name`, as a string or inside a list.      Substr

### Community 53 - "conftest.py"
Cohesion: 0.13
Nodes (23): _Change, _perfume_id(), price_history(), _product_id(), Connection, Row, SQLite persistence: an append-only price history.  Tables: sites, perfumes, prod, Write one scan's reading of one size, and return its snapshot id.      The perfu (+15 more)

### Community 54 - "Endpoint Schema Fields"
Cohesion: 0.22
Nodes (9): result_item, result_title, result_url, url_template, search, additionalProperties, description, required (+1 more)

### Community 55 - "tui/__init__.py"
Cohesion: 0.12
Nodes (18): Any, Connection, Command-line entry point.  Subcommands will be added incrementally as the projec, Scan every perfume against every site and print each site as it lands.      One, Write one site's rows in a transaction of its own.      Per site rather than per, One line per site: which site, how it went, and what it said.      The site id i, _report_line(), _scan_all() (+10 more)

### Community 56 - "Request Schema Fields"
Cohesion: 0.31
Nodes (11): Path, Give the test profile's site id a hook file. The id is what binds them., test_a_before_search_that_returns_no_query_is_refused(), test_a_broken_hook_is_an_error_not_a_silent_empty(), test_a_hook_that_reads_nothing_is_named_as_the_culprit(), test_a_site_with_no_hook_file_is_driven_by_its_profile_alone(), test_after_search_can_drop_a_result_the_selectors_could_not(), test_before_search_rewrites_the_query_that_is_actually_sent() (+3 more)

### Community 57 - "_FixtureFetcher"
Cohesion: 0.26
Nodes (7): _FixtureFetcher, FormData, Headers, Method, Strategy, Serves one site's saved capture in place of the network.      Only three kinds o, The one real result card that led to the captured product page.          Cut out

### Community 58 - "ComposeResult"
Cohesion: 0.14
Nodes (20): basket_lines(), basket_prices(), basket_sites(), BasketLine, BasketPrice, BasketSite, One row of the basket: a size of a perfume, with the identity spelled out., One site's latest price for one basket line, only when it has one.      Rows wit (+12 more)

### Community 59 - "_named_profile"
Cohesion: 0.29
Nodes (7): items, type, type, items, type, exclude_keywords, needs_review

### Community 60 - "_NoRootParser"
Cohesion: 0.21
Nodes (7): _listing_filter(), Any, CacheKey, CandidateFilter, VariantsRead, Decide, from a search result's own title, whether to open its page., Scan one site for every perfume of this search, one at a time.          Serial i

### Community 61 - "Price History"
Cohesion: 0.22
Nodes (9): product_label(), Reduce a site's own title to the product it is about, spelled one way.      What, Split a title into what the bottle is and what it says it imitates.      The sec, _split_clone_reference(), test_a_clone_is_labelled_by_the_bottle_it_is_and_not_what_it_imitates(), test_a_longer_named_bottle_does_not_join_the_shorter_ones_block(), test_a_title_with_no_product_words_left_has_no_label(), test_every_shops_spelling_of_one_bottle_lands_in_one_block() (+1 more)

### Community 62 - "SiteValidation"
Cohesion: 0.22
Nodes (8): _age_line(), format_live_report(), Every check run against one site's profile, in the order they ran.      Checks s, Whether the profile is old enough to be worth re-discovering., The age note for one site, or None when its age is unremarkable.      A profile, Render offline and live results side by side, as APP_FLOW §6 shows them.      Bo, SiteValidation, test_the_live_report_names_the_edit_that_would_repair_the_profile()

### Community 63 - "enum"
Cohesion: 0.25
Nodes (8): Split one typed line into the perfumes it asks for, on " - ".      The separator, split_queries(), test_a_hyphen_inside_a_brand_name_does_not_split_the_search(), test_a_line_naming_three_perfumes_is_read_as_three_searches(), test_a_piece_that_names_no_perfume_survives_to_be_complained_about(), test_a_stray_separator_is_not_worth_failing_over(), test_one_perfume_is_still_one_search(), test_the_same_perfume_typed_twice_is_scanned_once()

### Community 64 - ".__call__"
Cohesion: 0.31
Nodes (7): _DeadSite, FormData, Headers, Method, Strategy, A host that cannot be reached at all., test_an_unreachable_site_is_not_reported_as_a_broken_profile()

### Community 65 - "rate_limit_ms"
Cohesion: 0.33
Nodes (7): connect(), Path, Open the price database, creating the schema if it isn't there yet.      Foreign, conn(), Path, Reopening an existing database must not wipe or re-raise on its schema., test_connect_is_idempotent_on_an_existing_database()

### Community 66 - "format_age"
Cohesion: 0.33
Nodes (6): _listing_filter(), CandidateFilter, Decide, from a search result's own title, whether to open its page., Whether a search result's own listing text is worth opening the page for.      J, title_could_match(), test_a_doubtful_listing_is_still_opened_because_the_page_decides()

### Community 67 - "_resolve_platform"
Cohesion: 0.50
Nodes (3): The template this site's profile would be based on, if any., Which of the matching templates gets applied, or None for none of them.      One, _resolve_platform()

### Community 68 - "extract_css_variants"
Cohesion: 0.50
Nodes (4): extract_css_variants(), Rung 4: read the rendered markup with selectors. Last resort.      `config["vari, test_css_reads_one_row_per_container(), test_css_without_a_container_reads_the_page_as_one_variant()

### Community 71 - "basket_prices"
Cohesion: 0.17
Nodes (21): One call has to leave a row the search table can read straight off.      The cal, The old price has to survive, and it must not become a second variant.      Appe, first_seen is what says how long a shop has carried a size., The title and URL are information, not identity.      A shop that rewords a list, EDT and EDP are different products at different prices.      Folding them into o, A sold-out size often shows no price at all, and 0 would mean free.      Writing, The column is 0/1, so the tri-state has to land somewhere on purpose.      Unkno, raw_title is the audit trail for a wrong match, so it cannot be blank.      A ro (+13 more)

### Community 72 - "ComposeResult"
Cohesion: 0.14
Nodes (7): Pressed, ComposeResult, ConfirmScreen, ComposeResult, Path, Asks before a low-confidence match is written to the basket.      The two answer, Static

## Knowledge Gaps
- **154 isolated node(s):** `parfum-finder`, `$schema`, `$id`, `title`, `description` (+149 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `SiteResult` connect `Search/Basket Domain Models` to `TUI App & Screens`, `Fetch Strategy Probing`, `HTTP/Browser Fetching`, `Search Engine per Site`, `TUI Confirm Dialog`, `ComposeResult`, `Search Engine Core`, `Basket Optimizer Core`, `Basket Domain Logic`, `._refresh_table`, `conftest.py`, `tui/__init__.py`, `ComposeResult`, `_NoRootParser`, `Store Timestamp Tests`, `Live Profile Validation`?**
  _High betweenness centrality (0.051) - this node is a cross-community bridge._
- **Why does `BasketScreen` connect `Basket Optimizer Core` to `TUI App & Screens`, `_ResultRow`, `Search/Basket Domain Models`, `TUI Confirm Dialog`, `ComposeResult`, `._refresh_table`, `conftest.py`, `tui/__init__.py`, `Price/Size Normalization`, `ComposeResult`, `Store Timestamp Tests`, `Live Profile Validation`?**
  _High betweenness centrality (0.035) - this node is a cross-community bridge._
- **Why does `PerfumeQuery` connect `_ResultRow` to `format_age`, `Title Matcher`, `Search/Basket Domain Models`, `TUI Confirm Dialog`, `ComposeResult`, `Basket Optimizer Core`, `._refresh_table`, `conftest.py`, `Basket Site Scenarios`, `tui/__init__.py`, `ComposeResult`, `_NoRootParser`, `Store Timestamp Tests`, `Live Profile Validation`?**
  _High betweenness centrality (0.032) - this node is a cross-community bridge._
- **Are the 7 inferred relationships involving `SearchScreen` (e.g. with `ParfumFinderApp` and `SiteResult`) actually correct?**
  _`SearchScreen` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Are the 16 inferred relationships involving `SiteResult` (e.g. with `RawVariant` and `Fetcher`) actually correct?**
  _`SiteResult` has 16 INFERRED edges - model-reasoned connections that need verification._
- **What connects `parfum-finder`, `$schema`, `$id` to the rest of the system?**
  _154 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `TUI App & Screens` be split into smaller, more focused modules?**
  _Cohesion score 0.09337992622791691 - nodes in this community are weakly interconnected._