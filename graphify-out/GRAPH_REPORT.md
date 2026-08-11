# Graph Report - parfum-finder  (2026-08-11)

## Corpus Check
- 70 files · ~259,000 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1799 nodes · 4943 edges · 70 communities (68 shown, 2 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 214 edges (avg confidence: 0.57)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `52b52ff0`
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
- TUI Confirm Dialog
- TUI App Shell
- Fetch Backends
- HTTP Request Schema
- Fixture Fetcher (Tests)
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
- Variant Pattern A
- Project Root
- ComposeResult
- _NoRootParser
- enum

## God Nodes (most connected - your core abstractions)
1. `search_site()` - 66 edges
2. `SearchScreen` - 63 edges
3. `PerfumeQuery` - 58 edges
4. `_profile()` - 58 edges
5. `discover()` - 56 edges
6. `SiteResult` - 53 edges
7. `BasketScreen` - 53 edges
8. `match_title()` - 45 edges
9. `_write_profile()` - 45 edges
10. `_app()` - 44 edges

## Surprising Connections (you probably didn't know these)
- `Shipping Non-linearity Rationale (why cheapest-per-item is wrong)` --semantically_similar_to--> `sites/ Site Profile Directory`  [INFERRED] [semantically similar]
  ARCHITECTURE.md → sites/README.md
- `Variant Pattern B (dropdown + AJAX price)` --semantically_similar_to--> `Variant Selector Detector Fix (WooCommerce 'variation' vs 'variant')`  [INFERRED] [semantically similar]
  ARCHITECTURE.md → docs/discovery-report.md
- `test_real_measurement_picks_httpx_for_a_plain_page()` --indirect_call--> `DiscoveryReport`  [INFERRED]
  tests/test_discover.py → src/parfum_finder/discover.py
- `_NoRootParser` --uses--> `ExtractionFailed`  [INFERRED]
  tests/test_engine.py → src/parfum_finder/engine.py
- `test_a_product_page_with_no_root_names_its_body_size()` --indirect_call--> `ExtractionFailed`  [INFERRED]
  tests/test_engine.py → src/parfum_finder/engine.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Sites Implementing Variant Pattern C (embedded JSON)** — docs_discovery_report_venco_site, docs_discovery_report_decantall_site, docs_discovery_report_luxurydekant_site, docs_discovery_report_ruxangroup_site, architecture_md_variant_pattern_c [EXTRACTED 1.00]
- **İdeasoft Platform Sites and Endpoint** — docs_discovery_report_dekantparfum_site, docs_discovery_report_dekantdoktoru_site, docs_discovery_report_ideasoft_related_options_endpoint, platforms_readme_ideasoft_json [EXTRACTED 1.00]
- **discover Command Output Artifacts (profile + fixtures + CI validation)** — architecture_md_discover_flow, sites_readme_sites_dir, fixtures_readme_fixtures_dir, github_workflows_ci_validate_profiles_step, architecture_md_validate_command [INFERRED 0.85]

## Communities (70 total, 2 thin omitted)

### Community 0 - "TUI App & Screens"
Cohesion: 0.10
Nodes (98): The Textual-based terminal UI: search and basket screens., _app(), _basket(), _cells(), _days_ago(), _leg(), _ok(), _open_basket() (+90 more)

### Community 1 - "Site Profiles & Templates"
Cohesion: 0.06
Nodes (81): _check_hook_kinds(), deep_merge(), _load_json(), load_platform_template(), load_platform_templates(), load_site_hooks(), load_site_profile(), Any (+73 more)

### Community 2 - "Title Matcher"
Cohesion: 0.13
Nodes (9): _Change, BasketPrice, One site's latest price for one basket line, only when it has one.      Rows wit, BasketScreen, Any, Path, The basket: the list on top, one scenario per site underneath., _remove() (+1 more)

### Community 3 - "HTTP/Browser Fetching"
Cohesion: 0.05
Nodes (59): BaseHTTPRequestHandler, browser_session(), _close_browser(), fetch(), _fetch_curl_cffi(), _fetch_httpx(), _fetch_playwright(), FetchResult (+51 more)

### Community 4 - "Search/Basket Domain Models"
Cohesion: 0.07
Nodes (116): Screen, ProductCandidate, One hit on a search results page, before its product page is opened.      `raw_t, One decant size of one product, in the units the database stores.      Tenths of, A candidate together with the decant sizes its product page offers., What one site had to say about one query, and how much to trust it.      Four st, SearchHit, SiteResult (+108 more)

### Community 5 - "Search Engine per Site"
Cohesion: 0.17
Nodes (23): ExtractionFailed, RuntimeError, A page answered but gave up nothing, where something was expected.      This is, Run one query against one site and read every hit's sizes.      Everything site-, search_site(), Path, Give the test profile's site id a hook file. The id is what binds them., test_a_before_search_that_returns_no_query_is_refused() (+15 more)

### Community 6 - "Platform Discovery Flow"
Cohesion: 0.15
Nodes (59): PlatformChooser, _ask_chooser(), discover(), Put the question only when there is one, and hold the answer to it.      An answ, Measure the strategies a site needs, then read its JSON-LD with the winner., _attempt(), _fake_probe(), Any (+51 more)

### Community 7 - "CLI Entry Points"
Cohesion: 0.08
Nodes (62): CaptureFixture, ask_which_platform(), main(), Any, Connection, Path, Command-line entry point.  Subcommands will be added incrementally as the projec, Scan every site for the perfumes named, store what came back, print it.      One (+54 more)

### Community 8 - "Architecture Rationale Docs"
Cohesion: 0.05
Nodes (53): basket Subset Enumeration + Local Improvement Algorithm, basket Optimizer (optimize function), Clone/Original Distinction (KLON ← <orijinal>), discover Discovery Flow, engine Concurrency Model (parallel sites, serial within site), Extraction Ladder (jsonld/endpoint/embedded/css), Fail-loud / status=suspect policy, hooks/<id>.py Escape Hatch (+45 more)

### Community 9 - "Search Engine Core"
Cohesion: 0.08
Nodes (45): HTMLParser, _check_variant_control(), _fetch_page(), _headers(), _is_excluded(), _paced_fetcher(), _page_offers_sizes(), _page_says_sold_out() (+37 more)

### Community 10 - "Basket Optimizer Core"
Cohesion: 0.15
Nodes (36): Collection, Prices, BasketItem, optimize(), Score one site against the basket, or against a subset of it.      `item_ids` is, Score every enabled site against the whole basket and sort the results.      Sit, Search for the cheapest way to split the basket across several sites.      Retur, One line of the shopping list: a basket row, not a unit count.      `item_id` is (+28 more)

### Community 11 - "Basket Store & Pricing"
Cohesion: 0.13
Nodes (24): Connection, Two snapshots written in the same second must resolve to the newer one.      A s, 5 ml at 125,00 TL is 25,00 TL per ml. Stored as kurus, ml as tenths., No price yet means no row, so the basket LEFT JOIN reads it as missing., A zero ml variant is a parse failure, and it must not reach the table.      If i, Adding the same perfume and size twice must accumulate, not clobber.      The ba, Insert one site → perfume → product → variant chain, return the variant id., The basket screen prints brand/name/concentration straight off this row.      Or (+16 more)

### Community 12 - "JSON-LD Product Extraction"
Cohesion: 0.09
Nodes (46): extract_embedded_variants(), extract_jsonld_products(), extract_jsonld_variants(), Read every JSON-LD Product declared on the page, in document order.      A block, Rung 1: read the page's JSON-LD as flat variant rows.      A product that declar, Rung 3: read the JSON blob the page carries but does not display.      Two shape, _fixture(), _one_product_html() (+38 more)

### Community 13 - "Basket TUI Screen"
Cohesion: 0.29
Nodes (7): price_history(), Row, Return one variant's past readings, newest first, capped at limit.      Empty fo, No history yet is a normal state for a variant, not an error to raise on., The identity a real scan writes must be the identity these lookups accept., test_a_scanned_perfume_can_be_read_back_by_basket_and_history(), test_price_history_is_empty_for_an_unknown_variant()

### Community 14 - "Platform Schema"
Cohesion: 0.06
Nodes (31): any, defaults, fingerprint, additionalProperties, items, minItems, type, description (+23 more)

### Community 15 - "Product Extraction"
Cohesion: 0.07
Nodes (45): _as_str(), _balanced_value(), _build_offer(), _build_product(), _coerce_in_stock(), _collect_offers(), _collect_products(), _collect_variants() (+37 more)

### Community 16 - "Schema Field Patterns"
Cohesion: 0.07
Nodes (29): format, pattern, type, pattern, type, default, type, pattern (+21 more)

### Community 17 - "Offline Profile Validation"
Cohesion: 0.10
Nodes (47): Run one site and classify what came back instead of raising.      It is also whe, run_site(), _counting_fetcher(), _profile(), Exception, Tests for the profile-driven search in parfum_finder.engine.  What these defend, Answer each call with the next canned result, then repeat the last one., A minimal working profile, with the fields a case cares about swapped in. (+39 more)

### Community 18 - "Playwright Errors"
Cohesion: 0.09
Nodes (41): PlaywrightNoResponse, PlaywrightNotInstalled, RuntimeError, The "playwright" strategy was requested but cannot run at all.      Covers both, Navigation completed but playwright returned no Response object.      Its own ty, _attempt(), _count_jsonld(), _count_product_objects() (+33 more)

### Community 19 - "Search TUI Screen"
Cohesion: 0.08
Nodes (42): find_header_columns(), find_match(), open_worksheet(), Any, Exception, Path, Protocol, Writing a search result onto the user's own Google Sheets wishlist.  The wishlis (+34 more)

### Community 20 - "Snapshot Writing"
Cohesion: 0.27
Nodes (13): apply_variant_rules(), Turn raw size rows into decant variants, dropping what is not a decant.      Thr, _row(), test_a_keyword_in_the_size_label_excludes_the_row_too(), test_a_literal_zero_price_reads_as_no_price_not_a_free_perfume(), test_a_size_at_the_threshold_is_a_bottle_whatever_it_calls_itself(), test_a_size_that_cannot_be_read_is_dropped(), test_an_uppercase_turkish_keyword_still_matches() (+5 more)

### Community 21 - "Candidate Filtering"
Cohesion: 0.09
Nodes (22): now_iso(), Return the current UTC time as 'YYYY-MM-DDTHH:MM:SSZ'.      Every timestamp writ, conn(), Path, Tests for parfum_finder.store: the timestamp helper and the schema.  The one har, An update aimed at a row that isn't there means the caller is out of sync., A snapshot pointing at a variant that doesn't exist has to be rejected.      SQL, Reopening an existing database must not wipe or re-raise on its schema. (+14 more)

### Community 22 - "Basket Site Scenarios"
Cohesion: 0.09
Nodes (30): One site's share of a split basket: what to buy there and what it costs.      `s, What it would cost to buy some or all of the basket from one site.      `covered, SiteScenario, SplitLeg, format_price(), Format a price for display (comma-thousands, dot-decimal).      Decimal('1250'), basket_lines(), basket_sites() (+22 more)

### Community 23 - "Price/Size Normalization"
Cohesion: 0.17
Nodes (19): _classify_single_separator(), format_ml(), _parse_number(), parse_price(), parse_size_ml(), Decimal, Number parsing and formatting for prices and volumes, plus text folding.  This i, Decide whether a lone separator marks a fraction or a thousands group.      Retu (+11 more)

### Community 24 - "JSON Schema Primitives"
Cohesion: 0.12
Nodes (23): null, string, properties, type, type, type, additionalProperties, properties (+15 more)

### Community 25 - "SQLite Store"
Cohesion: 0.22
Nodes (9): _FixtureFetcher, _path(), FormData, Headers, Method, Strategy, Serves one site's saved capture in place of the network.      Only three kinds o, The one real result card that led to the captured product page.          Cut out (+1 more)

### Community 26 - "Site Profile Fields"
Cohesion: 0.15
Nodes (13): base_url, discovered_at, extraction, id, needs_review, platform, search, shipping (+5 more)

### Community 27 - "Site Schema Validation Tests"
Cohesion: 0.19
Nodes (17): Draft202012Validator, _load_schema(), _platform_validator(), Any, Tests for schema/site.schema.json and schema/platform.schema.json.  These check, The third copy of the ladder is here, and nothing else would catch it drifting., _site_validator(), test_platform_schema_accepts_the_documented_example() (+9 more)

### Community 28 - "Variant Rule Fields"
Cohesion: 0.08
Nodes (26): exclude_keywords, field, max_size_ml, size_from, size_pattern, title, variant_label, items (+18 more)

### Community 29 - "Discovery CLI Reporting"
Cohesion: 0.09
Nodes (36): _choose_strategy(), DiscoveryReport, FieldConfidence, _flatten_defaults(), _format_choice(), _format_confidence(), _format_defaults(), _format_fingerprint() (+28 more)

### Community 30 - "Store Timestamp Tests"
Cohesion: 0.25
Nodes (6): _ClimbState, Basket scenario evaluation. A pure function, no network access, no sqlite.  Inpu, The hill-climb's working assignment plus the running per-site figures.      `sub, One site's shipping terms, read once and reused for every scenario.      `free_s, ShippingConfig, The three inputs basket.py's pure functions score: items, prices, shipping.

### Community 31 - "Live Profile Validation"
Cohesion: 0.09
Nodes (31): _canonical(), _covers(), _ends_with(), _index_of(), _match_text(), _own_identity(), product_label(), Perfume matching: brand and concentration are mandatory; fuzzy matching only app (+23 more)

### Community 32 - "Variant Extraction Fields"
Cohesion: 0.15
Nodes (13): attribute, script, type, properties, type, attribute, marker, selector (+5 more)

### Community 33 - "_ResultRow"
Cohesion: 0.09
Nodes (54): Match, match_title(), parse_query(), PerfumeQuery, The perfume being looked for, split into its three identity parts.      `concent, One site title judged against the query.      `concentration` is what the title, Split one typed line, "Dior Sauvage EDP", into the three identity parts.      Th, Judge one site title against a query, or None if it is not that perfume.      No (+46 more)

### Community 34 - "Fetch Strategy Probing"
Cohesion: 0.21
Nodes (12): One priced size of one perfume on one site, ready to be written.      The perfum, Write a whole scan at once and return how many prices were recorded.      Every, SnapshotRow, write_snapshots(), The drop happens here so no caller can forget it.      Both the CLI and the scre, A slow site must not spread one reading across several timestamps.      Rows wri, The number reported is what landed in the history, not what was offered., Half a site's sizes updated is worse than none of them.      The basket compares (+4 more)

### Community 35 - "Platform Field Mapping"
Cohesion: 0.18
Nodes (11): field_map, product_json, source, variants_path, additionalProperties, allOf, description, required (+3 more)

### Community 36 - "Shipping Config Schema"
Cohesion: 0.12
Nodes (16): free_shipping_threshold_kurus, integer, shipping_cost_kurus, minimum, type, type, free_shipping_threshold_kurus, notes (+8 more)

### Community 38 - "TUI Confirm Dialog"
Cohesion: 0.15
Nodes (23): One call has to leave a row the search table can read straight off.      The cal, The old price has to survive, and it must not become a second variant.      Appe, first_seen is what says how long a shop has carried a size., The title and URL are information, not identity.      A shop that rewords a list, EDT and EDP are different products at different prices.      Folding them into o, A sold-out size often shows no price at all, and 0 would mean free.      Writing, The column is 0/1, so the tri-state has to land somewhere on purpose.      Unkno, raw_title is the audit trail for a wrong match, so it cannot be blank.      A ro (+15 more)

### Community 39 - "TUI App Shell"
Cohesion: 0.19
Nodes (6): Decimal, Row, One priced size, exactly as the table shows it and as a keypress needs it., The default order: typed order, product, site, size.          The typed order co, The order once a column has been picked: the site layer drops out.          Aski, _ResultRow

### Community 40 - "Fetch Backends"
Cohesion: 0.14
Nodes (14): curl_cffi, httpx, playwright, result_item, result_title, result_url, strategy, url_template (+6 more)

### Community 41 - "HTTP Request Schema"
Cohesion: 0.12
Nodes (17): GET, POST, additionalProperties, allOf, description, properties, type, default (+9 more)

### Community 42 - "Fixture Fetcher (Tests)"
Cohesion: 0.22
Nodes (14): format_report(), Every site that has a profile, sorted so reports read the same way twice., Validate every site, or just the ones named.      Serial rather than concurrent:, Render the validations as the offline half of the report in APP_FLOW §6.      A, site_ids(), validate_all_offline(), _iso_days_ago(), A discovered_at stamp that lands a fixed number of days in the past.      Relati (+6 more)

### Community 44 - "Decant Variant Rules"
Cohesion: 0.11
Nodes (26): Fetcher, Protocol, Anything that can stand in for `fetch`.      Offline profile validation runs the, _age_of(), Check, _first_result_url(), _LayerUnavailable, _probe_layer() (+18 more)

### Community 45 - "Multi-Site Search Run"
Cohesion: 0.29
Nodes (13): Check one site's profile against that site's saved fixtures.      Never raises f, validate_offline(), _corrupted_sites_dir(), Any, Path, A sites/ directory holding one real profile with fields overwritten.      The re, test_a_dead_price_selector_is_caught_as_the_extraction_step(), test_a_dead_search_selector_is_caught_as_the_search_step() (+5 more)

### Community 46 - "Offline Validation Fixtures"
Cohesion: 0.25
Nodes (8): type, additionalProperties, type, body, request_headers, additionalProperties, description, type

### Community 47 - "Basket Domain Logic"
Cohesion: 0.21
Nodes (10): BasketReport, The cheapest basket split the search found. A heuristic, not a proof.      Every, Every site's single-site scenario, split by whether it covers everything.      A, SplitPlan, _heading(), A block title plus the blank line that keeps it off the block above it.      The, The one line that says the screen is holding something back, or is not., The best-combination block: its legs, grand total, and its honesty checks. (+2 more)

### Community 48 - "._build_rows"
Cohesion: 0.15
Nodes (19): collect_prices(), _format_product(), _format_stock(), _format_trial(), _has_exact_price(), PageTrial, Decimal, One page fetched with the chosen strategy and read for JSON-LD.      A fetch tha (+11 more)

### Community 49 - "test_engine.py"
Cohesion: 0.18
Nodes (12): _candidates_to_open(), CacheKey, CandidateFilter, Path, VariantsRead, Open one product page and read its sizes on the profile's layer.      A `cache`, Run every site against one query, all at once, and report each separately., Narrow the search results down to the pages worth a request.      The first one (+4 more)

### Community 50 - "Profile Age Checks"
Cohesion: 0.19
Nodes (17): format_live_report(), Run one site's profile against the real site.      Same contract as offline mode, Render offline and live results side by side, as APP_FLOW §6 shows them.      Bo, validate_live(), _DeadSite, _FakeSite, _fixture_site(), M5's own criterion: when a profile stops agreeing with its site's real markup, o (+9 more)

### Community 51 - "._refresh_table"
Cohesion: 0.12
Nodes (5): HeaderSelected, RowSelected, The initial screen: search bar, streaming results table, notices, footer., What each site charges for the product a block is about.          One entry per, SearchScreen

### Community 52 - "._cells"
Cohesion: 0.29
Nodes (5): Path, The Textual App root. Handles screen navigation and is the app's default entry p, Protocol, What this screen needs of engine.run_site.      A protocol rather than a plain c, SiteRunner

### Community 53 - "conftest.py"
Cohesion: 0.19
Nodes (19): add_basket_item(), _perfume_id(), _product_id(), Connection, SQLite persistence: an append-only price history.  Tables: sites, perfumes, prod, Write one scan's reading of one size, and return its snapshot id.      The perfu, Do the writing, without opening a transaction of its own., Add a size of a perfume to the basket, and return the basket_item_id.      The p (+11 more)

### Community 54 - "Endpoint Schema Fields"
Cohesion: 0.22
Nodes (9): result_item, result_title, result_url, url_template, search, additionalProperties, description, required (+1 more)

### Community 55 - "tui/__init__.py"
Cohesion: 0.18
Nodes (8): _age_line(), Every check run against one site's profile, in the order they ran.      Checks s, Whether the profile is old enough to be worth re-discovering., The check that broke, or None if the profile is intact., Validate every site against the live web, or just the ones named.      Serial li, The age note for one site, or None when its age is unremarkable.      A profile, SiteValidation, validate_all_live()

### Community 56 - "Request Schema Fields"
Cohesion: 0.18
Nodes (10): _count_result_cards(), live_query(), _no_results_check(), Any, Path, The query this site's fixture was captured with, read back out of its URL., Why an empty results page is suspicious, or why it is not.      A full page that, How many result rows the profile's own selectors find on a search page. (+2 more)

### Community 57 - "_FixtureFetcher"
Cohesion: 0.12
Nodes (9): Changed, Any, CacheKey, VariantsRead, One perfume of a search, as typed and as parsed.      The index is the outermost, Scan one site for every perfume of this search, one at a time.          Serial i, Empty the table for a new scan.          The columns are the same every time now, _Search (+1 more)

### Community 58 - "ComposeResult"
Cohesion: 0.27
Nodes (10): _named_profile(), Any, The real fetcher, with a list of every URL it was asked for., A profile whose search page lists two houses' bottles, as shops do., test_a_listing_from_another_house_costs_no_product_request(), test_a_scan_says_how_many_listings_it_skipped(), test_one_product_listed_under_two_searches_is_read_once(), test_two_shops_sharing_a_url_do_not_read_each_others_pages() (+2 more)

### Community 59 - "_named_profile"
Cohesion: 0.31
Nodes (9): _parse_selector(), Node, Run one "<css>::text" / "<css>::attr(name)" selector inside a node.      The nod, Run one "<css>::text" / "<css>::attr(name)" selector, reading every match., Split a "<css>::text" / "<css>::attr(name)" selector into its two parts., Read the attribute or text of one already-selected node, or None., _read_selected(), select_all() (+1 more)

### Community 60 - "_NoRootParser"
Cohesion: 0.25
Nodes (8): Split one typed line into the perfumes it asks for, on " - ".      The separator, split_queries(), test_a_hyphen_inside_a_brand_name_does_not_split_the_search(), test_a_line_naming_three_perfumes_is_read_as_three_searches(), test_a_piece_that_names_no_perfume_survives_to_be_complained_about(), test_a_stray_separator_is_not_worth_failing_over(), test_one_perfume_is_still_one_search(), test_the_same_perfume_typed_twice_is_scanned_once()

### Community 61 - "SiteScenario"
Cohesion: 0.27
Nodes (6): _listing_filter(), CandidateFilter, Decide, from a search result's own title, whether to open its page., _listing_filter(), CandidateFilter, Decide, from a search result's own title, whether to open its page.

### Community 62 - "format_age"
Cohesion: 0.25
Nodes (7): additionalProperties, allOf, description, $id, $schema, title, type

### Community 63 - "CandidateFilter"
Cohesion: 0.29
Nodes (7): in_stock, price, size_raw, additionalProperties, required, type, field_map

### Community 64 - "LogCaptureFixture"
Cohesion: 0.33
Nodes (6): basket_prices(), Return the basket price matrix: one row per (line, site) that has a price., A stale reading must never outrank the one taken after it.      latest_prices al, Whether an out-of-stock price counts as missing is the caller's call.      Dropp, test_basket_prices_keeps_out_of_stock_rows_with_in_stock_false(), test_basket_prices_reports_only_the_latest_snapshot()

### Community 65 - "MonkeyPatch"
Cohesion: 0.50
Nodes (4): rate_limit_ms, default, minimum, type

### Community 66 - "Runner"
Cohesion: 0.50
Nodes (3): The template this site's profile would be based on, if any., Which of the matching templates gets applied, or None for none of them.      One, _resolve_platform()

### Community 72 - "ComposeResult"
Cohesion: 0.14
Nodes (7): Pressed, ComposeResult, ConfirmScreen, ComposeResult, Path, Asks before a low-confidence match is written to the basket.      The two answer, Static

### Community 74 - "_NoRootParser"
Cohesion: 0.22
Nodes (9): _check_empty_search(), Fail when a search yielded no rows off a page that plainly lists products., _NoRootParser, MonkeyPatch, Record every delay the engine asks for instead of serving it.      Waiting for r, Stands in for HTMLParser when a page's markup cannot be read at all.      select, slept(), test_a_product_page_with_no_root_names_its_body_size() (+1 more)

### Community 91 - "enum"
Cohesion: 0.33
Nodes (6): css, embedded_json, endpoint, jsonld, enum, extraction

## Knowledge Gaps
- **154 isolated node(s):** `parfum-finder`, `$schema`, `$id`, `title`, `description` (+149 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `SiteResult` connect `Search/Basket Domain Models` to `TUI App & Screens`, `Title Matcher`, `HTTP/Browser Fetching`, `CLI Entry Points`, `Search Engine Core`, `Basket TUI Screen`, `Offline Profile Validation`, `Playwright Errors`, `Search TUI Screen`, `Basket Site Scenarios`, `_ResultRow`, `Fetch Strategy Probing`, `TUI App Shell`, `Decant Variant Rules`, `test_engine.py`, `._refresh_table`, `._cells`, `conftest.py`, `_FixtureFetcher`, `ComposeResult`?**
  _High betweenness centrality (0.041) - this node is a cross-community bridge._
- **Why does `load_site_profile()` connect `Site Profiles & Templates` to `TUI App & Screens`, `Title Matcher`, `CLI Entry Points`, `Decant Variant Rules`, `Multi-Site Search Run`, `Profile Age Checks`, `Search TUI Screen`, `Basket Site Scenarios`, `Request Schema Fields`, `_FixtureFetcher`?**
  _High betweenness centrality (0.032) - this node is a cross-community bridge._
- **Why does `PlaywrightNotInstalled` connect `Playwright Errors` to `HTTP/Browser Fetching`, `Search/Basket Domain Models`, `Search Engine per Site`, `Search Engine Core`, `_NoRootParser`, `._build_rows`, `Offline Profile Validation`, `Discovery CLI Reporting`?**
  _High betweenness centrality (0.029) - this node is a cross-community bridge._
- **Are the 9 inferred relationships involving `SearchScreen` (e.g. with `ParfumFinderApp` and `SiteResult`) actually correct?**
  _`SearchScreen` has 9 INFERRED edges - model-reasoned connections that need verification._
- **Are the 14 inferred relationships involving `PerfumeQuery` (e.g. with `SheetsError` and `WishlistRow`) actually correct?**
  _`PerfumeQuery` has 14 INFERRED edges - model-reasoned connections that need verification._
- **What connects `parfum-finder`, `$schema`, `$id` to the rest of the system?**
  _154 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `TUI App & Screens` be split into smaller, more focused modules?**
  _Cohesion score 0.09656565656565656 - nodes in this community are weakly interconnected._