import { act, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { WishlistScreen } from "../../src/screens/WishlistScreen";
import { resultRow } from "../helpers/fixtures";
import { DEFAULT_CONFIG, installFakeServer, searchStart } from "../helpers/server";
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

afterEach(() => {
  vi.useRealTimers();
  document.documentElement.style.removeProperty("--acc-collapse");
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
      onWishlistChanged={vi.fn()}
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
      onWishlistChanged={vi.fn()}
      onWishlistToggle={vi.fn()}
    />,
  );
}

function renderLazyRows(rows: WishlistRow[]) {
  return render(
    <WishlistScreen
      rows={rows}
      wishlistReady
      pendingWishlistKeys={new Set()}
      config={DEFAULT_CONFIG}
      siteNames={SITE_NAMES}
      notify={vi.fn()}
      onBasketChanged={vi.fn()}
      onWishlistChanged={vi.fn()}
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

describe("WishlistScreen lazy shop prices accordion", () => {
  it("does not mount offer details until a row is opened", () => {
    renderLazyRows([
      wishlistRow({
        raw_title: "Amber Night 5 ml",
        prices: { "site-a": 20_000, "site-b": 18_000 },
      }),
    ]);

    const trigger = screen.getByRole("button", {
      name: "Amber Night 5 ml diğer mağaza fiyatları",
    });
    expect(trigger).toHaveAttribute("aria-expanded", "false");
    expect(trigger).not.toHaveAttribute("aria-controls");
    expect(document.querySelector('[role="region"][aria-label*="Amber Night"]')).not.toBeInTheDocument();
  });

  it("mounts and opens details together, then waits for the computed close transition", () => {
    vi.useFakeTimers();
    document.documentElement.style.setProperty("--acc-collapse", "100ms");
    renderLazyRows([
      wishlistRow({
        raw_title: "Amber Night 5 ml",
        prices: { "site-a": 20_000, "site-b": 18_000 },
      }),
    ]);

    const trigger = screen.getByRole("button", {
      name: "Amber Night 5 ml diğer mağaza fiyatları",
    });
    fireEvent.click(trigger);
    expect(trigger).toHaveAttribute("aria-expanded", "true");

    const region = screen.getByRole("region", { name: /Amber Night/ });
    expect(trigger).toHaveAttribute("aria-expanded", "true");
    expect(region.id).toBe(trigger.getAttribute("aria-controls"));

    fireEvent.click(trigger);
    expect(document.querySelector('[role="region"][aria-label*="Amber Night"]')).toBeInTheDocument();
    act(() => vi.advanceTimersByTime(131));
    expect(document.querySelector('[role="region"][aria-label*="Amber Night"]')).toBeInTheDocument();
    act(() => vi.advanceTimersByTime(1));
    expect(document.querySelector('[role="region"][aria-label*="Amber Night"]')).not.toBeInTheDocument();
  });

  it("uses the panel duration and delay when they are available", () => {
    vi.useFakeTimers();
    document.documentElement.style.setProperty("--acc-collapse", "900ms");
    renderLazyRows([wishlistRow({ raw_title: "Panel timing", prices: { "site-b": 18_000 } })]);

    const trigger = screen.getByRole("button", { name: /Panel timing diğer mağaza/ });
    fireEvent.click(trigger);
    const region = screen.getByRole("region", { name: /Panel timing/ });
    const panel = region.parentElement as HTMLElement;
    panel.style.transitionDuration = "100ms";
    panel.style.transitionDelay = "20ms";

    fireEvent.click(trigger);
    act(() => vi.advanceTimersByTime(151));
    expect(document.querySelector('[role="region"][aria-label*="Panel timing"]')).toBeInTheDocument();
    act(() => vi.advanceTimersByTime(1));
    expect(document.querySelector('[role="region"][aria-label*="Panel timing"]')).not.toBeInTheDocument();
  });

  it("ignores transition end and cancel events and invalidates a stale close timer on reopen", () => {
    vi.useFakeTimers();
    document.documentElement.style.setProperty("--acc-collapse", "100ms");
    renderLazyRows([wishlistRow({ raw_title: "Race row", prices: { "site-b": 18_000 } })]);

    const trigger = screen.getByRole("button", { name: /Race row diğer mağaza/ });
    fireEvent.click(trigger);
    fireEvent.click(trigger);
    const region = document.querySelector('[role="region"][aria-label*="Race row"]') as HTMLElement;
    region.dispatchEvent(new Event("transitionend", { bubbles: true }));
    region.dispatchEvent(new Event("transitioncancel", { bubbles: true }));
    expect(document.querySelector('[role="region"][aria-label*="Race row"]')).toBeInTheDocument();

    act(() => vi.advanceTimersByTime(100));
    fireEvent.click(trigger);
    expect(trigger).toHaveAttribute("aria-expanded", "true");
    act(() => vi.advanceTimersByTime(132));
    expect(screen.getByRole("region", { name: /Race row/ })).toBeInTheDocument();

    fireEvent.click(trigger);
    act(() => vi.advanceTimersByTime(132));
    expect(document.querySelector('[role="region"][aria-label*="Race row"]')).not.toBeInTheDocument();
  });

  it("guards stale callbacks against reopening and rows removed before cleanup", () => {
    vi.useFakeTimers();
    document.documentElement.style.setProperty("--acc-collapse", "100ms");
    const clearTimeoutSpy = vi
      .spyOn(window, "clearTimeout")
      .mockImplementation(() => {});
    const row = wishlistRow({ raw_title: "Guarded row", prices: { "site-b": 18_000 } });
    const view = renderLazyRows([row]);
    const trigger = screen.getByRole("button", { name: /Guarded row diğer mağaza/ });

    fireEvent.click(trigger);
    fireEvent.click(trigger);
    fireEvent.click(trigger);
    act(() => vi.advanceTimersByTime(132));
    expect(trigger).toHaveAttribute("aria-expanded", "true");
    expect(document.querySelector('[role="region"][aria-label*="Guarded row"]')).toBeInTheDocument();

    fireEvent.click(trigger);
    view.rerender(
      <WishlistScreen
        rows={[]}
        wishlistReady
        pendingWishlistKeys={new Set()}
        config={DEFAULT_CONFIG}
        siteNames={SITE_NAMES}
        notify={vi.fn()}
        onBasketChanged={vi.fn()}
        onWishlistChanged={vi.fn()}
        onWishlistToggle={vi.fn()}
      />,
    );
    act(() => vi.advanceTimersByTime(132));
    expect(document.querySelector('[role="region"][aria-label*="Guarded row"]')).not.toBeInTheDocument();
    clearTimeoutSpy.mockRestore();
  });

  it("keeps open state and panel ids through sorting and filtering", async () => {
    const first = wishlistRow({
      raw_title: "First row",
      price_kurus: 20_000,
      prices: { "site-b": 18_000 },
    });
    const second = wishlistRow({
      site_id: "site-b",
      raw_title: "Second row",
      price_kurus: 10_000,
      prices: { "site-a": 8_000 },
    });
    renderLazyRows([first, second]);

    fireEvent.click(screen.getByRole("button", { name: /First row diğer mağaza/ }));
    const firstPanelId = screen
      .getByRole("button", { name: /First row diğer mağaza/ })
      .getAttribute("aria-controls");
    await userEvent.click(screen.getByRole("columnheader", { name: /Fiyat/ }));
    const sortedTrigger = screen.getByRole("button", { name: /First row diğer mağaza/ });
    expect(sortedTrigger).toHaveAttribute("aria-expanded", "true");
    expect(sortedTrigger).toHaveAttribute("aria-controls", firstPanelId);

    const search = screen.getByRole("searchbox", { name: "İstek listesinde ara" });
    await userEvent.type(search, "second");
    expect(screen.queryByRole("button", { name: /First row diğer mağaza/ })).not.toBeInTheDocument();
    await userEvent.clear(search);
    expect(screen.getByRole("button", { name: /First row diğer mağaza/ })).toHaveAttribute(
      "aria-expanded",
      "true",
    );
  });

  it("cleans close timers when rows disappear or the screen unmounts", () => {
    vi.useFakeTimers();
    document.documentElement.style.setProperty("--acc-collapse", "100ms");
    const row = wishlistRow({ raw_title: "Temporary row", prices: { "site-b": 18_000 } });
    const view = renderLazyRows([row]);
    const trigger = screen.getByRole("button", { name: /Temporary row diğer mağaza/ });
    fireEvent.click(trigger);
    fireEvent.click(trigger);
    expect(vi.getTimerCount()).toBeGreaterThan(0);

    view.rerender(
      <WishlistScreen
        rows={[]}
        wishlistReady
        pendingWishlistKeys={new Set()}
        config={DEFAULT_CONFIG}
        siteNames={SITE_NAMES}
        notify={vi.fn()}
        onBasketChanged={vi.fn()}
        onWishlistChanged={vi.fn()}
        onWishlistToggle={vi.fn()}
      />,
    );
    expect(vi.getTimerCount()).toBe(0);

    view.unmount();
    expect(vi.getTimerCount()).toBe(0);
  });

  it("removes details on the next task when reduced motion is active", () => {
    vi.useFakeTimers();
    const previousMatchMedia = window.matchMedia;
    Object.defineProperty(window, "matchMedia", {
      configurable: true,
      writable: true,
      value: (query: string) =>
        ({
          matches: query.includes("prefers-reduced-motion"),
          media: query,
          onchange: null,
          addEventListener: () => {},
          removeEventListener: () => {},
          addListener: () => {},
          removeListener: () => {},
          dispatchEvent: () => false,
        }) as unknown as MediaQueryList,
    });
    renderLazyRows([wishlistRow({ raw_title: "Reduced row", prices: { "site-b": 18_000 } })]);

    const trigger = screen.getByRole("button", { name: /Reduced row diğer mağaza/ });
    fireEvent.click(trigger);
    fireEvent.click(trigger);
    expect(document.querySelector('[role="region"][aria-label*="Reduced row"]')).toBeInTheDocument();
    act(() => vi.runOnlyPendingTimers());
    expect(document.querySelector('[role="region"][aria-label*="Reduced row"]')).not.toBeInTheDocument();
    Object.defineProperty(window, "matchMedia", {
      configurable: true,
      writable: true,
      value: previousMatchMedia,
    });
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
        onWishlistChanged={vi.fn()}
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
        onWishlistChanged={vi.fn()}
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

  it("refreshes only the stale wishlist row selected by its arrow button", async () => {
    const server = installFakeServer();
    server.reply(
      "POST /api/wishlist/refresh",
      searchStart(["Dior Sauvage EDP"], { search_id: "wishlist-refresh-1" }),
    );
    const onWishlistChanged = vi.fn().mockResolvedValue(undefined);
    const row = wishlistRow({
      site_id: "site-a",
      raw_title: "Dior Sauvage EDP 5 ml",
      brand: "Dior",
      name: "Sauvage",
      concentration: "EDP",
      size_ml_x10: 50,
      age_days: DEFAULT_CONFIG.stale_price_days,
    });
    render(
      <WishlistScreen
        rows={[row]}
        wishlistReady
        pendingWishlistKeys={new Set()}
        config={DEFAULT_CONFIG}
        siteNames={SITE_NAMES}
        notify={vi.fn()}
        onBasketChanged={vi.fn()}
        onWishlistChanged={onWishlistChanged}
        onWishlistToggle={vi.fn()}
      />,
    );

    const refresh = screen.getByRole("button", {
      name: "Dior Sauvage EDP 5 ml fiyatları yenilensin",
    });
    expect(refresh).toBeEnabled();

    await userEvent.click(refresh);

    await waitFor(() =>
      expect(server.requestsTo("POST", "/api/wishlist/refresh")).toHaveLength(1),
    );
    expect(server.requestsTo("POST", "/api/wishlist/refresh")[0]?.body).toEqual({
      site_id: "site-a",
      brand: "Dior",
      name: "Sauvage",
      concentration: "EDP",
      size_ml_x10: 50,
    });
    expect(refresh).toBeDisabled();
    expect(refresh).toHaveClass("spinning");

    const socket = await server.socket("/api/search/wishlist-refresh-1");
    socket.emit({ type: "scan_finished", error_count: 0 });

    await waitFor(() => expect(onWishlistChanged).toHaveBeenCalledOnce());
    await waitFor(() => expect(refresh).not.toHaveClass("spinning"));
    expect(refresh).toBeDisabled();
  });
});
