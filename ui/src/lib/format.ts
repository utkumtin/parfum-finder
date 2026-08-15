// Display only. Every function here mirrors the one in
// src/parfum_finder/normalize.py that the TUI paints with, so the same reading
// reads the same way in both front ends.

/** Kuruş to lira, comma-grouped and dot-decimal: 125000 -> "1,250.00 ₺". */
export function formatPrice(kurus: number | null): string {
  if (kurus === null) return "—";
  return `${(kurus / 100).toLocaleString("en-US", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })} ₺`;
}

/** Tenths of a millilitre to millilitres: 50 -> "5 ml", 15 -> "1.5 ml". */
export function formatMl(sizeMlX10: number): string {
  const ml = sizeMlX10 / 10;
  return `${Number.isInteger(ml) ? ml : ml.toFixed(1)} ml`;
}

/**
 * Kuruş per millilitre, which arrives as a Decimal's string form.
 *
 * Parsed here and nowhere else: this number decides the default block order,
 * and the server already sorted by it exactly. Re-deriving it as a float on
 * this side would eventually disagree with the order on screen.
 */
export function formatPerMl(perMlKurus: string | null): string {
  if (perMlKurus === null) return "—";
  return `${(Number(perMlKurus) / 100).toLocaleString("en-US", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })} ₺/ml`;
}

/** How old a reading is, in the words the age column uses. */
export function formatAge(ageDays: number | null): string {
  if (ageDays === null) return "—";
  if (ageDays <= 0) return "bugün";
  if (ageDays < 7) return `${ageDays} gün önce`;
  return `${Math.floor(ageDays / 7)} hafta önce`;
}
