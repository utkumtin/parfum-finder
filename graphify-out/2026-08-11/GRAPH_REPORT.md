# Graph Report - parfum-finder  (2026-08-11)

## Corpus Check
- 70 files · ~258,420 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1817 nodes · 4738 edges · 74 communities (60 shown, 14 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 173 edges (avg confidence: 0.59)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `040f53b0`
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

## God Nodes (most connected - your core abstractions)
1. `search_site()` - 66 edges
2. `SearchScreen` - 58 edges
3. `_profile()` - 58 edges
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
- `test_write_sheet_asks_confirmation_for_low_score_and_writes_only_after_yes()` --calls--> `WishlistRow`  [INFERRED]
  tests/test_tui.py → src/parfum_finder/sheets.py
- `test_write_sheet_writes_directly_on_a_confident_match()` --calls--> `WishlistRow`  [INFERRED]
  tests/test_tui.py → src/parfum_finder/sheets.py
- `test_the_low_confidence_dialog_can_be_answered_with_the_keyboard_alone()` --indirect_call--> `ConfirmScreen`  [INFERRED]
  tests/test_tui.py → src/parfum_finder/tui/search_screen.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Sites Implementing Variant Pattern C (embedded JSON)** — docs_discovery_report_venco_site, docs_discovery_report_decantall_site, docs_discovery_report_luxurydekant_site, docs_discovery_report_ruxangroup_site, architecture_md_variant_pattern_c [EXTRACTED 1.00]
- **İdeasoft Platform Sites and Endpoint** — docs_discovery_report_dekantparfum_site, docs_discovery_report_dekantdoktoru_site, docs_discovery_report_ideasoft_related_options_endpoint, platforms_readme_ideasoft_json [EXTRACTED 1.00]
- **discover Command Output Artifacts (profile + fixtures + CI validation)** — architecture_md_discover_flow, sites_readme_sites_dir, fixtures_readme_fixtures_dir, github_workflows_ci_validate_profiles_step, architecture_md_validate_command [INFERRED 0.85]

## Communities (74 total, 14 thin omitted)

### Community 0 - "TUI App & Screens"
Cohesion: 0.10
Nodes (98): The Textual-based terminal UI: search and basket screens., _app(), _basket(), _cells(), _days_ago(), _leg(), _ok(), _open_basket() (+90 more)

### Community 1 - "Site Profiles & Templates"
Cohesion: 0.06
Nodes (82): deep_merge(), _load_json(), load_platform_template(), load_platform_templates(), load_site_hooks(), load_site_profile(), Any, Connection (+74 more)

### Community 2 - "Title Matcher"
Cohesion: 0.13
Nodes (9): _Change, BasketReport, Every site's single-site scenario, split by whether it covers everything.      A, BasketScreen, Any, The basket: the list on top, one scenario per site underneath., The three inputs basket.py's pure functions score: items, prices, shipping., _remove() (+1 more)

### Community 3 - "HTTP/Browser Fetching"
Cohesion: 0.08
Nodes (35): browser_session(), fetch(), Strategy, Fetch one URL using exactly the given strategy.      `method`/`data` exist for t, Yield a fetcher that keeps one browser for every playwright page it reads., A multi-site price and stock comparison tool for perfume decants.  Includes a sh, _playwright_usable(), Whether the playwright rung can actually run here, binary included.      Checkin (+27 more)

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
Cohesion: 0.11
Nodes (44): BaseHTTPRequestHandler, CaptureFixture, ask_which_platform(), main(), Path, Scan every site for the perfumes named, store what came back, print it.      One, Ask at the terminal which of several matching templates to apply.      Asked whi, run_search() (+36 more)

### Community 8 - "Architecture Rationale Docs"
Cohesion: 0.05
Nodes (53): basket Subset Enumeration + Local Improvement Algorithm, basket Optimizer (optimize function), Clone/Original Distinction (KLON ← <orijinal>), discover Discovery Flow, engine Concurrency Model (parallel sites, serial within site), Extraction Ladder (jsonld/endpoint/embedded/css), Fail-loud / status=suspect policy, hooks/<id>.py Escape Hatch (+45 more)

### Community 9 - "Search Engine Core"
Cohesion: 0.06
Nodes (69): HTMLParser, _check_empty_search(), _check_variant_control(), ExtractionFailed, _fetch_page(), _headers(), _is_excluded(), _paced_fetcher() (+61 more)

### Community 10 - "Basket Optimizer Core"
Cohesion: 0.12
Nodes (41): Collection, Prices, BasketItem, _ClimbState, optimize(), Basket scenario evaluation. A pure function, no network access, no sqlite.  Inpu, The hill-climb's working assignment plus the running per-site figures.      `sub, Score one site against the basket, or against a subset of it.      `item_ids` is (+33 more)

### Community 11 - "Basket Store & Pricing"
Cohesion: 0.09
Nodes (38): conn(), Connection, Path, Tests for parfum_finder.store: the timestamp helper and the schema.  The one har, An update aimed at a row that isn't there means the caller is out of sync., A snapshot pointing at a variant that doesn't exist has to be rejected.      SQL, Two snapshots written in the same second must resolve to the newer one.      A s, 5 ml at 125,00 TL is 25,00 TL per ml. Stored as kurus, ml as tenths. (+30 more)

### Community 12 - "JSON-LD Product Extraction"
Cohesion: 0.08
Nodes (50): extract_embedded_variants(), extract_jsonld_products(), extract_jsonld_variants(), Read every JSON-LD Product declared on the page, in document order.      A block, Rung 1: read the page's JSON-LD as flat variant rows.      A product that declar, Rung 3: read the JSON blob the page carries but does not display.      Two shape, _fixture(), _one_product_html() (+42 more)

### Community 13 - "Basket TUI Screen"
Cohesion: 0.29
Nodes (7): price_history(), Row, Return one variant's past readings, newest first, capped at limit.      Empty fo, The trend panel reads row 0 as the latest reading, so order is the point.      A, No history yet is a normal state for a variant, not an error to raise on., test_price_history_is_empty_for_an_unknown_variant(), test_price_history_is_newest_first_and_capped_at_limit()

### Community 14 - "Platform Schema"
Cohesion: 0.06
Nodes (31): any, defaults, fingerprint, additionalProperties, items, minItems, type, description (+23 more)

### Community 15 - "Product Extraction"
Cohesion: 0.09
Nodes (30): _as_str(), _balanced_value(), _build_offer(), _build_product(), _collect_offers(), _collect_products(), _collect_variants(), _has_type() (+22 more)

### Community 16 - "Schema Field Patterns"
Cohesion: 0.06
Nodes (33): format, pattern, type, pattern, type, default, type, pattern (+25 more)

### Community 17 - "Offline Profile Validation"
Cohesion: 0.12
Nodes (22): _coerce_in_stock(), _css_variant(), _embedded_documents(), extract_css_variants(), _map_variant(), _parse_selector(), Any, Node (+14 more)

### Community 18 - "Playwright Errors"
Cohesion: 0.19
Nodes (15): PlaywrightNoResponse, RuntimeError, Navigation completed but playwright returned no Response object.      Its own ty, format_report(), _label_platform(), _one_line(), ProbeAttempt, ProbeReport (+7 more)

### Community 19 - "Search TUI Screen"
Cohesion: 0.08
Nodes (39): Exception, Match, find_header_columns(), find_match(), open_worksheet(), Any, PerfumeQuery, Worksheet (+31 more)

### Community 20 - "Snapshot Writing"
Cohesion: 0.11
Nodes (15): Command-line entry point.  Subcommands will be added incrementally as the projec, File logging for the app's own diagnostics.  Nothing here ever writes to the con, _attempt(), _count_jsonld(), _count_product_objects(), _detect_platforms(), Strategy, Strategy measurement: try every rung of the fetch ladder against one URL.  `prob (+7 more)

### Community 21 - "Candidate Filtering"
Cohesion: 0.10
Nodes (42): _age_line(), format_live_report(), format_report(), Every check run against one site's profile, in the order they ran.      Checks s, Whether the profile is old enough to be worth re-discovering., Check one site's profile against that site's saved fixtures.      Never raises f, Validate every site, or just the ones named.      Serial rather than concurrent:, Render the validations as the offline half of the report in APP_FLOW §6.      A (+34 more)

### Community 22 - "Basket Site Scenarios"
Cohesion: 0.15
Nodes (19): collect_prices(), _format_product(), _format_stock(), _format_trial(), _has_exact_price(), PageTrial, Decimal, One page fetched with the chosen strategy and read for JSON-LD.      A fetch tha (+11 more)

### Community 23 - "Price/Size Normalization"
Cohesion: 0.15
Nodes (21): _classify_single_separator(), format_ml(), format_price(), _parse_number(), parse_price(), parse_size_ml(), Decimal, Number parsing and formatting for prices and volumes, plus text folding.  This i (+13 more)

### Community 24 - "JSON Schema Primitives"
Cohesion: 0.11
Nodes (25): integer, null, string, properties, type, type, type, type (+17 more)

### Community 25 - "SQLite Store"
Cohesion: 0.11
Nodes (25): _close_browser(), _fetch_curl_cffi(), _fetch_httpx(), _fetch_playwright(), FetchResult, _launch_browser(), Any, FormData (+17 more)

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
Cohesion: 0.14
Nodes (23): DiscoveryReport, FieldConfidence, _flatten_defaults(), _format_choice(), _format_confidence(), _format_defaults(), _format_fingerprint(), _format_fixtures() (+15 more)

### Community 30 - "Store Timestamp Tests"
Cohesion: 0.21
Nodes (6): Decimal, Row, One priced size, exactly as the table shows it and as a keypress needs it., The default order: typed order, product, site, size.          The typed order co, The order once a column has been picked: the site layer drops out.          Aski, _ResultRow

### Community 31 - "Live Profile Validation"
Cohesion: 0.14
Nodes (13): CacheKey, Fetcher, SnapshotRow, _listing_filter(), Any, CandidateFilter, PerfumeQuery, SiteResult (+5 more)

### Community 32 - "Variant Extraction Fields"
Cohesion: 0.11
Nodes (18): attribute, in_stock, price, script, size_raw, type, properties, additionalProperties (+10 more)

### Community 33 - "_ResultRow"
Cohesion: 0.05
Nodes (89): _canonical(), _covers(), _ends_with(), _index_of(), Match, _match_text(), match_title(), _own_identity() (+81 more)

### Community 34 - "Fetch Strategy Probing"
Cohesion: 0.21
Nodes (13): Connection, _listing_filter(), Any, CandidateFilter, PerfumeQuery, SiteResult, Scan every perfume against every site and print each site as it lands.      One, Decide, from a search result's own title, whether to open its page. (+5 more)

### Community 35 - "Platform Field Mapping"
Cohesion: 0.12
Nodes (16): field_map, product_json, source, variants_path, additionalProperties, allOf, description, required (+8 more)

### Community 36 - "Shipping Config Schema"
Cohesion: 0.14
Nodes (14): free_shipping_threshold_kurus, shipping_cost_kurus, minimum, type, free_shipping_threshold_kurus, notes, shipping, shipping_cost_kurus (+6 more)

### Community 38 - "TUI Confirm Dialog"
Cohesion: 0.13
Nodes (26): One priced size of one perfume on one site, ready to be written.      The perfum, Write a whole scan at once and return how many prices were recorded.      Every, SnapshotRow, write_snapshots(), The drop happens here so no caller can forget it.      Both the CLI and the scre, The old price has to survive, and it must not become a second variant.      Appe, The title and URL are information, not identity.      A shop that rewords a list, EDT and EDP are different products at different prices.      Folding them into o (+18 more)

### Community 40 - "Fetch Backends"
Cohesion: 0.14
Nodes (14): curl_cffi, httpx, playwright, result_item, result_title, result_url, strategy, url_template (+6 more)

### Community 41 - "HTTP Request Schema"
Cohesion: 0.14
Nodes (14): GET, POST, properties, default, enum, type, type, type (+6 more)

### Community 42 - "Fixture Fetcher (Tests)"
Cohesion: 0.33
Nodes (10): Path, Attach the rotating file handler and return where it writes.      Safe to call m, setup_logging(), Path, The file logger's two promises: it writes to the file, and it stays silent.  Bot, _teardown(), test_an_error_lands_in_the_given_file(), test_setting_up_twice_does_not_double_the_lines() (+2 more)

### Community 44 - "Decant Variant Rules"
Cohesion: 0.08
Nodes (44): Fetcher, Protocol, Anything that can stand in for `fetch`.      Offline profile validation runs the, _age_of(), Check, _count_result_cards(), _first_result_url(), _LayerUnavailable (+36 more)

### Community 45 - "Multi-Site Search Run"
Cohesion: 0.22
Nodes (9): SiteResult, Turn one site's hits into the rows write_snapshots is ready to store.      Share, snapshot_rows(), A shop's imitation must not be stored as the perfume it imitates.      The clone, Another house's bottle on the same results page must not enter this history., EDT and EDP are different products, so the row has to say which one this was., test_snapshot_rows_drops_a_title_the_matcher_rejects(), test_snapshot_rows_marks_a_clone_instead_of_filing_it_as_the_original() (+1 more)

### Community 46 - "Offline Validation Fixtures"
Cohesion: 0.25
Nodes (8): type, additionalProperties, type, body, request_headers, additionalProperties, description, type

### Community 47 - "Basket Domain Logic"
Cohesion: 0.05
Nodes (102): apply_variant_rules(), _candidates_to_open(), CacheKey, CandidateFilter, Path, VariantsRead, Run one site and classify what came back instead of raising.      It is also whe, Run every site against one query, all at once, and report each separately. (+94 more)

### Community 48 - "._build_rows"
Cohesion: 0.25
Nodes (8): exclude_keywords, max_size_ml, size_from, size_pattern, variant_rules, additionalProperties, required, type

### Community 50 - "Profile Age Checks"
Cohesion: 0.16
Nodes (13): _choose_strategy(), _match_platforms(), Any, Path, Strategy, _qualifies(), The strategy the trials actually ran with., Pick the cheapest strategy that came back with real content, or None.      probe (+5 more)

### Community 51 - "._refresh_table"
Cohesion: 0.09
Nodes (8): Changed, HeaderSelected, RowSelected, The initial screen: search bar, streaming results table, notices, footer., Empty the table for a new scan.          The columns are the same every time now, What each site charges for the product a block is about.          One entry per, SearchScreen, Submitted

### Community 52 - "._cells"
Cohesion: 0.29
Nodes (5): Protocol, Path, Path, What this screen needs of engine.run_site.      A protocol rather than a plain c, SiteRunner

### Community 53 - "conftest.py"
Cohesion: 0.16
Nodes (22): basket_lines(), basket_prices(), _perfume_id(), _product_id(), Connection, SQLite persistence: an append-only price history.  Tables: sites, perfumes, prod, Write one scan's reading of one size, and return its snapshot id.      The perfu, Do the writing, without opening a transaction of its own. (+14 more)

### Community 54 - "Endpoint Schema Fields"
Cohesion: 0.22
Nodes (9): result_item, result_title, result_url, url_template, search, additionalProperties, description, required (+1 more)

### Community 55 - "tui/__init__.py"
Cohesion: 0.17
Nodes (12): add_basket_item(), now_iso(), Return the current UTC time as 'YYYY-MM-DDTHH:MM:SSZ'.      Every timestamp writ, Add a size of a perfume to the basket, and return the basket_item_id.      The p, A basket line for a perfume nobody has priced is a bug, not a state to keep., A stale reading must never outrank the one taken after it.      latest_prices al, A 10 ml listing must never fill a basket line asking for 5 ml.      The matrix j, test_add_basket_item_refuses_a_perfume_with_no_price_on_record() (+4 more)

### Community 57 - "_FixtureFetcher"
Cohesion: 0.31
Nodes (7): _DeadSite, FormData, Headers, Method, Strategy, A host that cannot be reached at all., test_an_unreachable_site_is_not_reported_as_a_broken_profile()

### Community 58 - "ComposeResult"
Cohesion: 0.11
Nodes (28): One site's share of a split basket: what to buy there and what it costs.      `s, The cheapest basket split the search found. A heuristic, not a proof.      Every, SplitLeg, SplitPlan, basket_sites(), BasketLine, BasketPrice, BasketSite (+20 more)

### Community 59 - "_named_profile"
Cohesion: 0.33
Nodes (6): css, embedded_json, endpoint, jsonld, enum, extraction

### Community 61 - "SiteScenario"
Cohesion: 0.40
Nodes (4): What it would cost to buy some or all of the basket from one site.      `covered, SiteScenario, The two or three lines one site's scenario takes up on screen., _scenario_block()

### Community 62 - "format_age"
Cohesion: 0.50
Nodes (4): format_age(), Turn a price age in days into the words the age column shows., The age column exists to be glanced at, so it is phrased, not printed., test_format_age_reads_as_words_not_a_timestamp()

### Community 67 - "_resolve_platform"
Cohesion: 0.50
Nodes (3): The template this site's profile would be based on, if any., Which of the matching templates gets applied, or None for none of them.      One, _resolve_platform()

### Community 71 - "basket_prices"
Cohesion: 0.18
Nodes (11): One call has to leave a row the search table can read straight off.      The cal, first_seen is what says how long a shop has carried a size., The column is 0/1, so the tri-state has to land somewhere on purpose.      Unkno, Sites come from the profiles, so an id nothing synced is a mistake., Whether an out-of-stock price counts as missing is the caller's call.      Dropp, _record(), test_a_second_scan_moves_last_seen_and_keeps_first_seen(), test_a_snapshot_for_an_unknown_site_is_refused() (+3 more)

### Community 72 - "ComposeResult"
Cohesion: 0.14
Nodes (7): ComposeResult, Pressed, ComposeResult, ConfirmScreen, Path, Asks before a low-confidence match is written to the basket.      The two answer, Static

## Knowledge Gaps
- **154 isolated node(s):** `parfum-finder`, `$schema`, `$id`, `title`, `description` (+149 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **14 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `SearchScreen` connect `._refresh_table` to `TUI App & Screens`, `Search/Basket Domain Models`, `ComposeResult`, `Search TUI Screen`, `Snapshot Writing`, `Store Timestamp Tests`, `Live Profile Validation`?**
  _High betweenness centrality (0.050) - this node is a cross-community bridge._
- **Why does `ParfumFinderApp` connect `Search/Basket Domain Models` to `TUI App & Screens`, `CLI Entry Points`, `._refresh_table`, `Snapshot Writing`, `._cells`?**
  _High betweenness centrality (0.028) - this node is a cross-community bridge._
- **Why does `search_site()` connect `Basket Domain Logic` to `Search Engine Core`, `Decant Variant Rules`, `Candidate Filtering`, `Site Profiles & Templates`?**
  _High betweenness centrality (0.026) - this node is a cross-community bridge._
- **Are the 4 inferred relationships involving `SearchScreen` (e.g. with `ParfumFinderApp` and `SheetsError`) actually correct?**
  _`SearchScreen` has 4 INFERRED edges - model-reasoned connections that need verification._
- **What connects `parfum-finder`, `$schema`, `$id` to the rest of the system?**
  _154 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `TUI App & Screens` be split into smaller, more focused modules?**
  _Cohesion score 0.09656565656565656 - nodes in this community are weakly interconnected._
- **Should `Site Profiles & Templates` be split into smaller, more focused modules?**
  _Cohesion score 0.0560875512995896 - nodes in this community are weakly interconnected._