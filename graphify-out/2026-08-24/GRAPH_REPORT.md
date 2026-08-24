# Graph Report - parfum-finder  (2026-08-24)

## Corpus Check
- 134 files · ~317,462 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2630 nodes · 7068 edges · 121 communities (101 shown, 20 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 466 edges (avg confidence: 0.54)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `cf4895ce`
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
- Headers
- Method
- Strategy

## God Nodes (most connected - your core abstractions)
1. `PerfumeQuery` - 81 edges
2. `_profile()` - 69 edges
3. `SearchScreen` - 61 edges
4. `SiteResult` - 58 edges
5. `match_title()` - 55 edges
6. `discover()` - 54 edges
7. `Fetcher` - 53 edges
8. `parse_query()` - 52 edges
9. `_write_profile()` - 51 edges
10. `_app()` - 49 edges

## Surprising Connections (you probably didn't know these)
- `Shipping Non-linearity Rationale (why cheapest-per-item is wrong)` --semantically_similar_to--> `sites/ Site Profile Directory`  [INFERRED] [semantically similar]
  ARCHITECTURE.md → sites/README.md
- `Variant Pattern B (dropdown + AJAX price)` --semantically_similar_to--> `Variant Selector Detector Fix (WooCommerce 'variation' vs 'variant')`  [INFERRED] [semantically similar]
  ARCHITECTURE.md → docs/discovery-report.md
- `_NoRootParser` --uses--> `PerfumeQuery`  [INFERRED]
  tests/test_engine.py → src/parfum_finder/matcher.py
- `test_attempts_continue_past_safe_alternative_until_requested_match()` --calls--> `PerfumeQuery`  [EXTRACTED]
  tests/test_engine.py → src/parfum_finder/matcher.py
- `test_attempts_stop_immediately_for_a_suspect_result()` --calls--> `PerfumeQuery`  [EXTRACTED]
  tests/test_engine.py → src/parfum_finder/matcher.py

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

## Communities (121 total, 20 thin omitted)

### Community 0 - "TUI App & Screens"
Cohesion: 0.09
Nodes (100): The Textual-based terminal UI: search and basket screens., _app(), _basket(), _cells(), _days_ago(), _leg(), _ok(), _open_basket() (+92 more)

### Community 1 - "Site Profiles & Templates"
Cohesion: 0.06
Nodes (81): _check_hook_kinds(), deep_merge(), _load_json(), load_platform_template(), load_platform_templates(), load_site_hooks(), load_site_profile(), Any (+73 more)

### Community 2 - "Title Matcher"
Cohesion: 0.06
Nodes (54): _attempt_hit(), _profile(), Tests for the profile-driven search in parfum_finder.engine.  What these defend, A minimal working profile, with the fields a case cares about swapped in., test_a_cached_page_is_still_checked_against_its_size_picker(), test_a_dead_link_selector_is_suspect_not_empty(), test_a_dead_row_selector_on_a_full_page_is_suspect(), test_a_dead_site_does_not_take_the_others_down() (+46 more)

### Community 3 - "HTTP/Browser Fetching"
Cohesion: 0.12
Nodes (33): browser_session(), fetch(), Strategy, Fetch one URL using exactly the given strategy.      `method`/`data` exist for t, Yield a fetcher that keeps one browser for every playwright page it reads., _playwright_usable(), Whether the playwright rung can actually run here, binary included.      Checkin, _fake_launch() (+25 more)

### Community 4 - "Search/Basket Domain Models"
Cohesion: 0.08
Nodes (113): LogCaptureFixture, ParfumFinderApp, Runner, SearchHit, SiteResult, _app(), _basket_count(), _counting_runner() (+105 more)

### Community 5 - "Search Engine per Site"
Cohesion: 0.27
Nodes (11): fetch_latest_release(), En son yayımlanmış sürüm, ya da ulaşılamadıysa None.      /releases/latest tasla, _enable_checks(), _patch_get(), MonkeyPatch, The .exe is what gets downloaded, whatever else is attached.      Releases carry, _release_payload(), test_check_is_off_outside_a_frozen_build() (+3 more)

### Community 6 - "Platform Discovery Flow"
Cohesion: 0.15
Nodes (59): PlatformChooser, _ask_chooser(), discover(), Put the question only when there is one, and hold the answer to it.      An answ, Measure the strategies a site needs, then read its JSON-LD with the winner., _attempt(), _fake_probe(), Any (+51 more)

### Community 7 - "CLI Entry Points"
Cohesion: 0.10
Nodes (48): BaseHTTPRequestHandler, CaptureFixture, ask_which_platform(), main(), Path, Scan every site for the perfumes named, store what came back, print it.      One, Ask at the terminal which of several matching templates to apply.      Asked whi, run_search() (+40 more)

### Community 8 - "Architecture Rationale Docs"
Cohesion: 0.05
Nodes (53): basket Subset Enumeration + Local Improvement Algorithm, basket Optimizer (optimize function), Clone/Original Distinction (KLON ← <orijinal>), discover Discovery Flow, engine Concurrency Model (parallel sites, serial within site), Extraction Ladder (jsonld/endpoint/embedded/css), Fail-loud / status=suspect policy, hooks/<id>.py Escape Hatch (+45 more)

### Community 9 - "Search Engine Core"
Cohesion: 0.07
Nodes (47): apply_variant_rules(), _canonical_path(), canonical_url(), _check_variant_control(), _decode_unreserved(), _has_product_ancestor(), _headers(), _is_excluded() (+39 more)

### Community 10 - "Basket Optimizer Core"
Cohesion: 0.10
Nodes (50): Collection, basket_inputs(), BasketItem, build_basket_rows(), optimize(), BasketRow, Prices, Score one site against the basket, or against a subset of it.      `item_ids` is (+42 more)

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
Cohesion: 0.06
Nodes (54): ExtractionFailed, RuntimeError, A page answered but gave up nothing, where something was expected.      This is, The Textual App root. Handles screen navigation and is the app's default entry p, _age_line(), _age_of(), Check, _count_result_cards() (+46 more)

### Community 16 - "Schema Field Patterns"
Cohesion: 0.06
Nodes (33): format, pattern, type, pattern, type, default, type, pattern (+25 more)

### Community 17 - "Offline Profile Validation"
Cohesion: 0.21
Nodes (12): Fetcher, _named_profile(), Any, The real fetcher, with a list of every URL it was asked for., A profile whose search page lists two houses' bottles, as shops do., test_a_broken_profile_is_still_suspect_when_no_title_looked_right(), test_diagnostic_candidate_checks_extraction_but_never_emits_a_hit(), test_one_product_listed_under_two_searches_is_read_once() (+4 more)

### Community 18 - "Playwright Errors"
Cohesion: 0.14
Nodes (22): HTMLParser, _attempt(), _count_jsonld(), _count_product_objects(), _detect_platforms(), format_report(), _label_platform(), _one_line() (+14 more)

### Community 19 - "Search TUI Screen"
Cohesion: 0.07
Nodes (43): Match, One site title judged against the query.      `concentration` is what the title, find_header_columns(), find_match(), open_worksheet(), Any, Exception, Path (+35 more)

### Community 20 - "Snapshot Writing"
Cohesion: 0.18
Nodes (21): grouped_value(), Decimal, ResultRow, What each site charges for the product a block is about.      One entry per site, The default order: typed order, product, site, size.      The typed order comes, The order once a column has been picked: the site layer drops out.      Asking f, site_ranks(), sorted_value() (+13 more)

### Community 21 - "Candidate Filtering"
Cohesion: 0.10
Nodes (22): add_basket_item(), basket_prices(), Add a size of a perfume to the basket, and return the basket_item_id.      The p, Return the basket price matrix: one row per (line, site) that has a price., The basket screen prints brand/name/concentration straight off this row.      Or, Two lines added within the same second must still read back the same way twice., A basket line nobody sells must still be visible via basket_lines.      basket_p, A stale reading must never outrank the one taken after it.      latest_prices al (+14 more)

### Community 22 - "Basket Site Scenarios"
Cohesion: 0.15
Nodes (6): Changed, Close out a submit that named no perfume anyone could look for., Show what storage already knows, then go to the shops for the rest.          `fo, Say a perfume came off the record instead of off the shops.          Without thi, Empty the table for a new scan.          The columns are the same every time now, Submitted

### Community 23 - "Price/Size Normalization"
Cohesion: 0.18
Nodes (18): Exception, _counting_fetcher(), FetchResult, Answer each call with the next canned result, then repeat the last one., test_a_missing_browser_is_reported_at_once_not_retried(), test_a_page_that_is_simply_missing_is_not_asked_for_again(), test_a_pause_named_as_a_date_is_read_the_same_way(), test_a_profile_asking_for_no_pacing_gets_none_jitter_included() (+10 more)

### Community 24 - "JSON Schema Primitives"
Cohesion: 0.11
Nodes (25): integer, null, string, properties, type, type, type, type (+17 more)

### Community 25 - "SQLite Store"
Cohesion: 0.08
Nodes (37): BasketReport, compare_split_to_best_full(), _label(), Basket scenario evaluation. A pure function, no network access, no sqlite.  Inpu, Every site's single-site scenario, split by whether it covers everything.      A, One site's share of a split basket: what to buy there and what it costs.      `s, The cheapest basket split the search found. A heuristic, not a proof.      Every, Name one basket line the way a missing-item warning has to read it. (+29 more)

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
Cohesion: 0.11
Nodes (20): BasketResponse, basket(), basketRow(), resultRow(), scenario(), splitCombination(), compile(), DEFAULT_CONFIG (+12 more)

### Community 31 - "Live Profile Validation"
Cohesion: 0.09
Nodes (36): Pattern, _brand_pattern(), _canonical(), _canonical_brands(), _covers(), display_title(), _ends_with(), _index_of() (+28 more)

### Community 32 - "Variant Extraction Fields"
Cohesion: 0.11
Nodes (18): attribute, in_stock, price, script, size_raw, type, properties, additionalProperties (+10 more)

### Community 33 - "_ResultRow"
Cohesion: 0.08
Nodes (63): match_title(), parse_query(), PerfumeQuery, The perfume being looked for, split into its three identity parts.      `concent, Split one typed line, "Dior Sauvage EDP", into the three identity parts.      Th, Judge one site title against a query, or None if it is not that perfume.      No, Whether a search result's own listing text is worth opening the page for.      J, title_could_match() (+55 more)

### Community 34 - "Fetch Strategy Probing"
Cohesion: 0.26
Nodes (7): _FixtureFetcher, FormData, Headers, Method, Strategy, Serves one site's saved capture in place of the network.      Only three kinds o, The one real result card that led to the captured product page.          Cut out

### Community 35 - "Platform Field Mapping"
Cohesion: 0.12
Nodes (16): field_map, product_json, source, variants_path, additionalProperties, allOf, description, required (+8 more)

### Community 36 - "Shipping Config Schema"
Cohesion: 0.14
Nodes (14): free_shipping_threshold_kurus, shipping_cost_kurus, minimum, type, free_shipping_threshold_kurus, notes, shipping, shipping_cost_kurus (+6 more)

### Community 37 - "_trial"
Cohesion: 0.13
Nodes (22): casefold_tr(), _classify_single_separator(), format_age(), _parse_number(), parse_price(), parse_size_ml(), Decimal, Number parsing and formatting for prices and volumes, plus text folding.  This i (+14 more)

### Community 38 - "TUI Confirm Dialog"
Cohesion: 0.10
Nodes (33): One decant size of one product, in the units the database stores.      Tenths of, Variant, basket_lines(), _perfume_id(), _product_id(), Connection, datetime, SQLite persistence: an append-only price history.  Tables: sites, perfumes, prod (+25 more)

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
Cohesion: 0.09
Nodes (63): BaseModel, FastAPI, SplitPlan, AcceptedSearch, _add_basket_item(), _AppState, BasketAddRequest, BasketQtyRequest (+55 more)

### Community 43 - "FieldConfidence"
Cohesion: 0.15
Nodes (10): PlaywrightNoResponse, PlaywrightNotInstalled, RuntimeError, The "playwright" strategy was requested but cannot run at all.      Covers both, Navigation completed but playwright returned no Response object.      Its own ty, _FakeBrowser, _FakePage, Any (+2 more)

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
Cohesion: 0.08
Nodes (46): _choose_strategy(), collect_prices(), DiscoveryReport, FieldConfidence, _flatten_defaults(), _format_choice(), _format_confidence(), _format_defaults() (+38 more)

### Community 49 - "_RecordingFetcher"
Cohesion: 0.13
Nodes (22): conn(), Path, Tests for parfum_finder.store: the timestamp helper and the schema.  The one har, Insert one site → perfume → product → variant chain, return the variant id., Two snapshots written in the same second must resolve to the newer one.      A s, 5 ml at 125,00 TL is 25,00 TL per ml. Stored as kurus, ml as tenths., No price yet means no row, so the basket LEFT JOIN reads it as missing., A zero ml variant is a parse failure, and it must not reach the table.      If i (+14 more)

### Community 50 - "Profile Age Checks"
Cohesion: 0.09
Nodes (38): FormData, Headers, Method, Strategy, _corrupted_sites_dir(), _DeadSite, _FakeSite, _fixture_site() (+30 more)

### Community 51 - "._refresh_table"
Cohesion: 0.09
Nodes (20): RawVariant, _redirect_page(), _row(), test_a_keyword_in_the_size_label_excludes_the_row_too(), test_a_literal_zero_price_reads_as_no_price_not_a_free_perfume(), test_a_size_at_the_threshold_is_a_bottle_whatever_it_calls_itself(), test_a_size_that_cannot_be_read_is_dropped(), test_an_uppercase_turkish_keyword_still_matches() (+12 more)

### Community 52 - "FetchResult"
Cohesion: 0.13
Nodes (48): Lock, _record_search(), _sync_profiles(), Connection, Mirror site profiles into the sites table and return how many were written., sync_to_db(), Any, BasketRow (+40 more)

### Community 53 - "conftest.py"
Cohesion: 0.21
Nodes (12): api, authToken(), readDetail(), request(), Window, refusalReason(), streamUrl(), useEventStream() (+4 more)

### Community 54 - "Endpoint Schema Fields"
Cohesion: 0.22
Nodes (9): result_item, result_title, result_url, url_template, search, additionalProperties, description, required (+1 more)

### Community 55 - "apply_variant_rules"
Cohesion: 0.27
Nodes (12): Path, Give the test profile's site id a hook file. The id is what binds them., test_a_before_search_that_returns_no_query_is_refused(), test_a_broken_hook_is_an_error_not_a_silent_empty(), test_a_hook_that_reads_nothing_is_named_as_the_culprit(), test_a_site_with_no_hook_file_is_driven_by_its_profile_alone(), test_after_search_can_drop_a_result_the_selectors_could_not(), test_attempts_share_cache_pacer_and_hooks_directory() (+4 more)

### Community 56 - "Request Schema Fields"
Cohesion: 0.04
Nodes (45): jsdom, motion, @playwright/test, react, react-dom, @testing-library/jest-dom, @testing-library/react, @testing-library/user-event (+37 more)

### Community 57 - "_FixtureFetcher"
Cohesion: 0.15
Nodes (7): _Change, BasketScreen, BasketRow, Path, The basket: the list on top, one scenario per site underneath., _remove(), _set_qty()

### Community 58 - "setup_logging"
Cohesion: 0.07
Nodes (27): DOM, DOM.Iterable, e2e, ES2022, playwright.config.ts, src, tests, vite/client (+19 more)

### Community 59 - "_named_profile"
Cohesion: 0.18
Nodes (20): _close_browser(), _close_session_browser(), _fetch_curl_cffi(), _fetch_httpx(), _fetch_playwright(), _folded(), _launch_browser(), Any (+12 more)

### Community 60 - "_wait_for_table"
Cohesion: 0.15
Nodes (16): A candidate together with the decant sizes its product page offers., SearchHit, A shop's imitation must not be stored as the perfume it imitates.      The clone, Layton' finding 'Layton Exclusif' must not price the two as one bottle.      A s, The title prefix is the missing brand, not the model's first word., test_snapshot_rows_files_a_low_score_match_under_its_own_name(), test_snapshot_rows_marks_a_clone_instead_of_filing_it_as_the_original(), test_snapshot_rows_recovers_a_multiword_model_search_brand() (+8 more)

### Community 61 - "._apply_scan_event"
Cohesion: 0.15
Nodes (13): Connection, A disabled site loses its basket column, but an enabled quiet one keeps one., NULL means the site has no free shipping tier at all, not a threshold of zero., An update aimed at a row that isn't there means the caller is out of sync., The recents list has five slots, so a repeat must not consume two.      Someone, A snapshot pointing at a variant that doesn't exist has to be rejected.      SQL, test_basket_sites_omits_a_disabled_site_and_keeps_one_that_prices_nothing(), test_basket_sites_preserves_a_null_free_shipping_threshold_as_none() (+5 more)

### Community 62 - "snapshot_rows"
Cohesion: 0.14
Nodes (20): One call has to leave a row the search table can read straight off.      The cal, The old price has to survive, and it must not become a second variant.      Appe, first_seen is what says how long a shop has carried a size., The title and URL are information, not identity.      A shop that rewords a list, EDT and EDP are different products at different prices.      Folding them into o, A sold-out size often shows no price at all, and 0 would mean free.      Writing, The column is 0/1, so the tri-state has to land somewhere on purpose.      Unkno, raw_title is the audit trail for a wrong match, so it cannot be blank.      A ro (+12 more)

### Community 64 - "validate_live"
Cohesion: 0.14
Nodes (9): Client, DownloadProgress, launch_installer(), _powershell_literal(), Path, İndirmeyi başlatır. Zaten çalışıyorsa None., state: idle | downloading | ready | installing | error., Uygulama kapanınca kurulum zincirinin de ölmemesi buna bağlı.      gui.py, playw (+1 more)

### Community 65 - "_named_profile"
Cohesion: 0.15
Nodes (27): CacheKey, CandidateFilter, _candidates_to_open(), _check_empty_search(), _paced_fetcher(), Any, Path, Run one matcher-aware spelling sequence for every site in parallel. (+19 more)

### Community 67 - "extract_embedded_variants"
Cohesion: 0.21
Nodes (15): probe(), Fetch `url` with every strategy and report diagnostics for each.      timeout_s, MonkeyPatch, Tests for parfum_finder.probe.  probe() always tries all three strategies -- the, test_probe_counts_jsonld_product_and_platform_signature(), test_probe_counts_product_across_jsonld_root_shapes(), test_probe_counts_product_markup_without_any_jsonld(), test_probe_counts_products_nested_below_the_top_level() (+7 more)

### Community 68 - "JsonLdProduct"
Cohesion: 0.27
Nodes (11): check_enabled(), check_for_update(), _installer_asset(), _no_update(), Any, GitHub'daki son sürümü sorar, yenisini indirir ve kurulumu devreder.  Güncellene, ReleaseInfo, No network is not an error the user has to be told about.      The check runs un (+3 more)

### Community 71 - "exclude_keywords"
Cohesion: 0.09
Nodes (28): Any, Connection, Command-line entry point.  Subcommands will be added incrementally as the projec, Scan every perfume against every site and print each site as it lands.      One, Write one site's rows in a transaction of its own.      Per site rather than per, One line per site: which site, how it went, and what it said.      The site id i, _report_line(), _scan_all() (+20 more)

### Community 72 - "write_snapshots"
Cohesion: 0.25
Nodes (8): Split one typed line into the perfumes it asks for, on " - ".      The separator, split_queries(), test_a_hyphen_inside_a_brand_name_does_not_split_the_search(), test_a_line_naming_three_perfumes_is_read_as_three_searches(), test_a_piece_that_names_no_perfume_survives_to_be_complained_about(), test_a_stray_separator_is_not_worth_failing_over(), test_one_perfume_is_still_one_search(), test_the_same_perfume_typed_twice_is_scanned_once()

### Community 73 - "_css_variant"
Cohesion: 0.18
Nodes (11): product_label(), Reduce a site's own title to the product it is about, spelled one way.      What, test_a_clone_is_labelled_by_the_bottle_it_is_and_not_what_it_imitates(), test_a_longer_named_bottle_does_not_join_the_shorter_ones_block(), test_a_title_with_no_product_words_left_has_no_label(), test_catalog_decorations_do_not_split_product_groups(), test_every_shops_spelling_of_one_bottle_lands_in_one_block(), test_one_bottle_spelled_two_ways_lands_in_one_block() (+3 more)

### Community 74 - "ConfirmDialog.tsx"
Cohesion: 0.29
Nodes (7): price_history(), Row, Return one variant's past readings, newest first, capped at limit.      Empty fo, The trend panel reads row 0 as the latest reading, so order is the point.      A, No history yet is a normal state for a variant, not an error to raise on., test_price_history_is_empty_for_an_unknown_variant(), test_price_history_is_newest_first_and_capped_at_limit()

### Community 75 - "ResultRow"
Cohesion: 0.13
Nodes (25): _build_offer(), _coerce_in_stock(), _collect_offers(), _css_variant(), JsonLdOffer, _parse_availability(), _parse_price_value(), _parse_selector() (+17 more)

### Community 76 - "SplitPlan"
Cohesion: 0.38
Nodes (4): BookmarkIcon(), BookmarkIconProps, variants, WishlistButton()

### Community 77 - "_collect_products"
Cohesion: 0.25
Nodes (8): exclude_keywords, max_size_ml, size_from, size_pattern, variant_rules, additionalProperties, required, type

### Community 79 - "AddButton.tsx"
Cohesion: 0.29
Nodes (7): _fold_search_separators(), One search line, then the same line with the brand written the other ways., Turn punctuation that commonly splits catalog tokens into spaces., search_spellings(), test_a_brand_nobody_abbreviates_is_asked_for_once(), test_brand_aliases_each_receive_one_separator_folded_attempt_in_order(), test_the_typed_spelling_is_asked_first_and_the_rest_only_follow()

### Community 80 - "_write_hook"
Cohesion: 0.38
Nodes (7): _match_platforms(), Any, Path, Every template with at least one of its markers somewhere in the page.      Case, Write one page and return where it landed plus its digest.      Saved as UTF-8 w, _save_fixture(), _trial()

### Community 81 - "run_sites"
Cohesion: 0.09
Nodes (58): Pressed, ScanEvent, BasketRefreshEvent and viewmodel dataclasses as JSON-safe dicts.  Eve, In-memory session state for the two streamed operations: a search scan and a bas, Protocol, What one site had to say about one query, and how much to trust it.      Four st, One site's pacing state, for as long as whoever holds it says.      The gate and, What a caller needs of run_site, as a type callers can stand a fake in for., SitePace (+50 more)

### Community 82 - "test_connect_is_idempotent_on_an_existing_database"
Cohesion: 0.33
Nodes (6): _NoRootParser, MonkeyPatch, Stands in for HTMLParser when a page's markup cannot be read at all.      select, test_a_product_page_with_no_root_names_its_body_size(), test_a_search_page_with_no_root_names_its_body_size(), test_jitter_is_added_to_a_wait_and_never_taken_off_it()

### Community 83 - "DownloadProgress"
Cohesion: 0.16
Nodes (25): Node, SiteHooks, _fetch_page(), _microdata_scope_values(), _microdata_value(), ProductCandidate, Parse a page once, or say there is no page to parse.      Both ways of having no, Fetch one page with the strategy, headers and timeout the profile asks for. (+17 more)

### Community 84 - "_wait_until"
Cohesion: 0.10
Nodes (25): _balanced_value(), _embedded_documents(), extract_css_variants(), extract_endpoint_variants(), _flatten_jsonld(), _loads_or_skip(), _map_variant(), Any (+17 more)

### Community 85 - "enum"
Cohesion: 0.50
Nodes (3): The template this site's profile would be based on, if any., Which of the matching templates gets applied, or None for none of them.      One, _resolve_platform()

### Community 86 - "._write_to_sheet"
Cohesion: 0.25
Nodes (5): Screen, ParfumFinderApp, Path, Root app: pushes the search screen on mount., SystemCommand

### Community 87 - "helpers.ts"
Cohesion: 0.49
Nodes (7): addFirstRow(), authToken(), clearBasket(), openApp(), search(), searchButton(), tab()

### Community 88 - "handoff_command"
Cohesion: 0.12
Nodes (18): Block, Notice, pickVerdicts(), ResultsScreen(), SORT_LABELS, toBlocks(), TRIAL_SIZES_ML_X10, Verdicts (+10 more)

### Community 89 - "._write_to_sheet"
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: Review redirect classification, diagnostic suppression, and shared attempt cache and pacing, Source Nodes

### Community 90 - "._start_search"
Cohesion: 0.18
Nodes (3): RowSelected, ResultRow, Row

### Community 92 - "_FakeStreamResponse"
Cohesion: 0.18
Nodes (4): _FakeClient, _FakeStreamResponse, Any, Exception

### Community 94 - "Arayüz testleri"
Cohesion: 0.40
Nodes (4): Arayüz testleri, jsdom katmanı (`tests/`), Ne test edilmiyor, Tarayıcı katmanı (`e2e/`)

### Community 95 - "_seed_site"
Cohesion: 0.15
Nodes (17): Write a whole scan at once and return how many prices were recorded.      Every, write_snapshots(), The identity a real scan writes must be the identity these lookups accept., The drop happens here so no caller can forget it.      Both the CLI and the scre, A slow site must not spread one reading across several timestamps.      Rows wri, The number reported is what landed in the history, not what was offered., Half a site's sizes updated is worse than none of them.      The basket compares, A shop that just writes the same bottle differently must not fork it.      Filin (+9 more)

### Community 96 - "_redirect_product_candidate"
Cohesion: 0.33
Nodes (6): css, embedded_json, endpoint, jsonld, enum, extraction

### Community 97 - "cached_prices"
Cohesion: 0.20
Nodes (10): cached_prices(), Return the latest stored price of every size of this perfume, per site.      Bra, A search that named no concentration is asking for all of them.      "" means "a, A price nobody will scan again may not be offered as a result.      Refreshing i, Nothing on record is the state before a first search, not an error.      The sea, The search screen's second search must be answered with today's numbers.      Tw, test_cached_prices_is_empty_for_a_perfume_nobody_scanned(), test_cached_prices_leaves_out_a_disabled_site() (+2 more)

### Community 98 - ".on_mount"
Cohesion: 0.17
Nodes (3): Any, The initial screen: search bar, streaming results table, notices, footer., SearchScreen

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
- **20 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `PerfumeQuery` connect `_ResultRow` to `.on_mount`, `Title Matcher`, `TUI Confirm Dialog`, `exclude_keywords`, `Fixture Fetcher (Tests)`, `run_sites`, `test_connect_is_idempotent_on_an_existing_database`, `Search TUI Screen`, `FetchResult`, `apply_variant_rules`, `._start_search`, `Live Profile Validation`?**
  _High betweenness centrality (0.039) - this node is a cross-community bridge._
- **Why does `SearchScreen` connect `.on_mount` to `TUI App & Screens`, `_ResultRow`, `TUI Confirm Dialog`, `Static`, `._load_profiles`, `Fixture Fetcher (Tests)`, `.action_sort`, `.__init__`, `Product Extraction`, `run_sites`, `._write_to_sheet`, `Basket Site Scenarios`, `._start_search`?**
  _High betweenness centrality (0.034) - this node is a cross-community bridge._
- **Why does `match_title()` connect `_ResultRow` to `_named_profile`, `TUI Confirm Dialog`, `exclude_keywords`, `Search Engine Core`, `Search TUI Screen`, `Live Profile Validation`?**
  _High betweenness centrality (0.023) - this node is a cross-community bridge._
- **Are the 24 inferred relationships involving `PerfumeQuery` (e.g. with `BasketPriceExcluded` and `BasketRefreshFinished`) actually correct?**
  _`PerfumeQuery` has 24 INFERRED edges - model-reasoned connections that need verification._
- **Are the 11 inferred relationships involving `SearchScreen` (e.g. with `ParfumFinderApp` and `SiteRunner`) actually correct?**
  _`SearchScreen` has 11 INFERRED edges - model-reasoned connections that need verification._
- **Are the 23 inferred relationships involving `SiteResult` (e.g. with `Fetcher` and `FetchResult`) actually correct?**
  _`SiteResult` has 23 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Answer`, `Outcome`, `Source Nodes` to the rest of the system?**
  _229 weakly-connected nodes found - possible documentation gaps or missing edges._