# Graph Report - parfum-finder  (2026-08-22)

## Corpus Check
- 130 files · ~311,415 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2510 nodes · 7102 edges · 92 communities (87 shown, 5 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 496 edges (avg confidence: 0.55)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `3f52820b`
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
- AddButton.tsx
- run_sites
- test_connect_is_idempotent_on_an_existing_database
- DownloadProgress
- BasketScreen.tsx
- _factory
- ._scan
- helpers.ts
- handoff_command
- Arayüz testleri
- test_paths.py
- cached_prices

## God Nodes (most connected - your core abstractions)
1. `SiteResult` - 69 edges
2. `PerfumeQuery` - 69 edges
3. `_profile()` - 68 edges
4. `search_site()` - 66 edges
5. `SearchScreen` - 64 edges
6. `connect()` - 58 edges
7. `discover()` - 56 edges
8. `Fetcher` - 53 edges
9. `match_title()` - 51 edges
10. `_write_profile()` - 50 edges

## Surprising Connections (you probably didn't know these)
- `Shipping Non-linearity Rationale (why cheapest-per-item is wrong)` --semantically_similar_to--> `sites/ Site Profile Directory`  [INFERRED] [semantically similar]
  ARCHITECTURE.md → sites/README.md
- `Variant Pattern B (dropdown + AJAX price)` --semantically_similar_to--> `Variant Selector Detector Fix (WooCommerce 'variation' vs 'variant')`  [INFERRED] [semantically similar]
  ARCHITECTURE.md → docs/discovery-report.md
- `test_real_measurement_picks_httpx_for_a_plain_page()` --indirect_call--> `DiscoveryReport`  [INFERRED]
  tests/test_discover.py → src/parfum_finder/discover.py
- `test_a_hook_that_reads_nothing_is_named_as_the_culprit()` --indirect_call--> `ExtractionFailed`  [INFERRED]
  tests/test_engine.py → src/parfum_finder/engine.py
- `test_a_post_endpoint_missing_a_static_body_field_fails_loudly()` --indirect_call--> `ExtractionFailed`  [INFERRED]
  tests/test_engine.py → src/parfum_finder/engine.py

## Import Cycles
- 3-file cycle: `src/parfum_finder/__init__.py -> src/parfum_finder/cli.py -> src/parfum_finder/store.py -> src/parfum_finder/__init__.py`
- 3-file cycle: `src/parfum_finder/__init__.py -> src/parfum_finder/cli.py -> src/parfum_finder/validate.py -> src/parfum_finder/__init__.py`
- 3-file cycle: `src/parfum_finder/__init__.py -> src/parfum_finder/cli.py -> src/parfum_finder/profiles.py -> src/parfum_finder/__init__.py`
- 3-file cycle: `src/parfum_finder/__init__.py -> src/parfum_finder/cli.py -> src/parfum_finder/logging_setup.py -> src/parfum_finder/__init__.py`
- 4-file cycle: `src/parfum_finder/__init__.py -> src/parfum_finder/cli.py -> src/parfum_finder/discover.py -> src/parfum_finder/store.py -> src/parfum_finder/__init__.py`
- 4-file cycle: `src/parfum_finder/__init__.py -> src/parfum_finder/cli.py -> src/parfum_finder/validate.py -> src/parfum_finder/profiles.py -> src/parfum_finder/__init__.py`
- 4-file cycle: `src/parfum_finder/__init__.py -> src/parfum_finder/cli.py -> src/parfum_finder/discover.py -> src/parfum_finder/profiles.py -> src/parfum_finder/__init__.py`
- 4-file cycle: `src/parfum_finder/__init__.py -> src/parfum_finder/cli.py -> src/parfum_finder/engine.py -> src/parfum_finder/profiles.py -> src/parfum_finder/__init__.py`
- 5-file cycle: `src/parfum_finder/__init__.py -> src/parfum_finder/cli.py -> src/parfum_finder/store.py -> src/parfum_finder/engine.py -> src/parfum_finder/profiles.py -> src/parfum_finder/__init__.py`
- 5-file cycle: `src/parfum_finder/__init__.py -> src/parfum_finder/cli.py -> src/parfum_finder/validate.py -> src/parfum_finder/engine.py -> src/parfum_finder/profiles.py -> src/parfum_finder/__init__.py`

## Hyperedges (group relationships)
- **Sites Implementing Variant Pattern C (embedded JSON)** — docs_discovery_report_venco_site, docs_discovery_report_decantall_site, docs_discovery_report_luxurydekant_site, docs_discovery_report_ruxangroup_site, architecture_md_variant_pattern_c [EXTRACTED 1.00]
- **İdeasoft Platform Sites and Endpoint** — docs_discovery_report_dekantparfum_site, docs_discovery_report_dekantdoktoru_site, docs_discovery_report_ideasoft_related_options_endpoint, platforms_readme_ideasoft_json [EXTRACTED 1.00]
- **discover Command Output Artifacts (profile + fixtures + CI validation)** — architecture_md_discover_flow, sites_readme_sites_dir, fixtures_readme_fixtures_dir, github_workflows_ci_validate_profiles_step, architecture_md_validate_command [INFERRED 0.85]

## Communities (92 total, 5 thin omitted)

### Community 0 - "TUI App & Screens"
Cohesion: 0.09
Nodes (100): The Textual-based terminal UI: search and basket screens., _app(), _basket(), _cells(), _days_ago(), _leg(), _ok(), _open_basket() (+92 more)

### Community 1 - "Site Profiles & Templates"
Cohesion: 0.06
Nodes (80): _check_hook_kinds(), deep_merge(), _load_json(), load_platform_template(), load_platform_templates(), load_site_hooks(), load_site_profile(), Any (+72 more)

### Community 2 - "Title Matcher"
Cohesion: 0.26
Nodes (12): encode_basket_report(), encode_result_row(), encode_scan_event(), encode_site_scenario(), _encode_split_leg(), encode_split_plan(), Any, BasketReport (+4 more)

### Community 3 - "HTTP/Browser Fetching"
Cohesion: 0.13
Nodes (31): browser_session(), fetch(), Strategy, Fetch one URL using exactly the given strategy.      `method`/`data` exist for t, Yield a fetcher that keeps one browser for every playwright page it reads., test_the_no_results_page_would_otherwise_read_as_suspect(), _fake_launch(), Event (+23 more)

### Community 4 - "Search/Basket Domain Models"
Cohesion: 0.13
Nodes (47): _app(), _painted_in_basket(), _per_query_runner(), Any, Tests for the search screen: grouping, persistence, and the key bindings.  A fak, Wait for the scan to end, which is the only time the table is filled.      Count, The table stays empty for the whole scan, and the bar carries the news.      Row, Answer each perfume with a row of its own, and record every scan asked for. (+39 more)

### Community 5 - "Search Engine per Site"
Cohesion: 0.14
Nodes (20): add_basket_item(), _perfume_id(), _product_id(), Connection, Do the writing, without opening a transaction of its own., Add a size of a perfume to the basket, and return the basket_item_id.      The p, Set a basket line's quantity, clamped to at least 1, and return it.      The tab, Read back the id of a row that was just inserted or already existed.      RETURN (+12 more)

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
Cohesion: 0.06
Nodes (67): CacheKey, HTMLParser, _check_empty_search(), _check_variant_control(), ExtractionFailed, _fetch_page(), _headers(), _jitter_s() (+59 more)

### Community 10 - "Basket Optimizer Core"
Cohesion: 0.15
Nodes (35): BasketItem, optimize(), Prices, Score one site against the basket, or against a subset of it.      `item_ids` is, Score every enabled site against the whole basket and sort the results.      Sit, Search for the cheapest way to split the basket across several sites.      Retur, One line of the shopping list: a basket row, not a unit count.      `item_id` is, single_site_scenarios() (+27 more)

### Community 11 - "Basket Store & Pricing"
Cohesion: 0.08
Nodes (37): ProductCandidate, One hit on a search results page, before its product page is opened.      `raw_t, One decant size of one product, in the units the database stores.      Tenths of, A candidate together with the decant sizes its product page offers., What one site had to say about one query, and how much to trust it.      Four st, SearchHit, SiteResult, Variant (+29 more)

### Community 12 - "JSON-LD Product Extraction"
Cohesion: 0.10
Nodes (39): extract_jsonld_products(), Read every JSON-LD Product declared on the page, in document order.      A block, _one_product_html(), Tests for parfum_finder.extract.  Every case here is a shape a real store actual, Wrap a JSON-LD product body in a page, for the one-field-at-a-time cases., test_a_broken_block_does_not_lose_the_valid_one(), test_availability_spellings_all_land_in_the_same_bucket(), test_boolean_values_are_never_read_as_price_or_text() (+31 more)

### Community 13 - "Basket TUI Screen"
Cohesion: 0.08
Nodes (47): PyInstaller entry point for the packaged desktop app.  Kept outside src/parfum_f, _close_window_when_asked(), _hold_app_mutex(), _kill_children_with_app(), main(), _ping(), Event, Path (+39 more)

### Community 14 - "Platform Schema"
Cohesion: 0.06
Nodes (31): any, defaults, fingerprint, additionalProperties, items, minItems, type, description (+23 more)

### Community 15 - "Product Extraction"
Cohesion: 0.08
Nodes (43): extract_embedded_variants(), extract_jsonld_variants(), Rung 1: read the page's JSON-LD as flat variant rows.      A product that declar, Rung 3: read the JSON blob the page carries but does not display.      Two shape, The Textual App root. Handles screen navigation and is the app's default entry p, _age_of(), Check, _count_result_cards() (+35 more)

### Community 16 - "Schema Field Patterns"
Cohesion: 0.05
Nodes (39): css, embedded_json, endpoint, jsonld, format, pattern, type, pattern (+31 more)

### Community 17 - "Offline Profile Validation"
Cohesion: 0.06
Nodes (97): CandidateFilter, _candidates_to_open(), Path, Run one site and classify what came back instead of raising.      It is also whe, Run every site against one query, all at once, and report each separately., Run one query against one site and read every hit's sizes.      Everything site-, Narrow the search results down to the pages worth a request.      The first one, run_site() (+89 more)

### Community 18 - "Playwright Errors"
Cohesion: 0.12
Nodes (25): _choose_strategy(), _qualifies(), Pick the cheapest strategy that came back with real content, or None.      probe, Whether one strategy came back with a usable page., _attempt(), _count_jsonld(), _count_product_objects(), _detect_platforms() (+17 more)

### Community 19 - "Search TUI Screen"
Cohesion: 0.07
Nodes (44): A multi-site price and stock comparison tool for perfume decants.  Includes a sh, File logging for the app's own diagnostics.  Nothing here ever writes to the con, find_header_columns(), find_match(), open_worksheet(), Any, Exception, Path (+36 more)

### Community 20 - "Snapshot Writing"
Cohesion: 0.18
Nodes (22): grouped_value(), Decimal, ResultRow, Pure sorting and grouping rules for the results table.  No I/O, no Textual state, What each site charges for the product a block is about.      One entry per site, The default order: typed order, product, site, size.      The typed order comes, The order once a column has been picked: the site layer drops out.      Asking f, site_ranks() (+14 more)

### Community 21 - "Candidate Filtering"
Cohesion: 0.12
Nodes (19): Any, Connection, Command-line entry point.  Subcommands will be added incrementally as the projec, Scan every perfume against every site and print each site as it lands.      One, Write one site's rows in a transaction of its own.      Per site rather than per, One line per site: which site, how it went, and what it said.      The site id i, _report_line(), _scan_all() (+11 more)

### Community 22 - "Basket Site Scenarios"
Cohesion: 0.16
Nodes (33): ParfumFinderApp, Path, Root app: pushes the search screen on mount., _ok_result(), LogCaptureFixture, MonkeyPatch, Path, Submitting a query has to hand focus to the table.      A focused Input swallows (+25 more)

### Community 23 - "Price/Size Normalization"
Cohesion: 0.09
Nodes (30): _read_basket(), One site's share of a split basket: what to buy there and what it costs.      `s, The cheapest basket split the search found. A heuristic, not a proof.      Every, What it would cost to buy some or all of the basket from one site.      `covered, SiteScenario, SplitLeg, SplitPlan, basket_lines() (+22 more)

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
Nodes (19): exclude_keywords, field, max_size_ml, size_from, size_pattern, title, variant_label, exclusiveMinimum (+11 more)

### Community 29 - "Discovery CLI Reporting"
Cohesion: 0.15
Nodes (23): AddButton(), Badge(), BadgeKind, ConfirmDialog(), ScanStatus(), VerdictAddButton(), basketKey(), formatAge() (+15 more)

### Community 30 - "Store Timestamp Tests"
Cohesion: 0.10
Nodes (21): BasketResponse, ResultsResponse, SiteSummary, basket(), basketRow(), resultRow(), scenario(), splitCombination() (+13 more)

### Community 31 - "Live Profile Validation"
Cohesion: 0.07
Nodes (39): Pattern, _brand_pattern(), _canonical(), _canonical_brands(), _covers(), _ends_with(), _index_of(), _match_text() (+31 more)

### Community 32 - "Variant Extraction Fields"
Cohesion: 0.12
Nodes (16): attribute, script, type, additionalProperties, allOf, description, properties, type (+8 more)

### Community 33 - "_ResultRow"
Cohesion: 0.09
Nodes (59): Match, match_title(), parse_query(), PerfumeQuery, The perfume being looked for, split into its three identity parts.      `concent, One site title judged against the query.      `concentration` is what the title, Split one typed line, "Dior Sauvage EDP", into the three identity parts.      Th, Judge one site title against a query, or None if it is not that perfume.      No (+51 more)

### Community 34 - "Fetch Strategy Probing"
Cohesion: 0.21
Nodes (8): _FixtureFetcher, FormData, Headers, Method, Path, Strategy, Serves one site's saved capture in place of the network.      Only three kinds o, The one real result card that led to the captured product page.          Cut out

### Community 35 - "Platform Field Mapping"
Cohesion: 0.18
Nodes (11): field_map, product_json, source, variants_path, required, additionalProperties, allOf, description (+3 more)

### Community 36 - "Shipping Config Schema"
Cohesion: 0.14
Nodes (14): free_shipping_threshold_kurus, shipping_cost_kurus, minimum, type, free_shipping_threshold_kurus, notes, shipping, shipping_cost_kurus (+6 more)

### Community 37 - "_trial"
Cohesion: 0.12
Nodes (25): _classify_single_separator(), format_age(), format_ml(), format_price(), _parse_number(), parse_price(), parse_size_ml(), Decimal (+17 more)

### Community 38 - "TUI Confirm Dialog"
Cohesion: 0.12
Nodes (48): BaseModel, FastAPI, AcceptedSearch, _add_basket_item(), _AppState, BasketAddRequest, BasketQtyRequest, create_app() (+40 more)

### Community 39 - "TUI App Shell"
Cohesion: 0.06
Nodes (15): Changed, HeaderSelected, RowSelected, ComposeResult, ComposeResult, ResultRow, Row, The initial screen: search bar, streaming results table, notices, footer. (+7 more)

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
Cohesion: 0.14
Nodes (16): api, ApiError, readDetail(), request(), Window, UpdateDialog(), daysSince(), SearchScreen() (+8 more)

### Community 45 - "_ResultRow"
Cohesion: 0.14
Nodes (51): TestClient, _auth(), _client(), db_path(), _ok_result(), Any, MonkeyPatch, Path (+43 more)

### Community 46 - "Offline Validation Fixtures"
Cohesion: 0.25
Nodes (8): type, additionalProperties, type, body, request_headers, additionalProperties, description, type

### Community 47 - "JsonLdProduct"
Cohesion: 0.20
Nodes (11): App(), Toast, View, BookmarkIcon(), BookmarkIconProps, variants, WishlistButton(), loadWishlist() (+3 more)

### Community 48 - "._build_rows"
Cohesion: 0.07
Nodes (49): collect_prices(), DiscoveryReport, FieldConfidence, _flatten_defaults(), _format_choice(), _format_confidence(), _format_defaults(), _format_fingerprint() (+41 more)

### Community 49 - "_RecordingFetcher"
Cohesion: 0.12
Nodes (25): Connection, Two lines added within the same second must still read back the same way twice., A basket line nobody sells must still be visible via basket_lines.      basket_p, Deleting a row that's already gone is a race between two screens, not a bug., Insert one site → perfume → product → variant chain, return the variant id., Two snapshots written in the same second must resolve to the newer one.      A s, 5 ml at 125,00 TL is 25,00 TL per ml. Stored as kurus, ml as tenths., No price yet means no row, so the basket LEFT JOIN reads it as missing. (+17 more)

### Community 50 - "Profile Age Checks"
Cohesion: 0.06
Nodes (59): _age_line(), format_live_report(), format_report(), profile_age_days(), datetime, Every check run against one site's profile, in the order they ran.      Checks s, Whether the profile is old enough to be worth re-discovering., The check that broke, or None if the profile is intact. (+51 more)

### Community 51 - "._refresh_table"
Cohesion: 0.13
Nodes (23): apply_variant_rules(), _is_excluded(), Decimal, Turn raw size rows into decant variants, dropping what is not a decant.      Thr, Read one row's volume in millilitres, or None if the text does not say.      "fi, Whether this row is something other than a decant.      The size threshold is in, Convert a price in lira to whole kuruş.      Integers all the way, never a float, _read_size_ml() (+15 more)

### Community 52 - "FetchResult"
Cohesion: 0.19
Nodes (34): Connection, Mirror site profiles into the sites table and return how many were written., sync_to_db(), now_iso(), Return the current UTC time as 'YYYY-MM-DDTHH:MM:SSZ'.      Every timestamp writ, _basket_row(), _collect(), _ok_result() (+26 more)

### Community 53 - "conftest.py"
Cohesion: 0.14
Nodes (20): Collection, basket_inputs(), build_basket_rows(), _ClimbState, _label(), BasketRow, Basket scenario evaluation. A pure function, no network access, no sqlite.  Inpu, The hill-climb's working assignment plus the running per-site figures.      `sub (+12 more)

### Community 54 - "Endpoint Schema Fields"
Cohesion: 0.22
Nodes (9): result_item, result_title, result_url, url_template, search, additionalProperties, description, required (+1 more)

### Community 55 - "apply_variant_rules"
Cohesion: 0.13
Nodes (21): connect(), Path, Open the price database, creating the schema if it isn't there yet.      Foreign, Write one scan's reading of one size, and return its snapshot id.      The perfu, record_snapshot(), _basket_count(), _counting_runner(), _days_ago() (+13 more)

### Community 56 - "Request Schema Fields"
Cohesion: 0.04
Nodes (45): jsdom, motion, @playwright/test, react, react-dom, @testing-library/jest-dom, @testing-library/react, @testing-library/user-event (+37 more)

### Community 57 - "_FixtureFetcher"
Cohesion: 0.17
Nodes (6): _Change, BasketScreen, Path, The basket: the list on top, one scenario per site underneath., _remove(), _set_qty()

### Community 58 - "setup_logging"
Cohesion: 0.07
Nodes (27): DOM, DOM.Iterable, e2e, ES2022, playwright.config.ts, src, tests, vite/client (+19 more)

### Community 59 - "_named_profile"
Cohesion: 0.18
Nodes (20): _close_browser(), _close_session_browser(), _fetch_curl_cffi(), _fetch_httpx(), _fetch_playwright(), _folded(), _launch_browser(), Any (+12 more)

### Community 60 - "_wait_for_table"
Cohesion: 0.24
Nodes (14): fetch_latest_release(), En son yayımlanmış sürüm, ya da ulaşılamadıysa None.      /releases/latest tasla, _enable_checks(), _patch_get(), MonkeyPatch, Tests for parfum_finder.updater: the version compare, the release read, and the, No network is not an error the user has to be told about.      The check runs un, The .exe is what gets downloaded, whatever else is attached.      Releases carry (+6 more)

### Community 61 - "._apply_scan_event"
Cohesion: 0.33
Nodes (8): _fake_runner(), main(), _matching_product(), _profile(), Any, The backend playwright drives: the real app, with the shops stubbed out.  Everyt, Which catalogue product a typed query is about, by its leading words.      Delib, A profile that passes schema validation and is never actually fetched.

### Community 62 - "snapshot_rows"
Cohesion: 0.08
Nodes (39): A stale reading must never outrank the one taken after it.      latest_prices al, Whether an out-of-stock price counts as missing is the caller's call.      Dropp, The drop happens here so no caller can forget it.      Both the CLI and the scre, One call has to leave a row the search table can read straight off.      The cal, The old price has to survive, and it must not become a second variant.      Appe, first_seen is what says how long a shop has carried a size., The title and URL are information, not identity.      A shop that rewords a list, EDT and EDP are different products at different prices.      Folding them into o (+31 more)

### Community 64 - "validate_live"
Cohesion: 0.22
Nodes (4): Pressed, ConfirmScreen, Path, Asks before a low-confidence match is written to the basket.      The two answer

### Community 65 - "_named_profile"
Cohesion: 0.33
Nodes (7): Remember a query line so the search screen can offer it again.      Re-running t, The most recently run query lines, newest first, as (text, searched_at)., recent_searches(), record_search(), The recents list has five slots, so a repeat must not consume two.      Someone, test_recent_searches_stops_at_the_limit(), test_rerunning_a_search_moves_it_up_instead_of_adding_a_second_copy()

### Community 67 - "extract_embedded_variants"
Cohesion: 0.67
Nodes (4): authToken(), refusalReason(), streamUrl(), useEventStream()

### Community 68 - "JsonLdProduct"
Cohesion: 0.18
Nodes (4): _FakeClient, _FakeStreamResponse, Any, Exception

### Community 71 - "exclude_keywords"
Cohesion: 0.22
Nodes (9): price_history(), Row, Return one variant's past readings, newest first, capped at limit.      Empty fo, The trend panel reads row 0 as the latest reading, so order is the point.      A, No history yet is a normal state for a variant, not an error to raise on., The identity a real scan writes must be the identity these lookups accept., test_a_scanned_perfume_can_be_read_back_by_basket_and_history(), test_price_history_is_empty_for_an_unknown_variant() (+1 more)

### Community 72 - "write_snapshots"
Cohesion: 0.50
Nodes (3): The template this site's profile would be based on, if any., Which of the matching templates gets applied, or None for none of them.      One, _resolve_platform()

### Community 73 - "_css_variant"
Cohesion: 0.25
Nodes (11): BasketReport, compare_split_to_best_full(), Every site's single-site scenario, split by whether it covers everything.      A, Whether a split plan beats the best full-coverage single site.      `best_full`, Score a split plan against the cheapest full-coverage single site.      Only the, SplitVerdict, _full_scenario(), _plan() (+3 more)

### Community 75 - "ResultRow"
Cohesion: 0.06
Nodes (54): _as_str(), _balanced_value(), _build_offer(), _build_product(), _coerce_in_stock(), _collect_offers(), _collect_products(), _collect_variants() (+46 more)

### Community 77 - "_collect_products"
Cohesion: 0.29
Nodes (7): in_stock, price, size_raw, additionalProperties, required, type, field_map

### Community 79 - "AddButton.tsx"
Cohesion: 0.50
Nodes (4): One search line, then the same line with the brand written the other ways., search_spellings(), test_a_brand_nobody_abbreviates_is_asked_for_once(), test_the_typed_spelling_is_asked_first_and_the_rest_only_follow()

### Community 81 - "run_sites"
Cohesion: 0.08
Nodes (63): Lock, ScanEvent, BasketRefreshEvent and viewmodel dataclasses as JSON-safe dicts.  Eve, Protocol, One site's pacing state, for as long as whoever holds it says.      The gate and, What a caller needs of run_site, as a type callers can stand a fake in for., SitePace, SiteRunner, BasketPriceExcluded (+55 more)

### Community 82 - "test_connect_is_idempotent_on_an_existing_database"
Cohesion: 0.18
Nodes (9): BaseHTTPRequestHandler, _Handler, _playwright_usable(), MonkeyPatch, Shared pytest fixtures.  A local HTTP server used by fetch/probe tests: real req, Whether the playwright rung can actually run here, binary included.      Checkin, Record every delay the engine asks for instead of serving it.      Waiting for r, server_url() (+1 more)

### Community 83 - "DownloadProgress"
Cohesion: 0.22
Nodes (4): Client, DownloadProgress, İndirmeyi başlatır. Zaten çalışıyorsa None., state: idle | downloading | ready | installing | error.

### Community 84 - "BasketScreen.tsx"
Cohesion: 0.13
Nodes (15): ProgressBar(), cheapestSite(), Scenario(), xMarkPathVariants, AcceptedSearch, BasketRefreshEvent, BasketReport, BasketRow (+7 more)

### Community 85 - "_factory"
Cohesion: 0.33
Nodes (10): _factory(), Path, An error state is what turns the button back on with a reason.      Falling back, Nothing is spawned unless a complete file is on disk.      Running a half-writte, test_a_failed_download_says_so_instead_of_going_quiet(), test_a_second_download_is_refused_while_one_runs(), test_download_writes_the_installer_and_reports_ready(), test_install_hands_the_downloaded_file_over() (+2 more)

### Community 86 - "._scan"
Cohesion: 0.29
Nodes (7): items, type, type, items, type, exclude_keywords, needs_review

### Community 87 - "helpers.ts"
Cohesion: 0.49
Nodes (7): addFirstRow(), authToken(), clearBasket(), openApp(), search(), searchButton(), tab()

### Community 88 - "handoff_command"
Cohesion: 0.29
Nodes (8): handoff_command(), launch_installer(), Path, Kurulumu biz kapandıktan sonra çalıştıran, sonra uygulamayı geri açan     cmd.ex, Üç şey de doğru olmadan güncelleme sessizce başarısız olur.      Bekleme olmazsa, Uygulama kapanınca kurulum zincirinin de ölmemesi buna bağlı.      gui.py, playw, test_the_handoff_breaks_out_of_the_apps_job_object(), test_the_handoff_waits_before_installing_and_reopens_the_app()

### Community 94 - "Arayüz testleri"
Cohesion: 0.40
Nodes (4): Arayüz testleri, jsdom katmanı (`tests/`), Ne test edilmiyor, Tarayıcı katmanı (`e2e/`)

### Community 97 - "test_paths.py"
Cohesion: 0.38
Nodes (11): _freeze(), MonkeyPatch, Path, Tests for parfum_finder.paths: frozen vs. source path resolution.  `ensure_user_, A source run has nothing to seed: resource_dir and user_data_dir are     already, test_ensure_user_data_is_a_noop_when_not_frozen(), test_ensure_user_data_never_overwrites_an_edited_file(), test_ensure_user_data_seeds_sites_platforms_and_hooks() (+3 more)

### Community 99 - "cached_prices"
Cohesion: 0.14
Nodes (15): conn(), Path, Tests for parfum_finder.store: the timestamp helper and the schema.  The one har, A disabled site loses its basket column, but an enabled quiet one keeps one., NULL means the site has no free shipping tier at all, not a threshold of zero., A snapshot pointing at a variant that doesn't exist has to be rejected.      SQL, Reopening an existing database must not wipe or re-raise on its schema., Nothing on record is the state before a first search, not an error.      The sea (+7 more)

## Knowledge Gaps
- **226 isolated node(s):** `parfum-finder`, `$schema`, `$id`, `title`, `description` (+221 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **5 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `SearchScreen` connect `TUI App Shell` to `validate_live`, `_ResultRow`, `Site Profiles & Templates`, `TUI App & Screens`, `TUI Confirm Dialog`, `Product Extraction`, `run_sites`, `Search TUI Screen`, `FetchResult`, `Basket Site Scenarios`, `_FixtureFetcher`?**
  _High betweenness centrality (0.031) - this node is a cross-community bridge._
- **Why does `PlaywrightNotInstalled` connect `FieldConfidence` to `Search Engine Core`, `Basket Store & Pricing`, `._build_rows`, `run_sites`, `Playwright Errors`, `test_connect_is_idempotent_on_an_existing_database`, `Offline Profile Validation`, `SQLite Store`, `_named_profile`?**
  _High betweenness centrality (0.029) - this node is a cross-community bridge._
- **Why does `SiteRunner` connect `run_sites` to `validate_live`, `TUI Confirm Dialog`, `TUI App Shell`, `Search Engine Core`, `FieldConfidence`, `Basket Store & Pricing`, `_ResultRow`, `Offline Profile Validation`, `Search TUI Screen`, `FetchResult`, `Basket Site Scenarios`, `Price/Size Normalization`, `_FixtureFetcher`?**
  _High betweenness centrality (0.026) - this node is a cross-community bridge._
- **Are the 25 inferred relationships involving `SiteResult` (e.g. with `RawVariant` and `Fetcher`) actually correct?**
  _`SiteResult` has 25 INFERRED edges - model-reasoned connections that need verification._
- **Are the 23 inferred relationships involving `PerfumeQuery` (e.g. with `BasketPriceExcluded` and `BasketRefreshFinished`) actually correct?**
  _`PerfumeQuery` has 23 INFERRED edges - model-reasoned connections that need verification._
- **Are the 14 inferred relationships involving `SearchScreen` (e.g. with `ParfumFinderApp` and `SiteRunner`) actually correct?**
  _`SearchScreen` has 14 INFERRED edges - model-reasoned connections that need verification._
- **What connects `parfum-finder`, `$schema`, `$id` to the rest of the system?**
  _226 weakly-connected nodes found - possible documentation gaps or missing edges._