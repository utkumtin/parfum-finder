import type { ResultRow } from "../types";

export function basketKey(
  item: Pick<ResultRow, "brand" | "name" | "concentration" | "size_ml_x10">,
): string {
  return `${item.brand}|${item.name}|${item.concentration}|${item.size_ml_x10}`;
}
