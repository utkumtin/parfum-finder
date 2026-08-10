# Graph Report - parfum-finder  (2026-08-09)

## Corpus Check
- 65 files · ~228,490 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1710 nodes · 4500 edges · 80 communities (68 shown, 12 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 167 edges (avg confidence: 0.58)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `91411cdb`
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
- Variant Extraction Ladder
- Fetch Strategy Probing
- Platform Field Mapping
- Shipping Config Schema
- Discovery Report Model
- TUI Confirm Dialog
- TUI App Shell
- Fetch Backends
- HTTP Request Schema
- Fixture Fetcher (Tests)
- Validation Reporting
- Decant Variant Rules
- Multi-Site Search Run
- Offline Validation Fixtures
- Basket Domain Logic
- Search Screen Rows
- test_engine.py
- Profile Age Checks
- extract_endpoint_variants
- Snapshot Row Semantics
- conftest.py
- Endpoint Schema Fields
- _named_profile
- Request Schema Fields
- _write_hook
- Snapshot Row Building
- Variant Field Types
- Fetch Strategy Selection
- Price History
- Extraction Layer Enum
- validate_live
- _FakePage
- .__call__
- Endpoint Variant Extraction
- exclude_keywords
- format_age
- Variant Pattern A
- Project Root
- Decimal
- CacheKey
- CandidateFilter
- ComposeResult
- Protocol
- Row
- VariantsRead
- MonkeyPatch
- Runner

## God Nodes (most connected - your core abstractions)
1. `search_site()` - 64 edges
2. `discover()` - 56 edges
3. `_profile()` - 54 edges
4. `PerfumeQuery` - 50 edges
5. `SearchScreen` - 50 edges
6. `BasketScreen` - 45 edges
7. `_attempt()` - 42 edges
8. `_fake_probe()` - 42 edges
9. `_app()` - 41 edges
10. `match_title()` - 40 edges

## Surprising Connections (you probably didn't know these)
- `Shipping Non-linearity Rationale (why cheapest-per-item is wrong)` --semantically_similar_to--> `sites/ Site Profile Directory`  [INFERRED] [semantically similar]
  ARCHITECTURE.md → sites/README.md
- `Variant Pattern B (dropdown + AJAX price)` --semantically_similar_to--> `Variant Selector Detector Fix (WooCommerce 'variation' vs 'variant')`  [INFERRED] [semantically similar]
  ARCHITECTURE.md → docs/discovery-report.md
- `test_the_low_confidence_dialog_can_be_answered_with_the_keyboard_alone()` --indirect_call--> `ConfirmScreen`  [INFERRED]
  tests/test_tui.py → src/parfum_finder/tui/search_screen.py
- `test_the_low_confidence_dialog_shows_the_keys_it_answers_to()` --indirect_call--> `ConfirmScreen`  [INFERRED]
  tests/test_tui.py → src/parfum_finder/tui/search_screen.py
- `test_s_opens_the_basket_and_escape_comes_back_to_the_results()` --indirect_call--> `SearchScreen`  [INFERRED]
  tests/test_basket_screen.py → src/parfum_finder/tui/search_screen.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Sites Implementing Variant Pattern C (embedded JSON)** — docs_discovery_report_venco_site, docs_discovery_report_decantall_site, docs_discovery_report_luxurydekant_site, docs_discovery_report_ruxangroup_site, architecture_md_variant_pattern_c [EXTRACTED 1.00]
- **İdeasoft Platform Sites and Endpoint** — docs_discovery_report_dekantparfum_site, docs_discovery_report_dekantdoktoru_site, docs_discovery_report_ideasoft_related_options_endpoint, platforms_readme_ideasoft_json [EXTRACTED 1.00]
- **discover Command Output Artifacts (profile + fixtures + CI validation)** — architecture_md_discover_flow, sites_readme_sites_dir, fixtures_readme_fixtures_dir, github_workflows_ci_validate_profiles_step, architecture_md_validate_command [INFERRED 0.85]

## Communities (80 total, 12 thin omitted)

### Community 0 - "TUI App & Screens"
Cohesion: 0.11
Nodes (88): The Textual-based terminal UI: search and basket screens., _app(), _basket(), _cells(), _days_ago(), _leg(), _ok(), _open_basket() (+80 more)

### Community 1 - "Site Profiles & Templates"
Cohesion: 0.06
Nodes (83): _check_hook_kinds(), deep_merge(), _load_json(), load_platform_template(), load_platform_templates(), load_site_hooks(), load_site_profile(), Any (+75 more)

### Community 2 - "Title Matcher"
Cohesion: 0.10
Nodes (50): Match, match_title(), parse_query(), PerfumeQuery, The perfume being looked for, split into its three identity parts.      `concent, One site title judged against the query.      `concentration` is what the title, Split one typed line, "Dior Sauvage EDP", into the three identity parts.      Th, Judge one site title against a query, or None if it is not that perfume.      No (+42 more)

### Community 3 - "HTTP/Browser Fetching"
Cohesion: 0.14
Nodes (27): browser_session(), fetch(), Fetch one URL using exactly the given strategy.      `method`/`data` exist for t, Yield a fetcher that keeps one browser for every playwright page it reads., _fake_launch(), MonkeyPatch, Tests for parfum_finder.fetch.  httpx and curl_cffi are exercised against a real, Stand in for the browser process, and count how many were started. (+19 more)

### Community 4 - "Search/Basket Domain Models"
Cohesion: 0.10
Nodes (86): LogCaptureFixture, MonkeyPatch, ParfumFinderApp, Runner, _app(), _basket_count(), _named_result(), _ok_result() (+78 more)

### Community 5 - "Search Engine per Site"
Cohesion: 0.14
Nodes (8): _Change, BasketScreen, Any, Path, The basket: the list on top, one scenario per site underneath., The three inputs basket.py's pure functions score: items, prices, shipping., _remove(), _set_qty()

### Community 6 - "Platform Discovery Flow"
Cohesion: 0.15
Nodes (59): PlatformChooser, _ask_chooser(), discover(), Put the question only when there is one, and hold the answer to it.      An answ, Measure the strategies a site needs, then read its JSON-LD with the winner., _attempt(), _fake_probe(), Any (+51 more)

### Community 7 - "CLI Entry Points"
Cohesion: 0.13
Nodes (43): CaptureFixture, ask_which_platform(), main(), Path, Scan every site for the perfumes named, store what came back, print it.      One, Ask at the terminal which of several matching templates to apply.      Asked whi, run_search(), A multi-site price and stock comparison tool for perfume decants.  Includes a sh (+35 more)

### Community 8 - "Architecture Rationale Docs"
Cohesion: 0.05
Nodes (53): basket Subset Enumeration + Local Improvement Algorithm, basket Optimizer (optimize function), Clone/Original Distinction (KLON ← <orijinal>), discover Discovery Flow, engine Concurrency Model (parallel sites, serial within site), Extraction Ladder (jsonld/endpoint/embedded/css), Fail-loud / status=suspect policy, hooks/<id>.py Escape Hatch (+45 more)

### Community 9 - "Search Engine Core"
Cohesion: 0.10
Nodes (39): _fetch_page(), _headers(), _is_excluded(), _paced_fetcher(), _parse_endpoint_document(), ProductCandidate, Any, Decimal (+31 more)

### Community 10 - "Basket Optimizer Core"
Cohesion: 0.14
Nodes (36): Collection, Prices, BasketItem, optimize(), Basket scenario evaluation. A pure function, no network access, no sqlite.  Inpu, Score one site against the basket, or against a subset of it.      `item_ids` is, Score every enabled site against the whole basket and sort the results.      Sit, Search for the cheapest way to split the basket across several sites.      Retur (+28 more)

### Community 11 - "Basket Store & Pricing"
Cohesion: 0.08
Nodes (52): add_basket_item(), basket_prices(), Add a size of a perfume to the basket, and return the basket_item_id.      The p, Return the basket price matrix: one row per (line, site) that has a price., conn(), Connection, Path, Tests for parfum_finder.store: the timestamp helper and the schema.  The one har (+44 more)

### Community 12 - "JSON-LD Product Extraction"
Cohesion: 0.15
Nodes (30): extract_jsonld_products(), Read every JSON-LD Product declared on the page, in document order.      A block, _one_product_html(), Tests for parfum_finder.extract.  Every case here is a shape a real store actual, Wrap a JSON-LD product body in a page, for the one-field-at-a-time cases., test_a_broken_block_does_not_lose_the_valid_one(), test_availability_spellings_all_land_in_the_same_bucket(), test_boolean_values_are_never_read_as_price_or_text() (+22 more)

### Community 13 - "Basket TUI Screen"
Cohesion: 0.11
Nodes (27): _canonical(), _covers(), _ends_with(), _index_of(), _match_text(), product_label(), Perfume matching: brand and concentration are mandatory; fuzzy matching only app, Reduce a site's own title to the product it is about, spelled one way.      What (+19 more)

### Community 14 - "Platform Schema"
Cohesion: 0.06
Nodes (31): any, defaults, fingerprint, additionalProperties, items, minItems, type, description (+23 more)

### Community 15 - "Product Extraction"
Cohesion: 0.11
Nodes (28): _as_str(), _build_offer(), _build_product(), _coerce_in_stock(), _collect_offers(), _collect_products(), _collect_variants(), _has_type() (+20 more)

### Community 16 - "Schema Field Patterns"
Cohesion: 0.07
Nodes (30): format, pattern, type, pattern, type, default, type, pattern (+22 more)

### Community 17 - "Offline Profile Validation"
Cohesion: 0.10
Nodes (26): HTMLParser, Fetcher, Protocol, Anything that can stand in for `fetch`.      Offline profile validation runs the, Check, _count_result_cards(), _first_result_url(), _LayerUnavailable (+18 more)

### Community 18 - "Playwright Errors"
Cohesion: 0.15
Nodes (21): _attempt(), _count_jsonld(), _count_product_objects(), _detect_platforms(), format_report(), _label_platform(), _one_line(), ProbeAttempt (+13 more)

### Community 19 - "Search TUI Screen"
Cohesion: 0.08
Nodes (14): Decimal, HeaderSelected, Row, RowSelected, The search screen: a progress bar while scanning, one grouped table after.  Colu, One priced size, exactly as the table shows it and as a keypress needs it., The initial screen: search bar, streaming results table, notices, footer., Empty the table for a new scan.          The columns are the same every time now (+6 more)

### Community 20 - "Snapshot Writing"
Cohesion: 0.11
Nodes (31): One priced size of one perfume on one site, ready to be written.      The perfum, SnapshotRow, The drop happens here so no caller can forget it.      Both the CLI and the scre, One call has to leave a row the search table can read straight off.      The cal, The old price has to survive, and it must not become a second variant.      Appe, first_seen is what says how long a shop has carried a size., The title and URL are information, not identity.      A shop that rewords a list, EDT and EDP are different products at different prices.      Folding them into o (+23 more)

### Community 21 - "Candidate Filtering"
Cohesion: 0.14
Nodes (12): CacheKey, CandidateFilter, Fetcher, SnapshotRow, _listing_filter(), Any, SiteResult, Decide, from a search result's own title, whether to open its page. (+4 more)

### Community 22 - "Basket Site Scenarios"
Cohesion: 0.11
Nodes (26): BasketReport, One site's share of a split basket: what to buy there and what it costs.      `s, The cheapest basket split the search found. A heuristic, not a proof.      Every, What it would cost to buy some or all of the basket from one site.      `covered, Every site's single-site scenario, split by whether it covers everything.      A, SiteScenario, SplitLeg, SplitPlan (+18 more)

### Community 23 - "Price/Size Normalization"
Cohesion: 0.15
Nodes (21): _classify_single_separator(), format_ml(), format_price(), _parse_number(), parse_price(), parse_size_ml(), Decimal, Number parsing and formatting for prices and volumes, plus text folding.  This i (+13 more)

### Community 24 - "JSON Schema Primitives"
Cohesion: 0.12
Nodes (23): null, string, properties, type, type, type, additionalProperties, properties (+15 more)

### Community 25 - "SQLite Store"
Cohesion: 0.12
Nodes (29): One decant size of one product, in the units the database stores.      Tenths of, Variant, basket_lines(), basket_sites(), BasketSite, now_iso(), _perfume_id(), _product_id() (+21 more)

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
Nodes (17): collect_prices(), _format_product(), _format_stock(), _format_trial(), _has_exact_price(), PageTrial, Decimal, One page fetched with the chosen strategy and read for JSON-LD.      A fetch tha (+9 more)

### Community 30 - "Store Timestamp Tests"
Cohesion: 0.15
Nodes (21): _close_browser(), _fetch_curl_cffi(), _fetch_httpx(), _fetch_playwright(), _launch_browser(), PlaywrightNoResponse, PlaywrightNotInstalled, Any (+13 more)

### Community 31 - "Live Profile Validation"
Cohesion: 0.19
Nodes (28): format_report(), Check one site's profile against that site's saved fixtures.      Never raises f, Validate every site, or just the ones named.      Serial rather than concurrent:, Render the validations as the offline half of the report in APP_FLOW §6.      A, validate_all_offline(), validate_offline(), _corrupted_sites_dir(), _iso_days_ago() (+20 more)

### Community 32 - "Variant Extraction Fields"
Cohesion: 0.12
Nodes (16): attribute, script, type, additionalProperties, allOf, description, properties, type (+8 more)

### Community 33 - "Variant Extraction Ladder"
Cohesion: 0.11
Nodes (20): _check_empty_search(), _check_variant_control(), ExtractionFailed, RuntimeError, A page answered but gave up nothing, where something was expected.      This is, Fail when a search yielded no rows off a page that plainly lists products., Fail when the page's size picker offers more sizes than the layer read.      The, _NoRootParser (+12 more)

### Community 34 - "Fetch Strategy Probing"
Cohesion: 0.21
Nodes (15): probe(), Fetch `url` with every strategy and report diagnostics for each.      timeout_s, MonkeyPatch, Tests for parfum_finder.probe.  probe() always tries all three strategies -- the, test_probe_counts_jsonld_product_and_platform_signature(), test_probe_counts_product_across_jsonld_root_shapes(), test_probe_counts_product_markup_without_any_jsonld(), test_probe_counts_products_nested_below_the_top_level() (+7 more)

### Community 35 - "Platform Field Mapping"
Cohesion: 0.18
Nodes (11): field_map, product_json, source, variants_path, required, additionalProperties, allOf, description (+3 more)

### Community 36 - "Shipping Config Schema"
Cohesion: 0.12
Nodes (16): free_shipping_threshold_kurus, integer, shipping_cost_kurus, minimum, type, type, free_shipping_threshold_kurus, notes (+8 more)

### Community 37 - "Discovery Report Model"
Cohesion: 0.08
Nodes (39): _choose_strategy(), DiscoveryReport, FieldConfidence, _flatten_defaults(), _format_choice(), _format_confidence(), _format_defaults(), _format_fingerprint() (+31 more)

### Community 38 - "TUI Confirm Dialog"
Cohesion: 0.11
Nodes (20): _candidates_to_open(), CandidateFilter, Run one query against one site and read every hit's sizes.      Everything site-, Narrow the search results down to the pages worth a request.      The first one, search_site(), test_a_full_bottle_next_to_a_decant_does_not_sink_the_site(), test_a_full_bottle_page_is_not_checked_against_the_picker(), test_a_post_endpoint_asks_once_per_size_option_off_the_page() (+12 more)

### Community 39 - "TUI App Shell"
Cohesion: 0.18
Nodes (9): Protocol, Screen, ParfumFinderApp, Path, The Textual App root. Handles screen navigation and is the app's default entry p, Root app: pushes the search screen on mount., What this screen needs of engine.run_site.      A protocol rather than a plain c, SiteRunner (+1 more)

### Community 40 - "Fetch Backends"
Cohesion: 0.14
Nodes (14): curl_cffi, httpx, playwright, result_item, result_title, result_url, strategy, url_template (+6 more)

### Community 41 - "HTTP Request Schema"
Cohesion: 0.14
Nodes (14): GET, POST, properties, default, enum, type, type, type (+6 more)

### Community 42 - "Fixture Fetcher (Tests)"
Cohesion: 0.15
Nodes (18): _age_of(), live_query(), _path(), profile_age_days(), datetime, Profile staleness checks. Two modes: offline (against saved fixtures) and live (, A URL's path with no trailing slash, for comparing two spellings of one page., Every site that has a profile, sorted so reports read the same way twice. (+10 more)

### Community 43 - "Validation Reporting"
Cohesion: 0.15
Nodes (18): extract_embedded_variants(), extract_jsonld_variants(), _flatten_jsonld(), Rung 1: read the page's JSON-LD as flat variant rows.      A product that declar, Turn one Product and everything under it into rows., Rung 3: read the JSON blob the page carries but does not display.      Two shape, _fixture(), Read a captured product page. (+10 more)

### Community 44 - "Decant Variant Rules"
Cohesion: 0.20
Nodes (9): Changed, Split one typed line into the perfumes it asks for, on " - ".      The separator, split_queries(), test_a_hyphen_inside_a_brand_name_does_not_split_the_search(), test_a_line_naming_three_perfumes_is_read_as_three_searches(), test_a_piece_that_names_no_perfume_survives_to_be_complained_about(), test_a_stray_separator_is_not_worth_failing_over(), test_one_perfume_is_still_one_search() (+1 more)

### Community 45 - "Multi-Site Search Run"
Cohesion: 0.22
Nodes (14): A candidate together with the decant sizes its product page offers., What one site had to say about one query, and how much to trust it.      Four st, SearchHit, SiteResult, Turn one site's hits into the rows write_snapshots is ready to store.      Share, snapshot_rows(), A shop's imitation must not be stored as the perfume it imitates.      The clone, Another house's bottle on the same results page must not enter this history. (+6 more)

### Community 46 - "Offline Validation Fixtures"
Cohesion: 0.14
Nodes (7): ComposeResult, Pressed, ComposeResult, ConfirmScreen, Path, Asks before a low-confidence match is written to the basket.      The two answer, Static

### Community 47 - "Basket Domain Logic"
Cohesion: 0.16
Nodes (24): Run one site and classify what came back instead of raising.      It is also whe, run_site(), _counting_fetcher(), _profile(), Exception, Answer each call with the next canned result, then repeat the last one., A minimal working profile, with the fields a case cares about swapped in., test_a_dead_link_selector_is_suspect_not_empty() (+16 more)

### Community 49 - "test_engine.py"
Cohesion: 0.31
Nodes (14): apply_variant_rules(), Turn raw size rows into decant variants, dropping what is not a decant.      Thr, Tests for the profile-driven search in parfum_finder.engine.  What these defend, _row(), test_a_keyword_in_the_size_label_excludes_the_row_too(), test_a_literal_zero_price_reads_as_no_price_not_a_free_perfume(), test_a_size_at_the_threshold_is_a_bottle_whatever_it_calls_itself(), test_a_size_that_cannot_be_read_is_dropped() (+6 more)

### Community 50 - "Profile Age Checks"
Cohesion: 0.25
Nodes (7): _age_line(), format_live_report(), Every check run against one site's profile, in the order they ran.      Checks s, Whether the profile is old enough to be worth re-discovering., The age note for one site, or None when its age is unremarkable.      A profile, Render offline and live results side by side, as APP_FLOW §6 shows them.      Bo, SiteValidation

### Community 51 - "extract_endpoint_variants"
Cohesion: 0.14
Nodes (15): _balanced_value(), _embedded_documents(), extract_endpoint_variants(), _loads_or_skip(), Any, Rung 2: read the variant list out of a platform's JSON response.      `document`, Yield every JSON document the page hides, in document order., Parse `text` as JSON, yielding nothing when it isn't JSON.      Pages are full o (+7 more)

### Community 52 - "Snapshot Row Semantics"
Cohesion: 0.23
Nodes (9): FetchResult, One fetched page, uniform regardless of which strategy produced it., _FixtureFetcher, FormData, Headers, Method, Strategy, Serves one site's saved capture in place of the network.      Only three kinds o (+1 more)

### Community 53 - "conftest.py"
Cohesion: 0.24
Nodes (6): BaseHTTPRequestHandler, _Handler, _playwright_usable(), Shared pytest fixtures.  A local HTTP server used by fetch/probe tests: real req, Whether the playwright rung can actually run here, binary included.      Checkin, server_url()

### Community 54 - "Endpoint Schema Fields"
Cohesion: 0.22
Nodes (9): result_item, result_title, result_url, url_template, search, additionalProperties, description, required (+1 more)

### Community 55 - "_named_profile"
Cohesion: 0.24
Nodes (11): _named_profile(), Any, The real fetcher, with a list of every URL it was asked for., A profile whose search page lists two houses' bottles, as shops do., test_a_broken_profile_is_still_suspect_when_no_title_looked_right(), test_a_listing_from_another_house_costs_no_product_request(), test_a_scan_says_how_many_listings_it_skipped(), test_one_product_listed_under_two_searches_is_read_once() (+3 more)

### Community 56 - "Request Schema Fields"
Cohesion: 0.25
Nodes (8): type, additionalProperties, type, body, request_headers, additionalProperties, description, type

### Community 57 - "_write_hook"
Cohesion: 0.31
Nodes (11): Path, Give the test profile's site id a hook file. The id is what binds them., test_a_before_search_that_returns_no_query_is_refused(), test_a_broken_hook_is_an_error_not_a_silent_empty(), test_a_hook_that_reads_nothing_is_named_as_the_culprit(), test_a_site_with_no_hook_file_is_driven_by_its_profile_alone(), test_after_search_can_drop_a_result_the_selectors_could_not(), test_before_search_rewrites_the_query_that_is_actually_sent() (+3 more)

### Community 58 - "Snapshot Row Building"
Cohesion: 0.12
Nodes (23): _listing_filter(), Any, CandidateFilter, Connection, Command-line entry point.  Subcommands will be added incrementally as the projec, Scan every perfume against every site and print each site as it lands.      One, Decide, from a search result's own title, whether to open its page., Write one site's rows in a transaction of its own.      Per site rather than per (+15 more)

### Community 59 - "Variant Field Types"
Cohesion: 0.20
Nodes (10): CacheKey, Path, VariantsRead, Run every site against one query, all at once, and report each separately., run_sites(), test_a_dead_site_does_not_take_the_others_down(), test_a_profile_that_breaks_on_setup_is_contained_too(), test_no_sites_is_an_empty_run_not_a_crash() (+2 more)

### Community 60 - "Fetch Strategy Selection"
Cohesion: 0.17
Nodes (15): Node, _css_variant(), extract_css_variants(), _parse_selector(), Rung 4: read the rendered markup with selectors. Last resort.      `config["vari, Read one variant's fields out of its container node., Run one "<css>::text" / "<css>::attr(name)" selector inside a node.      The nod, Run one "<css>::text" / "<css>::attr(name)" selector, reading every match. (+7 more)

### Community 61 - "Price History"
Cohesion: 0.40
Nodes (5): price_history(), Row, Return one variant's past readings, newest first, capped at limit.      Empty fo, No history yet is a normal state for a variant, not an error to raise on., test_price_history_is_empty_for_an_unknown_variant()

### Community 62 - "Extraction Layer Enum"
Cohesion: 0.33
Nodes (6): css, embedded_json, endpoint, jsonld, enum, extraction

### Community 63 - "validate_live"
Cohesion: 0.27
Nodes (9): Run one site's profile against the real site.      Same contract as offline mode, validate_live(), _FakeSite, _fixture_site(), A stand-in for one live site, answering the search page then the rest.      Live, test_a_broken_layer_reports_which_other_layer_could_take_over(), test_a_working_profile_passes_against_a_site_that_still_answers(), test_zero_results_on_a_full_page_blames_the_result_selector() (+1 more)

### Community 64 - "_FakePage"
Cohesion: 0.22
Nodes (3): _FakeBrowser, _FakePage, Any

### Community 65 - ".__call__"
Cohesion: 0.31
Nodes (7): _DeadSite, FormData, Headers, Method, Strategy, A host that cannot be reached at all., test_an_unreachable_site_is_not_reported_as_a_broken_profile()

### Community 66 - "Endpoint Variant Extraction"
Cohesion: 0.29
Nodes (7): in_stock, price, size_raw, additionalProperties, required, type, field_map

### Community 67 - "exclude_keywords"
Cohesion: 0.29
Nodes (7): items, type, type, items, type, exclude_keywords, needs_review

### Community 68 - "format_age"
Cohesion: 0.50
Nodes (4): format_age(), Turn a price age in days into the words the age column shows., The age column exists to be glanced at, so it is phrased, not printed., test_format_age_reads_as_words_not_a_timestamp()

## Knowledge Gaps
- **152 isolated node(s):** `parfum-finder`, `$schema`, `$id`, `title`, `description` (+147 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **12 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `SearchScreen` connect `Search TUI Screen` to `TUI App & Screens`, `Title Matcher`, `TUI App Shell`, `Decant Variant Rules`, `Offline Validation Fixtures`, `Candidate Filtering`?**
  _High betweenness centrality (0.048) - this node is a cross-community bridge._
- **Why does `PerfumeQuery` connect `Title Matcher` to `Search Engine per Site`, `TUI App Shell`, `Multi-Site Search Run`, `Basket TUI Screen`, `Offline Validation Fixtures`, `Search TUI Screen`, `Snapshot Writing`, `Candidate Filtering`, `Basket Site Scenarios`, `SQLite Store`, `Snapshot Row Building`?**
  _High betweenness centrality (0.038) - this node is a cross-community bridge._
- **Why does `PlaywrightNotInstalled` connect `Store Timestamp Tests` to `_FakePage`, `Variant Extraction Ladder`, `Fetch Strategy Probing`, `HTTP/Browser Fetching`, `Discovery Report Model`, `Search Engine Core`, `Multi-Site Search Run`, `Basket Domain Logic`, `Playwright Errors`, `conftest.py`, `SQLite Store`, `Discovery CLI Reporting`?**
  _High betweenness centrality (0.030) - this node is a cross-community bridge._
- **Are the 11 inferred relationships involving `PerfumeQuery` (e.g. with `BasketLine` and `BasketPrice`) actually correct?**
  _`PerfumeQuery` has 11 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `SearchScreen` (e.g. with `ParfumFinderApp` and `PerfumeQuery`) actually correct?**
  _`SearchScreen` has 3 INFERRED edges - model-reasoned connections that need verification._
- **What connects `parfum-finder`, `$schema`, `$id` to the rest of the system?**
  _152 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `TUI App & Screens` be split into smaller, more focused modules?**
  _Cohesion score 0.10536828963795256 - nodes in this community are weakly interconnected._