# Graph Report - parfum-finder  (2026-08-15)

## Corpus Check
- 101 files · ~278,553 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2204 nodes · 6066 edges · 80 communities (69 shown, 11 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 369 edges (avg confidence: 0.56)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `008eb460`
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
- ._write_to_sheet
- Headers
- format_age
- BasketRefreshEvent
- Protocol
- test_snapshot_rows_still_merges_a_confident_match_under_the_searched_name
- Strategy

## God Nodes (most connected - your core abstractions)
1. `search_site()` - 66 edges
2. `PerfumeQuery` - 65 edges
3. `SearchScreen` - 64 edges
4. `SiteResult` - 60 edges
5. `_profile()` - 58 edges
6. `discover()` - 54 edges
7. `Fetcher` - 50 edges
8. `_write_profile()` - 50 edges
9. `BasketScreen` - 48 edges
10. `_app()` - 48 edges

## Surprising Connections (you probably didn't know these)
- `Shipping Non-linearity Rationale (why cheapest-per-item is wrong)` --semantically_similar_to--> `sites/ Site Profile Directory`  [INFERRED] [semantically similar]
  ARCHITECTURE.md → sites/README.md
- `Variant Pattern B (dropdown + AJAX price)` --semantically_similar_to--> `Variant Selector Detector Fix (WooCommerce 'variation' vs 'variant')`  [INFERRED] [semantically similar]
  ARCHITECTURE.md → docs/discovery-report.md
- `_Handler` --uses--> `PlaywrightNotInstalled`  [INFERRED]
  tests/conftest.py → src/parfum_finder/fetch.py
- `_NoRootParser` --uses--> `PlaywrightNotInstalled`  [INFERRED]
  tests/test_engine.py → src/parfum_finder/fetch.py
- `_FakeBrowser` --uses--> `PlaywrightNotInstalled`  [INFERRED]
  tests/test_fetch.py → src/parfum_finder/fetch.py

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

## Communities (80 total, 11 thin omitted)

### Community 0 - "TUI App & Screens"
Cohesion: 0.09
Nodes (100): The Textual-based terminal UI: search and basket screens., _app(), _basket(), _cells(), _days_ago(), _leg(), _ok(), _open_basket() (+92 more)

### Community 1 - "Site Profiles & Templates"
Cohesion: 0.05
Nodes (86): _check_hook_kinds(), deep_merge(), _load_json(), load_platform_template(), load_platform_templates(), load_site_hooks(), load_site_profile(), Any (+78 more)

### Community 2 - "Title Matcher"
Cohesion: 0.15
Nodes (7): _Change, BasketScreen, BasketRow, Path, The basket: the list on top, one scenario per site underneath., _remove(), _set_qty()

### Community 3 - "HTTP/Browser Fetching"
Cohesion: 0.14
Nodes (28): browser_session(), fetch(), Fetch one URL using exactly the given strategy.      `method`/`data` exist for t, Yield a fetcher that keeps one browser for every playwright page it reads., test_the_no_results_page_would_otherwise_read_as_suspect(), _fake_launch(), MonkeyPatch, Tests for parfum_finder.fetch.  httpx and curl_cffi are exercised against a real (+20 more)

### Community 4 - "Search/Basket Domain Models"
Cohesion: 0.07
Nodes (119): Screen, One decant size of one product, in the units the database stores.      Tenths of, A candidate together with the decant sizes its product page offers., SearchHit, Variant, Write one scan's reading of one size, and return its snapshot id.      The perfu, record_snapshot(), ParfumFinderApp (+111 more)

### Community 5 - "Search Engine per Site"
Cohesion: 0.19
Nodes (16): FormData, Headers, Method, _close_browser(), _fetch_curl_cffi(), _fetch_httpx(), _fetch_playwright(), _launch_browser() (+8 more)

### Community 6 - "Platform Discovery Flow"
Cohesion: 0.15
Nodes (59): PlatformChooser, _ask_chooser(), discover(), Put the question only when there is one, and hold the answer to it.      An answ, Measure the strategies a site needs, then read its JSON-LD with the winner., _attempt(), _fake_probe(), Any (+51 more)

### Community 7 - "CLI Entry Points"
Cohesion: 0.11
Nodes (52): CaptureFixture, Connection, PerfumeQuery, ask_which_platform(), main(), Any, Path, SiteResult (+44 more)

### Community 8 - "Architecture Rationale Docs"
Cohesion: 0.05
Nodes (53): basket Subset Enumeration + Local Improvement Algorithm, basket Optimizer (optimize function), Clone/Original Distinction (KLON ← <orijinal>), discover Discovery Flow, engine Concurrency Model (parallel sites, serial within site), Extraction Ladder (jsonld/endpoint/embedded/css), Fail-loud / status=suspect policy, hooks/<id>.py Escape Hatch (+45 more)

### Community 9 - "Search Engine Core"
Cohesion: 0.07
Nodes (61): HTMLParser, _candidates_to_open(), _check_empty_search(), _check_variant_control(), ExtractionFailed, _fetch_page(), _headers(), _is_excluded() (+53 more)

### Community 10 - "Basket Optimizer Core"
Cohesion: 0.15
Nodes (35): BasketItem, optimize(), Prices, Score one site against the basket, or against a subset of it.      `item_ids` is, Score every enabled site against the whole basket and sort the results.      Sit, Search for the cheapest way to split the basket across several sites.      Retur, One line of the shopping list: a basket row, not a unit count.      `item_id` is, single_site_scenarios() (+27 more)

### Community 11 - "Basket Store & Pricing"
Cohesion: 0.08
Nodes (41): A shop's imitation must not be stored as the perfume it imitates.      The clone, The drop happens here so no caller can forget it.      Both the CLI and the scre, One call has to leave a row the search table can read straight off.      The cal, The old price has to survive, and it must not become a second variant.      Appe, first_seen is what says how long a shop has carried a size., The title and URL are information, not identity.      A shop that rewords a list, EDT and EDP are different products at different prices.      Folding them into o, A sold-out size often shows no price at all, and 0 would mean free.      Writing (+33 more)

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
Cohesion: 0.11
Nodes (28): _as_str(), _build_offer(), _build_product(), _coerce_in_stock(), _collect_offers(), _collect_products(), _collect_variants(), _has_type() (+20 more)

### Community 16 - "Schema Field Patterns"
Cohesion: 0.06
Nodes (33): format, pattern, type, pattern, type, default, type, pattern (+25 more)

### Community 17 - "Offline Profile Validation"
Cohesion: 0.05
Nodes (100): CacheKey, CandidateFilter, apply_variant_rules(), Path, Run one site and classify what came back instead of raising.      It is also whe, Run every site against one query, all at once, and report each separately., Run one query against one site and read every hit's sizes.      Everything site-, Turn raw size rows into decant variants, dropping what is not a decant.      Thr (+92 more)

### Community 18 - "Playwright Errors"
Cohesion: 0.13
Nodes (26): RuntimeError, PlaywrightNoResponse, PlaywrightNotInstalled, The "playwright" strategy was requested but cannot run at all.      Covers both, Navigation completed but playwright returned no Response object.      Its own ty, _attempt(), _count_jsonld(), _count_product_objects() (+18 more)

### Community 19 - "Search TUI Screen"
Cohesion: 0.07
Nodes (46): A multi-site price and stock comparison tool for perfume decants.  Includes a sh, File logging for the app's own diagnostics.  Nothing here ever writes to the con, Match, One site title judged against the query.      `concentration` is what the title, find_header_columns(), find_match(), open_worksheet(), Any (+38 more)

### Community 20 - "Snapshot Writing"
Cohesion: 0.27
Nodes (9): FetchResult, One fetched page, uniform regardless of which strategy produced it., _DeadSite, FormData, Headers, Method, Strategy, A host that cannot be reached at all. (+1 more)

### Community 21 - "Candidate Filtering"
Cohesion: 0.18
Nodes (17): collect_prices(), _format_product(), _format_stock(), _format_trial(), _has_exact_price(), PageTrial, Decimal, One page fetched with the chosen strategy and read for JSON-LD.      A fetch tha (+9 more)

### Community 22 - "Basket Site Scenarios"
Cohesion: 0.24
Nodes (6): BaseHTTPRequestHandler, _Handler, _playwright_usable(), Shared pytest fixtures.  A local HTTP server used by fetch/probe tests: real req, Whether the playwright rung can actually run here, binary included.      Checkin, server_url()

### Community 23 - "Price/Size Normalization"
Cohesion: 0.13
Nodes (24): _classify_single_separator(), format_age(), format_ml(), format_price(), _parse_number(), parse_price(), parse_size_ml(), Decimal (+16 more)

### Community 24 - "JSON Schema Primitives"
Cohesion: 0.11
Nodes (25): integer, null, string, properties, type, type, type, type (+17 more)

### Community 25 - "SQLite Store"
Cohesion: 0.21
Nodes (8): _FixtureFetcher, FormData, Headers, Method, Path, Strategy, Serves one site's saved capture in place of the network.      Only three kinds o, The one real result card that led to the captured product page.          Cut out

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
Cohesion: 0.08
Nodes (47): api, ApiError, authToken(), readDetail(), request(), Window, refusalReason(), streamUrl() (+39 more)

### Community 30 - "Store Timestamp Tests"
Cohesion: 0.15
Nodes (18): extract_embedded_variants(), extract_jsonld_variants(), _flatten_jsonld(), Rung 1: read the page's JSON-LD as flat variant rows.      A product that declar, Turn one Product and everything under it into rows., Rung 3: read the JSON blob the page carries but does not display.      Two shape, _fixture(), Read a captured product page. (+10 more)

### Community 31 - "Live Profile Validation"
Cohesion: 0.09
Nodes (33): _canonical(), _covers(), _ends_with(), _index_of(), listing_filter(), _match_text(), _own_identity(), product_label() (+25 more)

### Community 32 - "Variant Extraction Fields"
Cohesion: 0.11
Nodes (18): attribute, in_stock, price, script, size_raw, type, properties, additionalProperties (+10 more)

### Community 33 - "_ResultRow"
Cohesion: 0.10
Nodes (52): match_title(), parse_query(), PerfumeQuery, The perfume being looked for, split into its three identity parts.      `concent, Split one typed line, "Dior Sauvage EDP", into the three identity parts.      Th, Judge one site title against a query, or None if it is not that perfume.      No, Whether a search result's own listing text is worth opening the page for.      J, title_could_match() (+44 more)

### Community 34 - "Fetch Strategy Probing"
Cohesion: 0.16
Nodes (14): _heading(), _leg_block(), BasketReport, Prices, SiteScenario, SplitLeg, A block title plus the blank line that keeps it off the block above it.      The, The one line that says the screen is holding something back, or is not. (+6 more)

### Community 35 - "Platform Field Mapping"
Cohesion: 0.12
Nodes (16): field_map, product_json, source, variants_path, additionalProperties, allOf, description, required (+8 more)

### Community 36 - "Shipping Config Schema"
Cohesion: 0.14
Nodes (14): free_shipping_threshold_kurus, shipping_cost_kurus, minimum, type, free_shipping_threshold_kurus, notes, shipping, shipping_cost_kurus (+6 more)

### Community 37 - "_trial"
Cohesion: 0.18
Nodes (15): Collection, basket_inputs(), build_basket_rows(), _label(), BasketRow, Name one basket line the way a missing-item warning has to read it., Turn basket lines and their site prices into what the table shows.      Out of s, The three inputs site_scenario/optimize score: items, prices, shipping.      Bui (+7 more)

### Community 38 - "TUI Confirm Dialog"
Cohesion: 0.05
Nodes (109): Lock, encode_basket_refresh_event(), encode_basket_report(), encode_basket_row(), encode_result_row(), encode_scan_event(), encode_site_scenario(), _encode_split_leg() (+101 more)

### Community 39 - "TUI App Shell"
Cohesion: 0.31
Nodes (9): Path, Attach the rotating file handler and return where it writes.      Safe to call m, setup_logging(), Path, The file logger's two promises: it writes to the file, and it stays silent.  Bot, _teardown(), test_an_error_lands_in_the_given_file(), test_setting_up_twice_does_not_double_the_lines() (+1 more)

### Community 40 - "Fetch Backends"
Cohesion: 0.14
Nodes (14): curl_cffi, httpx, playwright, result_item, result_title, result_url, strategy, url_template (+6 more)

### Community 41 - "HTTP Request Schema"
Cohesion: 0.14
Nodes (14): GET, POST, properties, default, enum, type, type, type (+6 more)

### Community 42 - "Fixture Fetcher (Tests)"
Cohesion: 0.09
Nodes (40): conn(), Connection, Path, Tests for parfum_finder.store: the timestamp helper and the schema.  The one har, A disabled site loses its basket column, but an enabled quiet one keeps one., NULL means the site has no free shipping tier at all, not a threshold of zero., Deleting a row that's already gone is a race between two screens, not a bug., The table's CHECK (qty > 0) would reject a bare 0, and the '-' key has to     su (+32 more)

### Community 43 - "FieldConfidence"
Cohesion: 0.22
Nodes (3): _FakeBrowser, _FakePage, Any

### Community 44 - "Decant Variant Rules"
Cohesion: 0.20
Nodes (10): add_basket_item(), Add a size of a perfume to the basket, and return the basket_item_id.      The p, A stale reading must never outrank the one taken after it.      latest_prices al, A 10 ml listing must never fill a basket line asking for 5 ml.      The matrix j, Whether an out-of-stock price counts as missing is the caller's call.      Dropp, A basket line for a perfume nobody has priced is a bug, not a state to keep., test_add_basket_item_refuses_a_perfume_with_no_price_on_record(), test_basket_prices_joins_on_the_exact_integer_size() (+2 more)

### Community 45 - "_ResultRow"
Cohesion: 0.06
Nodes (92): BaseModel, BasketLine, BasketPrice, BasketRow, BasketSite, FastAPI, AcceptedSearch, _add_basket_item() (+84 more)

### Community 46 - "Offline Validation Fixtures"
Cohesion: 0.25
Nodes (8): type, additionalProperties, type, body, request_headers, additionalProperties, description, type

### Community 47 - "JsonLdProduct"
Cohesion: 0.22
Nodes (6): _age_line(), Every check run against one site's profile, in the order they ran.      Checks s, Whether the profile is old enough to be worth re-discovering., The check that broke, or None if the profile is intact., The age note for one site, or None when its age is unremarkable.      A profile, SiteValidation

### Community 48 - "._build_rows"
Cohesion: 0.08
Nodes (39): _choose_strategy(), DiscoveryReport, FieldConfidence, _flatten_defaults(), _format_choice(), _format_confidence(), _format_defaults(), _format_fingerprint() (+31 more)

### Community 49 - "_RecordingFetcher"
Cohesion: 0.09
Nodes (39): Protocol, Fetcher, Anything that can stand in for `fetch`.      Offline profile validation runs the, The Textual App root. Handles screen navigation and is the app's default entry p, _age_of(), Check, _count_result_cards(), _first_result_url() (+31 more)

### Community 50 - "Profile Age Checks"
Cohesion: 0.13
Nodes (37): format_live_report(), format_report(), Check one site's profile against that site's saved fixtures.      Never raises f, Validate every site, or just the ones named.      Serial rather than concurrent:, Render the validations as the offline half of the report in APP_FLOW §6.      A, Render offline and live results side by side, as APP_FLOW §6 shows them.      Bo, validate_all_offline(), validate_offline() (+29 more)

### Community 51 - "._refresh_table"
Cohesion: 0.06
Nodes (16): Changed, HeaderSelected, RowSelected, ComposeResult, ComposeResult, Path, ResultRow, Row (+8 more)

### Community 52 - "FetchResult"
Cohesion: 0.12
Nodes (33): encode_split_plan(), The split plan plus its verdict against the best full-coverage site.      Named, BasketReport, _ClimbState, compare_split_to_best_full(), Basket scenario evaluation. A pure function, no network access, no sqlite.  Inpu, Every site's single-site scenario, split by whether it covers everything.      A, One site's share of a split basket: what to buy there and what it costs.      `s (+25 more)

### Community 53 - "conftest.py"
Cohesion: 0.15
Nodes (23): basket_lines(), basket_prices(), cached_prices(), _perfume_id(), _product_id(), Connection, SQLite persistence: an append-only price history.  Tables: sites, perfumes, prod, Write a whole scan at once and return how many prices were recorded.      Every (+15 more)

### Community 54 - "Endpoint Schema Fields"
Cohesion: 0.22
Nodes (9): result_item, result_title, result_url, url_template, search, additionalProperties, description, required (+1 more)

### Community 55 - "apply_variant_rules"
Cohesion: 0.25
Nodes (8): Split one typed line into the perfumes it asks for, on " - ".      The separator, split_queries(), test_a_hyphen_inside_a_brand_name_does_not_split_the_search(), test_a_line_naming_three_perfumes_is_read_as_three_searches(), test_a_piece_that_names_no_perfume_survives_to_be_complained_about(), test_a_stray_separator_is_not_worth_failing_over(), test_one_perfume_is_still_one_search(), test_the_same_perfume_typed_twice_is_scanned_once()

### Community 56 - "Request Schema Fields"
Cohesion: 0.07
Nodes (27): motion, react, react-dom, @types/react, @types/react-dom, typescript, dependencies, motion (+19 more)

### Community 57 - "_FixtureFetcher"
Cohesion: 0.20
Nodes (11): _css_variant(), extract_endpoint_variants(), Any, Rung 2: read the variant list out of a platform's JSON response.      `document`, Read one variant's fields out of its container node., Read variant rows out of a parsed JSON document.      Shared by the endpoint and, Follow a dotted path into parsed JSON, e.g. "data.options.0.price".      A segme, _resolve_path() (+3 more)

### Community 58 - "setup_logging"
Cohesion: 0.08
Nodes (23): DOM, DOM.Iterable, ES2022, src, vite/client, vite.config.ts, compilerOptions, isolatedModules (+15 more)

### Community 59 - "_named_profile"
Cohesion: 0.33
Nodes (3): Pressed, ConfirmScreen, Asks before a low-confidence match is written to the basket.      The two answer

### Community 60 - "._scan"
Cohesion: 0.31
Nodes (9): _parse_selector(), Node, Run one "<css>::text" / "<css>::attr(name)" selector inside a node.      The nod, Run one "<css>::text" / "<css>::attr(name)" selector, reading every match., Split a "<css>::text" / "<css>::attr(name)" selector into its two parts., Read the attribute or text of one already-selected node, or None., _read_selected(), select_all() (+1 more)

### Community 61 - "single_site_scenarios"
Cohesion: 0.38
Nodes (11): _freeze(), MonkeyPatch, Path, Tests for parfum_finder.paths: frozen vs. source path resolution.  `ensure_user_, A source run has nothing to seed: resource_dir and user_data_dir are     already, test_ensure_user_data_is_a_noop_when_not_frozen(), test_ensure_user_data_never_overwrites_an_edited_file(), test_ensure_user_data_seeds_sites_platforms_and_hooks() (+3 more)

### Community 62 - "snapshot_rows"
Cohesion: 0.25
Nodes (8): exclude_keywords, max_size_ml, size_from, size_pattern, variant_rules, additionalProperties, required, type

### Community 64 - "validate_live"
Cohesion: 0.40
Nodes (5): profile_age_days(), datetime, Whole days between a profile's `discovered_at` and now.      Only the exact UTC, test_a_timestamp_that_is_not_the_schema_format_is_rejected(), test_profile_age_is_counted_in_whole_days_from_the_schema_timestamp()

### Community 66 - ".__call__"
Cohesion: 0.22
Nodes (9): price_history(), Row, Return one variant's past readings, newest first, capped at limit.      Empty fo, The trend panel reads row 0 as the latest reading, so order is the point.      A, No history yet is a normal state for a variant, not an error to raise on., The identity a real scan writes must be the identity these lookups accept., test_a_scanned_perfume_can_be_read_back_by_basket_and_history(), test_price_history_is_empty_for_an_unknown_variant() (+1 more)

### Community 67 - "test_cached_prices_is_empty_for_a_perfume_nobody_scanned"
Cohesion: 0.33
Nodes (6): css, embedded_json, endpoint, jsonld, enum, extraction

### Community 68 - "field_map"
Cohesion: 0.33
Nodes (6): _balanced_value(), _embedded_documents(), _loads_or_skip(), Yield every JSON document the page hides, in document order., Parse `text` as JSON, yielding nothing when it isn't JSON.      Pages are full o, Return the JSON object or array beginning at or after `start`.      Scanning for

### Community 75 - "BasketRefreshEvent"
Cohesion: 0.21
Nodes (15): probe(), Fetch `url` with every strategy and report diagnostics for each.      timeout_s, MonkeyPatch, Tests for parfum_finder.probe.  probe() always tries all three strategies -- the, test_probe_counts_jsonld_product_and_platform_signature(), test_probe_counts_product_across_jsonld_root_shapes(), test_probe_counts_product_markup_without_any_jsonld(), test_probe_counts_products_nested_below_the_top_level() (+7 more)

## Knowledge Gaps
- **201 isolated node(s):** `parfum-finder`, `$schema`, `$id`, `title`, `description` (+196 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **11 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `SearchScreen` connect `._refresh_table` to `TUI App & Screens`, `_ResultRow`, `Title Matcher`, `Site Profiles & Templates`, `Search/Basket Domain Models`, `TUI Confirm Dialog`, `_RecordingFetcher`, `Search TUI Screen`?**
  _High betweenness centrality (0.040) - this node is a cross-community bridge._
- **Why does `PlaywrightNotInstalled` connect `Playwright Errors` to `HTTP/Browser Fetching`, `Search/Basket Domain Models`, `Search Engine per Site`, `TUI Confirm Dialog`, `Search Engine Core`, `FieldConfidence`, `BasketRefreshEvent`, `._build_rows`, `Offline Profile Validation`, `Candidate Filtering`, `Basket Site Scenarios`?**
  _High betweenness centrality (0.030) - this node is a cross-community bridge._
- **Why does `extract_jsonld_products()` connect `JSON-LD Product Extraction` to `Search Engine Core`, `Product Extraction`, `._build_rows`, `Candidate Filtering`, `Store Timestamp Tests`?**
  _High betweenness centrality (0.027) - this node is a cross-community bridge._
- **Are the 23 inferred relationships involving `PerfumeQuery` (e.g. with `BasketPriceExcluded` and `BasketRefreshFinished`) actually correct?**
  _`PerfumeQuery` has 23 INFERRED edges - model-reasoned connections that need verification._
- **Are the 14 inferred relationships involving `SearchScreen` (e.g. with `ParfumFinderApp` and `SiteRunner`) actually correct?**
  _`SearchScreen` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Are the 23 inferred relationships involving `SiteResult` (e.g. with `RawVariant` and `Fetcher`) actually correct?**
  _`SiteResult` has 23 INFERRED edges - model-reasoned connections that need verification._
- **What connects `parfum-finder`, `$schema`, `$id` to the rest of the system?**
  _201 weakly-connected nodes found - possible documentation gaps or missing edges._