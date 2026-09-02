# Graph Report - parfum-finder  (2026-09-01)

## Corpus Check
- 137 files · ~318,456 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2643 nodes · 7471 edges · 96 communities (90 shown, 6 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 536 edges (avg confidence: 0.57)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `7b214dbc`
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
- .__init__
- write_snapshots
- _css_variant
- ConfirmDialog.tsx
- ResultRow
- SplitPlan
- _collect_products
- AddButton.tsx
- run_sites
- Node
- _wait_until
- enum
- BasketRow
- helpers.ts
- handoff_command
- ._write_to_sheet
- ._start_search
- _FakeStreamResponse
- _scenario_block
- Arayüz testleri
- cached_prices
- .on_mount
- Static

## God Nodes (most connected - your core abstractions)
1. `PerfumeQuery` - 74 edges
2. `search_site()` - 70 edges
3. `_profile()` - 69 edges
4. `connect()` - 66 edges
5. `SearchScreen` - 64 edges
6. `discover()` - 56 edges
7. `match_title()` - 55 edges
8. `SiteRunner` - 54 edges
9. `FetchResult` - 52 edges
10. `Fetcher` - 52 edges

## Surprising Connections (you probably didn't know these)
- `Shipping Non-linearity Rationale (why cheapest-per-item is wrong)` --semantically_similar_to--> `sites/ Site Profile Directory`  [INFERRED] [semantically similar]
  ARCHITECTURE.md → sites/README.md
- `Variant Pattern B (dropdown + AJAX price)` --semantically_similar_to--> `Variant Selector Detector Fix (WooCommerce 'variation' vs 'variant')`  [INFERRED] [semantically similar]
  ARCHITECTURE.md → docs/discovery-report.md
- `test_memory_database_initializes_without_wal()` --calls--> `connect()`  [EXTRACTED]
  tests/test_store.py → src/parfum_finder/store.py
- `test_real_measurement_picks_httpx_for_a_plain_page()` --indirect_call--> `DiscoveryReport`  [INFERRED]
  tests/test_discover.py → src/parfum_finder/discover.py
- `test_a_hook_that_reads_nothing_is_named_as_the_culprit()` --indirect_call--> `ExtractionFailed`  [INFERRED]
  tests/test_engine.py → src/parfum_finder/engine.py

## Import Cycles
- 3-file cycle: `src/parfum_finder/__init__.py -> src/parfum_finder/cli.py -> src/parfum_finder/validate.py -> src/parfum_finder/__init__.py`
- 3-file cycle: `src/parfum_finder/__init__.py -> src/parfum_finder/cli.py -> src/parfum_finder/profiles.py -> src/parfum_finder/__init__.py`
- 3-file cycle: `src/parfum_finder/__init__.py -> src/parfum_finder/cli.py -> src/parfum_finder/logging_setup.py -> src/parfum_finder/__init__.py`
- 4-file cycle: `src/parfum_finder/__init__.py -> src/parfum_finder/cli.py -> src/parfum_finder/validate.py -> src/parfum_finder/profiles.py -> src/parfum_finder/__init__.py`
- 4-file cycle: `src/parfum_finder/__init__.py -> src/parfum_finder/cli.py -> src/parfum_finder/engine.py -> src/parfum_finder/profiles.py -> src/parfum_finder/__init__.py`
- 4-file cycle: `src/parfum_finder/__init__.py -> src/parfum_finder/cli.py -> src/parfum_finder/discover.py -> src/parfum_finder/profiles.py -> src/parfum_finder/__init__.py`
- 5-file cycle: `src/parfum_finder/__init__.py -> src/parfum_finder/cli.py -> src/parfum_finder/validate.py -> src/parfum_finder/engine.py -> src/parfum_finder/profiles.py -> src/parfum_finder/__init__.py`

## Hyperedges (group relationships)
- **Sites Implementing Variant Pattern C (embedded JSON)** — docs_discovery_report_venco_site, docs_discovery_report_decantall_site, docs_discovery_report_luxurydekant_site, docs_discovery_report_ruxangroup_site, architecture_md_variant_pattern_c [EXTRACTED 1.00]
- **İdeasoft Platform Sites and Endpoint** — docs_discovery_report_dekantparfum_site, docs_discovery_report_dekantdoktoru_site, docs_discovery_report_ideasoft_related_options_endpoint, platforms_readme_ideasoft_json [EXTRACTED 1.00]
- **discover Command Output Artifacts (profile + fixtures + CI validation)** — architecture_md_discover_flow, sites_readme_sites_dir, fixtures_readme_fixtures_dir, github_workflows_ci_validate_profiles_step, architecture_md_validate_command [INFERRED 0.85]

## Communities (96 total, 6 thin omitted)

### Community 0 - "TUI App & Screens"
Cohesion: 0.09
Nodes (100): The Textual-based terminal UI: search and basket screens., _app(), _basket(), _cells(), _days_ago(), _leg(), _ok(), _open_basket() (+92 more)

### Community 1 - "Site Profiles & Templates"
Cohesion: 0.06
Nodes (82): _check_hook_kinds(), deep_merge(), _load_json(), load_platform_template(), load_platform_templates(), load_site_hooks(), load_site_profile(), Any (+74 more)

### Community 2 - "Title Matcher"
Cohesion: 0.08
Nodes (34): _check_empty_search(), ExtractionFailed, RuntimeError, Fail when a search yielded no rows off a page that plainly lists products., A page answered but gave up nothing, where something was expected.      This is, Run one query against one site and read every hit's sizes.      Everything site-, search_site(), _NoRootParser (+26 more)

### Community 3 - "HTTP/Browser Fetching"
Cohesion: 0.18
Nodes (22): browser_session(), Yield a fetcher that keeps one browser for every playwright page it reads., _fake_launch(), Event, MonkeyPatch, Tests for parfum_finder.fetch.  httpx and curl_cffi are exercised against a real, Stand in for the browser process, and count how many were started., _read_one_page_then_hang() (+14 more)

### Community 4 - "Search/Basket Domain Models"
Cohesion: 0.05
Nodes (136): Screen, ProductCandidate, Dependency-free models shared by search, persistence, and presentation., One decant size of one product, in the units the database stores.      Tenths of, A candidate together with the decant sizes its product page offers., What one site had to say about one query, and how much to trust it.      Four st, One hit on a search results page, before its product page is opened.      `raw_t, SearchHit (+128 more)

### Community 5 - "Search Engine per Site"
Cohesion: 0.27
Nodes (11): fetch_latest_release(), En son yayımlanmış sürüm, ya da ulaşılamadıysa None.      /releases/latest tasla, _enable_checks(), _patch_get(), MonkeyPatch, The .exe is what gets downloaded, whatever else is attached.      Releases carry, _release_payload(), test_check_is_off_outside_a_frozen_build() (+3 more)

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
Nodes (74): HTMLParser, _canonical_path(), canonical_url(), _check_variant_control(), _decode_unreserved(), _fetch_page(), _has_product_ancestor(), _headers() (+66 more)

### Community 10 - "Basket Optimizer Core"
Cohesion: 0.13
Nodes (38): Collection, BasketRow, _score_basket(), BasketItem, optimize(), Prices, Score one site against the basket, or against a subset of it.      `item_ids` is, Score every enabled site against the whole basket and sort the results.      Sit (+30 more)

### Community 11 - "Basket Store & Pricing"
Cohesion: 0.24
Nodes (17): handoff_command(), Uygulamanın kapanmasını bekleyen ayrık PowerShell komutu., _factory(), _handoff_script(), Path, Tests for parfum_finder.updater: the version compare, the release read, and the, An error state is what turns the button back on with a reason.      Falling back, Nothing is spawned unless a complete file is on disk.      Running a half-writte (+9 more)

### Community 12 - "JSON-LD Product Extraction"
Cohesion: 0.09
Nodes (48): extract_embedded_variants(), extract_jsonld_products(), extract_jsonld_variants(), _flatten_jsonld(), Read every JSON-LD Product declared on the page, in document order.      A block, Rung 1: read the page's JSON-LD as flat variant rows.      A product that declar, Turn one Product and everything under it into rows., Rung 3: read the JSON blob the page carries but does not display.      Two shape (+40 more)

### Community 13 - "Basket TUI Screen"
Cohesion: 0.08
Nodes (47): PyInstaller entry point for the packaged desktop app.  Kept outside src/parfum_f, _close_window_when_asked(), _hold_app_mutex(), _kill_children_with_app(), main(), _ping(), Event, Path (+39 more)

### Community 14 - "Platform Schema"
Cohesion: 0.06
Nodes (31): any, defaults, fingerprint, additionalProperties, items, minItems, type, description (+23 more)

### Community 15 - "Product Extraction"
Cohesion: 0.08
Nodes (38): _age_of(), Check, _count_result_cards(), _first_result_url(), _LayerUnavailable, live_query(), _no_results_check(), _path() (+30 more)

### Community 16 - "Schema Field Patterns"
Cohesion: 0.06
Nodes (33): format, pattern, type, pattern, type, default, type, pattern (+25 more)

### Community 17 - "Offline Profile Validation"
Cohesion: 0.21
Nodes (13): _named_profile(), Any, The real fetcher, with a list of every URL it was asked for., A profile whose search page lists two houses' bottles, as shops do., test_a_broken_profile_is_still_suspect_when_no_title_looked_right(), test_a_listing_from_another_house_costs_no_product_request(), test_a_scan_says_how_many_listings_it_skipped(), test_diagnostic_candidate_checks_extraction_but_never_emits_a_hit() (+5 more)

### Community 18 - "Playwright Errors"
Cohesion: 0.10
Nodes (30): Any, Connection, Command-line entry point.  Subcommands will be added incrementally as the projec, Scan every perfume against every site and print each site as it lands.      One, Write one site's rows in a transaction of its own.      Per site rather than per, One line per site: which site, how it went, and what it said.      The site id i, _report_line(), _scan_all() (+22 more)

### Community 19 - "Search TUI Screen"
Cohesion: 0.08
Nodes (41): find_header_columns(), find_match(), open_worksheet(), Any, Exception, Path, Protocol, Writing a search result onto the user's own Google Sheets wishlist.  The wishlis (+33 more)

### Community 20 - "Snapshot Writing"
Cohesion: 0.18
Nodes (22): grouped_value(), Decimal, ResultRow, Pure sorting and grouping rules for the results table.  No I/O, no Textual state, What each site charges for the product a block is about.      One entry per site, The default order: typed order, product, site, size.      The typed order comes, The order once a column has been picked: the site layer drops out.      Asking f, site_ranks() (+14 more)

### Community 21 - "Candidate Filtering"
Cohesion: 0.08
Nodes (40): add_basket_item(), Add a size of a perfume to the basket, and return the basket_item_id.      The p, Connection, Adding the same perfume and size twice must accumulate, not clobber.      The ba, A basket line for a perfume nobody has priced is a bug, not a state to keep., The basket screen prints brand/name/concentration straight off this row.      Or, Two lines added within the same second must still read back the same way twice., A basket line nobody sells must still be visible via basket_lines.      basket_p (+32 more)

### Community 22 - "Basket Site Scenarios"
Cohesion: 0.26
Nodes (12): encode_basket_report(), encode_result_row(), encode_scan_event(), encode_site_scenario(), _encode_split_leg(), encode_split_plan(), Any, BasketReport (+4 more)

### Community 23 - "Price/Size Normalization"
Cohesion: 0.22
Nodes (9): is_newer(), _pad(), parse_version(), v0.2.1 -> (0, 2, 1). Sayıya çevrilemeyen her şey None., Okunamayan bir sürüm asla "yeni" sayılmaz.      Yanlış tarafa düşmenin bedeli si, A tag nobody can order against must not open a dialog.      The two failure dire, test_an_unreadable_tag_never_counts_as_an_update(), test_is_newer() (+1 more)

### Community 24 - "JSON Schema Primitives"
Cohesion: 0.11
Nodes (25): integer, null, string, properties, type, type, type, type (+17 more)

### Community 25 - "SQLite Store"
Cohesion: 0.10
Nodes (25): conn(), Path, Tests for parfum_finder.store: the timestamp helper and the schema.  The one har, Nothing on record is the state before a first search, not an error.      The sea, A disabled site loses its basket column, but an enabled quiet one keeps one., NULL means the site has no free shipping tier at all, not a threshold of zero., An update aimed at a row that isn't there means the caller is out of sync., The recents list has five slots, so a repeat must not consume two.      Someone (+17 more)

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
Cohesion: 0.37
Nodes (12): _freeze(), MonkeyPatch, Path, Tests for parfum_finder.paths: frozen vs. source path resolution.  `ensure_user_, A source run has nothing to seed: resource_dir and user_data_dir are     already, test_ensure_user_data_is_a_noop_when_not_frozen(), test_ensure_user_data_never_overwrites_an_edited_file(), test_ensure_user_data_seeds_sites_platforms_and_hooks() (+4 more)

### Community 30 - "Store Timestamp Tests"
Cohesion: 0.07
Nodes (28): UpdateDialog(), BasketResponse, BasketRow, BestCombination, ResultsResponse, SiteScenario, INFO, basket() (+20 more)

### Community 31 - "Live Profile Validation"
Cohesion: 0.09
Nodes (37): Pattern, _brand_pattern(), _canonical(), _canonical_brands(), _covers(), _ends_with(), _index_of(), listing_filter() (+29 more)

### Community 32 - "Variant Extraction Fields"
Cohesion: 0.11
Nodes (18): attribute, in_stock, price, script, size_raw, type, properties, additionalProperties (+10 more)

### Community 33 - "_ResultRow"
Cohesion: 0.08
Nodes (46): parse_query(), product_label(), Split one typed line, "Dior Sauvage EDP", into the three identity parts.      Th, Reduce a site's own title to the product it is about, spelled one way.      What, Whether a search result's own listing text is worth opening the page for.      J, title_could_match(), test_reported_false_negative_searches_keep_requested_identity_and_sizes(), Tests for parfum_finder.matcher.  The thing being defended here is not "does it (+38 more)

### Community 34 - "Fetch Strategy Probing"
Cohesion: 0.21
Nodes (8): _FixtureFetcher, FormData, Headers, Method, Path, Strategy, Serves one site's saved capture in place of the network.      Only three kinds o, The one real result card that led to the captured product page.          Cut out

### Community 35 - "Platform Field Mapping"
Cohesion: 0.12
Nodes (16): field_map, product_json, source, variants_path, additionalProperties, allOf, description, required (+8 more)

### Community 36 - "Shipping Config Schema"
Cohesion: 0.14
Nodes (14): free_shipping_threshold_kurus, shipping_cost_kurus, minimum, type, free_shipping_threshold_kurus, notes, shipping, shipping_cost_kurus (+6 more)

### Community 37 - "_trial"
Cohesion: 0.18
Nodes (17): _classify_single_separator(), _parse_number(), parse_price(), parse_size_ml(), Decimal, Number parsing and formatting for prices and volumes, plus text folding.  This i, Decide whether a lone separator marks a fraction or a thousands group.      Retu, Parse a price string, e.g. '1.250,00 TL' -> Decimal('1250.00').      Recognizes (+9 more)

### Community 38 - "TUI Confirm Dialog"
Cohesion: 0.08
Nodes (39): datetime, _recent_searches(), _remove_basket_item(), _set_basket_qty(), cached_prices(), _calendar_months_before(), _downsample_price_snapshots(), _downsample_sql() (+31 more)

### Community 39 - "TUI App Shell"
Cohesion: 0.15
Nodes (16): format_price(), Format a price for display (comma-thousands, dot-decimal).      Decimal('1250'), _heading(), _leg_block(), BasketReport, Prices, SiteScenario, SplitLeg (+8 more)

### Community 40 - "Fetch Backends"
Cohesion: 0.14
Nodes (14): curl_cffi, httpx, playwright, result_item, result_title, result_url, strategy, url_template (+6 more)

### Community 41 - "HTTP Request Schema"
Cohesion: 0.14
Nodes (14): GET, POST, properties, default, enum, type, type, type (+6 more)

### Community 42 - "Fixture Fetcher (Tests)"
Cohesion: 0.13
Nodes (45): BaseModel, FastAPI, AcceptedSearch, _add_basket_item(), _AppState, BasketAddRequest, BasketQtyRequest, create_app() (+37 more)

### Community 43 - "FieldConfidence"
Cohesion: 0.14
Nodes (11): PlaywrightNoResponse, PlaywrightNotInstalled, RuntimeError, The "playwright" strategy was requested but cannot run at all.      Covers both, Navigation completed but playwright returned no Response object.      Its own ty, _FakeBrowser, _FakePage, Any (+3 more)

### Community 44 - "Decant Variant Rules"
Cohesion: 0.13
Nodes (25): api, ApiError, authToken(), readDetail(), request(), Window, Toast, View (+17 more)

### Community 45 - "_ResultRow"
Cohesion: 0.10
Nodes (59): TestClient, _auth(), _client(), db_path(), _ok_result(), Any, MonkeyPatch, Path (+51 more)

### Community 46 - "Offline Validation Fixtures"
Cohesion: 0.25
Nodes (8): type, additionalProperties, type, body, request_headers, additionalProperties, description, type

### Community 47 - "JsonLdProduct"
Cohesion: 0.14
Nodes (24): refusalReason(), streamUrl(), useEventStream(), ProgressBar(), ScanStatus(), VerdictAddButton(), basketKey(), formatAge() (+16 more)

### Community 48 - "._build_rows"
Cohesion: 0.07
Nodes (53): _choose_strategy(), collect_prices(), DiscoveryReport, FieldConfidence, _flatten_defaults(), _format_choice(), _format_confidence(), _format_defaults() (+45 more)

### Community 49 - "_RecordingFetcher"
Cohesion: 0.11
Nodes (42): How long the shop asked to be left alone, or None if it did not say.      A refu, Run one site and classify what came back instead of raising.      It is also whe, _retry_after_s(), run_site(), FetchResult, One fetched page, uniform regardless of which strategy produced it., _counting_fetcher(), _profile() (+34 more)

### Community 50 - "Profile Age Checks"
Cohesion: 0.08
Nodes (50): _age_line(), format_live_report(), format_report(), Every check run against one site's profile, in the order they ran.      Checks s, Whether the profile is old enough to be worth re-discovering., Every site that has a profile, sorted so reports read the same way twice., Check one site's profile against that site's saved fixtures.      Never raises f, Validate every site, or just the ones named.      Serial rather than concurrent: (+42 more)

### Community 51 - "._refresh_table"
Cohesion: 0.16
Nodes (25): apply_variant_rules(), Turn raw size rows into decant variants, dropping what is not a decant.      Thr, Try spelling variants until this site returns an emittable match.      The match, run_site_attempts(), _attempt_hit(), Tests for the profile-driven search in parfum_finder.engine.  What these defend, _row(), test_a_keyword_in_the_size_label_excludes_the_row_too() (+17 more)

### Community 52 - "FetchResult"
Cohesion: 0.14
Nodes (45): Lock, _record_search(), Any, BasketRow, Path, A site's display name, with a badge when its profile is old enough     to be wor, Rebuild the table's rows for every searched perfume already on record.      Site, Show what storage already knows, then go to the shops for the rest.      `force= (+37 more)

### Community 53 - "conftest.py"
Cohesion: 0.29
Nodes (11): _normalized_product_name(), Recognize a single product page after a material same-origin redirect., _redirect_product_candidate(), _redirect_page(), test_material_redirect_cleans_tracking_and_rejects_cross_origin_metadata_url(), test_metadata_formats_agree_across_typographic_separators(), test_multiple_top_level_microdata_products_are_ambiguous(), test_nested_related_product_name_does_not_name_the_page_scope() (+3 more)

### Community 54 - "Endpoint Schema Fields"
Cohesion: 0.22
Nodes (9): result_item, result_title, result_url, url_template, search, additionalProperties, description, required (+1 more)

### Community 55 - "apply_variant_rules"
Cohesion: 0.22
Nodes (9): Row, price_history(), Return one variant's past readings, newest first, capped at limit.      Empty fo, The trend panel reads row 0 as the latest reading, so order is the point.      A, No history yet is a normal state for a variant, not an error to raise on., The identity a real scan writes must be the identity these lookups accept., test_a_scanned_perfume_can_be_read_back_by_basket_and_history(), test_price_history_is_empty_for_an_unknown_variant() (+1 more)

### Community 56 - "Request Schema Fields"
Cohesion: 0.04
Nodes (45): jsdom, motion, @playwright/test, react, react-dom, @testing-library/jest-dom, @testing-library/react, @testing-library/user-event (+37 more)

### Community 57 - "_FixtureFetcher"
Cohesion: 0.14
Nodes (6): Changed, Close out a submit that named no perfume anyone could look for., Show what storage already knows, then go to the shops for the rest.          `fo, Say a perfume came off the record instead of off the shops.          Without thi, Empty the table for a new scan.          The columns are the same every time now, Submitted

### Community 58 - "setup_logging"
Cohesion: 0.07
Nodes (27): DOM, DOM.Iterable, e2e, ES2022, playwright.config.ts, src, tests, vite/client (+19 more)

### Community 59 - "_named_profile"
Cohesion: 0.12
Nodes (29): _close_browser(), _close_session_browser(), fetch(), _fetch_curl_cffi(), _fetch_httpx(), _fetch_playwright(), _folded(), _launch_browser() (+21 more)

### Community 60 - "_wait_for_table"
Cohesion: 0.31
Nodes (11): Path, Give the test profile's site id a hook file. The id is what binds them., test_a_before_search_that_returns_no_query_is_refused(), test_a_broken_hook_is_an_error_not_a_silent_empty(), test_a_hook_that_reads_nothing_is_named_as_the_culprit(), test_a_site_with_no_hook_file_is_driven_by_its_profile_alone(), test_after_search_can_drop_a_result_the_selectors_could_not(), test_before_search_rewrites_the_query_that_is_actually_sent() (+3 more)

### Community 61 - "._apply_scan_event"
Cohesion: 0.25
Nodes (8): exclude_keywords, max_size_ml, size_from, size_pattern, variant_rules, additionalProperties, required, type

### Community 62 - "snapshot_rows"
Cohesion: 0.09
Nodes (30): The search screen's second search must be answered with today's numbers.      Tw, A search that named no concentration is asking for all of them.      "" means "a, One call has to leave a row the search table can read straight off.      The cal, The old price has to survive, and it must not become a second variant.      Appe, first_seen is what says how long a shop has carried a size., The title and URL are information, not identity.      A shop that rewords a list, EDT and EDP are different products at different prices.      Folding them into o, A sold-out size often shows no price at all, and 0 would mean free.      Writing (+22 more)

### Community 64 - "validate_live"
Cohesion: 0.14
Nodes (9): Client, DownloadProgress, launch_installer(), _powershell_literal(), Path, İndirmeyi başlatır. Zaten çalışıyorsa None., state: idle | downloading | ready | installing | error., Uygulama kapanınca kurulum zincirinin de ölmemesi buna bağlı.      gui.py, playw (+1 more)

### Community 65 - "_named_profile"
Cohesion: 0.17
Nodes (15): CacheKey, CandidateFilter, _candidates_to_open(), Path, Narrow the search results down to the pages worth a request.      The first one, Run every site against one query, all at once, and report each separately., Run one matcher-aware spelling sequence for every site in parallel., run_sites() (+7 more)

### Community 67 - "extract_embedded_variants"
Cohesion: 0.33
Nodes (6): css, embedded_json, endpoint, jsonld, enum, extraction

### Community 68 - "JsonLdProduct"
Cohesion: 0.27
Nodes (11): check_enabled(), check_for_update(), _installer_asset(), _no_update(), Any, GitHub'daki son sürümü sorar, yenisini indirir ve kurulumu devreder.  Güncellene, ReleaseInfo, No network is not an error the user has to be told about.      The check runs un (+3 more)

### Community 72 - "write_snapshots"
Cohesion: 0.25
Nodes (8): Split one typed line into the perfumes it asks for, on " - ".      The separator, split_queries(), test_a_hyphen_inside_a_brand_name_does_not_split_the_search(), test_a_line_naming_three_perfumes_is_read_as_three_searches(), test_a_piece_that_names_no_perfume_survives_to_be_complained_about(), test_a_stray_separator_is_not_worth_failing_over(), test_one_perfume_is_still_one_search(), test_the_same_perfume_typed_twice_is_scanned_once()

### Community 74 - "ConfirmDialog.tsx"
Cohesion: 0.53
Nodes (4): FormData, Headers, Method, Strategy

### Community 75 - "ResultRow"
Cohesion: 0.06
Nodes (58): _as_str(), _balanced_value(), _build_offer(), _build_product(), _coerce_in_stock(), _collect_offers(), _collect_products(), _collect_variants() (+50 more)

### Community 76 - "SplitPlan"
Cohesion: 0.19
Nodes (8): AddButton(), Badge(), BadgeKind, BookmarkIcon(), BookmarkIconProps, variants, ConfirmDialog(), WishlistButton()

### Community 79 - "AddButton.tsx"
Cohesion: 0.29
Nodes (7): _fold_search_separators(), One search line, then the same line with the brand written the other ways., Turn punctuation that commonly splits catalog tokens into spaces., search_spellings(), test_a_brand_nobody_abbreviates_is_asked_for_once(), test_brand_aliases_each_receive_one_separator_folded_attempt_in_order(), test_the_typed_spelling_is_asked_first_and_the_rest_only_follow()

### Community 81 - "run_sites"
Cohesion: 0.07
Nodes (50): _Change, Pressed, ScanEvent, BasketRefreshEvent and viewmodel dataclasses as JSON-safe dicts.  Eve, One site's pacing state, for as long as whoever holds it says.      The gate and, SitePace, A multi-site price and stock comparison tool for perfume decants.  Includes a sh, File logging for the app's own diagnostics.  Nothing here ever writes to the con, display_title() (+42 more)

### Community 82 - "Node"
Cohesion: 0.12
Nodes (33): Match, match_title(), PerfumeQuery, The perfume being looked for, split into its three identity parts.      `concent, One site title judged against the query.      `concentration` is what the title, Judge one site title against a query, or None if it is not that perfume.      No, Map search results into persistence rows., Turn one site's hits into the rows persistence is ready to store.      Shared by (+25 more)

### Community 84 - "_wait_until"
Cohesion: 0.21
Nodes (15): probe(), Fetch `url` with every strategy and report diagnostics for each.      timeout_s, MonkeyPatch, Tests for parfum_finder.probe.  probe() always tries all three strategies -- the, test_probe_counts_jsonld_product_and_platform_signature(), test_probe_counts_product_across_jsonld_root_shapes(), test_probe_counts_product_markup_without_any_jsonld(), test_probe_counts_products_nested_below_the_top_level() (+7 more)

### Community 85 - "enum"
Cohesion: 0.50
Nodes (3): The template this site's profile would be based on, if any., Which of the matching templates gets applied, or None for none of them.      One, _resolve_platform()

### Community 86 - "BasketRow"
Cohesion: 0.18
Nodes (9): BaseHTTPRequestHandler, _Handler, _playwright_usable(), MonkeyPatch, Shared pytest fixtures.  A local HTTP server used by fetch/probe tests: real req, Whether the playwright rung can actually run here, binary included.      Checkin, Record every delay the engine asks for instead of serving it.      Waiting for r, server_url() (+1 more)

### Community 87 - "helpers.ts"
Cohesion: 0.49
Nodes (7): addFirstRow(), authToken(), clearBasket(), openApp(), search(), searchButton(), tab()

### Community 88 - "handoff_command"
Cohesion: 0.20
Nodes (7): App(), wishlistIdentity, wishlistKey(), root, Block, Verdicts, ResultRow

### Community 89 - "._write_to_sheet"
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: Review redirect classification, diagnostic suppression, and shared attempt cache and pacing, Source Nodes

### Community 90 - "._start_search"
Cohesion: 0.14
Nodes (6): RowSelected, format_age(), Turn a price age in days into the words the age column shows., ResultRow, Row, test_format_age_reads_as_words_not_a_timestamp()

### Community 92 - "_FakeStreamResponse"
Cohesion: 0.18
Nodes (4): _FakeClient, _FakeStreamResponse, Any, Exception

### Community 93 - "_scenario_block"
Cohesion: 0.07
Nodes (56): _read_basket(), basket_inputs(), BasketReport, build_basket_rows(), _ClimbState, compare_split_to_best_full(), _label(), BasketRow (+48 more)

### Community 94 - "Arayüz testleri"
Cohesion: 0.40
Nodes (4): Arayüz testleri, jsdom katmanı (`tests/`), Ne test edilmiyor, Tarayıcı katmanı (`e2e/`)

### Community 97 - "cached_prices"
Cohesion: 0.07
Nodes (33): _normalize_utc_timestamp(), Return one aware timestamp in the database's canonical UTC format., Write a whole scan at once and return how many prices were recorded.      Every, write_snapshots(), A model word must not become the brand in the database.      Different houses ca, The title prefix is the missing brand, not the model's first word., A price nobody will scan again may not be offered as a result.      Refreshing i, A shop's imitation must not be stored as the perfume it imitates.      The clone (+25 more)

### Community 98 - ".on_mount"
Cohesion: 0.14
Nodes (4): HeaderSelected, Any, The initial screen: search bar, streaming results table, notices, footer., SearchScreen

### Community 103 - "Static"
Cohesion: 0.40
Nodes (3): ComposeResult, ComposeResult, Static

## Knowledge Gaps
- **229 isolated node(s):** `parfum-finder`, `$schema`, `$id`, `title`, `description` (+224 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **6 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `SearchScreen` connect `.on_mount` to `TUI App & Screens`, `Search/Basket Domain Models`, `Static`, `.__init__`, `Fixture Fetcher (Tests)`, `run_sites`, `Node`, `Search TUI Screen`, `FetchResult`, `_FixtureFetcher`, `._start_search`?**
  _High betweenness centrality (0.027) - this node is a cross-community bridge._
- **Why does `BasketScreen` connect `run_sites` to `TUI App & Screens`, `Site Profiles & Templates`, `.on_mount`, `Static`, `TUI App Shell`, `Basket Optimizer Core`, `Fixture Fetcher (Tests)`, `_scenario_block`?**
  _High betweenness centrality (0.026) - this node is a cross-community bridge._
- **Why does `SiteRunner` connect `Fixture Fetcher (Tests)` to `_named_profile`, `.on_mount`, `Search/Basket Domain Models`, `.__init__`, `Search Engine Core`, `FieldConfidence`, `_ResultRow`, `_RecordingFetcher`, `run_sites`, `._refresh_table`, `FetchResult`, `_scenario_block`?**
  _High betweenness centrality (0.025) - this node is a cross-community bridge._
- **Are the 19 inferred relationships involving `PerfumeQuery` (e.g. with `BasketPriceExcluded` and `BasketRefreshFinished`) actually correct?**
  _`PerfumeQuery` has 19 INFERRED edges - model-reasoned connections that need verification._
- **Are the 14 inferred relationships involving `SearchScreen` (e.g. with `ParfumFinderApp` and `SiteRunner`) actually correct?**
  _`SearchScreen` has 14 INFERRED edges - model-reasoned connections that need verification._
- **What connects `parfum-finder`, `$schema`, `$id` to the rest of the system?**
  _229 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `TUI App & Screens` be split into smaller, more focused modules?**
  _Cohesion score 0.09337992622791691 - nodes in this community are weakly interconnected._