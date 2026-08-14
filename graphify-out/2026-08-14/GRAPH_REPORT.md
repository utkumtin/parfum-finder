# Graph Report - parfum-finder  (2026-08-14)

## Corpus Check
- 70 files · ~261,557 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1837 nodes · 5071 edges · 72 communities (69 shown, 3 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 222 edges (avg confidence: 0.57)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `ea704a93`
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
- SiteScenario
- format_age
- CandidateFilter
- LogCaptureFixture
- MonkeyPatch
- Runner
- test_cached_prices_is_empty_for_a_perfume_nobody_scanned
- Variant Pattern A
- Project Root
- ComposeResult
- _NoRootParser

## God Nodes (most connected - your core abstractions)
1. `SearchScreen` - 70 edges
2. `search_site()` - 66 edges
3. `PerfumeQuery` - 59 edges
4. `_profile()` - 58 edges
5. `discover()` - 56 edges
6. `SiteResult` - 54 edges
7. `BasketScreen` - 53 edges
8. `_write_profile()` - 49 edges
9. `_app()` - 48 edges
10. `_submit_query()` - 47 edges

## Surprising Connections (you probably didn't know these)
- `Shipping Non-linearity Rationale (why cheapest-per-item is wrong)` --semantically_similar_to--> `sites/ Site Profile Directory`  [INFERRED] [semantically similar]
  ARCHITECTURE.md → sites/README.md
- `Variant Pattern B (dropdown + AJAX price)` --semantically_similar_to--> `Variant Selector Detector Fix (WooCommerce 'variation' vs 'variant')`  [INFERRED] [semantically similar]
  ARCHITECTURE.md → docs/discovery-report.md
- `test_real_measurement_picks_httpx_for_a_plain_page()` --indirect_call--> `DiscoveryReport`  [INFERRED]
  tests/test_discover.py → src/parfum_finder/discover.py
- `_NoRootParser` --uses--> `ExtractionFailed`  [INFERRED]
  tests/test_engine.py → src/parfum_finder/engine.py
- `test_a_hook_that_reads_nothing_is_named_as_the_culprit()` --indirect_call--> `ExtractionFailed`  [INFERRED]
  tests/test_engine.py → src/parfum_finder/engine.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Sites Implementing Variant Pattern C (embedded JSON)** — docs_discovery_report_venco_site, docs_discovery_report_decantall_site, docs_discovery_report_luxurydekant_site, docs_discovery_report_ruxangroup_site, architecture_md_variant_pattern_c [EXTRACTED 1.00]
- **İdeasoft Platform Sites and Endpoint** — docs_discovery_report_dekantparfum_site, docs_discovery_report_dekantdoktoru_site, docs_discovery_report_ideasoft_related_options_endpoint, platforms_readme_ideasoft_json [EXTRACTED 1.00]
- **discover Command Output Artifacts (profile + fixtures + CI validation)** — architecture_md_discover_flow, sites_readme_sites_dir, fixtures_readme_fixtures_dir, github_workflows_ci_validate_profiles_step, architecture_md_validate_command [INFERRED 0.85]

## Communities (72 total, 3 thin omitted)

### Community 0 - "TUI App & Screens"
Cohesion: 0.10
Nodes (98): The Textual-based terminal UI: search and basket screens., _app(), _basket(), _cells(), _days_ago(), _leg(), _ok(), _open_basket() (+90 more)

### Community 1 - "Site Profiles & Templates"
Cohesion: 0.06
Nodes (81): _check_hook_kinds(), deep_merge(), _load_json(), load_platform_template(), load_platform_templates(), load_site_hooks(), load_site_profile(), Any (+73 more)

### Community 2 - "Title Matcher"
Cohesion: 0.13
Nodes (7): _Change, BasketScreen, Any, Path, The basket: the list on top, one scenario per site underneath., The three inputs basket.py's pure functions score: items, prices, shipping., _set_qty()

### Community 3 - "HTTP/Browser Fetching"
Cohesion: 0.13
Nodes (29): browser_session(), fetch(), PlaywrightNotInstalled, Fetch one URL using exactly the given strategy.      `method`/`data` exist for t, Yield a fetcher that keeps one browser for every playwright page it reads., The "playwright" strategy was requested but cannot run at all.      Covers both, test_the_no_results_page_would_otherwise_read_as_suspect(), _fake_launch() (+21 more)

### Community 4 - "Search/Basket Domain Models"
Cohesion: 0.07
Nodes (117): One decant size of one product, in the units the database stores.      Tenths of, A candidate together with the decant sizes its product page offers., What one site had to say about one query, and how much to trust it.      Four st, SearchHit, SiteResult, Variant, A shop's imitation must not be stored as the perfume it imitates.      The clone, EDT and EDP are different products, so the row has to say which one this was. (+109 more)

### Community 5 - "Search Engine per Site"
Cohesion: 0.19
Nodes (18): _close_browser(), _fetch_curl_cffi(), _fetch_httpx(), _fetch_playwright(), FetchResult, _launch_browser(), Any, FormData (+10 more)

### Community 6 - "Platform Discovery Flow"
Cohesion: 0.15
Nodes (59): PlatformChooser, _ask_chooser(), discover(), Put the question only when there is one, and hold the answer to it.      An answ, Measure the strategies a site needs, then read its JSON-LD with the winner., _attempt(), _fake_probe(), Any (+51 more)

### Community 7 - "CLI Entry Points"
Cohesion: 0.09
Nodes (54): CaptureFixture, ask_which_platform(), main(), Path, Scan every site for the perfumes named, store what came back, print it.      One, Ask at the terminal which of several matching templates to apply.      Asked whi, run_search(), A multi-site price and stock comparison tool for perfume decants.  Includes a sh (+46 more)

### Community 8 - "Architecture Rationale Docs"
Cohesion: 0.05
Nodes (53): basket Subset Enumeration + Local Improvement Algorithm, basket Optimizer (optimize function), Clone/Original Distinction (KLON ← <orijinal>), discover Discovery Flow, engine Concurrency Model (parallel sites, serial within site), Extraction Ladder (jsonld/endpoint/embedded/css), Fail-loud / status=suspect policy, hooks/<id>.py Escape Hatch (+45 more)

### Community 9 - "Search Engine Core"
Cohesion: 0.07
Nodes (61): HTMLParser, _check_empty_search(), _check_variant_control(), _fetch_page(), _headers(), _is_excluded(), _paced_fetcher(), _page_offers_sizes() (+53 more)

### Community 10 - "Basket Optimizer Core"
Cohesion: 0.12
Nodes (41): Collection, Prices, BasketItem, _ClimbState, optimize(), Basket scenario evaluation. A pure function, no network access, no sqlite.  Inpu, The hill-climb's working assignment plus the running per-site figures.      `sub, Score one site against the basket, or against a subset of it.      `item_ids` is (+33 more)

### Community 11 - "Basket Store & Pricing"
Cohesion: 0.09
Nodes (31): conn(), Path, Tests for parfum_finder.store: the timestamp helper and the schema.  The one har, NULL means the site has no free shipping tier at all, not a threshold of zero., Deleting a row that's already gone is a race between two screens, not a bug., A snapshot pointing at a variant that doesn't exist has to be rejected.      SQL, Two snapshots written in the same second must resolve to the newer one.      A s, 5 ml at 125,00 TL is 25,00 TL per ml. Stored as kurus, ml as tenths. (+23 more)

### Community 12 - "JSON-LD Product Extraction"
Cohesion: 0.13
Nodes (32): extract_jsonld_products(), Read every JSON-LD Product declared on the page, in document order.      A block, _one_product_html(), Tests for parfum_finder.extract.  Every case here is a shape a real store actual, Wrap a JSON-LD product body in a page, for the one-field-at-a-time cases., test_a_broken_block_does_not_lose_the_valid_one(), test_availability_spellings_all_land_in_the_same_bucket(), test_boolean_values_are_never_read_as_price_or_text() (+24 more)

### Community 13 - "Basket TUI Screen"
Cohesion: 0.29
Nodes (7): price_history(), Row, Return one variant's past readings, newest first, capped at limit.      Empty fo, No history yet is a normal state for a variant, not an error to raise on., The identity a real scan writes must be the identity these lookups accept., test_a_scanned_perfume_can_be_read_back_by_basket_and_history(), test_price_history_is_empty_for_an_unknown_variant()

### Community 14 - "Platform Schema"
Cohesion: 0.06
Nodes (31): any, defaults, fingerprint, additionalProperties, items, minItems, type, description (+23 more)

### Community 15 - "Product Extraction"
Cohesion: 0.11
Nodes (30): _as_str(), _build_offer(), _build_product(), _coerce_in_stock(), _collect_offers(), _collect_products(), _collect_variants(), _css_variant() (+22 more)

### Community 16 - "Schema Field Patterns"
Cohesion: 0.05
Nodes (39): css, embedded_json, endpoint, jsonld, format, pattern, type, pattern (+31 more)

### Community 17 - "Offline Profile Validation"
Cohesion: 0.10
Nodes (40): ExtractionFailed, RuntimeError, A page answered but gave up nothing, where something was expected.      This is, Run one query against one site and read every hit's sizes.      Everything site-, search_site(), _named_profile(), Any, Tests for the profile-driven search in parfum_finder.engine.  What these defend (+32 more)

### Community 18 - "Playwright Errors"
Cohesion: 0.15
Nodes (21): _attempt(), _count_jsonld(), _count_product_objects(), _detect_platforms(), format_report(), _label_platform(), _one_line(), ProbeAttempt (+13 more)

### Community 19 - "Search TUI Screen"
Cohesion: 0.07
Nodes (43): File logging for the app's own diagnostics.  Nothing here ever writes to the con, find_header_columns(), find_match(), open_worksheet(), Any, Exception, Path, Protocol (+35 more)

### Community 20 - "Snapshot Writing"
Cohesion: 0.27
Nodes (13): apply_variant_rules(), Turn raw size rows into decant variants, dropping what is not a decant.      Thr, _row(), test_a_keyword_in_the_size_label_excludes_the_row_too(), test_a_literal_zero_price_reads_as_no_price_not_a_free_perfume(), test_a_size_at_the_threshold_is_a_bottle_whatever_it_calls_itself(), test_a_size_that_cannot_be_read_is_dropped(), test_an_uppercase_turkish_keyword_still_matches() (+5 more)

### Community 21 - "Candidate Filtering"
Cohesion: 0.15
Nodes (18): extract_embedded_variants(), extract_jsonld_variants(), _flatten_jsonld(), Rung 1: read the page's JSON-LD as flat variant rows.      A product that declar, Turn one Product and everything under it into rows., Rung 3: read the JSON blob the page carries but does not display.      Two shape, _fixture(), Read a captured product page. (+10 more)

### Community 22 - "Basket Site Scenarios"
Cohesion: 0.21
Nodes (15): probe(), Fetch `url` with every strategy and report diagnostics for each.      timeout_s, MonkeyPatch, Tests for parfum_finder.probe.  probe() always tries all three strategies -- the, test_probe_counts_jsonld_product_and_platform_signature(), test_probe_counts_product_across_jsonld_root_shapes(), test_probe_counts_product_markup_without_any_jsonld(), test_probe_counts_products_nested_below_the_top_level() (+7 more)

### Community 23 - "Price/Size Normalization"
Cohesion: 0.15
Nodes (21): _classify_single_separator(), format_ml(), format_price(), _parse_number(), parse_price(), parse_size_ml(), Decimal, Number parsing and formatting for prices and volumes, plus text folding.  This i (+13 more)

### Community 24 - "JSON Schema Primitives"
Cohesion: 0.11
Nodes (25): integer, null, string, properties, type, type, type, type (+17 more)

### Community 25 - "SQLite Store"
Cohesion: 0.22
Nodes (9): _FixtureFetcher, _path(), FormData, Headers, Method, Strategy, Serves one site's saved capture in place of the network.      Only three kinds o, The one real result card that led to the captured product page.          Cut out (+1 more)

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
Cohesion: 0.50
Nodes (3): The template this site's profile would be based on, if any., Which of the matching templates gets applied, or None for none of them.      One, _resolve_platform()

### Community 30 - "Store Timestamp Tests"
Cohesion: 0.14
Nodes (15): _balanced_value(), _embedded_documents(), extract_endpoint_variants(), _loads_or_skip(), Any, Rung 2: read the variant list out of a platform's JSON response.      `document`, Yield every JSON document the page hides, in document order., Parse `text` as JSON, yielding nothing when it isn't JSON.      Pages are full o (+7 more)

### Community 31 - "Live Profile Validation"
Cohesion: 0.09
Nodes (31): _canonical(), _covers(), _ends_with(), _index_of(), _match_text(), _own_identity(), product_label(), Perfume matching: brand and concentration are mandatory; fuzzy matching only app (+23 more)

### Community 32 - "Variant Extraction Fields"
Cohesion: 0.12
Nodes (16): attribute, script, type, additionalProperties, allOf, description, properties, type (+8 more)

### Community 33 - "_ResultRow"
Cohesion: 0.10
Nodes (52): Match, match_title(), parse_query(), PerfumeQuery, The perfume being looked for, split into its three identity parts.      `concent, One site title judged against the query.      `concentration` is what the title, Split one typed line, "Dior Sauvage EDP", into the three identity parts.      Th, Judge one site title against a query, or None if it is not that perfume.      No (+44 more)

### Community 34 - "Fetch Strategy Probing"
Cohesion: 0.10
Nodes (27): One site's share of a split basket: what to buy there and what it costs.      `s, What it would cost to buy some or all of the basket from one site.      `covered, SiteScenario, SplitLeg, basket_sites(), BasketLine, BasketPrice, BasketSite (+19 more)

### Community 35 - "Platform Field Mapping"
Cohesion: 0.18
Nodes (11): field_map, product_json, source, variants_path, required, additionalProperties, allOf, description (+3 more)

### Community 36 - "Shipping Config Schema"
Cohesion: 0.14
Nodes (14): free_shipping_threshold_kurus, shipping_cost_kurus, minimum, type, free_shipping_threshold_kurus, notes, shipping, shipping_cost_kurus (+6 more)

### Community 37 - "_trial"
Cohesion: 0.14
Nodes (27): Run one site and classify what came back instead of raising.      It is also whe, run_site(), _counting_fetcher(), _profile(), Exception, Answer each call with the next canned result, then repeat the last one., A minimal working profile, with the fields a case cares about swapped in., test_a_dead_link_selector_is_suspect_not_empty() (+19 more)

### Community 38 - "TUI Confirm Dialog"
Cohesion: 0.11
Nodes (40): Connection, The drop happens here so no caller can forget it.      Both the CLI and the scre, One call has to leave a row the search table can read straight off.      The cal, The old price has to survive, and it must not become a second variant.      Appe, first_seen is what says how long a shop has carried a size., The title and URL are information, not identity.      A shop that rewords a list, EDT and EDP are different products at different prices.      Folding them into o, A sold-out size often shows no price at all, and 0 would mean free.      Writing (+32 more)

### Community 39 - "TUI App Shell"
Cohesion: 0.13
Nodes (17): _age_line(), _age_of(), format_live_report(), profile_age_days(), datetime, Profile staleness checks. Two modes: offline (against saved fixtures) and live (, Every check run against one site's profile, in the order they ran.      Checks s, Whether the profile is old enough to be worth re-discovering. (+9 more)

### Community 40 - "Fetch Backends"
Cohesion: 0.14
Nodes (14): curl_cffi, httpx, playwright, result_item, result_title, result_url, strategy, url_template (+6 more)

### Community 41 - "HTTP Request Schema"
Cohesion: 0.14
Nodes (14): GET, POST, properties, default, enum, type, type, type (+6 more)

### Community 42 - "Fixture Fetcher (Tests)"
Cohesion: 0.25
Nodes (8): exclude_keywords, max_size_ml, size_from, size_pattern, variant_rules, additionalProperties, required, type

### Community 43 - "FieldConfidence"
Cohesion: 0.16
Nodes (7): PlaywrightNoResponse, RuntimeError, Navigation completed but playwright returned no Response object.      Its own ty, _FakeBrowser, _FakePage, Any, test_fetch_playwright_no_response_raises_its_own_error_type()

### Community 44 - "Decant Variant Rules"
Cohesion: 0.13
Nodes (18): Check, _count_result_cards(), _first_result_url(), _no_results_check(), _probe_layer(), _probe_other_layers(), Any, Path (+10 more)

### Community 45 - "Multi-Site Search Run"
Cohesion: 0.22
Nodes (14): format_report(), Every site that has a profile, sorted so reports read the same way twice., Validate every site, or just the ones named.      Serial rather than concurrent:, Render the validations as the offline half of the report in APP_FLOW §6.      A, site_ids(), validate_all_offline(), _iso_days_ago(), A discovered_at stamp that lands a fixed number of days in the past.      Relati (+6 more)

### Community 46 - "Offline Validation Fixtures"
Cohesion: 0.25
Nodes (8): type, additionalProperties, type, body, request_headers, additionalProperties, description, type

### Community 47 - "Basket Domain Logic"
Cohesion: 0.40
Nodes (3): ComposeResult, ComposeResult, Static

### Community 48 - "._build_rows"
Cohesion: 0.07
Nodes (53): _choose_strategy(), collect_prices(), DiscoveryReport, FieldConfidence, _flatten_defaults(), _format_choice(), _format_confidence(), _format_defaults() (+45 more)

### Community 49 - "test_engine.py"
Cohesion: 0.29
Nodes (13): Check one site's profile against that site's saved fixtures.      Never raises f, validate_offline(), _corrupted_sites_dir(), Any, Path, A sites/ directory holding one real profile with fields overwritten.      The re, test_a_dead_price_selector_is_caught_as_the_extraction_step(), test_a_dead_search_selector_is_caught_as_the_search_step() (+5 more)

### Community 50 - "Profile Age Checks"
Cohesion: 0.17
Nodes (19): live_query(), The query this site's fixture was captured with, read back out of its URL., Run one site's profile against the real site.      Same contract as offline mode, validate_live(), _DeadSite, _FakeSite, _fixture_site(), M5's own criterion: when a profile stops agreeing with its site's real markup, o (+11 more)

### Community 51 - "._refresh_table"
Cohesion: 0.07
Nodes (17): Changed, HeaderSelected, RowSelected, Decimal, Row, One priced size, exactly as the table shows it and as a keypress needs it., The initial screen: search bar, streaming results table, notices, footer., Close out a submit that named no perfume anyone could look for. (+9 more)

### Community 52 - "._cells"
Cohesion: 0.21
Nodes (10): BasketReport, The cheapest basket split the search found. A heuristic, not a proof.      Every, Every site's single-site scenario, split by whether it covers everything.      A, SplitPlan, _heading(), A block title plus the blank line that keeps it off the block above it.      The, The one line that says the screen is holding something back, or is not., The best-combination block: its legs, grand total, and its honesty checks. (+2 more)

### Community 53 - "conftest.py"
Cohesion: 0.16
Nodes (20): add_basket_item(), now_iso(), _perfume_id(), _product_id(), Connection, Return the current UTC time as 'YYYY-MM-DDTHH:MM:SSZ'.      Every timestamp writ, Write one scan's reading of one size, and return its snapshot id.      The perfu, Write a whole scan at once and return how many prices were recorded.      Every (+12 more)

### Community 54 - "Endpoint Schema Fields"
Cohesion: 0.22
Nodes (9): result_item, result_title, result_url, url_template, search, additionalProperties, description, required (+1 more)

### Community 55 - "tui/__init__.py"
Cohesion: 0.17
Nodes (12): _candidates_to_open(), CacheKey, CandidateFilter, Path, Run every site against one query, all at once, and report each separately., Narrow the search results down to the pages worth a request.      The first one, run_sites(), test_a_dead_site_does_not_take_the_others_down() (+4 more)

### Community 56 - "Request Schema Fields"
Cohesion: 0.24
Nodes (6): BaseHTTPRequestHandler, _Handler, _playwright_usable(), Shared pytest fixtures.  A local HTTP server used by fetch/probe tests: real req, Whether the playwright rung can actually run here, binary included.      Checkin, server_url()

### Community 57 - "_FixtureFetcher"
Cohesion: 0.09
Nodes (23): cached_prices(), CachedPrice, SQLite persistence: an append-only price history.  Tables: sites, perfumes, prod, One priced size of one perfume on one site, ready to be written.      The perfum, Turn one site's hits into the rows write_snapshots is ready to store.      Share, One stored price for one size of one perfume on one site.      What the results, Return the latest stored price of every size of this perfume, per site.      Bra, snapshot_rows() (+15 more)

### Community 58 - "ComposeResult"
Cohesion: 0.36
Nodes (10): Path, Give the test profile's site id a hook file. The id is what binds them., test_a_before_search_that_returns_no_query_is_refused(), test_a_broken_hook_is_an_error_not_a_silent_empty(), test_a_hook_that_reads_nothing_is_named_as_the_culprit(), test_after_search_can_drop_a_result_the_selectors_could_not(), test_before_search_rewrites_the_query_that_is_actually_sent(), test_parse_variants_returning_none_leaves_the_page_to_the_profile() (+2 more)

### Community 59 - "_named_profile"
Cohesion: 0.31
Nodes (9): _parse_selector(), Node, Run one "<css>::text" / "<css>::attr(name)" selector inside a node.      The nod, Run one "<css>::text" / "<css>::attr(name)" selector, reading every match., Split a "<css>::text" / "<css>::attr(name)" selector into its two parts., Read the attribute or text of one already-selected node, or None., _read_selected(), select_all() (+1 more)

### Community 60 - "_NoRootParser"
Cohesion: 0.29
Nodes (7): in_stock, price, size_raw, additionalProperties, required, type, field_map

### Community 61 - "SiteScenario"
Cohesion: 0.11
Nodes (20): _listing_filter(), Any, CandidateFilter, Connection, Command-line entry point.  Subcommands will be added incrementally as the projec, Scan every perfume against every site and print each site as it lands.      One, Decide, from a search result's own title, whether to open its page., Write one site's rows in a transaction of its own.      Per site rather than per (+12 more)

### Community 62 - "format_age"
Cohesion: 0.33
Nodes (6): basket_lines(), Return every basket line, oldest add first.      Ordered by added_at with basket, Two lines added within the same second must still read back the same way twice., A basket line nobody sells must still be visible via basket_lines.      basket_p, test_basket_lines_breaks_a_same_second_tie_by_basket_item_id(), test_basket_prices_has_no_row_for_a_line_no_site_prices()

### Community 63 - "CandidateFilter"
Cohesion: 0.33
Nodes (6): basket_prices(), Return the basket price matrix: one row per (line, site) that has a price., A 10 ml listing must never fill a basket line asking for 5 ml.      The matrix j, Whether an out-of-stock price counts as missing is the caller's call.      Dropp, test_basket_prices_joins_on_the_exact_integer_size(), test_basket_prices_keeps_out_of_stock_rows_with_in_stock_false()

### Community 64 - "LogCaptureFixture"
Cohesion: 0.33
Nodes (6): Set a basket line's quantity, clamped to at least 1, and return it.      The tab, set_basket_qty(), The table's CHECK (qty > 0) would reject a bare 0, and the '-' key has to     su, An update aimed at a row that isn't there means the caller is out of sync., test_set_basket_qty_clamps_zero_and_negatives_to_one(), test_set_basket_qty_on_an_unknown_id_raises()

### Community 65 - "MonkeyPatch"
Cohesion: 0.53
Nodes (4): FormData, Headers, Method, Strategy

### Community 66 - "Runner"
Cohesion: 0.50
Nodes (4): format_age(), Turn a price age in days into the words the age column shows., The age column exists to be glanced at, so it is phrased, not printed., test_format_age_reads_as_words_not_a_timestamp()

### Community 72 - "ComposeResult"
Cohesion: 0.10
Nodes (13): Pressed, Screen, ParfumFinderApp, Path, The Textual App root. Handles screen navigation and is the app's default entry p, Root app: pushes the search screen on mount., ConfirmScreen, Path (+5 more)

### Community 74 - "_NoRootParser"
Cohesion: 0.29
Nodes (6): _NoRootParser, MonkeyPatch, Record every delay the engine asks for instead of serving it.      Waiting for r, Stands in for HTMLParser when a page's markup cannot be read at all.      select, slept(), test_a_search_page_with_no_root_names_its_body_size()

## Knowledge Gaps
- **154 isolated node(s):** `parfum-finder`, `$schema`, `$id`, `title`, `description` (+149 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `SiteResult` connect `Search/Basket Domain Models` to `TUI App & Screens`, `Fetch Strategy Probing`, `HTTP/Browser Fetching`, `Title Matcher`, `Search Engine per Site`, `_trial`, `ComposeResult`, `Search Engine Core`, `Basket TUI Screen`, `Search TUI Screen`, `._refresh_table`, `tui/__init__.py`, `_FixtureFetcher`, `SiteScenario`?**
  _High betweenness centrality (0.048) - this node is a cross-community bridge._
- **Why does `PlaywrightNotInstalled` connect `HTTP/Browser Fetching` to `Search/Basket Domain Models`, `Search Engine per Site`, `_trial`, `Search Engine Core`, `_NoRootParser`, `FieldConfidence`, `._build_rows`, `Offline Profile Validation`, `Playwright Errors`, `Basket Site Scenarios`, `Request Schema Fields`?**
  _High betweenness centrality (0.039) - this node is a cross-community bridge._
- **Why does `SearchScreen` connect `._refresh_table` to `TUI App & Screens`, `_ResultRow`, `Title Matcher`, `Search/Basket Domain Models`, `CLI Entry Points`, `ComposeResult`, `Search Engine Core`, `Basket Domain Logic`, `Search TUI Screen`, `_FixtureFetcher`?**
  _High betweenness centrality (0.033) - this node is a cross-community bridge._
- **Are the 10 inferred relationships involving `SearchScreen` (e.g. with `ParfumFinderApp` and `SiteResult`) actually correct?**
  _`SearchScreen` has 10 INFERRED edges - model-reasoned connections that need verification._
- **Are the 15 inferred relationships involving `PerfumeQuery` (e.g. with `SheetsError` and `WishlistRow`) actually correct?**
  _`PerfumeQuery` has 15 INFERRED edges - model-reasoned connections that need verification._
- **What connects `parfum-finder`, `$schema`, `$id` to the rest of the system?**
  _154 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `TUI App & Screens` be split into smaller, more focused modules?**
  _Cohesion score 0.09656565656565656 - nodes in this community are weakly interconnected._