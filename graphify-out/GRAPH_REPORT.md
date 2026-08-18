# Graph Report - parfum-finder  (2026-08-18)

## Corpus Check
- 125 files · ~301,950 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2423 nodes · 6795 edges · 86 communities (80 shown, 6 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 470 edges (avg confidence: 0.55)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `0147f141`
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
- ResultRow
- _collect_products
- ScanStatus.tsx
- BasketScreen.tsx
- Static
- test_paths.py
- helpers.ts
- .__call__
- ws.ts
- Arayüz testleri

## God Nodes (most connected - your core abstractions)
1. `SiteResult` - 69 edges
2. `PerfumeQuery` - 68 edges
3. `search_site()` - 66 edges
4. `SearchScreen` - 64 edges
5. `_profile()` - 58 edges
6. `discover()` - 56 edges
7. `connect()` - 55 edges
8. `Fetcher` - 50 edges
9. `_write_profile()` - 50 edges
10. `match_title()` - 48 edges

## Surprising Connections (you probably didn't know these)
- `Shipping Non-linearity Rationale (why cheapest-per-item is wrong)` --semantically_similar_to--> `sites/ Site Profile Directory`  [INFERRED] [semantically similar]
  ARCHITECTURE.md → sites/README.md
- `Variant Pattern B (dropdown + AJAX price)` --semantically_similar_to--> `Variant Selector Detector Fix (WooCommerce 'variation' vs 'variant')`  [INFERRED] [semantically similar]
  ARCHITECTURE.md → docs/discovery-report.md
- `test_real_measurement_picks_httpx_for_a_plain_page()` --indirect_call--> `DiscoveryReport`  [INFERRED]
  tests/test_discover.py → src/parfum_finder/discover.py
- `_RecordingClient` --uses--> `ProductCandidate`  [INFERRED]
  tests/test_api.py → src/parfum_finder/engine.py
- `_RecordingStream` --uses--> `ProductCandidate`  [INFERRED]
  tests/test_api.py → src/parfum_finder/engine.py

## Import Cycles
- 3-file cycle: `src/parfum_finder/__init__.py -> src/parfum_finder/cli.py -> src/parfum_finder/logging_setup.py -> src/parfum_finder/__init__.py`
- 3-file cycle: `src/parfum_finder/__init__.py -> src/parfum_finder/cli.py -> src/parfum_finder/profiles.py -> src/parfum_finder/__init__.py`
- 3-file cycle: `src/parfum_finder/__init__.py -> src/parfum_finder/cli.py -> src/parfum_finder/store.py -> src/parfum_finder/__init__.py`
- 3-file cycle: `src/parfum_finder/__init__.py -> src/parfum_finder/cli.py -> src/parfum_finder/validate.py -> src/parfum_finder/__init__.py`
- 4-file cycle: `src/parfum_finder/__init__.py -> src/parfum_finder/cli.py -> src/parfum_finder/engine.py -> src/parfum_finder/profiles.py -> src/parfum_finder/__init__.py`
- 4-file cycle: `src/parfum_finder/__init__.py -> src/parfum_finder/cli.py -> src/parfum_finder/discover.py -> src/parfum_finder/profiles.py -> src/parfum_finder/__init__.py`
- 4-file cycle: `src/parfum_finder/__init__.py -> src/parfum_finder/cli.py -> src/parfum_finder/discover.py -> src/parfum_finder/store.py -> src/parfum_finder/__init__.py`
- 4-file cycle: `src/parfum_finder/__init__.py -> src/parfum_finder/cli.py -> src/parfum_finder/validate.py -> src/parfum_finder/profiles.py -> src/parfum_finder/__init__.py`
- 5-file cycle: `src/parfum_finder/__init__.py -> src/parfum_finder/cli.py -> src/parfum_finder/store.py -> src/parfum_finder/engine.py -> src/parfum_finder/profiles.py -> src/parfum_finder/__init__.py`
- 5-file cycle: `src/parfum_finder/__init__.py -> src/parfum_finder/cli.py -> src/parfum_finder/validate.py -> src/parfum_finder/engine.py -> src/parfum_finder/profiles.py -> src/parfum_finder/__init__.py`

## Hyperedges (group relationships)
- **Sites Implementing Variant Pattern C (embedded JSON)** — docs_discovery_report_venco_site, docs_discovery_report_decantall_site, docs_discovery_report_luxurydekant_site, docs_discovery_report_ruxangroup_site, architecture_md_variant_pattern_c [EXTRACTED 1.00]
- **İdeasoft Platform Sites and Endpoint** — docs_discovery_report_dekantparfum_site, docs_discovery_report_dekantdoktoru_site, docs_discovery_report_ideasoft_related_options_endpoint, platforms_readme_ideasoft_json [EXTRACTED 1.00]
- **discover Command Output Artifacts (profile + fixtures + CI validation)** — architecture_md_discover_flow, sites_readme_sites_dir, fixtures_readme_fixtures_dir, github_workflows_ci_validate_profiles_step, architecture_md_validate_command [INFERRED 0.85]

## Communities (86 total, 6 thin omitted)

### Community 0 - "TUI App & Screens"
Cohesion: 0.09
Nodes (100): The Textual-based terminal UI: search and basket screens., _app(), _basket(), _cells(), _days_ago(), _leg(), _ok(), _open_basket() (+92 more)

### Community 1 - "Site Profiles & Templates"
Cohesion: 0.06
Nodes (82): _check_hook_kinds(), deep_merge(), _load_json(), load_platform_template(), load_platform_templates(), load_site_hooks(), load_site_profile(), Any (+74 more)

### Community 2 - "Title Matcher"
Cohesion: 0.09
Nodes (53): Pressed, ScanEvent, BasketRefreshEvent and viewmodel dataclasses as JSON-safe dicts.  Eve, Protocol, What one site had to say about one query, and how much to trust it.      Four st, What a caller needs of run_site, as a type callers can stand a fake in for., SiteResult, SiteRunner, Fetcher (+45 more)

### Community 3 - "HTTP/Browser Fetching"
Cohesion: 0.14
Nodes (28): browser_session(), fetch(), Fetch one URL using exactly the given strategy.      `method`/`data` exist for t, Yield a fetcher that keeps one browser for every playwright page it reads., test_the_no_results_page_would_otherwise_read_as_suspect(), _fake_launch(), MonkeyPatch, Tests for parfum_finder.fetch.  httpx and curl_cffi are exercised against a real (+20 more)

### Community 4 - "Search/Basket Domain Models"
Cohesion: 0.06
Nodes (121): Screen, One decant size of one product, in the units the database stores.      Tenths of, A candidate together with the decant sizes its product page offers., SearchHit, Variant, Write one scan's reading of one size, and return its snapshot id.      The perfu, record_snapshot(), ParfumFinderApp (+113 more)

### Community 5 - "Search Engine per Site"
Cohesion: 0.08
Nodes (38): _load_profiles(), Any, Path, _recent_searches(), _record_search(), _remove_basket_item(), _set_basket_qty(), _site_summary() (+30 more)

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
Cohesion: 0.08
Nodes (53): HTMLParser, _check_variant_control(), _fetch_page(), _headers(), _is_excluded(), _paced_fetcher(), _page_offers_sizes(), _page_says_sold_out() (+45 more)

### Community 10 - "Basket Optimizer Core"
Cohesion: 0.08
Nodes (60): Collection, BasketRow, _score_basket(), basket_inputs(), BasketItem, build_basket_rows(), _label(), optimize() (+52 more)

### Community 11 - "Basket Store & Pricing"
Cohesion: 0.12
Nodes (18): Check, _no_results_check(), _probe_other_layers(), The check that broke, or None if the profile is intact., The real fetcher, remembering what came back.      Live mode needs the search pa, Run one site's profile against the real site.      Same contract as offline mode, Why an empty results page is suspicious, or why it is not.      A full page that, Try every extraction layer the profile is not using, on a real page.      Every (+10 more)

### Community 12 - "JSON-LD Product Extraction"
Cohesion: 0.09
Nodes (46): extract_embedded_variants(), extract_jsonld_products(), extract_jsonld_variants(), Read every JSON-LD Product declared on the page, in document order.      A block, Rung 1: read the page's JSON-LD as flat variant rows.      A product that declar, Rung 3: read the JSON blob the page carries but does not display.      Two shape, _fixture(), _one_product_html() (+38 more)

### Community 13 - "Basket TUI Screen"
Cohesion: 0.10
Nodes (36): PyInstaller entry point for the packaged desktop app.  Kept outside src/parfum_f, _hold_app_mutex(), main(), _ping(), Path, The Windows desktop entry point: an ephemeral-port FastAPI backend behind a nati, Kurulum dosyasının uygulamanın açık olduğunu görmesini sağlar.      packaging/in, Best-effort native message box.      A missing WebView2 Runtime is the expected (+28 more)

### Community 14 - "Platform Schema"
Cohesion: 0.06
Nodes (31): any, defaults, fingerprint, additionalProperties, items, minItems, type, description (+23 more)

### Community 15 - "Product Extraction"
Cohesion: 0.14
Nodes (21): _age_of(), live_query(), _path(), profile_age_days(), datetime, Profile staleness checks. Two modes: offline (against saved fixtures) and live (, A URL's path with no trailing slash, for comparing two spellings of one page., Every site that has a profile, sorted so reports read the same way twice. (+13 more)

### Community 16 - "Schema Field Patterns"
Cohesion: 0.05
Nodes (39): css, embedded_json, endpoint, jsonld, format, pattern, type, pattern (+31 more)

### Community 17 - "Offline Profile Validation"
Cohesion: 0.05
Nodes (99): CacheKey, CandidateFilter, _candidates_to_open(), _check_empty_search(), ExtractionFailed, Path, RuntimeError, A page answered but gave up nothing, where something was expected.      This is (+91 more)

### Community 18 - "Playwright Errors"
Cohesion: 0.12
Nodes (25): _choose_strategy(), _qualifies(), Pick the cheapest strategy that came back with real content, or None.      probe, Whether one strategy came back with a usable page., _attempt(), _count_jsonld(), _count_product_objects(), _detect_platforms() (+17 more)

### Community 19 - "Search TUI Screen"
Cohesion: 0.08
Nodes (41): find_header_columns(), find_match(), open_worksheet(), Any, Exception, Path, Protocol, Writing a search result onto the user's own Google Sheets wishlist.  The wishlis (+33 more)

### Community 20 - "Snapshot Writing"
Cohesion: 0.18
Nodes (21): grouped_value(), Decimal, ResultRow, What each site charges for the product a block is about.      One entry per site, The default order: typed order, product, site, size.      The typed order comes, The order once a column has been picked: the site layer drops out.      Asking f, site_ranks(), sorted_value() (+13 more)

### Community 21 - "Candidate Filtering"
Cohesion: 0.14
Nodes (40): Lock, Any, BasketRow, Path, A site's display name, with a badge when its profile is old enough     to be wor, Rebuild the table's rows for every searched perfume already on record.      Site, Show what storage already knows, then go to the shops for the rest.      `force=, Ask every enabled site for today's price of every basket row.      One task per (+32 more)

### Community 22 - "Basket Site Scenarios"
Cohesion: 0.24
Nodes (6): BaseHTTPRequestHandler, _Handler, _playwright_usable(), Shared pytest fixtures.  A local HTTP server used by fetch/probe tests: real req, Whether the playwright rung can actually run here, binary included.      Checkin, server_url()

### Community 23 - "Price/Size Normalization"
Cohesion: 0.08
Nodes (25): _Change, compare_split_to_best_full(), The cheapest basket split the search found. A heuristic, not a proof.      Every, Score a split plan against the cheapest full-coverage single site.      Only the, SplitPlan, format_ml(), Format a volume for display (dot-decimal): Decimal('1.5') -> '1.5 ml'., BasketScreen (+17 more)

### Community 24 - "JSON Schema Primitives"
Cohesion: 0.11
Nodes (25): integer, null, string, properties, type, type, type, type (+17 more)

### Community 25 - "SQLite Store"
Cohesion: 0.33
Nodes (8): _fake_runner(), main(), _matching_product(), _profile(), Any, The backend playwright drives: the real app, with the shops stubbed out.  Everyt, Which catalogue product a typed query is about, by its leading words.      Delib, A profile that passes schema validation and is never actually fetched.

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
Cohesion: 0.13
Nodes (16): AddButton(), Badge(), BadgeKind, ConfirmDialog(), ScanStatus(), VerdictAddButton(), basketKey(), Block (+8 more)

### Community 31 - "Live Profile Validation"
Cohesion: 0.10
Nodes (30): _canonical(), _covers(), _ends_with(), _index_of(), _match_text(), _own_identity(), product_label(), Perfume matching: brand and concentration are mandatory; fuzzy matching only app (+22 more)

### Community 32 - "Variant Extraction Fields"
Cohesion: 0.12
Nodes (16): attribute, script, type, additionalProperties, allOf, description, properties, type (+8 more)

### Community 33 - "_ResultRow"
Cohesion: 0.09
Nodes (55): Match, match_title(), parse_query(), PerfumeQuery, The perfume being looked for, split into its three identity parts.      `concent, One site title judged against the query.      `concentration` is what the title, Split one typed line, "Dior Sauvage EDP", into the three identity parts.      Th, Judge one site title against a query, or None if it is not that perfume.      No (+47 more)

### Community 34 - "Fetch Strategy Probing"
Cohesion: 0.24
Nodes (7): _FixtureFetcher, FormData, Headers, Method, Path, Strategy, Serves one site's saved capture in place of the network.      Only three kinds o

### Community 35 - "Platform Field Mapping"
Cohesion: 0.18
Nodes (11): field_map, product_json, source, variants_path, required, additionalProperties, allOf, description (+3 more)

### Community 36 - "Shipping Config Schema"
Cohesion: 0.14
Nodes (14): free_shipping_threshold_kurus, shipping_cost_kurus, minimum, type, free_shipping_threshold_kurus, notes, shipping, shipping_cost_kurus (+6 more)

### Community 37 - "_trial"
Cohesion: 0.17
Nodes (19): _classify_single_separator(), format_price(), _parse_number(), parse_price(), parse_size_ml(), Decimal, Number parsing and formatting for prices and volumes, plus text folding.  This i, Decide whether a lone separator marks a fraction or a thousands group.      Retu (+11 more)

### Community 38 - "TUI Confirm Dialog"
Cohesion: 0.13
Nodes (46): BaseModel, AcceptedSearch, _add_basket_item(), _AppState, BasketAddRequest, BasketQtyRequest, The FastAPI app: a thin HTTP/WS wrapper around the Faz 1 services.  No business, _read_basket() (+38 more)

### Community 39 - "TUI App Shell"
Cohesion: 0.12
Nodes (5): HeaderSelected, RowSelected, Any, The initial screen: search bar, streaming results table, notices, footer., SearchScreen

### Community 40 - "Fetch Backends"
Cohesion: 0.14
Nodes (14): curl_cffi, httpx, playwright, result_item, result_title, result_url, strategy, url_template (+6 more)

### Community 41 - "HTTP Request Schema"
Cohesion: 0.14
Nodes (14): GET, POST, properties, default, enum, type, type, type (+6 more)

### Community 42 - "Fixture Fetcher (Tests)"
Cohesion: 0.05
Nodes (56): Client, check_enabled(), check_for_update(), DownloadProgress, fetch_latest_release(), handoff_command(), _installer_asset(), is_newer() (+48 more)

### Community 43 - "FieldConfidence"
Cohesion: 0.22
Nodes (3): _FakeBrowser, _FakePage, Any

### Community 44 - "Decant Variant Rules"
Cohesion: 0.11
Nodes (26): api, ApiError, Window, App(), Toast, View, root, daysSince() (+18 more)

### Community 45 - "_ResultRow"
Cohesion: 0.10
Nodes (54): TestClient, _auth(), _client(), db_path(), _ok_result(), Any, MonkeyPatch, Path (+46 more)

### Community 46 - "Offline Validation Fixtures"
Cohesion: 0.25
Nodes (8): type, additionalProperties, type, body, request_headers, additionalProperties, description, type

### Community 47 - "JsonLdProduct"
Cohesion: 0.11
Nodes (19): BasketResponse, basket(), basketRow(), resultRow(), scenario(), splitCombination(), compile(), DEFAULT_CONFIG (+11 more)

### Community 48 - "._build_rows"
Cohesion: 0.07
Nodes (49): collect_prices(), DiscoveryReport, FieldConfidence, _flatten_defaults(), _format_choice(), _format_confidence(), _format_defaults(), _format_fingerprint() (+41 more)

### Community 49 - "_RecordingFetcher"
Cohesion: 0.05
Nodes (93): add_basket_item(), Write a whole scan at once and return how many prices were recorded.      Every, Add a size of a perfume to the basket, and return the basket_item_id.      The p, write_snapshots(), conn(), Connection, Path, Tests for parfum_finder.store: the timestamp helper and the schema.  The one har (+85 more)

### Community 50 - "Profile Age Checks"
Cohesion: 0.23
Nodes (22): Check one site's profile against that site's saved fixtures.      Never raises f, validate_offline(), _corrupted_sites_dir(), _iso_days_ago(), Any, Path, M5's own criterion: when a profile stops agreeing with its site's real markup, o, A sites/ directory holding one real profile with fields overwritten.      The re (+14 more)

### Community 51 - "._refresh_table"
Cohesion: 0.11
Nodes (25): apply_variant_rules(), Turn raw size rows into decant variants, dropping what is not a decant.      Thr, _count_result_cards(), _first_result_url(), _LayerUnavailable, _probe_layer(), Any, Exception (+17 more)

### Community 52 - "FetchResult"
Cohesion: 0.67
Nodes (3): SiteScenario, The two or three lines one site's scenario takes up on screen., _scenario_block()

### Community 53 - "conftest.py"
Cohesion: 0.23
Nodes (11): Any, Connection, Command-line entry point.  Subcommands will be added incrementally as the projec, Scan every perfume against every site and print each site as it lands.      One, Write one site's rows in a transaction of its own.      Per site rather than per, One line per site: which site, how it went, and what it said.      The site id i, _report_line(), _scan_all() (+3 more)

### Community 54 - "Endpoint Schema Fields"
Cohesion: 0.22
Nodes (9): result_item, result_title, result_url, url_template, search, additionalProperties, description, required (+1 more)

### Community 55 - "apply_variant_rules"
Cohesion: 0.20
Nodes (10): _age_line(), format_live_report(), format_report(), Every check run against one site's profile, in the order they ran.      Checks s, Whether the profile is old enough to be worth re-discovering., Render the validations as the offline half of the report in APP_FLOW §6.      A, The age note for one site, or None when its age is unremarkable.      A profile, Render offline and live results side by side, as APP_FLOW §6 shows them.      Bo (+2 more)

### Community 56 - "Request Schema Fields"
Cohesion: 0.04
Nodes (45): jsdom, motion, @playwright/test, react, react-dom, @testing-library/jest-dom, @testing-library/react, @testing-library/user-event (+37 more)

### Community 57 - "_FixtureFetcher"
Cohesion: 0.29
Nodes (7): in_stock, price, size_raw, additionalProperties, required, type, field_map

### Community 58 - "setup_logging"
Cohesion: 0.07
Nodes (27): DOM, DOM.Iterable, e2e, ES2022, playwright.config.ts, src, tests, vite/client (+19 more)

### Community 59 - "_named_profile"
Cohesion: 0.15
Nodes (23): _close_browser(), _fetch_curl_cffi(), _fetch_httpx(), _fetch_playwright(), FetchResult, _launch_browser(), PlaywrightNoResponse, PlaywrightNotInstalled (+15 more)

### Community 60 - "_wait_for_table"
Cohesion: 0.29
Nodes (7): items, type, type, items, type, exclude_keywords, needs_review

### Community 61 - "._apply_scan_event"
Cohesion: 0.15
Nodes (5): Changed, Close out a submit that named no perfume anyone could look for., Show what storage already knows, then go to the shops for the rest.          `fo, Empty the table for a new scan.          The columns are the same every time now, Submitted

### Community 62 - "snapshot_rows"
Cohesion: 0.17
Nodes (12): Turn one site's hits into the rows write_snapshots is ready to store.      Share, snapshot_rows(), A shop's imitation must not be stored as the perfume it imitates.      The clone, Another house's bottle on the same results page must not enter this history., EDT and EDP are different products, so the row has to say which one this was., Layton' finding 'Layton Exclusif' must not price the two as one bottle.      A s, A shop that just writes the same bottle differently must not fork it.      Filin, test_snapshot_rows_drops_a_title_the_matcher_rejects() (+4 more)

### Community 64 - "validate_live"
Cohesion: 0.06
Nodes (57): _as_str(), _balanced_value(), _build_offer(), _build_product(), _coerce_in_stock(), _collect_offers(), _collect_products(), _collect_variants() (+49 more)

### Community 65 - "_named_profile"
Cohesion: 0.21
Nodes (15): probe(), Fetch `url` with every strategy and report diagnostics for each.      timeout_s, MonkeyPatch, Tests for parfum_finder.probe.  probe() always tries all three strategies -- the, test_probe_counts_jsonld_product_and_platform_signature(), test_probe_counts_product_across_jsonld_root_shapes(), test_probe_counts_product_markup_without_any_jsonld(), test_probe_counts_products_nested_below_the_top_level() (+7 more)

### Community 67 - "extract_embedded_variants"
Cohesion: 0.40
Nodes (3): format_age(), Turn a price age in days into the words the age column shows., test_format_age_reads_as_words_not_a_timestamp()

### Community 68 - "JsonLdProduct"
Cohesion: 0.40
Nodes (3): UpdateDialog(), INFO, updateProgress()

### Community 71 - "exclude_keywords"
Cohesion: 0.40
Nodes (5): price_history(), Row, Return one variant's past readings, newest first, capped at limit.      Empty fo, No history yet is a normal state for a variant, not an error to raise on., test_price_history_is_empty_for_an_unknown_variant()

### Community 72 - "write_snapshots"
Cohesion: 0.50
Nodes (3): The template this site's profile would be based on, if any., Which of the matching templates gets applied, or None for none of them.      One, _resolve_platform()

### Community 77 - "_collect_products"
Cohesion: 0.25
Nodes (8): Split one typed line into the perfumes it asks for, on " - ".      The separator, split_queries(), test_a_hyphen_inside_a_brand_name_does_not_split_the_search(), test_a_line_naming_three_perfumes_is_read_as_three_searches(), test_a_piece_that_names_no_perfume_survives_to_be_complained_about(), test_a_stray_separator_is_not_worth_failing_over(), test_one_perfume_is_still_one_search(), test_the_same_perfume_typed_twice_is_scanned_once()

### Community 81 - "ScanStatus.tsx"
Cohesion: 0.17
Nodes (18): FastAPI, create_app(), HTTP/WS backend for the GUI frontend. See api/app.py for the app itself., encode_basket_refresh_event(), encode_basket_report(), encode_basket_row(), encode_result_row(), encode_scan_event() (+10 more)

### Community 84 - "BasketScreen.tsx"
Cohesion: 0.26
Nodes (11): ProgressBar(), formatAge(), formatMl(), formatPerMl(), formatPrice(), formatPriceWhole(), BasketScreen(), cheapestSite() (+3 more)

### Community 85 - "Static"
Cohesion: 0.40
Nodes (3): ComposeResult, ComposeResult, Static

### Community 86 - "test_paths.py"
Cohesion: 0.38
Nodes (11): _freeze(), MonkeyPatch, Path, Tests for parfum_finder.paths: frozen vs. source path resolution.  `ensure_user_, A source run has nothing to seed: resource_dir and user_data_dir are     already, test_ensure_user_data_is_a_noop_when_not_frozen(), test_ensure_user_data_never_overwrites_an_edited_file(), test_ensure_user_data_seeds_sites_platforms_and_hooks() (+3 more)

### Community 87 - "helpers.ts"
Cohesion: 0.47
Nodes (7): addFirstRow(), authToken(), clearBasket(), openApp(), search(), searchButton(), tab()

### Community 88 - ".__call__"
Cohesion: 0.31
Nodes (7): _DeadSite, FormData, Headers, Method, Strategy, A host that cannot be reached at all., test_an_unreachable_site_is_not_reported_as_a_broken_profile()

### Community 93 - "ws.ts"
Cohesion: 0.43
Nodes (6): authToken(), readDetail(), request(), refusalReason(), streamUrl(), useEventStream()

### Community 94 - "Arayüz testleri"
Cohesion: 0.40
Nodes (4): Arayüz testleri, jsdom katmanı (`tests/`), Ne test edilmiyor, Tarayıcı katmanı (`e2e/`)

## Knowledge Gaps
- **224 isolated node(s):** `parfum-finder`, `$schema`, `$id`, `title`, `description` (+219 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **6 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `SearchScreen` connect `TUI App Shell` to `TUI App & Screens`, `_ResultRow`, `Title Matcher`, `extract_embedded_variants`, `Search/Basket Domain Models`, `Search Engine per Site`, `TUI Confirm Dialog`, `_css_variant`, `ResultRow`, `Search TUI Screen`, `Static`, `Price/Size Normalization`, `._apply_scan_event`?**
  _High betweenness centrality (0.038) - this node is a cross-community bridge._
- **Why does `BasketScreen` connect `Price/Size Normalization` to `TUI App & Screens`, `Site Profiles & Templates`, `Title Matcher`, `TUI Confirm Dialog`, `TUI App Shell`, `Basket Optimizer Core`, `Static`?**
  _High betweenness centrality (0.025) - this node is a cross-community bridge._
- **Why does `SiteRunner` connect `Title Matcher` to `Search/Basket Domain Models`, `TUI Confirm Dialog`, `TUI App Shell`, `Search Engine Core`, `_css_variant`, `_ResultRow`, `ScanStatus.tsx`, `Offline Profile Validation`, `Candidate Filtering`, `Price/Size Normalization`, `_named_profile`?**
  _High betweenness centrality (0.023) - this node is a cross-community bridge._
- **Are the 25 inferred relationships involving `SiteResult` (e.g. with `RawVariant` and `Fetcher`) actually correct?**
  _`SiteResult` has 25 INFERRED edges - model-reasoned connections that need verification._
- **Are the 23 inferred relationships involving `PerfumeQuery` (e.g. with `BasketPriceExcluded` and `BasketRefreshFinished`) actually correct?**
  _`PerfumeQuery` has 23 INFERRED edges - model-reasoned connections that need verification._
- **Are the 14 inferred relationships involving `SearchScreen` (e.g. with `ParfumFinderApp` and `SiteRunner`) actually correct?**
  _`SearchScreen` has 14 INFERRED edges - model-reasoned connections that need verification._
- **What connects `parfum-finder`, `$schema`, `$id` to the rest of the system?**
  _224 weakly-connected nodes found - possible documentation gaps or missing edges._