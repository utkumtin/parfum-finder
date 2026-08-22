# Graph Report - parfum-finder  (2026-08-22)

## Corpus Check
- 131 files · ~311,536 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2511 nodes · 7010 edges · 108 communities (103 shown, 5 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 496 edges (avg confidence: 0.55)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `3d0c1423`
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
- BasketScreen.tsx
- _factory
- ._scan
- helpers.ts
- handoff_command
- set_basket_qty
- Static
- extract_endpoint_variants
- .__init__
- _jitter_s
- Arayüz testleri
- _retry_after_s
- DownloadProgress
- test_paths.py
- _FakeStreamResponse
- cached_prices
- test_gui.py
- UpdateDialog.test.tsx

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
- `_RecordingClient` --uses--> `ProductCandidate`  [INFERRED]
  tests/test_api.py → src/parfum_finder/engine.py

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

## Communities (108 total, 5 thin omitted)

### Community 0 - "TUI App & Screens"
Cohesion: 0.09
Nodes (100): The Textual-based terminal UI: search and basket screens., _app(), _basket(), _cells(), _days_ago(), _leg(), _ok(), _open_basket() (+92 more)

### Community 1 - "Site Profiles & Templates"
Cohesion: 0.18
Nodes (29): load_site_hooks(), Load hooks/<id>.py if that site has one, else return empty hooks.      A missing, Path, Tests for parfum_finder.profiles: loading, schema validation, platform merge.  T, test_load_platform_template_loads_and_validates(), test_load_platform_template_rejects_a_broken_template(), test_load_platform_templates_keys_them_by_file_name(), test_load_platform_templates_rejects_a_name_that_disagrees_with_its_file() (+21 more)

### Community 2 - "Title Matcher"
Cohesion: 0.17
Nodes (18): FastAPI, create_app(), HTTP/WS backend for the GUI frontend. See api/app.py for the app itself., encode_basket_refresh_event(), encode_basket_report(), encode_basket_row(), encode_result_row(), encode_scan_event() (+10 more)

### Community 3 - "HTTP/Browser Fetching"
Cohesion: 0.13
Nodes (31): browser_session(), fetch(), Strategy, Fetch one URL using exactly the given strategy.      `method`/`data` exist for t, Yield a fetcher that keeps one browser for every playwright page it reads., test_the_no_results_page_would_otherwise_read_as_suspect(), _fake_launch(), Event (+23 more)

### Community 4 - "Search/Basket Domain Models"
Cohesion: 0.07
Nodes (120): Screen, One decant size of one product, in the units the database stores.      Tenths of, A candidate together with the decant sizes its product page offers., SearchHit, Variant, Write one scan's reading of one size, and return its snapshot id.      The perfu, record_snapshot(), ParfumFinderApp (+112 more)

### Community 5 - "Search Engine per Site"
Cohesion: 0.17
Nodes (12): add_basket_item(), Add a size of a perfume to the basket, and return the basket_item_id.      The p, A basket line nobody sells must still be visible via basket_lines.      basket_p, A stale reading must never outrank the one taken after it.      latest_prices al, A 10 ml listing must never fill a basket line asking for 5 ml.      The matrix j, Whether an out-of-stock price counts as missing is the caller's call.      Dropp, A basket line for a perfume nobody has priced is a bug, not a state to keep., test_add_basket_item_refuses_a_perfume_with_no_price_on_record() (+4 more)

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
Nodes (57): HTMLParser, _check_variant_control(), _fetch_page(), _headers(), _is_excluded(), _jitter_s(), _page_evidence(), _page_offers_sizes() (+49 more)

### Community 10 - "Basket Optimizer Core"
Cohesion: 0.12
Nodes (44): BasketItem, optimize(), Prices, Score one site against the basket, or against a subset of it.      `item_ids` is, Score every enabled site against the whole basket and sort the results.      Sit, Search for the cheapest way to split the basket across several sites.      Retur, One line of the shopping list: a basket row, not a unit count.      `item_id` is, One site's shipping terms, read once and reused for every scenario.      `free_s (+36 more)

### Community 11 - "Basket Store & Pricing"
Cohesion: 0.14
Nodes (29): Run one query against one site and read every hit's sizes.      Everything site-, search_site(), _named_profile(), Tests for the profile-driven search in parfum_finder.engine.  What these defend, The real fetcher, with a list of every URL it was asked for., A profile whose search page lists two houses' bottles, as shops do., test_a_broken_profile_is_still_suspect_when_no_title_looked_right(), test_a_full_bottle_next_to_a_decant_does_not_sink_the_site() (+21 more)

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
Nodes (21): Check, _count_result_cards(), _first_result_url(), live_query(), _no_results_check(), _probe_layer(), _probe_other_layers(), Any (+13 more)

### Community 16 - "Schema Field Patterns"
Cohesion: 0.05
Nodes (39): css, embedded_json, endpoint, jsonld, format, pattern, type, pattern (+31 more)

### Community 17 - "Offline Profile Validation"
Cohesion: 0.12
Nodes (39): Run one site and classify what came back instead of raising.      It is also whe, run_site(), FetchResult, One fetched page, uniform regardless of which strategy produced it., _counting_fetcher(), _profile(), Exception, Answer each call with the next canned result, then repeat the last one. (+31 more)

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
Cohesion: 0.10
Nodes (31): Any, Connection, Command-line entry point.  Subcommands will be added incrementally as the projec, Scan every perfume against every site and print each site as it lands.      One, Write one site's rows in a transaction of its own.      Per site rather than per, One line per site: which site, how it went, and what it said.      The site id i, _report_line(), _scan_all() (+23 more)

### Community 22 - "Basket Site Scenarios"
Cohesion: 0.14
Nodes (6): Changed, Close out a submit that named no perfume anyone could look for., Show what storage already knows, then go to the shops for the rest.          `fo, Say a perfume came off the record instead of off the shops.          Without thi, Empty the table for a new scan.          The columns are the same every time now, Submitted

### Community 23 - "Price/Size Normalization"
Cohesion: 0.15
Nodes (21): _check_hook_kinds(), _load_json(), load_platform_template(), load_platform_templates(), Any, Path, Site profile loading, schema validation, and platform-template merging.  Fields, Flatten one profile into the column order of the sites table.      The shipping (+13 more)

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
Cohesion: 0.18
Nodes (14): Badge(), BadgeKind, ProgressBar(), formatAge(), formatMl(), formatPerMl(), formatPrice(), formatPriceWhole() (+6 more)

### Community 30 - "Store Timestamp Tests"
Cohesion: 0.11
Nodes (13): compile(), DEFAULT_CONFIG, EMPTY_BASKET, FakeServer, FakeWebSocket, installFakeServer(), NO_UPDATE, RecordedRequest (+5 more)

### Community 31 - "Live Profile Validation"
Cohesion: 0.06
Nodes (47): Pattern, _brand_pattern(), _canonical(), _canonical_brands(), _covers(), _ends_with(), _index_of(), _match_text() (+39 more)

### Community 32 - "Variant Extraction Fields"
Cohesion: 0.12
Nodes (16): attribute, script, type, additionalProperties, allOf, description, properties, type (+8 more)

### Community 33 - "_ResultRow"
Cohesion: 0.09
Nodes (59): Match, match_title(), parse_query(), PerfumeQuery, The perfume being looked for, split into its three identity parts.      `concent, One site title judged against the query.      `concentration` is what the title, Split one typed line, "Dior Sauvage EDP", into the three identity parts.      Th, Judge one site title against a query, or None if it is not that perfume.      No (+51 more)

### Community 34 - "Fetch Strategy Probing"
Cohesion: 0.31
Nodes (6): _FixtureFetcher, FormData, Headers, Method, Strategy, Serves one site's saved capture in place of the network.      Only three kinds o

### Community 35 - "Platform Field Mapping"
Cohesion: 0.18
Nodes (11): field_map, product_json, source, variants_path, required, additionalProperties, allOf, description (+3 more)

### Community 36 - "Shipping Config Schema"
Cohesion: 0.14
Nodes (14): free_shipping_threshold_kurus, shipping_cost_kurus, minimum, type, free_shipping_threshold_kurus, notes, shipping, shipping_cost_kurus (+6 more)

### Community 37 - "_trial"
Cohesion: 0.17
Nodes (19): _classify_single_separator(), format_ml(), _parse_number(), parse_price(), parse_size_ml(), Decimal, Number parsing and formatting for prices and volumes, plus text folding.  This i, Decide whether a lone separator marks a fraction or a thousands group.      Retu (+11 more)

### Community 38 - "TUI Confirm Dialog"
Cohesion: 0.15
Nodes (43): BaseModel, AcceptedSearch, _add_basket_item(), _AppState, BasketAddRequest, BasketQtyRequest, The FastAPI app: a thin HTTP/WS wrapper around the Faz 1 services.  No business, _read_basket() (+35 more)

### Community 39 - "TUI App Shell"
Cohesion: 0.15
Nodes (3): HeaderSelected, The initial screen: search bar, streaming results table, notices, footer., SearchScreen

### Community 40 - "Fetch Backends"
Cohesion: 0.14
Nodes (14): curl_cffi, httpx, playwright, result_item, result_title, result_url, strategy, url_template (+6 more)

### Community 41 - "HTTP Request Schema"
Cohesion: 0.14
Nodes (14): GET, POST, properties, default, enum, type, type, type (+6 more)

### Community 42 - "Fixture Fetcher (Tests)"
Cohesion: 0.06
Nodes (54): check_enabled(), check_for_update(), fetch_latest_release(), handoff_command(), _installer_asset(), is_newer(), launch_installer(), _no_update() (+46 more)

### Community 43 - "FieldConfidence"
Cohesion: 0.14
Nodes (11): PlaywrightNoResponse, PlaywrightNotInstalled, RuntimeError, The "playwright" strategy was requested but cannot run at all.      Covers both, Navigation completed but playwright returned no Response object.      Its own ty, _FakeBrowser, _FakePage, Any (+3 more)

### Community 44 - "Decant Variant Rules"
Cohesion: 0.16
Nodes (15): api, ApiError, readDetail(), request(), Window, daysSince(), SearchScreen(), splitParts() (+7 more)

### Community 45 - "_ResultRow"
Cohesion: 0.10
Nodes (54): TestClient, _auth(), _client(), db_path(), _ok_result(), Any, MonkeyPatch, Path (+46 more)

### Community 46 - "Offline Validation Fixtures"
Cohesion: 0.25
Nodes (8): type, additionalProperties, type, body, request_headers, additionalProperties, description, type

### Community 47 - "JsonLdProduct"
Cohesion: 0.10
Nodes (21): App(), Toast, View, BookmarkIcon(), BookmarkIconProps, variants, WishlistButton(), basketKey() (+13 more)

### Community 48 - "._build_rows"
Cohesion: 0.07
Nodes (49): collect_prices(), DiscoveryReport, FieldConfidence, _flatten_defaults(), _format_choice(), _format_confidence(), _format_defaults(), _format_fingerprint() (+41 more)

### Community 49 - "_RecordingFetcher"
Cohesion: 0.13
Nodes (23): Connection, Two lines added within the same second must still read back the same way twice., Deleting a row that's already gone is a race between two screens, not a bug., Insert one site → perfume → product → variant chain, return the variant id., Two snapshots written in the same second must resolve to the newer one.      A s, 5 ml at 125,00 TL is 25,00 TL per ml. Stored as kurus, ml as tenths., No price yet means no row, so the basket LEFT JOIN reads it as missing., A zero ml variant is a parse failure, and it must not reach the table.      If i (+15 more)

### Community 50 - "Profile Age Checks"
Cohesion: 0.21
Nodes (24): format_report(), Check one site's profile against that site's saved fixtures.      Never raises f, Render the validations as the offline half of the report in APP_FLOW §6.      A, validate_offline(), _corrupted_sites_dir(), _iso_days_ago(), Any, Path (+16 more)

### Community 51 - "._refresh_table"
Cohesion: 0.24
Nodes (14): apply_variant_rules(), Turn raw size rows into decant variants, dropping what is not a decant.      Thr, Any, _row(), test_a_keyword_in_the_size_label_excludes_the_row_too(), test_a_literal_zero_price_reads_as_no_price_not_a_free_perfume(), test_a_size_at_the_threshold_is_a_bottle_whatever_it_calls_itself(), test_a_size_that_cannot_be_read_is_dropped() (+6 more)

### Community 52 - "FetchResult"
Cohesion: 0.20
Nodes (33): Lock, Any, A site's display name, with a badge when its profile is old enough     to be wor, Show what storage already knows, then go to the shops for the rest.      `force=, run_scan(), site_label(), _basket_row(), _collect() (+25 more)

### Community 53 - "conftest.py"
Cohesion: 0.25
Nodes (8): Collection, basket_inputs(), build_basket_rows(), _label(), BasketRow, Name one basket line the way a missing-item warning has to read it., Turn basket lines and their site prices into what the table shows.      Out of s, The three inputs site_scenario/optimize score: items, prices, shipping.      Bui

### Community 54 - "Endpoint Schema Fields"
Cohesion: 0.22
Nodes (9): result_item, result_title, result_url, url_template, search, additionalProperties, description, required (+1 more)

### Community 55 - "apply_variant_rules"
Cohesion: 0.14
Nodes (17): _check_empty_search(), ExtractionFailed, RuntimeError, A page answered but gave up nothing, where something was expected.      This is, Fail when a search yielded no rows off a page that plainly lists products., _NoRootParser, MonkeyPatch, Stands in for HTMLParser when a page's markup cannot be read at all.      select (+9 more)

### Community 56 - "Request Schema Fields"
Cohesion: 0.04
Nodes (45): jsdom, motion, @playwright/test, react, react-dom, @testing-library/jest-dom, @testing-library/react, @testing-library/user-event (+37 more)

### Community 57 - "_FixtureFetcher"
Cohesion: 0.14
Nodes (7): _Change, BasketScreen, BasketRow, Path, The basket: the list on top, one scenario per site underneath., _remove(), _set_qty()

### Community 58 - "setup_logging"
Cohesion: 0.07
Nodes (27): DOM, DOM.Iterable, e2e, ES2022, playwright.config.ts, src, tests, vite/client (+19 more)

### Community 59 - "_named_profile"
Cohesion: 0.18
Nodes (20): _close_browser(), _close_session_browser(), _fetch_curl_cffi(), _fetch_httpx(), _fetch_playwright(), _folded(), _launch_browser(), Any (+12 more)

### Community 60 - "_wait_for_table"
Cohesion: 0.11
Nodes (23): extract_embedded_variants(), extract_jsonld_variants(), _flatten_jsonld(), Rung 1: read the page's JSON-LD as flat variant rows.      A product that declar, Turn one Product and everything under it into rows., Rung 3: read the JSON blob the page carries but does not display.      Two shape, _LayerUnavailable, Exception (+15 more)

### Community 61 - "._apply_scan_event"
Cohesion: 0.33
Nodes (8): _fake_runner(), main(), _matching_product(), _profile(), Any, The backend playwright drives: the real app, with the shops stubbed out.  Everyt, Which catalogue product a typed query is about, by its leading words.      Delib, A profile that passes schema validation and is never actually fetched.

### Community 62 - "snapshot_rows"
Cohesion: 0.09
Nodes (37): The drop happens here so no caller can forget it.      Both the CLI and the scre, One call has to leave a row the search table can read straight off.      The cal, The old price has to survive, and it must not become a second variant.      Appe, first_seen is what says how long a shop has carried a size., The title and URL are information, not identity.      A shop that rewords a list, EDT and EDP are different products at different prices.      Folding them into o, A sold-out size often shows no price at all, and 0 would mean free.      Writing, The column is 0/1, so the tri-state has to land somewhere on purpose.      Unkno (+29 more)

### Community 64 - "validate_live"
Cohesion: 0.33
Nodes (3): Pressed, ConfirmScreen, Asks before a low-confidence match is written to the basket.      The two answer

### Community 65 - "_named_profile"
Cohesion: 0.33
Nodes (7): Remember a query line so the search screen can offer it again.      Re-running t, The most recently run query lines, newest first, as (text, searched_at)., recent_searches(), record_search(), The recents list has five slots, so a repeat must not consume two.      Someone, test_recent_searches_stops_at_the_limit(), test_rerunning_a_search_moves_it_up_instead_of_adding_a_second_copy()

### Community 67 - "extract_embedded_variants"
Cohesion: 0.67
Nodes (4): authToken(), refusalReason(), streamUrl(), useEventStream()

### Community 68 - "JsonLdProduct"
Cohesion: 0.18
Nodes (17): _age_of(), _path(), profile_age_days(), datetime, Profile staleness checks. Two modes: offline (against saved fixtures) and live (, A URL's path with no trailing slash, for comparing two spellings of one page., Every site that has a profile, sorted so reports read the same way twice., Whole days between a profile's `discovered_at` and now.      Only the exact UTC (+9 more)

### Community 71 - "exclude_keywords"
Cohesion: 0.14
Nodes (6): RowSelected, format_age(), Turn a price age in days into the words the age column shows., ResultRow, Row, test_format_age_reads_as_words_not_a_timestamp()

### Community 72 - "write_snapshots"
Cohesion: 0.50
Nodes (3): The template this site's profile would be based on, if any., Which of the matching templates gets applied, or None for none of them.      One, _resolve_platform()

### Community 73 - "_css_variant"
Cohesion: 0.16
Nodes (13): CacheKey, CandidateFilter, _candidates_to_open(), Path, Run every site against one query, all at once, and report each separately., Narrow the search results down to the pages worth a request.      The first one, run_sites(), test_a_dead_site_does_not_take_the_others_down() (+5 more)

### Community 74 - "ConfirmDialog.tsx"
Cohesion: 0.13
Nodes (18): _record_search(), _sync_profiles(), Connection, Mirror site profiles into the sites table and return how many were written., sync_to_db(), connect(), now_iso(), Path (+10 more)

### Community 75 - "ResultRow"
Cohesion: 0.06
Nodes (51): _as_str(), _balanced_value(), _build_offer(), _build_product(), _coerce_in_stock(), _collect_offers(), _collect_products(), _collect_variants() (+43 more)

### Community 76 - "SplitPlan"
Cohesion: 0.21
Nodes (18): load_site_profile(), Load one site profile, applying its platform template if it has one.      Return, Any, _fake_fetch(), _meta(), _path(), Proof that M4's own criterion holds: every real site profile drives the generic, The one real search-result card that led to this site's captured product.      C (+10 more)

### Community 77 - "_collect_products"
Cohesion: 0.09
Nodes (35): BasketReport, compare_split_to_best_full(), Basket scenario evaluation. A pure function, no network access, no sqlite.  Inpu, Every site's single-site scenario, split by whether it covers everything.      A, One site's share of a split basket: what to buy there and what it costs.      `s, The cheapest basket split the search found. A heuristic, not a proof.      Every, Whether a split plan beats the best full-coverage single site.      `best_full`, Score a split plan against the cheapest full-coverage single site.      Only the (+27 more)

### Community 78 - "validate_live"
Cohesion: 0.25
Nodes (10): Run one site's profile against the real site.      Same contract as offline mode, validate_live(), _FakeSite, _fixture_site(), A stand-in for one live site, answering the search page then the rest.      Live, test_a_broken_layer_reports_which_other_layer_could_take_over(), test_a_working_profile_passes_against_a_site_that_still_answers(), test_the_live_report_carries_the_age_from_the_offline_half() (+2 more)

### Community 79 - "AddButton.tsx"
Cohesion: 0.50
Nodes (4): One search line, then the same line with the brand written the other ways., search_spellings(), test_a_brand_nobody_abbreviates_is_asked_for_once(), test_the_typed_spelling_is_asked_first_and_the_rest_only_follow()

### Community 80 - "_write_hook"
Cohesion: 0.31
Nodes (11): Path, Give the test profile's site id a hook file. The id is what binds them., test_a_before_search_that_returns_no_query_is_refused(), test_a_broken_hook_is_an_error_not_a_silent_empty(), test_a_hook_that_reads_nothing_is_named_as_the_culprit(), test_a_site_with_no_hook_file_is_driven_by_its_profile_alone(), test_after_search_can_drop_a_result_the_selectors_could_not(), test_before_search_rewrites_the_query_that_is_actually_sent() (+3 more)

### Community 81 - "run_sites"
Cohesion: 0.08
Nodes (65): ScanEvent, BasketRefreshEvent and viewmodel dataclasses as JSON-safe dicts.  Eve, _paced_fetcher(), What one site had to say about one query, and how much to trust it.      Four st, One site's pacing state, for as long as whoever holds it says.      The gate and, Wrap a fetcher so one site's requests go out one at a time, spaced apart.      T, SitePace, SiteResult, Fetcher (+57 more)

### Community 82 - "test_connect_is_idempotent_on_an_existing_database"
Cohesion: 0.18
Nodes (9): BaseHTTPRequestHandler, _Handler, _playwright_usable(), MonkeyPatch, Shared pytest fixtures.  A local HTTP server used by fetch/probe tests: real req, Whether the playwright rung can actually run here, binary included.      Checkin, Record every delay the engine asks for instead of serving it.      Waiting for r, server_url() (+1 more)

### Community 83 - "DownloadProgress"
Cohesion: 0.50
Nodes (4): extract_css_variants(), Rung 4: read the rendered markup with selectors. Last resort.      `config["vari, test_css_reads_one_row_per_container(), test_css_without_a_container_reads_the_page_as_one_variant()

### Community 84 - "BasketScreen.tsx"
Cohesion: 0.16
Nodes (14): AcceptedSearch, BasketReport, BasketResponse, BasketRow, BestCombination, ResultRow, ScanEvent, SiteScenario (+6 more)

### Community 85 - "_factory"
Cohesion: 0.25
Nodes (7): _age_line(), format_live_report(), Every check run against one site's profile, in the order they ran.      Checks s, Whether the profile is old enough to be worth re-discovering., The age note for one site, or None when its age is unremarkable.      A profile, Render offline and live results side by side, as APP_FLOW §6 shows them.      Bo, SiteValidation

### Community 86 - "._scan"
Cohesion: 0.18
Nodes (11): _load_profiles(), Any, BasketRow, Path, _recent_searches(), _remove_basket_item(), _score_basket(), _set_basket_qty() (+3 more)

### Community 87 - "helpers.ts"
Cohesion: 0.49
Nodes (7): addFirstRow(), authToken(), clearBasket(), openApp(), search(), searchButton(), tab()

### Community 88 - "handoff_command"
Cohesion: 0.31
Nodes (7): _DeadSite, FormData, Headers, Method, Strategy, A host that cannot be reached at all., test_an_unreachable_site_is_not_reported_as_a_broken_profile()

### Community 89 - "set_basket_qty"
Cohesion: 0.33
Nodes (6): Set a basket line's quantity, clamped to at least 1, and return it.      The tab, set_basket_qty(), The table's CHECK (qty > 0) would reject a bare 0, and the '-' key has to     su, An update aimed at a row that isn't there means the caller is out of sync., test_set_basket_qty_clamps_zero_and_negatives_to_one(), test_set_basket_qty_on_an_unknown_id_raises()

### Community 90 - "Static"
Cohesion: 0.40
Nodes (3): ComposeResult, ComposeResult, Static

### Community 91 - "extract_endpoint_variants"
Cohesion: 0.50
Nodes (4): extract_endpoint_variants(), Rung 2: read the variant list out of a platform's JSON response.      `document`, test_endpoint_reads_every_size_from_one_response(), test_endpoint_without_a_field_map_reads_nothing()

### Community 93 - "_jitter_s"
Cohesion: 0.29
Nodes (7): in_stock, price, size_raw, additionalProperties, required, type, field_map

### Community 94 - "Arayüz testleri"
Cohesion: 0.40
Nodes (4): Arayüz testleri, jsdom katmanı (`tests/`), Ne test edilmiyor, Tarayıcı katmanı (`e2e/`)

### Community 96 - "DownloadProgress"
Cohesion: 0.22
Nodes (4): Client, DownloadProgress, İndirmeyi başlatır. Zaten çalışıyorsa None., state: idle | downloading | ready | installing | error.

### Community 97 - "test_paths.py"
Cohesion: 0.38
Nodes (11): _freeze(), MonkeyPatch, Path, Tests for parfum_finder.paths: frozen vs. source path resolution.  `ensure_user_, A source run has nothing to seed: resource_dir and user_data_dir are     already, test_ensure_user_data_is_a_noop_when_not_frozen(), test_ensure_user_data_never_overwrites_an_edited_file(), test_ensure_user_data_seeds_sites_platforms_and_hooks() (+3 more)

### Community 98 - "_FakeStreamResponse"
Cohesion: 0.29
Nodes (7): items, type, type, items, type, exclude_keywords, needs_review

### Community 99 - "cached_prices"
Cohesion: 0.12
Nodes (17): conn(), Path, Tests for parfum_finder.store: the timestamp helper and the schema.  The one har, A disabled site loses its basket column, but an enabled quiet one keeps one., NULL means the site has no free shipping tier at all, not a threshold of zero., A snapshot pointing at a variant that doesn't exist has to be rejected.      SQL, Reopening an existing database must not wipe or re-raise on its schema., No history yet is a normal state for a variant, not an error to raise on. (+9 more)

### Community 102 - "test_gui.py"
Cohesion: 0.33
Nodes (6): deep_merge(), Recursively merge override onto base. override always wins on conflicts.      Ne, test_deep_merge_does_not_mutate_its_inputs(), test_deep_merge_fills_gaps_from_base(), test_deep_merge_override_wins_on_conflict(), test_deep_merge_replaces_arrays_wholesale_instead_of_combining()

### Community 103 - "UpdateDialog.test.tsx"
Cohesion: 0.28
Nodes (5): UpdateDialog(), UpdateInfo, UpdateProgress, INFO, updateProgress()

## Knowledge Gaps
- **231 isolated node(s):** `parfum-finder`, `View`, `Toast`, `BookmarkIconProps`, `variants` (+226 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **5 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `parse_query()` connect `_ResultRow` to `Title Matcher`, `TUI Confirm Dialog`, `CLI Entry Points`, `Basket Store & Pricing`, `run_sites`, `Search TUI Screen`, `Candidate Filtering`, `Basket Site Scenarios`, `Live Profile Validation`?**
  _High betweenness centrality (0.027) - this node is a cross-community bridge._
- **Why does `SearchScreen` connect `TUI App Shell` to `TUI App & Screens`, `_ResultRow`, `Search/Basket Domain Models`, `TUI Confirm Dialog`, `exclude_keywords`, `ConfirmDialog.tsx`, `run_sites`, `Search TUI Screen`, `Candidate Filtering`, `Basket Site Scenarios`, `_FixtureFetcher`, `Static`, `.__init__`?**
  _High betweenness centrality (0.026) - this node is a cross-community bridge._
- **Why does `SiteResult` connect `run_sites` to `TUI App & Screens`, `Search/Basket Domain Models`, `TUI Confirm Dialog`, `_css_variant`, `Search Engine Core`, `FieldConfidence`, `_ResultRow`, `Offline Profile Validation`, `FetchResult`, `Candidate Filtering`, `._apply_scan_event`?**
  _High betweenness centrality (0.026) - this node is a cross-community bridge._
- **Are the 25 inferred relationships involving `SiteResult` (e.g. with `RawVariant` and `Fetcher`) actually correct?**
  _`SiteResult` has 25 INFERRED edges - model-reasoned connections that need verification._
- **Are the 23 inferred relationships involving `PerfumeQuery` (e.g. with `BasketPriceExcluded` and `BasketRefreshFinished`) actually correct?**
  _`PerfumeQuery` has 23 INFERRED edges - model-reasoned connections that need verification._
- **Are the 14 inferred relationships involving `SearchScreen` (e.g. with `ParfumFinderApp` and `SiteRunner`) actually correct?**
  _`SearchScreen` has 14 INFERRED edges - model-reasoned connections that need verification._
- **What connects `parfum-finder`, `View`, `Toast` to the rest of the system?**
  _231 weakly-connected nodes found - possible documentation gaps or missing edges._