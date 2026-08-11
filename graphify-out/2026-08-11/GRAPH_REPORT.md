# Graph Report - parfum-finder  (2026-08-11)

## Corpus Check
- 70 files · ~258,831 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1828 nodes · 4680 edges · 84 communities (62 shown, 22 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 141 edges (avg confidence: 0.6)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `de55777f`
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
- ._build_rows
- test_engine.py
- Profile Age Checks
- ._refresh_table
- ._cells
- conftest.py
- Endpoint Schema Fields
- tui/__init__.py
- Request Schema Fields
- _FixtureFetcher
- ComposeResult
- _named_profile
- _NoRootParser
- SiteScenario
- format_age
- CandidateFilter
- LogCaptureFixture
- MonkeyPatch
- ParfumFinderApp
- _resolve_platform
- Connection
- Variant Pattern A
- Project Root
- basket_prices
- ComposeResult
- Row
- _NoRootParser
- field_map
- exclude_keywords
- SiteResult
- CacheKey
- Decimal
- Node
- RuntimeError
- VariantsRead
- Exception

## God Nodes (most connected - your core abstractions)
1. `search_site()` - 65 edges
2. `_profile()` - 58 edges
3. `SearchScreen` - 58 edges
4. `discover()` - 54 edges
5. `_write_profile()` - 46 edges
6. `BasketScreen` - 46 edges
7. `_app()` - 45 edges
8. `_submit_query()` - 44 edges
9. `match_title()` - 43 edges
10. `_sync()` - 42 edges

## Surprising Connections (you probably didn't know these)
- `Shipping Non-linearity Rationale (why cheapest-per-item is wrong)` --semantically_similar_to--> `sites/ Site Profile Directory`  [INFERRED] [semantically similar]
  ARCHITECTURE.md → sites/README.md
- `Variant Pattern B (dropdown + AJAX price)` --semantically_similar_to--> `Variant Selector Detector Fix (WooCommerce 'variation' vs 'variant')`  [INFERRED] [semantically similar]
  ARCHITECTURE.md → docs/discovery-report.md
- `_NoRootParser` --uses--> `ExtractionFailed`  [INFERRED]
  tests/test_engine.py → src/parfum_finder/engine.py
- `test_a_hook_that_reads_nothing_is_named_as_the_culprit()` --indirect_call--> `ExtractionFailed`  [INFERRED]
  tests/test_engine.py → src/parfum_finder/engine.py
- `test_a_product_page_with_no_root_names_its_body_size()` --indirect_call--> `ExtractionFailed`  [INFERRED]
  tests/test_engine.py → src/parfum_finder/engine.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Sites Implementing Variant Pattern C (embedded JSON)** — docs_discovery_report_venco_site, docs_discovery_report_decantall_site, docs_discovery_report_luxurydekant_site, docs_discovery_report_ruxangroup_site, architecture_md_variant_pattern_c [EXTRACTED 1.00]
- **İdeasoft Platform Sites and Endpoint** — docs_discovery_report_dekantparfum_site, docs_discovery_report_dekantdoktoru_site, docs_discovery_report_ideasoft_related_options_endpoint, platforms_readme_ideasoft_json [EXTRACTED 1.00]
- **discover Command Output Artifacts (profile + fixtures + CI validation)** — architecture_md_discover_flow, sites_readme_sites_dir, fixtures_readme_fixtures_dir, github_workflows_ci_validate_profiles_step, architecture_md_validate_command [INFERRED 0.85]

## Communities (84 total, 22 thin omitted)

### Community 0 - "TUI App & Screens"
Cohesion: 0.09
Nodes (100): What one site had to say about one query, and how much to trust it.      Four st, SiteResult, The Textual-based terminal UI: search and basket screens., _app(), _basket(), _cells(), _days_ago(), _leg() (+92 more)

### Community 1 - "Site Profiles & Templates"
Cohesion: 0.06
Nodes (86): _check_hook_kinds(), deep_merge(), _load_json(), load_platform_template(), load_platform_templates(), load_site_hooks(), load_site_profile(), Any (+78 more)

### Community 2 - "Title Matcher"
Cohesion: 0.12
Nodes (13): _Change, BasketLine, One row of the basket: a size of a perfume, with the identity spelled out., _BasketRow, BasketScreen, _label(), Any, The basket: the list on top, one scenario per site underneath. (+5 more)

### Community 3 - "HTTP/Browser Fetching"
Cohesion: 0.05
Nodes (58): BaseHTTPRequestHandler, browser_session(), _close_browser(), fetch(), _fetch_curl_cffi(), _fetch_httpx(), _fetch_playwright(), FetchResult (+50 more)

### Community 4 - "Search/Basket Domain Models"
Cohesion: 0.08
Nodes (100): Runner, Screen, ParfumFinderApp, Root app: pushes the search screen on mount., SystemCommand, _app(), _basket_count(), _named_result() (+92 more)

### Community 5 - "Search Engine per Site"
Cohesion: 0.21
Nodes (15): probe(), Fetch `url` with every strategy and report diagnostics for each.      timeout_s, MonkeyPatch, Tests for parfum_finder.probe.  probe() always tries all three strategies -- the, test_probe_counts_jsonld_product_and_platform_signature(), test_probe_counts_product_across_jsonld_root_shapes(), test_probe_counts_product_markup_without_any_jsonld(), test_probe_counts_products_nested_below_the_top_level() (+7 more)

### Community 6 - "Platform Discovery Flow"
Cohesion: 0.15
Nodes (59): PlatformChooser, _ask_chooser(), discover(), Put the question only when there is one, and hold the answer to it.      An answ, Measure the strategies a site needs, then read its JSON-LD with the winner., _attempt(), _fake_probe(), Any (+51 more)

### Community 7 - "CLI Entry Points"
Cohesion: 0.10
Nodes (55): CaptureFixture, Connection, PerfumeQuery, ask_which_platform(), _listing_filter(), main(), Any, CandidateFilter (+47 more)

### Community 8 - "Architecture Rationale Docs"
Cohesion: 0.05
Nodes (53): basket Subset Enumeration + Local Improvement Algorithm, basket Optimizer (optimize function), Clone/Original Distinction (KLON ← <orijinal>), discover Discovery Flow, engine Concurrency Model (parallel sites, serial within site), Extraction Ladder (jsonld/endpoint/embedded/css), Fail-loud / status=suspect policy, hooks/<id>.py Escape Hatch (+45 more)

### Community 9 - "Search Engine Core"
Cohesion: 0.09
Nodes (44): Node, SiteHooks, _check_empty_search(), _check_variant_control(), _fetch_page(), _headers(), _paced_fetcher(), _page_offers_sizes() (+36 more)

### Community 10 - "Basket Optimizer Core"
Cohesion: 0.15
Nodes (33): Collection, BasketItem, optimize(), Score one site against the basket, or against a subset of it.      `item_ids` is, Search for the cheapest way to split the basket across several sites.      Retur, One line of the shopping list: a basket row, not a unit count.      `item_id` is, site_scenario(), Tests for parfum_finder.basket: single-site scenario scoring.  Money is INTEGER (+25 more)

### Community 11 - "Basket Store & Pricing"
Cohesion: 0.09
Nodes (38): add_basket_item(), basket_lines(), Add a size of a perfume to the basket, and return the basket_item_id.      The p, Return every basket line, oldest add first.      Ordered by added_at with basket, Connection, Two snapshots written in the same second must resolve to the newer one.      A s, 5 ml at 125,00 TL is 25,00 TL per ml. Stored as kurus, ml as tenths., No price yet means no row, so the basket LEFT JOIN reads it as missing. (+30 more)

### Community 12 - "JSON-LD Product Extraction"
Cohesion: 0.09
Nodes (46): extract_embedded_variants(), extract_jsonld_products(), extract_jsonld_variants(), Read every JSON-LD Product declared on the page, in document order.      A block, Rung 1: read the page's JSON-LD as flat variant rows.      A product that declar, Rung 3: read the JSON blob the page carries but does not display.      Two shape, _fixture(), _one_product_html() (+38 more)

### Community 13 - "Basket TUI Screen"
Cohesion: 0.29
Nodes (7): price_history(), Row, Return one variant's past readings, newest first, capped at limit.      Empty fo, The trend panel reads row 0 as the latest reading, so order is the point.      A, No history yet is a normal state for a variant, not an error to raise on., test_price_history_is_empty_for_an_unknown_variant(), test_price_history_is_newest_first_and_capped_at_limit()

### Community 14 - "Platform Schema"
Cohesion: 0.06
Nodes (31): any, defaults, fingerprint, additionalProperties, items, minItems, type, description (+23 more)

### Community 15 - "Product Extraction"
Cohesion: 0.05
Nodes (62): _as_str(), _balanced_value(), _build_offer(), _build_product(), _coerce_in_stock(), _collect_offers(), _collect_products(), _collect_variants() (+54 more)

### Community 16 - "Schema Field Patterns"
Cohesion: 0.05
Nodes (39): css, embedded_json, endpoint, jsonld, format, pattern, type, pattern (+31 more)

### Community 17 - "Offline Profile Validation"
Cohesion: 0.15
Nodes (27): Run one site and classify what came back instead of raising.      It is also whe, run_site(), _counting_fetcher(), _profile(), FetchResult, Answer each call with the next canned result, then repeat the last one., A minimal working profile, with the fields a case cares about swapped in., test_a_dead_link_selector_is_suspect_not_empty() (+19 more)

### Community 18 - "Playwright Errors"
Cohesion: 0.12
Nodes (29): HTMLParser, PageTrial, One page fetched with the chosen strategy and read for JSON-LD.      A fetch tha, PlaywrightNoResponse, PlaywrightNotInstalled, RuntimeError, The "playwright" strategy was requested but cannot run at all.      Covers both, Navigation completed but playwright returned no Response object.      Its own ty (+21 more)

### Community 19 - "Search TUI Screen"
Cohesion: 0.08
Nodes (40): Exception, Match, find_header_columns(), find_match(), open_worksheet(), Any, PerfumeQuery, Worksheet (+32 more)

### Community 20 - "Snapshot Writing"
Cohesion: 0.15
Nodes (23): Decimal, apply_variant_rules(), _is_excluded(), One decant size of one product, in the units the database stores.      Tenths of, Turn raw size rows into decant variants, dropping what is not a decant.      Thr, Read one row's volume in millilitres, or None if the text does not say.      "fi, Whether this row is something other than a decant.      The size threshold is in, Convert a price in lira to whole kuruş.      Integers all the way, never a float (+15 more)

### Community 21 - "Candidate Filtering"
Cohesion: 0.19
Nodes (17): format_live_report(), Run one site's profile against the real site.      Same contract as offline mode, Render offline and live results side by side, as APP_FLOW §6 shows them.      Bo, validate_live(), _DeadSite, _FakeSite, _fixture_site(), M5's own criterion: when a profile stops agreeing with its site's real markup, o (+9 more)

### Community 22 - "Basket Site Scenarios"
Cohesion: 0.22
Nodes (14): format_report(), Every site that has a profile, sorted so reports read the same way twice., Validate every site, or just the ones named.      Serial rather than concurrent:, Render the validations as the offline half of the report in APP_FLOW §6.      A, site_ids(), validate_all_offline(), _iso_days_ago(), A discovered_at stamp that lands a fixed number of days in the past.      Relati (+6 more)

### Community 23 - "Price/Size Normalization"
Cohesion: 0.14
Nodes (23): casefold_tr(), _classify_single_separator(), format_ml(), format_price(), _parse_number(), parse_price(), parse_size_ml(), Decimal (+15 more)

### Community 24 - "JSON Schema Primitives"
Cohesion: 0.11
Nodes (25): integer, null, string, properties, type, type, type, type (+17 more)

### Community 25 - "SQLite Store"
Cohesion: 0.22
Nodes (9): _FixtureFetcher, _path(), FormData, Headers, Method, Strategy, Serves one site's saved capture in place of the network.      Only three kinds o, The one real result card that led to the captured product page.          Cut out (+1 more)

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
Cohesion: 0.07
Nodes (51): _choose_strategy(), collect_prices(), DiscoveryReport, FieldConfidence, _flatten_defaults(), _format_choice(), _format_confidence(), _format_defaults() (+43 more)

### Community 30 - "Store Timestamp Tests"
Cohesion: 0.12
Nodes (5): Row, RowSelected, One priced size, exactly as the table shows it and as a keypress needs it., The order once a column has been picked: the site layer drops out.          Aski, _ResultRow

### Community 31 - "Live Profile Validation"
Cohesion: 0.17
Nodes (12): CacheKey, _candidates_to_open(), CandidateFilter, Path, Run every site against one query, all at once, and report each separately., Narrow the search results down to the pages worth a request.      The first one, run_sites(), test_a_dead_site_does_not_take_the_others_down() (+4 more)

### Community 32 - "Variant Extraction Fields"
Cohesion: 0.12
Nodes (16): attribute, script, type, additionalProperties, allOf, description, properties, type (+8 more)

### Community 33 - "_ResultRow"
Cohesion: 0.05
Nodes (89): _canonical(), _covers(), _ends_with(), _index_of(), Match, _match_text(), match_title(), _own_identity() (+81 more)

### Community 35 - "Platform Field Mapping"
Cohesion: 0.18
Nodes (11): field_map, product_json, source, variants_path, required, additionalProperties, allOf, description (+3 more)

### Community 36 - "Shipping Config Schema"
Cohesion: 0.14
Nodes (14): free_shipping_threshold_kurus, shipping_cost_kurus, minimum, type, free_shipping_threshold_kurus, notes, shipping, shipping_cost_kurus (+6 more)

### Community 38 - "TUI Confirm Dialog"
Cohesion: 0.10
Nodes (35): One priced size of one perfume on one site, ready to be written.      The perfum, Write a whole scan at once and return how many prices were recorded.      Every, SnapshotRow, write_snapshots(), The drop happens here so no caller can forget it.      Both the CLI and the scre, One call has to leave a row the search table can read straight off.      The cal, The old price has to survive, and it must not become a second variant.      Appe, first_seen is what says how long a shop has carried a size. (+27 more)

### Community 40 - "Fetch Backends"
Cohesion: 0.14
Nodes (14): curl_cffi, httpx, playwright, result_item, result_title, result_url, strategy, url_template (+6 more)

### Community 41 - "HTTP Request Schema"
Cohesion: 0.14
Nodes (14): GET, POST, properties, default, enum, type, type, type (+6 more)

### Community 42 - "Fixture Fetcher (Tests)"
Cohesion: 0.27
Nodes (11): Path, File logging for the app's own diagnostics.  Nothing here ever writes to the con, Attach the rotating file handler and return where it writes.      Safe to call m, setup_logging(), Path, The file logger's two promises: it writes to the file, and it stays silent.  Bot, _teardown(), test_an_error_lands_in_the_given_file() (+3 more)

### Community 44 - "Decant Variant Rules"
Cohesion: 0.11
Nodes (26): Fetcher, Protocol, Anything that can stand in for `fetch`.      Offline profile validation runs the, _age_of(), Check, _first_result_url(), _LayerUnavailable, _probe_layer() (+18 more)

### Community 45 - "Multi-Site Search Run"
Cohesion: 0.22
Nodes (9): SiteResult, Turn one site's hits into the rows write_snapshots is ready to store.      Share, snapshot_rows(), A shop's imitation must not be stored as the perfume it imitates.      The clone, Another house's bottle on the same results page must not enter this history., EDT and EDP are different products, so the row has to say which one this was., test_snapshot_rows_drops_a_title_the_matcher_rejects(), test_snapshot_rows_marks_a_clone_instead_of_filing_it_as_the_original() (+1 more)

### Community 46 - "Offline Validation Fixtures"
Cohesion: 0.25
Nodes (8): type, additionalProperties, type, body, request_headers, additionalProperties, description, type

### Community 47 - "Basket Domain Logic"
Cohesion: 0.09
Nodes (41): RuntimeError, ExtractionFailed, A page answered but gave up nothing, where something was expected.      This is, Run one query against one site and read every hit's sizes.      Everything site-, search_site(), _named_profile(), Any, Fetcher (+33 more)

### Community 48 - "._build_rows"
Cohesion: 0.18
Nodes (12): basket_prices(), basket_sites(), BasketPrice, BasketSite, One site's latest price for one basket line, only when it has one.      Rows wit, A site the basket screen is willing to show a column for.      Deliberately just, Return the basket price matrix: one row per (line, site) that has a price., Return every enabled site, for the basket screen's fixed set of columns.      So (+4 more)

### Community 50 - "Profile Age Checks"
Cohesion: 0.29
Nodes (13): Check one site's profile against that site's saved fixtures.      Never raises f, validate_offline(), _corrupted_sites_dir(), Any, Path, A sites/ directory holding one real profile with fields overwritten.      The re, test_a_dead_price_selector_is_caught_as_the_extraction_step(), test_a_dead_search_selector_is_caught_as_the_search_step() (+5 more)

### Community 51 - "._refresh_table"
Cohesion: 0.08
Nodes (14): Changed, HeaderSelected, SnapshotRow, Any, SiteResult, One perfume of a search, as typed and as parsed.      The index is the outermost, The initial screen: search bar, streaming results table, notices, footer., Scan one site for every perfume of this search, one at a time.          Serial i (+6 more)

### Community 52 - "._cells"
Cohesion: 0.12
Nodes (11): Fetcher, Protocol, Path, The Textual App root. Handles screen navigation and is the app's default entry p, Path, _listing_filter(), CandidateFilter, PerfumeQuery (+3 more)

### Community 53 - "conftest.py"
Cohesion: 0.24
Nodes (16): _perfume_id(), _product_id(), Connection, SQLite persistence: an append-only price history.  Tables: sites, perfumes, prod, Write one scan's reading of one size, and return its snapshot id.      The perfu, Do the writing, without opening a transaction of its own., Delete one basket line, and say whether there was one to delete.      Returns Fa, Set a basket line's quantity, clamped to at least 1, and return it.      The tab (+8 more)

### Community 54 - "Endpoint Schema Fields"
Cohesion: 0.22
Nodes (9): result_item, result_title, result_url, url_template, search, additionalProperties, description, required (+1 more)

### Community 55 - "tui/__init__.py"
Cohesion: 0.15
Nodes (14): now_iso(), Return the current UTC time as 'YYYY-MM-DDTHH:MM:SSZ'.      Every timestamp writ, conn(), Path, Tests for parfum_finder.store: the timestamp helper and the schema.  The one har, An update aimed at a row that isn't there means the caller is out of sync., A snapshot pointing at a variant that doesn't exist has to be rejected.      SQL, Reopening an existing database must not wipe or re-raise on its schema. (+6 more)

### Community 57 - "_FixtureFetcher"
Cohesion: 0.22
Nodes (10): Prices, BasketReport, _ClimbState, Basket scenario evaluation. A pure function, no network access, no sqlite.  Inpu, The hill-climb's working assignment plus the running per-site figures.      `sub, Score every enabled site against the whole basket and sort the results.      Sit, One site's shipping terms, read once and reused for every scenario.      `free_s, Every site's single-site scenario, split by whether it covers everything.      A (+2 more)

### Community 58 - "ComposeResult"
Cohesion: 0.12
Nodes (20): One site's share of a split basket: what to buy there and what it costs.      `s, The cheapest basket split the search found. A heuristic, not a proof.      Every, What it would cost to buy some or all of the basket from one site.      `covered, SiteScenario, SplitLeg, SplitPlan, _heading(), _leg_block() (+12 more)

### Community 59 - "_named_profile"
Cohesion: 0.18
Nodes (8): _age_line(), Every check run against one site's profile, in the order they ran.      Checks s, Whether the profile is old enough to be worth re-discovering., The check that broke, or None if the profile is intact., Validate every site against the live web, or just the ones named.      Serial li, The age note for one site, or None when its age is unremarkable.      A profile, SiteValidation, validate_all_live()

### Community 61 - "SiteScenario"
Cohesion: 0.18
Nodes (10): _count_result_cards(), live_query(), _no_results_check(), Any, Path, The query this site's fixture was captured with, read back out of its URL., Why an empty results page is suspicious, or why it is not.      A full page that, How many result rows the profile's own selectors find on a search page. (+2 more)

### Community 62 - "format_age"
Cohesion: 0.50
Nodes (4): format_age(), Turn a price age in days into the words the age column shows., The age column exists to be glanced at, so it is phrased, not printed., test_format_age_reads_as_words_not_a_timestamp()

### Community 67 - "_resolve_platform"
Cohesion: 0.50
Nodes (3): The template this site's profile would be based on, if any., Which of the matching templates gets applied, or None for none of them.      One, _resolve_platform()

### Community 71 - "basket_prices"
Cohesion: 0.36
Nodes (10): Path, Give the test profile's site id a hook file. The id is what binds them., test_a_before_search_that_returns_no_query_is_refused(), test_a_broken_hook_is_an_error_not_a_silent_empty(), test_a_hook_that_reads_nothing_is_named_as_the_culprit(), test_after_search_can_drop_a_result_the_selectors_could_not(), test_before_search_rewrites_the_query_that_is_actually_sent(), test_parse_variants_returning_none_leaves_the_page_to_the_profile() (+2 more)

### Community 72 - "ComposeResult"
Cohesion: 0.14
Nodes (7): ComposeResult, Pressed, ComposeResult, ConfirmScreen, Path, Asks before a low-confidence match is written to the basket.      The two answer, Static

### Community 74 - "_NoRootParser"
Cohesion: 0.29
Nodes (7): _NoRootParser, MonkeyPatch, Record every delay the engine asks for instead of serving it.      Waiting for r, Stands in for HTMLParser when a page's markup cannot be read at all.      select, slept(), test_a_product_page_with_no_root_names_its_body_size(), test_a_search_page_with_no_root_names_its_body_size()

### Community 75 - "field_map"
Cohesion: 0.29
Nodes (7): in_stock, price, size_raw, additionalProperties, required, type, field_map

### Community 76 - "exclude_keywords"
Cohesion: 0.29
Nodes (7): items, type, type, items, type, exclude_keywords, needs_review

## Knowledge Gaps
- **154 isolated node(s):** `parfum-finder`, `$schema`, `$id`, `title`, `description` (+149 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **22 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `SearchScreen` connect `._refresh_table` to `TUI App & Screens`, `Search/Basket Domain Models`, `ComposeResult`, `Search TUI Screen`, `._cells`, `Store Timestamp Tests`?**
  _High betweenness centrality (0.039) - this node is a cross-community bridge._
- **Why does `BasketScreen` connect `Title Matcher` to `TUI App & Screens`, `_ResultRow`, `TUI Confirm Dialog`, `ComposeResult`, `Basket Optimizer Core`, `._build_rows`, `._cells`, `_FixtureFetcher`, `ComposeResult`?**
  _High betweenness centrality (0.035) - this node is a cross-community bridge._
- **Why does `PerfumeQuery` connect `_ResultRow` to `Title Matcher`, `TUI Confirm Dialog`, `Multi-Site Search Run`, `._build_rows`, `conftest.py`, `ComposeResult`?**
  _High betweenness centrality (0.022) - this node is a cross-community bridge._
- **Are the 4 inferred relationships involving `SearchScreen` (e.g. with `ParfumFinderApp` and `SheetsError`) actually correct?**
  _`SearchScreen` has 4 INFERRED edges - model-reasoned connections that need verification._
- **What connects `parfum-finder`, `$schema`, `$id` to the rest of the system?**
  _154 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `TUI App & Screens` be split into smaller, more focused modules?**
  _Cohesion score 0.0937682003494467 - nodes in this community are weakly interconnected._
- **Should `Site Profiles & Templates` be split into smaller, more focused modules?**
  _Cohesion score 0.05518925518925519 - nodes in this community are weakly interconnected._