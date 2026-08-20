# Graph Report - parfum-finder  (2026-08-21)

## Corpus Check
- 125 files · ~310,215 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2497 nodes · 7039 edges · 99 communities (95 shown, 4 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 493 edges (avg confidence: 0.55)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `54ccaf8d`
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
- .__init__
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
- `_NoRootParser` --uses--> `ExtractionFailed`  [INFERRED]
  tests/test_engine.py → src/parfum_finder/engine.py
- `test_a_product_page_with_no_root_names_its_body_size()` --indirect_call--> `ExtractionFailed`  [INFERRED]
  tests/test_engine.py → src/parfum_finder/engine.py

## Import Cycles
- 3-file cycle: `src/parfum_finder/__init__.py -> src/parfum_finder/cli.py -> src/parfum_finder/store.py -> src/parfum_finder/__init__.py`
- 3-file cycle: `src/parfum_finder/__init__.py -> src/parfum_finder/cli.py -> src/parfum_finder/logging_setup.py -> src/parfum_finder/__init__.py`
- 3-file cycle: `src/parfum_finder/__init__.py -> src/parfum_finder/cli.py -> src/parfum_finder/profiles.py -> src/parfum_finder/__init__.py`
- 3-file cycle: `src/parfum_finder/__init__.py -> src/parfum_finder/cli.py -> src/parfum_finder/validate.py -> src/parfum_finder/__init__.py`
- 4-file cycle: `src/parfum_finder/__init__.py -> src/parfum_finder/cli.py -> src/parfum_finder/discover.py -> src/parfum_finder/store.py -> src/parfum_finder/__init__.py`
- 4-file cycle: `src/parfum_finder/__init__.py -> src/parfum_finder/cli.py -> src/parfum_finder/discover.py -> src/parfum_finder/profiles.py -> src/parfum_finder/__init__.py`
- 4-file cycle: `src/parfum_finder/__init__.py -> src/parfum_finder/cli.py -> src/parfum_finder/engine.py -> src/parfum_finder/profiles.py -> src/parfum_finder/__init__.py`
- 4-file cycle: `src/parfum_finder/__init__.py -> src/parfum_finder/cli.py -> src/parfum_finder/validate.py -> src/parfum_finder/profiles.py -> src/parfum_finder/__init__.py`
- 5-file cycle: `src/parfum_finder/__init__.py -> src/parfum_finder/cli.py -> src/parfum_finder/store.py -> src/parfum_finder/engine.py -> src/parfum_finder/profiles.py -> src/parfum_finder/__init__.py`
- 5-file cycle: `src/parfum_finder/__init__.py -> src/parfum_finder/cli.py -> src/parfum_finder/validate.py -> src/parfum_finder/engine.py -> src/parfum_finder/profiles.py -> src/parfum_finder/__init__.py`

## Hyperedges (group relationships)
- **Sites Implementing Variant Pattern C (embedded JSON)** — docs_discovery_report_venco_site, docs_discovery_report_decantall_site, docs_discovery_report_luxurydekant_site, docs_discovery_report_ruxangroup_site, architecture_md_variant_pattern_c [EXTRACTED 1.00]
- **İdeasoft Platform Sites and Endpoint** — docs_discovery_report_dekantparfum_site, docs_discovery_report_dekantdoktoru_site, docs_discovery_report_ideasoft_related_options_endpoint, platforms_readme_ideasoft_json [EXTRACTED 1.00]
- **discover Command Output Artifacts (profile + fixtures + CI validation)** — architecture_md_discover_flow, sites_readme_sites_dir, fixtures_readme_fixtures_dir, github_workflows_ci_validate_profiles_step, architecture_md_validate_command [INFERRED 0.85]

## Communities (99 total, 4 thin omitted)

### Community 0 - "TUI App & Screens"
Cohesion: 0.09
Nodes (100): The Textual-based terminal UI: search and basket screens., _app(), _basket(), _cells(), _days_ago(), _leg(), _ok(), _open_basket() (+92 more)

### Community 1 - "Site Profiles & Templates"
Cohesion: 0.06
Nodes (79): _check_hook_kinds(), deep_merge(), _load_json(), load_platform_template(), load_platform_templates(), load_site_hooks(), load_site_profile(), Any (+71 more)

### Community 2 - "Title Matcher"
Cohesion: 0.18
Nodes (19): FastAPI, create_app(), HTTP/WS backend for the GUI frontend. See api/app.py for the app itself., encode_basket_refresh_event(), encode_basket_report(), encode_basket_row(), encode_result_row(), encode_scan_event() (+11 more)

### Community 3 - "HTTP/Browser Fetching"
Cohesion: 0.11
Nodes (36): browser_session(), fetch(), PlaywrightNotInstalled, Strategy, Fetch one URL using exactly the given strategy.      `method`/`data` exist for t, Yield a fetcher that keeps one browser for every playwright page it reads., The "playwright" strategy was requested but cannot run at all.      Covers both, _reject_playwright_post() (+28 more)

### Community 4 - "Search/Basket Domain Models"
Cohesion: 0.06
Nodes (133): Screen, ProductCandidate, One hit on a search results page, before its product page is opened.      `raw_t, One decant size of one product, in the units the database stores.      Tenths of, A candidate together with the decant sizes its product page offers., SearchHit, Variant, connect() (+125 more)

### Community 5 - "Search Engine per Site"
Cohesion: 0.08
Nodes (37): _load_profiles(), Any, Path, _read_basket(), _recent_searches(), _record_search(), _remove_basket_item(), _set_basket_qty() (+29 more)

### Community 6 - "Platform Discovery Flow"
Cohesion: 0.15
Nodes (59): PlatformChooser, _ask_chooser(), discover(), Put the question only when there is one, and hold the answer to it.      An answ, Measure the strategies a site needs, then read its JSON-LD with the winner., _attempt(), _fake_probe(), Any (+51 more)

### Community 7 - "CLI Entry Points"
Cohesion: 0.10
Nodes (52): CaptureFixture, ask_which_platform(), main(), Path, Scan every site for the perfumes named, store what came back, print it.      One, Ask at the terminal which of several matching templates to apply.      Asked whi, run_search(), A multi-site price and stock comparison tool for perfume decants.  Includes a sh (+44 more)

### Community 8 - "Architecture Rationale Docs"
Cohesion: 0.05
Nodes (53): basket Subset Enumeration + Local Improvement Algorithm, basket Optimizer (optimize function), Clone/Original Distinction (KLON ← <orijinal>), discover Discovery Flow, engine Concurrency Model (parallel sites, serial within site), Extraction Ladder (jsonld/endpoint/embedded/css), Fail-loud / status=suspect policy, hooks/<id>.py Escape Hatch (+45 more)

### Community 9 - "Search Engine Core"
Cohesion: 0.07
Nodes (59): CacheKey, HTMLParser, _check_empty_search(), _check_variant_control(), _fetch_page(), _headers(), _is_excluded(), _jitter_s() (+51 more)

### Community 10 - "Basket Optimizer Core"
Cohesion: 0.10
Nodes (52): Collection, BasketRow, _score_basket(), basket_inputs(), BasketItem, build_basket_rows(), optimize(), BasketRow (+44 more)

### Community 11 - "Basket Store & Pricing"
Cohesion: 0.09
Nodes (51): ExtractionFailed, RuntimeError, A page answered but gave up nothing, where something was expected.      This is, Run one query against one site and read every hit's sizes.      Everything site-, search_site(), _named_profile(), Any, Path (+43 more)

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
Nodes (22): Check, _count_result_cards(), _first_result_url(), _LayerUnavailable, _no_results_check(), _probe_layer(), _probe_other_layers(), Any (+14 more)

### Community 16 - "Schema Field Patterns"
Cohesion: 0.05
Nodes (39): css, embedded_json, endpoint, jsonld, format, pattern, type, pattern (+31 more)

### Community 17 - "Offline Profile Validation"
Cohesion: 0.12
Nodes (39): Run one site and classify what came back instead of raising.      It is also whe, run_site(), FetchResult, One fetched page, uniform regardless of which strategy produced it., _counting_fetcher(), _profile(), Exception, Answer each call with the next canned result, then repeat the last one. (+31 more)

### Community 18 - "Playwright Errors"
Cohesion: 0.08
Nodes (34): Any, Connection, Command-line entry point.  Subcommands will be added incrementally as the projec, Scan every perfume against every site and print each site as it lands.      One, Write one site's rows in a transaction of its own.      Per site rather than per, One line per site: which site, how it went, and what it said.      The site id i, _report_line(), _scan_all() (+26 more)

### Community 19 - "Search TUI Screen"
Cohesion: 0.08
Nodes (41): find_header_columns(), find_match(), open_worksheet(), Any, Exception, Path, Protocol, Writing a search result onto the user's own Google Sheets wishlist.  The wishlis (+33 more)

### Community 20 - "Snapshot Writing"
Cohesion: 0.18
Nodes (21): grouped_value(), Decimal, ResultRow, What each site charges for the product a block is about.      One entry per site, The default order: typed order, product, site, size.      The typed order comes, The order once a column has been picked: the site layer drops out.      Asking f, site_ranks(), sorted_value() (+13 more)

### Community 21 - "Candidate Filtering"
Cohesion: 0.17
Nodes (35): Connection, Mirror site profiles into the sites table and return how many were written., sync_to_db(), now_iso(), Return the current UTC time as 'YYYY-MM-DDTHH:MM:SSZ'.      Every timestamp writ, Any, _basket_row(), _collect() (+27 more)

### Community 22 - "Basket Site Scenarios"
Cohesion: 0.17
Nodes (19): format_live_report(), Run one site's profile against the real site.      Same contract as offline mode, Render offline and live results side by side, as APP_FLOW §6 shows them.      Bo, validate_live(), _DeadSite, _FakeSite, _fixture_site(), M5's own criterion: when a profile stops agreeing with its site's real markup, o (+11 more)

### Community 23 - "Price/Size Normalization"
Cohesion: 0.08
Nodes (33): BasketReport, compare_split_to_best_full(), _label(), Basket scenario evaluation. A pure function, no network access, no sqlite.  Inpu, Every site's single-site scenario, split by whether it covers everything.      A, One site's share of a split basket: what to buy there and what it costs.      `s, The cheapest basket split the search found. A heuristic, not a proof.      Every, Name one basket line the way a missing-item warning has to read it. (+25 more)

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
Cohesion: 0.11
Nodes (17): AddButton(), Badge(), BadgeKind, ConfirmDialog(), ScanStatus(), VerdictAddButton(), basketKey(), Block (+9 more)

### Community 30 - "Store Timestamp Tests"
Cohesion: 0.11
Nodes (13): compile(), DEFAULT_CONFIG, EMPTY_BASKET, FakeServer, FakeWebSocket, installFakeServer(), NO_UPDATE, RecordedRequest (+5 more)

### Community 31 - "Live Profile Validation"
Cohesion: 0.10
Nodes (29): Pattern, _brand_pattern(), _canonical(), _canonical_brands(), _covers(), _ends_with(), _index_of(), listing_filter() (+21 more)

### Community 32 - "Variant Extraction Fields"
Cohesion: 0.12
Nodes (16): attribute, script, type, additionalProperties, allOf, description, properties, type (+8 more)

### Community 33 - "_ResultRow"
Cohesion: 0.09
Nodes (38): parse_query(), Split one typed line into the perfumes it asks for, on " - ".      The separator, Split one typed line, "Dior Sauvage EDP", into the three identity parts.      Th, Whether a search result's own listing text is worth opening the page for.      J, split_queries(), title_could_match(), Tests for parfum_finder.matcher.  The thing being defended here is not "does it, test_a_brand_the_shop_writes_out_in_full_does_not_cost_the_match() (+30 more)

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
Cohesion: 0.17
Nodes (19): _classify_single_separator(), format_price(), _parse_number(), parse_price(), parse_size_ml(), Decimal, Number parsing and formatting for prices and volumes, plus text folding.  This i, Decide whether a lone separator marks a fraction or a thousands group.      Retu (+11 more)

### Community 38 - "TUI Confirm Dialog"
Cohesion: 0.16
Nodes (38): BaseModel, AcceptedSearch, _add_basket_item(), _AppState, BasketAddRequest, BasketQtyRequest, The FastAPI app: a thin HTTP/WS wrapper around the Faz 1 services.  No business, RefreshRequest (+30 more)

### Community 39 - "TUI App Shell"
Cohesion: 0.10
Nodes (8): Changed, HeaderSelected, The initial screen: search bar, streaming results table, notices, footer., Close out a submit that named no perfume anyone could look for., Show what storage already knows, then go to the shops for the rest.          `fo, Empty the table for a new scan.          The columns are the same every time now, SearchScreen, Submitted

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
Cohesion: 0.16
Nodes (7): PlaywrightNoResponse, RuntimeError, Navigation completed but playwright returned no Response object.      Its own ty, _FakeBrowser, _FakePage, Any, test_fetch_playwright_no_response_raises_its_own_error_type()

### Community 44 - "Decant Variant Rules"
Cohesion: 0.14
Nodes (22): api, ApiError, Window, Toast, View, UpdateDialog(), daysSince(), SearchScreen() (+14 more)

### Community 45 - "_ResultRow"
Cohesion: 0.10
Nodes (54): TestClient, _auth(), _client(), db_path(), _ok_result(), Any, MonkeyPatch, Path (+46 more)

### Community 46 - "Offline Validation Fixtures"
Cohesion: 0.25
Nodes (8): type, additionalProperties, type, body, request_headers, additionalProperties, description, type

### Community 47 - "JsonLdProduct"
Cohesion: 0.15
Nodes (10): App(), root, BasketResponse, BestCombination, basket(), basketRow(), resultRow(), scenario() (+2 more)

### Community 48 - "._build_rows"
Cohesion: 0.07
Nodes (49): collect_prices(), DiscoveryReport, FieldConfidence, _flatten_defaults(), _format_choice(), _format_confidence(), _format_defaults(), _format_fingerprint() (+41 more)

### Community 49 - "_RecordingFetcher"
Cohesion: 0.09
Nodes (37): add_basket_item(), Add a size of a perfume to the basket, and return the basket_item_id.      The p, Connection, Two lines added within the same second must still read back the same way twice., A basket line nobody sells must still be visible via basket_lines.      basket_p, A stale reading must never outrank the one taken after it.      latest_prices al, A 10 ml listing must never fill a basket line asking for 5 ml.      The matrix j, Whether an out-of-stock price counts as missing is the caller's call.      Dropp (+29 more)

### Community 50 - "Profile Age Checks"
Cohesion: 0.17
Nodes (25): format_report(), Check one site's profile against that site's saved fixtures.      Never raises f, Validate every site, or just the ones named.      Serial rather than concurrent:, Render the validations as the offline half of the report in APP_FLOW §6.      A, validate_all_offline(), validate_offline(), _corrupted_sites_dir(), _iso_days_ago() (+17 more)

### Community 51 - "._refresh_table"
Cohesion: 0.27
Nodes (13): apply_variant_rules(), Turn raw size rows into decant variants, dropping what is not a decant.      Thr, _row(), test_a_keyword_in_the_size_label_excludes_the_row_too(), test_a_literal_zero_price_reads_as_no_price_not_a_free_perfume(), test_a_size_at_the_threshold_is_a_bottle_whatever_it_calls_itself(), test_a_size_that_cannot_be_read_is_dropped(), test_an_uppercase_turkish_keyword_still_matches() (+5 more)

### Community 52 - "FetchResult"
Cohesion: 0.14
Nodes (29): Match, match_title(), PerfumeQuery, The perfume being looked for, split into its three identity parts.      `concent, One site title judged against the query.      `concentration` is what the title, Judge one site title against a query, or None if it is not that perfume.      No, test_a_brand_needs_all_of_its_words_not_one(), test_a_brand_only_query_matches_a_title_that_is_only_that_brand() (+21 more)

### Community 53 - "conftest.py"
Cohesion: 0.15
Nodes (18): extract_embedded_variants(), extract_jsonld_variants(), _flatten_jsonld(), Rung 1: read the page's JSON-LD as flat variant rows.      A product that declar, Turn one Product and everything under it into rows., Rung 3: read the JSON blob the page carries but does not display.      Two shape, _fixture(), Read a captured product page. (+10 more)

### Community 54 - "Endpoint Schema Fields"
Cohesion: 0.22
Nodes (9): result_item, result_title, result_url, url_template, search, additionalProperties, description, required (+1 more)

### Community 55 - "apply_variant_rules"
Cohesion: 0.17
Nodes (12): product_label(), Reduce a site's own title to the product it is about, spelled one way.      What, Split a title into what the bottle is and what it says it imitates.      The sec, _split_clone_reference(), test_a_clone_is_labelled_by_the_bottle_it_is_and_not_what_it_imitates(), test_a_longer_named_bottle_does_not_join_the_shorter_ones_block(), test_a_title_with_no_product_words_left_has_no_label(), test_every_shops_spelling_of_one_bottle_lands_in_one_block() (+4 more)

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
Cohesion: 0.19
Nodes (19): _close_browser(), _close_session_browser(), _fetch_curl_cffi(), _fetch_httpx(), _fetch_playwright(), _folded(), _launch_browser(), Any (+11 more)

### Community 60 - "_wait_for_table"
Cohesion: 0.24
Nodes (14): fetch_latest_release(), En son yayımlanmış sürüm, ya da ulaşılamadıysa None.      /releases/latest tasla, _enable_checks(), _patch_get(), MonkeyPatch, Tests for parfum_finder.updater: the version compare, the release read, and the, No network is not an error the user has to be told about.      The check runs un, The .exe is what gets downloaded, whatever else is attached.      Releases carry (+6 more)

### Community 61 - "._apply_scan_event"
Cohesion: 0.24
Nodes (3): RowSelected, ResultRow, Row

### Community 62 - "snapshot_rows"
Cohesion: 0.14
Nodes (20): One call has to leave a row the search table can read straight off.      The cal, The old price has to survive, and it must not become a second variant.      Appe, first_seen is what says how long a shop has carried a size., The title and URL are information, not identity.      A shop that rewords a list, EDT and EDP are different products at different prices.      Folding them into o, A sold-out size often shows no price at all, and 0 would mean free.      Writing, The column is 0/1, so the tri-state has to land somewhere on purpose.      Unkno, raw_title is the audit trail for a wrong match, so it cannot be blank.      A ro (+12 more)

### Community 64 - "validate_live"
Cohesion: 0.18
Nodes (16): _age_of(), live_query(), _path(), profile_age_days(), datetime, Profile staleness checks. Two modes: offline (against saved fixtures) and live (, A URL's path with no trailing slash, for comparing two spellings of one page., Every site that has a profile, sorted so reports read the same way twice. (+8 more)

### Community 65 - "_named_profile"
Cohesion: 0.22
Nodes (6): format_age(), format_ml(), Format a volume for display (dot-decimal): Decimal('1.5') -> '1.5 ml'., Turn a price age in days into the words the age column shows., BasketRow, test_format_age_reads_as_words_not_a_timestamp()

### Community 67 - "extract_embedded_variants"
Cohesion: 0.20
Nodes (10): cached_prices(), Return the latest stored price of every size of this perfume, per site.      Bra, The search screen's second search must be answered with today's numbers.      Tw, A search that named no concentration is asking for all of them.      "" means "a, A price nobody will scan again may not be offered as a result.      Refreshing i, Nothing on record is the state before a first search, not an error.      The sea, test_cached_prices_is_empty_for_a_perfume_nobody_scanned(), test_cached_prices_leaves_out_a_disabled_site() (+2 more)

### Community 68 - "JsonLdProduct"
Cohesion: 0.18
Nodes (4): _FakeClient, _FakeStreamResponse, Any, Exception

### Community 71 - "exclude_keywords"
Cohesion: 0.29
Nodes (7): price_history(), Row, Return one variant's past readings, newest first, capped at limit.      Empty fo, The trend panel reads row 0 as the latest reading, so order is the point.      A, No history yet is a normal state for a variant, not an error to raise on., test_price_history_is_empty_for_an_unknown_variant(), test_price_history_is_newest_first_and_capped_at_limit()

### Community 72 - "write_snapshots"
Cohesion: 0.50
Nodes (3): The template this site's profile would be based on, if any., Which of the matching templates gets applied, or None for none of them.      One, _resolve_platform()

### Community 73 - "_css_variant"
Cohesion: 0.29
Nodes (5): _age_line(), Every check run against one site's profile, in the order they ran.      Checks s, Whether the profile is old enough to be worth re-discovering., The age note for one site, or None when its age is unremarkable.      A profile, SiteValidation

### Community 74 - "ConfirmDialog.tsx"
Cohesion: 0.43
Nodes (6): authToken(), readDetail(), request(), refusalReason(), streamUrl(), useEventStream()

### Community 75 - "ResultRow"
Cohesion: 0.15
Nodes (16): _as_str(), _build_offer(), _build_product(), _collect_offers(), _collect_variants(), JsonLdOffer, _parse_availability(), One offer attached to a product.      A plain Offer fills `price`. An AggregateO (+8 more)

### Community 76 - "SplitPlan"
Cohesion: 0.11
Nodes (22): _coerce_in_stock(), _css_variant(), extract_css_variants(), extract_endpoint_variants(), _map_variant(), _parse_price_value(), Any, Decimal (+14 more)

### Community 77 - "_collect_products"
Cohesion: 0.29
Nodes (7): items, type, type, items, type, exclude_keywords, needs_review

### Community 78 - "exclude_keywords"
Cohesion: 0.53
Nodes (4): FormData, Headers, Method, Strategy

### Community 79 - "AddButton.tsx"
Cohesion: 0.50
Nodes (4): One search line, then the same line with the brand written the other ways., search_spellings(), test_a_brand_nobody_abbreviates_is_asked_for_once(), test_the_typed_spelling_is_asked_first_and_the_rest_only_follow()

### Community 80 - "write_snapshots"
Cohesion: 0.11
Nodes (25): Turn one site's hits into the rows write_snapshots is ready to store.      Share, Write a whole scan at once and return how many prices were recorded.      Every, snapshot_rows(), write_snapshots(), A shop's imitation must not be stored as the perfume it imitates.      The clone, The drop happens here so no caller can forget it.      Both the CLI and the scre, A slow site must not spread one reading across several timestamps.      Rows wri, The number reported is what landed in the history, not what was offered. (+17 more)

### Community 81 - "run_sites"
Cohesion: 0.08
Nodes (63): Lock, Pressed, _paced_fetcher(), Protocol, What one site had to say about one query, and how much to trust it.      Four st, One site's pacing state, for as long as whoever holds it says.      The gate and, Wrap a fetcher so one site's requests go out one at a time, spaced apart.      T, What a caller needs of run_site, as a type callers can stand a fake in for. (+55 more)

### Community 82 - "test_connect_is_idempotent_on_an_existing_database"
Cohesion: 0.18
Nodes (9): BaseHTTPRequestHandler, _Handler, _playwright_usable(), MonkeyPatch, Shared pytest fixtures.  A local HTTP server used by fetch/probe tests: real req, Whether the playwright rung can actually run here, binary included.      Checkin, Record every delay the engine asks for instead of serving it.      Waiting for r, server_url() (+1 more)

### Community 83 - "DownloadProgress"
Cohesion: 0.22
Nodes (4): Client, DownloadProgress, İndirmeyi başlatır. Zaten çalışıyorsa None., state: idle | downloading | ready | installing | error.

### Community 84 - "BasketScreen.tsx"
Cohesion: 0.19
Nodes (15): ProgressBar(), formatAge(), formatMl(), formatPerMl(), formatPrice(), formatPriceWhole(), BasketScreen(), cheapestSite() (+7 more)

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
Cohesion: 0.40
Nodes (3): ComposeResult, ComposeResult, Static

### Community 90 - "BasketRow"
Cohesion: 0.14
Nodes (20): _balanced_value(), _collect_products(), _embedded_documents(), _has_type(), _loads_or_skip(), _parse_selector(), Node, Extraction ladder: JSON-LD -> platform JSON endpoint -> embedded JS state -> CSS (+12 more)

### Community 91 - "ResultRow"
Cohesion: 0.29
Nodes (7): in_stock, price, size_raw, additionalProperties, required, type, field_map

### Community 92 - "MonkeyPatch"
Cohesion: 0.40
Nodes (5): _NoRootParser, MonkeyPatch, Stands in for HTMLParser when a page's markup cannot be read at all.      select, test_a_product_page_with_no_root_names_its_body_size(), test_a_search_page_with_no_root_names_its_body_size()

### Community 94 - "Arayüz testleri"
Cohesion: 0.40
Nodes (4): Arayüz testleri, jsdom katmanı (`tests/`), Ne test edilmiyor, Tarayıcı katmanı (`e2e/`)

### Community 96 - ".__init__"
Cohesion: 0.18
Nodes (11): CandidateFilter, _candidates_to_open(), Path, Run every site against one query, all at once, and report each separately., Narrow the search results down to the pages worth a request.      The first one, run_sites(), test_a_dead_site_does_not_take_the_others_down(), test_a_profile_that_breaks_on_setup_is_contained_too() (+3 more)

### Community 99 - "cached_prices"
Cohesion: 0.12
Nodes (18): conn(), Path, Tests for parfum_finder.store: the timestamp helper and the schema.  The one har, A disabled site loses its basket column, but an enabled quiet one keeps one., NULL means the site has no free shipping tier at all, not a threshold of zero., An update aimed at a row that isn't there means the caller is out of sync., The recents list has five slots, so a repeat must not consume two.      Someone, A snapshot pointing at a variant that doesn't exist has to be rejected.      SQL (+10 more)

## Knowledge Gaps
- **224 isolated node(s):** `parfum-finder`, `$schema`, `$id`, `title`, `description` (+219 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `SearchScreen` connect `TUI App Shell` to `test_an_unreadable_tag_never_counts_as_an_update`, `_named_profile`, `TUI App & Screens`, `Search/Basket Domain Models`, `Search Engine per Site`, `TUI Confirm Dialog`, `run_sites`, `Search TUI Screen`, `FetchResult`, `Candidate Filtering`, `_FixtureFetcher`, `._apply_scan_event`?**
  _High betweenness centrality (0.031) - this node is a cross-community bridge._
- **Why does `PlaywrightNotInstalled` connect `HTTP/Browser Fetching` to `Search/Basket Domain Models`, `Search Engine Core`, `Basket Store & Pricing`, `FieldConfidence`, `._build_rows`, `run_sites`, `Playwright Errors`, `test_connect_is_idempotent_on_an_existing_database`, `Offline Profile Validation`, `SQLite Store`, `_named_profile`, `MonkeyPatch`?**
  _High betweenness centrality (0.029) - this node is a cross-community bridge._
- **Why does `SiteRunner` connect `run_sites` to `Title Matcher`, `HTTP/Browser Fetching`, `Search/Basket Domain Models`, `TUI Confirm Dialog`, `TUI App Shell`, `Search Engine Core`, `_ResultRow`, `Offline Profile Validation`, `Candidate Filtering`, `Price/Size Normalization`, `_FixtureFetcher`?**
  _High betweenness centrality (0.026) - this node is a cross-community bridge._
- **Are the 25 inferred relationships involving `SiteResult` (e.g. with `RawVariant` and `Fetcher`) actually correct?**
  _`SiteResult` has 25 INFERRED edges - model-reasoned connections that need verification._
- **Are the 23 inferred relationships involving `PerfumeQuery` (e.g. with `BasketPriceExcluded` and `BasketRefreshFinished`) actually correct?**
  _`PerfumeQuery` has 23 INFERRED edges - model-reasoned connections that need verification._
- **Are the 14 inferred relationships involving `SearchScreen` (e.g. with `ParfumFinderApp` and `SiteRunner`) actually correct?**
  _`SearchScreen` has 14 INFERRED edges - model-reasoned connections that need verification._
- **What connects `parfum-finder`, `$schema`, `$id` to the rest of the system?**
  _224 weakly-connected nodes found - possible documentation gaps or missing edges._