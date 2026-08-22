import type { ResultRow } from "../types";

export type WishlistIdentity = Pick<
  ResultRow,
  "site_id" | "brand" | "name" | "concentration" | "size_ml_x10"
>;

export function wishlistIdentity(row: WishlistIdentity): WishlistIdentity {
  return {
    site_id: row.site_id,
    brand: row.brand,
    name: row.name,
    concentration: row.concentration,
    size_ml_x10: row.size_ml_x10,
  };
}

export function wishlistKey(row: WishlistIdentity): string {
  return JSON.stringify([
    row.site_id,
    row.brand,
    row.name,
    row.concentration,
    row.size_ml_x10,
  ]);
}
