# Graph Report - parfum-finder  (2026-08-18)

## Corpus Check
- 125 files · ~309,926 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2514 nodes · 6888 edges · 122 communities (102 shown, 20 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 429 edges (avg confidence: 0.55)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `fee81fd7`
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
- _wait_for_table
- ._apply_scan_event
- snapshot_rows
- CandidateFilter
- validate_live
- _named_profile
- extract_embedded_variants
- JsonLdProduct
- Variant Pattern A
- Project Root
- exclude_keywords
- write_snapshots
- _css_variant
- ConfirmDialog.tsx
- ResultRow
- SplitPlan
- _collect_products
- exclude_keywords
- AddButton.tsx
- write_snapshots
- run_sites
- test_connect_is_idempotent_on_an_existing_database
- DownloadProgress
- BasketScreen.tsx
- _factory
- test_paths.py
- helpers.ts
- handoff_command
- test_an_unreadable_tag_never_counts_as_an_update
- BasketRow
- ResultRow
- MonkeyPatch
- ws.ts
- Arayüz testleri
- Static
- .__init__
- _retry_after_s
- _about
- cached_prices
- recent_searches
- enum
- Static
- .get_system_commands
- .__init__
- _retry_after_s
- test_every_shipped_site_has_a_colour_that_survives_256_colours
- test_an_unreadable_tag_never_counts_as_an_update
- Decimal
- Node
- FormData
- Headers
- Method
- Strategy
- BasketRow
- ResultRow
- datetime
- Row
- Exception
- Event

## God Nodes (most connected - your core abstractions)
1. `_profile()` - 68 edges
2. `SiteResult` - 67 edges
3. `search_site()` - 65 edges
4. `SearchScreen` - 64 edges
5. `connect()` - 58 edges
6. `discover()` - 54 edges
7. `Fetcher` - 53 edges
8. `_write_profile()` - 50 edges
9. `FetchResult` - 49 edges
10. `match_title()` - 49 edges

## Surprising Connections (you probably didn't know these)
- `Shipping Non-linearity Rationale (why cheapest-per-item is wrong)` --semantically_similar_to--> `sites/ Site Profile Directory`  [INFERRED] [semantically similar]
  ARCHITECTURE.md → sites/README.md
- `Variant Pattern B (dropdown + AJAX price)` --semantically_similar_to--> `Variant Selector Detector Fix (WooCommerce 'variation' vs 'variant')`  [INFERRED] [semantically similar]
  ARCHITECTURE.md → docs/discovery-report.md
- `_NoRootParser` --uses--> `ExtractionFailed`  [INFERRED]
  tests/test_engine.py → src/parfum_finder/engine.py
- `test_a_product_page_with_no_root_names_its_body_size()` --indirect_call--> `ExtractionFailed`  [INFERRED]
  tests/test_engine.py → src/parfum_finder/engine.py
- `test_a_search_page_with_no_root_names_its_body_size()` --indirect_call--> `ExtractionFailed`  [INFERRED]
  tests/test_engine.py → src/parfum_finder/engine.py

## Import Cycles
- 3-file cycle: `src/parfum_finder/__init__.py -> src/parfum_finder/cli.py -> src/parfum_finder/validate.py -> src/parfum_finder/__init__.py`
- 3-file cycle: `src/parfum_finder/__init__.py -> src/parfum_finder/cli.py -> src/parfum_finder/profiles.py -> src/parfum_finder/__init__.py`
- 3-file cycle: `src/parfum_finder/__init__.py -> src/parfum_finder/cli.py -> src/parfum_finder/logging_setup.py -> src/parfum_finder/__init__.py`
- 4-file cycle: `src/parfum_finder/__init__.py -> src/parfum_finder/cli.py -> src/parfum_finder/validate.py -> src/parfum_finder/profiles.py -> src/parfum_finder/__init__.py`
- 4-file cycle: `src/parfum_finder/__init__.py -> src/parfum_finder/cli.py -> src/parfum_finder/engine.py -> src/parfum_finder/profiles.py -> src/parfum_finder/__init__.py`
- 4-file cycle: `src/parfum_finder/__init__.py -> src/parfum_finder/cli.py -> src/parfum_finder/discover.py -> src/parfum_finder/profiles.py -> src/parfum_finder/__init__.py`
- 5-file cycle: `src/parfum_finder/__init__.py -> src/parfum_finder/cli.py -> src/parfum_finder/validate.py -> src/parfum_finder/engine.py -> src/parfum_finder/profiles.py -> src/parfum_finder/__init__.py`
- 5-file cycle: `src/parfum_finder/__init__.py -> src/parfum_finder/cli.py -> src/parfum_finder/store.py -> src/parfum_finder/engine.py -> src/parfum_finder/profiles.py -> src/parfum_finder/__init__.py`

## Hyperedges (group relationships)
- **Sites Implementing Variant Pattern C (embedded JSON)** — docs_discovery_report_venco_site, docs_discovery_report_decantall_site, docs_discovery_report_luxurydekant_site, docs_discovery_report_ruxangroup_site, architecture_md_variant_pattern_c [EXTRACTED 1.00]
- **İdeasoft Platform Sites and Endpoint** — docs_discovery_report_dekantparfum_site, docs_discovery_report_dekantdoktoru_site, docs_discovery_report_ideasoft_related_options_endpoint, platforms_readme_ideasoft_json [EXTRACTED 1.00]
- **discover Command Output Artifacts (profile + fixtures + CI validation)** — architecture_md_discover_flow, sites_readme_sites_dir, fixtures_readme_fixtures_dir, github_workflows_ci_validate_profiles_step, architecture_md_validate_command [INFERRED 0.85]

## Communities (122 total, 20 thin omitted)

### Community 0 - "TUI App & Screens"
Cohesion: 0.09
Nodes (100): The Textual-based terminal UI: search and basket screens., _app(), _basket(), _cells(), _days_ago(), _leg(), _ok(), _open_basket() (+92 more)

### Community 1 - "Site Profiles & Templates"
Cohesion: 0.06
Nodes (84): _check_hook_kinds(), deep_merge(), _load_json(), load_platform_template(), load_platform_templates(), load_site_hooks(), load_site_profile(), Any (+76 more)

### Community 2 - "Title Matcher"
Cohesion: 0.18
Nodes (19): FastAPI, create_app(), HTTP/WS backend for the GUI frontend. See api/app.py for the app itself., encode_basket_refresh_event(), encode_basket_report(), encode_basket_row(), encode_result_row(), encode_scan_event() (+11 more)

### Community 3 - "HTTP/Browser Fetching"
Cohesion: 0.13
Nodes (31): Event, browser_session(), fetch(), Fetch one URL using exactly the given strategy.      `method`/`data` exist for t, Yield a fetcher that keeps one browser for every playwright page it reads., Strategy, test_the_no_results_page_would_otherwise_read_as_suspect(), _fake_launch() (+23 more)

### Community 4 - "Search/Basket Domain Models"
Cohesion: 0.09
Nodes (90): ParfumFinderApp, Root app: pushes the search screen on mount., _app(), _counting_runner(), _days_ago(), _ok_result(), _painted_in_basket(), _per_query_runner() (+82 more)

### Community 5 - "Search Engine per Site"
Cohesion: 0.17
Nodes (13): _load_profiles(), Any, Path, _recent_searches(), _record_search(), _remove_basket_item(), _set_basket_qty(), _site_summary() (+5 more)

### Community 6 - "Platform Discovery Flow"
Cohesion: 0.15
Nodes (59): PlatformChooser, _ask_chooser(), discover(), Put the question only when there is one, and hold the answer to it.      An answ, Measure the strategies a site needs, then read its JSON-LD with the winner., _attempt(), _fake_probe(), Any (+51 more)

### Community 7 - "CLI Entry Points"
Cohesion: 0.15
Nodes (41): CaptureFixture, ask_which_platform(), main(), Path, Scan every site for the perfumes named, store what came back, print it.      One, Ask at the terminal which of several matching templates to apply.      Asked whi, run_search(), _answers() (+33 more)

### Community 8 - "Architecture Rationale Docs"
Cohesion: 0.05
Nodes (53): basket Subset Enumeration + Local Improvement Algorithm, basket Optimizer (optimize function), Clone/Original Distinction (KLON ← <orijinal>), discover Discovery Flow, engine Concurrency Model (parallel sites, serial within site), Extraction Ladder (jsonld/endpoint/embedded/css), Fail-loud / status=suspect policy, hooks/<id>.py Escape Hatch (+45 more)

### Community 9 - "Search Engine Core"
Cohesion: 0.08
Nodes (54): CacheKey, Node, SiteHooks, _check_variant_control(), _fetch_page(), _headers(), _is_excluded(), _jitter_s() (+46 more)

### Community 10 - "Basket Optimizer Core"
Cohesion: 0.11
Nodes (46): BasketRow, _score_basket(), basket_inputs(), BasketItem, optimize(), BasketRow, Prices, Score one site against the basket, or against a subset of it.      `item_ids` is (+38 more)

### Community 11 - "Basket Store & Pricing"
Cohesion: 0.17
Nodes (23): ExtractionFailed, RuntimeError, A page answered but gave up nothing, where something was expected.      This is, Run one query against one site and read every hit's sizes.      Everything site-, search_site(), Path, Give the test profile's site id a hook file. The id is what binds them., test_a_before_search_that_returns_no_query_is_refused() (+15 more)

### Community 12 - "JSON-LD Product Extraction"
Cohesion: 0.15
Nodes (30): extract_jsonld_products(), Read every JSON-LD Product declared on the page, in document order.      A block, _one_product_html(), Tests for parfum_finder.extract.  Every case here is a shape a real store actual, Wrap a JSON-LD product body in a page, for the one-field-at-a-time cases., test_a_broken_block_does_not_lose_the_valid_one(), test_availability_spellings_all_land_in_the_same_bucket(), test_boolean_values_are_never_read_as_price_or_text() (+22 more)

### Community 13 - "Basket TUI Screen"
Cohesion: 0.08
Nodes (47): PyInstaller entry point for the packaged desktop app.  Kept outside src/parfum_f, _close_window_when_asked(), _hold_app_mutex(), _kill_children_with_app(), main(), _ping(), Event, Path (+39 more)

### Community 14 - "Platform Schema"
Cohesion: 0.06
Nodes (31): any, defaults, fingerprint, additionalProperties, items, minItems, type, description (+23 more)

### Community 15 - "Product Extraction"
Cohesion: 0.11
Nodes (20): Check, _first_result_url(), _LayerUnavailable, _no_results_check(), _probe_layer(), _probe_other_layers(), Any, Exception (+12 more)

### Community 16 - "Schema Field Patterns"
Cohesion: 0.06
Nodes (33): format, pattern, type, pattern, type, default, type, pattern (+25 more)

### Community 17 - "Offline Profile Validation"
Cohesion: 0.10
Nodes (55): Exception, Run one site and classify what came back instead of raising.      It is also whe, run_site(), FetchResult, One fetched page, uniform regardless of which strategy produced it., _counting_fetcher(), _profile(), Tests for the profile-driven search in parfum_finder.engine.  What these defend (+47 more)

### Community 18 - "Playwright Errors"
Cohesion: 0.14
Nodes (22): HTMLParser, _attempt(), _count_jsonld(), _count_product_objects(), _detect_platforms(), format_report(), _label_platform(), _one_line() (+14 more)

### Community 19 - "Search TUI Screen"
Cohesion: 0.07
Nodes (44): A multi-site price and stock comparison tool for perfume decants.  Includes a sh, File logging for the app's own diagnostics.  Nothing here ever writes to the con, find_header_columns(), find_match(), open_worksheet(), Any, Exception, Path (+36 more)

### Community 20 - "Snapshot Writing"
Cohesion: 0.18
Nodes (22): grouped_value(), Decimal, ResultRow, Pure sorting and grouping rules for the results table.  No I/O, no Textual state, What each site charges for the product a block is about.      One entry per site, The default order: typed order, product, site, size.      The typed order comes, The order once a column has been picked: the site layer drops out.      Asking f, site_ranks() (+14 more)

### Community 21 - "Candidate Filtering"
Cohesion: 0.14
Nodes (44): BasketRefreshEvent, BasketRow, Lock, ScanEvent, Any, Path, The scan is over. `error_count` is every failure any event above     reported, e, A site's display name, with a badge when its profile is old enough     to be wor (+36 more)

### Community 22 - "Basket Site Scenarios"
Cohesion: 0.21
Nodes (11): _count_result_cards(), Run one site's profile against the real site.      Same contract as offline mode, How many result rows the profile's own selectors find on a search page., validate_live(), _FakeSite, _fixture_site(), A stand-in for one live site, answering the search page then the rest.      Live, test_a_broken_layer_reports_which_other_layer_could_take_over() (+3 more)

### Community 23 - "Price/Size Normalization"
Cohesion: 0.09
Nodes (33): BasketReport, compare_split_to_best_full(), Basket scenario evaluation. A pure function, no network access, no sqlite.  Inpu, Every site's single-site scenario, split by whether it covers everything.      A, One site's share of a split basket: what to buy there and what it costs.      `s, The cheapest basket split the search found. A heuristic, not a proof.      Every, Score a split plan against the cheapest full-coverage single site.      Only the, What it would cost to buy some or all of the basket from one site.      `covered (+25 more)

### Community 24 - "JSON Schema Primitives"
Cohesion: 0.11
Nodes (25): integer, null, string, properties, type, type, type, type (+17 more)

### Community 25 - "SQLite Store"
Cohesion: 0.21
Nodes (15): probe(), Fetch `url` with every strategy and report diagnostics for each.      timeout_s, MonkeyPatch, Tests for parfum_finder.probe.  probe() always tries all three strategies -- the, test_probe_counts_jsonld_product_and_platform_signature(), test_probe_counts_product_across_jsonld_root_shapes(), test_probe_counts_product_markup_without_any_jsonld(), test_probe_counts_products_nested_below_the_top_level() (+7 more)

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
Cohesion: 0.13
Nodes (16): AddButton(), Badge(), BadgeKind, ConfirmDialog(), ScanStatus(), VerdictAddButton(), basketKey(), Block (+8 more)

### Community 30 - "Store Timestamp Tests"
Cohesion: 0.13
Nodes (11): RecentSearch, DEFAULT_CONFIG, EMPTY_BASKET, FakeWebSocket, NO_UPDATE, RecordedRequest, Reply, Route (+3 more)

### Community 31 - "Live Profile Validation"
Cohesion: 0.10
Nodes (31): Pattern, _brand_pattern(), _canonical(), _canonical_brands(), _covers(), _ends_with(), _index_of(), listing_filter() (+23 more)

### Community 32 - "Variant Extraction Fields"
Cohesion: 0.11
Nodes (18): attribute, in_stock, price, script, size_raw, type, properties, additionalProperties (+10 more)

### Community 33 - "_ResultRow"
Cohesion: 0.09
Nodes (59): Match, match_title(), parse_query(), PerfumeQuery, The perfume being looked for, split into its three identity parts.      `concent, One site title judged against the query.      `concentration` is what the title, Split one typed line, "Dior Sauvage EDP", into the three identity parts.      Th, Judge one site title against a query, or None if it is not that perfume.      No (+51 more)

### Community 34 - "Fetch Strategy Probing"
Cohesion: 0.26
Nodes (7): _FixtureFetcher, FormData, Headers, Method, Strategy, Serves one site's saved capture in place of the network.      Only three kinds o, The one real result card that led to the captured product page.          Cut out

### Community 35 - "Platform Field Mapping"
Cohesion: 0.12
Nodes (16): field_map, product_json, source, variants_path, additionalProperties, allOf, description, required (+8 more)

### Community 36 - "Shipping Config Schema"
Cohesion: 0.14
Nodes (14): free_shipping_threshold_kurus, shipping_cost_kurus, minimum, type, free_shipping_threshold_kurus, notes, shipping, shipping_cost_kurus (+6 more)

### Community 37 - "_trial"
Cohesion: 0.17
Nodes (19): _classify_single_separator(), format_ml(), _parse_number(), parse_price(), parse_size_ml(), Decimal, Number parsing and formatting for prices and volumes, plus text folding.  This i, Decide whether a lone separator marks a fraction or a thousands group.      Retu (+11 more)

### Community 38 - "TUI Confirm Dialog"
Cohesion: 0.11
Nodes (50): BaseModel, AcceptedSearch, _add_basket_item(), _AppState, BasketAddRequest, BasketQtyRequest, The FastAPI app: a thin HTTP/WS wrapper around the Faz 1 services.  No business, _read_basket() (+42 more)

### Community 39 - "TUI App Shell"
Cohesion: 0.14
Nodes (6): Changed, Close out a submit that named no perfume anyone could look for., Show what storage already knows, then go to the shops for the rest.          `fo, Say a perfume came off the record instead of off the shops.          Without thi, Empty the table for a new scan.          The columns are the same every time now, Submitted

### Community 40 - "Fetch Backends"
Cohesion: 0.14
Nodes (14): curl_cffi, httpx, playwright, result_item, result_title, result_url, strategy, url_template (+6 more)

### Community 41 - "HTTP Request Schema"
Cohesion: 0.14
Nodes (14): GET, POST, properties, default, enum, type, type, type (+6 more)

### Community 42 - "Fixture Fetcher (Tests)"
Cohesion: 0.15
Nodes (18): check_enabled(), check_for_update(), _installer_asset(), is_newer(), _no_update(), _pad(), parse_version(), Any (+10 more)

### Community 43 - "FieldConfidence"
Cohesion: 0.14
Nodes (11): PlaywrightNoResponse, PlaywrightNotInstalled, RuntimeError, The "playwright" strategy was requested but cannot run at all.      Covers both, Navigation completed but playwright returned no Response object.      Its own ty, _FakeBrowser, _FakePage, Any (+3 more)

### Community 44 - "Decant Variant Rules"
Cohesion: 0.12
Nodes (19): readDetail(), request(), Window, UpdateDialog(), AcceptedSearch, BasketRefreshEvent, BasketReport, BestCombination (+11 more)

### Community 45 - "_ResultRow"
Cohesion: 0.14
Nodes (51): TestClient, _auth(), _client(), db_path(), _ok_result(), Any, MonkeyPatch, Path (+43 more)

### Community 46 - "Offline Validation Fixtures"
Cohesion: 0.25
Nodes (8): type, additionalProperties, type, body, request_headers, additionalProperties, description, type

### Community 47 - "JsonLdProduct"
Cohesion: 0.14
Nodes (10): BasketResponse, basket(), basketRow(), resultRow(), scenario(), splitCombination(), compile(), FakeServer (+2 more)

### Community 48 - "._build_rows"
Cohesion: 0.07
Nodes (51): _choose_strategy(), collect_prices(), DiscoveryReport, FieldConfidence, _flatten_defaults(), _format_choice(), _format_confidence(), _format_defaults() (+43 more)

### Community 49 - "_RecordingFetcher"
Cohesion: 0.09
Nodes (37): add_basket_item(), Add a size of a perfume to the basket, and return the basket_item_id.      The p, Connection, Two lines added within the same second must still read back the same way twice., A basket line nobody sells must still be visible via basket_lines.      basket_p, A stale reading must never outrank the one taken after it.      latest_prices al, A 10 ml listing must never fill a basket line asking for 5 ml.      The matrix j, Whether an out-of-stock price counts as missing is the caller's call.      Dropp (+29 more)

### Community 50 - "Profile Age Checks"
Cohesion: 0.15
Nodes (32): format_live_report(), format_report(), Check one site's profile against that site's saved fixtures.      Never raises f, Validate every site, or just the ones named.      Serial rather than concurrent:, Render the validations as the offline half of the report in APP_FLOW §6.      A, Render offline and live results side by side, as APP_FLOW §6 shows them.      Bo, validate_all_offline(), validate_offline() (+24 more)

### Community 51 - "._refresh_table"
Cohesion: 0.21
Nodes (17): Decimal, apply_variant_rules(), Turn raw size rows into decant variants, dropping what is not a decant.      Thr, Convert a price in lira to whole kuruş.      Integers all the way, never a float, _to_kurus(), RawVariant, _row(), test_a_keyword_in_the_size_label_excludes_the_row_too() (+9 more)

### Community 52 - "FetchResult"
Cohesion: 0.07
Nodes (34): ProductCandidate, One hit on a search results page, before its product page is opened.      `raw_t, A candidate together with the decant sizes its product page offers., SearchHit, PerfumeQuery, Turn one site's hits into the rows write_snapshots is ready to store.      Share, snapshot_rows(), Just enough of an httpx streaming response to be downloaded from. (+26 more)

### Community 53 - "conftest.py"
Cohesion: 0.17
Nodes (16): extract_embedded_variants(), extract_jsonld_variants(), Rung 1: read the page's JSON-LD as flat variant rows.      A product that declar, Rung 3: read the JSON blob the page carries but does not display.      Two shape, _fixture(), Read a captured product page., test_embedded_attribute_reads_a_second_site_with_the_same_shape(), test_embedded_attribute_reads_the_woocommerce_variation_table() (+8 more)

### Community 54 - "Endpoint Schema Fields"
Cohesion: 0.22
Nodes (9): result_item, result_title, result_url, url_template, search, additionalProperties, description, required (+1 more)

### Community 55 - "apply_variant_rules"
Cohesion: 0.09
Nodes (20): product_label(), Split one typed line into the perfumes it asks for, on " - ".      The separator, Reduce a site's own title to the product it is about, spelled one way.      What, Split a title into what the bottle is and what it says it imitates.      The sec, _split_clone_reference(), split_queries(), test_a_clone_is_labelled_by_the_bottle_it_is_and_not_what_it_imitates(), test_a_hyphen_inside_a_brand_name_does_not_split_the_search() (+12 more)

### Community 56 - "Request Schema Fields"
Cohesion: 0.04
Nodes (45): jsdom, motion, @playwright/test, react, react-dom, @testing-library/jest-dom, @testing-library/react, @testing-library/user-event (+37 more)

### Community 57 - "_FixtureFetcher"
Cohesion: 0.12
Nodes (11): _Change, BasketPriceExcluded, BasketRowFinished, One (site, row) pair the refresh could not price, whether the site     broke or, One (site, row) refresh attempt is done, whatever it ended in.      Always the l, BasketScreen, BasketRow, Path (+3 more)

### Community 58 - "setup_logging"
Cohesion: 0.07
Nodes (27): DOM, DOM.Iterable, e2e, ES2022, playwright.config.ts, src, tests, vite/client (+19 more)

### Community 59 - "_named_profile"
Cohesion: 0.18
Nodes (20): FormData, Headers, Method, _close_browser(), _close_session_browser(), _fetch_curl_cffi(), _fetch_httpx(), _fetch_playwright() (+12 more)

### Community 60 - "_wait_for_table"
Cohesion: 0.29
Nodes (12): fetch_latest_release(), En son yayımlanmış sürüm, ya da ulaşılamadıysa None.      /releases/latest tasla, _enable_checks(), _patch_get(), MonkeyPatch, Tests for parfum_finder.updater: the version compare, the release read, and the, The .exe is what gets downloaded, whatever else is attached.      Releases carry, _release_payload() (+4 more)

### Community 61 - "._apply_scan_event"
Cohesion: 0.13
Nodes (17): datetime, conn(), Path, Tests for parfum_finder.store: the timestamp helper and the schema.  The one har, A disabled site loses its basket column, but an enabled quiet one keeps one., NULL means the site has no free shipping tier at all, not a threshold of zero., An update aimed at a row that isn't there means the caller is out of sync., A snapshot pointing at a variant that doesn't exist has to be rejected.      SQL (+9 more)

### Community 62 - "snapshot_rows"
Cohesion: 0.11
Nodes (31): The drop happens here so no caller can forget it.      Both the CLI and the scre, One call has to leave a row the search table can read straight off.      The cal, The old price has to survive, and it must not become a second variant.      Appe, first_seen is what says how long a shop has carried a size., The title and URL are information, not identity.      A shop that rewords a list, EDT and EDP are different products at different prices.      Folding them into o, A sold-out size often shows no price at all, and 0 would mean free.      Writing, The column is 0/1, so the tri-state has to land somewhere on purpose.      Unkno (+23 more)

### Community 64 - "validate_live"
Cohesion: 0.18
Nodes (16): _age_of(), live_query(), _path(), profile_age_days(), datetime, Profile staleness checks. Two modes: offline (against saved fixtures) and live (, A URL's path with no trailing slash, for comparing two spellings of one page., Every site that has a profile, sorted so reports read the same way twice. (+8 more)

### Community 65 - "_named_profile"
Cohesion: 0.25
Nodes (11): _css_variant(), _parse_selector(), Node, Read one variant's fields out of its container node., Run one "<css>::text" / "<css>::attr(name)" selector inside a node.      The nod, Run one "<css>::text" / "<css>::attr(name)" selector, reading every match., Split a "<css>::text" / "<css>::attr(name)" selector into its two parts., Read the attribute or text of one already-selected node, or None. (+3 more)

### Community 67 - "extract_embedded_variants"
Cohesion: 0.14
Nodes (4): HeaderSelected, Any, The initial screen: search bar, streaming results table, notices, footer., SearchScreen

### Community 68 - "JsonLdProduct"
Cohesion: 0.18
Nodes (4): _FakeClient, _FakeStreamResponse, Any, Exception

### Community 71 - "exclude_keywords"
Cohesion: 0.22
Nodes (9): Row, price_history(), Return one variant's past readings, newest first, capped at limit.      Empty fo, The trend panel reads row 0 as the latest reading, so order is the point.      A, No history yet is a normal state for a variant, not an error to raise on., The identity a real scan writes must be the identity these lookups accept., test_a_scanned_perfume_can_be_read_back_by_basket_and_history(), test_price_history_is_empty_for_an_unknown_variant() (+1 more)

### Community 72 - "write_snapshots"
Cohesion: 0.50
Nodes (3): The template this site's profile would be based on, if any., Which of the matching templates gets applied, or None for none of them.      One, _resolve_platform()

### Community 73 - "_css_variant"
Cohesion: 0.29
Nodes (5): _age_line(), Every check run against one site's profile, in the order they ran.      Checks s, Whether the profile is old enough to be worth re-discovering., The age note for one site, or None when its age is unremarkable.      A profile, SiteValidation

### Community 74 - "ConfirmDialog.tsx"
Cohesion: 0.14
Nodes (6): RowSelected, format_age(), Turn a price age in days into the words the age column shows., ResultRow, Row, test_format_age_reads_as_words_not_a_timestamp()

### Community 75 - "ResultRow"
Cohesion: 0.11
Nodes (30): _as_str(), _build_offer(), _build_product(), _coerce_in_stock(), _collect_offers(), _collect_products(), _collect_variants(), _has_type() (+22 more)

### Community 76 - "SplitPlan"
Cohesion: 0.18
Nodes (11): _balanced_value(), _embedded_documents(), extract_css_variants(), _loads_or_skip(), Any, Rung 4: read the rendered markup with selectors. Last resort.      `config["vari, Yield every JSON document the page hides, in document order., Parse `text` as JSON, yielding nothing when it isn't JSON.      Pages are full o (+3 more)

### Community 77 - "_collect_products"
Cohesion: 0.21
Nodes (12): _named_profile(), Any, The real fetcher, with a list of every URL it was asked for., A profile whose search page lists two houses' bottles, as shops do., test_a_broken_profile_is_still_suspect_when_no_title_looked_right(), test_a_listing_from_another_house_costs_no_product_request(), test_a_scan_says_how_many_listings_it_skipped(), test_one_product_listed_under_two_searches_is_read_once() (+4 more)

### Community 78 - "exclude_keywords"
Cohesion: 0.31
Nodes (7): _DeadSite, FormData, Headers, Method, Strategy, A host that cannot be reached at all., test_an_unreachable_site_is_not_reported_as_a_broken_profile()

### Community 79 - "AddButton.tsx"
Cohesion: 0.50
Nodes (4): One search line, then the same line with the brand written the other ways., search_spellings(), test_a_brand_nobody_abbreviates_is_asked_for_once(), test_the_typed_spelling_is_asked_first_and_the_rest_only_follow()

### Community 80 - "write_snapshots"
Cohesion: 0.11
Nodes (31): Any, Connection, PerfumeQuery, Command-line entry point.  Subcommands will be added incrementally as the projec, Scan every perfume against every site and print each site as it lands.      One, Write one site's rows in a transaction of its own.      Per site rather than per, One line per site: which site, how it went, and what it said.      The site id i, _report_line() (+23 more)

### Community 81 - "run_sites"
Cohesion: 0.12
Nodes (31): Pressed, What one site had to say about one query, and how much to trust it.      Four st, One site's pacing state, for as long as whoever holds it says.      The gate and, SitePace, SiteResult, BasketRefreshFinished, BasketRefreshStarted, BasketWriteFailed (+23 more)

### Community 82 - "test_connect_is_idempotent_on_an_existing_database"
Cohesion: 0.18
Nodes (9): BaseHTTPRequestHandler, _Handler, _playwright_usable(), MonkeyPatch, Shared pytest fixtures.  A local HTTP server used by fetch/probe tests: real req, Whether the playwright rung can actually run here, binary included.      Checkin, Record every delay the engine asks for instead of serving it.      Waiting for r, server_url() (+1 more)

### Community 83 - "DownloadProgress"
Cohesion: 0.22
Nodes (4): Client, DownloadProgress, İndirmeyi başlatır. Zaten çalışıyorsa None., state: idle | downloading | ready | installing | error.

### Community 84 - "BasketScreen.tsx"
Cohesion: 0.26
Nodes (11): ProgressBar(), formatAge(), formatMl(), formatPerMl(), formatPrice(), formatPriceWhole(), BasketScreen(), cheapestSite() (+3 more)

### Community 85 - "_factory"
Cohesion: 0.33
Nodes (10): _factory(), Path, An error state is what turns the button back on with a reason.      Falling back, Nothing is spawned unless a complete file is on disk.      Running a half-writte, test_a_failed_download_says_so_instead_of_going_quiet(), test_a_second_download_is_refused_while_one_runs(), test_download_writes_the_installer_and_reports_ready(), test_install_hands_the_downloaded_file_over() (+2 more)

### Community 86 - "test_paths.py"
Cohesion: 0.38
Nodes (11): _freeze(), MonkeyPatch, Path, Tests for parfum_finder.paths: frozen vs. source path resolution.  `ensure_user_, A source run has nothing to seed: resource_dir and user_data_dir are     already, test_ensure_user_data_is_a_noop_when_not_frozen(), test_ensure_user_data_never_overwrites_an_edited_file(), test_ensure_user_data_seeds_sites_platforms_and_hooks() (+3 more)

### Community 87 - "helpers.ts"
Cohesion: 0.47
Nodes (7): addFirstRow(), authToken(), clearBasket(), openApp(), search(), searchButton(), tab()

### Community 88 - "handoff_command"
Cohesion: 0.29
Nodes (8): handoff_command(), launch_installer(), Path, Kurulumu biz kapandıktan sonra çalıştıran, sonra uygulamayı geri açan     cmd.ex, Üç şey de doğru olmadan güncelleme sessizce başarısız olur.      Bekleme olmazsa, Uygulama kapanınca kurulum zincirinin de ölmemesi buna bağlı.      gui.py, playw, test_the_handoff_breaks_out_of_the_apps_job_object(), test_the_handoff_waits_before_installing_and_reopens_the_app()

### Community 89 - "test_an_unreadable_tag_never_counts_as_an_update"
Cohesion: 0.20
Nodes (11): api, ApiError, App(), Toast, View, root, daysSince(), SearchScreen() (+3 more)

### Community 90 - "BasketRow"
Cohesion: 0.18
Nodes (12): extract_endpoint_variants(), _flatten_jsonld(), Turn one Product and everything under it into rows., Rung 2: read the variant list out of a platform's JSON response.      `document`, Read variant rows out of a parsed JSON document.      Shared by the endpoint and, Follow a dotted path into parsed JSON, e.g. "data.options.0.price".      A segme, One buyable size of one product, exactly as the page or feed states it.      Thi, RawVariant (+4 more)

### Community 91 - "ResultRow"
Cohesion: 0.31
Nodes (9): Path, Attach the rotating file handler and return where it writes.      Safe to call m, setup_logging(), Path, The file logger's two promises: it writes to the file, and it stays silent.  Bot, _teardown(), test_an_error_lands_in_the_given_file(), test_setting_up_twice_does_not_double_the_lines() (+1 more)

### Community 92 - "MonkeyPatch"
Cohesion: 0.33
Nodes (8): _fake_runner(), main(), _matching_product(), _profile(), Any, The backend playwright drives: the real app, with the shops stubbed out.  Everyt, Which catalogue product a typed query is about, by its leading words.      Delib, A profile that passes schema validation and is never actually fetched.

### Community 93 - "ws.ts"
Cohesion: 0.67
Nodes (4): authToken(), refusalReason(), streamUrl(), useEventStream()

### Community 94 - "Arayüz testleri"
Cohesion: 0.40
Nodes (4): Arayüz testleri, jsdom katmanı (`tests/`), Ne test edilmiyor, Tarayıcı katmanı (`e2e/`)

### Community 95 - "Static"
Cohesion: 0.14
Nodes (16): Collection, ResultRow, build_basket_rows(), _label(), Name one basket line the way a missing-item warning has to read it., Turn basket lines and their site prices into what the table shows.      Out of s, _cached_result_row(), Turn one stored price back into the row the table shows.      Everything the tab (+8 more)

### Community 96 - ".__init__"
Cohesion: 0.18
Nodes (11): CandidateFilter, _candidates_to_open(), Path, Run every site against one query, all at once, and report each separately., Narrow the search results down to the pages worth a request.      The first one, run_sites(), test_a_dead_site_does_not_take_the_others_down(), test_a_profile_that_breaks_on_setup_is_contained_too() (+3 more)

### Community 97 - "_retry_after_s"
Cohesion: 0.25
Nodes (8): exclude_keywords, max_size_ml, size_from, size_pattern, variant_rules, additionalProperties, required, type

### Community 98 - "_about"
Cohesion: 0.29
Nodes (7): _check_empty_search(), Fail when a search yielded no rows off a page that plainly lists products., _NoRootParser, MonkeyPatch, Stands in for HTMLParser when a page's markup cannot be read at all.      select, test_a_product_page_with_no_root_names_its_body_size(), test_a_search_page_with_no_root_names_its_body_size()

### Community 99 - "cached_prices"
Cohesion: 0.25
Nodes (8): cached_prices(), Return the latest stored price of every size of this perfume, per site.      Bra, A search that named no concentration is asking for all of them.      "" means "a, A price nobody will scan again may not be offered as a result.      Refreshing i, Nothing on record is the state before a first search, not an error.      The sea, test_cached_prices_is_empty_for_a_perfume_nobody_scanned(), test_cached_prices_leaves_out_a_disabled_site(), test_cached_prices_without_a_concentration_returns_every_one()

### Community 102 - "recent_searches"
Cohesion: 0.33
Nodes (7): Remember a query line so the search screen can offer it again.      Re-running t, The most recently run query lines, newest first, as (text, searched_at)., recent_searches(), record_search(), The recents list has five slots, so a repeat must not consume two.      Someone, test_recent_searches_stops_at_the_limit(), test_rerunning_a_search_moves_it_up_instead_of_adding_a_second_copy()

### Community 103 - "enum"
Cohesion: 0.33
Nodes (6): css, embedded_json, endpoint, jsonld, enum, extraction

### Community 104 - "Static"
Cohesion: 0.40
Nodes (3): ComposeResult, ComposeResult, Static

## Knowledge Gaps
- **224 isolated node(s):** `parfum-finder`, `$schema`, `$id`, `title`, `description` (+219 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **20 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `PlaywrightNotInstalled` connect `FieldConfidence` to `_about`, `TUI Confirm Dialog`, `Search Engine Core`, `Basket Store & Pricing`, `._build_rows`, `run_sites`, `write_snapshots`, `Playwright Errors`, `FetchResult`, `test_connect_is_idempotent_on_an_existing_database`, `Offline Profile Validation`, `SQLite Store`, `_named_profile`?**
  _High betweenness centrality (0.048) - this node is a cross-community bridge._
- **Why does `SearchScreen` connect `extract_embedded_variants` to `TUI App & Screens`, `_ResultRow`, `Search/Basket Domain Models`, `TUI Confirm Dialog`, `TUI App Shell`, `Static`, `ConfirmDialog.tsx`, `.__init__`, `write_snapshots`, `run_sites`, `Search TUI Screen`, `_FixtureFetcher`?**
  _High betweenness centrality (0.031) - this node is a cross-community bridge._
- **Why does `SiteRunner` connect `TUI Confirm Dialog` to `Title Matcher`, `extract_embedded_variants`, `Search Engine Core`, `.__init__`, `FieldConfidence`, `_ResultRow`, `run_sites`, `Offline Profile Validation`, `Search TUI Screen`, `FetchResult`, `Candidate Filtering`, `Price/Size Normalization`, `_FixtureFetcher`?**
  _High betweenness centrality (0.026) - this node is a cross-community bridge._
- **Are the 23 inferred relationships involving `SiteResult` (e.g. with `Fetcher` and `FetchResult`) actually correct?**
  _`SiteResult` has 23 INFERRED edges - model-reasoned connections that need verification._
- **Are the 14 inferred relationships involving `SearchScreen` (e.g. with `ParfumFinderApp` and `SiteRunner`) actually correct?**
  _`SearchScreen` has 14 INFERRED edges - model-reasoned connections that need verification._
- **What connects `parfum-finder`, `$schema`, `$id` to the rest of the system?**
  _224 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `TUI App & Screens` be split into smaller, more focused modules?**
  _Cohesion score 0.09337992622791691 - nodes in this community are weakly interconnected._