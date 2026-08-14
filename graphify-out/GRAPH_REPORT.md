# Graph Report - parfum-finder  (2026-08-14)

## Corpus Check
- 70 files · ~262,806 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1845 nodes · 5108 edges · 59 communities (56 shown, 3 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 222 edges (avg confidence: 0.57)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `ea704a93`
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
- Offline Validation Fixtures
- ._build_rows
- Profile Age Checks
- ._refresh_table
- conftest.py
- Endpoint Schema Fields
- Request Schema Fields
- _FixtureFetcher
- _named_profile
- CandidateFilter
- test_cached_prices_is_empty_for_a_perfume_nobody_scanned
- Variant Pattern A
- Project Root
- ComposeResult

## God Nodes (most connected - your core abstractions)
1. `SearchScreen` - 70 edges
2. `search_site()` - 66 edges
3. `PerfumeQuery` - 60 edges
4. `_profile()` - 58 edges
5. `discover()` - 56 edges
6. `SiteResult` - 56 edges
7. `BasketScreen` - 53 edges
8. `_write_profile()` - 50 edges
9. `_app()` - 49 edges
10. `_submit_query()` - 48 edges

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

## Communities (59 total, 3 thin omitted)

### Community 0 - "TUI App & Screens"
Cohesion: 0.09
Nodes (100): The Textual-based terminal UI: search and basket screens., _app(), _basket(), _cells(), _days_ago(), _leg(), _ok(), _open_basket() (+92 more)

### Community 1 - "Site Profiles & Templates"
Cohesion: 0.06
Nodes (81): _check_hook_kinds(), deep_merge(), _load_json(), load_platform_template(), load_platform_templates(), load_site_hooks(), load_site_profile(), Any (+73 more)

### Community 2 - "Title Matcher"
Cohesion: 0.05
Nodes (51): _Change, What it would cost to buy some or all of the basket from one site.      `covered, SiteScenario, Write one site's rows in a transaction of its own.      Per site rather than per, _store_site_result(), format_ml(), Format a volume for display (dot-decimal): Decimal('1.5') -> '1.5 ml'., basket_lines() (+43 more)

### Community 3 - "HTTP/Browser Fetching"
Cohesion: 0.12
Nodes (30): browser_session(), fetch(), PlaywrightNotInstalled, Fetch one URL using exactly the given strategy.      `method`/`data` exist for t, Yield a fetcher that keeps one browser for every playwright page it reads., The "playwright" strategy was requested but cannot run at all.      Covers both, test_the_no_results_page_would_otherwise_read_as_suspect(), _fake_launch() (+22 more)

### Community 4 - "Search/Basket Domain Models"
Cohesion: 0.07
Nodes (121): Screen, One decant size of one product, in the units the database stores.      Tenths of, A candidate together with the decant sizes its product page offers., SearchHit, Variant, connect(), Path, Open the price database, creating the schema if it isn't there yet.      Foreign (+113 more)

### Community 5 - "Search Engine per Site"
Cohesion: 0.15
Nodes (20): _close_browser(), _fetch_curl_cffi(), _fetch_httpx(), _fetch_playwright(), _launch_browser(), PlaywrightNoResponse, Any, FormData (+12 more)

### Community 6 - "Platform Discovery Flow"
Cohesion: 0.15
Nodes (59): PlatformChooser, _ask_chooser(), discover(), Put the question only when there is one, and hold the answer to it.      An answ, Measure the strategies a site needs, then read its JSON-LD with the winner., _attempt(), _fake_probe(), Any (+51 more)

### Community 7 - "CLI Entry Points"
Cohesion: 0.08
Nodes (63): CaptureFixture, ask_which_platform(), _listing_filter(), main(), Any, CandidateFilter, Connection, Path (+55 more)

### Community 8 - "Architecture Rationale Docs"
Cohesion: 0.05
Nodes (53): basket Subset Enumeration + Local Improvement Algorithm, basket Optimizer (optimize function), Clone/Original Distinction (KLON ← <orijinal>), discover Discovery Flow, engine Concurrency Model (parallel sites, serial within site), Extraction Ladder (jsonld/endpoint/embedded/css), Fail-loud / status=suspect policy, hooks/<id>.py Escape Hatch (+45 more)

### Community 9 - "Search Engine Core"
Cohesion: 0.07
Nodes (62): HTMLParser, _check_empty_search(), _check_variant_control(), ExtractionFailed, _fetch_page(), _headers(), _is_excluded(), _paced_fetcher() (+54 more)

### Community 10 - "Basket Optimizer Core"
Cohesion: 0.08
Nodes (56): Collection, Prices, BasketItem, BasketReport, _ClimbState, optimize(), Basket scenario evaluation. A pure function, no network access, no sqlite.  Inpu, One site's share of a split basket: what to buy there and what it costs.      `s (+48 more)

### Community 11 - "Basket Store & Pricing"
Cohesion: 0.09
Nodes (40): conn(), Connection, Path, Tests for parfum_finder.store: the timestamp helper and the schema.  The one har, A disabled site loses its basket column, but an enabled quiet one keeps one., NULL means the site has no free shipping tier at all, not a threshold of zero., Deleting a row that's already gone is a race between two screens, not a bug., The table's CHECK (qty > 0) would reject a bare 0, and the '-' key has to     su (+32 more)

### Community 12 - "JSON-LD Product Extraction"
Cohesion: 0.13
Nodes (32): extract_jsonld_products(), Read every JSON-LD Product declared on the page, in document order.      A block, _one_product_html(), Tests for parfum_finder.extract.  Every case here is a shape a real store actual, Wrap a JSON-LD product body in a page, for the one-field-at-a-time cases., test_a_broken_block_does_not_lose_the_valid_one(), test_availability_spellings_all_land_in_the_same_bucket(), test_boolean_values_are_never_read_as_price_or_text() (+24 more)

### Community 13 - "Basket TUI Screen"
Cohesion: 0.22
Nodes (9): price_history(), Row, Return one variant's past readings, newest first, capped at limit.      Empty fo, The trend panel reads row 0 as the latest reading, so order is the point.      A, No history yet is a normal state for a variant, not an error to raise on., The identity a real scan writes must be the identity these lookups accept., test_a_scanned_perfume_can_be_read_back_by_basket_and_history(), test_price_history_is_empty_for_an_unknown_variant() (+1 more)

### Community 14 - "Platform Schema"
Cohesion: 0.06
Nodes (31): any, defaults, fingerprint, additionalProperties, items, minItems, type, description (+23 more)

### Community 15 - "Product Extraction"
Cohesion: 0.11
Nodes (28): _as_str(), _build_offer(), _build_product(), _coerce_in_stock(), _collect_offers(), _collect_products(), _collect_variants(), _has_type() (+20 more)

### Community 16 - "Schema Field Patterns"
Cohesion: 0.06
Nodes (33): format, pattern, type, pattern, type, default, type, pattern (+25 more)

### Community 17 - "Offline Profile Validation"
Cohesion: 0.05
Nodes (102): apply_variant_rules(), _candidates_to_open(), CacheKey, CandidateFilter, Path, VariantsRead, Run one site and classify what came back instead of raising.      It is also whe, Run every site against one query, all at once, and report each separately. (+94 more)

### Community 18 - "Playwright Errors"
Cohesion: 0.15
Nodes (21): _attempt(), _count_jsonld(), _count_product_objects(), _detect_platforms(), format_report(), _label_platform(), _one_line(), ProbeAttempt (+13 more)

### Community 19 - "Search TUI Screen"
Cohesion: 0.08
Nodes (41): find_header_columns(), find_match(), open_worksheet(), Any, Exception, Path, Protocol, Writing a search result onto the user's own Google Sheets wishlist.  The wishlis (+33 more)

### Community 20 - "Snapshot Writing"
Cohesion: 0.38
Nodes (7): _match_platforms(), Any, Path, Every template with at least one of its markers somewhere in the page.      Case, Write one page and return where it landed plus its digest.      Saved as UTF-8 w, _save_fixture(), _trial()

### Community 21 - "Candidate Filtering"
Cohesion: 0.15
Nodes (18): extract_embedded_variants(), extract_jsonld_variants(), _flatten_jsonld(), Rung 1: read the page's JSON-LD as flat variant rows.      A product that declar, Turn one Product and everything under it into rows., Rung 3: read the JSON blob the page carries but does not display.      Two shape, _fixture(), Read a captured product page. (+10 more)

### Community 22 - "Basket Site Scenarios"
Cohesion: 0.21
Nodes (15): probe(), Fetch `url` with every strategy and report diagnostics for each.      timeout_s, MonkeyPatch, Tests for parfum_finder.probe.  probe() always tries all three strategies -- the, test_probe_counts_jsonld_product_and_platform_signature(), test_probe_counts_product_across_jsonld_root_shapes(), test_probe_counts_product_markup_without_any_jsonld(), test_probe_counts_products_nested_below_the_top_level() (+7 more)

### Community 23 - "Price/Size Normalization"
Cohesion: 0.18
Nodes (17): _classify_single_separator(), _parse_number(), parse_price(), parse_size_ml(), Decimal, Number parsing and formatting for prices and volumes, plus text folding.  This i, Decide whether a lone separator marks a fraction or a thousands group.      Retu, Parse a price string, e.g. '1.250,00 TL' -> Decimal('1250.00').      Recognizes (+9 more)

### Community 24 - "JSON Schema Primitives"
Cohesion: 0.11
Nodes (25): integer, null, string, properties, type, type, type, type (+17 more)

### Community 25 - "SQLite Store"
Cohesion: 0.12
Nodes (16): FetchResult, One fetched page, uniform regardless of which strategy produced it., _FixtureFetcher, FormData, Headers, Method, Path, Strategy (+8 more)

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
Cohesion: 0.50
Nodes (3): The template this site's profile would be based on, if any., Which of the matching templates gets applied, or None for none of them.      One, _resolve_platform()

### Community 30 - "Store Timestamp Tests"
Cohesion: 0.20
Nodes (11): _css_variant(), extract_endpoint_variants(), Any, Rung 2: read the variant list out of a platform's JSON response.      `document`, Read one variant's fields out of its container node., Read variant rows out of a parsed JSON document.      Shared by the endpoint and, Follow a dotted path into parsed JSON, e.g. "data.options.0.price".      A segme, _resolve_path() (+3 more)

### Community 31 - "Live Profile Validation"
Cohesion: 0.10
Nodes (31): _canonical(), _covers(), _ends_with(), _index_of(), _match_text(), _own_identity(), product_label(), Perfume matching: brand and concentration are mandatory; fuzzy matching only app (+23 more)

### Community 32 - "Variant Extraction Fields"
Cohesion: 0.10
Nodes (20): attribute, in_stock, price, script, size_raw, type, properties, additionalProperties (+12 more)

### Community 33 - "_ResultRow"
Cohesion: 0.08
Nodes (62): Match, match_title(), parse_query(), PerfumeQuery, The perfume being looked for, split into its three identity parts.      `concent, One site title judged against the query.      `concentration` is what the title, Split one typed line into the perfumes it asks for, on " - ".      The separator, Split one typed line, "Dior Sauvage EDP", into the three identity parts.      Th (+54 more)

### Community 34 - "Fetch Strategy Probing"
Cohesion: 0.33
Nodes (6): css, embedded_json, endpoint, jsonld, enum, extraction

### Community 35 - "Platform Field Mapping"
Cohesion: 0.18
Nodes (11): field_map, product_json, source, variants_path, additionalProperties, allOf, description, required (+3 more)

### Community 36 - "Shipping Config Schema"
Cohesion: 0.14
Nodes (14): free_shipping_threshold_kurus, shipping_cost_kurus, minimum, type, free_shipping_threshold_kurus, notes, shipping, shipping_cost_kurus (+6 more)

### Community 37 - "_trial"
Cohesion: 0.33
Nodes (6): _balanced_value(), _embedded_documents(), _loads_or_skip(), Yield every JSON document the page hides, in document order., Parse `text` as JSON, yielding nothing when it isn't JSON.      Pages are full o, Return the JSON object or array beginning at or after `start`.      Scanning for

### Community 38 - "TUI Confirm Dialog"
Cohesion: 0.09
Nodes (33): A shop's imitation must not be stored as the perfume it imitates.      The clone, The drop happens here so no caller can forget it.      Both the CLI and the scre, One call has to leave a row the search table can read straight off.      The cal, The old price has to survive, and it must not become a second variant.      Appe, first_seen is what says how long a shop has carried a size., The title and URL are information, not identity.      A shop that rewords a list, EDT and EDP are different products at different prices.      Folding them into o, A sold-out size often shows no price at all, and 0 would mean free.      Writing (+25 more)

### Community 39 - "TUI App Shell"
Cohesion: 0.22
Nodes (6): _age_line(), Every check run against one site's profile, in the order they ran.      Checks s, Whether the profile is old enough to be worth re-discovering., The check that broke, or None if the profile is intact., The age note for one site, or None when its age is unremarkable.      A profile, SiteValidation

### Community 40 - "Fetch Backends"
Cohesion: 0.14
Nodes (14): curl_cffi, httpx, playwright, result_item, result_title, result_url, strategy, url_template (+6 more)

### Community 41 - "HTTP Request Schema"
Cohesion: 0.12
Nodes (17): GET, POST, additionalProperties, allOf, description, properties, type, default (+9 more)

### Community 42 - "Fixture Fetcher (Tests)"
Cohesion: 0.25
Nodes (8): exclude_keywords, max_size_ml, size_from, size_pattern, variant_rules, additionalProperties, required, type

### Community 44 - "Decant Variant Rules"
Cohesion: 0.09
Nodes (36): Run one "<css>::text" / "<css>::attr(name)" selector inside a node.      The nod, select_field(), _age_of(), Check, _count_result_cards(), _first_result_url(), _LayerUnavailable, live_query() (+28 more)

### Community 46 - "Offline Validation Fixtures"
Cohesion: 0.25
Nodes (8): type, additionalProperties, type, body, request_headers, additionalProperties, description, type

### Community 48 - "._build_rows"
Cohesion: 0.08
Nodes (46): _choose_strategy(), collect_prices(), DiscoveryReport, FieldConfidence, _flatten_defaults(), _format_choice(), _format_confidence(), _format_defaults() (+38 more)

### Community 50 - "Profile Age Checks"
Cohesion: 0.11
Nodes (44): format_live_report(), format_report(), Check one site's profile against that site's saved fixtures.      Never raises f, Validate every site, or just the ones named.      Serial rather than concurrent:, Run one site's profile against the real site.      Same contract as offline mode, Render the validations as the offline half of the report in APP_FLOW §6.      A, Render offline and live results side by side, as APP_FLOW §6 shows them.      Bo, validate_all_offline() (+36 more)

### Community 51 - "._refresh_table"
Cohesion: 0.07
Nodes (19): Changed, HeaderSelected, RowSelected, format_price(), Format a price for display (comma-thousands, dot-decimal).      Decimal('1250'), Decimal, Row, One priced size, exactly as the table shows it and as a keypress needs it. (+11 more)

### Community 53 - "conftest.py"
Cohesion: 0.20
Nodes (16): add_basket_item(), now_iso(), _perfume_id(), _product_id(), Connection, Return the current UTC time as 'YYYY-MM-DDTHH:MM:SSZ'.      Every timestamp writ, Write one scan's reading of one size, and return its snapshot id.      The perfu, Do the writing, without opening a transaction of its own. (+8 more)

### Community 54 - "Endpoint Schema Fields"
Cohesion: 0.22
Nodes (9): result_item, result_title, result_url, url_template, search, additionalProperties, description, required (+1 more)

### Community 56 - "Request Schema Fields"
Cohesion: 0.24
Nodes (6): BaseHTTPRequestHandler, _Handler, _playwright_usable(), Shared pytest fixtures.  A local HTTP server used by fetch/probe tests: real req, Whether the playwright rung can actually run here, binary included.      Checkin, server_url()

### Community 57 - "_FixtureFetcher"
Cohesion: 0.11
Nodes (18): What one site had to say about one query, and how much to trust it.      Four st, SiteResult, _listing_filter(), Any, CacheKey, CandidateFilter, VariantsRead, Decide, from a search result's own title, whether to open its page. (+10 more)

### Community 59 - "_named_profile"
Cohesion: 0.33
Nodes (7): _parse_selector(), Node, Run one "<css>::text" / "<css>::attr(name)" selector, reading every match., Split a "<css>::text" / "<css>::attr(name)" selector into its two parts., Read the attribute or text of one already-selected node, or None., _read_selected(), select_all()

### Community 63 - "CandidateFilter"
Cohesion: 0.20
Nodes (10): basket_prices(), Return the basket price matrix: one row per (line, site) that has a price., A stale reading must never outrank the one taken after it.      latest_prices al, A 10 ml listing must never fill a basket line asking for 5 ml.      The matrix j, Whether an out-of-stock price counts as missing is the caller's call.      Dropp, A basket line nobody sells must still be visible via basket_lines.      basket_p, test_basket_prices_has_no_row_for_a_line_no_site_prices(), test_basket_prices_joins_on_the_exact_integer_size() (+2 more)

### Community 67 - "test_cached_prices_is_empty_for_a_perfume_nobody_scanned"
Cohesion: 0.20
Nodes (10): cached_prices(), Return the latest stored price of every size of this perfume, per site.      Bra, The search screen's second search must be answered with today's numbers.      Tw, A search that named no concentration is asking for all of them.      "" means "a, A price nobody will scan again may not be offered as a result.      Refreshing i, Nothing on record is the state before a first search, not an error.      The sea, test_cached_prices_is_empty_for_a_perfume_nobody_scanned(), test_cached_prices_leaves_out_a_disabled_site() (+2 more)

### Community 72 - "ComposeResult"
Cohesion: 0.11
Nodes (11): Pressed, ComposeResult, Path, ConfirmScreen, ComposeResult, Path, Protocol, What this screen needs of engine.run_site.      A protocol rather than a plain c (+3 more)

## Knowledge Gaps
- **154 isolated node(s):** `parfum-finder`, `$schema`, `$id`, `title`, `description` (+149 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `SiteResult` connect `_FixtureFetcher` to `TUI App & Screens`, `Title Matcher`, `HTTP/Browser Fetching`, `Search/Basket Domain Models`, `TUI Confirm Dialog`, `CLI Entry Points`, `ComposeResult`, `Search Engine Core`, `Basket TUI Screen`, `Offline Profile Validation`, `._refresh_table`, `SQLite Store`?**
  _High betweenness centrality (0.053) - this node is a cross-community bridge._
- **Why does `PlaywrightNotInstalled` connect `HTTP/Browser Fetching` to `Search/Basket Domain Models`, `Search Engine per Site`, `Search Engine Core`, `FieldConfidence`, `._build_rows`, `Offline Profile Validation`, `Playwright Errors`, `Basket Site Scenarios`, `Request Schema Fields`, `_FixtureFetcher`?**
  _High betweenness centrality (0.050) - this node is a cross-community bridge._
- **Why does `SearchScreen` connect `._refresh_table` to `TUI App & Screens`, `_ResultRow`, `Title Matcher`, `Search/Basket Domain Models`, `ComposeResult`, `Search Engine Core`, `Search TUI Screen`, `_FixtureFetcher`?**
  _High betweenness centrality (0.033) - this node is a cross-community bridge._
- **Are the 10 inferred relationships involving `SearchScreen` (e.g. with `ParfumFinderApp` and `SiteResult`) actually correct?**
  _`SearchScreen` has 10 INFERRED edges - model-reasoned connections that need verification._
- **Are the 15 inferred relationships involving `PerfumeQuery` (e.g. with `SheetsError` and `WishlistRow`) actually correct?**
  _`PerfumeQuery` has 15 INFERRED edges - model-reasoned connections that need verification._
- **What connects `parfum-finder`, `$schema`, `$id` to the rest of the system?**
  _154 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `TUI App & Screens` be split into smaller, more focused modules?**
  _Cohesion score 0.093185789167152 - nodes in this community are weakly interconnected._