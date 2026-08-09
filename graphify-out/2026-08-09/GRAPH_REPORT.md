# Graph Report - parfum-finder  (2026-08-09)

## Corpus Check
- 65 files · ~228,248 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1694 nodes · 4582 edges · 75 communities (71 shown, 4 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 187 edges (avg confidence: 0.57)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `27cf3514`
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
- Template Matching
- Profile Age Checks
- Live Query Tests
- Snapshot Row Semantics
- CSS Selector Parsing
- Endpoint Schema Fields
- Multi-House Listing Tests
- Request Schema Fields
- Field Confidence Scoring
- Snapshot Row Building
- Variant Field Types
- Fetch Strategy Selection
- Price History
- Extraction Layer Enum
- Embedded JSON Parsing
- Engine Delay Tests
- JSON-LD Product Walking
- Endpoint Variant Extraction
- Price Age Formatting
- No-Root HTML Parser
- Variant Pattern A
- Project Root
- Decimal
- Protocol
- Row
- VariantsRead

## God Nodes (most connected - your core abstractions)
1. `search_site()` - 64 edges
2. `discover()` - 56 edges
3. `SearchScreen` - 54 edges
4. `_profile()` - 54 edges
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
- `test_a_hook_that_reads_nothing_is_named_as_the_culprit()` --indirect_call--> `ExtractionFailed`  [INFERRED]
  tests/test_engine.py → src/parfum_finder/engine.py
- `test_a_post_endpoint_missing_a_static_body_field_fails_loudly()` --indirect_call--> `ExtractionFailed`  [INFERRED]
  tests/test_engine.py → src/parfum_finder/engine.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Sites Implementing Variant Pattern C (embedded JSON)** — docs_discovery_report_venco_site, docs_discovery_report_decantall_site, docs_discovery_report_luxurydekant_site, docs_discovery_report_ruxangroup_site, architecture_md_variant_pattern_c [EXTRACTED 1.00]
- **İdeasoft Platform Sites and Endpoint** — docs_discovery_report_dekantparfum_site, docs_discovery_report_dekantdoktoru_site, docs_discovery_report_ideasoft_related_options_endpoint, platforms_readme_ideasoft_json [EXTRACTED 1.00]
- **discover Command Output Artifacts (profile + fixtures + CI validation)** — architecture_md_discover_flow, sites_readme_sites_dir, fixtures_readme_fixtures_dir, github_workflows_ci_validate_profiles_step, architecture_md_validate_command [INFERRED 0.85]

## Communities (75 total, 4 thin omitted)

### Community 0 - "TUI App & Screens"
Cohesion: 0.11
Nodes (88): The Textual-based terminal UI: search and basket screens., _app(), _basket(), _cells(), _days_ago(), _leg(), _ok(), _open_basket() (+80 more)

### Community 1 - "Site Profiles & Templates"
Cohesion: 0.06
Nodes (81): _check_hook_kinds(), deep_merge(), _load_json(), load_platform_template(), load_platform_templates(), load_site_hooks(), load_site_profile(), Any (+73 more)

### Community 2 - "Title Matcher"
Cohesion: 0.05
Nodes (88): _listing_filter(), CandidateFilter, Decide, from a search result's own title, whether to open its page., _canonical(), _covers(), _ends_with(), _index_of(), Match (+80 more)

### Community 3 - "HTTP/Browser Fetching"
Cohesion: 0.14
Nodes (28): browser_session(), fetch(), PlaywrightNotInstalled, Fetch one URL using exactly the given strategy.      `method`/`data` exist for t, Yield a fetcher that keeps one browser for every playwright page it reads., The "playwright" strategy was requested but cannot run at all.      Covers both, _fake_launch(), MonkeyPatch (+20 more)

### Community 4 - "Search/Basket Domain Models"
Cohesion: 0.07
Nodes (101): LogCaptureFixture, Pressed, ProductCandidate, One hit on a search results page, before its product page is opened.      `raw_t, One decant size of one product, in the units the database stores.      Tenths of, A candidate together with the decant sizes its product page offers., What one site had to say about one query, and how much to trust it.      Four st, SearchHit (+93 more)

### Community 5 - "Search Engine per Site"
Cohesion: 0.15
Nodes (25): Run one site and classify what came back instead of raising.      It is also whe, run_site(), _counting_fetcher(), Exception, Tests for the profile-driven search in parfum_finder.engine.  What these defend, Answer each call with the next canned result, then repeat the last one., test_a_broken_profile_is_still_suspect_when_no_title_looked_right(), test_a_dead_link_selector_is_suspect_not_empty() (+17 more)

### Community 6 - "Platform Discovery Flow"
Cohesion: 0.15
Nodes (59): PlatformChooser, _ask_chooser(), discover(), Put the question only when there is one, and hold the answer to it.      An answ, Measure the strategies a site needs, then read its JSON-LD with the winner., _attempt(), _fake_probe(), Any (+51 more)

### Community 7 - "CLI Entry Points"
Cohesion: 0.14
Nodes (40): CaptureFixture, ask_which_platform(), main(), Path, Scan every site for the perfumes named, store what came back, print it.      One, Ask at the terminal which of several matching templates to apply.      Asked whi, run_search(), A multi-site price and stock comparison tool for perfume decants.  Includes a sh (+32 more)

### Community 8 - "Architecture Rationale Docs"
Cohesion: 0.05
Nodes (53): basket Subset Enumeration + Local Improvement Algorithm, basket Optimizer (optimize function), Clone/Original Distinction (KLON ← <orijinal>), discover Discovery Flow, engine Concurrency Model (parallel sites, serial within site), Extraction Ladder (jsonld/endpoint/embedded/css), Fail-loud / status=suspect policy, hooks/<id>.py Escape Hatch (+45 more)

### Community 9 - "Search Engine Core"
Cohesion: 0.09
Nodes (43): HTMLParser, _check_variant_control(), _fetch_page(), _headers(), _is_excluded(), _paced_fetcher(), _parse_endpoint_document(), Any (+35 more)

### Community 10 - "Basket Optimizer Core"
Cohesion: 0.14
Nodes (36): Collection, Prices, BasketItem, optimize(), Basket scenario evaluation. A pure function, no network access, no sqlite.  Inpu, Score one site against the basket, or against a subset of it.      `item_ids` is, Score every enabled site against the whole basket and sort the results.      Sit, Search for the cheapest way to split the basket across several sites.      Retur (+28 more)

### Community 11 - "Basket Store & Pricing"
Cohesion: 0.10
Nodes (29): Connection, A snapshot pointing at a variant that doesn't exist has to be rejected.      SQL, Two snapshots written in the same second must resolve to the newer one.      A s, 5 ml at 125,00 TL is 25,00 TL per ml. Stored as kurus, ml as tenths., No price yet means no row, so the basket LEFT JOIN reads it as missing., A zero ml variant is a parse failure, and it must not reach the table.      If i, Adding the same perfume and size twice must accumulate, not clobber.      The ba, Insert one site → perfume → product → variant chain, return the variant id. (+21 more)

### Community 12 - "JSON-LD Product Extraction"
Cohesion: 0.13
Nodes (32): extract_jsonld_products(), Read every JSON-LD Product declared on the page, in document order.      A block, _one_product_html(), Tests for parfum_finder.extract.  Every case here is a shape a real store actual, Wrap a JSON-LD product body in a page, for the one-field-at-a-time cases., test_a_broken_block_does_not_lose_the_valid_one(), test_availability_spellings_all_land_in_the_same_bucket(), test_boolean_values_are_never_read_as_price_or_text() (+24 more)

### Community 13 - "Basket TUI Screen"
Cohesion: 0.12
Nodes (10): _Change, BasketReport, Every site's single-site scenario, split by whether it covers everything.      A, BasketScreen, Any, Path, The basket: the list on top, one scenario per site underneath., The three inputs basket.py's pure functions score: items, prices, shipping. (+2 more)

### Community 14 - "Platform Schema"
Cohesion: 0.06
Nodes (31): any, defaults, fingerprint, additionalProperties, items, minItems, type, description (+23 more)

### Community 15 - "Product Extraction"
Cohesion: 0.11
Nodes (31): _as_str(), _build_offer(), _build_product(), _coerce_in_stock(), _collect_offers(), _collect_variants(), _css_variant(), JsonLdOffer (+23 more)

### Community 16 - "Schema Field Patterns"
Cohesion: 0.07
Nodes (30): format, pattern, type, pattern, type, default, type, pattern (+22 more)

### Community 17 - "Offline Profile Validation"
Cohesion: 0.11
Nodes (26): Fetcher, Protocol, Anything that can stand in for `fetch`.      Offline profile validation runs the, _age_of(), Check, _first_result_url(), _LayerUnavailable, _probe_layer() (+18 more)

### Community 18 - "Playwright Errors"
Cohesion: 0.15
Nodes (21): _attempt(), _count_jsonld(), _count_product_objects(), _detect_platforms(), format_report(), _label_platform(), _one_line(), ProbeAttempt (+13 more)

### Community 19 - "Search TUI Screen"
Cohesion: 0.17
Nodes (3): RowSelected, The initial screen: search bar, streaming results table, notices, footer., SearchScreen

### Community 20 - "Snapshot Writing"
Cohesion: 0.21
Nodes (12): One priced size of one perfume on one site, ready to be written.      The perfum, Write a whole scan at once and return how many prices were recorded.      Every, SnapshotRow, write_snapshots(), The drop happens here so no caller can forget it.      Both the CLI and the scre, A slow site must not spread one reading across several timestamps.      Rows wri, The number reported is what landed in the history, not what was offered., Half a site's sizes updated is worse than none of them.      The basket compares (+4 more)

### Community 21 - "Candidate Filtering"
Cohesion: 0.18
Nodes (9): _listing_filter(), Any, CacheKey, CandidateFilter, VariantsRead, Decide, from a search result's own title, whether to open its page., One perfume of a search, as typed and as parsed.      The index is what groups t, Scan one site for every perfume of this search, one at a time.          Serial i (+1 more)

### Community 22 - "Basket Site Scenarios"
Cohesion: 0.12
Nodes (24): What it would cost to buy some or all of the basket from one site.      `covered, SiteScenario, basket_lines(), basket_prices(), basket_sites(), BasketLine, BasketPrice, BasketSite (+16 more)

### Community 23 - "Price/Size Normalization"
Cohesion: 0.15
Nodes (21): _classify_single_separator(), format_ml(), format_price(), _parse_number(), parse_price(), parse_size_ml(), Decimal, Number parsing and formatting for prices and volumes, plus text folding.  This i (+13 more)

### Community 24 - "JSON Schema Primitives"
Cohesion: 0.12
Nodes (23): null, string, properties, type, type, type, additionalProperties, properties (+15 more)

### Community 25 - "SQLite Store"
Cohesion: 0.13
Nodes (25): add_basket_item(), _perfume_id(), _product_id(), Connection, SQLite persistence: an append-only price history.  Tables: sites, perfumes, prod, Write one scan's reading of one size, and return its snapshot id.      The perfu, Do the writing, without opening a transaction of its own., Add a size of a perfume to the basket, and return the basket_item_id.      The p (+17 more)

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
Cohesion: 0.07
Nodes (53): _choose_strategy(), collect_prices(), DiscoveryReport, FieldConfidence, _flatten_defaults(), _format_choice(), _format_confidence(), _format_defaults() (+45 more)

### Community 30 - "Store Timestamp Tests"
Cohesion: 0.19
Nodes (18): _close_browser(), _fetch_curl_cffi(), _fetch_httpx(), _fetch_playwright(), FetchResult, _launch_browser(), Any, FormData (+10 more)

### Community 31 - "Live Profile Validation"
Cohesion: 0.19
Nodes (17): format_live_report(), Run one site's profile against the real site.      Same contract as offline mode, Render offline and live results side by side, as APP_FLOW §6 shows them.      Bo, validate_live(), _DeadSite, _FakeSite, _fixture_site(), M5's own criterion: when a profile stops agreeing with its site's real markup, o (+9 more)

### Community 32 - "Variant Extraction Fields"
Cohesion: 0.11
Nodes (18): attribute, in_stock, price, script, size_raw, type, properties, additionalProperties (+10 more)

### Community 33 - "Variant Extraction Ladder"
Cohesion: 0.15
Nodes (18): extract_embedded_variants(), extract_jsonld_variants(), _flatten_jsonld(), Rung 1: read the page's JSON-LD as flat variant rows.      A product that declar, Turn one Product and everything under it into rows., Rung 3: read the JSON blob the page carries but does not display.      Two shape, _fixture(), Read a captured product page. (+10 more)

### Community 34 - "Fetch Strategy Probing"
Cohesion: 0.21
Nodes (15): probe(), Fetch `url` with every strategy and report diagnostics for each.      timeout_s, MonkeyPatch, Tests for parfum_finder.probe.  probe() always tries all three strategies -- the, test_probe_counts_jsonld_product_and_platform_signature(), test_probe_counts_product_across_jsonld_root_shapes(), test_probe_counts_product_markup_without_any_jsonld(), test_probe_counts_products_nested_below_the_top_level() (+7 more)

### Community 35 - "Platform Field Mapping"
Cohesion: 0.12
Nodes (16): field_map, product_json, source, variants_path, additionalProperties, allOf, description, required (+8 more)

### Community 36 - "Shipping Config Schema"
Cohesion: 0.12
Nodes (16): free_shipping_threshold_kurus, integer, shipping_cost_kurus, minimum, type, type, free_shipping_threshold_kurus, notes (+8 more)

### Community 37 - "Discovery Report Model"
Cohesion: 0.50
Nodes (3): The template this site's profile would be based on, if any., Which of the matching templates gets applied, or None for none of them.      One, _resolve_platform()

### Community 38 - "TUI Confirm Dialog"
Cohesion: 0.40
Nodes (3): ComposeResult, ComposeResult, Static

### Community 39 - "TUI App Shell"
Cohesion: 0.20
Nodes (9): Screen, ParfumFinderApp, Path, The Textual App root. Handles screen navigation and is the app's default entry p, Root app: pushes the search screen on mount., Protocol, What this screen needs of engine.run_site.      A protocol rather than a plain c, SiteRunner (+1 more)

### Community 40 - "Fetch Backends"
Cohesion: 0.14
Nodes (14): curl_cffi, httpx, playwright, result_item, result_title, result_url, strategy, url_template (+6 more)

### Community 41 - "HTTP Request Schema"
Cohesion: 0.14
Nodes (14): GET, POST, properties, default, enum, type, type, type (+6 more)

### Community 42 - "Fixture Fetcher (Tests)"
Cohesion: 0.22
Nodes (9): _FixtureFetcher, _path(), FormData, Headers, Method, Strategy, Serves one site's saved capture in place of the network.      Only three kinds o, The one real result card that led to the captured product page.          Cut out (+1 more)

### Community 43 - "Validation Reporting"
Cohesion: 0.22
Nodes (14): format_report(), Every site that has a profile, sorted so reports read the same way twice., Validate every site, or just the ones named.      Serial rather than concurrent:, Render the validations as the offline half of the report in APP_FLOW §6.      A, site_ids(), validate_all_offline(), _iso_days_ago(), A discovered_at stamp that lands a fixed number of days in the past.      Relati (+6 more)

### Community 44 - "Decant Variant Rules"
Cohesion: 0.27
Nodes (13): apply_variant_rules(), Turn raw size rows into decant variants, dropping what is not a decant.      Thr, _row(), test_a_keyword_in_the_size_label_excludes_the_row_too(), test_a_literal_zero_price_reads_as_no_price_not_a_free_perfume(), test_a_size_at_the_threshold_is_a_bottle_whatever_it_calls_itself(), test_a_size_that_cannot_be_read_is_dropped(), test_an_uppercase_turkish_keyword_still_matches() (+5 more)

### Community 45 - "Multi-Site Search Run"
Cohesion: 0.17
Nodes (12): _candidates_to_open(), CacheKey, CandidateFilter, Path, Run every site against one query, all at once, and report each separately., Narrow the search results down to the pages worth a request.      The first one, run_sites(), test_a_dead_site_does_not_take_the_others_down() (+4 more)

### Community 46 - "Offline Validation Fixtures"
Cohesion: 0.29
Nodes (13): Check one site's profile against that site's saved fixtures.      Never raises f, validate_offline(), _corrupted_sites_dir(), Any, Path, A sites/ directory holding one real profile with fields overwritten.      The re, test_a_dead_price_selector_is_caught_as_the_extraction_step(), test_a_dead_search_selector_is_caught_as_the_search_step() (+5 more)

### Community 47 - "Basket Domain Logic"
Cohesion: 0.12
Nodes (36): Run one query against one site and read every hit's sizes.      Everything site-, search_site(), _profile(), Path, A minimal working profile, with the fields a case cares about swapped in., Give the test profile's site id a hook file. The id is what binds them., test_a_before_search_that_returns_no_query_is_refused(), test_a_broken_hook_is_an_error_not_a_silent_empty() (+28 more)

### Community 48 - "Search Screen Rows"
Cohesion: 0.21
Nodes (6): Decimal, Row, One priced size, exactly as the table shows it and as a keypress needs it., The default order: typed order, product, site, size.          The typed order co, The order once a column has been picked: the site layer drops out.          Aski, _ResultRow

### Community 49 - "Template Matching"
Cohesion: 0.16
Nodes (7): PlaywrightNoResponse, RuntimeError, Navigation completed but playwright returned no Response object.      Its own ty, _FakeBrowser, _FakePage, Any, test_fetch_playwright_no_response_raises_its_own_error_type()

### Community 50 - "Profile Age Checks"
Cohesion: 0.18
Nodes (8): _age_line(), Every check run against one site's profile, in the order they ran.      Checks s, Whether the profile is old enough to be worth re-discovering., The check that broke, or None if the profile is intact., Validate every site against the live web, or just the ones named.      Serial li, The age note for one site, or None when its age is unremarkable.      A profile, SiteValidation, validate_all_live()

### Community 51 - "Live Query Tests"
Cohesion: 0.33
Nodes (10): Path, Attach the rotating file handler and return where it writes.      Safe to call m, setup_logging(), Path, The file logger's two promises: it writes to the file, and it stays silent.  Bot, _teardown(), test_an_error_lands_in_the_given_file(), test_setting_up_twice_does_not_double_the_lines() (+2 more)

### Community 52 - "Snapshot Row Semantics"
Cohesion: 0.14
Nodes (30): Tests for parfum_finder.store: the timestamp helper and the schema.  The one har, One call has to leave a row the search table can read straight off.      The cal, The old price has to survive, and it must not become a second variant.      Appe, first_seen is what says how long a shop has carried a size., The title and URL are information, not identity.      A shop that rewords a list, EDT and EDP are different products at different prices.      Folding them into o, A sold-out size often shows no price at all, and 0 would mean free.      Writing, The column is 0/1, so the tri-state has to land somewhere on purpose.      Unkno (+22 more)

### Community 53 - "CSS Selector Parsing"
Cohesion: 0.24
Nodes (6): BaseHTTPRequestHandler, _Handler, _playwright_usable(), Shared pytest fixtures.  A local HTTP server used by fetch/probe tests: real req, Whether the playwright rung can actually run here, binary included.      Checkin, server_url()

### Community 54 - "Endpoint Schema Fields"
Cohesion: 0.22
Nodes (9): result_item, result_title, result_url, url_template, search, additionalProperties, description, required (+1 more)

### Community 55 - "Multi-House Listing Tests"
Cohesion: 0.31
Nodes (9): _named_profile(), Any, The real fetcher, with a list of every URL it was asked for., A profile whose search page lists two houses' bottles, as shops do., test_a_listing_from_another_house_costs_no_product_request(), test_one_product_listed_under_two_searches_is_read_once(), test_two_shops_sharing_a_url_do_not_read_each_others_pages(), test_without_a_filter_every_listing_is_still_opened() (+1 more)

### Community 56 - "Request Schema Fields"
Cohesion: 0.25
Nodes (8): type, additionalProperties, type, body, request_headers, additionalProperties, description, type

### Community 57 - "Field Confidence Scoring"
Cohesion: 0.18
Nodes (10): _count_result_cards(), live_query(), _no_results_check(), Any, Path, The query this site's fixture was captured with, read back out of its URL., Why an empty results page is suspicious, or why it is not.      A full page that, How many result rows the profile's own selectors find on a search page. (+2 more)

### Community 58 - "Snapshot Row Building"
Cohesion: 0.10
Nodes (24): Any, Connection, Command-line entry point.  Subcommands will be added incrementally as the projec, Scan every perfume against every site and print each site as it lands.      One, Write one site's rows in a transaction of its own.      Per site rather than per, One line per site: which site, how it went, and what it said.      The site id i, _report_line(), _scan_all() (+16 more)

### Community 59 - "Variant Field Types"
Cohesion: 0.22
Nodes (3): Changed, Empty the table for a new scan.          The columns are the same every time now, Submitted

### Community 60 - "Fetch Strategy Selection"
Cohesion: 0.31
Nodes (9): Node, _parse_selector(), Run one "<css>::text" / "<css>::attr(name)" selector inside a node.      The nod, Run one "<css>::text" / "<css>::attr(name)" selector, reading every match., Split a "<css>::text" / "<css>::attr(name)" selector into its two parts., Read the attribute or text of one already-selected node, or None., _read_selected(), select_all() (+1 more)

### Community 61 - "Price History"
Cohesion: 0.29
Nodes (7): price_history(), Row, Return one variant's past readings, newest first, capped at limit.      Empty fo, No history yet is a normal state for a variant, not an error to raise on., The identity a real scan writes must be the identity these lookups accept., test_a_scanned_perfume_can_be_read_back_by_basket_and_history(), test_price_history_is_empty_for_an_unknown_variant()

### Community 62 - "Extraction Layer Enum"
Cohesion: 0.33
Nodes (6): css, embedded_json, endpoint, jsonld, enum, extraction

### Community 63 - "Embedded JSON Parsing"
Cohesion: 0.33
Nodes (6): _balanced_value(), _embedded_documents(), _loads_or_skip(), Yield every JSON document the page hides, in document order., Parse `text` as JSON, yielding nothing when it isn't JSON.      Pages are full o, Return the JSON object or array beginning at or after `start`.      Scanning for

### Community 64 - "Engine Delay Tests"
Cohesion: 0.21
Nodes (12): _check_empty_search(), ExtractionFailed, RuntimeError, A page answered but gave up nothing, where something was expected.      This is, Fail when a search yielded no rows off a page that plainly lists products., _NoRootParser, MonkeyPatch, Record every delay the engine asks for instead of serving it.      Waiting for r (+4 more)

### Community 65 - "JSON-LD Product Walking"
Cohesion: 0.50
Nodes (4): _collect_products(), _has_type(), Walk a parsed JSON-LD block and append every Product found, depth first.      De, Whether a node's "@type" names `name`, as a string or inside a list.      Substr

### Community 66 - "Endpoint Variant Extraction"
Cohesion: 0.25
Nodes (8): exclude_keywords, max_size_ml, size_from, size_pattern, variant_rules, additionalProperties, required, type

### Community 67 - "Price Age Formatting"
Cohesion: 0.50
Nodes (4): format_age(), Turn a price age in days into the words the age column shows., The age column exists to be glanced at, so it is phrased, not printed., test_format_age_reads_as_words_not_a_timestamp()

### Community 68 - "No-Root HTML Parser"
Cohesion: 0.25
Nodes (8): One site's share of a split basket: what to buy there and what it costs.      `s, The cheapest basket split the search found. A heuristic, not a proof.      Every, SplitLeg, SplitPlan, _leg_block(), One site's share of a split: its assigned items, then its own subtotal.      A s, The best-combination block: its legs, grand total, and its honesty checks., _split_block()

### Community 72 - "Protocol"
Cohesion: 0.53
Nodes (4): FormData, Headers, Method, Strategy

### Community 73 - "Row"
Cohesion: 0.50
Nodes (4): extract_endpoint_variants(), Rung 2: read the variant list out of a platform's JSON response.      `document`, test_endpoint_reads_every_size_from_one_response(), test_endpoint_without_a_field_map_reads_nothing()

## Knowledge Gaps
- **152 isolated node(s):** `parfum-finder`, `$schema`, `$id`, `title`, `description` (+147 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `SiteResult` connect `Search/Basket Domain Models` to `TUI App & Screens`, `HTTP/Browser Fetching`, `Search Engine per Site`, `TUI App Shell`, `Search Engine Core`, `Multi-Site Search Run`, `Basket TUI Screen`, `Search Screen Rows`, `Offline Profile Validation`, `Search TUI Screen`, `Snapshot Writing`, `Candidate Filtering`, `Basket Site Scenarios`, `SQLite Store`, `Snapshot Row Building`, `Price History`, `Store Timestamp Tests`?**
  _High betweenness centrality (0.060) - this node is a cross-community bridge._
- **Why does `SearchScreen` connect `Search TUI Screen` to `TUI App & Screens`, `Title Matcher`, `Search/Basket Domain Models`, `TUI Confirm Dialog`, `TUI App Shell`, `Decimal`, `VariantsRead`, `Basket TUI Screen`, `Search Screen Rows`, `Offline Profile Validation`, `Snapshot Writing`, `Candidate Filtering`, `Snapshot Row Building`, `Variant Field Types`?**
  _High betweenness centrality (0.056) - this node is a cross-community bridge._
- **Why does `PlaywrightNotInstalled` connect `HTTP/Browser Fetching` to `Engine Delay Tests`, `Fetch Strategy Probing`, `Search/Basket Domain Models`, `Search Engine per Site`, `Search Engine Core`, `Template Matching`, `Playwright Errors`, `CSS Selector Parsing`, `Discovery CLI Reporting`, `Store Timestamp Tests`?**
  _High betweenness centrality (0.033) - this node is a cross-community bridge._
- **Are the 7 inferred relationships involving `SearchScreen` (e.g. with `ParfumFinderApp` and `SiteResult`) actually correct?**
  _`SearchScreen` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Are the 16 inferred relationships involving `SiteResult` (e.g. with `RawVariant` and `Fetcher`) actually correct?**
  _`SiteResult` has 16 INFERRED edges - model-reasoned connections that need verification._
- **What connects `parfum-finder`, `$schema`, `$id` to the rest of the system?**
  _152 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `TUI App & Screens` be split into smaller, more focused modules?**
  _Cohesion score 0.10536828963795256 - nodes in this community are weakly interconnected._