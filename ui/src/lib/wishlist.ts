import type { ResultRow } from "../types";

const STORAGE_KEY = "parfum-finder-wishlist";

export function wishlistKey(row: Pick<ResultRow, "site_id" | "brand" | "name" | "concentration" | "size_ml_x10">): string {
  return `${row.site_id}|${row.brand}|${row.name}|${row.concentration}|${row.size_ml_x10}`;
}

export function loadWishlist(): ResultRow[] {
  try {
    const stored = window.localStorage.getItem(STORAGE_KEY);
    if (stored === null) return [];
    const parsed: unknown = JSON.parse(stored);
    return Array.isArray(parsed) ? (parsed as ResultRow[]) : [];
  } catch {
    return [];
  }
}

export function saveWishlist(rows: ResultRow[]): void {
  window.localStorage.setItem(STORAGE_KEY, JSON.stringify(rows));
}
