# Graph Report - parfum-finder  (2026-08-16)

## Corpus Check
- 106 files · ~287,815 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2330 nodes · 6409 edges · 88 communities (82 shown, 6 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 386 edges (avg confidence: 0.56)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `0eba8b20`
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
- product_label
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
- .__call__
- _LayerUnavailable
- ScanStatus.tsx
- _named_profile
- exclude_keywords
- _collect_products
- .__init__
- BasketRow
- Exception

## God Nodes (most connected - your core abstractions)
1. `PerfumeQuery` - 68 edges
2. `search_site()` - 66 edges
3. `SiteResult` - 64 edges
4. `SearchScreen` - 64 edges
5. `_profile()` - 58 edges
6. `discover()` - 56 edges
7. `Fetcher` - 50 edges
8. `_write_profile()` - 50 edges
9. `match_title()` - 48 edges
10. `BasketScreen` - 48 edges

## Surprising Connections (you probably didn't know these)
- `Shipping Non-linearity Rationale (why cheapest-per-item is wrong)` --semantically_similar_to--> `sites/ Site Profile Directory`  [INFERRED] [semantically similar]
  ARCHITECTURE.md → sites/README.md
- `Variant Pattern B (dropdown + AJAX price)` --semantically_similar_to--> `Variant Selector Detector Fix (WooCommerce 'variation' vs 'variant')`  [INFERRED] [semantically similar]
  ARCHITECTURE.md → docs/discovery-report.md
- `_FakeClient` --uses--> `ReleaseInfo`  [INFERRED]
  tests/test_updater.py → src/parfum_finder/updater.py
- `_FakeStreamResponse` --uses--> `ReleaseInfo`  [INFERRED]
  tests/test_updater.py → src/parfum_finder/updater.py
- `_FakeClient` --uses--> `DownloadProgress`  [INFERRED]
  tests/test_updater.py → src/parfum_finder/updater.py

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

## Communities (88 total, 6 thin omitted)

### Community 0 - "TUI App & Screens"
Cohesion: 0.09
Nodes (100): The Textual-based terminal UI: search and basket screens., _app(), _basket(), _cells(), _days_ago(), _leg(), _ok(), _open_basket() (+92 more)

### Community 1 - "Site Profiles & Templates"
Cohesion: 0.06
Nodes (82): _check_hook_kinds(), deep_merge(), _load_json(), load_platform_template(), load_platform_templates(), load_site_hooks(), load_site_profile(), Any (+74 more)

### Community 2 - "Title Matcher"
Cohesion: 0.14
Nodes (41): Protocol, What one site had to say about one query, and how much to trust it.      Four st, What a caller needs of run_site, as a type callers can stand a fake in for., SiteResult, SiteRunner, Fetcher, Protocol, Anything that can stand in for `fetch`.      Offline profile validation runs the (+33 more)

### Community 3 - "HTTP/Browser Fetching"
Cohesion: 0.14
Nodes (27): browser_session(), fetch(), Fetch one URL using exactly the given strategy.      `method`/`data` exist for t, Yield a fetcher that keeps one browser for every playwright page it reads., _fake_launch(), MonkeyPatch, Tests for parfum_finder.fetch.  httpx and curl_cffi are exercised against a real, Stand in for the browser process, and count how many were started. (+19 more)

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
Cohesion: 0.15
Nodes (41): CaptureFixture, ask_which_platform(), main(), Path, Scan every site for the perfumes named, store what came back, print it.      One, Ask at the terminal which of several matching templates to apply.      Asked whi, run_search(), _answers() (+33 more)

### Community 8 - "Architecture Rationale Docs"
Cohesion: 0.05
Nodes (53): basket Subset Enumeration + Local Improvement Algorithm, basket Optimizer (optimize function), Clone/Original Distinction (KLON ← <orijinal>), discover Discovery Flow, engine Concurrency Model (parallel sites, serial within site), Extraction Ladder (jsonld/endpoint/embedded/css), Fail-loud / status=suspect policy, hooks/<id>.py Escape Hatch (+45 more)

### Community 9 - "Search Engine Core"
Cohesion: 0.08
Nodes (54): HTMLParser, _check_empty_search(), _check_variant_control(), _fetch_page(), _headers(), _is_excluded(), _paced_fetcher(), _page_offers_sizes() (+46 more)

### Community 10 - "Basket Optimizer Core"
Cohesion: 0.15
Nodes (35): BasketItem, optimize(), Prices, Score one site against the basket, or against a subset of it.      `item_ids` is, Score every enabled site against the whole basket and sort the results.      Sit, Search for the cheapest way to split the basket across several sites.      Retur, One line of the shopping list: a basket row, not a unit count.      `item_id` is, single_site_scenarios() (+27 more)

### Community 11 - "Basket Store & Pricing"
Cohesion: 0.25
Nodes (8): cached_prices(), Return the latest stored price of every size of this perfume, per site.      Bra, The search screen's second search must be answered with today's numbers.      Tw, A price nobody will scan again may not be offered as a result.      Refreshing i, Nothing on record is the state before a first search, not an error.      The sea, test_cached_prices_is_empty_for_a_perfume_nobody_scanned(), test_cached_prices_leaves_out_a_disabled_site(), test_cached_prices_serves_the_latest_reading_of_every_size()

### Community 12 - "JSON-LD Product Extraction"
Cohesion: 0.13
Nodes (32): extract_jsonld_products(), Read every JSON-LD Product declared on the page, in document order.      A block, _one_product_html(), Tests for parfum_finder.extract.  Every case here is a shape a real store actual, Wrap a JSON-LD product body in a page, for the one-field-at-a-time cases., test_a_broken_block_does_not_lose_the_valid_one(), test_availability_spellings_all_land_in_the_same_bucket(), test_boolean_values_are_never_read_as_price_or_text() (+24 more)

### Community 13 - "Basket TUI Screen"
Cohesion: 0.10
Nodes (36): PyInstaller entry point for the packaged desktop app.  Kept outside src/parfum_f, _hold_app_mutex(), main(), _ping(), Path, The Windows desktop entry point: an ephemeral-port FastAPI backend behind a nati, Kurulum dosyasının uygulamanın açık olduğunu görmesini sağlar.      packaging/in, Best-effort native message box.      A missing WebView2 Runtime is the expected (+28 more)

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
Cohesion: 0.09
Nodes (49): Run one site and classify what came back instead of raising.      It is also whe, run_site(), _counting_fetcher(), _profile(), Exception, Tests for the profile-driven search in parfum_finder.engine.  What these defend, Answer each call with the next canned result, then repeat the last one., A minimal working profile, with the fields a case cares about swapped in. (+41 more)

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
Cohesion: 0.24
Nodes (26): now_iso(), Return the current UTC time as 'YYYY-MM-DDTHH:MM:SSZ'.      Every timestamp writ, _basket_row(), _collect(), _ok_result(), _profile(), Any, MonkeyPatch (+18 more)

### Community 22 - "Basket Site Scenarios"
Cohesion: 0.24
Nodes (6): BaseHTTPRequestHandler, _Handler, _playwright_usable(), Shared pytest fixtures.  A local HTTP server used by fetch/probe tests: real req, Whether the playwright rung can actually run here, binary included.      Checkin, server_url()

### Community 23 - "Price/Size Normalization"
Cohesion: 0.15
Nodes (7): _Change, BasketScreen, BasketRow, Path, The basket: the list on top, one scenario per site underneath., _remove(), _set_qty()

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
Nodes (60): api, ApiError, authToken(), readDetail(), request(), Window, refusalReason(), streamUrl() (+52 more)

### Community 30 - "Store Timestamp Tests"
Cohesion: 0.13
Nodes (20): Any, Connection, Command-line entry point.  Subcommands will be added incrementally as the projec, Scan every perfume against every site and print each site as it lands.      One, Write one site's rows in a transaction of its own.      Per site rather than per, One line per site: which site, how it went, and what it said.      The site id i, _report_line(), _scan_all() (+12 more)

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
Nodes (34): BaseModel, BasketLine, BasketPrice, BasketSite, Client, FastAPI, AcceptedSearch, _add_basket_item() (+26 more)

### Community 35 - "Platform Field Mapping"
Cohesion: 0.18
Nodes (11): field_map, product_json, source, variants_path, required, additionalProperties, allOf, description (+3 more)

### Community 36 - "Shipping Config Schema"
Cohesion: 0.14
Nodes (14): free_shipping_threshold_kurus, shipping_cost_kurus, minimum, type, free_shipping_threshold_kurus, notes, shipping, shipping_cost_kurus (+6 more)

### Community 37 - "_trial"
Cohesion: 0.14
Nodes (22): _classify_single_separator(), format_age(), format_ml(), _parse_number(), parse_price(), parse_size_ml(), Decimal, Number parsing and formatting for prices and volumes, plus text folding.  This i (+14 more)

### Community 38 - "TUI Confirm Dialog"
Cohesion: 0.21
Nodes (16): encode_basket_refresh_event(), encode_basket_report(), encode_basket_row(), encode_result_row(), encode_scan_event(), encode_site_scenario(), _encode_split_leg(), encode_split_plan() (+8 more)

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
Cohesion: 0.10
Nodes (28): Exception, fetch_latest_release(), En son yayımlanmış sürüm, ya da ulaşılamadıysa None.      /releases/latest tasla, _enable_checks(), _factory(), _FakeClient, _FakeStreamResponse, _patch_get() (+20 more)

### Community 43 - "FieldConfidence"
Cohesion: 0.22
Nodes (3): _FakeBrowser, _FakePage, Any

### Community 44 - "Decant Variant Rules"
Cohesion: 0.14
Nodes (15): _balanced_value(), _embedded_documents(), extract_endpoint_variants(), _loads_or_skip(), Any, Rung 2: read the variant list out of a platform's JSON response.      `document`, Yield every JSON document the page hides, in document order., Parse `text` as JSON, yielding nothing when it isn't JSON.      Pages are full o (+7 more)

### Community 45 - "_ResultRow"
Cohesion: 0.13
Nodes (54): SiteResult, create_app(), SiteRunner, TestClient, _auth(), _client(), db_path(), _ok_result() (+46 more)

### Community 46 - "Offline Validation Fixtures"
Cohesion: 0.25
Nodes (8): type, additionalProperties, type, body, request_headers, additionalProperties, description, type

### Community 47 - "JsonLdProduct"
Cohesion: 0.09
Nodes (36): _age_of(), Check, _count_result_cards(), _first_result_url(), _LayerUnavailable, live_query(), _no_results_check(), _path() (+28 more)

### Community 48 - "._build_rows"
Cohesion: 0.08
Nodes (39): _choose_strategy(), DiscoveryReport, FieldConfidence, _flatten_defaults(), _format_choice(), _format_confidence(), _format_defaults(), _format_fingerprint() (+31 more)

### Community 49 - "_RecordingFetcher"
Cohesion: 0.08
Nodes (48): add_basket_item(), Add a size of a perfume to the basket, and return the basket_item_id.      The p, conn(), Connection, Path, Tests for parfum_finder.store: the timestamp helper and the schema.  The one har, A stale reading must never outrank the one taken after it.      latest_prices al, A 10 ml listing must never fill a basket line asking for 5 ml.      The matrix j (+40 more)

### Community 50 - "Profile Age Checks"
Cohesion: 0.11
Nodes (44): format_live_report(), format_report(), Check one site's profile against that site's saved fixtures.      Never raises f, Validate every site, or just the ones named.      Serial rather than concurrent:, Run one site's profile against the real site.      Same contract as offline mode, Render the validations as the offline half of the report in APP_FLOW §6.      A, Render offline and live results side by side, as APP_FLOW §6 shows them.      Bo, validate_all_offline() (+36 more)

### Community 51 - "._refresh_table"
Cohesion: 0.27
Nodes (13): apply_variant_rules(), Turn raw size rows into decant variants, dropping what is not a decant.      Thr, _row(), test_a_keyword_in_the_size_label_excludes_the_row_too(), test_a_literal_zero_price_reads_as_no_price_not_a_free_perfume(), test_a_size_at_the_threshold_is_a_bottle_whatever_it_calls_itself(), test_a_size_that_cannot_be_read_is_dropped(), test_an_uppercase_turkish_keyword_still_matches() (+5 more)

### Community 52 - "FetchResult"
Cohesion: 0.11
Nodes (28): BasketReport, compare_split_to_best_full(), Every site's single-site scenario, split by whether it covers everything.      A, The cheapest basket split the search found. A heuristic, not a proof.      Every, Score a split plan against the cheapest full-coverage single site.      Only the, SplitPlan, format_price(), Format a price for display (comma-thousands, dot-decimal).      Decimal('1250') (+20 more)

### Community 53 - "conftest.py"
Cohesion: 0.11
Nodes (34): Collection, basket_inputs(), build_basket_rows(), _ClimbState, _label(), BasketRow, Basket scenario evaluation. A pure function, no network access, no sqlite.  Inpu, One site's share of a split basket: what to buy there and what it costs.      `s (+26 more)

### Community 54 - "Endpoint Schema Fields"
Cohesion: 0.22
Nodes (9): result_item, result_title, result_url, url_template, search, additionalProperties, description, required (+1 more)

### Community 55 - "apply_variant_rules"
Cohesion: 0.13
Nodes (22): One call has to leave a row the search table can read straight off.      The cal, The old price has to survive, and it must not become a second variant.      Appe, first_seen is what says how long a shop has carried a size., The title and URL are information, not identity.      A shop that rewords a list, EDT and EDP are different products at different prices.      Folding them into o, A sold-out size often shows no price at all, and 0 would mean free.      Writing, The column is 0/1, so the tri-state has to land somewhere on purpose.      Unkno, raw_title is the audit trail for a wrong match, so it cannot be blank.      A ro (+14 more)

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
Cohesion: 0.15
Nodes (21): _close_browser(), _fetch_curl_cffi(), _fetch_httpx(), _fetch_playwright(), _launch_browser(), PlaywrightNoResponse, PlaywrightNotInstalled, Any (+13 more)

### Community 60 - "._scan"
Cohesion: 0.29
Nodes (7): _NoRootParser, MonkeyPatch, Record every delay the engine asks for instead of serving it.      Waiting for r, Stands in for HTMLParser when a page's markup cannot be read at all.      select, slept(), test_a_product_page_with_no_root_names_its_body_size(), test_a_search_page_with_no_root_names_its_body_size()

### Community 61 - "single_site_scenarios"
Cohesion: 0.17
Nodes (23): ExtractionFailed, RuntimeError, A page answered but gave up nothing, where something was expected.      This is, Run one query against one site and read every hit's sizes.      Everything site-, search_site(), Path, Give the test profile's site id a hook file. The id is what binds them., test_a_before_search_that_returns_no_query_is_refused() (+15 more)

### Community 62 - "snapshot_rows"
Cohesion: 0.11
Nodes (23): Turn one site's hits into the rows write_snapshots is ready to store.      Share, snapshot_rows(), A shop's imitation must not be stored as the perfume it imitates.      The clone, The drop happens here so no caller can forget it.      Both the CLI and the scre, A slow site must not spread one reading across several timestamps.      Rows wri, The number reported is what landed in the history, not what was offered., Half a site's sizes updated is worse than none of them.      The basket compares, Another house's bottle on the same results page must not enter this history. (+15 more)

### Community 64 - "validate_live"
Cohesion: 0.11
Nodes (24): check_enabled(), check_for_update(), handoff_command(), _installer_asset(), is_newer(), launch_installer(), _no_update(), _pad() (+16 more)

### Community 65 - "_named_profile"
Cohesion: 0.10
Nodes (35): _as_str(), _build_offer(), _build_product(), _coerce_in_stock(), _collect_offers(), _collect_variants(), _css_variant(), JsonLdOffer (+27 more)

### Community 66 - "product_label"
Cohesion: 0.20
Nodes (10): product_label(), Reduce a site's own title to the product it is about, spelled one way.      What, Split a title into what the bottle is and what it says it imitates.      The sec, _split_clone_reference(), test_a_clone_is_labelled_by_the_bottle_it_is_and_not_what_it_imitates(), test_a_longer_named_bottle_does_not_join_the_shorter_ones_block(), test_a_title_with_no_product_words_left_has_no_label(), test_every_shops_spelling_of_one_bottle_lands_in_one_block() (+2 more)

### Community 67 - "test_cached_prices_is_empty_for_a_perfume_nobody_scanned"
Cohesion: 0.15
Nodes (18): BasketRefreshSession, In-memory session state for the two streamed operations: a search scan and a bas, ScanSession, _about(), _cached_result_row(), ResultRow, Turn one stored price back into the row the table shows.      Everything the tab, Rebuild the table's rows for every searched perfume already on record.      Site (+10 more)

### Community 68 - "field_map"
Cohesion: 0.24
Nodes (9): CacheKey, CandidateFilter, _candidates_to_open(), Path, Run every site against one query, all at once, and report each separately., Narrow the search results down to the pages worth a request.      The first one, run_sites(), test_no_sites_is_an_empty_run_not_a_crash() (+1 more)

### Community 71 - "exclude_keywords"
Cohesion: 0.10
Nodes (31): basket_lines(), basket_prices(), basket_sites(), _perfume_id(), _product_id(), Connection, datetime, SQLite persistence: an append-only price history.  Tables: sites, perfumes, prod (+23 more)

### Community 72 - "_scenario_block"
Cohesion: 0.29
Nodes (7): in_stock, price, size_raw, additionalProperties, required, type, field_map

### Community 73 - "Headers"
Cohesion: 0.18
Nodes (17): collect_prices(), _format_product(), _format_stock(), _format_trial(), _has_exact_price(), PageTrial, Decimal, One page fetched with the chosen strategy and read for JSON-LD.      A fetch tha (+9 more)

### Community 74 - "format_age"
Cohesion: 0.22
Nodes (6): _age_line(), Every check run against one site's profile, in the order they ran.      Checks s, Whether the profile is old enough to be worth re-discovering., The check that broke, or None if the profile is intact., The age note for one site, or None when its age is unremarkable.      A profile, SiteValidation

### Community 75 - "_NoRootParser"
Cohesion: 0.18
Nodes (4): Any, Just enough of an httpx streaming response to be downloaded from., _RecordingClient, _RecordingStream

### Community 76 - "enum"
Cohesion: 0.38
Nodes (11): _freeze(), MonkeyPatch, Path, Tests for parfum_finder.paths: frozen vs. source path resolution.  `ensure_user_, A source run has nothing to seed: resource_dir and user_data_dir are     already, test_ensure_user_data_is_a_noop_when_not_frozen(), test_ensure_user_data_never_overwrites_an_edited_file(), test_ensure_user_data_seeds_sites_platforms_and_hooks() (+3 more)

### Community 77 - "_collect_products"
Cohesion: 0.29
Nodes (7): price_history(), Row, Return one variant's past readings, newest first, capped at limit.      Empty fo, The trend panel reads row 0 as the latest reading, so order is the point.      A, No history yet is a normal state for a variant, not an error to raise on., test_price_history_is_empty_for_an_unknown_variant(), test_price_history_is_newest_first_and_capped_at_limit()

### Community 79 - ".__call__"
Cohesion: 0.53
Nodes (4): FormData, Headers, Method, Strategy

### Community 80 - "_LayerUnavailable"
Cohesion: 0.22
Nodes (10): Lock, listing_filter(), Decide, from a search result's own title, whether to open its page.      Structu, Any, Path, A site's display name, with a badge when its profile is old enough     to be wor, Show what storage already knows, then go to the shops for the rest.      `force=, run_scan() (+2 more)

### Community 81 - "ScanStatus.tsx"
Cohesion: 0.22
Nodes (4): Pressed, ConfirmScreen, Path, Asks before a low-confidence match is written to the basket.      The two answer

### Community 82 - "_named_profile"
Cohesion: 0.31
Nodes (9): _named_profile(), Any, The real fetcher, with a list of every URL it was asked for., A profile whose search page lists two houses' bottles, as shops do., test_a_listing_from_another_house_costs_no_product_request(), test_one_product_listed_under_two_searches_is_read_once(), test_two_shops_sharing_a_url_do_not_read_each_others_pages(), test_without_a_filter_every_listing_is_still_opened() (+1 more)

### Community 83 - "exclude_keywords"
Cohesion: 0.29
Nodes (7): items, type, type, items, type, exclude_keywords, needs_review

### Community 84 - "_collect_products"
Cohesion: 0.50
Nodes (4): _collect_products(), _has_type(), Walk a parsed JSON-LD block and append every Product found, depth first.      De, Whether a node's "@type" names `name`, as a string or inside a list.      Substr

## Knowledge Gaps
- **201 isolated node(s):** `View`, `Toast`, `Window`, `SiteStatus`, `BasketReport` (+196 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **6 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `SiteResult` connect `Title Matcher` to `TUI App & Screens`, `test_cached_prices_is_empty_for_a_perfume_nobody_scanned`, `field_map`, `Search/Basket Domain Models`, `exclude_keywords`, `Search Engine Core`, `_LayerUnavailable`, `Offline Profile Validation`, `conftest.py`, `Candidate Filtering`, `snapshot_rows`, `_named_profile`, `Store Timestamp Tests`?**
  _High betweenness centrality (0.029) - this node is a cross-community bridge._
- **Why does `UpdateDownload` connect `Fetch Strategy Probing` to `validate_live`, `Fixture Fetcher (Tests)`, `_NoRootParser`, `_ResultRow`?**
  _High betweenness centrality (0.028) - this node is a cross-community bridge._
- **Why does `discover()` connect `Platform Discovery Flow` to `Site Profiles & Templates`, `CLI Entry Points`, `Product Extraction`, `._build_rows`, `Store Timestamp Tests`?**
  _High betweenness centrality (0.028) - this node is a cross-community bridge._
- **Are the 23 inferred relationships involving `PerfumeQuery` (e.g. with `BasketPriceExcluded` and `BasketRefreshFinished`) actually correct?**
  _`PerfumeQuery` has 23 INFERRED edges - model-reasoned connections that need verification._
- **Are the 23 inferred relationships involving `SiteResult` (e.g. with `RawVariant` and `Fetcher`) actually correct?**
  _`SiteResult` has 23 INFERRED edges - model-reasoned connections that need verification._
- **Are the 14 inferred relationships involving `SearchScreen` (e.g. with `ParfumFinderApp` and `SiteRunner`) actually correct?**
  _`SearchScreen` has 14 INFERRED edges - model-reasoned connections that need verification._
- **What connects `View`, `Toast`, `Window` to the rest of the system?**
  _201 weakly-connected nodes found - possible documentation gaps or missing edges._