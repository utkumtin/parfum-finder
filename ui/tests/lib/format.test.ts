// These four functions are the frontend's half of a contract with
// src/parfum_finder/normalize.py: the same reading has to read the same way in
// the TUI and in the window. Each case below is a rule from that contract, not
// a snapshot of what the code currently returns.

import { describe, expect, it } from "vitest";
import {
  formatAge,
  formatMl,
  formatPerMl,
  formatPrice,
  formatPriceWhole,
} from "../../src/lib/format";

describe("formatPrice", () => {
  it("groups thousands with commas and keeps two decimals", () => {
    // The canonical output format TECH_STACK.md fixes: comma thousands, dot
    // decimal. A Turkish-locale rendering would say "1.250,00" and read as a
    // number a thousand times smaller to anyone reading it as canonical.
    expect(formatPrice(125000)).toBe("1,250.00 ₺");
  });

  it("keeps the kuruş even when they are zero", () => {
    expect(formatPrice(25000)).toBe("250.00 ₺");
  });

  it("shows a dash for a size that has no price", () => {
    // Not "0.00 ₺": a sold-out size has no price at all, and a zero would read
    // as free.
    expect(formatPrice(null)).toBe("—");
  });
});

describe("formatPriceWhole", () => {
  it("rounds to the nearest lira rather than truncating", () => {
    // Truncating would put a cell further from the real price than it has to
    // be, in the one place on the screen where columns are compared by eye.
    expect(formatPriceWhole(125060)).toBe("1,251 ₺");
    expect(formatPriceWhole(125040)).toBe("1,250 ₺");
  });

  it("shows a dash for a line no shop prices", () => {
    expect(formatPriceWhole(null)).toBe("—");
  });
});

describe("formatMl", () => {
  it("drops the decimal on a whole millilitre", () => {
    expect(formatMl(50)).toBe("5 ml");
  });

  it("keeps one decimal on a half millilitre", () => {
    // The sizes shops actually sell include 1.5 ml, and "2 ml" would be a
    // different product.
    expect(formatMl(15)).toBe("1.5 ml");
  });
});

describe("formatPerMl", () => {
  it("reads the exact decimal string the backend sent", () => {
    // Arrives as a string because ranking.py computed it as a Decimal. Parsing
    // it here is display only, which is why nothing re-derives it from price
    // and size.
    expect(formatPerMl("5000")).toBe("50.00 ₺/ml");
  });

  it("shows a dash when the rate could not be computed", () => {
    expect(formatPerMl(null)).toBe("—");
  });
});

describe("formatAge", () => {
  it("calls today's reading today rather than zero days", () => {
    expect(formatAge(0)).toBe("bugün");
  });

  it("counts in days inside the first week", () => {
    expect(formatAge(6)).toBe("6 gün önce");
  });

  it("switches to whole weeks from seven days on", () => {
    // The age column has one narrow line; "21 gün önce" and "3 hafta önce" are
    // the same fact, and the shorter one is the one that fits.
    expect(formatAge(7)).toBe("1 hafta önce");
    expect(formatAge(20)).toBe("2 hafta önce");
  });

  it("shows a dash when nothing has ever been read", () => {
    expect(formatAge(null)).toBe("—");
  });
});
