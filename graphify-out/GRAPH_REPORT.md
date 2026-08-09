# Graph Report - .  (2026-08-09)

## Corpus Check
- 76 files · ~224,430 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1665 nodes · 4479 edges · 71 communities (68 shown, 3 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 165 edges (avg confidence: 0.55)
- Token cost: 71,152 input · 0 output

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

## God Nodes (most connected - your core abstractions)
1. `search_site()` - 64 edges
2. `discover()` - 56 edges
3. `_profile()` - 54 edges
4. `SiteResult` - 51 edges
5. `BasketScreen` - 51 edges
6. `SearchScreen` - 51 edges
7. `PerfumeQuery` - 50 edges
8. `Fetcher` - 42 edges
9. `_attempt()` - 42 edges
10. `_fake_probe()` - 42 edges

## Surprising Connections (you probably didn't know these)
- `Shipping Non-linearity Rationale (why cheapest-per-item is wrong)` --semantically_similar_to--> `sites/ Site Profile Directory`  [INFERRED] [semantically similar]
  ARCHITECTURE.md → sites/README.md
- `Variant Pattern B (dropdown + AJAX price)` --semantically_similar_to--> `Variant Selector Detector Fix (WooCommerce 'variation' vs 'variant')`  [INFERRED] [semantically similar]
  ARCHITECTURE.md → docs/discovery-report.md
- `_NoRootParser` --uses--> `ExtractionFailed`  [INFERRED]
  tests/test_engine.py → src/parfum_finder/engine.py
- `_NoRootParser` --uses--> `RawVariant`  [INFERRED]
  tests/test_engine.py → src/parfum_finder/extract.py
- `test_css_reads_one_row_per_container()` --calls--> `extract_css_variants()`  [EXTRACTED]
  tests/test_extract.py → src/parfum_finder/extract.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Sites Implementing Variant Pattern C (embedded JSON)** — docs_discovery_report_venco_site, docs_discovery_report_decantall_site, docs_discovery_report_luxurydekant_site, docs_discovery_report_ruxangroup_site, architecture_md_variant_pattern_c [EXTRACTED 1.00]
- **İdeasoft Platform Sites and Endpoint** — docs_discovery_report_dekantparfum_site, docs_discovery_report_dekantdoktoru_site, docs_discovery_report_ideasoft_related_options_endpoint, platforms_readme_ideasoft_json [EXTRACTED 1.00]
- **discover Command Output Artifacts (profile + fixtures + CI validation)** — architecture_md_discover_flow, sites_readme_sites_dir, fixtures_readme_fixtures_dir, github_workflows_ci_validate_profiles_step, architecture_md_validate_command [INFERRED 0.85]

## Communities (71 total, 3 thin omitted)

### Community 0 - "TUI App & Screens"
Cohesion: 0.11
Nodes (88): The Textual-based terminal UI: search and basket screens., _app(), _basket(), _cells(), _days_ago(), _leg(), _ok(), _open_basket() (+80 more)

### Community 1 - "Site Profiles & Templates"
Cohesion: 0.06
Nodes (83): _check_hook_kinds(), deep_merge(), _load_json(), load_platform_template(), load_platform_templates(), load_site_hooks(), load_site_profile(), Any (+75 more)

### Community 2 - "Title Matcher"
Cohesion: 0.06
Nodes (78): _canonical(), _covers(), _ends_with(), _index_of(), Match, _match_text(), match_title(), parse_query() (+70 more)

### Community 3 - "HTTP/Browser Fetching"
Cohesion: 0.05
Nodes (61): BaseHTTPRequestHandler, requires_playwright_package, browser_session(), _close_browser(), fetch(), _fetch_curl_cffi(), _fetch_httpx(), _fetch_playwright() (+53 more)

### Community 4 - "Search/Basket Domain Models"
Cohesion: 0.11
Nodes (73): One decant size of one product, in the units the database stores. Tenths of a…, A candidate together with the decant sizes its product page offers., What one site had to say about one query, and how much to trust it. Four…, SearchHit, SiteResult, Variant, connect(), Path (+65 more)

### Community 5 - "Search Engine per Site"
Cohesion: 0.09
Nodes (61): Run one site and classify what came back instead of raising. It is also where…, Run one query against one site and read every hit's sizes. Everything site-…, run_site(), search_site(), _counting_fetcher(), _profile(), Exception, Path (+53 more)

### Community 6 - "Platform Discovery Flow"
Cohesion: 0.14
Nodes (60): PlatformChooser, _ask_chooser(), discover(), Put the question only when there is one, and hold the answer to it. An answer…, Measure the strategies a site needs, then read its JSON-LD with the winner.…, _attempt(), _fake_probe(), Any (+52 more)

### Community 7 - "CLI Entry Points"
Cohesion: 0.09
Nodes (55): CaptureFixture, ask_which_platform(), _listing_filter(), main(), Any, CandidateFilter, Connection, Path (+47 more)

### Community 8 - "Architecture Rationale Docs"
Cohesion: 0.05
Nodes (53): basket Subset Enumeration + Local Improvement Algorithm, basket Optimizer (optimize function), Clone/Original Distinction (KLON ← <orijinal>), discover Discovery Flow, engine Concurrency Model (parallel sites, serial within site), Extraction Ladder (jsonld/endpoint/embedded/css), Fail-loud / status=suspect policy, hooks/<id>.py Escape Hatch (+45 more)

### Community 9 - "Search Engine Core"
Cohesion: 0.08
Nodes (51): HTMLParser, _check_empty_search(), _check_variant_control(), ExtractionFailed, _fetch_page(), _headers(), _is_excluded(), _paced_fetcher() (+43 more)

### Community 10 - "Basket Optimizer Core"
Cohesion: 0.15
Nodes (33): Collection, Prices, BasketItem, optimize(), Score one site against the basket, or against a subset of it. `item_ids` is how…, Score every enabled site against the whole basket and sort the results. Sites…, Search for the cheapest way to split the basket across several sites. Returns…, One line of the shopping list: a basket row, not a unit count. `item_id` is… (+25 more)

### Community 11 - "Basket Store & Pricing"
Cohesion: 0.10
Nodes (34): add_basket_item(), Add a size of a perfume to the basket, and return the basket_item_id. The…, Connection, Two snapshots written in the same second must resolve to the newer one. A scan…, 5 ml at 125,00 TL is 25,00 TL per ml. Stored as kurus, ml as tenths., No price yet means no row, so the basket LEFT JOIN reads it as missing., A zero ml variant is a parse failure, and it must not reach the table. If it…, Adding the same perfume and size twice must accumulate, not clobber. The basket… (+26 more)

### Community 12 - "JSON-LD Product Extraction"
Cohesion: 0.13
Nodes (32): extract_jsonld_products(), Read every JSON-LD Product declared on the page, in document order. A block…, _one_product_html(), Tests for parfum_finder.extract. Every case here is a shape a real store…, Wrap a JSON-LD product body in a page, for the one-field-at-a-time cases., test_a_broken_block_does_not_lose_the_valid_one(), test_availability_spellings_all_land_in_the_same_bucket(), test_boolean_values_are_never_read_as_price_or_text() (+24 more)

### Community 13 - "Basket TUI Screen"
Cohesion: 0.13
Nodes (10): _Change, BasketReport, Every site's single-site scenario, split by whether it covers everything. A…, BasketScreen, Any, work, The basket: the list on top, one scenario per site underneath., The three inputs basket.py's pure functions score: items, prices, shipping.… (+2 more)

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
Nodes (26): Fetcher, Protocol, Anything that can stand in for `fetch`. Offline profile validation runs the…, _age_of(), Check, _first_result_url(), _LayerUnavailable, _probe_layer() (+18 more)

### Community 18 - "Playwright Errors"
Cohesion: 0.13
Nodes (26): PlaywrightNoResponse, PlaywrightNotInstalled, RuntimeError, The "playwright" strategy was requested but cannot run at all. Covers both…, Navigation completed but playwright returned no Response object. Its own type…, _attempt(), _count_jsonld(), _count_product_objects() (+18 more)

### Community 19 - "Search TUI Screen"
Cohesion: 0.13
Nodes (6): HeaderSelected, RowSelected, work, The initial screen: search bar, streaming results table, notices, footer., Empty the table and give it the columns this search needs. The perfume column…, SearchScreen

### Community 20 - "Snapshot Writing"
Cohesion: 0.13
Nodes (24): One priced size of one perfume on one site, ready to be written. The perfume is…, Write a whole scan at once and return how many prices were recorded. Every row…, SnapshotRow, write_snapshots(), The drop happens here so no caller can forget it. Both the CLI and the screen…, EDT and EDP are different products at different prices. Folding them into one…, A sold-out size often shows no price at all, and 0 would mean free. Writing a…, The column is 0/1, so the tri-state has to land somewhere on purpose. Unknown… (+16 more)

### Community 21 - "Candidate Filtering"
Cohesion: 0.12
Nodes (11): Changed, _listing_filter(), Any, CacheKey, CandidateFilter, VariantsRead, Decide, from a search result's own title, whether to open its page., One perfume of a search, as typed and as parsed. The index is what groups the… (+3 more)

### Community 22 - "Basket Site Scenarios"
Cohesion: 0.14
Nodes (20): What it would cost to buy some or all of the basket from one site. `covered`…, SiteScenario, basket_sites(), BasketLine, BasketPrice, BasketSite, One row of the basket: a size of a perfume, with the identity spelled out. The…, One site's latest price for one basket line, only when it has one. Rows with no… (+12 more)

### Community 23 - "Price/Size Normalization"
Cohesion: 0.14
Nodes (22): _classify_single_separator(), format_ml(), format_price(), _parse_number(), parse_price(), parse_size_ml(), Decimal, Number parsing and formatting for prices and volumes, plus text folding. This… (+14 more)

### Community 24 - "JSON Schema Primitives"
Cohesion: 0.12
Nodes (23): null, string, properties, type, type, type, additionalProperties, properties (+15 more)

### Community 25 - "SQLite Store"
Cohesion: 0.16
Nodes (21): basket_lines(), basket_prices(), _perfume_id(), _product_id(), Connection, SQLite persistence: an append-only price history. Tables: sites, perfumes,…, Write one scan's reading of one size, and return its snapshot id. The perfume,…, Do the writing, without opening a transaction of its own. (+13 more)

### Community 26 - "Site Profile Fields"
Cohesion: 0.10
Nodes (20): base_url, discovered_at, extraction, id, needs_review, platform, search, shipping (+12 more)

### Community 27 - "Site Schema Validation Tests"
Cohesion: 0.18
Nodes (18): Draft202012Validator, _load_schema(), _platform_validator(), Any, parametrize, Tests for schema/site.schema.json and schema/platform.schema.json. These check…, The third copy of the ladder is here, and nothing else would catch it drifting.…, _site_validator() (+10 more)

### Community 28 - "Variant Rule Fields"
Cohesion: 0.11
Nodes (19): exclude_keywords, field, max_size_ml, size_from, size_pattern, title, variant_label, exclusiveMinimum (+11 more)

### Community 29 - "Discovery CLI Reporting"
Cohesion: 0.20
Nodes (18): collect_prices(), _format_product(), _format_stock(), _format_trial(), _has_exact_price(), PageTrial, Decimal, Site discovery: turns a URL into a profile, with human review. Not fully… (+10 more)

### Community 30 - "Store Timestamp Tests"
Cohesion: 0.12
Nodes (18): now_iso(), Return the current UTC time as 'YYYY-MM-DDTHH:MM:SSZ'. Every timestamp written…, conn(), Path, Tests for parfum_finder.store: the timestamp helper and the schema. The one…, An update aimed at a row that isn't there means the caller is out of sync.…, A snapshot pointing at a variant that doesn't exist has to be rejected. SQLite…, Reopening an existing database must not wipe or re-raise on its schema. (+10 more)

### Community 31 - "Live Profile Validation"
Cohesion: 0.19
Nodes (17): format_live_report(), Run one site's profile against the real site. Same contract as offline mode: a…, Render offline and live results side by side, as APP_FLOW §6 shows them. Both…, validate_live(), _DeadSite, _FakeSite, _fixture_site(), M5's own criterion: when a profile stops agreeing with its site's real markup,… (+9 more)

### Community 32 - "Variant Extraction Fields"
Cohesion: 0.11
Nodes (18): attribute, in_stock, price, script, size_raw, type, properties, additionalProperties (+10 more)

### Community 33 - "Variant Extraction Ladder"
Cohesion: 0.15
Nodes (18): extract_embedded_variants(), extract_jsonld_variants(), _flatten_jsonld(), Rung 1: read the page's JSON-LD as flat variant rows. A product that declares…, Turn one Product and everything under it into rows., Rung 3: read the JSON blob the page carries but does not display. Two shapes of…, _fixture(), Read a captured product page. (+10 more)

### Community 34 - "Fetch Strategy Probing"
Cohesion: 0.24
Nodes (17): probe(), Fetch `url` with every strategy and report diagnostics for each. timeout_s…, MonkeyPatch, parametrize, requires_playwright, Tests for parfum_finder.probe. probe() always tries all three strategies --…, test_probe_counts_jsonld_product_and_platform_signature(), test_probe_counts_product_across_jsonld_root_shapes() (+9 more)

### Community 35 - "Platform Field Mapping"
Cohesion: 0.12
Nodes (16): field_map, product_json, source, variants_path, additionalProperties, allOf, description, required (+8 more)

### Community 36 - "Shipping Config Schema"
Cohesion: 0.12
Nodes (16): free_shipping_threshold_kurus, integer, shipping_cost_kurus, minimum, type, type, free_shipping_threshold_kurus, notes (+8 more)

### Community 37 - "Discovery Report Model"
Cohesion: 0.16
Nodes (14): DiscoveryReport, _format_choice(), _format_confidence(), _format_fingerprint(), _format_fixtures(), format_report(), The template this site's profile would be based on, if any., The scored fields a person still has to confirm, in profile order. Anything… (+6 more)

### Community 38 - "TUI Confirm Dialog"
Cohesion: 0.14
Nodes (7): Pressed, ComposeResult, ConfirmScreen, ComposeResult, Path, Asks before a low-confidence match is written to the basket. The two answers…, Static

### Community 39 - "TUI App Shell"
Cohesion: 0.15
Nodes (10): Screen, ParfumFinderApp, Path, The Textual App root. Handles screen navigation and is the app's default entry…, Root app: pushes the search screen on mount., Path, Protocol, What this screen needs of engine.run_site. A protocol rather than a plain… (+2 more)

### Community 40 - "Fetch Backends"
Cohesion: 0.14
Nodes (14): curl_cffi, httpx, playwright, result_item, result_title, result_url, strategy, url_template (+6 more)

### Community 41 - "HTTP Request Schema"
Cohesion: 0.14
Nodes (14): GET, POST, properties, default, enum, type, type, type (+6 more)

### Community 42 - "Fixture Fetcher (Tests)"
Cohesion: 0.22
Nodes (9): _FixtureFetcher, _path(), FormData, Headers, Method, Strategy, Serves one site's saved capture in place of the network. Only three kinds of…, The one real result card that led to the captured product page. Cut out of the… (+1 more)

### Community 43 - "Validation Reporting"
Cohesion: 0.22
Nodes (14): format_report(), Every site that has a profile, sorted so reports read the same way twice., Validate every site, or just the ones named. Serial rather than concurrent:…, Render the validations as the offline half of the report in APP_FLOW §6. A…, site_ids(), validate_all_offline(), _iso_days_ago(), A discovered_at stamp that lands a fixed number of days in the past. Relative… (+6 more)

### Community 44 - "Decant Variant Rules"
Cohesion: 0.27
Nodes (13): apply_variant_rules(), Turn raw size rows into decant variants, dropping what is not a decant. Three…, _row(), test_a_keyword_in_the_size_label_excludes_the_row_too(), test_a_literal_zero_price_reads_as_no_price_not_a_free_perfume(), test_a_size_at_the_threshold_is_a_bottle_whatever_it_calls_itself(), test_a_size_that_cannot_be_read_is_dropped(), test_an_uppercase_turkish_keyword_still_matches() (+5 more)

### Community 45 - "Multi-Site Search Run"
Cohesion: 0.15
Nodes (13): _candidates_to_open(), CacheKey, CandidateFilter, Path, VariantsRead, Run every site against one query, all at once, and report each separately.…, Narrow the search results down to the pages worth a request. The first one…, run_sites() (+5 more)

### Community 46 - "Offline Validation Fixtures"
Cohesion: 0.29
Nodes (13): Check one site's profile against that site's saved fixtures. Never raises for a…, validate_offline(), _corrupted_sites_dir(), Any, Path, A sites/ directory holding one real profile with fields overwritten. The real…, test_a_dead_price_selector_is_caught_as_the_extraction_step(), test_a_dead_search_selector_is_caught_as_the_search_step() (+5 more)

### Community 47 - "Basket Domain Logic"
Cohesion: 0.18
Nodes (11): Basket scenario evaluation. A pure function, no network access, no sqlite.…, One site's share of a split basket: what to buy there and what it costs.…, The cheapest basket split the search found. A heuristic, not a proof. Every…, One site's shipping terms, read once and reused for every scenario.…, ShippingConfig, SplitLeg, SplitPlan, _leg_block() (+3 more)

### Community 48 - "Search Screen Rows"
Cohesion: 0.24
Nodes (5): Decimal, Row, The search screen: a results table that fills in as each site finishes.…, One priced size, exactly as the table shows it and as a keypress needs it., _ResultRow

### Community 49 - "Template Matching"
Cohesion: 0.24
Nodes (11): _flatten_defaults(), _format_defaults(), _match_platforms(), Any, Path, Every template with at least one of its markers somewhere in the page. Case-…, Write one page and return where it landed plus its digest. Saved as UTF-8 with…, Render a template's defaults as one dotted key per line. (+3 more)

### Community 50 - "Profile Age Checks"
Cohesion: 0.18
Nodes (8): _age_line(), Every check run against one site's profile, in the order they ran. Checks stop…, Whether the profile is old enough to be worth re-discovering., The check that broke, or None if the profile is intact., Validate every site against the live web, or just the ones named. Serial like…, The age note for one site, or None when its age is unremarkable. A profile…, SiteValidation, validate_all_live()

### Community 51 - "Live Query Tests"
Cohesion: 0.18
Nodes (10): _count_result_cards(), live_query(), _no_results_check(), Any, Path, The query this site's fixture was captured with, read back out of its URL. Live…, Why an empty results page is suspicious, or why it is not. A full page that…, How many result rows the profile's own selectors find on a search page. (+2 more)

### Community 52 - "Snapshot Row Semantics"
Cohesion: 0.18
Nodes (11): One call has to leave a row the search table can read straight off. The caller…, The old price has to survive, and it must not become a second variant. Append-…, first_seen is what says how long a shop has carried a size., The title and URL are information, not identity. A shop that rewords a listing…, Sites come from the profiles, so an id nothing synced is a mistake., _record(), test_a_renamed_listing_keeps_its_price_history(), test_a_second_scan_appends_instead_of_overwriting() (+3 more)

### Community 53 - "CSS Selector Parsing"
Cohesion: 0.31
Nodes (9): Node, _parse_selector(), Run one "<css>::text" / "<css>::attr(name)" selector inside a node. The node…, Run one "<css>::text" / "<css>::attr(name)" selector, reading every match. Same…, Split a "<css>::text" / "<css>::attr(name)" selector into its two parts., Read the attribute or text of one already-selected node, or None., _read_selected(), select_all() (+1 more)

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
Cohesion: 0.32
Nodes (7): FieldConfidence, One field this run can fill in, with how far it can be trusted. `field` is the…, Every profile field this run can put a value on, scored., Score every profile field this run can fill in, in profile order. Only fields…, Read the extraction layer off the page, for a site no template covers. Judged…, _score_extraction(), score_fields()

### Community 58 - "Snapshot Row Building"
Cohesion: 0.25
Nodes (8): Turn one site's hits into the rows write_snapshots is ready to store. Shared by…, snapshot_rows(), A shop's imitation must not be stored as the perfume it imitates. The clone is…, Another house's bottle on the same results page must not enter this history.…, EDT and EDP are different products, so the row has to say which one this was. A…, test_snapshot_rows_drops_a_title_the_matcher_rejects(), test_snapshot_rows_marks_a_clone_instead_of_filing_it_as_the_original(), test_snapshot_rows_stores_the_titles_own_concentration()

### Community 59 - "Variant Field Types"
Cohesion: 0.29
Nodes (7): items, type, type, items, type, exclude_keywords, needs_review

### Community 60 - "Fetch Strategy Selection"
Cohesion: 0.29
Nodes (6): _choose_strategy(), Strategy, _qualifies(), The strategy the trials actually ran with., Pick the cheapest strategy that came back with real content, or None. probe…, Whether one strategy came back with a usable page.

### Community 61 - "Price History"
Cohesion: 0.29
Nodes (7): price_history(), Row, Return one variant's past readings, newest first, capped at limit. Empty for a…, The trend panel reads row 0 as the latest reading, so order is the point. A…, No history yet is a normal state for a variant, not an error to raise on., test_price_history_is_empty_for_an_unknown_variant(), test_price_history_is_newest_first_and_capped_at_limit()

### Community 62 - "Extraction Layer Enum"
Cohesion: 0.33
Nodes (6): css, embedded_json, endpoint, jsonld, enum, extraction

### Community 63 - "Embedded JSON Parsing"
Cohesion: 0.33
Nodes (6): _balanced_value(), _embedded_documents(), _loads_or_skip(), Yield every JSON document the page hides, in document order., Parse `text` as JSON, yielding nothing when it isn't JSON. Pages are full of…, Return the JSON object or array beginning at or after `start`. Scanning for the…

### Community 64 - "Engine Delay Tests"
Cohesion: 0.40
Nodes (5): MonkeyPatch, Record every delay the engine asks for instead of serving it. Waiting for real…, slept(), test_a_product_page_with_no_root_names_its_body_size(), test_a_search_page_with_no_root_names_its_body_size()

### Community 65 - "JSON-LD Product Walking"
Cohesion: 0.50
Nodes (4): _collect_products(), _has_type(), Walk a parsed JSON-LD block and append every Product found, depth first.…, Whether a node's "@type" names `name`, as a string or inside a list. Substring…

### Community 66 - "Endpoint Variant Extraction"
Cohesion: 0.50
Nodes (4): extract_endpoint_variants(), Rung 2: read the variant list out of a platform's JSON response. `document` is…, test_endpoint_reads_every_size_from_one_response(), test_endpoint_without_a_field_map_reads_nothing()

### Community 67 - "Price Age Formatting"
Cohesion: 0.50
Nodes (4): format_age(), Turn a price age in days into the words the age column shows., The age column exists to be glanced at, so it is phrased, not printed., test_format_age_reads_as_words_not_a_timestamp()

## Knowledge Gaps
- **152 isolated node(s):** `parfum-finder`, `$schema`, `$id`, `title`, `description` (+147 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `SearchScreen` connect `Search TUI Screen` to `Title Matcher`, `Search/Basket Domain Models`, `TUI Confirm Dialog`, `TUI App Shell`, `Basket TUI Screen`, `Search Screen Rows`, `Offline Profile Validation`, `Snapshot Writing`, `Candidate Filtering`?**
  _High betweenness centrality (0.061) - this node is a cross-community bridge._
- **Why does `SiteResult` connect `Search/Basket Domain Models` to `TUI App & Screens`, `HTTP/Browser Fetching`, `Search Engine per Site`, `TUI Confirm Dialog`, `CLI Entry Points`, `TUI App Shell`, `Search Engine Core`, `Multi-Site Search Run`, `Basket TUI Screen`, `Search Screen Rows`, `Offline Profile Validation`, `Playwright Errors`, `Search TUI Screen`, `Snapshot Writing`, `Candidate Filtering`, `Basket Site Scenarios`, `SQLite Store`, `Snapshot Row Building`?**
  _High betweenness centrality (0.053) - this node is a cross-community bridge._
- **Why does `PlaywrightNotInstalled` connect `Playwright Errors` to `HTTP/Browser Fetching`, `Search/Basket Domain Models`, `Discovery Report Model`, `No-Root HTML Parser`, `Search Engine per Site`, `Search Engine Core`, `Field Confidence Scoring`, `Discovery CLI Reporting`?**
  _High betweenness centrality (0.048) - this node is a cross-community bridge._
- **Are the 16 inferred relationships involving `SiteResult` (e.g. with `RawVariant` and `Fetcher`) actually correct?**
  _`SiteResult` has 16 INFERRED edges - model-reasoned connections that need verification._
- **Are the 17 inferred relationships involving `BasketScreen` (e.g. with `BasketItem` and `BasketReport`) actually correct?**
  _`BasketScreen` has 17 INFERRED edges - model-reasoned connections that need verification._
- **What connects `parfum-finder`, `$schema`, `$id` to the rest of the system?**
  _152 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `TUI App & Screens` be split into smaller, more focused modules?**
  _Cohesion score 0.10536828963795256 - nodes in this community are weakly interconnected._