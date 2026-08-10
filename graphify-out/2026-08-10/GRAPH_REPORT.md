# Graph Report - parfum-finder  (2026-08-10)

## Corpus Check
- 68 files · ~255,625 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1742 nodes · 4746 edges · 71 communities (69 shown, 2 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 190 edges (avg confidence: 0.57)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `5456b5f3`
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
- Price History
- SiteValidation
- enum
- .__call__
- rate_limit_ms
- format_age
- Variant Pattern A
- Project Root
- basket_prices
- ComposeResult

## God Nodes (most connected - your core abstractions)
1. `search_site()` - 66 edges
2. `SearchScreen` - 58 edges
3. `_profile()` - 58 edges
4. `discover()` - 56 edges
5. `BasketScreen` - 53 edges
6. `SiteResult` - 52 edges
7. `PerfumeQuery` - 52 edges
8. `match_title()` - 43 edges
9. `_app()` - 43 edges
10. `Fetcher` - 42 edges

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

## Communities (71 total, 2 thin omitted)

### Community 0 - "TUI App & Screens"
Cohesion: 0.10
Nodes (98): The Textual-based terminal UI: search and basket screens., _app(), _basket(), _cells(), _days_ago(), _leg(), _ok(), _open_basket() (+90 more)

### Community 1 - "Site Profiles & Templates"
Cohesion: 0.06
Nodes (83): _check_hook_kinds(), deep_merge(), _load_json(), load_platform_template(), load_platform_templates(), load_site_hooks(), load_site_profile(), Any (+75 more)

### Community 2 - "Title Matcher"
Cohesion: 0.10
Nodes (27): BasketReport, _ClimbState, Basket scenario evaluation. A pure function, no network access, no sqlite.  Inpu, One site's share of a split basket: what to buy there and what it costs.      `s, The cheapest basket split the search found. A heuristic, not a proof.      Every, The hill-climb's working assignment plus the running per-site figures.      `sub, What it would cost to buy some or all of the basket from one site.      `covered, Every site's single-site scenario, split by whether it covers everything.      A (+19 more)

### Community 3 - "HTTP/Browser Fetching"
Cohesion: 0.12
Nodes (30): browser_session(), fetch(), PlaywrightNotInstalled, Strategy, Fetch one URL using exactly the given strategy.      `method`/`data` exist for t, Yield a fetcher that keeps one browser for every playwright page it reads., The "playwright" strategy was requested but cannot run at all.      Covers both, test_the_no_results_page_would_otherwise_read_as_suspect() (+22 more)

### Community 4 - "Search/Basket Domain Models"
Cohesion: 0.08
Nodes (96): LogCaptureFixture, One decant size of one product, in the units the database stores.      Tenths of, A candidate together with the decant sizes its product page offers., SearchHit, Variant, connect(), Path, Open the price database, creating the schema if it isn't there yet.      Foreign (+88 more)

### Community 5 - "Search Engine per Site"
Cohesion: 0.19
Nodes (17): _check_empty_search(), _check_variant_control(), ExtractionFailed, RuntimeError, A page answered but gave up nothing, where something was expected.      This is, Run one query against one site and read every hit's sizes.      Everything site-, Fail when a search yielded no rows off a page that plainly lists products., Fail when the page's size picker offers more sizes than the layer read.      The (+9 more)

### Community 6 - "Platform Discovery Flow"
Cohesion: 0.15
Nodes (59): PlatformChooser, _ask_chooser(), discover(), Put the question only when there is one, and hold the answer to it.      An answ, Measure the strategies a site needs, then read its JSON-LD with the winner., _attempt(), _fake_probe(), Any (+51 more)

### Community 7 - "CLI Entry Points"
Cohesion: 0.15
Nodes (39): CaptureFixture, ask_which_platform(), main(), Path, Scan every site for the perfumes named, store what came back, print it.      One, Ask at the terminal which of several matching templates to apply.      Asked whi, run_search(), _answers() (+31 more)

### Community 8 - "Architecture Rationale Docs"
Cohesion: 0.05
Nodes (53): basket Subset Enumeration + Local Improvement Algorithm, basket Optimizer (optimize function), Clone/Original Distinction (KLON ← <orijinal>), discover Discovery Flow, engine Concurrency Model (parallel sites, serial within site), Extraction Ladder (jsonld/endpoint/embedded/css), Fail-loud / status=suspect policy, hooks/<id>.py Escape Hatch (+45 more)

### Community 9 - "Search Engine Core"
Cohesion: 0.07
Nodes (52): _candidates_to_open(), _fetch_page(), _headers(), _is_excluded(), _paced_fetcher(), _page_offers_sizes(), _page_says_sold_out(), _parse_endpoint_document() (+44 more)

### Community 10 - "Basket Optimizer Core"
Cohesion: 0.15
Nodes (36): Collection, Prices, BasketItem, optimize(), Score one site against the basket, or against a subset of it.      `item_ids` is, Score every enabled site against the whole basket and sort the results.      Sit, Search for the cheapest way to split the basket across several sites.      Retur, One line of the shopping list: a basket row, not a unit count.      `item_id` is (+28 more)

### Community 11 - "Basket Store & Pricing"
Cohesion: 0.10
Nodes (32): add_basket_item(), Add a size of a perfume to the basket, and return the basket_item_id.      The p, Connection, Two snapshots written in the same second must resolve to the newer one.      A s, 5 ml at 125,00 TL is 25,00 TL per ml. Stored as kurus, ml as tenths., No price yet means no row, so the basket LEFT JOIN reads it as missing., A zero ml variant is a parse failure, and it must not reach the table.      If i, Adding the same perfume and size twice must accumulate, not clobber.      The ba (+24 more)

### Community 12 - "JSON-LD Product Extraction"
Cohesion: 0.15
Nodes (30): extract_jsonld_products(), Read every JSON-LD Product declared on the page, in document order.      A block, _one_product_html(), Tests for parfum_finder.extract.  Every case here is a shape a real store actual, Wrap a JSON-LD product body in a page, for the one-field-at-a-time cases., test_a_broken_block_does_not_lose_the_valid_one(), test_availability_spellings_all_land_in_the_same_bucket(), test_boolean_values_are_never_read_as_price_or_text() (+22 more)

### Community 13 - "Basket TUI Screen"
Cohesion: 0.17
Nodes (6): _Change, BasketScreen, Any, The basket: the list on top, one scenario per site underneath., _remove(), _set_qty()

### Community 14 - "Platform Schema"
Cohesion: 0.06
Nodes (31): any, defaults, fingerprint, additionalProperties, items, minItems, type, description (+23 more)

### Community 15 - "Product Extraction"
Cohesion: 0.09
Nodes (37): _as_str(), _build_offer(), _coerce_in_stock(), _collect_offers(), _css_variant(), extract_css_variants(), extract_endpoint_variants(), _flatten_jsonld() (+29 more)

### Community 16 - "Schema Field Patterns"
Cohesion: 0.05
Nodes (39): css, embedded_json, endpoint, jsonld, format, pattern, type, pattern (+31 more)

### Community 17 - "Offline Profile Validation"
Cohesion: 0.11
Nodes (20): Check, _first_result_url(), _LayerUnavailable, _no_results_check(), _probe_layer(), _probe_other_layers(), Any, Exception (+12 more)

### Community 18 - "Playwright Errors"
Cohesion: 0.12
Nodes (25): _choose_strategy(), _qualifies(), Pick the cheapest strategy that came back with real content, or None.      probe, Whether one strategy came back with a usable page., _attempt(), _count_jsonld(), _count_product_objects(), _detect_platforms() (+17 more)

### Community 19 - "Search TUI Screen"
Cohesion: 0.13
Nodes (21): _listing_filter(), Any, CandidateFilter, Connection, Command-line entry point.  Subcommands will be added incrementally as the projec, Scan every perfume against every site and print each site as it lands.      One, Decide, from a search result's own title, whether to open its page., One line per site: which site, how it went, and what it said.      The site id i (+13 more)

### Community 20 - "Snapshot Writing"
Cohesion: 0.33
Nodes (6): _balanced_value(), _embedded_documents(), _loads_or_skip(), Yield every JSON document the page hides, in document order., Parse `text` as JSON, yielding nothing when it isn't JSON.      Pages are full o, Return the JSON object or array beginning at or after `start`.      Scanning for

### Community 21 - "Candidate Filtering"
Cohesion: 0.19
Nodes (22): format_report(), Check one site's profile against that site's saved fixtures.      Never raises f, Render the validations as the offline half of the report in APP_FLOW §6.      A, validate_offline(), _corrupted_sites_dir(), _iso_days_ago(), Any, Path (+14 more)

### Community 22 - "Basket Site Scenarios"
Cohesion: 0.19
Nodes (13): HTMLParser, _parse_selector(), Node, Run one "<css>::text" / "<css>::attr(name)" selector inside a node.      The nod, Run one "<css>::text" / "<css>::attr(name)" selector, reading every match., Split a "<css>::text" / "<css>::attr(name)" selector into its two parts., Read the attribute or text of one already-selected node, or None., _read_selected() (+5 more)

### Community 23 - "Price/Size Normalization"
Cohesion: 0.17
Nodes (19): _classify_single_separator(), format_price(), _parse_number(), parse_price(), parse_size_ml(), Decimal, Number parsing and formatting for prices and volumes, plus text folding.  This i, Decide whether a lone separator marks a fraction or a thousands group.      Retu (+11 more)

### Community 24 - "JSON Schema Primitives"
Cohesion: 0.11
Nodes (25): integer, null, string, properties, type, type, type, type (+17 more)

### Community 25 - "SQLite Store"
Cohesion: 0.21
Nodes (15): _close_browser(), _fetch_curl_cffi(), _fetch_httpx(), _fetch_playwright(), _launch_browser(), Any, FormData, Headers (+7 more)

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
Cohesion: 0.09
Nodes (39): collect_prices(), DiscoveryReport, FieldConfidence, _format_choice(), _format_confidence(), _format_fingerprint(), _format_fixtures(), _format_product() (+31 more)

### Community 30 - "Store Timestamp Tests"
Cohesion: 0.16
Nodes (7): PlaywrightNoResponse, RuntimeError, Navigation completed but playwright returned no Response object.      Its own ty, _FakeBrowser, _FakePage, Any, test_fetch_playwright_no_response_raises_its_own_error_type()

### Community 31 - "Live Profile Validation"
Cohesion: 0.08
Nodes (22): Changed, Write one site's rows in a transaction of its own.      Per site rather than per, _store_site_result(), What one site had to say about one query, and how much to trust it.      Four st, SiteResult, Turn one site's hits into the rows write_snapshots is ready to store.      Share, snapshot_rows(), _listing_filter() (+14 more)

### Community 32 - "Variant Extraction Fields"
Cohesion: 0.12
Nodes (16): attribute, script, type, additionalProperties, allOf, description, properties, type (+8 more)

### Community 33 - "_ResultRow"
Cohesion: 0.05
Nodes (91): _canonical(), _covers(), _ends_with(), _index_of(), Match, _match_text(), match_title(), _own_identity() (+83 more)

### Community 34 - "Fetch Strategy Probing"
Cohesion: 0.18
Nodes (16): A multi-site price and stock comparison tool for perfume decants.  Includes a sh, probe(), Fetch `url` with every strategy and report diagnostics for each.      timeout_s, MonkeyPatch, Tests for parfum_finder.probe.  probe() always tries all three strategies -- the, test_probe_counts_jsonld_product_and_platform_signature(), test_probe_counts_product_across_jsonld_root_shapes(), test_probe_counts_product_markup_without_any_jsonld() (+8 more)

### Community 35 - "Platform Field Mapping"
Cohesion: 0.18
Nodes (11): field_map, product_json, source, variants_path, required, additionalProperties, allOf, description (+3 more)

### Community 36 - "Shipping Config Schema"
Cohesion: 0.14
Nodes (14): free_shipping_threshold_kurus, shipping_cost_kurus, minimum, type, free_shipping_threshold_kurus, notes, shipping, shipping_cost_kurus (+6 more)

### Community 37 - "Discovery Report Model"
Cohesion: 0.22
Nodes (15): Run one site's profile against the real site.      Same contract as offline mode, validate_live(), _DeadSite, _FakeSite, _fixture_site(), M5's own criterion: when a profile stops agreeing with its site's real markup, o, A stand-in for one live site, answering the search page then the rest.      Live, A host that cannot be reached at all. (+7 more)

### Community 38 - "TUI Confirm Dialog"
Cohesion: 0.19
Nodes (8): Pressed, One priced size of one perfume on one site, ready to be written.      The perfum, Write a whole scan at once and return how many prices were recorded.      Every, SnapshotRow, write_snapshots(), ConfirmScreen, The search screen: a progress bar while scanning, one grouped table after.  Colu, Asks before a low-confidence match is written to the basket.      The two answer

### Community 39 - "TUI App Shell"
Cohesion: 0.12
Nodes (11): Screen, ParfumFinderApp, Path, The Textual App root. Handles screen navigation and is the app's default entry p, Root app: pushes the search screen on mount., Path, Path, Protocol (+3 more)

### Community 40 - "Fetch Backends"
Cohesion: 0.14
Nodes (14): curl_cffi, httpx, playwright, result_item, result_title, result_url, strategy, url_template (+6 more)

### Community 41 - "HTTP Request Schema"
Cohesion: 0.14
Nodes (14): GET, POST, properties, default, enum, type, type, type (+6 more)

### Community 42 - "Fixture Fetcher (Tests)"
Cohesion: 0.24
Nodes (6): BaseHTTPRequestHandler, _Handler, _playwright_usable(), Shared pytest fixtures.  A local HTTP server used by fetch/probe tests: real req, Whether the playwright rung can actually run here, binary included.      Checkin, server_url()

### Community 43 - "Validation Reporting"
Cohesion: 0.31
Nodes (9): _named_profile(), Any, The real fetcher, with a list of every URL it was asked for., A profile whose search page lists two houses' bottles, as shops do., test_a_listing_from_another_house_costs_no_product_request(), test_one_product_listed_under_two_searches_is_read_once(), test_two_shops_sharing_a_url_do_not_read_each_others_pages(), test_without_a_filter_every_listing_is_still_opened() (+1 more)

### Community 44 - "Decant Variant Rules"
Cohesion: 0.14
Nodes (21): _age_of(), live_query(), _path(), profile_age_days(), datetime, Profile staleness checks. Two modes: offline (against saved fixtures) and live (, A URL's path with no trailing slash, for comparing two spellings of one page., Every site that has a profile, sorted so reports read the same way twice. (+13 more)

### Community 45 - "Multi-Site Search Run"
Cohesion: 0.17
Nodes (16): extract_embedded_variants(), extract_jsonld_variants(), Rung 1: read the page's JSON-LD as flat variant rows.      A product that declar, Rung 3: read the JSON blob the page carries but does not display.      Two shape, _fixture(), Read a captured product page., test_embedded_attribute_reads_a_second_site_with_the_same_shape(), test_embedded_attribute_reads_the_woocommerce_variation_table() (+8 more)

### Community 46 - "Offline Validation Fixtures"
Cohesion: 0.25
Nodes (8): type, additionalProperties, type, body, request_headers, additionalProperties, description, type

### Community 47 - "Basket Domain Logic"
Cohesion: 0.10
Nodes (43): Run one site and classify what came back instead of raising.      It is also whe, run_site(), _profile(), Tests for the profile-driven search in parfum_finder.engine.  What these defend, A minimal working profile, with the fields a case cares about swapped in., test_a_broken_profile_is_still_suspect_when_no_title_looked_right(), test_a_dead_link_selector_is_suspect_not_empty(), test_a_dead_row_selector_on_a_full_page_is_suspect() (+35 more)

### Community 48 - "._build_rows"
Cohesion: 0.29
Nodes (7): in_stock, price, size_raw, additionalProperties, required, type, field_map

### Community 49 - "test_engine.py"
Cohesion: 0.27
Nodes (13): apply_variant_rules(), Turn raw size rows into decant variants, dropping what is not a decant.      Thr, _row(), test_a_keyword_in_the_size_label_excludes_the_row_too(), test_a_literal_zero_price_reads_as_no_price_not_a_free_perfume(), test_a_size_at_the_threshold_is_a_bottle_whatever_it_calls_itself(), test_a_size_that_cannot_be_read_is_dropped(), test_an_uppercase_turkish_keyword_still_matches() (+5 more)

### Community 50 - "Profile Age Checks"
Cohesion: 0.18
Nodes (13): _flatten_defaults(), _format_defaults(), _match_platforms(), Any, Path, Strategy, The strategy the trials actually ran with., Every template with at least one of its markers somewhere in the page.      Case (+5 more)

### Community 51 - "._refresh_table"
Cohesion: 0.10
Nodes (11): HeaderSelected, RowSelected, Decimal, Row, One priced size, exactly as the table shows it and as a keypress needs it., The initial screen: search bar, streaming results table, notices, footer., What each site charges for the product a block is about.          One entry per, The default order: typed order, product, site, size.          The typed order co (+3 more)

### Community 52 - "._cells"
Cohesion: 0.22
Nodes (10): _build_product(), _collect_products(), _collect_variants(), _has_type(), Walk a parsed JSON-LD block and append every Product found, depth first.      De, Whether a node's "@type" names `name`, as a string or inside a list.      Substr, Turn one Product node into a JsonLdProduct., Read the sizes listed by the parent group a product points back to.      Some st (+2 more)

### Community 53 - "conftest.py"
Cohesion: 0.16
Nodes (21): basket_prices(), basket_sites(), BasketSite, _perfume_id(), _product_id(), Connection, SQLite persistence: an append-only price history.  Tables: sites, perfumes, prod, Write one scan's reading of one size, and return its snapshot id.      The perfu (+13 more)

### Community 54 - "Endpoint Schema Fields"
Cohesion: 0.22
Nodes (9): result_item, result_title, result_url, url_template, search, additionalProperties, description, required (+1 more)

### Community 55 - "tui/__init__.py"
Cohesion: 0.12
Nodes (18): now_iso(), Return the current UTC time as 'YYYY-MM-DDTHH:MM:SSZ'.      Every timestamp writ, conn(), Path, Tests for parfum_finder.store: the timestamp helper and the schema.  The one har, An update aimed at a row that isn't there means the caller is out of sync., A snapshot pointing at a variant that doesn't exist has to be rejected.      SQL, Reopening an existing database must not wipe or re-raise on its schema. (+10 more)

### Community 56 - "Request Schema Fields"
Cohesion: 0.31
Nodes (11): Path, Give the test profile's site id a hook file. The id is what binds them., test_a_before_search_that_returns_no_query_is_refused(), test_a_broken_hook_is_an_error_not_a_silent_empty(), test_a_hook_that_reads_nothing_is_named_as_the_culprit(), test_a_site_with_no_hook_file_is_driven_by_its_profile_alone(), test_after_search_can_drop_a_result_the_selectors_could_not(), test_before_search_rewrites_the_query_that_is_actually_sent() (+3 more)

### Community 57 - "_FixtureFetcher"
Cohesion: 0.31
Nodes (6): _FixtureFetcher, FormData, Headers, Method, Strategy, Serves one site's saved capture in place of the network.      Only three kinds o

### Community 58 - "ComposeResult"
Cohesion: 0.24
Nodes (8): format_ml(), Format a volume for display (dot-decimal): Decimal('1.5') -> '1.5 ml'., BasketLine, BasketPrice, One row of the basket: a size of a perfume, with the identity spelled out., One site's latest price for one basket line, only when it has one.      Rows wit, _label(), Name one basket line the way a missing-item warning has to read it.

### Community 59 - "_named_profile"
Cohesion: 0.29
Nodes (7): items, type, type, items, type, exclude_keywords, needs_review

### Community 60 - "_NoRootParser"
Cohesion: 0.16
Nodes (14): FetchResult, One fetched page, uniform regardless of which strategy produced it., _counting_fetcher(), _NoRootParser, Exception, MonkeyPatch, Record every delay the engine asks for instead of serving it.      Waiting for r, Answer each call with the next canned result, then repeat the last one. (+6 more)

### Community 61 - "Price History"
Cohesion: 0.22
Nodes (9): price_history(), Row, Return one variant's past readings, newest first, capped at limit.      Empty fo, The trend panel reads row 0 as the latest reading, so order is the point.      A, No history yet is a normal state for a variant, not an error to raise on., The identity a real scan writes must be the identity these lookups accept., test_a_scanned_perfume_can_be_read_back_by_basket_and_history(), test_price_history_is_empty_for_an_unknown_variant() (+1 more)

### Community 62 - "SiteValidation"
Cohesion: 0.25
Nodes (7): _age_line(), format_live_report(), Every check run against one site's profile, in the order they ran.      Checks s, Whether the profile is old enough to be worth re-discovering., The age note for one site, or None when its age is unremarkable.      A profile, Render offline and live results side by side, as APP_FLOW §6 shows them.      Bo, SiteValidation

### Community 63 - "enum"
Cohesion: 0.40
Nodes (4): basket_lines(), Return every basket line, oldest add first.      Ordered by added_at with basket, A basket line nobody sells must still be visible via basket_lines.      basket_p, test_basket_prices_has_no_row_for_a_line_no_site_prices()

### Community 64 - ".__call__"
Cohesion: 0.53
Nodes (4): FormData, Headers, Method, Strategy

### Community 65 - "rate_limit_ms"
Cohesion: 0.50
Nodes (3): One site's shipping terms, read once and reused for every scenario.      `free_s, ShippingConfig, The three inputs basket.py's pure functions score: items, prices, shipping.

### Community 66 - "format_age"
Cohesion: 0.40
Nodes (4): format_age(), Turn a price age in days into the words the age column shows., The age column exists to be glanced at, so it is phrased, not printed., test_format_age_reads_as_words_not_a_timestamp()

### Community 71 - "basket_prices"
Cohesion: 0.09
Nodes (33): The drop happens here so no caller can forget it.      Both the CLI and the scre, One call has to leave a row the search table can read straight off.      The cal, The old price has to survive, and it must not become a second variant.      Appe, first_seen is what says how long a shop has carried a size., The title and URL are information, not identity.      A shop that rewords a list, EDT and EDP are different products at different prices.      Folding them into o, A sold-out size often shows no price at all, and 0 would mean free.      Writing, The column is 0/1, so the tri-state has to land somewhere on purpose.      Unkno (+25 more)

### Community 72 - "ComposeResult"
Cohesion: 0.40
Nodes (3): ComposeResult, ComposeResult, Static

## Knowledge Gaps
- **154 isolated node(s):** `parfum-finder`, `$schema`, `$id`, `title`, `description` (+149 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `SiteResult` connect `Live Profile Validation` to `TUI App & Screens`, `Site Profiles & Templates`, `Title Matcher`, `HTTP/Browser Fetching`, `Search/Basket Domain Models`, `TUI Confirm Dialog`, `TUI App Shell`, `basket_prices`, `Search Engine Core`, `Basket TUI Screen`, `Product Extraction`, `Basket Domain Logic`, `Search TUI Screen`, `._refresh_table`, `conftest.py`, `ComposeResult`, `_NoRootParser`, `Price History`?**
  _High betweenness centrality (0.051) - this node is a cross-community bridge._
- **Why does `BasketScreen` connect `Basket TUI Screen` to `TUI App & Screens`, `rate_limit_ms`, `Title Matcher`, `_ResultRow`, `format_age`, `TUI Confirm Dialog`, `TUI App Shell`, `ComposeResult`, `Basket Optimizer Core`, `._refresh_table`, `conftest.py`, `ComposeResult`, `Live Profile Validation`?**
  _High betweenness centrality (0.035) - this node is a cross-community bridge._
- **Why does `PerfumeQuery` connect `_ResultRow` to `Title Matcher`, `TUI Confirm Dialog`, `TUI App Shell`, `basket_prices`, `Basket TUI Screen`, `Search TUI Screen`, `._refresh_table`, `conftest.py`, `ComposeResult`, `Live Profile Validation`?**
  _High betweenness centrality (0.032) - this node is a cross-community bridge._
- **Are the 7 inferred relationships involving `SearchScreen` (e.g. with `ParfumFinderApp` and `SiteResult`) actually correct?**
  _`SearchScreen` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Are the 18 inferred relationships involving `BasketScreen` (e.g. with `BasketItem` and `BasketReport`) actually correct?**
  _`BasketScreen` has 18 INFERRED edges - model-reasoned connections that need verification._
- **What connects `parfum-finder`, `$schema`, `$id` to the rest of the system?**
  _154 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `TUI App & Screens` be split into smaller, more focused modules?**
  _Cohesion score 0.09656565656565656 - nodes in this community are weakly interconnected._