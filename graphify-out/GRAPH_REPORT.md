# Graph Report - parfum-finder  (2026-08-10)

## Corpus Check
- 68 files · ~248,348 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1696 nodes · 4590 edges · 62 communities (59 shown, 3 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 187 edges (avg confidence: 0.57)
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
- Request Schema Fields
- Snapshot Row Building
- Fetch Strategy Selection
- Price History
- Extraction Layer Enum
- Variant Pattern A
- Project Root

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

## Communities (62 total, 3 thin omitted)

### Community 0 - "TUI App & Screens"
Cohesion: 0.11
Nodes (88): The Textual-based terminal UI: search and basket screens., _app(), _basket(), _cells(), _days_ago(), _leg(), _ok(), _open_basket() (+80 more)

### Community 1 - "Site Profiles & Templates"
Cohesion: 0.06
Nodes (79): Command-line entry point.  Subcommands will be added incrementally as the projec, Path, File logging for the app's own diagnostics.  Nothing here ever writes to the con, Attach the rotating file handler and return where it writes.      Safe to call m, setup_logging(), _check_hook_kinds(), deep_merge(), _load_json() (+71 more)

### Community 2 - "Title Matcher"
Cohesion: 0.15
Nodes (27): Match, match_title(), PerfumeQuery, The perfume being looked for, split into its three identity parts.      `concent, One site title judged against the query.      `concentration` is what the title, Judge one site title against a query, or None if it is not that perfume.      No, test_a_brand_needs_all_of_its_words_not_one(), test_a_brand_only_query_matches_a_title_that_is_only_that_brand() (+19 more)

### Community 3 - "HTTP/Browser Fetching"
Cohesion: 0.07
Nodes (37): BaseHTTPRequestHandler, browser_session(), fetch(), Strategy, Fetch one URL using exactly the given strategy.      `method`/`data` exist for t, Yield a fetcher that keeps one browser for every playwright page it reads., _Handler, _playwright_usable() (+29 more)

### Community 4 - "Search/Basket Domain Models"
Cohesion: 0.07
Nodes (99): LogCaptureFixture, Pressed, One decant size of one product, in the units the database stores.      Tenths of, A candidate together with the decant sizes its product page offers., What one site had to say about one query, and how much to trust it.      Four st, SearchHit, SiteResult, Variant (+91 more)

### Community 5 - "Search Engine per Site"
Cohesion: 0.16
Nodes (23): parse_query(), Split one typed line, "Dior Sauvage EDP", into the three identity parts.      Th, Whether a search result's own listing text is worth opening the page for.      J, title_could_match(), Tests for parfum_finder.matcher.  The thing being defended here is not "does it, test_a_brand_the_shop_writes_out_in_full_does_not_cost_the_match(), test_a_clone_is_still_shown_because_it_may_be_worth_buying(), test_a_clones_own_name_is_scored_without_what_it_imitates() (+15 more)

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
Cohesion: 0.07
Nodes (57): HTMLParser, _candidates_to_open(), _check_empty_search(), _check_variant_control(), ExtractionFailed, _fetch_page(), _headers(), _is_excluded() (+49 more)

### Community 10 - "Basket Optimizer Core"
Cohesion: 0.06
Nodes (57): _Change, Collection, Prices, BasketItem, BasketReport, optimize(), Basket scenario evaluation. A pure function, no network access, no sqlite.  Inpu, One site's share of a split basket: what to buy there and what it costs.      `s (+49 more)

### Community 11 - "Basket Store & Pricing"
Cohesion: 0.09
Nodes (40): conn(), Connection, Path, Tests for parfum_finder.store: the timestamp helper and the schema.  The one har, An update aimed at a row that isn't there means the caller is out of sync., A snapshot pointing at a variant that doesn't exist has to be rejected.      SQL, Two snapshots written in the same second must resolve to the newer one.      A s, 5 ml at 125,00 TL is 25,00 TL per ml. Stored as kurus, ml as tenths. (+32 more)

### Community 12 - "JSON-LD Product Extraction"
Cohesion: 0.08
Nodes (48): extract_jsonld_products(), extract_jsonld_variants(), Read every JSON-LD Product declared on the page, in document order.      A block, Rung 1: read the page's JSON-LD as flat variant rows.      A product that declar, _fixture(), _one_product_html(), Tests for parfum_finder.extract.  Every case here is a shape a real store actual, Wrap a JSON-LD product body in a page, for the one-field-at-a-time cases. (+40 more)

### Community 13 - "Basket TUI Screen"
Cohesion: 0.16
Nodes (18): _canonical(), _covers(), _ends_with(), _index_of(), _match_text(), Perfume matching: brand and concentration are mandatory; fuzzy matching only app, Judge one piece of title text, with no clone handling of its own., Fold, cut a size out, split into words and numbers, and drop noise.      A size (+10 more)

### Community 14 - "Platform Schema"
Cohesion: 0.06
Nodes (31): any, defaults, fingerprint, additionalProperties, items, minItems, type, description (+23 more)

### Community 15 - "Product Extraction"
Cohesion: 0.07
Nodes (53): _as_str(), _balanced_value(), _build_offer(), _build_product(), _coerce_in_stock(), _collect_offers(), _collect_products(), _collect_variants() (+45 more)

### Community 16 - "Schema Field Patterns"
Cohesion: 0.07
Nodes (30): format, pattern, type, pattern, type, default, type, pattern (+22 more)

### Community 17 - "Offline Profile Validation"
Cohesion: 0.07
Nodes (43): FetchResult, One fetched page, uniform regardless of which strategy produced it., The Textual App root. Handles screen navigation and is the app's default entry p, _age_of(), Check, _count_result_cards(), _first_result_url(), _FixtureFetcher (+35 more)

### Community 18 - "Playwright Errors"
Cohesion: 0.13
Nodes (24): PlaywrightNoResponse, RuntimeError, Navigation completed but playwright returned no Response object.      Its own ty, _attempt(), _count_jsonld(), _count_product_objects(), _detect_platforms(), format_report() (+16 more)

### Community 19 - "Search TUI Screen"
Cohesion: 0.18
Nodes (3): RowSelected, The initial screen: search bar, streaming results table, notices, footer., SearchScreen

### Community 20 - "Snapshot Writing"
Cohesion: 0.11
Nodes (28): One priced size of one perfume on one site, ready to be written.      The perfum, Write a whole scan at once and return how many prices were recorded.      Every, SnapshotRow, write_snapshots(), The drop happens here so no caller can forget it.      Both the CLI and the scre, The old price has to survive, and it must not become a second variant.      Appe, The title and URL are information, not identity.      A shop that rewords a list, EDT and EDP are different products at different prices.      Folding them into o (+20 more)

### Community 21 - "Candidate Filtering"
Cohesion: 0.21
Nodes (7): _listing_filter(), Any, CacheKey, CandidateFilter, VariantsRead, Decide, from a search result's own title, whether to open its page., Scan one site for every perfume of this search, one at a time.          Serial i

### Community 22 - "Basket Site Scenarios"
Cohesion: 0.14
Nodes (22): basket_lines(), basket_prices(), basket_sites(), BasketLine, BasketPrice, BasketSite, One row of the basket: a size of a perfume, with the identity spelled out., One site's latest price for one basket line, only when it has one.      Rows wit (+14 more)

### Community 23 - "Price/Size Normalization"
Cohesion: 0.12
Nodes (25): _classify_single_separator(), format_ml(), format_price(), _parse_number(), parse_price(), parse_size_ml(), Decimal, Number parsing and formatting for prices and volumes, plus text folding.  This i (+17 more)

### Community 24 - "JSON Schema Primitives"
Cohesion: 0.12
Nodes (23): null, string, properties, type, type, type, additionalProperties, properties (+15 more)

### Community 25 - "SQLite Store"
Cohesion: 0.17
Nodes (21): add_basket_item(), now_iso(), _perfume_id(), _product_id(), Connection, SQLite persistence: an append-only price history.  Tables: sites, perfumes, prod, Return the current UTC time as 'YYYY-MM-DDTHH:MM:SSZ'.      Every timestamp writ, Write one scan's reading of one size, and return its snapshot id.      The perfu (+13 more)

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
Cohesion: 0.20
Nodes (18): collect_prices(), _format_product(), _format_stock(), _format_trial(), _has_exact_price(), PageTrial, Decimal, Site discovery: turns a URL into a profile, with human review. Not fully automat (+10 more)

### Community 30 - "Store Timestamp Tests"
Cohesion: 0.18
Nodes (17): _close_browser(), _fetch_curl_cffi(), _fetch_httpx(), _fetch_playwright(), _launch_browser(), PlaywrightNotInstalled, Any, FormData (+9 more)

### Community 31 - "Live Profile Validation"
Cohesion: 0.09
Nodes (48): format_report(), profile_age_days(), datetime, Whole days between a profile's `discovered_at` and now.      Only the exact UTC, Check one site's profile against that site's saved fixtures.      Never raises f, Validate every site, or just the ones named.      Serial rather than concurrent:, Render the validations as the offline half of the report in APP_FLOW §6.      A, validate_all_offline() (+40 more)

### Community 32 - "Variant Extraction Fields"
Cohesion: 0.11
Nodes (18): attribute, in_stock, price, script, size_raw, type, properties, additionalProperties (+10 more)

### Community 33 - "Variant Extraction Ladder"
Cohesion: 0.16
Nodes (5): Changed, One perfume of a search, as typed and as parsed.      The index is the outermost, Empty the table for a new scan.          The columns are the same every time now, _Search, Submitted

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
Cohesion: 0.16
Nodes (14): DiscoveryReport, _format_choice(), _format_confidence(), _format_fingerprint(), _format_fixtures(), format_report(), The template this site's profile would be based on, if any., The scored fields a person still has to confirm, in profile order.          Anyt (+6 more)

### Community 38 - "TUI Confirm Dialog"
Cohesion: 0.24
Nodes (15): _fake_fetch(), _meta(), _path(), Proof that M4's own criterion holds: every real site profile drives the generic, The one real search-result card that led to this site's captured product.      C, Route every fetch call a site's search_site() run makes to real bytes.      Only, _single_result_search_html(), test_decantall_reads_its_four_real_decant_prices() (+7 more)

### Community 39 - "TUI App Shell"
Cohesion: 0.13
Nodes (10): Screen, ParfumFinderApp, Path, Root app: pushes the search screen on mount., Path, Path, Protocol, What this screen needs of engine.run_site.      A protocol rather than a plain c (+2 more)

### Community 40 - "Fetch Backends"
Cohesion: 0.14
Nodes (14): curl_cffi, httpx, playwright, result_item, result_title, result_url, strategy, url_template (+6 more)

### Community 41 - "HTTP Request Schema"
Cohesion: 0.14
Nodes (14): GET, POST, properties, default, enum, type, type, type (+6 more)

### Community 42 - "Fixture Fetcher (Tests)"
Cohesion: 0.15
Nodes (13): One call has to leave a row the search table can read straight off.      The cal, first_seen is what says how long a shop has carried a size., Sites come from the profiles, so an id nothing synced is a mistake., A stale reading must never outrank the one taken after it.      latest_prices al, A 10 ml listing must never fill a basket line asking for 5 ml.      The matrix j, Whether an out-of-stock price counts as missing is the caller's call.      Dropp, _record(), test_a_second_scan_moves_last_seen_and_keeps_first_seen() (+5 more)

### Community 43 - "Validation Reporting"
Cohesion: 0.24
Nodes (11): _flatten_defaults(), _format_defaults(), _match_platforms(), Any, Path, Every template with at least one of its markers somewhere in the page.      Case, Write one page and return where it landed plus its digest.      Saved as UTF-8 w, Render a template's defaults as one dotted key per line. (+3 more)

### Community 44 - "Decant Variant Rules"
Cohesion: 0.25
Nodes (8): Split one typed line into the perfumes it asks for, on " - ".      The separator, split_queries(), test_a_hyphen_inside_a_brand_name_does_not_split_the_search(), test_a_line_naming_three_perfumes_is_read_as_three_searches(), test_a_piece_that_names_no_perfume_survives_to_be_complained_about(), test_a_stray_separator_is_not_worth_failing_over(), test_one_perfume_is_still_one_search(), test_the_same_perfume_typed_twice_is_scanned_once()

### Community 45 - "Multi-Site Search Run"
Cohesion: 0.25
Nodes (8): Turn one site's hits into the rows write_snapshots is ready to store.      Share, snapshot_rows(), A shop's imitation must not be stored as the perfume it imitates.      The clone, Another house's bottle on the same results page must not enter this history., EDT and EDP are different products, so the row has to say which one this was., test_snapshot_rows_drops_a_title_the_matcher_rejects(), test_snapshot_rows_marks_a_clone_instead_of_filing_it_as_the_original(), test_snapshot_rows_stores_the_titles_own_concentration()

### Community 46 - "Offline Validation Fixtures"
Cohesion: 0.22
Nodes (9): product_label(), Reduce a site's own title to the product it is about, spelled one way.      What, Split a title into what the bottle is and what it says it imitates.      The sec, _split_clone_reference(), test_a_clone_is_labelled_by_the_bottle_it_is_and_not_what_it_imitates(), test_a_longer_named_bottle_does_not_join_the_shorter_ones_block(), test_a_title_with_no_product_words_left_has_no_label(), test_every_shops_spelling_of_one_bottle_lands_in_one_block() (+1 more)

### Community 47 - "Basket Domain Logic"
Cohesion: 0.06
Nodes (96): apply_variant_rules(), CacheKey, CandidateFilter, Path, VariantsRead, Run one site and classify what came back instead of raising.      It is also whe, Run every site against one query, all at once, and report each separately., Run one query against one site and read every hit's sizes.      Everything site- (+88 more)

### Community 48 - "Search Screen Rows"
Cohesion: 0.23
Nodes (6): Decimal, Row, One priced size, exactly as the table shows it and as a keypress needs it., The default order: typed order, product, site, size.          The typed order co, The order once a column has been picked: the site layer drops out.          Aski, _ResultRow

### Community 49 - "test_engine.py"
Cohesion: 0.25
Nodes (8): exclude_keywords, max_size_ml, size_from, size_pattern, variant_rules, additionalProperties, required, type

### Community 50 - "Profile Age Checks"
Cohesion: 0.20
Nodes (8): _age_line(), format_live_report(), Every check run against one site's profile, in the order they ran.      Checks s, Whether the profile is old enough to be worth re-discovering., The check that broke, or None if the profile is intact., The age note for one site, or None when its age is unremarkable.      A profile, Render offline and live results side by side, as APP_FLOW §6 shows them.      Bo, SiteValidation

### Community 51 - "extract_endpoint_variants"
Cohesion: 0.32
Nodes (7): FieldConfidence, One field this run can fill in, with how far it can be trusted.      `field` is, Every profile field this run can put a value on, scored., Score every profile field this run can fill in, in profile order.      Only fiel, Read the extraction layer off the page, for a site no template covers.      Judg, _score_extraction(), score_fields()

### Community 53 - "conftest.py"
Cohesion: 0.29
Nodes (6): _choose_strategy(), Strategy, _qualifies(), The strategy the trials actually ran with., Pick the cheapest strategy that came back with real content, or None.      probe, Whether one strategy came back with a usable page.

### Community 54 - "Endpoint Schema Fields"
Cohesion: 0.22
Nodes (9): result_item, result_title, result_url, url_template, search, additionalProperties, description, required (+1 more)

### Community 56 - "Request Schema Fields"
Cohesion: 0.25
Nodes (8): type, additionalProperties, type, body, request_headers, additionalProperties, description, type

### Community 58 - "Snapshot Row Building"
Cohesion: 0.20
Nodes (11): _listing_filter(), Any, CandidateFilter, Connection, Scan every perfume against every site and print each site as it lands.      One, Decide, from a search result's own title, whether to open its page., Write one site's rows in a transaction of its own.      Per site rather than per, One line per site: which site, how it went, and what it said.      The site id i (+3 more)

### Community 60 - "Fetch Strategy Selection"
Cohesion: 0.31
Nodes (9): Node, _parse_selector(), Run one "<css>::text" / "<css>::attr(name)" selector inside a node.      The nod, Run one "<css>::text" / "<css>::attr(name)" selector, reading every match., Split a "<css>::text" / "<css>::attr(name)" selector into its two parts., Read the attribute or text of one already-selected node, or None., _read_selected(), select_all() (+1 more)

### Community 61 - "Price History"
Cohesion: 0.29
Nodes (7): price_history(), Row, Return one variant's past readings, newest first, capped at limit.      Empty fo, The trend panel reads row 0 as the latest reading, so order is the point.      A, No history yet is a normal state for a variant, not an error to raise on., test_price_history_is_empty_for_an_unknown_variant(), test_price_history_is_newest_first_and_capped_at_limit()

### Community 62 - "Extraction Layer Enum"
Cohesion: 0.33
Nodes (6): css, embedded_json, endpoint, jsonld, enum, extraction

## Knowledge Gaps
- **152 isolated node(s):** `parfum-finder`, `$schema`, `$id`, `title`, `description` (+147 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `SiteResult` connect `Search/Basket Domain Models` to `TUI App & Screens`, `Site Profiles & Templates`, `Variant Extraction Ladder`, `TUI App Shell`, `Search Engine Core`, `Basket Optimizer Core`, `Multi-Site Search Run`, `Product Extraction`, `Basket Domain Logic`, `Offline Profile Validation`, `Search Screen Rows`, `Search TUI Screen`, `Snapshot Writing`, `Candidate Filtering`, `Basket Site Scenarios`, `SQLite Store`, `Snapshot Row Building`, `Store Timestamp Tests`?**
  _High betweenness centrality (0.061) - this node is a cross-community bridge._
- **Why does `SearchScreen` connect `Search TUI Screen` to `TUI App & Screens`, `Site Profiles & Templates`, `Title Matcher`, `Variant Extraction Ladder`, `Search/Basket Domain Models`, `TUI App Shell`, `Search Engine Core`, `Basket Optimizer Core`, `Search Screen Rows`, `Offline Profile Validation`, `Snapshot Writing`, `Snapshot Row Semantics`, `Candidate Filtering`?**
  _High betweenness centrality (0.056) - this node is a cross-community bridge._
- **Why does `PlaywrightNotInstalled` connect `Store Timestamp Tests` to `Fetch Strategy Probing`, `HTTP/Browser Fetching`, `Search/Basket Domain Models`, `Discovery Report Model`, `Search Engine Core`, `Basket Domain Logic`, `Playwright Errors`, `extract_endpoint_variants`, `Discovery CLI Reporting`?**
  _High betweenness centrality (0.033) - this node is a cross-community bridge._
- **Are the 7 inferred relationships involving `SearchScreen` (e.g. with `ParfumFinderApp` and `SiteResult`) actually correct?**
  _`SearchScreen` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Are the 16 inferred relationships involving `SiteResult` (e.g. with `RawVariant` and `Fetcher`) actually correct?**
  _`SiteResult` has 16 INFERRED edges - model-reasoned connections that need verification._
- **What connects `parfum-finder`, `$schema`, `$id` to the rest of the system?**
  _152 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `TUI App & Screens` be split into smaller, more focused modules?**
  _Cohesion score 0.10536828963795256 - nodes in this community are weakly interconnected._