# Graph Report - parfum-finder  (2026-09-05)

## Corpus Check
- 147 files · ~329,896 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2770 nodes · 7650 edges · 121 communities (112 shown, 9 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 515 edges (avg confidence: 0.56)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `1f233c13`
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
- _submit_query
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
- _ask_chooser
- run_sites
- Node
- test_one_query_finding_two_bottles_gets_two_blocks
- select_field
- enum
- SiteValidation
- helpers.ts
- BookmarkIcon.tsx
- ._write_to_sheet
- ._start_search
- Q: After correcting the free-delivery wishlist idea, what other genuinely useful, high-priority Windows app features could produce a 'brilliant that you thought of that' reaction?
- _FakeStreamResponse
- extract_endpoint_variants
- Arayüz testleri
- test_normalize.py
- test_updater.py
- product_label
- select_field
- SiteValidation
- enum
- Static
- ws.test.ts
- search_spellings
- Q: In the Windows application, when I release a new version, I click the ‘Update’ button to install the update, and the new update is downloaded. However, the application then closes and the installer does not launch. By pressing Win + R and then running the downloaded installer from the ‘%temp%’ directory, I am able to install the update without any issues. So I assume there is no block from Windows. I’m still experiencing this issue even though I’ve added it to the whitelist via Windows Defender. Could you please check if there’s an error in the code?
- FakeWebSocket
- apply_variant_rules
- _NoRootParser
- Badge.tsx
- ParfumFinderApp
- _with_candidate_identity
- tui/app.py
- test_every_shipped_site_has_a_colour_that_survives_256_colours

## God Nodes (most connected - your core abstractions)
1. `PerfumeQuery` - 76 edges
2. `search_site()` - 70 edges
3. `_profile()` - 69 edges
4. `connect()` - 66 edges
5. `SearchScreen` - 63 edges
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
- `_NoRootParser` --uses--> `ExtractionFailed`  [INFERRED]
  tests/test_engine.py → src/parfum_finder/engine.py
- `test_canonical_url_ignores_tracking_but_preserves_functional_duplicate_params()` --calls--> `canonical_url()`  [EXTRACTED]
  tests/test_engine.py → src/parfum_finder/engine.py
- `_RecordingClient` --uses--> `SiteRunner`  [INFERRED]
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
- 4-file cycle: `src/parfum_finder/__init__.py -> src/parfum_finder/cli.py -> src/parfum_finder/services/snapshots.py -> src/parfum_finder/store.py -> src/parfum_finder/__init__.py`
- 5-file cycle: `src/parfum_finder/__init__.py -> src/parfum_finder/cli.py -> src/parfum_finder/validate.py -> src/parfum_finder/engine.py -> src/parfum_finder/profiles.py -> src/parfum_finder/__init__.py`

## Hyperedges (group relationships)
- **Sites Implementing Variant Pattern C (embedded JSON)** — docs_discovery_report_venco_site, docs_discovery_report_decantall_site, docs_discovery_report_luxurydekant_site, docs_discovery_report_ruxangroup_site, architecture_md_variant_pattern_c [EXTRACTED 1.00]
- **İdeasoft Platform Sites and Endpoint** — docs_discovery_report_dekantparfum_site, docs_discovery_report_dekantdoktoru_site, docs_discovery_report_ideasoft_related_options_endpoint, platforms_readme_ideasoft_json [EXTRACTED 1.00]
- **discover Command Output Artifacts (profile + fixtures + CI validation)** — architecture_md_discover_flow, sites_readme_sites_dir, fixtures_readme_fixtures_dir, github_workflows_ci_validate_profiles_step, architecture_md_validate_command [INFERRED 0.85]

## Communities (121 total, 9 thin omitted)

### Community 0 - "TUI App & Screens"
Cohesion: 0.09
Nodes (100): The Textual-based terminal UI: search and basket screens., _app(), _basket(), _cells(), _days_ago(), _leg(), _ok(), _open_basket() (+92 more)

### Community 1 - "Site Profiles & Templates"
Cohesion: 0.06
Nodes (81): _check_hook_kinds(), deep_merge(), _load_json(), load_platform_template(), load_platform_templates(), load_site_hooks(), load_site_profile(), Any (+73 more)

### Community 2 - "Title Matcher"
Cohesion: 0.11
Nodes (7): HeaderSelected, RowSelected, Any, Path, work, The initial screen: search bar, streaming results table, notices, footer., SearchScreen

### Community 3 - "HTTP/Browser Fetching"
Cohesion: 0.08
Nodes (24): _Change, format_price(), Format a price for display (comma-thousands, dot-decimal). Decimal('1250') ->…, BasketScreen, _heading(), _leg_block(), BasketReport, BasketRow (+16 more)

### Community 4 - "Search/Basket Domain Models"
Cohesion: 0.15
Nodes (49): _app(), _basket_count(), _painted_in_basket(), _per_query_runner(), Path, Tests for the search screen: grouping, persistence, and the key bindings. A…, A clone goes into the basket as itself, and only after being named as one. Both…, The confirm dialog has to look and behave like something answerable. Its keys… (+41 more)

### Community 5 - "Search Engine per Site"
Cohesion: 0.10
Nodes (28): The search screen's second search must be answered with today's numbers. Two…, A search that named no concentration is asking for all of them. "" means "any"…, One call has to leave a row the search table can read straight off. The caller…, The old price has to survive, and it must not become a second variant. Append-…, first_seen is what says how long a shop has carried a size., The title and URL are information, not identity. A shop that rewords a listing…, EDT and EDP are different products at different prices. Folding them into one…, A sold-out size often shows no price at all, and 0 would mean free. Writing a… (+20 more)

### Community 6 - "Platform Discovery Flow"
Cohesion: 0.14
Nodes (60): PlatformChooser, _ask_chooser(), discover(), Put the question only when there is one, and hold the answer to it. An answer…, Measure the strategies a site needs, then read its JSON-LD with the winner.…, _attempt(), _fake_probe(), Any (+52 more)

### Community 7 - "CLI Entry Points"
Cohesion: 0.08
Nodes (65): CaptureFixture, ask_which_platform(), main(), Any, Connection, Path, Command-line entry point. Subcommands will be added incrementally as the…, Scan every site for the perfumes named, store what came back, print it. One… (+57 more)

### Community 8 - "Architecture Rationale Docs"
Cohesion: 0.05
Nodes (53): basket Subset Enumeration + Local Improvement Algorithm, basket Optimizer (optimize function), Clone/Original Distinction (KLON ← <orijinal>), discover Discovery Flow, engine Concurrency Model (parallel sites, serial within site), Extraction Ladder (jsonld/endpoint/embedded/css), Fail-loud / status=suspect policy, hooks/<id>.py Escape Hatch (+45 more)

### Community 9 - "Search Engine Core"
Cohesion: 0.07
Nodes (67): HTMLParser, _canonical_path(), canonical_url(), _check_variant_control(), _decode_unreserved(), ExtractionFailed, _fetch_page(), _has_product_ancestor() (+59 more)

### Community 10 - "Basket Optimizer Core"
Cohesion: 0.07
Nodes (66): Collection, BasketRow, _score_basket(), basket_inputs(), BasketItem, BasketReport, build_basket_rows(), compare_split_to_best_full() (+58 more)

### Community 11 - "Basket Store & Pricing"
Cohesion: 0.15
Nodes (18): Client, DownloadProgress, Kurulum dosyasının tek bir arka plan indirmesi ve devri. Süreç başına bir tane:…, İndirmeyi başlatır. Zaten çalışıyorsa None., İnen kurulumu başlatır. Hazır değilse False., state: idle | downloading | ready | installing | error., UpdateDownload, _factory() (+10 more)

### Community 12 - "JSON-LD Product Extraction"
Cohesion: 0.15
Nodes (30): extract_jsonld_products(), Read every JSON-LD Product declared on the page, in document order. A block…, _one_product_html(), Tests for parfum_finder.extract. Every case here is a shape a real store…, Wrap a JSON-LD product body in a page, for the one-field-at-a-time cases., test_a_broken_block_does_not_lose_the_valid_one(), test_availability_spellings_all_land_in_the_same_bucket(), test_boolean_values_are_never_read_as_price_or_text() (+22 more)

### Community 13 - "Basket TUI Screen"
Cohesion: 0.08
Nodes (46): PyInstaller entry point for the packaged desktop app. Kept outside…, _close_window_when_asked(), _hold_app_mutex(), _kill_children_with_app(), _ping(), Event, Path, The Windows desktop entry point: an ephemeral-port FastAPI backend behind a… (+38 more)

### Community 14 - "Platform Schema"
Cohesion: 0.06
Nodes (31): any, defaults, fingerprint, additionalProperties, items, minItems, type, description (+23 more)

### Community 15 - "Product Extraction"
Cohesion: 0.12
Nodes (52): BaseModel, FastAPI, AcceptedSearch, _add_basket_item(), _AppState, BasketAddRequest, BasketQtyRequest, create_app() (+44 more)

### Community 16 - "Schema Field Patterns"
Cohesion: 0.06
Nodes (33): format, pattern, type, pattern, type, default, type, pattern (+25 more)

### Community 17 - "Offline Profile Validation"
Cohesion: 0.27
Nodes (12): _normalized_product_name(), Recognize a single product page after a material same-origin redirect., _redirect_product_candidate(), parametrize, _redirect_page(), test_material_redirect_cleans_tracking_and_rejects_cross_origin_metadata_url(), test_metadata_formats_agree_across_typographic_separators(), test_multiple_top_level_microdata_products_are_ambiguous() (+4 more)

### Community 18 - "Playwright Errors"
Cohesion: 0.12
Nodes (28): FieldConfidence, One field this run can fill in, with how far it can be trusted. `field` is the…, PlaywrightNoResponse, PlaywrightNotInstalled, RuntimeError, The "playwright" strategy was requested but cannot run at all. Covers both…, Navigation completed but playwright returned no Response object. Its own type…, _attempt() (+20 more)

### Community 19 - "Search TUI Screen"
Cohesion: 0.07
Nodes (42): find_header_columns(), find_match(), open_worksheet(), Any, Exception, Path, Protocol, Writing a search result onto the user's own Google Sheets wishlist. The… (+34 more)

### Community 20 - "Snapshot Writing"
Cohesion: 0.13
Nodes (17): Check, _count_result_cards(), _first_result_url(), _no_results_check(), _probe_layer(), _probe_other_layers(), Any, Path (+9 more)

### Community 21 - "Candidate Filtering"
Cohesion: 0.09
Nodes (37): add_basket_item(), Add a size of a perfume to the basket, and return the basket_item_id. The…, Connection, Adding the same perfume and size twice must accumulate, not clobber. The basket…, A basket line for a perfume nobody has priced is a bug, not a state to keep.…, The basket screen prints brand/name/concentration straight off this row.…, Two lines added within the same second must still read back the same way twice.…, A basket line nobody sells must still be visible via basket_lines.… (+29 more)

### Community 22 - "_submit_query"
Cohesion: 0.18
Nodes (21): grouped_value(), Decimal, ResultRow, What each site charges for the product a block is about. One entry per site per…, The default order: typed order, product, site, size. The typed order comes…, The order once a column has been picked: the site layer drops out. Asking for…, site_ranks(), sorted_value() (+13 more)

### Community 23 - "Price/Size Normalization"
Cohesion: 0.22
Nodes (10): is_newer(), _pad(), parse_version(), v0.2.1 -> (0, 2, 1). Sayıya çevrilemeyen her şey None., Okunamayan bir sürüm asla "yeni" sayılmaz. Yanlış tarafa düşmenin bedeli…, parametrize, A tag nobody can order against must not open a dialog. The two failure…, test_an_unreadable_tag_never_counts_as_an_update() (+2 more)

### Community 24 - "JSON Schema Primitives"
Cohesion: 0.11
Nodes (25): integer, null, string, properties, type, type, type, type (+17 more)

### Community 25 - "SQLite Store"
Cohesion: 0.09
Nodes (27): conn(), Path, Tests for parfum_finder.store: the timestamp helper and the schema. The one…, Nothing on record is the state before a first search, not an error. The search…, A disabled site loses its basket column, but an enabled quiet one keeps one.…, NULL means the site has no free shipping tier at all, not a threshold of zero.…, An update aimed at a row that isn't there means the caller is out of sync.…, The recents list has five slots, so a repeat must not consume two. Someone who… (+19 more)

### Community 26 - "Site Profile Fields"
Cohesion: 0.10
Nodes (20): base_url, discovered_at, extraction, id, needs_review, platform, search, shipping (+12 more)

### Community 27 - "Site Schema Validation Tests"
Cohesion: 0.18
Nodes (18): Draft202012Validator, _load_schema(), _platform_validator(), Any, parametrize, Tests for schema/site.schema.json and schema/platform.schema.json. These check…, The third copy of the ladder is here, and nothing else would catch it drifting.…, _site_validator() (+10 more)

### Community 28 - "Variant Rule Fields"
Cohesion: 0.11
Nodes (18): field, title, variant_label, items, type, type, exclusiveMinimum, type (+10 more)

### Community 29 - "Discovery CLI Reporting"
Cohesion: 0.17
Nodes (5): format_age(), Turn a price age in days into the words the age column shows., ResultRow, Row, test_format_age_reads_as_words_not_a_timestamp()

### Community 30 - "Store Timestamp Tests"
Cohesion: 0.15
Nodes (13): UpdateDialog(), UpdateInfo, UpdateProgress, INFO, DEFAULT_SITES, EMPTY_BASKET, NO_UPDATE, RecordedRequest (+5 more)

### Community 31 - "Live Profile Validation"
Cohesion: 0.09
Nodes (36): Pattern, _brand_pattern(), _canonical(), _canonical_brands(), _covers(), _ends_with(), _index_of(), _match_text() (+28 more)

### Community 32 - "Variant Extraction Fields"
Cohesion: 0.11
Nodes (18): attribute, in_stock, price, script, size_raw, type, properties, additionalProperties (+10 more)

### Community 33 - "_ResultRow"
Cohesion: 0.08
Nodes (46): parse_query(), Split one typed line into the perfumes it asks for, on " - ". The separator has…, Split one typed line, "Dior Sauvage EDP", into the three identity parts. The…, Whether a search result's own listing text is worth opening the page for.…, split_queries(), title_could_match(), test_a_scan_says_how_many_listings_it_skipped(), test_reported_false_negative_searches_keep_requested_identity_and_sizes() (+38 more)

### Community 34 - "Fetch Strategy Probing"
Cohesion: 0.10
Nodes (46): _check_empty_search(), Fail when a search yielded no rows off a page that plainly lists products. The…, How long the shop asked to be left alone, or None if it did not say. A refusal…, Run one site and classify what came back instead of raising. It is also where…, _retry_after_s(), run_site(), FetchResult, One fetched page, uniform regardless of which strategy produced it. (+38 more)

### Community 35 - "Platform Field Mapping"
Cohesion: 0.12
Nodes (16): field_map, product_json, source, variants_path, additionalProperties, allOf, description, required (+8 more)

### Community 36 - "Shipping Config Schema"
Cohesion: 0.14
Nodes (14): free_shipping_threshold_kurus, shipping_cost_kurus, minimum, type, free_shipping_threshold_kurus, notes, shipping, shipping_cost_kurus (+6 more)

### Community 37 - "_trial"
Cohesion: 0.15
Nodes (20): _classify_single_separator(), format_ml(), _parse_number(), parse_price(), parse_size_ml(), Decimal, Number parsing and formatting for prices and volumes, plus text folding. This…, Decide whether a lone separator marks a fraction or a thousands group. Returns… (+12 more)

### Community 38 - "TUI Confirm Dialog"
Cohesion: 0.12
Nodes (36): requires_playwright_package, browser_session(), fetch(), Fetch one URL using exactly the given strategy. `method`/`data` exist for the…, Yield a fetcher that keeps one browser for every playwright page it reads. What…, test_the_no_results_page_would_otherwise_read_as_suspect(), _fake_launch(), Event (+28 more)

### Community 39 - "TUI App Shell"
Cohesion: 0.10
Nodes (39): Try spelling variants until this site returns an emittable match. The matcher…, run_site_attempts(), Match, match_title(), PerfumeQuery, The perfume being looked for, split into its three identity parts.…, One site title judged against the query. `concentration` is what the title…, Judge one site title against a query, or None if it is not that perfume. None… (+31 more)

### Community 40 - "Fetch Backends"
Cohesion: 0.14
Nodes (14): curl_cffi, httpx, playwright, result_item, result_title, result_url, strategy, url_template (+6 more)

### Community 41 - "HTTP Request Schema"
Cohesion: 0.14
Nodes (14): GET, POST, properties, default, enum, type, type, type (+6 more)

### Community 42 - "Fixture Fetcher (Tests)"
Cohesion: 0.16
Nodes (30): _ok_result(), LogCaptureFixture, MonkeyPatch, Submitting a query has to hand focus to the table. A focused Input swallows…, The row under the cursor has to survive the table being rebuilt. Nothing…, A database that will not take the prices must not erase the site. The table…, A result the screen cannot read is a broken site, not a quiet skip. Nothing…, The panel exists so today's price can be judged against its own past. A bare… (+22 more)

### Community 43 - "FieldConfidence"
Cohesion: 0.06
Nodes (48): App(), Toast, View, ActiveRequest, BasketSnapshot, Deferred, ensureBasket(), getBasketSnapshot() (+40 more)

### Community 44 - "Decant Variant Rules"
Cohesion: 0.10
Nodes (36): ProductCandidate, Dependency-free models shared by search, persistence, and presentation., One decant size of one product, in the units the database stores. Tenths of a…, A candidate together with the decant sizes its product page offers., What one site had to say about one query, and how much to trust it. Four…, One hit on a search results page, before its product page is opened.…, SearchHit, SiteResult (+28 more)

### Community 45 - "_ResultRow"
Cohesion: 0.10
Nodes (67): TestClient, _auth(), _client(), db_path(), _ok_result(), Any, MonkeyPatch, Path (+59 more)

### Community 46 - "Offline Validation Fixtures"
Cohesion: 0.25
Nodes (8): type, additionalProperties, type, body, request_headers, additionalProperties, description, type

### Community 47 - "JsonLdProduct"
Cohesion: 0.13
Nodes (12): AcceptedSearch, BasketRefreshEvent, BasketReport, BasketResponse, BasketRow, BestCombination, ResultRow, ScanEvent (+4 more)

### Community 48 - "._build_rows"
Cohesion: 0.07
Nodes (49): _choose_strategy(), collect_prices(), DiscoveryReport, _flatten_defaults(), _format_choice(), _format_confidence(), _format_defaults(), _format_fingerprint() (+41 more)

### Community 49 - "_RecordingFetcher"
Cohesion: 0.09
Nodes (51): Run one query against one site and read every hit's sizes. Everything site-…, search_site(), _attempt_hit(), _named_profile(), Path, Tests for the profile-driven search in parfum_finder.engine. What these defend…, The real fetcher, with a list of every URL it was asked for., A profile whose search page lists two houses' bottles, as shops do. (+43 more)

### Community 50 - "Profile Age Checks"
Cohesion: 0.18
Nodes (24): format_report(), Check one site's profile against that site's saved fixtures. Never raises for a…, Validate every site, or just the ones named. Serial rather than concurrent:…, Render the validations as the offline half of the report in APP_FLOW §6. A…, validate_all_offline(), validate_offline(), _corrupted_sites_dir(), _iso_days_ago() (+16 more)

### Community 51 - "._refresh_table"
Cohesion: 0.18
Nodes (10): ApiError, readDetail(), request(), Window, wishlistIdentity, wishlistKey(), RefreshStart, ResultsResponse (+2 more)

### Community 52 - "FetchResult"
Cohesion: 0.15
Nodes (41): Lock, _sync_profiles(), Connection, Mirror site profiles into the sites table and return how many were written. The…, sync_to_db(), Any, A site's display name, with a badge when its profile is old enough to be worth…, Show what storage already knows, then go to the shops for the rest.… (+33 more)

### Community 53 - "conftest.py"
Cohesion: 0.33
Nodes (8): _fake_runner(), main(), _matching_product(), _profile(), Any, The backend playwright drives: the real app, with the shops stubbed out.…, Which catalogue product a typed query is about, by its leading words.…, A profile that passes schema validation and is never actually fetched.

### Community 54 - "Endpoint Schema Fields"
Cohesion: 0.22
Nodes (9): result_item, result_title, result_url, url_template, search, additionalProperties, description, required (+1 more)

### Community 55 - "apply_variant_rules"
Cohesion: 0.12
Nodes (25): extract_embedded_variants(), extract_jsonld_variants(), _flatten_jsonld(), Rung 1: read the page's JSON-LD as flat variant rows. A product that declares…, Turn one Product and everything under it into rows., Rung 3: read the JSON blob the page carries but does not display. Two shapes of…, One buyable size of one product, exactly as the page or feed states it. This is…, RawVariant (+17 more)

### Community 56 - "Request Schema Fields"
Cohesion: 0.04
Nodes (45): jsdom, motion, @playwright/test, react, react-dom, @testing-library/jest-dom, @testing-library/react, @testing-library/user-event (+37 more)

### Community 57 - "_FixtureFetcher"
Cohesion: 0.14
Nodes (19): _age_of(), live_query(), _path(), profile_age_days(), datetime, Profile staleness checks. Two modes: offline (against saved fixtures) and live…, A URL's path with no trailing slash, for comparing two spellings of one page., Every site that has a profile, sorted so reports read the same way twice. (+11 more)

### Community 58 - "setup_logging"
Cohesion: 0.07
Nodes (27): DOM, DOM.Iterable, e2e, ES2022, playwright.config.ts, src, tests, vite/client (+19 more)

### Community 59 - "_named_profile"
Cohesion: 0.17
Nodes (21): _close_browser(), _close_session_browser(), _fetch_curl_cffi(), _fetch_httpx(), _fetch_playwright(), _folded(), _launch_browser(), Any (+13 more)

### Community 60 - "_wait_for_table"
Cohesion: 0.22
Nodes (3): _FakeBrowser, _FakePage, Any

### Community 61 - "._apply_scan_event"
Cohesion: 0.24
Nodes (15): _close_handle(), _copy_bootstrapper(), _create_ready_event(), handoff_command(), _kernel32(), launch_installer(), Path, RuntimeError (+7 more)

### Community 62 - "snapshot_rows"
Cohesion: 0.21
Nodes (17): Run one site's profile against the real site. Same contract as offline mode: a…, validate_live(), _DeadSite, _FakeSite, _fixture_site(), M5's own criterion: when a profile stops agreeing with its site's real markup,…, A stand-in for one live site, answering the search page then the rest. Live…, A host that cannot be reached at all. (+9 more)

### Community 64 - "validate_live"
Cohesion: 0.11
Nodes (19): _balanced_value(), _embedded_documents(), extract_css_variants(), extract_endpoint_variants(), _loads_or_skip(), Any, Rung 2: read the variant list out of a platform's JSON response. `document` is…, Rung 4: read the rendered markup with selectors. Last resort.… (+11 more)

### Community 65 - "_named_profile"
Cohesion: 0.17
Nodes (15): CacheKey, CandidateFilter, _candidates_to_open(), Path, Narrow the search results down to the pages worth a request. The first one…, Run every site against one query, all at once, and report each separately.…, Run one matcher-aware spelling sequence for every site in parallel., run_sites() (+7 more)

### Community 67 - "extract_embedded_variants"
Cohesion: 0.10
Nodes (22): Screen, ParfumFinderApp, Path, The Textual App root. Handles screen navigation and is the app's default entry…, Root app: pushes the search screen on mount., SystemCommand, _counting_runner(), _days_ago() (+14 more)

### Community 68 - "JsonLdProduct"
Cohesion: 0.24
Nodes (10): check_enabled(), check_for_update(), _installer_asset(), _no_update(), Any, ReleaseInfo, No network is not an error the user has to be told about. The check runs…, test_check_reports_nothing_when_the_release_is_the_installed_one() (+2 more)

### Community 71 - ".__init__"
Cohesion: 0.16
Nodes (9): BaseHTTPRequestHandler, _Handler, _playwright_usable(), MonkeyPatch, Shared pytest fixtures. A local HTTP server used by fetch/probe tests: real…, Whether the playwright rung can actually run here, binary included. Checking…, Record every delay the engine asks for instead of serving it. Waiting for real…, server_url() (+1 more)

### Community 72 - "write_snapshots"
Cohesion: 0.07
Nodes (52): _read_wishlist(), _record_search(), basket_lines(), basket_prices(), basket_sites(), cached_prices(), _calendar_months_before(), connect() (+44 more)

### Community 73 - "_css_variant"
Cohesion: 0.24
Nodes (17): probe(), Fetch `url` with every strategy and report diagnostics for each. timeout_s…, MonkeyPatch, parametrize, requires_playwright, Tests for parfum_finder.probe. probe() always tries all three strategies --…, test_probe_counts_jsonld_product_and_platform_signature(), test_probe_counts_product_across_jsonld_root_shapes() (+9 more)

### Community 74 - "ConfirmDialog.tsx"
Cohesion: 0.53
Nodes (4): FormData, Headers, Method, Strategy

### Community 75 - "ResultRow"
Cohesion: 0.11
Nodes (30): _as_str(), _build_offer(), _build_product(), _coerce_in_stock(), _collect_offers(), _collect_products(), _collect_variants(), _has_type() (+22 more)

### Community 76 - "SplitPlan"
Cohesion: 0.24
Nodes (11): formatAge(), formatMl(), formatPerMl(), formatPrice(), formatPriceWhole(), daysSince(), SearchScreen(), splitParts() (+3 more)

### Community 77 - "_collect_products"
Cohesion: 0.13
Nodes (21): Write a whole scan at once and return how many prices were recorded. Every row…, write_snapshots(), A model word must not become the brand in the database. Different houses can…, A price nobody will scan again may not be offered as a result. Refreshing is…, The drop happens here so no caller can forget it. Both the CLI and the screen…, A slow site must not spread one reading across several timestamps. Rows written…, The number reported is what landed in the history, not what was offered., Half a site's sizes updated is worse than none of them. The basket compares… (+13 more)

### Community 78 - "_fake_runner"
Cohesion: 0.28
Nodes (12): arguments_t, BOOL, DWORD, HINSTANCE, append_log(), argument_value(), launch_setup(), parse_arguments() (+4 more)

### Community 79 - "AddButton.tsx"
Cohesion: 0.22
Nodes (9): price_history(), Row, Return one variant's past readings, newest first, capped at limit. Empty for a…, The trend panel reads row 0 as the latest reading, so order is the point. A…, No history yet is a normal state for a variant, not an error to raise on., The identity a real scan writes must be the identity these lookups accept.…, test_a_scanned_perfume_can_be_read_back_by_basket_and_history(), test_price_history_is_empty_for_an_unknown_variant() (+1 more)

### Community 80 - "_ask_chooser"
Cohesion: 0.26
Nodes (7): _FixtureFetcher, FormData, Headers, Method, Strategy, Serves one site's saved capture in place of the network. Only three kinds of…, The one real result card that led to the captured product page. Cut out of the…

### Community 81 - "run_sites"
Cohesion: 0.08
Nodes (61): Pressed, ScanEvent, BasketRefreshEvent and viewmodel dataclasses as JSON-safe dicts.…, _paced_fetcher(), Protocol, One site's pacing state, for as long as whoever holds it says. The gate and the…, Wrap a fetcher so one site's requests go out one at a time, spaced apart. The…, What a caller needs of run_site, as a type callers can stand a fake in for. A…, SitePace (+53 more)

### Community 82 - "Node"
Cohesion: 0.41
Nodes (11): _bootstrapper(), _close_handle(), _command(), _kernel32(), Any, Path, Windows integration checks for the native update helper., _ready_event() (+3 more)

### Community 83 - "test_one_query_finding_two_bottles_gets_two_blocks"
Cohesion: 0.14
Nodes (6): Changed, Close out a submit that named no perfume anyone could look for., Show what storage already knows, then go to the shops for the rest.…, Say a perfume came off the record instead of off the shops. Without this the…, Empty the table for a new scan. The columns are the same every time now, so…, Submitted

### Community 84 - "select_field"
Cohesion: 0.17
Nodes (8): api, SiteSummary, compile(), DEFAULT_CONFIG, FakeServer, installFakeServer(), searchStart(), SITES

### Community 85 - "enum"
Cohesion: 0.26
Nodes (12): encode_basket_report(), encode_result_row(), encode_scan_event(), encode_site_scenario(), _encode_split_leg(), encode_split_plan(), Any, BasketReport (+4 more)

### Community 86 - "SiteValidation"
Cohesion: 0.25
Nodes (7): _age_line(), format_live_report(), Every check run against one site's profile, in the order they ran. Checks stop…, Whether the profile is old enough to be worth re-discovering., The age note for one site, or None when its age is unremarkable. A profile…, Render offline and live results side by side, as APP_FLOW §6 shows them. Both…, SiteValidation

### Community 87 - "helpers.ts"
Cohesion: 0.23
Nodes (15): addFirstRow(), authToken(), BrowserPerformanceSnapshot, clearBasket(), clearWishlist(), openApp(), PageDiagnostics, performanceSnapshot() (+7 more)

### Community 88 - "BookmarkIcon.tsx"
Cohesion: 0.38
Nodes (3): BookmarkIcon(), BookmarkIconProps, variants

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
Cohesion: 0.37
Nodes (12): _freeze(), MonkeyPatch, Path, Tests for parfum_finder.paths: frozen vs. source path resolution.…, A source run has nothing to seed: resource_dir and user_data_dir are already…, test_ensure_user_data_is_a_noop_when_not_frozen(), test_ensure_user_data_never_overwrites_an_edited_file(), test_ensure_user_data_seeds_sites_platforms_and_hooks() (+4 more)

### Community 94 - "Arayüz testleri"
Cohesion: 0.25
Nodes (7): Arayüz testleri, Geçiş ve büyük istek listesi regresyonları, jsdom katmanı (`tests/`), Ne test edilmiyor, Tarayıcı katmanı (`e2e/`), Timer ve observer regresyonları, Windows WebView2 el ile kontrol listesi

### Community 95 - "test_normalize.py"
Cohesion: 0.50
Nodes (3): Answer, Q: Which files own the navigation indicator, shared basket data, and wishlist lazy details?, Source Nodes

### Community 96 - "test_updater.py"
Cohesion: 0.24
Nodes (15): fetch_latest_release(), En son yayımlanmış sürüm, ya da ulaşılamadıysa None. /releases/latest…, _enable_checks(), _patch_get(), MonkeyPatch, Tests for parfum_finder.updater: the version compare, the release read, and the…, The .exe is what gets downloaded, whatever else is attached. Releases carry…, _release_payload() (+7 more)

### Community 97 - "product_label"
Cohesion: 0.15
Nodes (13): display_title(), product_label(), Hide catalog decorations while preserving the shop title for storage., Reduce a site's own title to the product it is about, spelled one way. What…, test_a_clone_is_labelled_by_the_bottle_it_is_and_not_what_it_imitates(), test_a_longer_named_bottle_does_not_join_the_shorter_ones_block(), test_a_title_with_no_product_words_left_has_no_label(), test_catalog_decorations_are_hidden_only_with_a_safe_boundary() (+5 more)

### Community 98 - "select_field"
Cohesion: 0.25
Nodes (11): _css_variant(), _parse_selector(), Node, Read one variant's fields out of its container node., Run one "<css>::text" / "<css>::attr(name)" selector inside a node. The node…, Run one "<css>::text" / "<css>::attr(name)" selector, reading every match. Same…, Split a "<css>::text" / "<css>::attr(name)" selector into its two parts., Read the attribute or text of one already-selected node, or None. (+3 more)

### Community 99 - "SiteValidation"
Cohesion: 0.25
Nodes (8): exclude_keywords, max_size_ml, size_from, size_pattern, variant_rules, additionalProperties, required, type

### Community 102 - "enum"
Cohesion: 0.33
Nodes (6): css, embedded_json, endpoint, jsonld, enum, extraction

### Community 103 - "Static"
Cohesion: 0.40
Nodes (3): ComposeResult, ComposeResult, Static

### Community 104 - "ws.test.ts"
Cohesion: 0.67
Nodes (4): authToken(), refusalReason(), streamUrl(), useEventStream()

### Community 105 - "search_spellings"
Cohesion: 0.29
Nodes (7): _fold_search_separators(), One search line, then the same line with the brand written the other ways. The…, Turn punctuation that commonly splits catalog tokens into spaces., search_spellings(), test_a_brand_nobody_abbreviates_is_asked_for_once(), test_brand_aliases_each_receive_one_separator_folded_attempt_in_order(), test_the_typed_spelling_is_asked_first_and_the_rest_only_follow()

### Community 106 - "Q: In the Windows application, when I release a new version, I click the ‘Update’ button to install the update, and the new update is downloaded. However, the application then closes and the installer does not launch. By pressing Win + R and then running the downloaded installer from the ‘%temp%’ directory, I am able to install the update without any issues. So I assume there is no block from Windows. I’m still experiencing this issue even though I’ve added it to the whitelist via Windows Defender. Could you please check if there’s an error in the code?"
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: In the Windows application, when I release a new version, I click the ‘Update’ button to install the update, and the new update is downloaded. However, the application then closes and the installer does not launch. By pressing Win + R and then running the downloaded installer from the ‘%temp%’ directory, I am able to install the update without any issues. So I assume there is no block from Windows. I’m still experiencing this issue even though I’ve added it to the whitelist via Windows Defender. Could you please check if there’s an error in the code?, Source Nodes

### Community 108 - "apply_variant_rules"
Cohesion: 0.24
Nodes (14): apply_variant_rules(), Turn raw size rows into decant variants, dropping what is not a decant. Three…, Any, _row(), test_a_keyword_in_the_size_label_excludes_the_row_too(), test_a_literal_zero_price_reads_as_no_price_not_a_free_perfume(), test_a_size_at_the_threshold_is_a_bottle_whatever_it_calls_itself(), test_a_size_that_cannot_be_read_is_dropped() (+6 more)

### Community 111 - "ParfumFinderApp"
Cohesion: 0.50
Nodes (3): The template this site's profile would be based on, if any., Which of the matching templates gets applied, or None for none of them. One…, _resolve_platform()

## Knowledge Gaps
- **260 isolated node(s):** `Answer`, `Source Nodes`, `jsdom katmanı (`tests/`)`, `Tarayıcı katmanı (`e2e/`)`, `Ne test edilmiyor` (+255 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **9 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Work-memory lessons

**Preferred sources** — corroborated by past sessions; start here.
- `price_history()` (2× useful, score=1.905493535)
- `BasketScreen()` (2× useful, score=1.905493535) _(code changed — re-verify)_

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `BasketScreen` connect `HTTP/Browser Fetching` to `TUI App & Screens`, `Site Profiles & Templates`, `Title Matcher`, `Static`, `write_snapshots`, `Basket Optimizer Core`, `Product Extraction`, `run_sites`?**
  _High betweenness centrality (0.035) - this node is a cross-community bridge._
- **Why does `SearchScreen` connect `Title Matcher` to `extract_embedded_variants`, `HTTP/Browser Fetching`, `TUI App Shell`, `Static`, `write_snapshots`, `Product Extraction`, `run_sites`, `Search TUI Screen`, `test_one_query_finding_two_bottles_gets_two_blocks`, `FetchResult`, `Discovery CLI Reporting`?**
  _High betweenness centrality (0.030) - this node is a cross-community bridge._
- **Why does `PerfumeQuery` connect `TUI App Shell` to `_ResultRow`, `Title Matcher`, `CLI Entry Points`, `Decant Variant Rules`, `_NoRootParser`, `Product Extraction`, `run_sites`, `_RecordingFetcher`, `Search TUI Screen`, `FetchResult`, `Discovery CLI Reporting`, `Live Profile Validation`?**
  _High betweenness centrality (0.030) - this node is a cross-community bridge._
- **Are the 19 inferred relationships involving `PerfumeQuery` (e.g. with `BasketPriceExcluded` and `BasketRefreshFinished`) actually correct?**
  _`PerfumeQuery` has 19 INFERRED edges - model-reasoned connections that need verification._
- **Are the 13 inferred relationships involving `SearchScreen` (e.g. with `ParfumFinderApp` and `SiteRunner`) actually correct?**
  _`SearchScreen` has 13 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Answer`, `Source Nodes`, `jsdom katmanı (`tests/`)` to the rest of the system?**
  _260 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `TUI App & Screens` be split into smaller, more focused modules?**
  _Cohesion score 0.09337992622791691 - nodes in this community are weakly interconnected._