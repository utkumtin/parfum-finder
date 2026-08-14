# Graph Report - parfum-finder  (2026-08-11)

## Corpus Check
- 70 files · ~259,000 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1817 nodes · 4808 edges · 72 communities (59 shown, 13 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 177 edges (avg confidence: 0.59)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `4df60f0c`
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
- Runner
- Variant Pattern A
- Project Root
- ComposeResult
- _NoRootParser
- enum

## God Nodes (most connected - your core abstractions)
1. `search_site()` - 66 edges
2. `_profile()` - 58 edges
3. `SearchScreen` - 56 edges
4. `discover()` - 56 edges
5. `PerfumeQuery` - 50 edges
6. `BasketScreen` - 46 edges
7. `_write_profile()` - 45 edges
8. `match_title()` - 45 edges
9. `_app()` - 44 edges
10. `_submit_query()` - 43 edges

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

## Communities (72 total, 13 thin omitted)

### Community 0 - "TUI App & Screens"
Cohesion: 0.10
Nodes (98): The Textual-based terminal UI: search and basket screens., _app(), _basket(), _cells(), _days_ago(), _leg(), _ok(), _open_basket() (+90 more)

### Community 1 - "Site Profiles & Templates"
Cohesion: 0.06
Nodes (84): _check_hook_kinds(), deep_merge(), _load_json(), load_platform_template(), load_platform_templates(), load_site_hooks(), load_site_profile(), Any (+76 more)

### Community 2 - "Title Matcher"
Cohesion: 0.07
Nodes (34): _Change, BasketReport, One site's share of a split basket: what to buy there and what it costs.      `s, The cheapest basket split the search found. A heuristic, not a proof.      Every, What it would cost to buy some or all of the basket from one site.      `covered, Every site's single-site scenario, split by whether it covers everything.      A, SiteScenario, SplitLeg (+26 more)

### Community 3 - "HTTP/Browser Fetching"
Cohesion: 0.07
Nodes (37): BaseHTTPRequestHandler, browser_session(), fetch(), Strategy, Fetch one URL using exactly the given strategy.      `method`/`data` exist for t, Yield a fetcher that keeps one browser for every playwright page it reads., _Handler, _playwright_usable() (+29 more)

### Community 4 - "Search/Basket Domain Models"
Cohesion: 0.09
Nodes (96): LogCaptureFixture, MonkeyPatch, ParfumFinderApp, Runner, _app(), _basket_count(), _named_result(), _ok_result() (+88 more)

### Community 5 - "Search Engine per Site"
Cohesion: 0.15
Nodes (23): _close_browser(), _fetch_curl_cffi(), _fetch_httpx(), _fetch_playwright(), FetchResult, _launch_browser(), Any, FormData (+15 more)

### Community 6 - "Platform Discovery Flow"
Cohesion: 0.15
Nodes (59): PlatformChooser, _ask_chooser(), discover(), Put the question only when there is one, and hold the answer to it.      An answ, Measure the strategies a site needs, then read its JSON-LD with the winner., _attempt(), _fake_probe(), Any (+51 more)

### Community 7 - "CLI Entry Points"
Cohesion: 0.11
Nodes (47): CaptureFixture, Screen, ask_which_platform(), main(), Path, Scan every site for the perfumes named, store what came back, print it.      One, Ask at the terminal which of several matching templates to apply.      Asked whi, run_search() (+39 more)

### Community 8 - "Architecture Rationale Docs"
Cohesion: 0.05
Nodes (53): basket Subset Enumeration + Local Improvement Algorithm, basket Optimizer (optimize function), Clone/Original Distinction (KLON ← <orijinal>), discover Discovery Flow, engine Concurrency Model (parallel sites, serial within site), Extraction Ladder (jsonld/endpoint/embedded/css), Fail-loud / status=suspect policy, hooks/<id>.py Escape Hatch (+45 more)

### Community 9 - "Search Engine Core"
Cohesion: 0.07
Nodes (60): HTMLParser, _check_empty_search(), _check_variant_control(), ExtractionFailed, _fetch_page(), _headers(), _paced_fetcher(), _page_offers_sizes() (+52 more)

### Community 10 - "Basket Optimizer Core"
Cohesion: 0.12
Nodes (42): Collection, Prices, BasketItem, _ClimbState, optimize(), Basket scenario evaluation. A pure function, no network access, no sqlite.  Inpu, The hill-climb's working assignment plus the running per-site figures.      `sub, Score one site against the basket, or against a subset of it.      `item_ids` is (+34 more)

### Community 11 - "Basket Store & Pricing"
Cohesion: 0.07
Nodes (54): add_basket_item(), basket_prices(), Add a size of a perfume to the basket, and return the basket_item_id.      The p, Return the basket price matrix: one row per (line, site) that has a price., conn(), Connection, Path, Tests for parfum_finder.store: the timestamp helper and the schema.  The one har (+46 more)

### Community 12 - "JSON-LD Product Extraction"
Cohesion: 0.13
Nodes (32): extract_jsonld_products(), Read every JSON-LD Product declared on the page, in document order.      A block, _one_product_html(), Tests for parfum_finder.extract.  Every case here is a shape a real store actual, Wrap a JSON-LD product body in a page, for the one-field-at-a-time cases., test_a_broken_block_does_not_lose_the_valid_one(), test_availability_spellings_all_land_in_the_same_bucket(), test_boolean_values_are_never_read_as_price_or_text() (+24 more)

### Community 13 - "Basket TUI Screen"
Cohesion: 0.40
Nodes (5): price_history(), Row, Return one variant's past readings, newest first, capped at limit.      Empty fo, No history yet is a normal state for a variant, not an error to raise on., test_price_history_is_empty_for_an_unknown_variant()

### Community 14 - "Platform Schema"
Cohesion: 0.06
Nodes (31): any, defaults, fingerprint, additionalProperties, items, minItems, type, description (+23 more)

### Community 15 - "Product Extraction"
Cohesion: 0.10
Nodes (35): _as_str(), _build_offer(), _build_product(), _coerce_in_stock(), _collect_offers(), _collect_variants(), _css_variant(), JsonLdOffer (+27 more)

### Community 16 - "Schema Field Patterns"
Cohesion: 0.06
Nodes (33): format, pattern, type, pattern, type, default, type, pattern (+25 more)

### Community 17 - "Offline Profile Validation"
Cohesion: 0.07
Nodes (81): _candidates_to_open(), CacheKey, CandidateFilter, Path, VariantsRead, Run one site and classify what came back instead of raising.      It is also whe, Run every site against one query, all at once, and report each separately., Run one query against one site and read every hit's sizes.      Everything site- (+73 more)

### Community 18 - "Playwright Errors"
Cohesion: 0.13
Nodes (24): PlaywrightNoResponse, RuntimeError, Navigation completed but playwright returned no Response object.      Its own ty, _attempt(), _count_jsonld(), _count_product_objects(), _detect_platforms(), format_report() (+16 more)

### Community 19 - "Search TUI Screen"
Cohesion: 0.08
Nodes (41): find_header_columns(), find_match(), open_worksheet(), Any, Exception, Path, Protocol, Writing a search result onto the user's own Google Sheets wishlist.  The wishlis (+33 more)

### Community 20 - "Snapshot Writing"
Cohesion: 0.16
Nodes (20): apply_variant_rules(), _is_excluded(), Decimal, Turn raw size rows into decant variants, dropping what is not a decant.      Thr, Read one row's volume in millilitres, or None if the text does not say.      "fi, Whether this row is something other than a decant.      The size threshold is in, Convert a price in lira to whole kuruş.      Integers all the way, never a float, _read_size_ml() (+12 more)

### Community 21 - "Candidate Filtering"
Cohesion: 0.15
Nodes (18): extract_embedded_variants(), extract_jsonld_variants(), _flatten_jsonld(), Rung 1: read the page's JSON-LD as flat variant rows.      A product that declar, Turn one Product and everything under it into rows., Rung 3: read the JSON blob the page carries but does not display.      Two shape, _fixture(), Read a captured product page. (+10 more)

### Community 22 - "Basket Site Scenarios"
Cohesion: 0.21
Nodes (15): probe(), Fetch `url` with every strategy and report diagnostics for each.      timeout_s, MonkeyPatch, Tests for parfum_finder.probe.  probe() always tries all three strategies -- the, test_probe_counts_jsonld_product_and_platform_signature(), test_probe_counts_product_across_jsonld_root_shapes(), test_probe_counts_product_markup_without_any_jsonld(), test_probe_counts_products_nested_below_the_top_level() (+7 more)

### Community 23 - "Price/Size Normalization"
Cohesion: 0.12
Nodes (25): _classify_single_separator(), format_ml(), format_price(), _parse_number(), parse_price(), parse_size_ml(), Decimal, Number parsing and formatting for prices and volumes, plus text folding.  This i (+17 more)

### Community 24 - "JSON Schema Primitives"
Cohesion: 0.11
Nodes (25): integer, null, string, properties, type, type, type, type (+17 more)

### Community 25 - "SQLite Store"
Cohesion: 0.26
Nodes (7): _FixtureFetcher, FormData, Headers, Method, Strategy, Serves one site's saved capture in place of the network.      Only three kinds o, The one real result card that led to the captured product page.          Cut out

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
Cohesion: 0.16
Nodes (14): DiscoveryReport, _format_choice(), _format_confidence(), _format_fingerprint(), _format_fixtures(), format_report(), The template this site's profile would be based on, if any., The scored fields a person still has to confirm, in profile order.          Anyt (+6 more)

### Community 30 - "Store Timestamp Tests"
Cohesion: 0.14
Nodes (15): _balanced_value(), _embedded_documents(), extract_endpoint_variants(), _loads_or_skip(), Any, Rung 2: read the variant list out of a platform's JSON response.      `document`, Yield every JSON document the page hides, in document order., Parse `text` as JSON, yielding nothing when it isn't JSON.      Pages are full o (+7 more)

### Community 31 - "Live Profile Validation"
Cohesion: 0.09
Nodes (31): _canonical(), _covers(), _ends_with(), _index_of(), _match_text(), _own_identity(), product_label(), Perfume matching: brand and concentration are mandatory; fuzzy matching only app (+23 more)

### Community 32 - "Variant Extraction Fields"
Cohesion: 0.11
Nodes (18): attribute, in_stock, price, script, size_raw, type, properties, additionalProperties (+10 more)

### Community 33 - "_ResultRow"
Cohesion: 0.10
Nodes (52): Match, match_title(), parse_query(), PerfumeQuery, The perfume being looked for, split into its three identity parts.      `concent, One site title judged against the query.      `concentration` is what the title, Split one typed line, "Dior Sauvage EDP", into the three identity parts.      Th, Judge one site title against a query, or None if it is not that perfume.      No (+44 more)

### Community 34 - "Fetch Strategy Probing"
Cohesion: 0.17
Nodes (4): HeaderSelected, Empty the table for a new scan.          The columns are the same every time now, What each site charges for the product a block is about.          One entry per, Submitted

### Community 35 - "Platform Field Mapping"
Cohesion: 0.12
Nodes (16): field_map, product_json, source, variants_path, additionalProperties, allOf, description, required (+8 more)

### Community 36 - "Shipping Config Schema"
Cohesion: 0.14
Nodes (14): free_shipping_threshold_kurus, shipping_cost_kurus, minimum, type, free_shipping_threshold_kurus, notes, shipping, shipping_cost_kurus (+6 more)

### Community 37 - "_trial"
Cohesion: 0.24
Nodes (11): _flatten_defaults(), _format_defaults(), _match_platforms(), Any, Path, Every template with at least one of its markers somewhere in the page.      Case, Write one page and return where it landed plus its digest.      Saved as UTF-8 w, Render a template's defaults as one dotted key per line. (+3 more)

### Community 38 - "TUI Confirm Dialog"
Cohesion: 0.10
Nodes (33): One priced size of one perfume on one site, ready to be written.      The perfum, SnapshotRow, The drop happens here so no caller can forget it.      Both the CLI and the scre, One call has to leave a row the search table can read straight off.      The cal, The old price has to survive, and it must not become a second variant.      Appe, first_seen is what says how long a shop has carried a size., The title and URL are information, not identity.      A shop that rewords a list, EDT and EDP are different products at different prices.      Folding them into o (+25 more)

### Community 39 - "TUI App Shell"
Cohesion: 0.21
Nodes (6): Decimal, Row, One priced size, exactly as the table shows it and as a keypress needs it., The default order: typed order, product, site, size.          The typed order co, The order once a column has been picked: the site layer drops out.          Aski, _ResultRow

### Community 40 - "Fetch Backends"
Cohesion: 0.14
Nodes (14): curl_cffi, httpx, playwright, result_item, result_title, result_url, strategy, url_template (+6 more)

### Community 41 - "HTTP Request Schema"
Cohesion: 0.14
Nodes (14): GET, POST, properties, default, enum, type, type, type (+6 more)

### Community 42 - "Fixture Fetcher (Tests)"
Cohesion: 0.25
Nodes (8): exclude_keywords, max_size_ml, size_from, size_pattern, variant_rules, additionalProperties, required, type

### Community 43 - "FieldConfidence"
Cohesion: 0.32
Nodes (7): FieldConfidence, One field this run can fill in, with how far it can be trusted.      `field` is, Every profile field this run can put a value on, scored., Score every profile field this run can fill in, in profile order.      Only fiel, Read the extraction layer off the page, for a site no template covers.      Judg, _score_extraction(), score_fields()

### Community 44 - "Decant Variant Rules"
Cohesion: 0.09
Nodes (36): The Textual App root. Handles screen navigation and is the app's default entry p, _age_of(), Check, _count_result_cards(), _first_result_url(), _LayerUnavailable, live_query(), _no_results_check() (+28 more)

### Community 45 - "Multi-Site Search Run"
Cohesion: 0.29
Nodes (6): _choose_strategy(), Strategy, _qualifies(), The strategy the trials actually ran with., Pick the cheapest strategy that came back with real content, or None.      probe, Whether one strategy came back with a usable page.

### Community 46 - "Offline Validation Fixtures"
Cohesion: 0.25
Nodes (8): type, additionalProperties, type, body, request_headers, additionalProperties, description, type

### Community 47 - "Basket Domain Logic"
Cohesion: 0.40
Nodes (3): ComposeResult, ComposeResult, Static

### Community 48 - "._build_rows"
Cohesion: 0.20
Nodes (18): collect_prices(), _format_product(), _format_stock(), _format_trial(), _has_exact_price(), PageTrial, Decimal, Site discovery: turns a URL into a profile, with human review. Not fully automat (+10 more)

### Community 49 - "test_engine.py"
Cohesion: 0.50
Nodes (4): _collect_products(), _has_type(), Walk a parsed JSON-LD block and append every Product found, depth first.      De, Whether a node's "@type" names `name`, as a string or inside a list.      Substr

### Community 50 - "Profile Age Checks"
Cohesion: 0.07
Nodes (56): _age_line(), format_live_report(), format_report(), profile_age_days(), datetime, Every check run against one site's profile, in the order they ran.      Checks s, Whether the profile is old enough to be worth re-discovering., The check that broke, or None if the profile is intact. (+48 more)

### Community 51 - "._refresh_table"
Cohesion: 0.11
Nodes (5): Changed, RowSelected, The initial screen: search bar, streaming results table, notices, footer., SearchScreen, Worksheet

### Community 53 - "conftest.py"
Cohesion: 0.12
Nodes (31): One decant size of one product, in the units the database stores.      Tenths of, Variant, basket_lines(), basket_sites(), BasketLine, BasketSite, now_iso(), _perfume_id() (+23 more)

### Community 54 - "Endpoint Schema Fields"
Cohesion: 0.22
Nodes (9): result_item, result_title, result_url, url_template, search, additionalProperties, description, required (+1 more)

### Community 57 - "_FixtureFetcher"
Cohesion: 0.18
Nodes (9): CacheKey, Fetcher, SnapshotRow, Any, SiteResult, One perfume of a search, as typed and as parsed.      The index is the outermost, Scan one site for every perfume of this search, one at a time.          Serial i, _Search (+1 more)

### Community 60 - "_NoRootParser"
Cohesion: 0.25
Nodes (8): Split one typed line into the perfumes it asks for, on " - ".      The separator, split_queries(), test_a_hyphen_inside_a_brand_name_does_not_split_the_search(), test_a_line_naming_three_perfumes_is_read_as_three_searches(), test_a_piece_that_names_no_perfume_survives_to_be_complained_about(), test_a_stray_separator_is_not_worth_failing_over(), test_one_perfume_is_still_one_search(), test_the_same_perfume_typed_twice_is_scanned_once()

### Community 61 - "SiteScenario"
Cohesion: 0.09
Nodes (33): _listing_filter(), Any, CandidateFilter, Connection, Command-line entry point.  Subcommands will be added incrementally as the projec, Scan every perfume against every site and print each site as it lands.      One, Decide, from a search result's own title, whether to open its page., Write one site's rows in a transaction of its own.      Per site rather than per (+25 more)

### Community 72 - "ComposeResult"
Cohesion: 0.11
Nodes (13): CandidateFilter, PerfumeQuery, Pressed, Protocol, Path, ConfirmScreen, _listing_filter(), Path (+5 more)

### Community 91 - "enum"
Cohesion: 0.33
Nodes (6): css, embedded_json, endpoint, jsonld, enum, extraction

## Knowledge Gaps
- **154 isolated node(s):** `parfum-finder`, `$schema`, `$id`, `title`, `description` (+149 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **13 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `SearchScreen` connect `._refresh_table` to `TUI App & Screens`, `Fetch Strategy Probing`, `TUI App Shell`, `ComposeResult`, `CLI Entry Points`, `Decant Variant Rules`, `Basket Domain Logic`, `_FixtureFetcher`?**
  _High betweenness centrality (0.059) - this node is a cross-community bridge._
- **Why does `discover()` connect `Platform Discovery Flow` to `Site Profiles & Templates`, `_trial`, `CLI Entry Points`, `Multi-Site Search Run`, `._build_rows`, `SiteScenario`, `Basket Site Scenarios`, `Discovery CLI Reporting`?**
  _High betweenness centrality (0.034) - this node is a cross-community bridge._
- **Why does `parse_query()` connect `_ResultRow` to `TUI Confirm Dialog`, `CLI Entry Points`, `Offline Profile Validation`, `Search TUI Screen`, `SiteScenario`, `Live Profile Validation`?**
  _High betweenness centrality (0.030) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `SearchScreen` (e.g. with `ParfumFinderApp` and `test_s_opens_the_basket_and_escape_comes_back_to_the_results()`) actually correct?**
  _`SearchScreen` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 9 inferred relationships involving `PerfumeQuery` (e.g. with `SheetsError` and `WishlistRow`) actually correct?**
  _`PerfumeQuery` has 9 INFERRED edges - model-reasoned connections that need verification._
- **What connects `parfum-finder`, `$schema`, `$id` to the rest of the system?**
  _154 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `TUI App & Screens` be split into smaller, more focused modules?**
  _Cohesion score 0.09656565656565656 - nodes in this community are weakly interconnected._