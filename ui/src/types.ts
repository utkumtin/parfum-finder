// The wire shapes, mirroring src/parfum_finder/api/serialize.py field for
// field. Money is always an integer of kuruş and volume an integer of tenths
// of a millilitre, exactly as the database stores them; only lib/format.ts
// turns either into something a person reads.

export type SiteStatus = "ok" | "empty" | "suspect" | "error";

export interface AppConfig {
  stale_price_days: number;
  max_queries: number;
  query_separator_pattern: string;
}

export interface SiteSummary {
  id: string;
  name: string;
  enabled: boolean;
  needs_review: boolean;
  discovered_at: string;
}

export interface ResultRow {
  site_id: string;
  site_label: string;
  query_index: number;
  product: string;
  raw_title: string;
  size_ml_x10: number;
  price_kurus: number | null;
  // A string because the backend computes it as an exact Decimal. Parse it for
  // display only: comparing two of these as floats is how a sort starts
  // disagreeing with the order the server actually sent.
  price_per_ml_kurus: string | null;
  in_stock: boolean | null;
  match_score: number;
  confident: boolean;
  brand: string;
  name: string;
  concentration: string;
  product_url: string | null;
  clone_of: string;
  own_identity: boolean;
  age_days: number;
}

export interface ResultsResponse {
  rows: ResultRow[];
  hidden_out_of_stock: number;
  finished: boolean;
}

export type ScanEvent =
  | { type: "scan_started"; total_sites: number; total_perfumes: number }
  | { type: "site_started"; site_id: string }
  | { type: "cache_hit"; query_index: number; age_days: number }
  | { type: "rows_ready"; rows: ResultRow[] }
  | {
      type: "site_finished";
      site_id: string;
      query_index: number;
      status: SiteStatus;
      detail: string | null;
      has_rows: boolean;
    }
  | { type: "write_failed"; site_id: string; query_index: number }
  | { type: "scan_finished"; error_count: number };

export type BasketRefreshEvent =
  | { type: "refresh_started"; total: number }
  | {
      type: "price_excluded";
      site_id: string;
      basket_item_id: number;
      notice: string | null;
    }
  | { type: "write_failed"; site_id: string; notice: string }
  | { type: "row_finished"; site_id: string; basket_item_id: number }
  | { type: "refresh_finished" };

export interface BasketRow {
  basket_item_id: number;
  brand: string;
  name: string;
  concentration: string;
  size_ml_x10: number;
  qty: number;
  label: string;
  // Unit price per site, only for the sites that can supply this line at all.
  prices: Record<string, number>;
  age_days: number | null;
}

export interface SiteScenario {
  site_id: string;
  name: string;
  subtotal_kurus: number;
  shipping_kurus: number;
  total_kurus: number;
  covered: number;
  total_items: number;
  missing: string[];
  free_shipping_gap_kurus: number | null;
  free_shipping_met: boolean;
  notes: string;
  is_full: boolean;
}

export interface BasketReport {
  full: SiteScenario[];
  partial: SiteScenario[];
  unavailable: string[];
}

export interface SplitLeg {
  scenario: SiteScenario;
  item_ids: number[];
}

// Named best_combination on the wire on purpose. It is a heuristic search's
// best find, never a proof that nothing cheaper exists, and the UI copy has to
// stay inside that claim.
export interface BestCombination {
  legs: SplitLeg[];
  total_kurus: number;
  omitted_sites: string[];
  best_full_site: SiteScenario | null;
  diff_kurus: number | null;
}

export interface BasketResponse {
  rows: BasketRow[];
  report: BasketReport;
  best_combination: BestCombination | null;
}

export interface AcceptedSearch {
  index: number;
  text: string;
}

export interface SearchStart {
  search_id: string;
  rejected: string[];
  // The only way to put a name to the query_index every scan event carries.
  searches: AcceptedSearch[];
}

export interface RecentSearch {
  // The whole line as it was typed, separators and all, so selecting one
  // replays the multi-perfume query rather than a single piece of it.
  text: string;
  searched_at: string;
}

export interface RefreshStart {
  refresh_id: string;
  total_rows: number;
}

export type SortKey = "ml" | "price" | "per_ml";
