# Graph Report - parfum-finder  (2026-08-10)

## Corpus Check
- 68 files · ~251,063 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1711 nodes · 4628 edges · 72 communities (70 shown, 2 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 190 edges (avg confidence: 0.57)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `45e9b725`
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
- ConfirmScreen
- Request Schema Fields
- _FixtureFetcher
- Snapshot Row Building
- _named_profile
- Fetch Strategy Selection
- Price History
- Extraction Layer Enum
- run_sites
- validate_live
- .__call__
- extract_endpoint_variants
- field_map
- exclude_keywords
- Variant Pattern A
- Project Root
- Any

## God Nodes (most connected - your core abstractions)
1. `search_site()` - 66 edges
2. `_profile()` - 58 edges
3. `discover()` - 56 edges
4. `SearchScreen` - 54 edges
5. `SiteResult` - 52 edges
6. `BasketScreen` - 52 edges
7. `PerfumeQuery` - 50 edges
8. `Fetcher` - 42 edges
9. `_attempt()` - 42 edges
10. `_fake_probe()` - 42 edges

## Surprising Connections (you probably didn't know these)
- `Shipping Non-linearity Rationale (why cheapest-per-item is wrong)` --semantically_similar_to--> `sites/ Site Profile Directory`  [INFERRED] [semantically similar]
  ARCHITECTURE.md → sites/README.md
- `Variant Pattern B (dropdown + AJAX price)` --semantically_similar_to--> `Variant Selector Detector Fix (WooCommerce 'variation' vs 'variant')`  [INFERRED] [semantically similar]
  ARCHITECTURE.md → docs/discovery-report.md
- `test_real_measurement_picks_httpx_for_a_plain_page()` --indirect_call--> `DiscoveryReport`  [INFERRED]
  tests/test_discover.py → src/parfum_finder/discover.py
- `_NoRootParser` --uses--> `ExtractionFailed`  [INFERRED]
  tests/test_engine.py → src/parfum_finder/engine.py
- `test_a_hook_that_reads_nothing_is_named_as_the_culprit()` --indirect_call--> `ExtractionFailed`  [INFERRED]
  tests/test_engine.py → src/parfum_finder/engine.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Sites Implementing Variant Pattern C (embedded JSON)** — docs_discovery_report_venco_site, docs_discovery_report_decantall_site, docs_discovery_report_luxurydekant_site, docs_discovery_report_ruxangroup_site, architecture_md_variant_pattern_c [EXTRACTED 1.00]
- **İdeasoft Platform Sites and Endpoint** — docs_discovery_report_dekantparfum_site, docs_discovery_report_dekantdoktoru_site, docs_discovery_report_ideasoft_related_options_endpoint, platforms_readme_ideasoft_json [EXTRACTED 1.00]
- **discover Command Output Artifacts (profile + fixtures + CI validation)** — architecture_md_discover_flow, sites_readme_sites_dir, fixtures_readme_fixtures_dir, github_workflows_ci_validate_profiles_step, architecture_md_validate_command [INFERRED 0.85]

## Communities (72 total, 2 thin omitted)

### Community 0 - "TUI App & Screens"
Cohesion: 0.11
Nodes (88): The Textual-based terminal UI: search and basket screens., _app(), _basket(), _cells(), _days_ago(), _leg(), _ok(), _open_basket() (+80 more)

### Community 1 - "Site Profiles & Templates"
Cohesion: 0.06
Nodes (83): _check_hook_kinds(), deep_merge(), _load_json(), load_platform_template(), load_platform_templates(), load_site_hooks(), load_site_profile(), Any (+75 more)

### Community 2 - "Title Matcher"
Cohesion: 0.05
Nodes (88): _listing_filter(), CandidateFilter, Decide, from a search result's own title, whether to open its page., _canonical(), _covers(), _ends_with(), _index_of(), Match (+80 more)

### Community 3 - "HTTP/Browser Fetching"
Cohesion: 0.13
Nodes (29): browser_session(), fetch(), PlaywrightNotInstalled, Fetch one URL using exactly the given strategy.      `method`/`data` exist for t, Yield a fetcher that keeps one browser for every playwright page it reads., The "playwright" strategy was requested but cannot run at all.      Covers both, test_the_no_results_page_would_otherwise_read_as_suspect(), _fake_launch() (+21 more)

### Community 4 - "Search/Basket Domain Models"
Cohesion: 0.08
Nodes (99): LogCaptureFixture, ProductCandidate, One hit on a search results page, before its product page is opened.      `raw_t, A candidate together with the decant sizes its product page offers., What one site had to say about one query, and how much to trust it.      Four st, SearchHit, SiteResult, connect() (+91 more)

### Community 5 - "Search Engine per Site"
Cohesion: 0.29
Nodes (7): _NoRootParser, MonkeyPatch, Record every delay the engine asks for instead of serving it.      Waiting for r, Stands in for HTMLParser when a page's markup cannot be read at all.      select, slept(), test_a_product_page_with_no_root_names_its_body_size(), test_a_search_page_with_no_root_names_its_body_size()

### Community 6 - "Platform Discovery Flow"
Cohesion: 0.15
Nodes (59): PlatformChooser, _ask_chooser(), discover(), Put the question only when there is one, and hold the answer to it.      An answ, Measure the strategies a site needs, then read its JSON-LD with the winner., _attempt(), _fake_probe(), Any (+51 more)

### Community 7 - "CLI Entry Points"
Cohesion: 0.08
Nodes (60): CaptureFixture, ask_which_platform(), main(), Any, Connection, Path, Command-line entry point.  Subcommands will be added incrementally as the projec, Scan every site for the perfumes named, store what came back, print it.      One (+52 more)

### Community 8 - "Architecture Rationale Docs"
Cohesion: 0.05
Nodes (53): basket Subset Enumeration + Local Improvement Algorithm, basket Optimizer (optimize function), Clone/Original Distinction (KLON ← <orijinal>), discover Discovery Flow, engine Concurrency Model (parallel sites, serial within site), Extraction Ladder (jsonld/endpoint/embedded/css), Fail-loud / status=suspect policy, hooks/<id>.py Escape Hatch (+45 more)

### Community 9 - "Search Engine Core"
Cohesion: 0.08
Nodes (48): HTMLParser, _check_empty_search(), _check_variant_control(), _fetch_page(), _headers(), _is_excluded(), _paced_fetcher(), _page_offers_sizes() (+40 more)

### Community 10 - "Basket Optimizer Core"
Cohesion: 0.14
Nodes (36): Collection, Prices, BasketItem, optimize(), Basket scenario evaluation. A pure function, no network access, no sqlite.  Inpu, Score one site against the basket, or against a subset of it.      `item_ids` is, Score every enabled site against the whole basket and sort the results.      Sit, Search for the cheapest way to split the basket across several sites.      Retur (+28 more)

### Community 11 - "Basket Store & Pricing"
Cohesion: 0.10
Nodes (36): add_basket_item(), Add a size of a perfume to the basket, and return the basket_item_id.      The p, Connection, Two snapshots written in the same second must resolve to the newer one.      A s, 5 ml at 125,00 TL is 25,00 TL per ml. Stored as kurus, ml as tenths., No price yet means no row, so the basket LEFT JOIN reads it as missing., A zero ml variant is a parse failure, and it must not reach the table.      If i, Adding the same perfume and size twice must accumulate, not clobber.      The ba (+28 more)

### Community 12 - "JSON-LD Product Extraction"
Cohesion: 0.15
Nodes (30): extract_jsonld_products(), Read every JSON-LD Product declared on the page, in document order.      A block, _one_product_html(), Tests for parfum_finder.extract.  Every case here is a shape a real store actual, Wrap a JSON-LD product body in a page, for the one-field-at-a-time cases., test_a_broken_block_does_not_lose_the_valid_one(), test_availability_spellings_all_land_in_the_same_bucket(), test_boolean_values_are_never_read_as_price_or_text() (+22 more)

### Community 13 - "Basket TUI Screen"
Cohesion: 0.14
Nodes (9): _Change, BasketReport, Every site's single-site scenario, split by whether it covers everything.      A, BasketScreen, Any, The basket: the list on top, one scenario per site underneath., The three inputs basket.py's pure functions score: items, prices, shipping., _remove() (+1 more)

### Community 14 - "Platform Schema"
Cohesion: 0.06
Nodes (31): any, defaults, fingerprint, additionalProperties, items, minItems, type, description (+23 more)

### Community 15 - "Product Extraction"
Cohesion: 0.11
Nodes (28): _as_str(), _build_offer(), _build_product(), _coerce_in_stock(), _collect_offers(), _collect_products(), _collect_variants(), _has_type() (+20 more)

### Community 16 - "Schema Field Patterns"
Cohesion: 0.07
Nodes (29): format, pattern, type, pattern, type, default, type, pattern (+21 more)

### Community 17 - "Offline Profile Validation"
Cohesion: 0.11
Nodes (21): Check, _count_result_cards(), _first_result_url(), live_query(), _no_results_check(), _probe_layer(), _probe_other_layers(), Any (+13 more)

### Community 18 - "Playwright Errors"
Cohesion: 0.15
Nodes (21): _attempt(), _count_jsonld(), _count_product_objects(), _detect_platforms(), format_report(), _label_platform(), _one_line(), ProbeAttempt (+13 more)

### Community 19 - "Search TUI Screen"
Cohesion: 0.13
Nodes (5): HeaderSelected, RowSelected, The initial screen: search bar, streaming results table, notices, footer., What each site charges for the product a block is about.          One entry per, SearchScreen

### Community 20 - "Snapshot Writing"
Cohesion: 0.14
Nodes (22): One priced size of one perfume on one site, ready to be written.      The perfum, Write a whole scan at once and return how many prices were recorded.      Every, SnapshotRow, write_snapshots(), The drop happens here so no caller can forget it.      Both the CLI and the scre, The title and URL are information, not identity.      A shop that rewords a list, EDT and EDP are different products at different prices.      Folding them into o, The column is 0/1, so the tri-state has to land somewhere on purpose.      Unkno (+14 more)

### Community 21 - "Candidate Filtering"
Cohesion: 0.21
Nodes (7): _listing_filter(), Any, CacheKey, CandidateFilter, VariantsRead, Decide, from a search result's own title, whether to open its page., Scan one site for every perfume of this search, one at a time.          Serial i

### Community 22 - "Basket Site Scenarios"
Cohesion: 0.10
Nodes (39): One decant size of one product, in the units the database stores.      Tenths of, Variant, basket_lines(), basket_prices(), basket_sites(), BasketLine, BasketPrice, BasketSite (+31 more)

### Community 23 - "Price/Size Normalization"
Cohesion: 0.15
Nodes (21): _classify_single_separator(), format_ml(), format_price(), _parse_number(), parse_price(), parse_size_ml(), Decimal, Number parsing and formatting for prices and volumes, plus text folding.  This i (+13 more)

### Community 24 - "JSON Schema Primitives"
Cohesion: 0.12
Nodes (23): null, string, properties, type, type, type, additionalProperties, properties (+15 more)

### Community 25 - "SQLite Store"
Cohesion: 0.19
Nodes (18): _close_browser(), _fetch_curl_cffi(), _fetch_httpx(), _fetch_playwright(), FetchResult, _launch_browser(), Any, FormData (+10 more)

### Community 26 - "Site Profile Fields"
Cohesion: 0.15
Nodes (13): base_url, discovered_at, extraction, id, needs_review, platform, search, shipping (+5 more)

### Community 27 - "Site Schema Validation Tests"
Cohesion: 0.19
Nodes (17): Draft202012Validator, _load_schema(), _platform_validator(), Any, Tests for schema/site.schema.json and schema/platform.schema.json.  These check, The third copy of the ladder is here, and nothing else would catch it drifting., _site_validator(), test_platform_schema_accepts_the_documented_example() (+9 more)

### Community 28 - "Variant Rule Fields"
Cohesion: 0.08
Nodes (26): exclude_keywords, field, max_size_ml, size_from, size_pattern, title, variant_label, items (+18 more)

### Community 29 - "Discovery CLI Reporting"
Cohesion: 0.07
Nodes (53): _choose_strategy(), collect_prices(), DiscoveryReport, FieldConfidence, _flatten_defaults(), _format_choice(), _format_confidence(), _format_defaults() (+45 more)

### Community 30 - "Store Timestamp Tests"
Cohesion: 0.16
Nodes (7): PlaywrightNoResponse, RuntimeError, Navigation completed but playwright returned no Response object.      Its own ty, _FakeBrowser, _FakePage, Any, test_fetch_playwright_no_response_raises_its_own_error_type()

### Community 31 - "Live Profile Validation"
Cohesion: 0.19
Nodes (22): format_report(), Check one site's profile against that site's saved fixtures.      Never raises f, Render the validations as the offline half of the report in APP_FLOW §6.      A, validate_offline(), _corrupted_sites_dir(), _iso_days_ago(), Any, Path (+14 more)

### Community 32 - "Variant Extraction Fields"
Cohesion: 0.15
Nodes (13): attribute, script, type, properties, type, attribute, marker, selector (+5 more)

### Community 33 - "Variant Extraction Ladder"
Cohesion: 0.16
Nodes (5): Changed, One perfume of a search, as typed and as parsed.      The index is the outermost, Empty the table for a new scan.          The columns are the same every time now, _Search, Submitted

### Community 34 - "Fetch Strategy Probing"
Cohesion: 0.21
Nodes (15): probe(), Fetch `url` with every strategy and report diagnostics for each.      timeout_s, MonkeyPatch, Tests for parfum_finder.probe.  probe() always tries all three strategies -- the, test_probe_counts_jsonld_product_and_platform_signature(), test_probe_counts_product_across_jsonld_root_shapes(), test_probe_counts_product_markup_without_any_jsonld(), test_probe_counts_products_nested_below_the_top_level() (+7 more)

### Community 35 - "Platform Field Mapping"
Cohesion: 0.18
Nodes (11): field_map, product_json, source, variants_path, additionalProperties, allOf, description, required (+3 more)

### Community 36 - "Shipping Config Schema"
Cohesion: 0.12
Nodes (16): free_shipping_threshold_kurus, integer, shipping_cost_kurus, minimum, type, type, free_shipping_threshold_kurus, notes (+8 more)

### Community 37 - "Discovery Report Model"
Cohesion: 0.50
Nodes (3): The template this site's profile would be based on, if any., Which of the matching templates gets applied, or None for none of them.      One, _resolve_platform()

### Community 38 - "TUI Confirm Dialog"
Cohesion: 0.15
Nodes (13): One call has to leave a row the search table can read straight off.      The cal, The old price has to survive, and it must not become a second variant.      Appe, first_seen is what says how long a shop has carried a size., A sold-out size often shows no price at all, and 0 would mean free.      Writing, raw_title is the audit trail for a wrong match, so it cannot be blank.      A ro, Sites come from the profiles, so an id nothing synced is a mistake., _record(), test_a_second_scan_appends_instead_of_overwriting() (+5 more)

### Community 39 - "TUI App Shell"
Cohesion: 0.12
Nodes (12): Screen, ParfumFinderApp, Path, The Textual App root. Handles screen navigation and is the app's default entry p, Root app: pushes the search screen on mount., Path, Path, Protocol (+4 more)

### Community 40 - "Fetch Backends"
Cohesion: 0.14
Nodes (14): curl_cffi, httpx, playwright, result_item, result_title, result_url, strategy, url_template (+6 more)

### Community 41 - "HTTP Request Schema"
Cohesion: 0.12
Nodes (17): GET, POST, additionalProperties, allOf, description, properties, type, default (+9 more)

### Community 42 - "Fixture Fetcher (Tests)"
Cohesion: 0.24
Nodes (6): BaseHTTPRequestHandler, _Handler, _playwright_usable(), Shared pytest fixtures.  A local HTTP server used by fetch/probe tests: real req, Whether the playwright rung can actually run here, binary included.      Checkin, server_url()

### Community 43 - "Validation Reporting"
Cohesion: 0.09
Nodes (29): ExtractionFailed, RuntimeError, A page answered but gave up nothing, where something was expected.      This is, Run one query against one site and read every hit's sizes.      Everything site-, Give a size the listing's title and URL when the page gave it none.      A site, search_site(), _with_candidate_identity(), test_a_full_bottle_next_to_a_decant_does_not_sink_the_site() (+21 more)

### Community 44 - "Decant Variant Rules"
Cohesion: 0.25
Nodes (11): _css_variant(), _parse_selector(), Node, Read one variant's fields out of its container node., Run one "<css>::text" / "<css>::attr(name)" selector inside a node.      The nod, Run one "<css>::text" / "<css>::attr(name)" selector, reading every match., Split a "<css>::text" / "<css>::attr(name)" selector into its two parts., Read the attribute or text of one already-selected node, or None. (+3 more)

### Community 45 - "Multi-Site Search Run"
Cohesion: 0.17
Nodes (15): _age_of(), profile_age_days(), datetime, Profile staleness checks. Two modes: offline (against saved fixtures) and live (, Every site that has a profile, sorted so reports read the same way twice., Whole days between a profile's `discovered_at` and now.      Only the exact UTC, Validate every site, or just the ones named.      Serial rather than concurrent:, The profile's age in days, or None if the file cannot say.      Reads the site f (+7 more)

### Community 46 - "Offline Validation Fixtures"
Cohesion: 0.15
Nodes (17): _balanced_value(), _embedded_documents(), extract_embedded_variants(), _loads_or_skip(), Any, Rung 3: read the JSON blob the page carries but does not display.      Two shape, Yield every JSON document the page hides, in document order., Parse `text` as JSON, yielding nothing when it isn't JSON.      Pages are full o (+9 more)

### Community 47 - "Basket Domain Logic"
Cohesion: 0.14
Nodes (27): Run one site and classify what came back instead of raising.      It is also whe, run_site(), _counting_fetcher(), _profile(), Exception, Answer each call with the next canned result, then repeat the last one., A minimal working profile, with the fields a case cares about swapped in., test_a_dead_link_selector_is_suspect_not_empty() (+19 more)

### Community 48 - "Search Screen Rows"
Cohesion: 0.22
Nodes (6): Decimal, Row, One priced size, exactly as the table shows it and as a keypress needs it., The default order: typed order, product, site, size.          The typed order co, The order once a column has been picked: the site layer drops out.          Aski, _ResultRow

### Community 49 - "test_engine.py"
Cohesion: 0.17
Nodes (25): apply_variant_rules(), Turn raw size rows into decant variants, dropping what is not a decant.      Thr, _named_profile(), Any, Tests for the profile-driven search in parfum_finder.engine.  What these defend, The real fetcher, with a list of every URL it was asked for., A profile whose search page lists two houses' bottles, as shops do., _row() (+17 more)

### Community 50 - "Profile Age Checks"
Cohesion: 0.25
Nodes (7): _age_line(), format_live_report(), Every check run against one site's profile, in the order they ran.      Checks s, Whether the profile is old enough to be worth re-discovering., The age note for one site, or None when its age is unremarkable.      A profile, Render offline and live results side by side, as APP_FLOW §6 shows them.      Bo, SiteValidation

### Community 51 - "extract_endpoint_variants"
Cohesion: 0.13
Nodes (19): extract_css_variants(), extract_jsonld_variants(), _flatten_jsonld(), Rung 1: read the page's JSON-LD as flat variant rows.      A product that declar, Turn one Product and everything under it into rows., Rung 4: read the rendered markup with selectors. Last resort.      `config["vari, One buyable size of one product, exactly as the page or feed states it.      Thi, RawVariant (+11 more)

### Community 52 - "Snapshot Row Semantics"
Cohesion: 0.25
Nodes (7): additionalProperties, allOf, description, $id, $schema, title, type

### Community 53 - "conftest.py"
Cohesion: 0.10
Nodes (20): now_iso(), Return the current UTC time as 'YYYY-MM-DDTHH:MM:SSZ'.      Every timestamp writ, conn(), Path, Tests for parfum_finder.store: the timestamp helper and the schema.  The one har, An update aimed at a row that isn't there means the caller is out of sync., A snapshot pointing at a variant that doesn't exist has to be rejected.      SQL, Reopening an existing database must not wipe or re-raise on its schema. (+12 more)

### Community 54 - "Endpoint Schema Fields"
Cohesion: 0.22
Nodes (9): result_item, result_title, result_url, url_template, search, additionalProperties, description, required (+1 more)

### Community 55 - "ConfirmScreen"
Cohesion: 0.18
Nodes (6): Pressed, ComposeResult, ConfirmScreen, ComposeResult, Asks before a low-confidence match is written to the basket.      The two answer, Static

### Community 56 - "Request Schema Fields"
Cohesion: 0.25
Nodes (8): type, additionalProperties, type, body, request_headers, additionalProperties, description, type

### Community 57 - "_FixtureFetcher"
Cohesion: 0.22
Nodes (9): _FixtureFetcher, _path(), FormData, Headers, Method, Strategy, Serves one site's saved capture in place of the network.      Only three kinds o, The one real result card that led to the captured product page.          Cut out (+1 more)

### Community 58 - "Snapshot Row Building"
Cohesion: 0.25
Nodes (8): One site's share of a split basket: what to buy there and what it costs.      `s, The cheapest basket split the search found. A heuristic, not a proof.      Every, SplitLeg, SplitPlan, _leg_block(), One site's share of a split: its assigned items, then its own subtotal.      A s, The best-combination block: its legs, grand total, and its honesty checks., _split_block()

### Community 59 - "_named_profile"
Cohesion: 0.40
Nodes (4): What it would cost to buy some or all of the basket from one site.      `covered, SiteScenario, The two or three lines one site's scenario takes up on screen., _scenario_block()

### Community 60 - "Fetch Strategy Selection"
Cohesion: 0.31
Nodes (11): Path, Give the test profile's site id a hook file. The id is what binds them., test_a_before_search_that_returns_no_query_is_refused(), test_a_broken_hook_is_an_error_not_a_silent_empty(), test_a_hook_that_reads_nothing_is_named_as_the_culprit(), test_a_site_with_no_hook_file_is_driven_by_its_profile_alone(), test_after_search_can_drop_a_result_the_selectors_could_not(), test_before_search_rewrites_the_query_that_is_actually_sent() (+3 more)

### Community 61 - "Price History"
Cohesion: 0.29
Nodes (7): price_history(), Row, Return one variant's past readings, newest first, capped at limit.      Empty fo, The trend panel reads row 0 as the latest reading, so order is the point.      A, No history yet is a normal state for a variant, not an error to raise on., test_price_history_is_empty_for_an_unknown_variant(), test_price_history_is_newest_first_and_capped_at_limit()

### Community 62 - "Extraction Layer Enum"
Cohesion: 0.33
Nodes (6): css, embedded_json, endpoint, jsonld, enum, extraction

### Community 63 - "run_sites"
Cohesion: 0.18
Nodes (11): _candidates_to_open(), CandidateFilter, Path, Run every site against one query, all at once, and report each separately., Narrow the search results down to the pages worth a request.      The first one, run_sites(), test_a_dead_site_does_not_take_the_others_down(), test_a_profile_that_breaks_on_setup_is_contained_too() (+3 more)

### Community 64 - "validate_live"
Cohesion: 0.22
Nodes (15): Run one site's profile against the real site.      Same contract as offline mode, validate_live(), _DeadSite, _FakeSite, _fixture_site(), M5's own criterion: when a profile stops agreeing with its site's real markup, o, A stand-in for one live site, answering the search page then the rest.      Live, A host that cannot be reached at all. (+7 more)

### Community 65 - ".__call__"
Cohesion: 0.53
Nodes (4): FormData, Headers, Method, Strategy

### Community 66 - "extract_endpoint_variants"
Cohesion: 0.25
Nodes (8): extract_endpoint_variants(), Rung 2: read the variant list out of a platform's JSON response.      `document`, Read variant rows out of a parsed JSON document.      Shared by the endpoint and, Follow a dotted path into parsed JSON, e.g. "data.options.0.price".      A segme, _resolve_path(), _variants_from_document(), test_endpoint_reads_every_size_from_one_response(), test_endpoint_without_a_field_map_reads_nothing()

### Community 67 - "field_map"
Cohesion: 0.29
Nodes (7): in_stock, price, size_raw, additionalProperties, required, type, field_map

### Community 68 - "exclude_keywords"
Cohesion: 0.50
Nodes (4): rate_limit_ms, default, minimum, type

### Community 71 - "Any"
Cohesion: 0.50
Nodes (4): format_age(), Turn a price age in days into the words the age column shows., The age column exists to be glanced at, so it is phrased, not printed., test_format_age_reads_as_words_not_a_timestamp()

## Knowledge Gaps
- **154 isolated node(s):** `parfum-finder`, `$schema`, `$id`, `title`, `description` (+149 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `SiteResult` connect `Search/Basket Domain Models` to `TUI App & Screens`, `Site Profiles & Templates`, `HTTP/Browser Fetching`, `CLI Entry Points`, `Search Engine Core`, `Basket TUI Screen`, `Search TUI Screen`, `Snapshot Writing`, `Candidate Filtering`, `Basket Site Scenarios`, `SQLite Store`, `Variant Extraction Ladder`, `TUI App Shell`, `Basket Domain Logic`, `Search Screen Rows`, `extract_endpoint_variants`, `conftest.py`, `ConfirmScreen`, `run_sites`?**
  _High betweenness centrality (0.042) - this node is a cross-community bridge._
- **Why does `SearchScreen` connect `Search TUI Screen` to `TUI App & Screens`, `Variant Extraction Ladder`, `Title Matcher`, `Search/Basket Domain Models`, `TUI App Shell`, `Search Engine Core`, `Basket TUI Screen`, `Search Screen Rows`, `Snapshot Writing`, `Candidate Filtering`, `ConfirmScreen`?**
  _High betweenness centrality (0.037) - this node is a cross-community bridge._
- **Why does `BasketScreen` connect `Basket TUI Screen` to `TUI App & Screens`, `Variant Extraction Ladder`, `Title Matcher`, `Search/Basket Domain Models`, `TUI App Shell`, `Basket Optimizer Core`, `Search Screen Rows`, `Search TUI Screen`, `Snapshot Writing`, `ConfirmScreen`, `Basket Site Scenarios`, `Price/Size Normalization`, `Snapshot Row Building`, `_named_profile`?**
  _High betweenness centrality (0.031) - this node is a cross-community bridge._
- **Are the 7 inferred relationships involving `SearchScreen` (e.g. with `ParfumFinderApp` and `SiteResult`) actually correct?**
  _`SearchScreen` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Are the 16 inferred relationships involving `SiteResult` (e.g. with `RawVariant` and `Fetcher`) actually correct?**
  _`SiteResult` has 16 INFERRED edges - model-reasoned connections that need verification._
- **What connects `parfum-finder`, `$schema`, `$id` to the rest of the system?**
  _154 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `TUI App & Screens` be split into smaller, more focused modules?**
  _Cohesion score 0.10536828963795256 - nodes in this community are weakly interconnected._