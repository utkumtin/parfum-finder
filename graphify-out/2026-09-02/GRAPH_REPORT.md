# Graph Report - parfum-finder  (2026-09-02)

## Corpus Check
- 142 files · ~320,690 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2699 nodes · 7421 edges · 99 communities (91 shown, 8 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 475 edges (avg confidence: 0.6)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `b39462a5`
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
- _fake_runner
- AddButton.tsx
- field_map
- run_sites
- Node
- test_one_query_finding_two_bottles_gets_two_blocks
- _wait_until
- enum
- BasketRow
- helpers.ts
- handoff_command
- ._write_to_sheet
- ._start_search
- Q: After correcting the free-delivery wishlist idea, what other genuinely useful, high-priority Windows app features could produce a 'brilliant that you thought of that' reaction?
- _FakeStreamResponse
- Arayüz testleri
- test_every_shipped_site_has_a_colour_that_survives_256_colours
- Q: In the Windows application, when I release a new version, I click the ‘Update’ button to install the update, and the new update is downloaded. However, the application then closes and the installer does not launch. By pressing Win + R and then running the downloaded installer from the ‘%temp%’ directory, I am able to install the update without any issues. So I assume there is no block from Windows. I’m still experiencing this issue even though I’ve added it to the whitelist via Windows Defender. Could you please check if there’s an error in the code?
- test_architecture.py

## God Nodes (most connected - your core abstractions)
1. `PerfumeQuery` - 76 edges
2. `search_site()` - 70 edges
3. `_profile()` - 69 edges
4. `SearchScreen` - 64 edges
5. `discover()` - 56 edges
6. `match_title()` - 56 edges
7. `connect()` - 55 edges
8. `FetchResult` - 52 edges
9. `Fetcher` - 52 edges
10. `parse_query()` - 51 edges

## Surprising Connections (you probably didn't know these)
- `Shipping Non-linearity Rationale (why cheapest-per-item is wrong)` --semantically_similar_to--> `sites/ Site Profile Directory`  [INFERRED] [semantically similar]
  ARCHITECTURE.md → sites/README.md
- `Variant Pattern B (dropdown + AJAX price)` --semantically_similar_to--> `Variant Selector Detector Fix (WooCommerce 'variation' vs 'variant')`  [INFERRED] [semantically similar]
  ARCHITECTURE.md → docs/discovery-report.md
- `_FakeClient` --uses--> `ReleaseInfo`  [INFERRED]
  tests/test_updater.py → src/parfum_finder/updater.py
- `_FakeStreamResponse` --uses--> `ReleaseInfo`  [INFERRED]
  tests/test_updater.py → src/parfum_finder/updater.py
- `_RecordingClient` --uses--> `DownloadProgress`  [INFERRED]
  tests/test_api.py → src/parfum_finder/updater.py

## Import Cycles
- 3-file cycle: `src/parfum_finder/__init__.py -> src/parfum_finder/cli.py -> src/parfum_finder/validate.py -> src/parfum_finder/__init__.py`
- 3-file cycle: `src/parfum_finder/__init__.py -> src/parfum_finder/cli.py -> src/parfum_finder/profiles.py -> src/parfum_finder/__init__.py`
- 3-file cycle: `src/parfum_finder/__init__.py -> src/parfum_finder/cli.py -> src/parfum_finder/logging_setup.py -> src/parfum_finder/__init__.py`
- 3-file cycle: `src/parfum_finder/__init__.py -> src/parfum_finder/cli.py -> src/parfum_finder/store.py -> src/parfum_finder/__init__.py`
- 4-file cycle: `src/parfum_finder/__init__.py -> src/parfum_finder/cli.py -> src/parfum_finder/validate.py -> src/parfum_finder/profiles.py -> src/parfum_finder/__init__.py`
- 4-file cycle: `src/parfum_finder/__init__.py -> src/parfum_finder/cli.py -> src/parfum_finder/engine.py -> src/parfum_finder/profiles.py -> src/parfum_finder/__init__.py`
- 4-file cycle: `src/parfum_finder/__init__.py -> src/parfum_finder/cli.py -> src/parfum_finder/discover.py -> src/parfum_finder/profiles.py -> src/parfum_finder/__init__.py`
- 4-file cycle: `src/parfum_finder/__init__.py -> src/parfum_finder/cli.py -> src/parfum_finder/discover.py -> src/parfum_finder/store.py -> src/parfum_finder/__init__.py`
- 4-file cycle: `src/parfum_finder/__init__.py -> src/parfum_finder/cli.py -> src/parfum_finder/services/snapshots.py -> src/parfum_finder/store.py -> src/parfum_finder/__init__.py`
- 5-file cycle: `src/parfum_finder/__init__.py -> src/parfum_finder/cli.py -> src/parfum_finder/validate.py -> src/parfum_finder/engine.py -> src/parfum_finder/profiles.py -> src/parfum_finder/__init__.py`

## Hyperedges (group relationships)
- **Sites Implementing Variant Pattern C (embedded JSON)** — docs_discovery_report_venco_site, docs_discovery_report_decantall_site, docs_discovery_report_luxurydekant_site, docs_discovery_report_ruxangroup_site, architecture_md_variant_pattern_c [EXTRACTED 1.00]
- **İdeasoft Platform Sites and Endpoint** — docs_discovery_report_dekantparfum_site, docs_discovery_report_dekantdoktoru_site, docs_discovery_report_ideasoft_related_options_endpoint, platforms_readme_ideasoft_json [EXTRACTED 1.00]
- **discover Command Output Artifacts (profile + fixtures + CI validation)** — architecture_md_discover_flow, sites_readme_sites_dir, fixtures_readme_fixtures_dir, github_workflows_ci_validate_profiles_step, architecture_md_validate_command [INFERRED 0.85]

## Communities (99 total, 8 thin omitted)

### Community 0 - "TUI App & Screens"
Cohesion: 0.09
Nodes (100): The Textual-based terminal UI: search and basket screens., _app(), _basket(), _cells(), _days_ago(), _leg(), _ok(), _open_basket() (+92 more)

### Community 1 - "Site Profiles & Templates"
Cohesion: 0.05
Nodes (83): _check_hook_kinds(), deep_merge(), _load_json(), load_platform_template(), load_platform_templates(), load_site_hooks(), load_site_profile(), Any (+75 more)

### Community 2 - "Title Matcher"
Cohesion: 0.29
Nodes (11): _normalized_product_name(), Recognize a single product page after a material same-origin redirect., _redirect_product_candidate(), _redirect_page(), test_material_redirect_cleans_tracking_and_rejects_cross_origin_metadata_url(), test_metadata_formats_agree_across_typographic_separators(), test_multiple_top_level_microdata_products_are_ambiguous(), test_nested_related_product_name_does_not_name_the_page_scope() (+3 more)

### Community 3 - "HTTP/Browser Fetching"
Cohesion: 0.12
Nodes (32): browser_session(), fetch(), Strategy, Fetch one URL using exactly the given strategy.      `method`/`data` exist for t, Yield a fetcher that keeps one browser for every playwright page it reads., _reject_playwright_post(), test_the_no_results_page_would_otherwise_read_as_suspect(), _fake_launch() (+24 more)

### Community 4 - "Search/Basket Domain Models"
Cohesion: 0.05
Nodes (148): Screen, ProductCandidate, Dependency-free models shared by search, persistence, and presentation., One decant size of one product, in the units the database stores.      Tenths of, A candidate together with the decant sizes its product page offers., What one site had to say about one query, and how much to trust it.      Four st, One hit on a search results page, before its product page is opened.      `raw_t, SearchHit (+140 more)

### Community 5 - "Search Engine per Site"
Cohesion: 0.11
Nodes (34): basket_inputs(), build_basket_rows(), _ClimbState, _label(), BasketRow, Basket scenario evaluation. A pure function, no network access, no sqlite.  Inpu, One site's share of a split basket: what to buy there and what it costs.      `s, The hill-climb's working assignment plus the running per-site figures.      `sub (+26 more)

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
Nodes (64): HTMLParser, _canonical_path(), canonical_url(), _check_variant_control(), _decode_unreserved(), _fetch_page(), _has_product_ancestor(), _headers() (+56 more)

### Community 10 - "Basket Optimizer Core"
Cohesion: 0.15
Nodes (36): Collection, BasketItem, optimize(), Prices, Score one site against the basket, or against a subset of it.      `item_ids` is, Score every enabled site against the whole basket and sort the results.      Sit, Search for the cheapest way to split the basket across several sites.      Retur, One line of the shopping list: a basket row, not a unit count.      `item_id` is (+28 more)

### Community 11 - "Basket Store & Pricing"
Cohesion: 0.19
Nodes (22): _enable_checks(), _factory(), _patch_get(), MonkeyPatch, Path, Tests for parfum_finder.updater: the version compare, the release read, and the, The .exe is what gets downloaded, whatever else is attached.      Releases carry, An error state is what turns the button back on with a reason.      Falling back (+14 more)

### Community 12 - "JSON-LD Product Extraction"
Cohesion: 0.09
Nodes (48): extract_embedded_variants(), extract_jsonld_products(), extract_jsonld_variants(), Read every JSON-LD Product declared on the page, in document order.      A block, Rung 1: read the page's JSON-LD as flat variant rows.      A product that declar, Rung 3: read the JSON blob the page carries but does not display.      Two shape, _fixture(), _one_product_html() (+40 more)

### Community 13 - "Basket TUI Screen"
Cohesion: 0.08
Nodes (47): Event, PyInstaller entry point for the packaged desktop app.  Kept outside src/parfum_f, _close_window_when_asked(), _hold_app_mutex(), _kill_children_with_app(), main(), _ping(), Path (+39 more)

### Community 14 - "Platform Schema"
Cohesion: 0.06
Nodes (31): any, defaults, fingerprint, additionalProperties, items, minItems, type, description (+23 more)

### Community 15 - "Product Extraction"
Cohesion: 0.08
Nodes (44): Fetcher, Protocol, Anything that can stand in for `fetch`.      Offline profile validation runs the, _age_of(), Check, _count_result_cards(), _first_result_url(), _LayerUnavailable (+36 more)

### Community 16 - "Schema Field Patterns"
Cohesion: 0.06
Nodes (33): format, pattern, type, pattern, type, default, type, pattern (+25 more)

### Community 17 - "Offline Profile Validation"
Cohesion: 0.08
Nodes (34): _check_empty_search(), ExtractionFailed, RuntimeError, Fail when a search yielded no rows off a page that plainly lists products., A page answered but gave up nothing, where something was expected.      This is, Run one query against one site and read every hit's sizes.      Everything site-, search_site(), _NoRootParser (+26 more)

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
Cohesion: 0.08
Nodes (41): add_basket_item(), basket_lines(), basket_prices(), Add a size of a perfume to the basket, and return the basket_item_id.      The p, Return every basket line, oldest add first.      Ordered by added_at with basket, Return the basket price matrix: one row per (line, site) that has a price., Connection, Adding the same perfume and size twice must accumulate, not clobber.      The ba (+33 more)

### Community 22 - "Basket Site Scenarios"
Cohesion: 0.19
Nodes (13): encode_basket_refresh_event(), encode_basket_report(), encode_basket_row(), encode_result_row(), encode_scan_event(), encode_site_scenario(), _encode_split_leg(), Any (+5 more)

### Community 23 - "Price/Size Normalization"
Cohesion: 0.22
Nodes (9): is_newer(), _pad(), parse_version(), v0.2.1 -> (0, 2, 1). Sayıya çevrilemeyen her şey None., Okunamayan bir sürüm asla "yeni" sayılmaz.      Yanlış tarafa düşmenin bedeli si, A tag nobody can order against must not open a dialog.      The two failure dire, test_an_unreadable_tag_never_counts_as_an_update(), test_is_newer() (+1 more)

### Community 24 - "JSON Schema Primitives"
Cohesion: 0.11
Nodes (25): integer, null, string, properties, type, type, type, type (+17 more)

### Community 25 - "SQLite Store"
Cohesion: 0.09
Nodes (27): conn(), Path, Tests for parfum_finder.store: the timestamp helper and the schema.  The one har, Nothing on record is the state before a first search, not an error.      The sea, A disabled site loses its basket column, but an enabled quiet one keeps one., NULL means the site has no free shipping tier at all, not a threshold of zero., An update aimed at a row that isn't there means the caller is out of sync., A snapshot pointing at a variant that doesn't exist has to be rejected.      SQL (+19 more)

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
Cohesion: 0.05
Nodes (55): Pattern, _brand_pattern(), _canonical(), _canonical_brands(), _covers(), display_title(), _ends_with(), _fold_search_separators() (+47 more)

### Community 32 - "Variant Extraction Fields"
Cohesion: 0.11
Nodes (18): attribute, in_stock, price, script, size_raw, type, properties, additionalProperties (+10 more)

### Community 33 - "_ResultRow"
Cohesion: 0.08
Nodes (64): Match, match_title(), parse_query(), PerfumeQuery, The perfume being looked for, split into its three identity parts.      `concent, One site title judged against the query.      `concentration` is what the title, Split one typed line, "Dior Sauvage EDP", into the three identity parts.      Th, Judge one site title against a query, or None if it is not that perfume.      No (+56 more)

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
Cohesion: 0.14
Nodes (21): _classify_single_separator(), format_ml(), _parse_number(), parse_price(), parse_size_ml(), Decimal, Number parsing and formatting for prices and volumes, plus text folding.  This i, Decide whether a lone separator marks a fraction or a thousands group.      Retu (+13 more)

### Community 38 - "TUI Confirm Dialog"
Cohesion: 0.08
Nodes (42): basket_sites(), cached_prices(), _calendar_months_before(), _downsample_price_snapshots(), _downsample_sql(), _initialize_database(), _normalize_utc_timestamp(), _perfume_id() (+34 more)

### Community 39 - "TUI App Shell"
Cohesion: 0.13
Nodes (23): encode_split_plan(), The split plan plus its verdict against the best full-coverage site.      Named, compare_split_to_best_full(), The cheapest basket split the search found. A heuristic, not a proof.      Every, Score a split plan against the cheapest full-coverage single site.      Only the, SplitPlan, format_price(), Format a price for display (comma-thousands, dot-decimal).      Decimal('1250') (+15 more)

### Community 40 - "Fetch Backends"
Cohesion: 0.14
Nodes (14): curl_cffi, httpx, playwright, result_item, result_title, result_url, strategy, url_template (+6 more)

### Community 41 - "HTTP Request Schema"
Cohesion: 0.14
Nodes (14): GET, POST, properties, default, enum, type, type, type (+6 more)

### Community 42 - "Fixture Fetcher (Tests)"
Cohesion: 0.11
Nodes (35): BaseModel, BasketLine, BasketPrice, BasketRow, BasketSite, FastAPI, AcceptedSearch, _add_basket_item() (+27 more)

### Community 43 - "FieldConfidence"
Cohesion: 0.14
Nodes (11): PlaywrightNoResponse, PlaywrightNotInstalled, RuntimeError, The "playwright" strategy was requested but cannot run at all.      Covers both, Navigation completed but playwright returned no Response object.      Its own ty, _FakeBrowser, _FakePage, Any (+3 more)

### Community 44 - "Decant Variant Rules"
Cohesion: 0.13
Nodes (25): api, ApiError, authToken(), readDetail(), request(), Window, Toast, View (+17 more)

### Community 45 - "_ResultRow"
Cohesion: 0.09
Nodes (64): SiteResult, create_app(), SiteRunner, TestClient, _auth(), _client(), db_path(), _ok_result() (+56 more)

### Community 46 - "Offline Validation Fixtures"
Cohesion: 0.25
Nodes (8): type, additionalProperties, type, body, request_headers, additionalProperties, description, type

### Community 47 - "JsonLdProduct"
Cohesion: 0.14
Nodes (24): refusalReason(), streamUrl(), useEventStream(), ProgressBar(), ScanStatus(), VerdictAddButton(), basketKey(), formatAge() (+16 more)

### Community 48 - "._build_rows"
Cohesion: 0.07
Nodes (51): _choose_strategy(), collect_prices(), DiscoveryReport, FieldConfidence, _flatten_defaults(), _format_choice(), _format_confidence(), _format_defaults() (+43 more)

### Community 49 - "_RecordingFetcher"
Cohesion: 0.11
Nodes (42): How long the shop asked to be left alone, or None if it did not say.      A refu, Run one site and classify what came back instead of raising.      It is also whe, _retry_after_s(), run_site(), FetchResult, One fetched page, uniform regardless of which strategy produced it., _counting_fetcher(), _profile() (+34 more)

### Community 50 - "Profile Age Checks"
Cohesion: 0.09
Nodes (47): _age_line(), format_live_report(), format_report(), Every check run against one site's profile, in the order they ran.      Checks s, Whether the profile is old enough to be worth re-discovering., Check one site's profile against that site's saved fixtures.      Never raises f, Validate every site, or just the ones named.      Serial rather than concurrent:, Render the validations as the offline half of the report in APP_FLOW §6.      A (+39 more)

### Community 51 - "._refresh_table"
Cohesion: 0.15
Nodes (26): apply_variant_rules(), Turn raw size rows into decant variants, dropping what is not a decant.      Thr, Try spelling variants until this site returns an emittable match.      The match, run_site_attempts(), _attempt_hit(), Tests for the profile-driven search in parfum_finder.engine.  What these defend, _row(), test_a_keyword_in_the_size_label_excludes_the_row_too() (+18 more)

### Community 52 - "FetchResult"
Cohesion: 0.22
Nodes (31): now_iso(), Return the current UTC time as 'YYYY-MM-DDTHH:MM:SSZ'.      Every timestamp writ, _basket_row(), _collect(), _ok_result(), _profile(), Any, MonkeyPatch (+23 more)

### Community 53 - "conftest.py"
Cohesion: 0.21
Nodes (13): _named_profile(), Any, The real fetcher, with a list of every URL it was asked for., A profile whose search page lists two houses' bottles, as shops do., test_a_broken_profile_is_still_suspect_when_no_title_looked_right(), test_a_listing_from_another_house_costs_no_product_request(), test_a_scan_says_how_many_listings_it_skipped(), test_diagnostic_candidate_checks_extraction_but_never_emits_a_hit() (+5 more)

### Community 54 - "Endpoint Schema Fields"
Cohesion: 0.22
Nodes (9): result_item, result_title, result_url, url_template, search, additionalProperties, description, required (+1 more)

### Community 55 - "apply_variant_rules"
Cohesion: 0.29
Nodes (7): price_history(), Row, Return one variant's past readings, newest first, capped at limit.      Empty fo, No history yet is a normal state for a variant, not an error to raise on., The identity a real scan writes must be the identity these lookups accept., test_a_scanned_perfume_can_be_read_back_by_basket_and_history(), test_price_history_is_empty_for_an_unknown_variant()

### Community 56 - "Request Schema Fields"
Cohesion: 0.04
Nodes (45): jsdom, motion, @playwright/test, react, react-dom, @testing-library/jest-dom, @testing-library/react, @testing-library/user-event (+37 more)

### Community 57 - "_FixtureFetcher"
Cohesion: 0.07
Nodes (16): Changed, HeaderSelected, RowSelected, format_age(), Turn a price age in days into the words the age column shows., The Textual App root. Handles screen navigation and is the app's default entry p, Path, ResultRow (+8 more)

### Community 58 - "setup_logging"
Cohesion: 0.07
Nodes (27): DOM, DOM.Iterable, e2e, ES2022, playwright.config.ts, src, tests, vite/client (+19 more)

### Community 59 - "_named_profile"
Cohesion: 0.19
Nodes (19): _close_browser(), _close_session_browser(), _fetch_curl_cffi(), _fetch_httpx(), _fetch_playwright(), _folded(), _launch_browser(), Any (+11 more)

### Community 60 - "_wait_for_table"
Cohesion: 0.31
Nodes (11): Path, Give the test profile's site id a hook file. The id is what binds them., test_a_before_search_that_returns_no_query_is_refused(), test_a_broken_hook_is_an_error_not_a_silent_empty(), test_a_hook_that_reads_nothing_is_named_as_the_culprit(), test_a_site_with_no_hook_file_is_driven_by_its_profile_alone(), test_after_search_can_drop_a_result_the_selectors_could_not(), test_before_search_rewrites_the_query_that_is_actually_sent() (+3 more)

### Community 61 - "._apply_scan_event"
Cohesion: 0.21
Nodes (16): RuntimeError, _close_handle(), _copy_bootstrapper(), _create_ready_event(), handoff_command(), _kernel32(), launch_installer(), Path (+8 more)

### Community 62 - "snapshot_rows"
Cohesion: 0.07
Nodes (47): A model word must not become the brand in the database.      Different houses ca, The trend panel reads row 0 as the latest reading, so order is the point.      A, The search screen's second search must be answered with today's numbers.      Tw, A search that named no concentration is asking for all of them.      "" means "a, A price nobody will scan again may not be offered as a result.      Refreshing i, The drop happens here so no caller can forget it.      Both the CLI and the scre, One call has to leave a row the search table can read straight off.      The cal, The old price has to survive, and it must not become a second variant.      Appe (+39 more)

### Community 64 - "validate_live"
Cohesion: 0.20
Nodes (4): Client, DownloadProgress, İndirmeyi başlatır. Zaten çalışıyorsa None., state: idle | downloading | ready | installing | error.

### Community 65 - "_named_profile"
Cohesion: 0.17
Nodes (15): CacheKey, CandidateFilter, _candidates_to_open(), Path, Narrow the search results down to the pages worth a request.      The first one, Run every site against one query, all at once, and report each separately., Run one matcher-aware spelling sequence for every site in parallel., run_sites() (+7 more)

### Community 67 - "extract_embedded_variants"
Cohesion: 0.10
Nodes (22): Any, Connection, Command-line entry point.  Subcommands will be added incrementally as the projec, Scan every perfume against every site and print each site as it lands.      One, Write one site's rows in a transaction of its own.      Per site rather than per, One line per site: which site, how it went, and what it said.      The site id i, _report_line(), _scan_all() (+14 more)

### Community 68 - "JsonLdProduct"
Cohesion: 0.19
Nodes (14): check_enabled(), check_for_update(), fetch_latest_release(), _installer_asset(), _no_update(), Any, En son yayımlanmış sürüm, ya da ulaşılamadıysa None.      /releases/latest tasla, ReleaseInfo (+6 more)

### Community 71 - ".__init__"
Cohesion: 0.25
Nodes (8): exclude_keywords, max_size_ml, size_from, size_pattern, variant_rules, additionalProperties, required, type

### Community 72 - "write_snapshots"
Cohesion: 0.38
Nodes (7): BasketReport, Every site's single-site scenario, split by whether it covers everything.      A, _full_scenario(), _plan(), SiteScenario, test_compare_split_to_best_full_reports_the_cheaper_side(), test_compare_split_to_best_full_with_no_full_coverage_site()

### Community 73 - "_css_variant"
Cohesion: 0.33
Nodes (6): css, embedded_json, endpoint, jsonld, enum, extraction

### Community 74 - "ConfirmDialog.tsx"
Cohesion: 0.53
Nodes (4): FormData, Headers, Method, Strategy

### Community 75 - "ResultRow"
Cohesion: 0.05
Nodes (68): _parse_endpoint_document(), Give a size the listing's title and URL when the page gave it none,     and make, Drive a platform's POST variant endpoint, one size option per request.      `bod, Parse one endpoint response and read its variant rows out of it., _read_endpoint_variants_post(), _with_candidate_identity(), _as_str(), _balanced_value() (+60 more)

### Community 76 - "SplitPlan"
Cohesion: 0.19
Nodes (8): AddButton(), Badge(), BadgeKind, BookmarkIcon(), BookmarkIconProps, variants, ConfirmDialog(), WishlistButton()

### Community 78 - "_fake_runner"
Cohesion: 0.28
Nodes (12): arguments_t, BOOL, DWORD, HINSTANCE, append_log(), argument_value(), launch_setup(), parse_arguments() (+4 more)

### Community 81 - "run_sites"
Cohesion: 0.08
Nodes (70): Lock, Pressed, ScanEvent, BasketRefreshEvent and viewmodel dataclasses as JSON-safe dicts.  Eve, BasketRefreshSession, In-memory session state for the two streamed operations: a search scan and a bas, ScanSession, Protocol, One site's pacing state, for as long as whoever holds it says.      The gate and (+62 more)

### Community 82 - "Node"
Cohesion: 0.41
Nodes (11): _bootstrapper(), _close_handle(), _command(), _kernel32(), Any, Path, Windows integration checks for the native update helper., _ready_event() (+3 more)

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
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: I’d like to have a brainstorming session with you now. I’m looking to come up with ideas for new features to add to the project’s Windows application. To this end, I’m looking forward to your suggestions. When adding features, I want them to be genuinely useful. I want to add features that will elicit feedback from users along the lines of, ‘It’s brilliant that you thought of that.’, Source Nodes

### Community 91 - "Q: After correcting the free-delivery wishlist idea, what other genuinely useful, high-priority Windows app features could produce a 'brilliant that you thought of that' reaction?"
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: After correcting the free-delivery wishlist idea, what other genuinely useful, high-priority Windows app features could produce a 'brilliant that you thought of that' reaction?, Source Nodes

### Community 92 - "_FakeStreamResponse"
Cohesion: 0.18
Nodes (4): Exception, _FakeClient, _FakeStreamResponse, Any

### Community 94 - "Arayüz testleri"
Cohesion: 0.40
Nodes (4): Arayüz testleri, jsdom katmanı (`tests/`), Ne test edilmiyor, Tarayıcı katmanı (`e2e/`)

### Community 95 - "test_every_shipped_site_has_a_colour_that_survives_256_colours"
Cohesion: 0.12
Nodes (9): _Change, BasketScreen, ComposeResult, Path, The basket: the list on top, one scenario per site underneath., _remove(), _set_qty(), ComposeResult (+1 more)

### Community 106 - "Q: In the Windows application, when I release a new version, I click the ‘Update’ button to install the update, and the new update is downloaded. However, the application then closes and the installer does not launch. By pressing Win + R and then running the downloaded installer from the ‘%temp%’ directory, I am able to install the update without any issues. So I assume there is no block from Windows. I’m still experiencing this issue even though I’ve added it to the whitelist via Windows Defender. Could you please check if there’s an error in the code?"
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: In the Windows application, when I release a new version, I click the ‘Update’ button to install the update, and the new update is downloaded. However, the application then closes and the installer does not launch. By pressing Win + R and then running the downloaded installer from the ‘%temp%’ directory, I am able to install the update without any issues. So I assume there is no block from Windows. I’m still experiencing this issue even though I’ve added it to the whitelist via Windows Defender. Could you please check if there’s an error in the code?, Source Nodes

## Knowledge Gaps
- **238 isolated node(s):** `Answer`, `Outcome`, `Source Nodes`, `parfum-finder`, `$schema` (+233 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **8 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Work-memory lessons

**Preferred sources** — corroborated by past sessions; start here.
- `price_history()` (2× useful, score=1.928174482)
- `BasketScreen()` (2× useful, score=1.928174482)

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `PerfumeQuery` connect `_ResultRow` to `extract_embedded_variants`, `Search/Basket Domain Models`, `run_sites`, `Offline Profile Validation`, `Search TUI Screen`, `._refresh_table`, `FetchResult`, `_FixtureFetcher`, `Live Profile Validation`?**
  _High betweenness centrality (0.018) - this node is a cross-community bridge._
- **Why does `UpdateDownload` connect `Fixture Fetcher (Tests)` to `validate_live`, `Basket Store & Pricing`, `_ResultRow`, `_FakeStreamResponse`, `._apply_scan_event`?**
  _High betweenness centrality (0.018) - this node is a cross-community bridge._
- **Why does `BasketScreen` connect `test_every_shipped_site_has_a_colour_that_survives_256_colours` to `TUI App & Screens`, `Site Profiles & Templates`, `Search Engine per Site`, `_trial`, `TUI App Shell`, `write_snapshots`, `Basket Optimizer Core`, `run_sites`, `_FixtureFetcher`?**
  _High betweenness centrality (0.017) - this node is a cross-community bridge._
- **Are the 19 inferred relationships involving `PerfumeQuery` (e.g. with `BasketPriceExcluded` and `BasketRefreshFinished`) actually correct?**
  _`PerfumeQuery` has 19 INFERRED edges - model-reasoned connections that need verification._
- **Are the 14 inferred relationships involving `SearchScreen` (e.g. with `ParfumFinderApp` and `SiteRunner`) actually correct?**
  _`SearchScreen` has 14 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Answer`, `Outcome`, `Source Nodes` to the rest of the system?**
  _238 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `TUI App & Screens` be split into smaller, more focused modules?**
  _Cohesion score 0.09337992622791691 - nodes in this community are weakly interconnected._