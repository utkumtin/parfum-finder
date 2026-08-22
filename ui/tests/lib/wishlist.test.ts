import { describe, expect, it } from "vitest";
import { wishlistKey } from "../../src/lib/wishlist";

describe("wishlistKey", () => {
  it("does not collide when identity fields contain separators", () => {
    const first = wishlistKey({
      site_id: "site|a",
      brand: "brand",
      name: "name|EDP",
      concentration: "EDT",
      size_ml_x10: 50,
    });
    const second = wishlistKey({
      site_id: "site",
      brand: "a|brand",
      name: "name",
      concentration: "EDP|EDT",
      size_ml_x10: 50,
    });

    expect(first).not.toBe(second);
  });
});
