# Graph Report - parfum-finder  (2026-08-10)

## Corpus Check
- 68 files · ~252,480 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1714 nodes · 4635 edges · 79 communities (74 shown, 5 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 190 edges (avg confidence: 0.57)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `a243713d`
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
- basket_lines
- Variant Pattern A
- Project Root
- basket_prices
- _NoRootParser
- _trial
- ._start_search
- set_basket_qty
- .__call__
- SiteScenario
- test_basket_sites_preserves_a_null_free_shipping_threshold_as_none

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

## Communities (79 total, 5 thin omitted)

### Community 0 - "TUI App & Screens"
Cohesion: 0.11
Nodes (88): The Textual-based terminal UI: search and basket screens., _app(), _basket(), _cells(), _days_ago(), _leg(), _ok(), _open_basket() (+80 more)

### Community 1 - "Site Profiles & Templates"
Cohesion: 0.06
Nodes (81): _check_hook_kinds(), deep_merge(), _load_json(), load_platform_template(), load_platform_templates(), load_site_hooks(), load_site_profile(), Any (+73 more)

### Community 2 - "Title Matcher"
Cohesion: 0.11
Nodes (31): parse_query(), Split one typed line into the perfumes it asks for, on " - ".      The separator, Split one typed line, "Dior Sauvage EDP", into the three identity parts.      Th, Whether a search result's own listing text is worth opening the page for.      J, split_queries(), title_could_match(), Tests for parfum_finder.matcher.  The thing being defended here is not "does it, test_a_brand_the_shop_writes_out_in_full_does_not_cost_the_match() (+23 more)

### Community 3 - "HTTP/Browser Fetching"
Cohesion: 0.12
Nodes (30): browser_session(), fetch(), PlaywrightNotInstalled, Fetch one URL using exactly the given strategy.      `method`/`data` exist for t, Yield a fetcher that keeps one browser for every playwright page it reads., The "playwright" strategy was requested but cannot run at all.      Covers both, test_the_no_results_page_would_otherwise_read_as_suspect(), _fake_launch() (+22 more)

### Community 4 - "Search/Basket Domain Models"
Cohesion: 0.08
Nodes (100): LogCaptureFixture, ProductCandidate, One hit on a search results page, before its product page is opened.      `raw_t, One decant size of one product, in the units the database stores.      Tenths of, A candidate together with the decant sizes its product page offers., What one site had to say about one query, and how much to trust it.      Four st, SearchHit, SiteResult (+92 more)

### Community 5 - "Search Engine per Site"
Cohesion: 0.10
Nodes (29): _canonical(), _covers(), _ends_with(), _index_of(), _match_text(), product_label(), Perfume matching: brand and concentration are mandatory; fuzzy matching only app, Reduce a site's own title to the product it is about, spelled one way.      What (+21 more)

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
Cohesion: 0.09
Nodes (39): _check_empty_search(), _fetch_page(), _headers(), _is_excluded(), _paced_fetcher(), _page_offers_sizes(), _page_says_sold_out(), _parse_endpoint_document() (+31 more)

### Community 10 - "Basket Optimizer Core"
Cohesion: 0.15
Nodes (34): Collection, Prices, BasketItem, optimize(), Score one site against the basket, or against a subset of it.      `item_ids` is, Score every enabled site against the whole basket and sort the results.      Sit, Search for the cheapest way to split the basket across several sites.      Retur, One line of the shopping list: a basket row, not a unit count.      `item_id` is (+26 more)

### Community 11 - "Basket Store & Pricing"
Cohesion: 0.11
Nodes (26): conn(), Path, Tests for parfum_finder.store: the timestamp helper and the schema.  The one har, A snapshot pointing at a variant that doesn't exist has to be rejected.      SQL, Two snapshots written in the same second must resolve to the newer one.      A s, 5 ml at 125,00 TL is 25,00 TL per ml. Stored as kurus, ml as tenths., No price yet means no row, so the basket LEFT JOIN reads it as missing., A zero ml variant is a parse failure, and it must not reach the table.      If i (+18 more)

### Community 12 - "JSON-LD Product Extraction"
Cohesion: 0.13
Nodes (32): extract_jsonld_products(), Read every JSON-LD Product declared on the page, in document order.      A block, _one_product_html(), Tests for parfum_finder.extract.  Every case here is a shape a real store actual, Wrap a JSON-LD product body in a page, for the one-field-at-a-time cases., test_a_broken_block_does_not_lose_the_valid_one(), test_availability_spellings_all_land_in_the_same_bucket(), test_boolean_values_are_never_read_as_price_or_text() (+24 more)

### Community 13 - "Basket TUI Screen"
Cohesion: 0.13
Nodes (9): _Change, BasketReport, Every site's single-site scenario, split by whether it covers everything.      A, BasketScreen, Any, Path, The basket: the list on top, one scenario per site underneath., The three inputs basket.py's pure functions score: items, prices, shipping. (+1 more)

### Community 14 - "Platform Schema"
Cohesion: 0.06
Nodes (31): any, defaults, fingerprint, additionalProperties, items, minItems, type, description (+23 more)

### Community 15 - "Product Extraction"
Cohesion: 0.11
Nodes (30): _as_str(), _build_offer(), _build_product(), _coerce_in_stock(), _collect_offers(), _collect_products(), _collect_variants(), _css_variant() (+22 more)

### Community 16 - "Schema Field Patterns"
Cohesion: 0.05
Nodes (39): css, embedded_json, endpoint, jsonld, format, pattern, type, pattern (+31 more)

### Community 17 - "Offline Profile Validation"
Cohesion: 0.13
Nodes (18): Fetcher, Protocol, Anything that can stand in for `fetch`.      Offline profile validation runs the, Check, _first_result_url(), _no_results_check(), _probe_layer(), _probe_other_layers() (+10 more)

### Community 18 - "Playwright Errors"
Cohesion: 0.15
Nodes (21): _attempt(), _count_jsonld(), _count_product_objects(), _detect_platforms(), format_report(), _label_platform(), _one_line(), ProbeAttempt (+13 more)

### Community 19 - "Search TUI Screen"
Cohesion: 0.15
Nodes (5): HeaderSelected, RowSelected, The initial screen: search bar, streaming results table, notices, footer., What each site charges for the product a block is about.          One entry per, SearchScreen

### Community 20 - "Snapshot Writing"
Cohesion: 0.15
Nodes (27): Match, match_title(), PerfumeQuery, The perfume being looked for, split into its three identity parts.      `concent, One site title judged against the query.      `concentration` is what the title, Judge one site title against a query, or None if it is not that perfume.      No, test_a_brand_needs_all_of_its_words_not_one(), test_a_brand_only_query_matches_a_title_that_is_only_that_brand() (+19 more)

### Community 21 - "Candidate Filtering"
Cohesion: 0.19
Nodes (22): format_report(), Check one site's profile against that site's saved fixtures.      Never raises f, Render the validations as the offline half of the report in APP_FLOW §6.      A, validate_offline(), _corrupted_sites_dir(), _iso_days_ago(), Any, Path (+14 more)

### Community 22 - "Basket Site Scenarios"
Cohesion: 0.15
Nodes (19): basket_sites(), BasketLine, BasketPrice, BasketSite, One row of the basket: a size of a perfume, with the identity spelled out., One site's latest price for one basket line, only when it has one.      Rows wit, A site the basket screen is willing to show a column for.      Deliberately just, Return every enabled site, for the basket screen's fixed set of columns.      So (+11 more)

### Community 23 - "Price/Size Normalization"
Cohesion: 0.17
Nodes (19): _classify_single_separator(), format_ml(), _parse_number(), parse_price(), parse_size_ml(), Decimal, Number parsing and formatting for prices and volumes, plus text folding.  This i, Decide whether a lone separator marks a fraction or a thousands group.      Retu (+11 more)

### Community 24 - "JSON Schema Primitives"
Cohesion: 0.11
Nodes (25): integer, null, string, properties, type, type, type, type (+17 more)

### Community 25 - "SQLite Store"
Cohesion: 0.15
Nodes (20): _close_browser(), _fetch_curl_cffi(), _fetch_httpx(), _fetch_playwright(), _launch_browser(), PlaywrightNoResponse, Any, FormData (+12 more)

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
Cohesion: 0.08
Nodes (46): _choose_strategy(), collect_prices(), DiscoveryReport, FieldConfidence, _flatten_defaults(), _format_choice(), _format_confidence(), _format_defaults() (+38 more)

### Community 31 - "Live Profile Validation"
Cohesion: 0.14
Nodes (21): _age_of(), live_query(), _path(), profile_age_days(), datetime, Profile staleness checks. Two modes: offline (against saved fixtures) and live (, A URL's path with no trailing slash, for comparing two spellings of one page., Every site that has a profile, sorted so reports read the same way twice. (+13 more)

### Community 32 - "Variant Extraction Fields"
Cohesion: 0.12
Nodes (16): attribute, script, type, additionalProperties, allOf, description, properties, type (+8 more)

### Community 33 - "Variant Extraction Ladder"
Cohesion: 0.15
Nodes (8): Changed, Any, CacheKey, CandidateFilter, VariantsRead, One perfume of a search, as typed and as parsed.      The index is the outermost, Scan one site for every perfume of this search, one at a time.          Serial i, _Search

### Community 34 - "Fetch Strategy Probing"
Cohesion: 0.21
Nodes (15): probe(), Fetch `url` with every strategy and report diagnostics for each.      timeout_s, MonkeyPatch, Tests for parfum_finder.probe.  probe() always tries all three strategies -- the, test_probe_counts_jsonld_product_and_platform_signature(), test_probe_counts_product_across_jsonld_root_shapes(), test_probe_counts_product_markup_without_any_jsonld(), test_probe_counts_products_nested_below_the_top_level() (+7 more)

### Community 35 - "Platform Field Mapping"
Cohesion: 0.18
Nodes (11): field_map, product_json, source, variants_path, required, additionalProperties, allOf, description (+3 more)

### Community 36 - "Shipping Config Schema"
Cohesion: 0.14
Nodes (14): free_shipping_threshold_kurus, shipping_cost_kurus, minimum, type, free_shipping_threshold_kurus, notes, shipping, shipping_cost_kurus (+6 more)

### Community 37 - "Discovery Report Model"
Cohesion: 0.50
Nodes (3): The template this site's profile would be based on, if any., Which of the matching templates gets applied, or None for none of them.      One, _resolve_platform()

### Community 38 - "TUI Confirm Dialog"
Cohesion: 0.11
Nodes (35): Connection, A shop's imitation must not be stored as the perfume it imitates.      The clone, The drop happens here so no caller can forget it.      Both the CLI and the scre, One call has to leave a row the search table can read straight off.      The cal, The old price has to survive, and it must not become a second variant.      Appe, first_seen is what says how long a shop has carried a size., The title and URL are information, not identity.      A shop that rewords a list, EDT and EDP are different products at different prices.      Folding them into o (+27 more)

### Community 39 - "TUI App Shell"
Cohesion: 0.11
Nodes (17): Screen, SQLite persistence: an append-only price history.  Tables: sites, perfumes, prod, One priced size of one perfume on one site, ready to be written.      The perfum, Write a whole scan at once and return how many prices were recorded.      Every, SnapshotRow, write_snapshots(), ParfumFinderApp, Path (+9 more)

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
Cohesion: 0.09
Nodes (29): ExtractionFailed, RuntimeError, A page answered but gave up nothing, where something was expected.      This is, Run one query against one site and read every hit's sizes.      Everything site-, Give a size the listing's title and URL when the page gave it none.      A site, search_site(), _with_candidate_identity(), test_a_full_bottle_next_to_a_decant_does_not_sink_the_site() (+21 more)

### Community 44 - "Decant Variant Rules"
Cohesion: 0.29
Nodes (7): items, type, type, items, type, exclude_keywords, needs_review

### Community 45 - "Multi-Site Search Run"
Cohesion: 0.15
Nodes (15): _listing_filter(), Any, CandidateFilter, Connection, Command-line entry point.  Subcommands will be added incrementally as the projec, Scan every perfume against every site and print each site as it lands.      One, Decide, from a search result's own title, whether to open its page., Write one site's rows in a transaction of its own.      Per site rather than per (+7 more)

### Community 46 - "Offline Validation Fixtures"
Cohesion: 0.15
Nodes (18): extract_embedded_variants(), extract_jsonld_variants(), _flatten_jsonld(), Rung 1: read the page's JSON-LD as flat variant rows.      A product that declar, Turn one Product and everything under it into rows., Rung 3: read the JSON blob the page carries but does not display.      Two shape, _fixture(), Read a captured product page. (+10 more)

### Community 47 - "Basket Domain Logic"
Cohesion: 0.13
Nodes (29): Run one site and classify what came back instead of raising.      It is also whe, run_site(), FetchResult, One fetched page, uniform regardless of which strategy produced it., _counting_fetcher(), _profile(), Exception, Answer each call with the next canned result, then repeat the last one. (+21 more)

### Community 48 - "Search Screen Rows"
Cohesion: 0.20
Nodes (6): Decimal, Row, One priced size, exactly as the table shows it and as a keypress needs it., The default order: typed order, product, site, size.          The typed order co, The order once a column has been picked: the site layer drops out.          Aski, _ResultRow

### Community 49 - "test_engine.py"
Cohesion: 0.17
Nodes (25): apply_variant_rules(), Turn raw size rows into decant variants, dropping what is not a decant.      Thr, _named_profile(), Any, Tests for the profile-driven search in parfum_finder.engine.  What these defend, The real fetcher, with a list of every URL it was asked for., A profile whose search page lists two houses' bottles, as shops do., _row() (+17 more)

### Community 50 - "Profile Age Checks"
Cohesion: 0.22
Nodes (15): Run one site's profile against the real site.      Same contract as offline mode, validate_live(), _DeadSite, _FakeSite, _fixture_site(), M5's own criterion: when a profile stops agreeing with its site's real markup, o, A stand-in for one live site, answering the search page then the rest.      Live, A host that cannot be reached at all. (+7 more)

### Community 51 - "extract_endpoint_variants"
Cohesion: 0.18
Nodes (14): HTMLParser, _check_variant_control(), Fail when the page's size picker offers more sizes than the layer read.      The, extract_css_variants(), Rung 4: read the rendered markup with selectors. Last resort.      `config["vari, One buyable size of one product, exactly as the page or feed states it.      Thi, RawVariant, _count_result_cards() (+6 more)

### Community 52 - "Snapshot Row Semantics"
Cohesion: 0.40
Nodes (3): ComposeResult, ComposeResult, Static

### Community 53 - "conftest.py"
Cohesion: 0.17
Nodes (18): add_basket_item(), now_iso(), _perfume_id(), _product_id(), Connection, Return the current UTC time as 'YYYY-MM-DDTHH:MM:SSZ'.      Every timestamp writ, Write one scan's reading of one size, and return its snapshot id.      The perfu, Do the writing, without opening a transaction of its own. (+10 more)

### Community 54 - "Endpoint Schema Fields"
Cohesion: 0.22
Nodes (9): result_item, result_title, result_url, url_template, search, additionalProperties, description, required (+1 more)

### Community 55 - "ConfirmScreen"
Cohesion: 0.18
Nodes (4): Pressed, ConfirmScreen, Path, Asks before a low-confidence match is written to the basket.      The two answer

### Community 56 - "Request Schema Fields"
Cohesion: 0.25
Nodes (8): type, additionalProperties, type, body, request_headers, additionalProperties, description, type

### Community 57 - "_FixtureFetcher"
Cohesion: 0.26
Nodes (7): _FixtureFetcher, FormData, Headers, Method, Strategy, Serves one site's saved capture in place of the network.      Only three kinds o, The one real result card that led to the captured product page.          Cut out

### Community 58 - "Snapshot Row Building"
Cohesion: 0.17
Nodes (12): One site's share of a split basket: what to buy there and what it costs.      `s, SplitLeg, format_price(), Format a price for display (comma-thousands, dot-decimal).      Decimal('1250'), format_age(), _leg_block(), Turn a price age in days into the words the age column shows., One site's share of a split: its assigned items, then its own subtotal.      A s (+4 more)

### Community 59 - "_named_profile"
Cohesion: 0.17
Nodes (12): _candidates_to_open(), CacheKey, CandidateFilter, Path, Run every site against one query, all at once, and report each separately., Narrow the search results down to the pages worth a request.      The first one, run_sites(), test_a_dead_site_does_not_take_the_others_down() (+4 more)

### Community 60 - "Fetch Strategy Selection"
Cohesion: 0.33
Nodes (10): Path, Attach the rotating file handler and return where it writes.      Safe to call m, setup_logging(), Path, The file logger's two promises: it writes to the file, and it stays silent.  Bot, _teardown(), test_an_error_lands_in_the_given_file(), test_setting_up_twice_does_not_double_the_lines() (+2 more)

### Community 61 - "Price History"
Cohesion: 0.29
Nodes (7): price_history(), Row, Return one variant's past readings, newest first, capped at limit.      Empty fo, No history yet is a normal state for a variant, not an error to raise on., The identity a real scan writes must be the identity these lookups accept., test_a_scanned_perfume_can_be_read_back_by_basket_and_history(), test_price_history_is_empty_for_an_unknown_variant()

### Community 62 - "Extraction Layer Enum"
Cohesion: 0.25
Nodes (7): _age_line(), format_live_report(), Every check run against one site's profile, in the order they ran.      Checks s, Whether the profile is old enough to be worth re-discovering., The age note for one site, or None when its age is unremarkable.      A profile, Render offline and live results side by side, as APP_FLOW §6 shows them.      Bo, SiteValidation

### Community 63 - "run_sites"
Cohesion: 0.31
Nodes (11): Path, Give the test profile's site id a hook file. The id is what binds them., test_a_before_search_that_returns_no_query_is_refused(), test_a_broken_hook_is_an_error_not_a_silent_empty(), test_a_hook_that_reads_nothing_is_named_as_the_culprit(), test_a_site_with_no_hook_file_is_driven_by_its_profile_alone(), test_after_search_can_drop_a_result_the_selectors_could_not(), test_before_search_rewrites_the_query_that_is_actually_sent() (+3 more)

### Community 64 - "validate_live"
Cohesion: 0.31
Nodes (9): _parse_selector(), Node, Run one "<css>::text" / "<css>::attr(name)" selector inside a node.      The nod, Run one "<css>::text" / "<css>::attr(name)" selector, reading every match., Split a "<css>::text" / "<css>::attr(name)" selector into its two parts., Read the attribute or text of one already-selected node, or None., _read_selected(), select_all() (+1 more)

### Community 65 - ".__call__"
Cohesion: 0.25
Nodes (7): _ClimbState, Basket scenario evaluation. A pure function, no network access, no sqlite.  Inpu, The cheapest basket split the search found. A heuristic, not a proof.      Every, The hill-climb's working assignment plus the running per-site figures.      `sub, One site's shipping terms, read once and reused for every scenario.      `free_s, ShippingConfig, SplitPlan

### Community 66 - "extract_endpoint_variants"
Cohesion: 0.14
Nodes (15): _balanced_value(), _embedded_documents(), extract_endpoint_variants(), _loads_or_skip(), Any, Rung 2: read the variant list out of a platform's JSON response.      `document`, Yield every JSON document the page hides, in document order., Parse `text` as JSON, yielding nothing when it isn't JSON.      Pages are full o (+7 more)

### Community 67 - "field_map"
Cohesion: 0.29
Nodes (7): in_stock, price, size_raw, additionalProperties, required, type, field_map

### Community 68 - "basket_lines"
Cohesion: 0.25
Nodes (8): basket_lines(), Return every basket line, oldest add first.      Ordered by added_at with basket, The basket screen prints brand/name/concentration straight off this row.      Or, Two lines added within the same second must still read back the same way twice., A basket line nobody sells must still be visible via basket_lines.      basket_p, test_basket_lines_breaks_a_same_second_tie_by_basket_item_id(), test_basket_lines_orders_by_added_at_and_carries_the_perfume_identity(), test_basket_prices_has_no_row_for_a_line_no_site_prices()

### Community 71 - "basket_prices"
Cohesion: 0.25
Nodes (8): basket_prices(), Return the basket price matrix: one row per (line, site) that has a price., A stale reading must never outrank the one taken after it.      latest_prices al, A 10 ml listing must never fill a basket line asking for 5 ml.      The matrix j, Whether an out-of-stock price counts as missing is the caller's call.      Dropp, test_basket_prices_joins_on_the_exact_integer_size(), test_basket_prices_keeps_out_of_stock_rows_with_in_stock_false(), test_basket_prices_reports_only_the_latest_snapshot()

### Community 72 - "_NoRootParser"
Cohesion: 0.29
Nodes (7): _NoRootParser, MonkeyPatch, Record every delay the engine asks for instead of serving it.      Waiting for r, Stands in for HTMLParser when a page's markup cannot be read at all.      select, slept(), test_a_product_page_with_no_root_names_its_body_size(), test_a_search_page_with_no_root_names_its_body_size()

### Community 73 - "_trial"
Cohesion: 0.38
Nodes (7): _match_platforms(), Any, Path, Every template with at least one of its markers somewhere in the page.      Case, Write one page and return where it landed plus its digest.      Saved as UTF-8 w, _save_fixture(), _trial()

### Community 75 - "set_basket_qty"
Cohesion: 0.33
Nodes (6): Set a basket line's quantity, clamped to at least 1, and return it.      The tab, set_basket_qty(), An update aimed at a row that isn't there means the caller is out of sync., The table's CHECK (qty > 0) would reject a bare 0, and the '-' key has to     su, test_set_basket_qty_clamps_zero_and_negatives_to_one(), test_set_basket_qty_on_an_unknown_id_raises()

### Community 76 - ".__call__"
Cohesion: 0.53
Nodes (4): FormData, Headers, Method, Strategy

### Community 77 - "SiteScenario"
Cohesion: 0.40
Nodes (4): What it would cost to buy some or all of the basket from one site.      `covered, SiteScenario, The two or three lines one site's scenario takes up on screen., _scenario_block()

## Knowledge Gaps
- **154 isolated node(s):** `parfum-finder`, `$schema`, `$id`, `title`, `description` (+149 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **5 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `SiteResult` connect `Search/Basket Domain Models` to `TUI App & Screens`, `Variant Extraction Ladder`, `HTTP/Browser Fetching`, `TUI Confirm Dialog`, `TUI App Shell`, `Search Engine Core`, `Multi-Site Search Run`, `Basket TUI Screen`, `Basket Domain Logic`, `Search Screen Rows`, `Offline Profile Validation`, `extract_endpoint_variants`, `Search TUI Screen`, `Basket Site Scenarios`, `ConfirmScreen`, `_named_profile`, `Price History`?**
  _High betweenness centrality (0.042) - this node is a cross-community bridge._
- **Why does `BasketScreen` connect `Basket TUI Screen` to `TUI App & Screens`, `.__call__`, `Variant Extraction Ladder`, `Search/Basket Domain Models`, `TUI App Shell`, `Basket Optimizer Core`, `SiteScenario`, `Search Screen Rows`, `Search TUI Screen`, `Snapshot Writing`, `Snapshot Row Semantics`, `Basket Site Scenarios`, `ConfirmScreen`, `Snapshot Row Building`?**
  _High betweenness centrality (0.040) - this node is a cross-community bridge._
- **Why does `parse_query()` connect `Title Matcher` to `Search Engine per Site`, `TUI Confirm Dialog`, `TUI App Shell`, `CLI Entry Points`, `._start_search`, `Multi-Site Search Run`, `test_engine.py`, `Snapshot Writing`, `Price History`?**
  _High betweenness centrality (0.036) - this node is a cross-community bridge._
- **Are the 7 inferred relationships involving `SearchScreen` (e.g. with `ParfumFinderApp` and `SiteResult`) actually correct?**
  _`SearchScreen` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Are the 16 inferred relationships involving `SiteResult` (e.g. with `RawVariant` and `Fetcher`) actually correct?**
  _`SiteResult` has 16 INFERRED edges - model-reasoned connections that need verification._
- **What connects `parfum-finder`, `$schema`, `$id` to the rest of the system?**
  _154 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `TUI App & Screens` be split into smaller, more focused modules?**
  _Cohesion score 0.10536828963795256 - nodes in this community are weakly interconnected._