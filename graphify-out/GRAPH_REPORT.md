# Graph Report - parfum-finder  (2026-08-24)

## Corpus Check
- 134 files · ~317,472 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2619 nodes · 7278 edges · 118 communities (100 shown, 18 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 483 edges (avg confidence: 0.54)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `a9580e2e`
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
- validate_live
- AddButton.tsx
- _write_hook
- run_sites
- test_connect_is_idempotent_on_an_existing_database
- DownloadProgress
- _wait_until
- enum
- ._write_to_sheet
- helpers.ts
- handoff_command
- ._write_to_sheet
- ._start_search
- test_write_sheet_asks_confirmation_for_a_stale_cached_price
- _FakeStreamResponse
- _scenario_block
- Arayüz testleri
- _seed_site
- _redirect_product_candidate
- cached_prices
- .on_mount
- _collect_products
- .get_system_commands
- Static
- tui/app.py
- ._load_profiles
- test_every_shipped_site_has_a_colour_that_survives_256_colours
- .action_sort
- .__init__
- ._reset_table
- .on_input_submitted
- SiteScenario
- SplitLeg
- Node
- ComposeResult
- LogCaptureFixture

## God Nodes (most connected - your core abstractions)
1. `PerfumeQuery` - 81 edges
2. `SiteResult` - 71 edges
3. `search_site()` - 69 edges
4. `_profile()` - 69 edges
5. `connect()` - 61 edges
6. `SearchScreen` - 61 edges
7. `FetchResult` - 56 edges
8. `Fetcher` - 56 edges
9. `match_title()` - 55 edges
10. `discover()` - 54 edges

## Surprising Connections (you probably didn't know these)
- `Shipping Non-linearity Rationale (why cheapest-per-item is wrong)` --semantically_similar_to--> `sites/ Site Profile Directory`  [INFERRED] [semantically similar]
  ARCHITECTURE.md → sites/README.md
- `Variant Pattern B (dropdown + AJAX price)` --semantically_similar_to--> `Variant Selector Detector Fix (WooCommerce 'variation' vs 'variant')`  [INFERRED] [semantically similar]
  ARCHITECTURE.md → docs/discovery-report.md
- `test_multiple_top_level_microdata_products_are_ambiguous()` --indirect_call--> `ExtractionFailed`  [INFERRED]
  tests/test_engine.py → src/parfum_finder/engine.py
- `test_nested_related_product_name_does_not_name_the_page_scope()` --indirect_call--> `ExtractionFailed`  [INFERRED]
  tests/test_engine.py → src/parfum_finder/engine.py
- `test_unclassified_or_conflicting_material_redirect_fails_loudly()` --indirect_call--> `ExtractionFailed`  [INFERRED]
  tests/test_engine.py → src/parfum_finder/engine.py

## Import Cycles
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

## Communities (118 total, 18 thin omitted)

### Community 0 - "TUI App & Screens"
Cohesion: 0.09
Nodes (100): The Textual-based terminal UI: search and basket screens., _app(), _basket(), _cells(), _days_ago(), _leg(), _ok(), _open_basket() (+92 more)

### Community 1 - "Site Profiles & Templates"
Cohesion: 0.06
Nodes (81): _check_hook_kinds(), deep_merge(), _load_json(), load_platform_template(), load_platform_templates(), load_site_hooks(), load_site_profile(), Any (+73 more)

### Community 2 - "Title Matcher"
Cohesion: 0.09
Nodes (62): Run one site and classify what came back instead of raising.      It is also whe, run_site(), FetchResult, One fetched page, uniform regardless of which strategy produced it., _counting_fetcher(), _profile(), Exception, Tests for the profile-driven search in parfum_finder.engine.  What these defend (+54 more)

### Community 3 - "HTTP/Browser Fetching"
Cohesion: 0.12
Nodes (35): browser_session(), fetch(), PlaywrightNotInstalled, Strategy, Fetch one URL using exactly the given strategy.      `method`/`data` exist for t, Yield a fetcher that keeps one browser for every playwright page it reads., The "playwright" strategy was requested but cannot run at all.      Covers both, test_the_no_results_page_would_otherwise_read_as_suspect() (+27 more)

### Community 4 - "Search/Basket Domain Models"
Cohesion: 0.07
Nodes (116): LogCaptureFixture, ParfumFinderApp, Runner, One decant size of one product, in the units the database stores.      Tenths of, Variant, Write one scan's reading of one size, and return its snapshot id.      The perfu, record_snapshot(), _app() (+108 more)

### Community 5 - "Search Engine per Site"
Cohesion: 0.27
Nodes (11): fetch_latest_release(), En son yayımlanmış sürüm, ya da ulaşılamadıysa None.      /releases/latest tasla, _enable_checks(), _patch_get(), MonkeyPatch, The .exe is what gets downloaded, whatever else is attached.      Releases carry, _release_payload(), test_check_is_off_outside_a_frozen_build() (+3 more)

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
Cohesion: 0.07
Nodes (62): Node, SiteHooks, _canonical_path(), _check_variant_control(), _decode_unreserved(), _fetch_page(), _has_product_ancestor(), _headers() (+54 more)

### Community 10 - "Basket Optimizer Core"
Cohesion: 0.10
Nodes (50): Collection, BasketRow, _score_basket(), basket_inputs(), BasketItem, optimize(), BasketRow, Prices (+42 more)

### Community 11 - "Basket Store & Pricing"
Cohesion: 0.24
Nodes (17): handoff_command(), Uygulamanın kapanmasını bekleyen ayrık PowerShell komutu., _factory(), _handoff_script(), Path, Tests for parfum_finder.updater: the version compare, the release read, and the, An error state is what turns the button back on with a reason.      Falling back, Nothing is spawned unless a complete file is on disk.      Running a half-writte (+9 more)

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
Cohesion: 0.10
Nodes (23): Check, _count_result_cards(), _first_result_url(), _LayerUnavailable, _no_results_check(), _probe_layer(), _probe_other_layers(), Any (+15 more)

### Community 16 - "Schema Field Patterns"
Cohesion: 0.05
Nodes (39): css, embedded_json, endpoint, jsonld, format, pattern, type, pattern (+31 more)

### Community 17 - "Offline Profile Validation"
Cohesion: 0.25
Nodes (11): _named_profile(), Any, The real fetcher, with a list of every URL it was asked for., A profile whose search page lists two houses' bottles, as shops do., test_a_listing_from_another_house_costs_no_product_request(), test_diagnostic_candidate_checks_extraction_but_never_emits_a_hit(), test_one_product_listed_under_two_searches_is_read_once(), test_the_product_cache_keeps_what_a_page_said_not_the_page() (+3 more)

### Community 18 - "Playwright Errors"
Cohesion: 0.12
Nodes (26): HTMLParser, _choose_strategy(), _qualifies(), Pick the cheapest strategy that came back with real content, or None.      probe, Whether one strategy came back with a usable page., _attempt(), _count_jsonld(), _count_product_objects() (+18 more)

### Community 19 - "Search TUI Screen"
Cohesion: 0.08
Nodes (41): find_header_columns(), find_match(), open_worksheet(), Any, Exception, Path, Protocol, Writing a search result onto the user's own Google Sheets wishlist.  The wishlis (+33 more)

### Community 20 - "Snapshot Writing"
Cohesion: 0.18
Nodes (22): grouped_value(), Decimal, ResultRow, Pure sorting and grouping rules for the results table.  No I/O, no Textual state, What each site charges for the product a block is about.      One entry per site, The default order: typed order, product, site, size.      The typed order comes, The order once a column has been picked: the site layer drops out.      Asking f, site_ranks() (+14 more)

### Community 21 - "Candidate Filtering"
Cohesion: 0.14
Nodes (29): Match, match_title(), PerfumeQuery, The perfume being looked for, split into its three identity parts.      `concent, One site title judged against the query.      `concentration` is what the title, Judge one site title against a query, or None if it is not that perfume.      No, test_a_brand_needs_all_of_its_words_not_one(), test_a_brand_only_query_matches_a_title_that_is_only_that_brand() (+21 more)

### Community 23 - "Price/Size Normalization"
Cohesion: 0.14
Nodes (21): _age_of(), live_query(), _path(), profile_age_days(), datetime, Profile staleness checks. Two modes: offline (against saved fixtures) and live (, A URL's path with no trailing slash, for comparing two spellings of one page., Every site that has a profile, sorted so reports read the same way twice. (+13 more)

### Community 24 - "JSON Schema Primitives"
Cohesion: 0.11
Nodes (25): integer, null, string, properties, type, type, type, type (+17 more)

### Community 25 - "SQLite Store"
Cohesion: 0.08
Nodes (48): _read_basket(), BasketReport, build_basket_rows(), _ClimbState, compare_split_to_best_full(), _label(), Basket scenario evaluation. A pure function, no network access, no sqlite.  Inpu, Every site's single-site scenario, split by whether it covers everything.      A (+40 more)

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
Cohesion: 0.24
Nodes (11): Run one site's profile against the real site.      Same contract as offline mode, validate_live(), _FakeSite, _fixture_site(), A stand-in for one live site, answering the search page then the rest.      Live, test_a_broken_layer_reports_which_other_layer_could_take_over(), test_a_working_profile_passes_against_a_site_that_still_answers(), test_live_validation_reports_recognized_product_redirect_format() (+3 more)

### Community 30 - "Store Timestamp Tests"
Cohesion: 0.11
Nodes (20): BasketResponse, basket(), basketRow(), resultRow(), scenario(), splitCombination(), compile(), DEFAULT_CONFIG (+12 more)

### Community 31 - "Live Profile Validation"
Cohesion: 0.09
Nodes (35): Pattern, _brand_pattern(), _canonical(), _canonical_brands(), _covers(), _ends_with(), _index_of(), listing_filter() (+27 more)

### Community 32 - "Variant Extraction Fields"
Cohesion: 0.12
Nodes (16): attribute, script, type, additionalProperties, allOf, description, properties, type (+8 more)

### Community 33 - "_ResultRow"
Cohesion: 0.08
Nodes (46): parse_query(), product_label(), Split one typed line, "Dior Sauvage EDP", into the three identity parts.      Th, Reduce a site's own title to the product it is about, spelled one way.      What, Whether a search result's own listing text is worth opening the page for.      J, title_could_match(), test_reported_false_negative_searches_keep_requested_identity_and_sizes(), Tests for parfum_finder.matcher.  The thing being defended here is not "does it (+38 more)

### Community 34 - "Fetch Strategy Probing"
Cohesion: 0.26
Nodes (7): _FixtureFetcher, FormData, Headers, Method, Strategy, Serves one site's saved capture in place of the network.      Only three kinds o, The one real result card that led to the captured product page.          Cut out

### Community 35 - "Platform Field Mapping"
Cohesion: 0.18
Nodes (11): field_map, product_json, source, variants_path, required, additionalProperties, allOf, description (+3 more)

### Community 36 - "Shipping Config Schema"
Cohesion: 0.14
Nodes (14): free_shipping_threshold_kurus, shipping_cost_kurus, minimum, type, free_shipping_threshold_kurus, notes, shipping, shipping_cost_kurus (+6 more)

### Community 37 - "_trial"
Cohesion: 0.11
Nodes (27): casefold_tr(), _classify_single_separator(), format_age(), format_price(), _parse_number(), parse_price(), parse_size_ml(), Decimal (+19 more)

### Community 38 - "TUI Confirm Dialog"
Cohesion: 0.10
Nodes (32): _load_profiles(), Any, Path, _read_wishlist(), _recent_searches(), _remove_basket_item(), _set_basket_qty(), _site_summary() (+24 more)

### Community 39 - "TUI App Shell"
Cohesion: 0.17
Nodes (16): extract_embedded_variants(), extract_jsonld_variants(), Rung 1: read the page's JSON-LD as flat variant rows.      A product that declar, Rung 3: read the JSON blob the page carries but does not display.      Two shape, _fixture(), Read a captured product page., test_embedded_attribute_reads_a_second_site_with_the_same_shape(), test_embedded_attribute_reads_the_woocommerce_variation_table() (+8 more)

### Community 40 - "Fetch Backends"
Cohesion: 0.14
Nodes (14): curl_cffi, httpx, playwright, result_item, result_title, result_url, strategy, url_template (+6 more)

### Community 41 - "HTTP Request Schema"
Cohesion: 0.14
Nodes (14): GET, POST, properties, default, enum, type, type, type (+6 more)

### Community 42 - "Fixture Fetcher (Tests)"
Cohesion: 0.12
Nodes (49): BaseModel, FastAPI, SplitPlan, AcceptedSearch, _add_basket_item(), _AppState, BasketAddRequest, BasketQtyRequest (+41 more)

### Community 43 - "FieldConfidence"
Cohesion: 0.16
Nodes (7): PlaywrightNoResponse, RuntimeError, Navigation completed but playwright returned no Response object.      Its own ty, _FakeBrowser, _FakePage, Any, test_fetch_playwright_no_response_raises_its_own_error_type()

### Community 44 - "Decant Variant Rules"
Cohesion: 0.17
Nodes (12): ApiError, App(), Toast, View, wishlistIdentity, wishlistKey(), root, daysSince() (+4 more)

### Community 45 - "_ResultRow"
Cohesion: 0.10
Nodes (60): TestClient, _auth(), _client(), db_path(), _ok_result(), Any, MonkeyPatch, Path (+52 more)

### Community 46 - "Offline Validation Fixtures"
Cohesion: 0.25
Nodes (8): type, additionalProperties, type, body, request_headers, additionalProperties, description, type

### Community 47 - "JsonLdProduct"
Cohesion: 0.15
Nodes (18): AddButton(), Badge(), BadgeKind, ConfirmDialog(), ProgressBar(), basketKey(), formatAge(), formatMl() (+10 more)

### Community 48 - "._build_rows"
Cohesion: 0.07
Nodes (49): collect_prices(), DiscoveryReport, FieldConfidence, _flatten_defaults(), _format_choice(), _format_confidence(), _format_defaults(), _format_fingerprint() (+41 more)

### Community 49 - "_RecordingFetcher"
Cohesion: 0.07
Nodes (54): add_basket_item(), Add a size of a perfume to the basket, and return the basket_item_id.      The p, conn(), Connection, Path, Tests for parfum_finder.store: the timestamp helper and the schema.  The one har, The basket screen prints brand/name/concentration straight off this row.      Or, Two lines added within the same second must still read back the same way twice. (+46 more)

### Community 50 - "Profile Age Checks"
Cohesion: 0.20
Nodes (25): format_report(), Check one site's profile against that site's saved fixtures.      Never raises f, Render the validations as the offline half of the report in APP_FLOW §6.      A, validate_offline(), _corrupted_sites_dir(), _iso_days_ago(), Any, Path (+17 more)

### Community 51 - "._refresh_table"
Cohesion: 0.20
Nodes (16): apply_variant_rules(), Turn raw size rows into decant variants, dropping what is not a decant.      Thr, Convert a price in lira to whole kuruş.      Integers all the way, never a float, _to_kurus(), RawVariant, _row(), test_a_keyword_in_the_size_label_excludes_the_row_too(), test_a_literal_zero_price_reads_as_no_price_not_a_free_perfume() (+8 more)

### Community 52 - "FetchResult"
Cohesion: 0.12
Nodes (52): Lock, _record_search(), _sync_profiles(), Connection, Mirror site profiles into the sites table and return how many were written., sync_to_db(), Any, BasketRow (+44 more)

### Community 53 - "conftest.py"
Cohesion: 0.21
Nodes (12): api, authToken(), readDetail(), request(), Window, refusalReason(), streamUrl(), useEventStream() (+4 more)

### Community 54 - "Endpoint Schema Fields"
Cohesion: 0.22
Nodes (9): result_item, result_title, result_url, url_template, search, additionalProperties, description, required (+1 more)

### Community 55 - "apply_variant_rules"
Cohesion: 0.11
Nodes (31): _check_empty_search(), ExtractionFailed, RuntimeError, Run one query against one site and read every hit's sizes.      Everything site-, Fail when a search yielded no rows off a page that plainly lists products., A page answered but gave up nothing, where something was expected.      This is, search_site(), _NoRootParser (+23 more)

### Community 56 - "Request Schema Fields"
Cohesion: 0.04
Nodes (45): jsdom, motion, @playwright/test, react, react-dom, @testing-library/jest-dom, @testing-library/react, @testing-library/user-event (+37 more)

### Community 57 - "_FixtureFetcher"
Cohesion: 0.12
Nodes (10): _Change, BasketScreen, BasketReport, BasketRow, Path, The one line that says the screen is holding something back, or is not., The basket: the list on top, one scenario per site underneath., _remove() (+2 more)

### Community 58 - "setup_logging"
Cohesion: 0.07
Nodes (27): DOM, DOM.Iterable, e2e, ES2022, playwright.config.ts, src, tests, vite/client (+19 more)

### Community 59 - "_named_profile"
Cohesion: 0.18
Nodes (20): _close_browser(), _close_session_browser(), _fetch_curl_cffi(), _fetch_httpx(), _fetch_playwright(), _folded(), _launch_browser(), Any (+12 more)

### Community 60 - "_wait_for_table"
Cohesion: 0.33
Nodes (8): _fake_runner(), main(), _matching_product(), _profile(), Any, The backend playwright drives: the real app, with the shops stubbed out.  Everyt, Which catalogue product a typed query is about, by its leading words.      Delib, A profile that passes schema validation and is never actually fetched.

### Community 61 - "._apply_scan_event"
Cohesion: 0.27
Nodes (9): Any, Connection, Command-line entry point.  Subcommands will be added incrementally as the projec, Scan every perfume against every site and print each site as it lands.      One, Write one site's rows in a transaction of its own.      Per site rather than per, One line per site: which site, how it went, and what it said.      The site id i, _report_line(), _scan_all() (+1 more)

### Community 62 - "snapshot_rows"
Cohesion: 0.12
Nodes (29): A search that named no concentration is asking for all of them.      "" means "a, A stale reading must never outrank the one taken after it.      latest_prices al, Whether an out-of-stock price counts as missing is the caller's call.      Dropp, One call has to leave a row the search table can read straight off.      The cal, The old price has to survive, and it must not become a second variant.      Appe, first_seen is what says how long a shop has carried a size., The title and URL are information, not identity.      A shop that rewords a list, EDT and EDP are different products at different prices.      Folding them into o (+21 more)

### Community 64 - "validate_live"
Cohesion: 0.14
Nodes (9): Client, DownloadProgress, launch_installer(), _powershell_literal(), Path, İndirmeyi başlatır. Zaten çalışıyorsa None., state: idle | downloading | ready | installing | error., Uygulama kapanınca kurulum zincirinin de ölmemesi buna bağlı.      gui.py, playw (+1 more)

### Community 65 - "_named_profile"
Cohesion: 0.13
Nodes (20): CacheKey, CandidateFilter, _candidates_to_open(), Path, Run one matcher-aware spelling sequence for every site in parallel., Narrow the search results down to the pages worth a request.      The first one, Try spelling variants until this site returns an emittable match.      The match, Run every site against one query, all at once, and report each separately. (+12 more)

### Community 67 - "extract_embedded_variants"
Cohesion: 0.21
Nodes (15): probe(), Fetch `url` with every strategy and report diagnostics for each.      timeout_s, MonkeyPatch, Tests for parfum_finder.probe.  probe() always tries all three strategies -- the, test_probe_counts_jsonld_product_and_platform_signature(), test_probe_counts_product_across_jsonld_root_shapes(), test_probe_counts_product_markup_without_any_jsonld(), test_probe_counts_products_nested_below_the_top_level() (+7 more)

### Community 68 - "JsonLdProduct"
Cohesion: 0.27
Nodes (11): check_enabled(), check_for_update(), _installer_asset(), _no_update(), Any, GitHub'daki son sürümü sorar, yenisini indirir ve kurulumu devreder.  Güncellene, ReleaseInfo, No network is not an error the user has to be told about.      The check runs un (+3 more)

### Community 71 - "exclude_keywords"
Cohesion: 0.15
Nodes (22): A multi-site price and stock comparison tool for perfume decants.  Includes a sh, Path, Attach the rotating file handler and return where it writes.      Safe to call m, setup_logging(), Path, The file logger's two promises: it writes to the file, and it stays silent.  Bot, _teardown(), test_an_error_lands_in_the_given_file() (+14 more)

### Community 72 - "write_snapshots"
Cohesion: 0.25
Nodes (8): Split one typed line into the perfumes it asks for, on " - ".      The separator, split_queries(), test_a_hyphen_inside_a_brand_name_does_not_split_the_search(), test_a_line_naming_three_perfumes_is_read_as_three_searches(), test_a_piece_that_names_no_perfume_survives_to_be_complained_about(), test_a_stray_separator_is_not_worth_failing_over(), test_one_perfume_is_still_one_search(), test_the_same_perfume_typed_twice_is_scanned_once()

### Community 73 - "_css_variant"
Cohesion: 0.25
Nodes (7): _age_line(), format_live_report(), Every check run against one site's profile, in the order they ran.      Checks s, Whether the profile is old enough to be worth re-discovering., The age note for one site, or None when its age is unremarkable.      A profile, Render offline and live results side by side, as APP_FLOW §6 shows them.      Bo, SiteValidation

### Community 74 - "ConfirmDialog.tsx"
Cohesion: 0.40
Nodes (5): price_history(), Row, Return one variant's past readings, newest first, capped at limit.      Empty fo, No history yet is a normal state for a variant, not an error to raise on., test_price_history_is_empty_for_an_unknown_variant()

### Community 75 - "ResultRow"
Cohesion: 0.13
Nodes (25): _build_offer(), _coerce_in_stock(), _collect_offers(), _css_variant(), JsonLdOffer, _parse_availability(), _parse_price_value(), _parse_selector() (+17 more)

### Community 76 - "SplitPlan"
Cohesion: 0.38
Nodes (4): BookmarkIcon(), BookmarkIconProps, variants, WishlistButton()

### Community 77 - "_collect_products"
Cohesion: 0.29
Nodes (7): in_stock, price, size_raw, additionalProperties, required, type, field_map

### Community 78 - "validate_live"
Cohesion: 0.31
Nodes (7): _DeadSite, FormData, Headers, Method, Strategy, A host that cannot be reached at all., test_an_unreachable_site_is_not_reported_as_a_broken_profile()

### Community 79 - "AddButton.tsx"
Cohesion: 0.29
Nodes (7): _fold_search_separators(), One search line, then the same line with the brand written the other ways., Turn punctuation that commonly splits catalog tokens into spaces., search_spellings(), test_a_brand_nobody_abbreviates_is_asked_for_once(), test_brand_aliases_each_receive_one_separator_folded_attempt_in_order(), test_the_typed_spelling_is_asked_first_and_the_rest_only_follow()

### Community 80 - "_write_hook"
Cohesion: 0.29
Nodes (7): items, type, type, items, type, exclude_keywords, needs_review

### Community 81 - "run_sites"
Cohesion: 0.08
Nodes (54): Pressed, ScanEvent, BasketRefreshEvent and viewmodel dataclasses as JSON-safe dicts.  Eve, _paced_fetcher(), What one site had to say about one query, and how much to trust it.      Four st, One site's pacing state, for as long as whoever holds it says.      The gate and, Wrap a fetcher so one site's requests go out one at a time, spaced apart.      T, SitePace, SiteResult (+46 more)

### Community 82 - "test_connect_is_idempotent_on_an_existing_database"
Cohesion: 0.18
Nodes (9): BaseHTTPRequestHandler, _Handler, _playwright_usable(), MonkeyPatch, Shared pytest fixtures.  A local HTTP server used by fetch/probe tests: real req, Whether the playwright rung can actually run here, binary included.      Checkin, Record every delay the engine asks for instead of serving it.      Waiting for r, server_url() (+1 more)

### Community 83 - "DownloadProgress"
Cohesion: 0.15
Nodes (23): ProductCandidate, One hit on a search results page, before its product page is opened.      `raw_t, A candidate together with the decant sizes its product page offers., SearchHit, Turn one site's hits into the rows write_snapshots is ready to store.      Share, snapshot_rows(), _attempt_hit(), The identity a real scan writes must be the identity these lookups accept. (+15 more)

### Community 84 - "_wait_until"
Cohesion: 0.10
Nodes (25): _balanced_value(), _embedded_documents(), extract_css_variants(), extract_endpoint_variants(), _flatten_jsonld(), _loads_or_skip(), _map_variant(), Any (+17 more)

### Community 85 - "enum"
Cohesion: 0.50
Nodes (3): The template this site's profile would be based on, if any., Which of the matching templates gets applied, or None for none of them.      One, _resolve_platform()

### Community 86 - "._write_to_sheet"
Cohesion: 0.20
Nodes (6): Screen, ParfumFinderApp, Path, The Textual App root. Handles screen navigation and is the app's default entry p, Root app: pushes the search screen on mount., SystemCommand

### Community 87 - "helpers.ts"
Cohesion: 0.49
Nodes (7): addFirstRow(), authToken(), clearBasket(), openApp(), search(), searchButton(), tab()

### Community 88 - "handoff_command"
Cohesion: 0.12
Nodes (18): Block, Notice, pickVerdicts(), ResultsScreen(), SORT_LABELS, toBlocks(), TRIAL_SIZES_ML_X10, Verdicts (+10 more)

### Community 89 - "._write_to_sheet"
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: Review redirect classification, diagnostic suppression, and shared attempt cache and pacing, Source Nodes

### Community 92 - "_FakeStreamResponse"
Cohesion: 0.18
Nodes (4): _FakeClient, _FakeStreamResponse, Any, Exception

### Community 94 - "Arayüz testleri"
Cohesion: 0.40
Nodes (4): Arayüz testleri, jsdom katmanı (`tests/`), Ne test edilmiyor, Tarayıcı katmanı (`e2e/`)

### Community 95 - "_seed_site"
Cohesion: 0.20
Nodes (10): Write a whole scan at once and return how many prices were recorded.      Every, write_snapshots(), The drop happens here so no caller can forget it.      Both the CLI and the scre, A slow site must not spread one reading across several timestamps.      Rows wri, The number reported is what landed in the history, not what was offered., Half a site's sizes updated is worse than none of them.      The basket compares, test_write_snapshots_counts_prices_not_rows(), test_write_snapshots_never_records_a_row_without_its_own_identity() (+2 more)

### Community 96 - "_redirect_product_candidate"
Cohesion: 0.17
Nodes (16): canonical_url(), _normalized_product_name(), Read the result rows off a search page.      Every site needs selectors here, wh, Return the stable identity of a URL without changing its fetch URL., Recognize a single product page after a material same-origin redirect., _read_candidates(), _redirect_product_candidate(), _redirect_page() (+8 more)

### Community 97 - "cached_prices"
Cohesion: 0.33
Nodes (6): cached_prices(), Return the latest stored price of every size of this perfume, per site.      Bra, A price nobody will scan again may not be offered as a result.      Refreshing i, Nothing on record is the state before a first search, not an error.      The sea, test_cached_prices_is_empty_for_a_perfume_nobody_scanned(), test_cached_prices_leaves_out_a_disabled_site()

### Community 98 - ".on_mount"
Cohesion: 0.15
Nodes (4): Any, The initial screen: search bar, streaming results table, notices, footer., SearchScreen, Worksheet

### Community 99 - "_collect_products"
Cohesion: 0.18
Nodes (12): _as_str(), _build_product(), _collect_products(), _collect_variants(), _has_type(), Walk a parsed JSON-LD block and append every Product found, depth first.      De, Whether a node's "@type" names `name`, as a string or inside a list.      Substr, Turn one Product node into a JsonLdProduct. (+4 more)

### Community 102 - ".get_system_commands"
Cohesion: 0.22
Nodes (9): is_newer(), _pad(), parse_version(), v0.2.1 -> (0, 2, 1). Sayıya çevrilemeyen her şey None., Okunamayan bir sürüm asla "yeni" sayılmaz.      Yanlış tarafa düşmenin bedeli si, A tag nobody can order against must not open a dialog.      The two failure dire, test_an_unreadable_tag_never_counts_as_an_update(), test_is_newer() (+1 more)

### Community 103 - "Static"
Cohesion: 0.40
Nodes (3): ComposeResult, ComposeResult, Static

### Community 104 - "tui/app.py"
Cohesion: 0.28
Nodes (5): UpdateDialog(), UpdateInfo, UpdateProgress, INFO, updateProgress()

## Knowledge Gaps
- **229 isolated node(s):** `Answer`, `Outcome`, `Source Nodes`, `Notice`, `TRIAL_SIZES_ML_X10` (+224 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **18 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `SearchScreen` connect `.on_mount` to `TUI App & Screens`, `Static`, `._load_profiles`, `Fixture Fetcher (Tests)`, `.action_sort`, `.__init__`, `._reset_table`, `.on_input_submitted`, `run_sites`, `Candidate Filtering`, `._write_to_sheet`, `Basket Site Scenarios`, `SQLite Store`, `._start_search`?**
  _High betweenness centrality (0.041) - this node is a cross-community bridge._
- **Why does `SiteRunner` connect `Fixture Fetcher (Tests)` to `_named_profile`, `Title Matcher`, `HTTP/Browser Fetching`, `.on_mount`, `Search Engine Core`, `.__init__`, `_ResultRow`, `run_sites`, `FetchResult`, `._write_to_sheet`, `SQLite Store`, `_FixtureFetcher`?**
  _High betweenness centrality (0.029) - this node is a cross-community bridge._
- **Why does `SiteResult` connect `run_sites` to `TUI App & Screens`, `_named_profile`, `Title Matcher`, `HTTP/Browser Fetching`, `Search/Basket Domain Models`, `TUI Confirm Dialog`, `Search Engine Core`, `Fixture Fetcher (Tests)`, `_ResultRow`, `DownloadProgress`, `FetchResult`, `SQLite Store`, `_wait_for_table`, `._apply_scan_event`?**
  _High betweenness centrality (0.024) - this node is a cross-community bridge._
- **Are the 24 inferred relationships involving `PerfumeQuery` (e.g. with `BasketPriceExcluded` and `BasketRefreshFinished`) actually correct?**
  _`PerfumeQuery` has 24 INFERRED edges - model-reasoned connections that need verification._
- **Are the 23 inferred relationships involving `SiteResult` (e.g. with `Fetcher` and `FetchResult`) actually correct?**
  _`SiteResult` has 23 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Answer`, `Outcome`, `Source Nodes` to the rest of the system?**
  _229 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `TUI App & Screens` be split into smaller, more focused modules?**
  _Cohesion score 0.09337992622791691 - nodes in this community are weakly interconnected._