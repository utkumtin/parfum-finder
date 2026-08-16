# Graph Report - parfum-finder  (2026-08-16)

## Corpus Check
- 103 files · ~283,866 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2220 nodes · 6343 edges · 80 communities (74 shown, 6 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 442 edges (avg confidence: 0.55)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `ae1a131d`
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
- ScanStatus.tsx

## God Nodes (most connected - your core abstractions)
1. `PerfumeQuery` - 68 edges
2. `SiteResult` - 66 edges
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
- `test_a_hook_that_reads_nothing_is_named_as_the_culprit()` --indirect_call--> `ExtractionFailed`  [INFERRED]
  tests/test_engine.py → src/parfum_finder/engine.py
- `test_a_post_endpoint_missing_a_static_body_field_fails_loudly()` --indirect_call--> `ExtractionFailed`  [INFERRED]
  tests/test_engine.py → src/parfum_finder/engine.py

## Import Cycles
- 3-file cycle: `src/parfum_finder/__init__.py -> src/parfum_finder/cli.py -> src/parfum_finder/logging_setup.py -> src/parfum_finder/__init__.py`
- 3-file cycle: `src/parfum_finder/__init__.py -> src/parfum_finder/cli.py -> src/parfum_finder/profiles.py -> src/parfum_finder/__init__.py`
- 3-file cycle: `src/parfum_finder/__init__.py -> src/parfum_finder/cli.py -> src/parfum_finder/store.py -> src/parfum_finder/__init__.py`
- 3-file cycle: `src/parfum_finder/__init__.py -> src/parfum_finder/cli.py -> src/parfum_finder/validate.py -> src/parfum_finder/__init__.py`
- 4-file cycle: `src/parfum_finder/__init__.py -> src/parfum_finder/cli.py -> src/parfum_finder/discover.py -> src/parfum_finder/profiles.py -> src/parfum_finder/__init__.py`
- 4-file cycle: `src/parfum_finder/__init__.py -> src/parfum_finder/cli.py -> src/parfum_finder/discover.py -> src/parfum_finder/store.py -> src/parfum_finder/__init__.py`
- 4-file cycle: `src/parfum_finder/__init__.py -> src/parfum_finder/cli.py -> src/parfum_finder/engine.py -> src/parfum_finder/profiles.py -> src/parfum_finder/__init__.py`
- 4-file cycle: `src/parfum_finder/__init__.py -> src/parfum_finder/cli.py -> src/parfum_finder/validate.py -> src/parfum_finder/profiles.py -> src/parfum_finder/__init__.py`
- 5-file cycle: `src/parfum_finder/__init__.py -> src/parfum_finder/cli.py -> src/parfum_finder/store.py -> src/parfum_finder/engine.py -> src/parfum_finder/profiles.py -> src/parfum_finder/__init__.py`
- 5-file cycle: `src/parfum_finder/__init__.py -> src/parfum_finder/cli.py -> src/parfum_finder/validate.py -> src/parfum_finder/engine.py -> src/parfum_finder/profiles.py -> src/parfum_finder/__init__.py`

## Hyperedges (group relationships)
- **Sites Implementing Variant Pattern C (embedded JSON)** — docs_discovery_report_venco_site, docs_discovery_report_decantall_site, docs_discovery_report_luxurydekant_site, docs_discovery_report_ruxangroup_site, architecture_md_variant_pattern_c [EXTRACTED 1.00]
- **İdeasoft Platform Sites and Endpoint** — docs_discovery_report_dekantparfum_site, docs_discovery_report_dekantdoktoru_site, docs_discovery_report_ideasoft_related_options_endpoint, platforms_readme_ideasoft_json [EXTRACTED 1.00]
- **discover Command Output Artifacts (profile + fixtures + CI validation)** — architecture_md_discover_flow, sites_readme_sites_dir, fixtures_readme_fixtures_dir, github_workflows_ci_validate_profiles_step, architecture_md_validate_command [INFERRED 0.85]

## Communities (80 total, 6 thin omitted)

### Community 0 - "TUI App & Screens"
Cohesion: 0.09
Nodes (100): The Textual-based terminal UI: search and basket screens., _app(), _basket(), _cells(), _days_ago(), _leg(), _ok(), _open_basket() (+92 more)

### Community 1 - "Site Profiles & Templates"
Cohesion: 0.06
Nodes (82): _check_hook_kinds(), deep_merge(), _load_json(), load_platform_template(), load_platform_templates(), load_site_hooks(), load_site_profile(), Any (+74 more)

### Community 2 - "Title Matcher"
Cohesion: 0.09
Nodes (45): Pressed, What one site had to say about one query, and how much to trust it.      Four st, SiteResult, _about(), BasketPriceExcluded, BasketRefreshFinished, BasketRefreshStarted, BasketRowFinished (+37 more)

### Community 3 - "HTTP/Browser Fetching"
Cohesion: 0.12
Nodes (30): browser_session(), fetch(), PlaywrightNotInstalled, Strategy, Fetch one URL using exactly the given strategy.      `method`/`data` exist for t, Yield a fetcher that keeps one browser for every playwright page it reads., The "playwright" strategy was requested but cannot run at all.      Covers both, test_the_no_results_page_would_otherwise_read_as_suspect() (+22 more)

### Community 4 - "Search/Basket Domain Models"
Cohesion: 0.07
Nodes (123): Screen, One decant size of one product, in the units the database stores.      Tenths of, A candidate together with the decant sizes its product page offers., SearchHit, Variant, connect(), Path, Open the price database, creating the schema if it isn't there yet.      Foreign (+115 more)

### Community 5 - "Search Engine per Site"
Cohesion: 0.15
Nodes (27): Match, match_title(), PerfumeQuery, The perfume being looked for, split into its three identity parts.      `concent, One site title judged against the query.      `concentration` is what the title, Judge one site title against a query, or None if it is not that perfume.      No, test_a_brand_needs_all_of_its_words_not_one(), test_a_brand_only_query_matches_a_title_that_is_only_that_brand() (+19 more)

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
Nodes (64): HTMLParser, _candidates_to_open(), _check_empty_search(), _check_variant_control(), ExtractionFailed, _fetch_page(), _headers(), _is_excluded() (+56 more)

### Community 10 - "Basket Optimizer Core"
Cohesion: 0.12
Nodes (41): BasketItem, optimize(), Prices, Score one site against the basket, or against a subset of it.      `item_ids` is, Score every enabled site against the whole basket and sort the results.      Sit, Search for the cheapest way to split the basket across several sites.      Retur, One line of the shopping list: a basket row, not a unit count.      `item_id` is, single_site_scenarios() (+33 more)

### Community 11 - "Basket Store & Pricing"
Cohesion: 0.12
Nodes (19): cached_prices(), Return the latest stored price of every size of this perfume, per site.      Bra, One call has to leave a row the search table can read straight off.      The cal, first_seen is what says how long a shop has carried a size., A sold-out size often shows no price at all, and 0 would mean free.      Writing, A slow site must not spread one reading across several timestamps.      Rows wri, The search screen's second search must be answered with today's numbers.      Tw, A search that named no concentration is asking for all of them.      "" means "a (+11 more)

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
Cohesion: 0.05
Nodes (39): css, embedded_json, endpoint, jsonld, format, pattern, type, pattern (+31 more)

### Community 17 - "Offline Profile Validation"
Cohesion: 0.05
Nodes (100): CacheKey, CandidateFilter, apply_variant_rules(), Path, Run one site and classify what came back instead of raising.      It is also whe, Run every site against one query, all at once, and report each separately., Run one query against one site and read every hit's sizes.      Everything site-, Turn raw size rows into decant variants, dropping what is not a decant.      Thr (+92 more)

### Community 18 - "Playwright Errors"
Cohesion: 0.15
Nodes (21): _attempt(), _count_jsonld(), _count_product_objects(), _detect_platforms(), format_report(), _label_platform(), _one_line(), ProbeAttempt (+13 more)

### Community 19 - "Search TUI Screen"
Cohesion: 0.08
Nodes (41): find_header_columns(), find_match(), open_worksheet(), Any, Exception, Path, Protocol, Writing a search result onto the user's own Google Sheets wishlist.  The wishlis (+33 more)

### Community 20 - "Snapshot Writing"
Cohesion: 0.18
Nodes (22): grouped_value(), Decimal, ResultRow, Pure sorting and grouping rules for the results table.  No I/O, no Textual state, What each site charges for the product a block is about.      One entry per site, The default order: typed order, product, site, size.      The typed order comes, The order once a column has been picked: the site layer drops out.      Asking f, site_ranks() (+14 more)

### Community 21 - "Candidate Filtering"
Cohesion: 0.16
Nodes (36): Lock, listing_filter(), Decide, from a search result's own title, whether to open its page.      Structu, Any, The scan is over. `error_count` is every failure any event above     reported, e, A site's display name, with a badge when its profile is old enough     to be wor, Show what storage already knows, then go to the shops for the rest.      `force=, run_scan() (+28 more)

### Community 22 - "Basket Site Scenarios"
Cohesion: 0.24
Nodes (6): BaseHTTPRequestHandler, _Handler, _playwright_usable(), Shared pytest fixtures.  A local HTTP server used by fetch/probe tests: real req, Whether the playwright rung can actually run here, binary included.      Checkin, server_url()

### Community 23 - "Price/Size Normalization"
Cohesion: 0.09
Nodes (20): _Change, The cheapest basket split the search found. A heuristic, not a proof.      Every, SplitPlan, BasketScreen, _heading(), _leg_block(), BasketReport, BasketRow (+12 more)

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
Nodes (19): exclude_keywords, field, max_size_ml, size_from, size_pattern, title, variant_label, exclusiveMinimum (+11 more)

### Community 29 - "Discovery CLI Reporting"
Cohesion: 0.06
Nodes (57): api, ApiError, authToken(), readDetail(), request(), Window, refusalReason(), streamUrl() (+49 more)

### Community 30 - "Store Timestamp Tests"
Cohesion: 0.27
Nodes (9): Any, Connection, Command-line entry point.  Subcommands will be added incrementally as the projec, Scan every perfume against every site and print each site as it lands.      One, Write one site's rows in a transaction of its own.      Per site rather than per, One line per site: which site, how it went, and what it said.      The site id i, _report_line(), _scan_all() (+1 more)

### Community 31 - "Live Profile Validation"
Cohesion: 0.14
Nodes (22): _canonical(), _covers(), _ends_with(), _index_of(), _match_text(), _own_identity(), Perfume matching: brand and concentration are mandatory; fuzzy matching only app, What a clone's own title says the bottle is, in the shape a query has.      Buil (+14 more)

### Community 32 - "Variant Extraction Fields"
Cohesion: 0.12
Nodes (16): attribute, script, type, additionalProperties, allOf, description, properties, type (+8 more)

### Community 33 - "_ResultRow"
Cohesion: 0.10
Nodes (36): parse_query(), Split one typed line into the perfumes it asks for, on " - ".      The separator, Split one typed line, "Dior Sauvage EDP", into the three identity parts.      Th, Whether a search result's own listing text is worth opening the page for.      J, split_queries(), title_could_match(), Tests for parfum_finder.matcher.  The thing being defended here is not "does it, test_a_brand_the_shop_writes_out_in_full_does_not_cost_the_match() (+28 more)

### Community 34 - "Fetch Strategy Probing"
Cohesion: 0.08
Nodes (41): The Textual App root. Handles screen navigation and is the app's default entry p, _age_of(), Check, _count_result_cards(), _first_result_url(), _LayerUnavailable, live_query(), _no_results_check() (+33 more)

### Community 35 - "Platform Field Mapping"
Cohesion: 0.18
Nodes (11): field_map, product_json, source, variants_path, required, additionalProperties, allOf, description (+3 more)

### Community 36 - "Shipping Config Schema"
Cohesion: 0.14
Nodes (14): free_shipping_threshold_kurus, shipping_cost_kurus, minimum, type, free_shipping_threshold_kurus, notes, shipping, shipping_cost_kurus (+6 more)

### Community 37 - "_trial"
Cohesion: 0.16
Nodes (20): _classify_single_separator(), format_price(), _parse_number(), parse_price(), parse_size_ml(), Decimal, Number parsing and formatting for prices and volumes, plus text folding.  This i, Decide whether a lone separator marks a fraction or a thousands group.      Retu (+12 more)

### Community 38 - "TUI Confirm Dialog"
Cohesion: 0.13
Nodes (27): FastAPI, create_app(), encode_basket_refresh_event(), encode_basket_report(), encode_basket_row(), encode_result_row(), encode_scan_event(), encode_site_scenario() (+19 more)

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
Cohesion: 0.13
Nodes (4): HeaderSelected, Any, The initial screen: search bar, streaming results table, notices, footer., SearchScreen

### Community 43 - "FieldConfidence"
Cohesion: 0.16
Nodes (7): PlaywrightNoResponse, RuntimeError, Navigation completed but playwright returned no Response object.      Its own ty, _FakeBrowser, _FakePage, Any, test_fetch_playwright_no_response_raises_its_own_error_type()

### Community 44 - "Decant Variant Rules"
Cohesion: 0.20
Nodes (11): _css_variant(), extract_endpoint_variants(), Any, Rung 2: read the variant list out of a platform's JSON response.      `document`, Read one variant's fields out of its container node., Read variant rows out of a parsed JSON document.      Shared by the endpoint and, Follow a dotted path into parsed JSON, e.g. "data.options.0.price".      A segme, _resolve_path() (+3 more)

### Community 45 - "_ResultRow"
Cohesion: 0.17
Nodes (44): TestClient, _auth(), _client(), db_path(), _ok_result(), Any, MonkeyPatch, Path (+36 more)

### Community 46 - "Offline Validation Fixtures"
Cohesion: 0.25
Nodes (8): type, additionalProperties, type, body, request_headers, additionalProperties, description, type

### Community 47 - "JsonLdProduct"
Cohesion: 0.17
Nodes (3): RowSelected, ResultRow, Row

### Community 48 - "._build_rows"
Cohesion: 0.09
Nodes (40): collect_prices(), DiscoveryReport, FieldConfidence, _flatten_defaults(), _format_choice(), _format_confidence(), _format_defaults(), _format_fingerprint() (+32 more)

### Community 49 - "_RecordingFetcher"
Cohesion: 0.08
Nodes (43): conn(), Connection, Path, Tests for parfum_finder.store: the timestamp helper and the schema.  The one har, A disabled site loses its basket column, but an enabled quiet one keeps one., NULL means the site has no free shipping tier at all, not a threshold of zero., Deleting a row that's already gone is a race between two screens, not a bug., The table's CHECK (qty > 0) would reject a bare 0, and the '-' key has to     su (+35 more)

### Community 50 - "Profile Age Checks"
Cohesion: 0.12
Nodes (39): _age_line(), format_live_report(), format_report(), Check one site's profile against that site's saved fixtures.      Never raises f, Validate every site, or just the ones named.      Serial rather than concurrent:, Render the validations as the offline half of the report in APP_FLOW §6.      A, The age note for one site, or None when its age is unremarkable.      A profile, Render offline and live results side by side, as APP_FLOW §6 shows them.      Bo (+31 more)

### Community 51 - "._refresh_table"
Cohesion: 0.20
Nodes (10): product_label(), Reduce a site's own title to the product it is about, spelled one way.      What, Split a title into what the bottle is and what it says it imitates.      The sec, _split_clone_reference(), test_a_clone_is_labelled_by_the_bottle_it_is_and_not_what_it_imitates(), test_a_longer_named_bottle_does_not_join_the_shorter_ones_block(), test_a_title_with_no_product_words_left_has_no_label(), test_every_shops_spelling_of_one_bottle_lands_in_one_block() (+2 more)

### Community 52 - "FetchResult"
Cohesion: 0.08
Nodes (44): Collection, BasketRow, _read_basket(), _score_basket(), basket_inputs(), build_basket_rows(), _ClimbState, _label() (+36 more)

### Community 53 - "conftest.py"
Cohesion: 0.13
Nodes (43): BaseModel, AcceptedSearch, _add_basket_item(), _AppState, BasketAddRequest, BasketQtyRequest, _load_profiles(), Any (+35 more)

### Community 54 - "Endpoint Schema Fields"
Cohesion: 0.22
Nodes (9): result_item, result_title, result_url, url_template, search, additionalProperties, description, required (+1 more)

### Community 55 - "apply_variant_rules"
Cohesion: 0.12
Nodes (17): A stale reading must never outrank the one taken after it.      latest_prices al, Whether an out-of-stock price counts as missing is the caller's call.      Dropp, The old price has to survive, and it must not become a second variant.      Appe, The title and URL are information, not identity.      A shop that rewords a list, EDT and EDP are different products at different prices.      Folding them into o, The column is 0/1, so the tri-state has to land somewhere on purpose.      Unkno, raw_title is the audit trail for a wrong match, so it cannot be blank.      A ro, Sites come from the profiles, so an id nothing synced is a mistake. (+9 more)

### Community 56 - "Request Schema Fields"
Cohesion: 0.07
Nodes (27): motion, react, react-dom, @types/react, @types/react-dom, typescript, dependencies, motion (+19 more)

### Community 57 - "_FixtureFetcher"
Cohesion: 0.15
Nodes (18): extract_embedded_variants(), extract_jsonld_variants(), _flatten_jsonld(), Rung 1: read the page's JSON-LD as flat variant rows.      A product that declar, Turn one Product and everything under it into rows., Rung 3: read the JSON blob the page carries but does not display.      Two shape, _fixture(), Read a captured product page. (+10 more)

### Community 58 - "setup_logging"
Cohesion: 0.08
Nodes (23): DOM, DOM.Iterable, ES2022, src, vite/client, vite.config.ts, compilerOptions, isolatedModules (+15 more)

### Community 59 - "_named_profile"
Cohesion: 0.13
Nodes (24): _close_browser(), _fetch_curl_cffi(), _fetch_httpx(), _fetch_playwright(), FetchResult, _launch_browser(), Any, FormData (+16 more)

### Community 60 - "._scan"
Cohesion: 0.29
Nodes (7): in_stock, price, size_raw, additionalProperties, required, type, field_map

### Community 61 - "single_site_scenarios"
Cohesion: 0.38
Nodes (11): _freeze(), MonkeyPatch, Path, Tests for parfum_finder.paths: frozen vs. source path resolution.  `ensure_user_, A source run has nothing to seed: resource_dir and user_data_dir are     already, test_ensure_user_data_is_a_noop_when_not_frozen(), test_ensure_user_data_never_overwrites_an_edited_file(), test_ensure_user_data_seeds_sites_platforms_and_hooks() (+3 more)

### Community 62 - "snapshot_rows"
Cohesion: 0.13
Nodes (19): Turn one site's hits into the rows write_snapshots is ready to store.      Share, snapshot_rows(), A 10 ml listing must never fill a basket line asking for 5 ml.      The matrix j, A shop's imitation must not be stored as the perfume it imitates.      The clone, The drop happens here so no caller can forget it.      Both the CLI and the scre, Half a site's sizes updated is worse than none of them.      The basket compares, Another house's bottle on the same results page must not enter this history., EDT and EDP are different products, so the row has to say which one this was. (+11 more)

### Community 64 - "validate_live"
Cohesion: 0.50
Nodes (3): The template this site's profile would be based on, if any., Which of the matching templates gets applied, or None for none of them.      One, _resolve_platform()

### Community 65 - "_named_profile"
Cohesion: 0.11
Nodes (28): _as_str(), _build_offer(), _build_product(), _coerce_in_stock(), _collect_offers(), _collect_products(), _collect_variants(), _has_type() (+20 more)

### Community 66 - ".__call__"
Cohesion: 0.29
Nodes (7): items, type, type, items, type, exclude_keywords, needs_review

### Community 67 - "test_cached_prices_is_empty_for_a_perfume_nobody_scanned"
Cohesion: 0.31
Nodes (9): _parse_selector(), Node, Run one "<css>::text" / "<css>::attr(name)" selector inside a node.      The nod, Run one "<css>::text" / "<css>::attr(name)" selector, reading every match., Split a "<css>::text" / "<css>::attr(name)" selector into its two parts., Read the attribute or text of one already-selected node, or None., _read_selected(), select_all() (+1 more)

### Community 68 - "field_map"
Cohesion: 0.16
Nodes (13): _choose_strategy(), _match_platforms(), Any, Path, Strategy, _qualifies(), The strategy the trials actually ran with., Pick the cheapest strategy that came back with real content, or None.      probe (+5 more)

### Community 71 - "exclude_keywords"
Cohesion: 0.14
Nodes (21): add_basket_item(), _perfume_id(), price_history(), _product_id(), Connection, Row, Write a whole scan at once and return how many prices were recorded.      Every, Do the writing, without opening a transaction of its own. (+13 more)

### Community 72 - "_scenario_block"
Cohesion: 0.33
Nodes (6): _balanced_value(), _embedded_documents(), _loads_or_skip(), Yield every JSON document the page hides, in document order., Parse `text` as JSON, yielding nothing when it isn't JSON.      Pages are full o, Return the JSON object or array beginning at or after `start`.      Scanning for

### Community 73 - "Headers"
Cohesion: 0.67
Nodes (3): SiteScenario, The two or three lines one site's scenario takes up on screen., _scenario_block()

### Community 74 - "format_age"
Cohesion: 0.29
Nodes (4): Every check run against one site's profile, in the order they ran.      Checks s, Whether the profile is old enough to be worth re-discovering., The check that broke, or None if the profile is intact., SiteValidation

### Community 81 - "ScanStatus.tsx"
Cohesion: 0.40
Nodes (3): ComposeResult, ComposeResult, Static

## Knowledge Gaps
- **201 isolated node(s):** `parfum-finder`, `$schema`, `$id`, `title`, `description` (+196 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **6 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `SearchScreen` connect `Fixture Fetcher (Tests)` to `TUI App & Screens`, `Fetch Strategy Probing`, `Title Matcher`, `Search/Basket Domain Models`, `Search Engine per Site`, `TUI App Shell`, `_NoRootParser`, `JsonLdProduct`, `ScanStatus.tsx`, `Search TUI Screen`, `FetchResult`, `conftest.py`, `Price/Size Normalization`?**
  _High betweenness centrality (0.037) - this node is a cross-community bridge._
- **Why does `PerfumeQuery` connect `Search Engine per Site` to `_ResultRow`, `Title Matcher`, `Fixture Fetcher (Tests)`, `JsonLdProduct`, `Search TUI Screen`, `FetchResult`, `Candidate Filtering`, `conftest.py`, `snapshot_rows`, `Store Timestamp Tests`, `Live Profile Validation`?**
  _High betweenness centrality (0.037) - this node is a cross-community bridge._
- **Why does `BasketScreen` connect `Price/Size Normalization` to `TUI App & Screens`, `Site Profiles & Templates`, `Title Matcher`, `TUI Confirm Dialog`, `Basket Optimizer Core`, `Fixture Fetcher (Tests)`, `ScanStatus.tsx`, `FetchResult`, `conftest.py`?**
  _High betweenness centrality (0.035) - this node is a cross-community bridge._
- **Are the 23 inferred relationships involving `PerfumeQuery` (e.g. with `BasketPriceExcluded` and `BasketRefreshFinished`) actually correct?**
  _`PerfumeQuery` has 23 INFERRED edges - model-reasoned connections that need verification._
- **Are the 23 inferred relationships involving `SiteResult` (e.g. with `RawVariant` and `Fetcher`) actually correct?**
  _`SiteResult` has 23 INFERRED edges - model-reasoned connections that need verification._
- **Are the 14 inferred relationships involving `SearchScreen` (e.g. with `ParfumFinderApp` and `SiteRunner`) actually correct?**
  _`SearchScreen` has 14 INFERRED edges - model-reasoned connections that need verification._
- **What connects `parfum-finder`, `$schema`, `$id` to the rest of the system?**
  _201 weakly-connected nodes found - possible documentation gaps or missing edges._