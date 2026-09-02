import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { WishlistScreen } from "../../src/screens/WishlistScreen";
import { resultRow } from "../helpers/fixtures";
import { DEFAULT_CONFIG, installFakeServer } from "../helpers/server";
import type { ResultRow, WishlistRow } from "../../src/types";

const SITE_NAMES = {
  "site-a": "İnci Dekant",
  "site-b": "Beta Mağaza",
  "site-c": "Gamma Parfümeri",
};

beforeEach(() => {
  installFakeServer();
  window.__PARFUM_TOKEN__ = "test-token";
});

function titles(): string[] {
  return Array.from(document.querySelectorAll("[data-wishlist-summary]")).map(
    (row) => within(row as HTMLElement).getAllByRole("cell")[0]?.textContent ?? "",
  );
}

function wishlistRow(
  overrides: Partial<ResultRow> & { prices?: Record<string, number> } = {},
): WishlistRow {
  const { prices = {}, ...rowOverrides } = overrides;
  return { ...resultRow(rowOverrides), prices };
}

function renderScreen() {
  const expensiveSmall = wishlistRow({
    site_id: "site-a",
    raw_title: "Small",
    size_ml_x10: 10,
    price_kurus: 10_000,
    price_per_ml_kurus: "10000",
  });
  const cheapLarge = wishlistRow({
    site_id: "site-b",
    raw_title: "Large",
    size_ml_x10: 100,
    price_kurus: 20_000,
    price_per_ml_kurus: "2000",
  });
  const missing = wishlistRow({
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
      siteNames={SITE_NAMES}
      notify={vi.fn()}
      onBasketChanged={vi.fn()}
      onWishlistToggle={vi.fn()}
    />,
  );
}

function renderSearchRows() {
  render(
    <WishlistScreen
      rows={[
        wishlistRow({
          site_id: "site-a",
          site_label: "İnci Dekant",
          raw_title: "IŞIK Eau de Parfum",
        }),
        wishlistRow({
          site_id: "site-b",
          site_label: "Beta Mağaza",
          raw_title: "Sauvagé Elixir",
        }),
        wishlistRow({
          site_id: "site-c",
          site_label: "Gamma Parfümeri",
          raw_title: "Amber Night",
        }),
      ]}
      wishlistReady
      pendingWishlistKeys={new Set()}
      config={DEFAULT_CONFIG}
      siteNames={SITE_NAMES}
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

describe("WishlistScreen search", () => {
  it("filters visible product titles and shop names on each keystroke", async () => {
    renderSearchRows();
    const searchInput = screen.getByRole("searchbox", { name: "İstek listesinde ara" });

    await userEvent.type(searchInput, "amb");
    expect(titles()).toEqual(["Amber Night"]);
    expect(screen.getByText("1 / 3 ürün")).toBeInTheDocument();

    await userEvent.clear(searchInput);
    await userEvent.type(searchInput, "beta");
    expect(titles()).toEqual(["Sauvagé Elixir"]);
  });

  it("normalizes Turkish casing, diacritics, and whitespace-separated terms", async () => {
    renderSearchRows();
    const searchInput = screen.getByRole("searchbox", { name: "İstek listesinde ara" });

    await userEvent.type(searchInput, "  ışık   parfum  ");
    expect(titles()).toEqual(["IŞIK Eau de Parfum"]);

    await userEvent.clear(searchInput);
    await userEvent.type(searchInput, "sauvage");
    expect(titles()).toEqual(["Sauvagé Elixir"]);

    await userEvent.clear(searchInput);
    await userEvent.type(searchInput, "inci");
    expect(titles()).toEqual(["IŞIK Eau de Parfum"]);
  });

  it("shows a dedicated no-match state and clears back to a focused full list", async () => {
    renderSearchRows();
    const searchInput = screen.getByRole("searchbox", { name: "İstek listesinde ara" });

    await userEvent.type(searchInput, "bulunmayan");
    expect(screen.getByText("Aramanızla eşleşen ürün bulunamadı.")).toBeInTheDocument();
    expect(screen.queryByRole("table")).not.toBeInTheDocument();

    await userEvent.click(screen.getByRole("button", { name: "Aramayı temizle" }));
    expect(searchInput).toHaveValue("");
    expect(searchInput).toHaveFocus();
    expect(titles()).toEqual(["IŞIK Eau de Parfum", "Sauvagé Elixir", "Amber Night"]);
  });

  it("keeps the active sort when the wishlist is filtered", async () => {
    renderScreen();
    await userEvent.click(screen.getByRole("columnheader", { name: /Fiyat/ }));
    await userEvent.type(
      screen.getByRole("searchbox", { name: "İstek listesinde ara" }),
      "large",
    );

    expect(titles()).toEqual(["Large"]);
    expect(screen.getByRole("columnheader", { name: /Fiyat/ })).toHaveAttribute(
      "aria-sort",
      "ascending",
    );
  });
});

describe("WishlistScreen shop prices accordion", () => {
  it("keeps multiple rows open and closes only the row clicked again", async () => {
    render(
      <WishlistScreen
        rows={[
          wishlistRow({
            site_id: "site-a",
            raw_title: "Amber Night 5 ml",
            prices: { "site-a": 20_000, "site-b": 18_000 },
          }),
          wishlistRow({
            site_id: "site-b",
            raw_title: "IŞIK 5 ml",
            prices: { "site-a": 24_000, "site-b": 21_000, "site-c": 23_000 },
          }),
        ]}
        wishlistReady
        pendingWishlistKeys={new Set()}
        config={DEFAULT_CONFIG}
        siteNames={SITE_NAMES}
        notify={vi.fn()}
        onBasketChanged={vi.fn()}
        onWishlistToggle={vi.fn()}
      />,
    );

    const amber = screen.getByRole("button", {
      name: "Amber Night 5 ml diğer mağaza fiyatları",
    });
    const light = screen.getByRole("button", {
      name: "IŞIK 5 ml diğer mağaza fiyatları",
    });

    await userEvent.click(amber);
    expect(amber).toHaveAttribute("aria-expanded", "true");
    const amberOffers = screen.getByRole("region", { name: /Amber Night/ });
    expect(amberOffers).toHaveTextContent("Beta Mağaza5 ml180.00 ₺");
    expect(amberOffers.querySelector("li .wishlist-offer-ml")).toHaveTextContent("5 ml");
    expect(amberOffers.querySelector("li .wishlist-offer-price")).toHaveTextContent("180.00 ₺");

    await userEvent.click(light);
    expect(amber).toHaveAttribute("aria-expanded", "true");
    expect(light).toHaveAttribute("aria-expanded", "true");
    expect(
      screen.getAllByRole("region", { name: /diğer mağaza fiyatları/ }),
    ).toHaveLength(2);

    await userEvent.click(amber);
    expect(amber).toHaveAttribute("aria-expanded", "false");
    expect(light).toHaveAttribute("aria-expanded", "true");
    expect(
      screen.getAllByRole("region", { name: /diğer mağaza fiyatları/ }),
    ).toHaveLength(1);
  });

  it("keeps row actions from changing the accordion state", async () => {
    const onWishlistToggle = vi.fn();
    render(
      <WishlistScreen
        rows={[wishlistRow({ raw_title: "Amber Night 5 ml" })]}
        wishlistReady
        pendingWishlistKeys={new Set()}
        config={DEFAULT_CONFIG}
        siteNames={SITE_NAMES}
        notify={vi.fn()}
        onBasketChanged={vi.fn()}
        onWishlistToggle={onWishlistToggle}
      />,
    );

    const trigger = screen.getByRole("button", {
      name: "Amber Night 5 ml diğer mağaza fiyatları",
    });
    await userEvent.click(screen.getByRole("button", { name: "İstek listesinden çıkar" }));

    expect(onWishlistToggle).toHaveBeenCalledOnce();
    expect(trigger).toHaveAttribute("aria-expanded", "false");
  });
});
