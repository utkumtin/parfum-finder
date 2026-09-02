# Graph Report - parfum-finder  (2026-09-02)

## Corpus Check
- 142 files · ~321,144 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2691 nodes · 7578 edges · 114 communities (107 shown, 7 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 569 edges (avg confidence: 0.58)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `1ee4d9c3`
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
- extract_endpoint_variants
- Arayüz testleri
- test_every_shipped_site_has_a_colour_that_survives_256_colours
- test_updater.py
- product_label
- cached_prices
- SiteValidation
- _fake_runner
- split_queries
- variant_rules
- search_spellings
- Q: In the Windows application, when I release a new version, I click the ‘Update’ button to install the update, and the new update is downloaded. However, the application then closes and the installer does not launch. By pressing Win + R and then running the downloaded installer from the ‘%temp%’ directory, I am able to install the update without any issues. So I assume there is no block from Windows. I’m still experiencing this issue even though I’ve added it to the whitelist via Windows Defender. Could you please check if there’s an error in the code?
- enum
- WishlistRow
- Static
- extract_css_variants
- _retry_after_s
- test_every_shipped_site_has_a_colour_that_survives_256_colours

## God Nodes (most connected - your core abstractions)
1. `PerfumeQuery` - 76 edges
2. `search_site()` - 70 edges
3. `_profile()` - 69 edges
4. `connect()` - 66 edges
5. `SearchScreen` - 64 edges
6. `discover()` - 56 edges
7. `match_title()` - 56 edges
8. `SiteRunner` - 54 edges
9. `parse_query()` - 53 edges
10. `FetchResult` - 52 edges

## Surprising Connections (you probably didn't know these)
- `Shipping Non-linearity Rationale (why cheapest-per-item is wrong)` --semantically_similar_to--> `sites/ Site Profile Directory`  [INFERRED] [semantically similar]
  ARCHITECTURE.md → sites/README.md
- `Variant Pattern B (dropdown + AJAX price)` --semantically_similar_to--> `Variant Selector Detector Fix (WooCommerce 'variation' vs 'variant')`  [INFERRED] [semantically similar]
  ARCHITECTURE.md → docs/discovery-report.md
- `test_real_measurement_picks_httpx_for_a_plain_page()` --indirect_call--> `DiscoveryReport`  [INFERRED]
  tests/test_discover.py → src/parfum_finder/discover.py
- `test_a_hook_that_reads_nothing_is_named_as_the_culprit()` --indirect_call--> `ExtractionFailed`  [INFERRED]
  tests/test_engine.py → src/parfum_finder/engine.py
- `test_multiple_top_level_microdata_products_are_ambiguous()` --indirect_call--> `ExtractionFailed`  [INFERRED]
  tests/test_engine.py → src/parfum_finder/engine.py

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

## Communities (114 total, 7 thin omitted)

### Community 0 - "TUI App & Screens"
Cohesion: 0.09
Nodes (100): The Textual-based terminal UI: search and basket screens., _app(), _basket(), _cells(), _days_ago(), _leg(), _ok(), _open_basket() (+92 more)

### Community 1 - "Site Profiles & Templates"
Cohesion: 0.06
Nodes (80): _check_hook_kinds(), deep_merge(), _load_json(), load_platform_template(), load_platform_templates(), load_site_hooks(), load_site_profile(), Any (+72 more)

### Community 2 - "Title Matcher"
Cohesion: 0.29
Nodes (11): _normalized_product_name(), Recognize a single product page after a material same-origin redirect., _redirect_product_candidate(), _redirect_page(), test_material_redirect_cleans_tracking_and_rejects_cross_origin_metadata_url(), test_metadata_formats_agree_across_typographic_separators(), test_multiple_top_level_microdata_products_are_ambiguous(), test_nested_related_product_name_does_not_name_the_page_scope() (+3 more)

### Community 3 - "HTTP/Browser Fetching"
Cohesion: 0.19
Nodes (17): fetch(), Fetch one URL using exactly the given strategy.      `method`/`data` exist for t, test_the_no_results_page_would_otherwise_read_as_suspect(), Tests for parfum_finder.fetch.  httpx and curl_cffi are exercised against a real, test_fetch_follows_redirects_to_final_url(), test_fetch_playwright_missing_browser_binary_raises_the_same_error(), test_fetch_playwright_missing_extra_raises_clear_error(), test_fetch_playwright_no_response_raises_its_own_error_type() (+9 more)

### Community 4 - "Search/Basket Domain Models"
Cohesion: 0.16
Nodes (48): _app(), _painted_in_basket(), _per_query_runner(), Path, Tests for the search screen: grouping, persistence, and the key bindings.  A fak, A clone goes into the basket as itself, and only after being named as one., The table stays empty for the whole scan, and the bar carries the news.      Row, Answer each perfume with a row of its own, and record every scan asked for. (+40 more)

### Community 5 - "Search Engine per Site"
Cohesion: 0.09
Nodes (35): ProductCandidate, Dependency-free models shared by search, persistence, and presentation., One decant size of one product, in the units the database stores.      Tenths of, A candidate together with the decant sizes its product page offers., What one site had to say about one query, and how much to trust it.      Four st, One hit on a search results page, before its product page is opened.      `raw_t, SearchHit, SiteResult (+27 more)

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
Cohesion: 0.06
Nodes (68): CacheKey, HTMLParser, _canonical_path(), canonical_url(), _check_variant_control(), _decode_unreserved(), _fetch_page(), _has_product_ancestor() (+60 more)

### Community 10 - "Basket Optimizer Core"
Cohesion: 0.12
Nodes (41): BasketItem, optimize(), Prices, Score one site against the basket, or against a subset of it.      `item_ids` is, Score every enabled site against the whole basket and sort the results.      Sit, Search for the cheapest way to split the basket across several sites.      Retur, One line of the shopping list: a basket row, not a unit count.      `item_id` is, single_site_scenarios() (+33 more)

### Community 11 - "Basket Store & Pricing"
Cohesion: 0.26
Nodes (13): _factory(), Path, An error state is what turns the button back on with a reason.      Falling back, Nothing is spawned unless a complete file is on disk.      Running a half-writte, test_a_failed_download_says_so_instead_of_going_quiet(), test_a_second_download_is_refused_while_one_runs(), test_copy_bootstrapper_uses_a_unique_temp_executable(), test_download_writes_the_installer_and_reports_ready() (+5 more)

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
Cohesion: 0.10
Nodes (22): Check, _count_result_cards(), _first_result_url(), _LayerUnavailable, _no_results_check(), _probe_layer(), _probe_other_layers(), Any (+14 more)

### Community 16 - "Schema Field Patterns"
Cohesion: 0.06
Nodes (33): format, pattern, type, pattern, type, default, type, pattern (+25 more)

### Community 17 - "Offline Profile Validation"
Cohesion: 0.07
Nodes (37): CandidateFilter, _candidates_to_open(), _check_empty_search(), ExtractionFailed, RuntimeError, Narrow the search results down to the pages worth a request.      The first one, Fail when a search yielded no rows off a page that plainly lists products., A page answered but gave up nothing, where something was expected.      This is (+29 more)

### Community 18 - "Playwright Errors"
Cohesion: 0.11
Nodes (30): _choose_strategy(), _qualifies(), Pick the cheapest strategy that came back with real content, or None.      probe, Whether one strategy came back with a usable page., PlaywrightNoResponse, PlaywrightNotInstalled, RuntimeError, The "playwright" strategy was requested but cannot run at all.      Covers both (+22 more)

### Community 19 - "Search TUI Screen"
Cohesion: 0.08
Nodes (35): find_header_columns(), open_worksheet(), Any, Exception, Path, Protocol, Writing a search result onto the user's own Google Sheets wishlist.  The wishlis, Read the whole tab in one request: the header row, and every wishlist     row un (+27 more)

### Community 20 - "Snapshot Writing"
Cohesion: 0.18
Nodes (22): grouped_value(), Decimal, ResultRow, Pure sorting and grouping rules for the results table.  No I/O, no Textual state, What each site charges for the product a block is about.      One entry per site, The default order: typed order, product, site, size.      The typed order comes, The order once a column has been picked: the site layer drops out.      Asking f, site_ranks() (+14 more)

### Community 21 - "Candidate Filtering"
Cohesion: 0.09
Nodes (37): add_basket_item(), Add a size of a perfume to the basket, and return the basket_item_id.      The p, Connection, Adding the same perfume and size twice must accumulate, not clobber.      The ba, A basket line for a perfume nobody has priced is a bug, not a state to keep., The basket screen prints brand/name/concentration straight off this row.      Or, Two lines added within the same second must still read back the same way twice., A basket line nobody sells must still be visible via basket_lines.      basket_p (+29 more)

### Community 22 - "Basket Site Scenarios"
Cohesion: 0.12
Nodes (10): _Change, BasketScreen, BasketReport, BasketRow, Path, The one line that says the screen is holding something back, or is not., The basket: the list on top, one scenario per site underneath., _remove() (+2 more)

### Community 23 - "Price/Size Normalization"
Cohesion: 0.22
Nodes (9): is_newer(), _pad(), parse_version(), v0.2.1 -> (0, 2, 1). Sayıya çevrilemeyen her şey None., Okunamayan bir sürüm asla "yeni" sayılmaz.      Yanlış tarafa düşmenin bedeli si, A tag nobody can order against must not open a dialog.      The two failure dire, test_an_unreadable_tag_never_counts_as_an_update(), test_is_newer() (+1 more)

### Community 24 - "JSON Schema Primitives"
Cohesion: 0.11
Nodes (25): integer, null, string, properties, type, type, type, type (+17 more)

### Community 25 - "SQLite Store"
Cohesion: 0.09
Nodes (27): conn(), Path, Tests for parfum_finder.store: the timestamp helper and the schema.  The one har, Nothing on record is the state before a first search, not an error.      The sea, A disabled site loses its basket column, but an enabled quiet one keeps one., NULL means the site has no free shipping tier at all, not a threshold of zero., An update aimed at a row that isn't there means the caller is out of sync., The recents list has five slots, so a repeat must not consume two.      Someone (+19 more)

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
Cohesion: 0.15
Nodes (10): BasketRow, BestCombination, SiteScenario, basket(), basketRow(), resultRow(), scenario(), splitCombination() (+2 more)

### Community 31 - "Live Profile Validation"
Cohesion: 0.09
Nodes (34): Pattern, _brand_pattern(), _canonical(), _canonical_brands(), _covers(), _ends_with(), _index_of(), _match_text() (+26 more)

### Community 32 - "Variant Extraction Fields"
Cohesion: 0.11
Nodes (18): attribute, in_stock, price, script, size_raw, type, properties, additionalProperties (+10 more)

### Community 33 - "_ResultRow"
Cohesion: 0.11
Nodes (35): parse_query(), Split one typed line, "Dior Sauvage EDP", into the three identity parts.      Th, Whether a search result's own listing text is worth opening the page for.      J, title_could_match(), Tests for parfum_finder.matcher.  The thing being defended here is not "does it, test_a_brand_the_shop_writes_out_in_full_does_not_cost_the_match(), test_a_clone_is_still_shown_because_it_may_be_worth_buying(), test_a_clone_whose_own_title_names_one_word_has_no_identity_to_store() (+27 more)

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
Cohesion: 0.15
Nodes (20): _classify_single_separator(), format_age(), _parse_number(), parse_price(), parse_size_ml(), Decimal, Number parsing and formatting for prices and volumes, plus text folding.  This i, Decide whether a lone separator marks a fraction or a thousands group.      Retu (+12 more)

### Community 38 - "TUI Confirm Dialog"
Cohesion: 0.08
Nodes (28): Screen, Write one scan's reading of one size, and return its snapshot id.      The perfu, record_snapshot(), ParfumFinderApp, Path, The Textual App root. Handles screen navigation and is the app's default entry p, Root app: pushes the search screen on mount., SystemCommand (+20 more)

### Community 39 - "TUI App Shell"
Cohesion: 0.07
Nodes (51): Collection, BasketRow, _score_basket(), basket_inputs(), BasketReport, build_basket_rows(), _ClimbState, compare_split_to_best_full() (+43 more)

### Community 40 - "Fetch Backends"
Cohesion: 0.14
Nodes (14): curl_cffi, httpx, playwright, result_item, result_title, result_url, strategy, url_template (+6 more)

### Community 41 - "HTTP Request Schema"
Cohesion: 0.14
Nodes (14): GET, POST, properties, default, enum, type, type, type (+6 more)

### Community 42 - "Fixture Fetcher (Tests)"
Cohesion: 0.14
Nodes (46): BaseModel, FastAPI, AcceptedSearch, _AppState, BasketAddRequest, BasketQtyRequest, create_app(), The FastAPI app: a thin HTTP/WS wrapper around the Faz 1 services.  No business (+38 more)

### Community 43 - "FieldConfidence"
Cohesion: 0.22
Nodes (3): _FakeBrowser, _FakePage, Any

### Community 44 - "Decant Variant Rules"
Cohesion: 0.12
Nodes (25): readDetail(), request(), Window, UpdateDialog(), AppConfig, BasketReport, BasketResponse, RecentSearch (+17 more)

### Community 45 - "_ResultRow"
Cohesion: 0.10
Nodes (60): TestClient, _auth(), _client(), db_path(), _ok_result(), Any, MonkeyPatch, Path (+52 more)

### Community 46 - "Offline Validation Fixtures"
Cohesion: 0.25
Nodes (8): type, additionalProperties, type, body, request_headers, additionalProperties, description, type

### Community 47 - "JsonLdProduct"
Cohesion: 0.18
Nodes (17): authToken(), refusalReason(), streamUrl(), useEventStream(), ProgressBar(), formatAge(), formatMl(), formatPerMl() (+9 more)

### Community 48 - "._build_rows"
Cohesion: 0.07
Nodes (49): collect_prices(), DiscoveryReport, FieldConfidence, _flatten_defaults(), _format_choice(), _format_confidence(), _format_defaults(), _format_fingerprint() (+41 more)

### Community 49 - "_RecordingFetcher"
Cohesion: 0.11
Nodes (53): Path, Run one site and classify what came back instead of raising.      It is also whe, Run every site against one query, all at once, and report each separately., run_site(), run_sites(), FetchResult, One fetched page, uniform regardless of which strategy produced it., _attempt_hit() (+45 more)

### Community 50 - "Profile Age Checks"
Cohesion: 0.19
Nodes (22): format_report(), Check one site's profile against that site's saved fixtures.      Never raises f, Render the validations as the offline half of the report in APP_FLOW §6.      A, validate_offline(), _corrupted_sites_dir(), _iso_days_ago(), Any, Path (+14 more)

### Community 51 - "._refresh_table"
Cohesion: 0.12
Nodes (26): apply_variant_rules(), _is_excluded(), Decimal, Give a size the listing's title and URL when the page gave it none,     and make, Turn raw size rows into decant variants, dropping what is not a decant.      Thr, Read one row's volume in millilitres, or None if the text does not say.      "fi, Whether this row is something other than a decant.      The size threshold is in, Convert a price in lira to whole kuruş.      Integers all the way, never a float (+18 more)

### Community 52 - "FetchResult"
Cohesion: 0.15
Nodes (40): Lock, Connection, Mirror site profiles into the sites table and return how many were written., sync_to_db(), Any, A site's display name, with a badge when its profile is old enough     to be wor, Show what storage already knows, then go to the shops for the rest.      `force=, run_scan() (+32 more)

### Community 53 - "conftest.py"
Cohesion: 0.14
Nodes (29): Match, match_title(), PerfumeQuery, The perfume being looked for, split into its three identity parts.      `concent, One site title judged against the query.      `concentration` is what the title, Judge one site title against a query, or None if it is not that perfume.      No, test_a_brand_needs_all_of_its_words_not_one(), test_a_brand_only_query_matches_a_title_that_is_only_that_brand() (+21 more)

### Community 54 - "Endpoint Schema Fields"
Cohesion: 0.22
Nodes (9): result_item, result_title, result_url, url_template, search, additionalProperties, description, required (+1 more)

### Community 55 - "apply_variant_rules"
Cohesion: 0.29
Nodes (7): price_history(), Row, Return one variant's past readings, newest first, capped at limit.      Empty fo, The trend panel reads row 0 as the latest reading, so order is the point.      A, No history yet is a normal state for a variant, not an error to raise on., test_price_history_is_empty_for_an_unknown_variant(), test_price_history_is_newest_first_and_capped_at_limit()

### Community 56 - "Request Schema Fields"
Cohesion: 0.04
Nodes (45): jsdom, motion, @playwright/test, react, react-dom, @testing-library/jest-dom, @testing-library/react, @testing-library/user-event (+37 more)

### Community 57 - "_FixtureFetcher"
Cohesion: 0.10
Nodes (9): Changed, HeaderSelected, The initial screen: search bar, streaming results table, notices, footer., Close out a submit that named no perfume anyone could look for., Show what storage already knows, then go to the shops for the rest.          `fo, Say a perfume came off the record instead of off the shops.          Without thi, Empty the table for a new scan.          The columns are the same every time now, SearchScreen (+1 more)

### Community 58 - "setup_logging"
Cohesion: 0.07
Nodes (27): DOM, DOM.Iterable, e2e, ES2022, playwright.config.ts, src, tests, vite/client (+19 more)

### Community 59 - "_named_profile"
Cohesion: 0.17
Nodes (21): _close_browser(), _close_session_browser(), _fetch_curl_cffi(), _fetch_httpx(), _fetch_playwright(), _folded(), _launch_browser(), Any (+13 more)

### Community 60 - "_wait_for_table"
Cohesion: 0.38
Nodes (4): BookmarkIcon(), BookmarkIconProps, variants, WishlistButton()

### Community 61 - "._apply_scan_event"
Cohesion: 0.21
Nodes (16): _close_handle(), _copy_bootstrapper(), _create_ready_event(), handoff_command(), _kernel32(), launch_installer(), Path, RuntimeError (+8 more)

### Community 62 - "snapshot_rows"
Cohesion: 0.09
Nodes (37): The search screen's second search must be answered with today's numbers.      Tw, A search that named no concentration is asking for all of them.      "" means "a, A price nobody will scan again may not be offered as a result.      Refreshing i, One call has to leave a row the search table can read straight off.      The cal, The old price has to survive, and it must not become a second variant.      Appe, first_seen is what says how long a shop has carried a size., The title and URL are information, not identity.      A shop that rewords a list, EDT and EDP are different products at different prices.      Folding them into o (+29 more)

### Community 64 - "validate_live"
Cohesion: 0.22
Nodes (4): Client, DownloadProgress, İndirmeyi başlatır. Zaten çalışıyorsa None., state: idle | downloading | ready | installing | error.

### Community 65 - "_named_profile"
Cohesion: 0.13
Nodes (20): Try spelling variants until this site returns an emittable match.      The match, run_site_attempts(), Path, Give the test profile's site id a hook file. The id is what binds them., test_a_before_search_that_returns_no_query_is_refused(), test_a_hook_that_reads_nothing_is_named_as_the_culprit(), test_a_site_with_no_hook_file_is_driven_by_its_profile_alone(), test_after_search_can_drop_a_result_the_selectors_could_not() (+12 more)

### Community 67 - "extract_embedded_variants"
Cohesion: 0.13
Nodes (19): Any, Connection, Command-line entry point.  Subcommands will be added incrementally as the projec, Scan every perfume against every site and print each site as it lands.      One, Write one site's rows in a transaction of its own.      Per site rather than per, One line per site: which site, how it went, and what it said.      The site id i, _report_line(), _scan_all() (+11 more)

### Community 68 - "JsonLdProduct"
Cohesion: 0.24
Nodes (10): check_enabled(), check_for_update(), _installer_asset(), _no_update(), Any, ReleaseInfo, No network is not an error the user has to be told about.      The check runs un, test_check_reports_nothing_when_the_release_is_the_installed_one() (+2 more)

### Community 72 - "write_snapshots"
Cohesion: 0.06
Nodes (59): _add_basket_item(), _load_profiles(), Any, Path, _read_basket(), _read_wishlist(), _recent_searches(), _record_search() (+51 more)

### Community 73 - "_css_variant"
Cohesion: 0.14
Nodes (21): _age_of(), live_query(), _path(), profile_age_days(), datetime, Profile staleness checks. Two modes: offline (against saved fixtures) and live (, A URL's path with no trailing slash, for comparing two spellings of one page., Every site that has a profile, sorted so reports read the same way twice. (+13 more)

### Community 74 - "ConfirmDialog.tsx"
Cohesion: 0.53
Nodes (4): FormData, Headers, Method, Strategy

### Community 75 - "ResultRow"
Cohesion: 0.06
Nodes (54): _as_str(), _balanced_value(), _build_offer(), _build_product(), _coerce_in_stock(), _collect_offers(), _collect_products(), _collect_variants() (+46 more)

### Community 76 - "SplitPlan"
Cohesion: 0.12
Nodes (17): AddButton(), Badge(), BadgeKind, ConfirmDialog(), ScanStatus(), VerdictAddButton(), basketKey(), Block (+9 more)

### Community 77 - "_collect_products"
Cohesion: 0.21
Nodes (17): Run one site's profile against the real site.      Same contract as offline mode, validate_live(), _DeadSite, _FakeSite, _fixture_site(), M5's own criterion: when a profile stops agreeing with its site's real markup, o, A stand-in for one live site, answering the search page then the rest.      Live, A host that cannot be reached at all. (+9 more)

### Community 78 - "_fake_runner"
Cohesion: 0.28
Nodes (12): arguments_t, BOOL, DWORD, HINSTANCE, append_log(), argument_value(), launch_setup(), parse_arguments() (+4 more)

### Community 79 - "AddButton.tsx"
Cohesion: 0.15
Nodes (27): _named_result(), _ok_result(), LogCaptureFixture, Submitting a query has to hand focus to the table.      A focused Input swallows, The row under the cursor has to survive the table being rebuilt.      Nothing re, A database that will not take the prices must not erase the site.      The table, A result the screen cannot read is a broken site, not a quiet skip.      Nothing, The panel exists so today's price can be judged against its own past.      A bar (+19 more)

### Community 80 - "field_map"
Cohesion: 0.17
Nodes (8): App(), Toast, View, wishlistIdentity, wishlistKey(), root, normalizeSearchText(), WishlistScreen()

### Community 81 - "run_sites"
Cohesion: 0.09
Nodes (57): Pressed, ScanEvent, BasketRefreshEvent and viewmodel dataclasses as JSON-safe dicts.  Eve, Protocol, One site's pacing state, for as long as whoever holds it says.      The gate and, What a caller needs of run_site, as a type callers can stand a fake in for., SitePace, SiteRunner, Fetcher (+49 more)

### Community 82 - "Node"
Cohesion: 0.41
Nodes (11): _bootstrapper(), _close_handle(), _command(), _kernel32(), Any, Path, Windows integration checks for the native update helper., _ready_event() (+3 more)

### Community 83 - "test_one_query_finding_two_bottles_gets_two_blocks"
Cohesion: 0.24
Nodes (16): browser_session(), Yield a fetcher that keeps one browser for every playwright page it reads., _fake_launch(), Event, MonkeyPatch, Stand in for the browser process, and count how many were started., _read_one_page_then_hang(), test_a_real_session_reads_two_pages_in_one_browser() (+8 more)

### Community 84 - "_wait_until"
Cohesion: 0.21
Nodes (15): probe(), Fetch `url` with every strategy and report diagnostics for each.      timeout_s, MonkeyPatch, Tests for parfum_finder.probe.  probe() always tries all three strategies -- the, test_probe_counts_jsonld_product_and_platform_signature(), test_probe_counts_product_across_jsonld_root_shapes(), test_probe_counts_product_markup_without_any_jsonld(), test_probe_counts_products_nested_below_the_top_level() (+7 more)

### Community 85 - "enum"
Cohesion: 0.50
Nodes (3): The template this site's profile would be based on, if any., Which of the matching templates gets applied, or None for none of them.      One, _resolve_platform()

### Community 86 - "BasketRow"
Cohesion: 0.18
Nodes (3): RowSelected, ResultRow, Row

### Community 87 - "helpers.ts"
Cohesion: 0.47
Nodes (7): addFirstRow(), authToken(), clearBasket(), openApp(), search(), searchButton(), tab()

### Community 88 - "handoff_command"
Cohesion: 0.15
Nodes (10): api, ApiError, daysSince(), SearchScreen(), splitParts(), compile(), DEFAULT_CONFIG, FakeServer (+2 more)

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
Nodes (4): _FakeClient, _FakeStreamResponse, Any, Exception

### Community 93 - "extract_endpoint_variants"
Cohesion: 0.18
Nodes (9): BaseHTTPRequestHandler, _Handler, _playwright_usable(), MonkeyPatch, Shared pytest fixtures.  A local HTTP server used by fetch/probe tests: real req, Whether the playwright rung can actually run here, binary included.      Checkin, Record every delay the engine asks for instead of serving it.      Waiting for r, server_url() (+1 more)

### Community 94 - "Arayüz testleri"
Cohesion: 0.40
Nodes (4): Arayüz testleri, jsdom katmanı (`tests/`), Ne test edilmiyor, Tarayıcı katmanı (`e2e/`)

### Community 95 - "test_every_shipped_site_has_a_colour_that_survives_256_colours"
Cohesion: 0.17
Nodes (12): _normalize_utc_timestamp(), Return one aware timestamp in the database's canonical UTC format., Write a whole scan at once and return how many prices were recorded.      Every, write_snapshots(), The drop happens here so no caller can forget it.      Both the CLI and the scre, A slow site must not spread one reading across several timestamps.      Rows wri, The number reported is what landed in the history, not what was offered., Half a site's sizes updated is worse than none of them.      The basket compares (+4 more)

### Community 96 - "test_updater.py"
Cohesion: 0.27
Nodes (13): fetch_latest_release(), En son yayımlanmış sürüm, ya da ulaşılamadıysa None.      /releases/latest tasla, _enable_checks(), _patch_get(), MonkeyPatch, Tests for parfum_finder.updater: the version compare, the release read, and the, The .exe is what gets downloaded, whatever else is attached.      Releases carry, _release_payload() (+5 more)

### Community 97 - "product_label"
Cohesion: 0.18
Nodes (11): product_label(), Reduce a site's own title to the product it is about, spelled one way.      What, test_a_clone_is_labelled_by_the_bottle_it_is_and_not_what_it_imitates(), test_a_longer_named_bottle_does_not_join_the_shorter_ones_block(), test_a_title_with_no_product_words_left_has_no_label(), test_catalog_decorations_do_not_split_product_groups(), test_every_shops_spelling_of_one_bottle_lands_in_one_block(), test_one_bottle_spelled_two_ways_lands_in_one_block() (+3 more)

### Community 98 - "cached_prices"
Cohesion: 0.25
Nodes (11): _named_profile(), Any, The real fetcher, with a list of every URL it was asked for., A profile whose search page lists two houses' bottles, as shops do., test_a_listing_from_another_house_costs_no_product_request(), test_diagnostic_candidate_checks_extraction_but_never_emits_a_hit(), test_one_product_listed_under_two_searches_is_read_once(), test_the_product_cache_keeps_what_a_page_said_not_the_page() (+3 more)

### Community 99 - "SiteValidation"
Cohesion: 0.25
Nodes (7): _age_line(), format_live_report(), Every check run against one site's profile, in the order they ran.      Checks s, Whether the profile is old enough to be worth re-discovering., The age note for one site, or None when its age is unremarkable.      A profile, Render offline and live results side by side, as APP_FLOW §6 shows them.      Bo, SiteValidation

### Community 102 - "_fake_runner"
Cohesion: 0.33
Nodes (8): _fake_runner(), main(), _matching_product(), _profile(), Any, The backend playwright drives: the real app, with the shops stubbed out.  Everyt, Which catalogue product a typed query is about, by its leading words.      Delib, A profile that passes schema validation and is never actually fetched.

### Community 103 - "split_queries"
Cohesion: 0.25
Nodes (8): Split one typed line into the perfumes it asks for, on " - ".      The separator, split_queries(), test_a_hyphen_inside_a_brand_name_does_not_split_the_search(), test_a_line_naming_three_perfumes_is_read_as_three_searches(), test_a_piece_that_names_no_perfume_survives_to_be_complained_about(), test_a_stray_separator_is_not_worth_failing_over(), test_one_perfume_is_still_one_search(), test_the_same_perfume_typed_twice_is_scanned_once()

### Community 104 - "variant_rules"
Cohesion: 0.25
Nodes (8): exclude_keywords, max_size_ml, size_from, size_pattern, variant_rules, additionalProperties, required, type

### Community 105 - "search_spellings"
Cohesion: 0.29
Nodes (7): _fold_search_separators(), One search line, then the same line with the brand written the other ways., Turn punctuation that commonly splits catalog tokens into spaces., search_spellings(), test_a_brand_nobody_abbreviates_is_asked_for_once(), test_brand_aliases_each_receive_one_separator_folded_attempt_in_order(), test_the_typed_spelling_is_asked_first_and_the_rest_only_follow()

### Community 106 - "Q: In the Windows application, when I release a new version, I click the ‘Update’ button to install the update, and the new update is downloaded. However, the application then closes and the installer does not launch. By pressing Win + R and then running the downloaded installer from the ‘%temp%’ directory, I am able to install the update without any issues. So I assume there is no block from Windows. I’m still experiencing this issue even though I’ve added it to the whitelist via Windows Defender. Could you please check if there’s an error in the code?"
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: In the Windows application, when I release a new version, I click the ‘Update’ button to install the update, and the new update is downloaded. However, the application then closes and the installer does not launch. By pressing Win + R and then running the downloaded installer from the ‘%temp%’ directory, I am able to install the update without any issues. So I assume there is no block from Windows. I’m still experiencing this issue even though I’ve added it to the whitelist via Windows Defender. Could you please check if there’s an error in the code?, Source Nodes

### Community 107 - "enum"
Cohesion: 0.33
Nodes (6): css, embedded_json, endpoint, jsonld, enum, extraction

### Community 108 - "WishlistRow"
Cohesion: 0.47
Nodes (6): find_match(), The wishlist row that best names the same perfume as `query`, if any     clears, One perfume as it sits in the wishlist: which sheet row it is on, and     the br, WishlistRow, test_find_match_picks_the_best_scoring_wishlist_row(), test_find_match_returns_none_when_nothing_clears_the_floor_score()

### Community 109 - "Static"
Cohesion: 0.40
Nodes (3): ComposeResult, ComposeResult, Static

## Knowledge Gaps
- **238 isolated node(s):** `parfum-finder`, `$schema`, `$id`, `title`, `description` (+233 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **7 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Work-memory lessons

**Preferred sources** — corroborated by past sessions; start here.
- `price_history()` (2× useful, score=1.923825881)
- `BasketScreen()` (2× useful, score=1.923825881)

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `SiteRunner` connect `run_sites` to `_named_profile`, `Search Engine per Site`, `TUI Confirm Dialog`, `TUI App Shell`, `Search Engine Core`, `Fixture Fetcher (Tests)`, `_ResultRow`, `extract_css_variants`, `_RecordingFetcher`, `Playwright Errors`, `._refresh_table`, `FetchResult`, `Basket Site Scenarios`, `_FixtureFetcher`?**
  _High betweenness centrality (0.029) - this node is a cross-community bridge._
- **Why does `BasketScreen` connect `Basket Site Scenarios` to `TUI App & Screens`, `Site Profiles & Templates`, `TUI App Shell`, `write_snapshots`, `Basket Optimizer Core`, `Fixture Fetcher (Tests)`, `Static`, `run_sites`, `_FixtureFetcher`?**
  _High betweenness centrality (0.024) - this node is a cross-community bridge._
- **Why does `connect()` connect `write_snapshots` to `TUI App & Screens`, `Site Profiles & Templates`, `extract_embedded_variants`, `Search/Basket Domain Models`, `Search Engine per Site`, `TUI Confirm Dialog`, `TUI App Shell`, `CLI Entry Points`, `Fixture Fetcher (Tests)`, `AddButton.tsx`, `run_sites`, `FetchResult`, `Basket Site Scenarios`, `BasketRow`, `SQLite Store`?**
  _High betweenness centrality (0.023) - this node is a cross-community bridge._
- **Are the 19 inferred relationships involving `PerfumeQuery` (e.g. with `BasketPriceExcluded` and `BasketRefreshFinished`) actually correct?**
  _`PerfumeQuery` has 19 INFERRED edges - model-reasoned connections that need verification._
- **Are the 14 inferred relationships involving `SearchScreen` (e.g. with `ParfumFinderApp` and `SiteRunner`) actually correct?**
  _`SearchScreen` has 14 INFERRED edges - model-reasoned connections that need verification._
- **What connects `parfum-finder`, `$schema`, `$id` to the rest of the system?**
  _238 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `TUI App & Screens` be split into smaller, more focused modules?**
  _Cohesion score 0.09337992622791691 - nodes in this community are weakly interconnected._