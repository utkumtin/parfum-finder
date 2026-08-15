# Graph Report - parfum-finder  (2026-08-14)

## Corpus Check
- 70 files · ~263,094 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1868 nodes · 4937 edges · 85 communities (72 shown, 13 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 173 edges (avg confidence: 0.59)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `02d948e5`
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
- _trial
- TUI Confirm Dialog
- TUI App Shell
- Fetch Backends
- HTTP Request Schema
- Fixture Fetcher (Tests)
- FieldConfidence
- Decant Variant Rules
- _ResultRow
- Offline Validation Fixtures
- JsonLdProduct
- ._build_rows
- _RecordingFetcher
- Profile Age Checks
- ._refresh_table
- FetchResult
- conftest.py
- Endpoint Schema Fields
- apply_variant_rules
- Request Schema Fields
- _FixtureFetcher
- setup_logging
- _named_profile
- ._scan
- single_site_scenarios
- snapshot_rows
- CandidateFilter
- validate_live
- _named_profile
- .__call__
- test_cached_prices_is_empty_for_a_perfume_nobody_scanned
- field_map
- Variant Pattern A
- Project Root
- exclude_keywords
- ComposeResult
- Static
- format_age
- _listing_filter
- CacheKey
- CandidateFilter
- ComposeResult
- Decimal
- Protocol
- VariantsRead
- LogCaptureFixture
- MonkeyPatch
- Runner

## God Nodes (most connected - your core abstractions)
1. `search_site()` - 66 edges
2. `SearchScreen` - 62 edges
3. `_profile()` - 58 edges
4. `discover()` - 56 edges
5. `PerfumeQuery` - 52 edges
6. `_write_profile()` - 51 edges
7. `_app()` - 49 edges
8. `_submit_query()` - 49 edges
9. `match_title()` - 47 edges
10. `BasketScreen` - 46 edges

## Surprising Connections (you probably didn't know these)
- `Shipping Non-linearity Rationale (why cheapest-per-item is wrong)` --semantically_similar_to--> `sites/ Site Profile Directory`  [INFERRED] [semantically similar]
  ARCHITECTURE.md → sites/README.md
- `Variant Pattern B (dropdown + AJAX price)` --semantically_similar_to--> `Variant Selector Detector Fix (WooCommerce 'variation' vs 'variant')`  [INFERRED] [semantically similar]
  ARCHITECTURE.md → docs/discovery-report.md
- `test_the_low_confidence_dialog_can_be_answered_with_the_keyboard_alone()` --indirect_call--> `ConfirmScreen`  [INFERRED]
  tests/test_tui.py → src/parfum_finder/tui/search_screen.py
- `test_the_low_confidence_dialog_shows_the_keys_it_answers_to()` --indirect_call--> `ConfirmScreen`  [INFERRED]
  tests/test_tui.py → src/parfum_finder/tui/search_screen.py
- `test_write_sheet_asks_confirmation_for_a_stale_cached_price()` --indirect_call--> `ConfirmScreen`  [INFERRED]
  tests/test_tui.py → src/parfum_finder/tui/search_screen.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Sites Implementing Variant Pattern C (embedded JSON)** — docs_discovery_report_venco_site, docs_discovery_report_decantall_site, docs_discovery_report_luxurydekant_site, docs_discovery_report_ruxangroup_site, architecture_md_variant_pattern_c [EXTRACTED 1.00]
- **İdeasoft Platform Sites and Endpoint** — docs_discovery_report_dekantparfum_site, docs_discovery_report_dekantdoktoru_site, docs_discovery_report_ideasoft_related_options_endpoint, platforms_readme_ideasoft_json [EXTRACTED 1.00]
- **discover Command Output Artifacts (profile + fixtures + CI validation)** — architecture_md_discover_flow, sites_readme_sites_dir, fixtures_readme_fixtures_dir, github_workflows_ci_validate_profiles_step, architecture_md_validate_command [INFERRED 0.85]

## Communities (85 total, 13 thin omitted)

### Community 0 - "TUI App & Screens"
Cohesion: 0.10
Nodes (98): The Textual-based terminal UI: search and basket screens., _app(), _basket(), _cells(), _days_ago(), _leg(), _ok(), _open_basket() (+90 more)

### Community 1 - "Site Profiles & Templates"
Cohesion: 0.06
Nodes (84): _check_hook_kinds(), deep_merge(), _load_json(), load_platform_template(), load_platform_templates(), load_site_hooks(), load_site_profile(), Any (+76 more)

### Community 2 - "Title Matcher"
Cohesion: 0.15
Nodes (7): _Change, BasketScreen, Any, The basket: the list on top, one scenario per site underneath., The three inputs basket.py's pure functions score: items, prices, shipping., _remove(), _set_qty()

### Community 3 - "HTTP/Browser Fetching"
Cohesion: 0.12
Nodes (30): browser_session(), fetch(), PlaywrightNotInstalled, Fetch one URL using exactly the given strategy.      `method`/`data` exist for t, Yield a fetcher that keeps one browser for every playwright page it reads., The "playwright" strategy was requested but cannot run at all.      Covers both, test_the_no_results_page_would_otherwise_read_as_suspect(), _fake_launch() (+22 more)

### Community 4 - "Search/Basket Domain Models"
Cohesion: 0.08
Nodes (114): LogCaptureFixture, MonkeyPatch, ParfumFinderApp, Runner, _app(), _basket_count(), _counting_runner(), _days_ago() (+106 more)

### Community 5 - "Search Engine per Site"
Cohesion: 0.15
Nodes (20): _close_browser(), _fetch_curl_cffi(), _fetch_httpx(), _fetch_playwright(), _launch_browser(), PlaywrightNoResponse, Any, FormData (+12 more)

### Community 6 - "Platform Discovery Flow"
Cohesion: 0.15
Nodes (59): PlatformChooser, _ask_chooser(), discover(), Put the question only when there is one, and hold the answer to it.      An answ, Measure the strategies a site needs, then read its JSON-LD with the winner., _attempt(), _fake_probe(), Any (+51 more)

### Community 7 - "CLI Entry Points"
Cohesion: 0.07
Nodes (65): CaptureFixture, ask_which_platform(), _listing_filter(), main(), Any, CandidateFilter, Connection, Path (+57 more)

### Community 8 - "Architecture Rationale Docs"
Cohesion: 0.05
Nodes (53): basket Subset Enumeration + Local Improvement Algorithm, basket Optimizer (optimize function), Clone/Original Distinction (KLON ← <orijinal>), discover Discovery Flow, engine Concurrency Model (parallel sites, serial within site), Extraction Ladder (jsonld/endpoint/embedded/css), Fail-loud / status=suspect policy, hooks/<id>.py Escape Hatch (+45 more)

### Community 9 - "Search Engine Core"
Cohesion: 0.08
Nodes (58): HTMLParser, _check_empty_search(), _check_variant_control(), _fetch_page(), _headers(), _paced_fetcher(), _page_offers_sizes(), _page_says_sold_out() (+50 more)

### Community 10 - "Basket Optimizer Core"
Cohesion: 0.14
Nodes (38): Collection, Prices, BasketItem, optimize(), Score one site against the basket, or against a subset of it.      `item_ids` is, Score every enabled site against the whole basket and sort the results.      Sit, Search for the cheapest way to split the basket across several sites.      Retur, One line of the shopping list: a basket row, not a unit count.      `item_id` is (+30 more)

### Community 11 - "Basket Store & Pricing"
Cohesion: 0.09
Nodes (40): add_basket_item(), basket_lines(), basket_prices(), Add a size of a perfume to the basket, and return the basket_item_id.      The p, Return every basket line, oldest add first.      Ordered by added_at with basket, Return the basket price matrix: one row per (line, site) that has a price., Connection, A stale reading must never outrank the one taken after it.      latest_prices al (+32 more)

### Community 12 - "JSON-LD Product Extraction"
Cohesion: 0.13
Nodes (32): extract_jsonld_products(), Read every JSON-LD Product declared on the page, in document order.      A block, _one_product_html(), Tests for parfum_finder.extract.  Every case here is a shape a real store actual, Wrap a JSON-LD product body in a page, for the one-field-at-a-time cases., test_a_broken_block_does_not_lose_the_valid_one(), test_availability_spellings_all_land_in_the_same_bucket(), test_boolean_values_are_never_read_as_price_or_text() (+24 more)

### Community 13 - "Basket TUI Screen"
Cohesion: 0.29
Nodes (7): price_history(), Row, Return one variant's past readings, newest first, capped at limit.      Empty fo, The trend panel reads row 0 as the latest reading, so order is the point.      A, No history yet is a normal state for a variant, not an error to raise on., test_price_history_is_empty_for_an_unknown_variant(), test_price_history_is_newest_first_and_capped_at_limit()

### Community 14 - "Platform Schema"
Cohesion: 0.06
Nodes (31): any, defaults, fingerprint, additionalProperties, items, minItems, type, description (+23 more)

### Community 15 - "Product Extraction"
Cohesion: 0.11
Nodes (30): _as_str(), _build_offer(), _build_product(), _coerce_in_stock(), _collect_offers(), _collect_products(), _collect_variants(), _css_variant() (+22 more)

### Community 16 - "Schema Field Patterns"
Cohesion: 0.06
Nodes (33): format, pattern, type, pattern, type, default, type, pattern (+25 more)

### Community 17 - "Offline Profile Validation"
Cohesion: 0.09
Nodes (49): Run one site and classify what came back instead of raising.      It is also whe, run_site(), _counting_fetcher(), _profile(), Exception, Tests for the profile-driven search in parfum_finder.engine.  What these defend, Answer each call with the next canned result, then repeat the last one., A minimal working profile, with the fields a case cares about swapped in. (+41 more)

### Community 18 - "Playwright Errors"
Cohesion: 0.15
Nodes (21): _attempt(), _count_jsonld(), _count_product_objects(), _detect_platforms(), format_report(), _label_platform(), _one_line(), ProbeAttempt (+13 more)

### Community 19 - "Search TUI Screen"
Cohesion: 0.08
Nodes (41): find_header_columns(), find_match(), open_worksheet(), Any, Exception, Path, Protocol, Writing a search result onto the user's own Google Sheets wishlist.  The wishlis (+33 more)

### Community 20 - "Snapshot Writing"
Cohesion: 0.10
Nodes (28): One site's share of a split basket: what to buy there and what it costs.      `s, What it would cost to buy some or all of the basket from one site.      `covered, SiteScenario, SplitLeg, format_price(), Format a price for display (comma-thousands, dot-decimal).      Decimal('1250'), BasketLine, BasketPrice (+20 more)

### Community 21 - "Candidate Filtering"
Cohesion: 0.15
Nodes (18): extract_embedded_variants(), extract_jsonld_variants(), _flatten_jsonld(), Rung 1: read the page's JSON-LD as flat variant rows.      A product that declar, Turn one Product and everything under it into rows., Rung 3: read the JSON blob the page carries but does not display.      Two shape, _fixture(), Read a captured product page. (+10 more)

### Community 22 - "Basket Site Scenarios"
Cohesion: 0.21
Nodes (15): probe(), Fetch `url` with every strategy and report diagnostics for each.      timeout_s, MonkeyPatch, Tests for parfum_finder.probe.  probe() always tries all three strategies -- the, test_probe_counts_jsonld_product_and_platform_signature(), test_probe_counts_product_across_jsonld_root_shapes(), test_probe_counts_product_markup_without_any_jsonld(), test_probe_counts_products_nested_below_the_top_level() (+7 more)

### Community 23 - "Price/Size Normalization"
Cohesion: 0.17
Nodes (19): _classify_single_separator(), format_ml(), _parse_number(), parse_price(), parse_size_ml(), Decimal, Number parsing and formatting for prices and volumes, plus text folding.  This i, Decide whether a lone separator marks a fraction or a thousands group.      Retu (+11 more)

### Community 24 - "JSON Schema Primitives"
Cohesion: 0.11
Nodes (25): integer, null, string, properties, type, type, type, type (+17 more)

### Community 25 - "SQLite Store"
Cohesion: 0.26
Nodes (7): _FixtureFetcher, FormData, Headers, Method, Strategy, Serves one site's saved capture in place of the network.      Only three kinds o, The one real result card that led to the captured product page.          Cut out

### Community 26 - "Site Profile Fields"
Cohesion: 0.10
Nodes (20): base_url, discovered_at, extraction, id, needs_review, platform, search, shipping (+12 more)

### Community 27 - "Site Schema Validation Tests"
Cohesion: 0.19
Nodes (17): Draft202012Validator, _load_schema(), _platform_validator(), Any, Tests for schema/site.schema.json and schema/platform.schema.json.  These check, The third copy of the ladder is here, and nothing else would catch it drifting., _site_validator(), test_platform_schema_accepts_the_documented_example() (+9 more)

### Community 28 - "Variant Rule Fields"
Cohesion: 0.11
Nodes (18): field, title, variant_label, items, type, type, exclusiveMinimum, type (+10 more)

### Community 29 - "Discovery CLI Reporting"
Cohesion: 0.15
Nodes (27): Match, match_title(), PerfumeQuery, The perfume being looked for, split into its three identity parts.      `concent, One site title judged against the query.      `concentration` is what the title, Judge one site title against a query, or None if it is not that perfume.      No, test_a_brand_needs_all_of_its_words_not_one(), test_a_brand_only_query_matches_a_title_that_is_only_that_brand() (+19 more)

### Community 30 - "Store Timestamp Tests"
Cohesion: 0.14
Nodes (15): _balanced_value(), _embedded_documents(), extract_endpoint_variants(), _loads_or_skip(), Any, Rung 2: read the variant list out of a platform's JSON response.      `document`, Yield every JSON document the page hides, in document order., Parse `text` as JSON, yielding nothing when it isn't JSON.      Pages are full o (+7 more)

### Community 31 - "Live Profile Validation"
Cohesion: 0.10
Nodes (29): _canonical(), _covers(), _ends_with(), _index_of(), _match_text(), _own_identity(), product_label(), Perfume matching: brand and concentration are mandatory; fuzzy matching only app (+21 more)

### Community 32 - "Variant Extraction Fields"
Cohesion: 0.11
Nodes (18): attribute, in_stock, price, script, size_raw, type, properties, additionalProperties (+10 more)

### Community 33 - "_ResultRow"
Cohesion: 0.10
Nodes (35): parse_query(), Split one typed line into the perfumes it asks for, on " - ".      The separator, Split one typed line, "Dior Sauvage EDP", into the three identity parts.      Th, Whether a search result's own listing text is worth opening the page for.      J, split_queries(), title_could_match(), Tests for parfum_finder.matcher.  The thing being defended here is not "does it, test_a_brand_the_shop_writes_out_in_full_does_not_cost_the_match() (+27 more)

### Community 34 - "Fetch Strategy Probing"
Cohesion: 0.17
Nodes (23): ExtractionFailed, RuntimeError, A page answered but gave up nothing, where something was expected.      This is, Run one query against one site and read every hit's sizes.      Everything site-, search_site(), Path, Give the test profile's site id a hook file. The id is what binds them., test_a_before_search_that_returns_no_query_is_refused() (+15 more)

### Community 35 - "Platform Field Mapping"
Cohesion: 0.12
Nodes (16): field_map, product_json, source, variants_path, additionalProperties, allOf, description, required (+8 more)

### Community 36 - "Shipping Config Schema"
Cohesion: 0.14
Nodes (14): free_shipping_threshold_kurus, shipping_cost_kurus, minimum, type, free_shipping_threshold_kurus, notes, shipping, shipping_cost_kurus (+6 more)

### Community 37 - "_trial"
Cohesion: 0.19
Nodes (3): Changed, PerfumeQuery, What each site charges for the product a block is about.          One entry per

### Community 38 - "TUI Confirm Dialog"
Cohesion: 0.10
Nodes (35): One priced size of one perfume on one site, ready to be written.      The perfum, Write a whole scan at once and return how many prices were recorded.      Every, SnapshotRow, write_snapshots(), The drop happens here so no caller can forget it.      Both the CLI and the scre, One call has to leave a row the search table can read straight off.      The cal, The old price has to survive, and it must not become a second variant.      Appe, first_seen is what says how long a shop has carried a size. (+27 more)

### Community 39 - "TUI App Shell"
Cohesion: 0.25
Nodes (7): _age_line(), format_live_report(), Every check run against one site's profile, in the order they ran.      Checks s, Whether the profile is old enough to be worth re-discovering., The age note for one site, or None when its age is unremarkable.      A profile, Render offline and live results side by side, as APP_FLOW §6 shows them.      Bo, SiteValidation

### Community 40 - "Fetch Backends"
Cohesion: 0.14
Nodes (14): curl_cffi, httpx, playwright, result_item, result_title, result_url, strategy, url_template (+6 more)

### Community 41 - "HTTP Request Schema"
Cohesion: 0.14
Nodes (14): GET, POST, properties, default, enum, type, type, type (+6 more)

### Community 42 - "Fixture Fetcher (Tests)"
Cohesion: 0.14
Nodes (7): ComposeResult, Pressed, ComposeResult, ConfirmScreen, Path, Asks before a low-confidence match is written to the basket.      The two answer, Static

### Community 44 - "Decant Variant Rules"
Cohesion: 0.15
Nodes (18): _age_of(), live_query(), _path(), profile_age_days(), datetime, Profile staleness checks. Two modes: offline (against saved fixtures) and live (, A URL's path with no trailing slash, for comparing two spellings of one page., Every site that has a profile, sorted so reports read the same way twice. (+10 more)

### Community 45 - "_ResultRow"
Cohesion: 0.18
Nodes (6): Decimal, Row, One priced size, exactly as the table shows it and as a keypress needs it., The default order: typed order, product, site, size.          The typed order co, The order once a column has been picked: the site layer drops out.          Aski, _ResultRow

### Community 46 - "Offline Validation Fixtures"
Cohesion: 0.25
Nodes (8): type, additionalProperties, type, body, request_headers, additionalProperties, description, type

### Community 47 - "JsonLdProduct"
Cohesion: 0.17
Nodes (12): cached_prices(), CachedPrice, One stored price for one size of one perfume on one site.      What the results, Return the latest stored price of every size of this perfume, per site.      Bra, The search screen's second search must be answered with today's numbers.      Tw, A search that named no concentration is asking for all of them.      "" means "a, A price nobody will scan again may not be offered as a result.      Refreshing i, Nothing on record is the state before a first search, not an error.      The sea (+4 more)

### Community 48 - "._build_rows"
Cohesion: 0.08
Nodes (46): _choose_strategy(), collect_prices(), DiscoveryReport, FieldConfidence, _flatten_defaults(), _format_choice(), _format_confidence(), _format_defaults() (+38 more)

### Community 49 - "_RecordingFetcher"
Cohesion: 0.12
Nodes (19): Check, _count_result_cards(), _first_result_url(), _no_results_check(), _probe_layer(), _probe_other_layers(), Any, Path (+11 more)

### Community 50 - "Profile Age Checks"
Cohesion: 0.17
Nodes (25): format_report(), Check one site's profile against that site's saved fixtures.      Never raises f, Validate every site, or just the ones named.      Serial rather than concurrent:, Render the validations as the offline half of the report in APP_FLOW §6.      A, validate_all_offline(), validate_offline(), _corrupted_sites_dir(), _iso_days_ago() (+17 more)

### Community 51 - "._refresh_table"
Cohesion: 0.12
Nodes (5): HeaderSelected, RowSelected, The initial screen: search bar, streaming results table, notices, footer., SearchScreen, Worksheet

### Community 52 - "FetchResult"
Cohesion: 0.25
Nodes (8): exclude_keywords, max_size_ml, size_from, size_pattern, variant_rules, additionalProperties, required, type

### Community 53 - "conftest.py"
Cohesion: 0.20
Nodes (18): _perfume_id(), _product_id(), Connection, SQLite persistence: an append-only price history.  Tables: sites, perfumes, prod, Write one scan's reading of one size, and return its snapshot id.      The perfu, Do the writing, without opening a transaction of its own., Delete one basket line, and say whether there was one to delete.      Returns Fa, Set a basket line's quantity, clamped to at least 1, and return it.      The tab (+10 more)

### Community 54 - "Endpoint Schema Fields"
Cohesion: 0.22
Nodes (9): result_item, result_title, result_url, url_template, search, additionalProperties, description, required (+1 more)

### Community 55 - "apply_variant_rules"
Cohesion: 0.14
Nodes (22): apply_variant_rules(), _is_excluded(), Decimal, Turn raw size rows into decant variants, dropping what is not a decant.      Thr, Read one row's volume in millilitres, or None if the text does not say.      "fi, Whether this row is something other than a decant.      The size threshold is in, Convert a price in lira to whole kuruş.      Integers all the way, never a float, _read_size_ml() (+14 more)

### Community 56 - "Request Schema Fields"
Cohesion: 0.24
Nodes (6): BaseHTTPRequestHandler, _Handler, _playwright_usable(), Shared pytest fixtures.  A local HTTP server used by fetch/probe tests: real req, Whether the playwright rung can actually run here, binary included.      Checkin, server_url()

### Community 57 - "_FixtureFetcher"
Cohesion: 0.17
Nodes (10): CacheKey, CandidateFilter, Fetcher, SnapshotRow, _listing_filter(), Any, SiteResult, Decide, from a search result's own title, whether to open its page. (+2 more)

### Community 58 - "setup_logging"
Cohesion: 0.29
Nodes (7): _NoRootParser, MonkeyPatch, Record every delay the engine asks for instead of serving it.      Waiting for r, Stands in for HTMLParser when a page's markup cannot be read at all.      select, slept(), test_a_product_page_with_no_root_names_its_body_size(), test_a_search_page_with_no_root_names_its_body_size()

### Community 59 - "_named_profile"
Cohesion: 0.31
Nodes (9): _parse_selector(), Node, Run one "<css>::text" / "<css>::attr(name)" selector inside a node.      The nod, Run one "<css>::text" / "<css>::attr(name)" selector, reading every match., Split a "<css>::text" / "<css>::attr(name)" selector into its two parts., Read the attribute or text of one already-selected node, or None., _read_selected(), select_all() (+1 more)

### Community 60 - "._scan"
Cohesion: 0.16
Nodes (7): One perfume of a search, as typed and as parsed.      The index is the outermost, Close out a submit that named no perfume anyone could look for., Show what storage already knows, then go to the shops for the rest.          `ca, Say which perfumes came off the record instead of off the shops.          Withou, Empty the table for a new scan.          The columns are the same every time now, _Search, Submitted

### Community 61 - "single_site_scenarios"
Cohesion: 0.16
Nodes (13): BasketReport, _ClimbState, Basket scenario evaluation. A pure function, no network access, no sqlite.  Inpu, The cheapest basket split the search found. A heuristic, not a proof.      Every, The hill-climb's working assignment plus the running per-site figures.      `sub, Every site's single-site scenario, split by whether it covers everything.      A, SplitPlan, _heading() (+5 more)

### Community 62 - "snapshot_rows"
Cohesion: 0.10
Nodes (25): now_iso(), SiteResult, Return the current UTC time as 'YYYY-MM-DDTHH:MM:SSZ'.      Every timestamp writ, Turn one site's hits into the rows write_snapshots is ready to store.      Share, snapshot_rows(), conn(), Path, Tests for parfum_finder.store: the timestamp helper and the schema.  The one har (+17 more)

### Community 63 - "CandidateFilter"
Cohesion: 0.38
Nodes (7): _match_platforms(), Any, Path, Every template with at least one of its markers somewhere in the page.      Case, Write one page and return where it landed plus its digest.      Saved as UTF-8 w, _save_fixture(), _trial()

### Community 64 - "validate_live"
Cohesion: 0.22
Nodes (15): Run one site's profile against the real site.      Same contract as offline mode, validate_live(), _DeadSite, _FakeSite, _fixture_site(), M5's own criterion: when a profile stops agreeing with its site's real markup, o, A stand-in for one live site, answering the search page then the rest.      Live, A host that cannot be reached at all. (+7 more)

### Community 65 - "_named_profile"
Cohesion: 0.31
Nodes (9): _named_profile(), Any, The real fetcher, with a list of every URL it was asked for., A profile whose search page lists two houses' bottles, as shops do., test_a_listing_from_another_house_costs_no_product_request(), test_one_product_listed_under_two_searches_is_read_once(), test_two_shops_sharing_a_url_do_not_read_each_others_pages(), test_without_a_filter_every_listing_is_still_opened() (+1 more)

### Community 66 - ".__call__"
Cohesion: 0.53
Nodes (4): FormData, Headers, Method, Strategy

### Community 67 - "test_cached_prices_is_empty_for_a_perfume_nobody_scanned"
Cohesion: 0.22
Nodes (9): _candidates_to_open(), CacheKey, CandidateFilter, Path, VariantsRead, Run every site against one query, all at once, and report each separately., Narrow the search results down to the pages worth a request.      The first one, run_sites() (+1 more)

### Community 68 - "field_map"
Cohesion: 0.33
Nodes (4): CachedPrice, _cached_result_row(), Turn one stored price back into the row the table shows.      Everything the tab, Rebuild the table's rows for every searched perfume already on record.

### Community 71 - "exclude_keywords"
Cohesion: 0.33
Nodes (6): css, embedded_json, endpoint, jsonld, enum, extraction

### Community 72 - "ComposeResult"
Cohesion: 0.14
Nodes (11): Protocol, Screen, ParfumFinderApp, Path, The Textual App root. Handles screen navigation and is the app's default entry p, Root app: pushes the search screen on mount., Path, The search screen: a progress bar while scanning, one grouped table after.  A pe (+3 more)

### Community 73 - "Static"
Cohesion: 0.33
Nodes (6): basket_sites(), Return every enabled site, for the basket screen's fixed set of columns.      So, A disabled site loses its basket column, but an enabled quiet one keeps one., NULL means the site has no free shipping tier at all, not a threshold of zero., test_basket_sites_omits_a_disabled_site_and_keeps_one_that_prices_nothing(), test_basket_sites_preserves_a_null_free_shipping_threshold_as_none()

### Community 74 - "format_age"
Cohesion: 0.50
Nodes (3): The template this site's profile would be based on, if any., Which of the matching templates gets applied, or None for none of them.      One, _resolve_platform()

## Knowledge Gaps
- **154 isolated node(s):** `parfum-finder`, `$schema`, `$id`, `title`, `description` (+149 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **13 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `SearchScreen` connect `._refresh_table` to `TUI App & Screens`, `field_map`, `_trial`, `ComposeResult`, `Fixture Fetcher (Tests)`, `_ResultRow`, `_FixtureFetcher`, `._scan`?**
  _High betweenness centrality (0.064) - this node is a cross-community bridge._
- **Why does `PerfumeQuery` connect `Discovery CLI Reporting` to `_ResultRow`, `Title Matcher`, `TUI Confirm Dialog`, `CLI Entry Points`, `JsonLdProduct`, `Search TUI Screen`, `Snapshot Writing`, `conftest.py`, `snapshot_rows`, `Live Profile Validation`?**
  _High betweenness centrality (0.046) - this node is a cross-community bridge._
- **Why does `discover()` connect `Platform Discovery Flow` to `Site Profiles & Templates`, `CLI Entry Points`, `format_age`, `._build_rows`, `Basket Site Scenarios`, `CandidateFilter`?**
  _High betweenness centrality (0.034) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `SearchScreen` (e.g. with `ParfumFinderApp` and `test_s_opens_the_basket_and_escape_comes_back_to_the_results()`) actually correct?**
  _`SearchScreen` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `parfum-finder`, `$schema`, `$id` to the rest of the system?**
  _154 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `TUI App & Screens` be split into smaller, more focused modules?**
  _Cohesion score 0.09656565656565656 - nodes in this community are weakly interconnected._
- **Should `Site Profiles & Templates` be split into smaller, more focused modules?**
  _Cohesion score 0.05669050051072523 - nodes in this community are weakly interconnected._