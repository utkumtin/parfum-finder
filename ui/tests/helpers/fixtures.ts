// Builders for the wire shapes, so a test states only the fields it is about.
//
// Every default here is a plausible reading, not a zero: a row with no price
// and no score would exercise the empty path in every test that forgot to fill
// it in, and the assertion would still pass.

import type {
  BasketResponse,
  BasketRow,
  BestCombination,
  ResultRow,
  SiteScenario,
} from "../../src/types";

export function resultRow(overrides: Partial<ResultRow> = {}): ResultRow {
  const size = overrides.size_ml_x10 ?? 50;
  const price = overrides.price_kurus ?? 25000;
  return {
    site_id: "site-a",
    site_label: "Site A",
    query_index: 0,
    product: "Dior Sauvage EDP",
    raw_title: "Dior Sauvage EDP Dekant 5 ml",
    size_ml_x10: size,
    price_kurus: price,
    // Kuruş per millilitre, the way ranking.py computes it: an exact ratio the
    // backend sends as a decimal string.
    price_per_ml_kurus: String(price / (size / 10)),
    in_stock: true,
    match_score: 95,
    confident: true,
    brand: "Dior",
    name: "Sauvage",
    concentration: "EDP",
    product_url: "https://example.com/p",
    clone_of: "",
    own_identity: true,
    age_days: 0,
    ...overrides,
  };
}

export function basketRow(overrides: Partial<BasketRow> = {}): BasketRow {
  return {
    basket_item_id: 1,
    brand: "Dior",
    name: "Sauvage",
    concentration: "EDP",
    size_ml_x10: 50,
    qty: 1,
    label: "Dior Sauvage EDP 5 ml",
    prices: { "site-a": 25000 },
    age_days: 0,
    ...overrides,
  };
}

export function scenario(overrides: Partial<SiteScenario> = {}): SiteScenario {
  const subtotal = overrides.subtotal_kurus ?? 25000;
  const shipping = overrides.shipping_kurus ?? 3000;
  return {
    site_id: "site-a",
    name: "Site A",
    subtotal_kurus: subtotal,
    shipping_kurus: shipping,
    total_kurus: subtotal + shipping,
    covered: 1,
    total_items: 1,
    missing: [],
    free_shipping_gap_kurus: null,
    free_shipping_met: false,
    notes: "",
    is_full: true,
    ...overrides,
  };
}

export function basket(
  rows: BasketRow[],
  overrides: Partial<BasketResponse> = {},
): BasketResponse {
  return {
    rows,
    report: { full: [], partial: [], unavailable: [] },
    best_combination: null,
    ...overrides,
  };
}

/** A two-shop split, the only shape that makes the combination card appear. */
export function splitCombination(
  legs: { scenario: SiteScenario; item_ids: number[] }[],
  overrides: Partial<BestCombination> = {},
): BestCombination {
  return {
    legs,
    total_kurus: legs.reduce((sum, leg) => sum + leg.scenario.total_kurus, 0),
    omitted_sites: [],
    best_full_site: null,
    diff_kurus: null,
    ...overrides,
  };
}
