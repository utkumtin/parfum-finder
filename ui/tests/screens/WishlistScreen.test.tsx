import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { WishlistScreen } from "../../src/screens/WishlistScreen";
import { resultRow } from "../helpers/fixtures";
import { DEFAULT_CONFIG, installFakeServer } from "../helpers/server";

beforeEach(() => {
  installFakeServer();
  window.__PARFUM_TOKEN__ = "test-token";
});

function titles(): string[] {
  return screen
    .getAllByRole("row")
    .slice(1)
    .map((row) => within(row).getAllByRole("cell")[0]?.textContent ?? "");
}

function renderScreen() {
  const expensiveSmall = resultRow({
    site_id: "site-a",
    raw_title: "Small",
    size_ml_x10: 10,
    price_kurus: 10_000,
    price_per_ml_kurus: "10000",
  });
  const cheapLarge = resultRow({
    site_id: "site-b",
    raw_title: "Large",
    size_ml_x10: 100,
    price_kurus: 20_000,
    price_per_ml_kurus: "2000",
  });
  const missing = resultRow({
    site_id: "site-c",
    raw_title: "Missing",
    price_kurus: null,
    price_per_ml_kurus: null,
  });
  render(
    <WishlistScreen
      rows={[missing, expensiveSmall, cheapLarge]}
      wishlistReady
      pendingWishlistKeys={new Set()}
      config={DEFAULT_CONFIG}
      notify={vi.fn()}
      onBasketChanged={vi.fn()}
      onWishlistToggle={vi.fn()}
    />,
  );
}

describe("WishlistScreen sorting", () => {
  it("sorts price ascending, puts missing prices last, then restores saved order", async () => {
    renderScreen();
    expect(titles()).toEqual(["Missing", "Small", "Large"]);

    const header = screen.getByRole("columnheader", { name: /Fiyat/ });
    await userEvent.click(header);
    expect(titles()).toEqual(["Small", "Large", "Missing"]);
    expect(header).toHaveAttribute("aria-sort", "ascending");

    await userEvent.click(header);
    expect(titles()).toEqual(["Missing", "Small", "Large"]);
    expect(header).toHaveAttribute("aria-sort", "none");
  });

  it("sorts exact price per ml ascending", async () => {
    renderScreen();

    await userEvent.click(screen.getByRole("columnheader", { name: /₺\/ml/ }));

    expect(titles()).toEqual(["Large", "Small", "Missing"]);
  });
});
