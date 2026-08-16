# Graph Report - parfum-finder  (2026-08-16)

## Corpus Check
- 103 files · ~282,823 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2228 nodes · 6145 edges · 85 communities (77 shown, 8 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 337 edges (avg confidence: 0.57)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `19d9d0e1`
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
- _scenario_block
- Headers
- format_age
- _NoRootParser
- enum
- _collect_products
- AddButton.tsx
- BasketRow
- ResultRow
- MonkeyPatch

## God Nodes (most connected - your core abstractions)
1. `search_site()` - 66 edges
2. `SearchScreen` - 64 edges
3. `_profile()` - 58 edges
4. `discover()` - 56 edges
5. `PerfumeQuery` - 52 edges
6. `_write_profile()` - 50 edges
7. `connect()` - 48 edges
8. `BasketScreen` - 48 edges
9. `_app()` - 48 edges
10. `_submit_query()` - 48 edges

## Surprising Connections (you probably didn't know these)
- `Shipping Non-linearity Rationale (why cheapest-per-item is wrong)` --semantically_similar_to--> `sites/ Site Profile Directory`  [INFERRED] [semantically similar]
  ARCHITECTURE.md → sites/README.md
- `Variant Pattern B (dropdown + AJAX price)` --semantically_similar_to--> `Variant Selector Detector Fix (WooCommerce 'variation' vs 'variant')`  [INFERRED] [semantically similar]
  ARCHITECTURE.md → docs/discovery-report.md
- `test_a_site_listing_the_same_size_twice_yields_one_row()` --indirect_call--> `RowsReady`  [INFERRED]
  tests/test_scan_service.py → src/parfum_finder/services/scan.py
- `test_a_write_failure_still_reports_the_rows_and_counts_as_an_error()` --indirect_call--> `RowsReady`  [INFERRED]
  tests/test_scan_service.py → src/parfum_finder/services/scan.py
- `test_a_runner_exception_is_reported_as_a_site_finished_error()` --indirect_call--> `SiteFinished`  [INFERRED]
  tests/test_scan_service.py → src/parfum_finder/services/scan.py

## Import Cycles
- 3-file cycle: `src/parfum_finder/__init__.py -> src/parfum_finder/cli.py -> src/parfum_finder/validate.py -> src/parfum_finder/__init__.py`
- 3-file cycle: `src/parfum_finder/__init__.py -> src/parfum_finder/cli.py -> src/parfum_finder/profiles.py -> src/parfum_finder/__init__.py`
- 3-file cycle: `src/parfum_finder/__init__.py -> src/parfum_finder/cli.py -> src/parfum_finder/logging_setup.py -> src/parfum_finder/__init__.py`
- 3-file cycle: `src/parfum_finder/__init__.py -> src/parfum_finder/cli.py -> src/parfum_finder/store.py -> src/parfum_finder/__init__.py`
- 4-file cycle: `src/parfum_finder/__init__.py -> src/parfum_finder/cli.py -> src/parfum_finder/validate.py -> src/parfum_finder/profiles.py -> src/parfum_finder/__init__.py`
- 4-file cycle: `src/parfum_finder/__init__.py -> src/parfum_finder/cli.py -> src/parfum_finder/engine.py -> src/parfum_finder/profiles.py -> src/parfum_finder/__init__.py`
- 4-file cycle: `src/parfum_finder/__init__.py -> src/parfum_finder/cli.py -> src/parfum_finder/discover.py -> src/parfum_finder/profiles.py -> src/parfum_finder/__init__.py`
- 4-file cycle: `src/parfum_finder/__init__.py -> src/parfum_finder/cli.py -> src/parfum_finder/discover.py -> src/parfum_finder/store.py -> src/parfum_finder/__init__.py`
- 5-file cycle: `src/parfum_finder/__init__.py -> src/parfum_finder/cli.py -> src/parfum_finder/validate.py -> src/parfum_finder/engine.py -> src/parfum_finder/profiles.py -> src/parfum_finder/__init__.py`
- 5-file cycle: `src/parfum_finder/__init__.py -> src/parfum_finder/cli.py -> src/parfum_finder/store.py -> src/parfum_finder/engine.py -> src/parfum_finder/profiles.py -> src/parfum_finder/__init__.py`

## Hyperedges (group relationships)
- **Sites Implementing Variant Pattern C (embedded JSON)** — docs_discovery_report_venco_site, docs_discovery_report_decantall_site, docs_discovery_report_luxurydekant_site, docs_discovery_report_ruxangroup_site, architecture_md_variant_pattern_c [EXTRACTED 1.00]
- **İdeasoft Platform Sites and Endpoint** — docs_discovery_report_dekantparfum_site, docs_discovery_report_dekantdoktoru_site, docs_discovery_report_ideasoft_related_options_endpoint, platforms_readme_ideasoft_json [EXTRACTED 1.00]
- **discover Command Output Artifacts (profile + fixtures + CI validation)** — architecture_md_discover_flow, sites_readme_sites_dir, fixtures_readme_fixtures_dir, github_workflows_ci_validate_profiles_step, architecture_md_validate_command [INFERRED 0.85]

## Communities (85 total, 8 thin omitted)

### Community 0 - "TUI App & Screens"
Cohesion: 0.09
Nodes (100): The Textual-based terminal UI: search and basket screens., _app(), _basket(), _cells(), _days_ago(), _leg(), _ok(), _open_basket() (+92 more)

### Community 1 - "Site Profiles & Templates"
Cohesion: 0.06
Nodes (82): _check_hook_kinds(), deep_merge(), _load_json(), load_platform_template(), load_platform_templates(), load_site_hooks(), load_site_profile(), Any (+74 more)

### Community 2 - "Title Matcher"
Cohesion: 0.08
Nodes (28): CachedPrice, _Change, ResultRow, SnapshotRow, _about(), BasketPriceExcluded, BasketRefreshStarted, BasketRowFinished (+20 more)

### Community 3 - "HTTP/Browser Fetching"
Cohesion: 0.08
Nodes (49): browser_session(), _close_browser(), fetch(), _fetch_curl_cffi(), _fetch_httpx(), _fetch_playwright(), FetchResult, _launch_browser() (+41 more)

### Community 4 - "Search/Basket Domain Models"
Cohesion: 0.07
Nodes (119): Screen, One decant size of one product, in the units the database stores.      Tenths of, Variant, connect(), Path, Open the price database, creating the schema if it isn't there yet.      Foreign, Write one scan's reading of one size, and return its snapshot id.      The perfu, record_snapshot() (+111 more)

### Community 5 - "Search Engine per Site"
Cohesion: 0.15
Nodes (27): Match, match_title(), PerfumeQuery, The perfume being looked for, split into its three identity parts.      `concent, One site title judged against the query.      `concentration` is what the title, Judge one site title against a query, or None if it is not that perfume.      No, test_a_brand_needs_all_of_its_words_not_one(), test_a_brand_only_query_matches_a_title_that_is_only_that_brand() (+19 more)

### Community 6 - "Platform Discovery Flow"
Cohesion: 0.15
Nodes (59): PlatformChooser, _ask_chooser(), discover(), Put the question only when there is one, and hold the answer to it.      An answ, Measure the strategies a site needs, then read its JSON-LD with the winner., _attempt(), _fake_probe(), Any (+51 more)

### Community 7 - "CLI Entry Points"
Cohesion: 0.11
Nodes (50): CaptureFixture, ask_which_platform(), main(), Path, Scan every site for the perfumes named, store what came back, print it.      One, Ask at the terminal which of several matching templates to apply.      Asked whi, run_search(), Path (+42 more)

### Community 8 - "Architecture Rationale Docs"
Cohesion: 0.05
Nodes (53): basket Subset Enumeration + Local Improvement Algorithm, basket Optimizer (optimize function), Clone/Original Distinction (KLON ← <orijinal>), discover Discovery Flow, engine Concurrency Model (parallel sites, serial within site), Extraction Ladder (jsonld/endpoint/embedded/css), Fail-loud / status=suspect policy, hooks/<id>.py Escape Hatch (+45 more)

### Community 9 - "Search Engine Core"
Cohesion: 0.07
Nodes (65): CandidateFilter, HTMLParser, _candidates_to_open(), _check_empty_search(), _check_variant_control(), ExtractionFailed, _fetch_page(), _headers() (+57 more)

### Community 10 - "Basket Optimizer Core"
Cohesion: 0.10
Nodes (52): Collection, BasketRow, _score_basket(), basket_inputs(), BasketItem, build_basket_rows(), optimize(), BasketRow (+44 more)

### Community 11 - "Basket Store & Pricing"
Cohesion: 0.12
Nodes (29): A stale reading must never outrank the one taken after it.      latest_prices al, A 10 ml listing must never fill a basket line asking for 5 ml.      The matrix j, One call has to leave a row the search table can read straight off.      The cal, The old price has to survive, and it must not become a second variant.      Appe, first_seen is what says how long a shop has carried a size., The title and URL are information, not identity.      A shop that rewords a list, EDT and EDP are different products at different prices.      Folding them into o, A sold-out size often shows no price at all, and 0 would mean free.      Writing (+21 more)

### Community 12 - "JSON-LD Product Extraction"
Cohesion: 0.13
Nodes (32): extract_jsonld_products(), Read every JSON-LD Product declared on the page, in document order.      A block, _one_product_html(), Tests for parfum_finder.extract.  Every case here is a shape a real store actual, Wrap a JSON-LD product body in a page, for the one-field-at-a-time cases., test_a_broken_block_does_not_lose_the_valid_one(), test_availability_spellings_all_land_in_the_same_bucket(), test_boolean_values_are_never_read_as_price_or_text() (+24 more)

### Community 13 - "Basket TUI Screen"
Cohesion: 0.11
Nodes (34): PyInstaller entry point for the packaged desktop app.  Kept outside src/parfum_f, main(), _ping(), Path, The Windows desktop entry point: an ephemeral-port FastAPI backend behind a nati, Best-effort native message box.      A missing WebView2 Runtime is the expected, Boot the backend headlessly, hit it once, exit. No window opens.      This is wh, _report_startup_failure() (+26 more)

### Community 14 - "Platform Schema"
Cohesion: 0.06
Nodes (31): any, defaults, fingerprint, additionalProperties, items, minItems, type, description (+23 more)

### Community 15 - "Product Extraction"
Cohesion: 0.21
Nodes (15): probe(), Fetch `url` with every strategy and report diagnostics for each.      timeout_s, MonkeyPatch, Tests for parfum_finder.probe.  probe() always tries all three strategies -- the, test_probe_counts_jsonld_product_and_platform_signature(), test_probe_counts_product_across_jsonld_root_shapes(), test_probe_counts_product_markup_without_any_jsonld(), test_probe_counts_products_nested_below_the_top_level() (+7 more)

### Community 16 - "Schema Field Patterns"
Cohesion: 0.06
Nodes (33): format, pattern, type, pattern, type, default, type, pattern (+25 more)

### Community 17 - "Offline Profile Validation"
Cohesion: 0.07
Nodes (79): Path, Run one site and classify what came back instead of raising.      It is also whe, Run one query against one site and read every hit's sizes.      Everything site-, run_site(), search_site(), _counting_fetcher(), _named_profile(), _profile() (+71 more)

### Community 18 - "Playwright Errors"
Cohesion: 0.13
Nodes (24): PlaywrightNoResponse, RuntimeError, Navigation completed but playwright returned no Response object.      Its own ty, _attempt(), _count_jsonld(), _count_product_objects(), _detect_platforms(), format_report() (+16 more)

### Community 19 - "Search TUI Screen"
Cohesion: 0.08
Nodes (41): find_header_columns(), find_match(), open_worksheet(), Any, Exception, Path, Protocol, Writing a search result onto the user's own Google Sheets wishlist.  The wishlis (+33 more)

### Community 20 - "Snapshot Writing"
Cohesion: 0.18
Nodes (22): grouped_value(), Decimal, ResultRow, Pure sorting and grouping rules for the results table.  No I/O, no Textual state, What each site charges for the product a block is about.      One entry per site, The default order: typed order, product, site, size.      The typed order comes, The order once a column has been picked: the site layer drops out.      Asking f, site_ranks() (+14 more)

### Community 21 - "Candidate Filtering"
Cohesion: 0.15
Nodes (38): BasketRefreshEvent, BasketRow, Lock, MonkeyPatch, ScanEvent, SiteResult, Any, SiteRunner (+30 more)

### Community 22 - "Basket Site Scenarios"
Cohesion: 0.24
Nodes (6): BaseHTTPRequestHandler, _Handler, _playwright_usable(), Shared pytest fixtures.  A local HTTP server used by fetch/probe tests: real req, Whether the playwright rung can actually run here, binary included.      Checkin, server_url()

### Community 23 - "Price/Size Normalization"
Cohesion: 0.08
Nodes (33): _label(), Name one basket line the way a missing-item warning has to read it., A multi-site price and stock comparison tool for perfume decants.  Includes a sh, File logging for the app's own diagnostics.  Nothing here ever writes to the con, _classify_single_separator(), format_age(), format_ml(), format_price() (+25 more)

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
Cohesion: 0.06
Nodes (52): api, ApiError, authToken(), readDetail(), request(), Window, refusalReason(), streamUrl() (+44 more)

### Community 30 - "Store Timestamp Tests"
Cohesion: 0.09
Nodes (34): CacheKey, Any, Connection, Command-line entry point.  Subcommands will be added incrementally as the projec, Scan every perfume against every site and print each site as it lands.      One, Write one site's rows in a transaction of its own.      Per site rather than per, One line per site: which site, how it went, and what it said.      The site id i, _report_line() (+26 more)

### Community 31 - "Live Profile Validation"
Cohesion: 0.09
Nodes (33): _canonical(), _covers(), _ends_with(), _index_of(), listing_filter(), _match_text(), _own_identity(), product_label() (+25 more)

### Community 32 - "Variant Extraction Fields"
Cohesion: 0.11
Nodes (18): attribute, in_stock, price, script, size_raw, type, properties, additionalProperties (+10 more)

### Community 33 - "_ResultRow"
Cohesion: 0.10
Nodes (35): parse_query(), Split one typed line into the perfumes it asks for, on " - ".      The separator, Split one typed line, "Dior Sauvage EDP", into the three identity parts.      Th, Whether a search result's own listing text is worth opening the page for.      J, split_queries(), title_could_match(), Tests for parfum_finder.matcher.  The thing being defended here is not "does it, test_a_brand_the_shop_writes_out_in_full_does_not_cost_the_match() (+27 more)

### Community 34 - "Fetch Strategy Probing"
Cohesion: 0.12
Nodes (19): Check, _count_result_cards(), _first_result_url(), _no_results_check(), _probe_layer(), _probe_other_layers(), Any, Path (+11 more)

### Community 35 - "Platform Field Mapping"
Cohesion: 0.12
Nodes (16): field_map, product_json, source, variants_path, additionalProperties, allOf, description, required (+8 more)

### Community 36 - "Shipping Config Schema"
Cohesion: 0.14
Nodes (14): free_shipping_threshold_kurus, shipping_cost_kurus, minimum, type, free_shipping_threshold_kurus, notes, shipping, shipping_cost_kurus (+6 more)

### Community 37 - "_trial"
Cohesion: 0.27
Nodes (13): apply_variant_rules(), Turn raw size rows into decant variants, dropping what is not a decant.      Thr, _row(), test_a_keyword_in_the_size_label_excludes_the_row_too(), test_a_literal_zero_price_reads_as_no_price_not_a_free_perfume(), test_a_size_at_the_threshold_is_a_bottle_whatever_it_calls_itself(), test_a_size_that_cannot_be_read_is_dropped(), test_an_uppercase_turkish_keyword_still_matches() (+5 more)

### Community 38 - "TUI Confirm Dialog"
Cohesion: 0.07
Nodes (34): FastAPI, Pressed, create_app(), HTTP/WS backend for the GUI frontend. See api/app.py for the app itself., encode_basket_refresh_event(), encode_basket_report(), encode_basket_row(), encode_result_row() (+26 more)

### Community 39 - "TUI App Shell"
Cohesion: 0.06
Nodes (16): Changed, HeaderSelected, RowSelected, ComposeResult, Any, ComposeResult, ResultRow, Row (+8 more)

### Community 40 - "Fetch Backends"
Cohesion: 0.14
Nodes (14): curl_cffi, httpx, playwright, result_item, result_title, result_url, strategy, url_template (+6 more)

### Community 41 - "HTTP Request Schema"
Cohesion: 0.14
Nodes (14): GET, POST, properties, default, enum, type, type, type (+6 more)

### Community 42 - "Fixture Fetcher (Tests)"
Cohesion: 0.12
Nodes (24): conn(), Path, Tests for parfum_finder.store: the timestamp helper and the schema.  The one har, The table's CHECK (qty > 0) would reject a bare 0, and the '-' key has to     su, Two snapshots written in the same second must resolve to the newer one.      A s, 5 ml at 125,00 TL is 25,00 TL per ml. Stored as kurus, ml as tenths., No price yet means no row, so the basket LEFT JOIN reads it as missing., A zero ml variant is a parse failure, and it must not reach the table.      If i (+16 more)

### Community 44 - "Decant Variant Rules"
Cohesion: 0.15
Nodes (18): extract_embedded_variants(), extract_jsonld_variants(), _flatten_jsonld(), Rung 1: read the page's JSON-LD as flat variant rows.      A product that declar, Turn one Product and everything under it into rows., Rung 3: read the JSON blob the page carries but does not display.      Two shape, _fixture(), Read a captured product page. (+10 more)

### Community 45 - "_ResultRow"
Cohesion: 0.17
Nodes (44): TestClient, _auth(), _client(), db_path(), _ok_result(), Any, MonkeyPatch, Path (+36 more)

### Community 46 - "Offline Validation Fixtures"
Cohesion: 0.25
Nodes (8): type, additionalProperties, type, body, request_headers, additionalProperties, description, type

### Community 47 - "JsonLdProduct"
Cohesion: 0.11
Nodes (25): BasketReport, compare_split_to_best_full(), Basket scenario evaluation. A pure function, no network access, no sqlite.  Inpu, Every site's single-site scenario, split by whether it covers everything.      A, One site's share of a split basket: what to buy there and what it costs.      `s, The cheapest basket split the search found. A heuristic, not a proof.      Every, Score a split plan against the cheapest full-coverage single site.      Only the, SplitLeg (+17 more)

### Community 48 - "._build_rows"
Cohesion: 0.20
Nodes (18): collect_prices(), _format_product(), _format_stock(), _format_trial(), _has_exact_price(), PageTrial, Decimal, Site discovery: turns a URL into a profile, with human review. Not fully automat (+10 more)

### Community 49 - "_RecordingFetcher"
Cohesion: 0.13
Nodes (15): Connection, A disabled site loses its basket column, but an enabled quiet one keeps one., NULL means the site has no free shipping tier at all, not a threshold of zero., An update aimed at a row that isn't there means the caller is out of sync., The recents list has five slots, so a repeat must not consume two.      Someone, A snapshot pointing at a variant that doesn't exist has to be rejected.      SQL, Sites come from the profiles, so an id nothing synced is a mistake., test_a_snapshot_for_an_unknown_site_is_refused() (+7 more)

### Community 50 - "Profile Age Checks"
Cohesion: 0.20
Nodes (24): format_report(), Check one site's profile against that site's saved fixtures.      Never raises f, Render the validations as the offline half of the report in APP_FLOW §6.      A, validate_offline(), _corrupted_sites_dir(), _iso_days_ago(), Any, Path (+16 more)

### Community 51 - "._refresh_table"
Cohesion: 0.14
Nodes (21): _age_of(), live_query(), _path(), profile_age_days(), datetime, Profile staleness checks. Two modes: offline (against saved fixtures) and live (, A URL's path with no trailing slash, for comparing two spellings of one page., Every site that has a profile, sorted so reports read the same way twice. (+13 more)

### Community 52 - "FetchResult"
Cohesion: 0.13
Nodes (46): BaseModel, AcceptedSearch, _add_basket_item(), _AppState, BasketAddRequest, BasketQtyRequest, The FastAPI app: a thin HTTP/WS wrapper around the Faz 1 services.  No business, _read_basket() (+38 more)

### Community 53 - "conftest.py"
Cohesion: 0.10
Nodes (31): _load_profiles(), Any, Path, _recent_searches(), _record_search(), _remove_basket_item(), _set_basket_qty(), _site_summary() (+23 more)

### Community 54 - "Endpoint Schema Fields"
Cohesion: 0.22
Nodes (9): result_item, result_title, result_url, url_template, search, additionalProperties, description, required (+1 more)

### Community 55 - "apply_variant_rules"
Cohesion: 0.14
Nodes (14): add_basket_item(), Add a size of a perfume to the basket, and return the basket_item_id.      The p, Whether an out-of-stock price counts as missing is the caller's call.      Dropp, Deleting a row that's already gone is a race between two screens, not a bug., Adding the same perfume and size twice must accumulate, not clobber.      The ba, A basket line for a perfume nobody has priced is a bug, not a state to keep., The basket screen prints brand/name/concentration straight off this row.      Or, A basket line nobody sells must still be visible via basket_lines.      basket_p (+6 more)

### Community 56 - "Request Schema Fields"
Cohesion: 0.07
Nodes (27): motion, react, react-dom, @types/react, @types/react-dom, typescript, dependencies, motion (+19 more)

### Community 57 - "_FixtureFetcher"
Cohesion: 0.14
Nodes (15): _balanced_value(), _embedded_documents(), extract_endpoint_variants(), _loads_or_skip(), Any, Rung 2: read the variant list out of a platform's JSON response.      `document`, Yield every JSON document the page hides, in document order., Parse `text` as JSON, yielding nothing when it isn't JSON.      Pages are full o (+7 more)

### Community 58 - "setup_logging"
Cohesion: 0.08
Nodes (23): DOM, DOM.Iterable, ES2022, src, vite/client, vite.config.ts, compilerOptions, isolatedModules (+15 more)

### Community 59 - "_named_profile"
Cohesion: 0.33
Nodes (6): cached_prices(), Return the latest stored price of every size of this perfume, per site.      Bra, A price nobody will scan again may not be offered as a result.      Refreshing i, Nothing on record is the state before a first search, not an error.      The sea, test_cached_prices_is_empty_for_a_perfume_nobody_scanned(), test_cached_prices_leaves_out_a_disabled_site()

### Community 60 - "._scan"
Cohesion: 0.22
Nodes (12): format_live_report(), Run one site's profile against the real site.      Same contract as offline mode, Render offline and live results side by side, as APP_FLOW §6 shows them.      Bo, validate_live(), _FakeSite, _fixture_site(), A stand-in for one live site, answering the search page then the rest.      Live, test_a_working_profile_passes_against_a_site_that_still_answers() (+4 more)

### Community 61 - "single_site_scenarios"
Cohesion: 0.38
Nodes (11): _freeze(), MonkeyPatch, Path, Tests for parfum_finder.paths: frozen vs. source path resolution.  `ensure_user_, A source run has nothing to seed: resource_dir and user_data_dir are     already, test_ensure_user_data_is_a_noop_when_not_frozen(), test_ensure_user_data_never_overwrites_an_edited_file(), test_ensure_user_data_seeds_sites_platforms_and_hooks() (+3 more)

### Community 62 - "snapshot_rows"
Cohesion: 0.23
Nodes (12): One priced size of one perfume on one site, ready to be written.      The perfum, Write a whole scan at once and return how many prices were recorded.      Every, SnapshotRow, write_snapshots(), The drop happens here so no caller can forget it.      Both the CLI and the scre, A slow site must not spread one reading across several timestamps.      Rows wri, The number reported is what landed in the history, not what was offered., Half a site's sizes updated is worse than none of them.      The basket compares (+4 more)

### Community 64 - "validate_live"
Cohesion: 0.16
Nodes (14): DiscoveryReport, _format_choice(), _format_confidence(), _format_fingerprint(), _format_fixtures(), format_report(), The template this site's profile would be based on, if any., The scored fields a person still has to confirm, in profile order.          Anyt (+6 more)

### Community 65 - "_named_profile"
Cohesion: 0.10
Nodes (35): _as_str(), _build_offer(), _build_product(), _coerce_in_stock(), _collect_offers(), _collect_variants(), _css_variant(), JsonLdOffer (+27 more)

### Community 66 - ".__call__"
Cohesion: 0.31
Nodes (7): _DeadSite, FormData, Headers, Method, Strategy, A host that cannot be reached at all., test_an_unreachable_site_is_not_reported_as_a_broken_profile()

### Community 67 - "test_cached_prices_is_empty_for_a_perfume_nobody_scanned"
Cohesion: 0.25
Nodes (8): exclude_keywords, max_size_ml, size_from, size_pattern, variant_rules, additionalProperties, required, type

### Community 68 - "field_map"
Cohesion: 0.24
Nodes (11): _flatten_defaults(), _format_defaults(), _match_platforms(), Any, Path, Every template with at least one of its markers somewhere in the page.      Case, Write one page and return where it landed plus its digest.      Saved as UTF-8 w, Render a template's defaults as one dotted key per line. (+3 more)

### Community 71 - "exclude_keywords"
Cohesion: 0.29
Nodes (7): price_history(), Row, Return one variant's past readings, newest first, capped at limit.      Empty fo, No history yet is a normal state for a variant, not an error to raise on., The identity a real scan writes must be the identity these lookups accept., test_a_scanned_perfume_can_be_read_back_by_basket_and_history(), test_price_history_is_empty_for_an_unknown_variant()

### Community 72 - "_scenario_block"
Cohesion: 0.32
Nodes (7): FieldConfidence, One field this run can fill in, with how far it can be trusted.      `field` is, Every profile field this run can put a value on, scored., Score every profile field this run can fill in, in profile order.      Only fiel, Read the extraction layer off the page, for a site no template covers.      Judg, _score_extraction(), score_fields()

### Community 73 - "Headers"
Cohesion: 0.29
Nodes (6): _choose_strategy(), Strategy, _qualifies(), The strategy the trials actually ran with., Pick the cheapest strategy that came back with real content, or None.      probe, Whether one strategy came back with a usable page.

### Community 74 - "format_age"
Cohesion: 0.29
Nodes (5): _age_line(), Every check run against one site's profile, in the order they ran.      Checks s, Whether the profile is old enough to be worth re-discovering., The age note for one site, or None when its age is unremarkable.      A profile, SiteValidation

### Community 75 - "_NoRootParser"
Cohesion: 0.29
Nodes (6): _NoRootParser, MonkeyPatch, Record every delay the engine asks for instead of serving it.      Waiting for r, Stands in for HTMLParser when a page's markup cannot be read at all.      select, slept(), test_a_search_page_with_no_root_names_its_body_size()

### Community 76 - "enum"
Cohesion: 0.33
Nodes (6): css, embedded_json, endpoint, jsonld, enum, extraction

### Community 77 - "_collect_products"
Cohesion: 0.50
Nodes (4): _collect_products(), _has_type(), Walk a parsed JSON-LD block and append every Product found, depth first.      De, Whether a node's "@type" names `name`, as a string or inside a list.      Substr

## Knowledge Gaps
- **207 isolated node(s):** `Notice`, `Block`, `TRIAL_SIZES_ML_X10`, `Verdicts`, `SORT_LABELS` (+202 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **8 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `PlaywrightNotInstalled` connect `HTTP/Browser Fetching` to `validate_live`, `Search/Basket Domain Models`, `_scenario_block`, `Search Engine Core`, `_NoRootParser`, `FieldConfidence`, `Product Extraction`, `._build_rows`, `Offline Profile Validation`, `Playwright Errors`, `FetchResult`, `Basket Site Scenarios`, `Store Timestamp Tests`?**
  _High betweenness centrality (0.032) - this node is a cross-community bridge._
- **Why does `SearchScreen` connect `TUI App Shell` to `TUI App & Screens`, `Title Matcher`, `Search/Basket Domain Models`, `Search Engine per Site`, `TUI Confirm Dialog`, `Search TUI Screen`, `FetchResult`, `Price/Size Normalization`?**
  _High betweenness centrality (0.032) - this node is a cross-community bridge._
- **Why does `SiteResult` connect `Store Timestamp Tests` to `TUI App & Screens`, `HTTP/Browser Fetching`, `Search/Basket Domain Models`, `exclude_keywords`, `Search Engine Core`, `_ResultRow`, `Offline Profile Validation`, `FetchResult`, `conftest.py`, `snapshot_rows`?**
  _High betweenness centrality (0.032) - this node is a cross-community bridge._
- **Are the 14 inferred relationships involving `SearchScreen` (e.g. with `ParfumFinderApp` and `SiteRunner`) actually correct?**
  _`SearchScreen` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Are the 10 inferred relationships involving `PerfumeQuery` (e.g. with `SheetsError` and `WishlistRow`) actually correct?**
  _`PerfumeQuery` has 10 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Notice`, `Block`, `TRIAL_SIZES_ML_X10` to the rest of the system?**
  _207 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `TUI App & Screens` be split into smaller, more focused modules?**
  _Cohesion score 0.09337992622791691 - nodes in this community are weakly interconnected._