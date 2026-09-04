// The screen a purchase is decided on. Its two claims are the cheapest cell in
// each row and the totals under the columns, and both are arithmetic a shopper
// checks by eye -- a wrong one is a wrong order.

import { act, render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { BasketScreen } from "../../src/screens/BasketScreen";
import {
  ensureBasket,
  refreshBasket,
  resetBasketStoreForTests,
} from "../../src/lib/basketStore";
import type { BasketResponse } from "../../src/types";
import { basket, basketRow, scenario, splitCombination } from "../helpers/fixtures";
import {
  DEFAULT_CONFIG,
  installFakeServer,
  type FakeServer,
} from "../helpers/server";

let server: FakeServer;

const SITE_NAMES = { "site-a": "Site A", "site-b": "Site B", "site-c": "Site C" };

beforeEach(() => {
  server = installFakeServer();
  resetBasketStoreForTests();
  window.__PARFUM_TOKEN__ = "test-token";
});

function renderScreen(data: BasketResponse) {
  const notify = vi.fn();
  server.on("GET /api/basket", () => ({ body: data }));
  render(
    <BasketScreen
      config={DEFAULT_CONFIG}
      siteNames={SITE_NAMES}
      notify={notify}
    />,
  );
  return { notify };
}

/** The cells of one matrix row, header cell first. */
function cellsOf(rowLabel: string | RegExp): HTMLElement[] {
  const row = screen.getByText(rowLabel).closest("tr");
  if (row === null) throw new Error("that line is not in the matrix");
  return within(row).getAllByRole("cell");
}

describe("BasketScreen matrix", () => {
  it("says the basket is empty rather than drawing an empty table", async () => {
    renderScreen(basket([]));
    expect(await screen.findByText("Sepet boş.")).toBeInTheDocument();
    expect(screen.queryByRole("table")).not.toBeInTheDocument();
  });

  it("shows cached rows immediately and refreshes them after remounting", async () => {
    let current = basket([basketRow({ brand: "Cached", name: "Perfume" })]);
    server.on("GET /api/basket", () => ({ body: current }));
    const first = render(
      <BasketScreen
        config={DEFAULT_CONFIG}
        siteNames={SITE_NAMES}
        notify={vi.fn()}
      />,
    );
    expect(await screen.findByText(/Cached Perfume/)).toBeInTheDocument();
    first.unmount();

    current = basket([basketRow({ brand: "Fresh", name: "Perfume" })]);
    render(
      <BasketScreen
        config={DEFAULT_CONFIG}
        siteNames={SITE_NAMES}
        notify={vi.fn()}
      />,
    );

    expect(screen.getByText(/Cached Perfume/)).toBeInTheDocument();
    expect(screen.queryByText("Sepet okunuyor…")).not.toBeInTheDocument();
    expect(await screen.findByText(/Fresh Perfume/)).toBeInTheDocument();
    expect(server.requestsTo("GET", "/api/basket")).toHaveLength(2);
  });

  it("gives a column only to shops that price at least one line", async () => {
    // A column of dashes costs the width the shops that do stock the line need.
    renderScreen(
      basket([
        basketRow({ prices: { "site-b": 26000 } }),
        basketRow({ basket_item_id: 2, prices: { "site-a": 24000 } }),
      ]),
    );

    await screen.findByRole("table");
    const headers = screen.getAllByRole("columnheader").map((h) => h.textContent);
    expect(headers).toContain("Site A");
    expect(headers).toContain("Site B");
    expect(headers).not.toContain("Site C");
    // Ordered by the name on screen, not by the id the prices arrived under.
    expect(headers.indexOf("Site A")).toBeLessThan(headers.indexOf("Site B"));
  });

  it("marks the cheapest shop for each line on its own", async () => {
    renderScreen(
      basket([
        basketRow({
          label: "Dior Sauvage EDP 5 ml",
          prices: { "site-a": 25000, "site-b": 22000 },
        }),
        basketRow({
          basket_item_id: 2,
          brand: "Creed",
          name: "Aventus",
          label: "Creed Aventus EDP 5 ml",
          prices: { "site-a": 30000, "site-b": 40000 },
        }),
      ]),
    );

    await screen.findByRole("table");
    // The mark is a pill drawn around the number, which is the "cheap" cell.
    const sauvage = cellsOf(/Dior Sauvage EDP · 5 ml/);
    expect(sauvage[2]).not.toHaveClass("cheap");
    expect(sauvage[3]).toHaveClass("cheap");

    const aventus = cellsOf(/Creed Aventus EDP · 5 ml/);
    expect(aventus[2]).toHaveClass("cheap");
    expect(aventus[3]).not.toHaveClass("cheap");
  });

  it("keeps a tie on the first column rather than picking one at random", async () => {
    // Two shops at the same price are the same answer; a mark that moved
    // between reloads would read as the price having changed.
    renderScreen(
      basket([basketRow({ prices: { "site-a": 25000, "site-b": 25000 } })]),
    );

    await screen.findByRole("table");
    const cells = cellsOf(/Dior Sauvage EDP · 5 ml/);
    expect(cells[2]).toHaveClass("cheap");
    expect(cells[3]).not.toHaveClass("cheap");
  });

  it("multiplies the column subtotals by the quantities", async () => {
    // The arithmetic of the cells directly above it. A total nobody can add up
    // by eye reads as a different number from the one the plan cards quote.
    renderScreen(
      basket([
        basketRow({ qty: 2, prices: { "site-a": 25000 } }),
        basketRow({ basket_item_id: 2, qty: 1, prices: { "site-a": 10000 } }),
      ]),
    );

    await screen.findByRole("table");
    const footer = screen.getByText("Ara toplam").closest("tr");
    expect(within(footer!).getByText("600 ₺")).toBeInTheDocument();
    expect(within(footer!).getByText("2/2 ürün")).toBeInTheDocument();
  });

  it("counts a line a shop cannot supply as uncovered, not as zero", async () => {
    renderScreen(
      basket([
        basketRow({ prices: { "site-a": 25000, "site-b": 26000 } }),
        basketRow({ basket_item_id: 2, prices: { "site-a": 10000 } }),
      ]),
    );

    await screen.findByRole("table");
    const footer = screen.getByText("Ara toplam").closest("tr");
    expect(within(footer!).getByText("1/2 ürün")).toBeInTheDocument();
    expect(within(footer!).getByText("2/2 ürün")).toBeInTheDocument();
  });

  it("badges a line whose stalest shop answered too long ago", async () => {
    renderScreen(basket([basketRow({ age_days: 20 })]));
    const badge = await screen.findByText("2 hafta önce güncellendi");
    expect(badge).toHaveClass("badge", "stale");
  });
});

describe("BasketScreen quantities", () => {
  it("steps a quantity up through the API", async () => {
    server.reply("PATCH /api/basket/items/1", { basket_item_id: 1, qty: 2 });
    renderScreen(basket([basketRow({ qty: 1 })]));

    await userEvent.click(await screen.findByLabelText("artır"));

    await waitFor(() =>
      expect(server.requestsTo("PATCH", "/api/basket/items/1")[0]?.body).toEqual({
        qty: 2,
      }),
    );
  });

  it("removes the line when the quantity would drop below one", async () => {
    // The row has no delete button of its own any more, so the step down from
    // 1 is the destructive press. Its label has to say so.
    server.on("DELETE /api/basket/items/1", () => ({ status: 204 }));
    let current = basket([basketRow({ qty: 1, label: "Dior Sauvage EDP 5 ml" })]);
    server.on("GET /api/basket", () => ({ body: current }));
    render(
      <BasketScreen
        config={DEFAULT_CONFIG}
        siteNames={SITE_NAMES}
        notify={vi.fn()}
      />,
    );

    const remove = await screen.findByLabelText("sepetten çıkar");
    current = basket([]);
    await userEvent.click(remove);

    await waitFor(() =>
      expect(server.requestsTo("DELETE", "/api/basket/items/1")).toHaveLength(1),
    );
    expect(
      await screen.findByText("Dior Sauvage EDP 5 ml sepetten çıkarıldı."),
    ).toBeInTheDocument();
  });

  it("puts a removed line back by adding the perfume again, already confirmed", async () => {
    // Adding it again rather than un-deleting it: the prices are stored against
    // the perfume and its size, not against the basket row, so the line comes
    // back with everything the table was showing. It was confirmed once
    // already, when it was first added, so it must not be asked about twice.
    server.on("DELETE /api/basket/items/1", () => ({ status: 204 }));
    server.reply("POST /api/basket/items", { basket_item_id: 9 });
    let current = basket([basketRow({ qty: 1 })]);
    server.on("GET /api/basket", () => ({ body: current }));
    render(
      <BasketScreen
        config={DEFAULT_CONFIG}
        siteNames={SITE_NAMES}
        notify={vi.fn()}
      />,
    );

    await userEvent.click(await screen.findByLabelText("sepetten çıkar"));
    current = basket([]);
    await userEvent.click(await screen.findByRole("button", { name: "Geri al" }));

    await waitFor(() =>
      expect(server.requestsTo("POST", "/api/basket/items")[0]?.body).toEqual({
        brand: "Dior",
        name: "Sauvage",
        concentration: "EDP",
        size_ml_x10: 50,
        qty: 1,
        own_identity: true,
        clone_of: "",
        confident: true,
        confirmed: true,
      }),
    );
  });

  it("reports a refused change instead of showing a quantity that was not saved", async () => {
    server.reply("PATCH /api/basket/items/1", { detail: "adet en az 1 olmalı" }, 422);
    const { notify } = renderScreen(basket([basketRow({ qty: 1 })]));

    await userEvent.click(await screen.findByLabelText("artır"));
    await waitFor(() => expect(notify).toHaveBeenCalledWith("adet en az 1 olmalı", "error"));
  });
});

describe("BasketScreen refresh", () => {
  it("invalidates an older basket read after the price refresh finishes", async () => {
    const initial = basket([basketRow({ prices: { "site-a": 25000 } })]);
    const latest = basket([basketRow({ prices: { "site-a": 19900 } })]);
    let requestCount = 0;
    let finishOlderRead!: () => void;
    const olderReadHeld = new Promise<void>((resolve) => {
      finishOlderRead = resolve;
    });
    server.on("GET /api/basket", async () => {
      requestCount += 1;
      if (requestCount === 2) await olderReadHeld;
      return { body: requestCount === 3 ? latest : initial };
    });
    server.reply("POST /api/basket/refresh", { refresh_id: "r1", total_rows: 1 });

    await ensureBasket();
    const olderRead = refreshBasket();
    await waitFor(() => expect(requestCount).toBe(2));
    render(
      <BasketScreen
        config={DEFAULT_CONFIG}
        siteNames={SITE_NAMES}
        notify={vi.fn()}
      />,
    );

    await userEvent.click(await screen.findByRole("button", { name: "Fiyatları yenile" }));
    const socket = await server.socket("/api/basket/refresh/r1");
    act(() => socket.emit({ type: "refresh_finished" }));
    finishOlderRead();

    await expect(olderRead).rejects.toThrow("Obsolete basket response");
    await waitFor(() => expect(requestCount).toBe(3));
    await waitFor(() =>
      expect(cellsOf(/Dior Sauvage EDP · 5 ml/)[2]).toHaveTextContent("199 ₺"),
    );
  });

  it("re-reads the basket once the whole-basket refresh finishes", async () => {
    let prices = { "site-a": 25000 };
    server.on("GET /api/basket", () => ({
      body: basket([basketRow({ prices, age_days: 20 })]),
    }));
    server.reply("POST /api/basket/refresh", { refresh_id: "r1", total_rows: 1 });
    render(
      <BasketScreen
        config={DEFAULT_CONFIG}
        siteNames={SITE_NAMES}
        notify={vi.fn()}
      />,
    );

    await userEvent.click(await screen.findByRole("button", { name: "Fiyatları yenile" }));
    const socket = await server.socket("/api/basket/refresh/r1");
    expect(screen.getByRole("progressbar")).toBeInTheDocument();

    prices = { "site-a": 19900 };
    act(() => socket.emit({ type: "refresh_started", total: 1 }));
    act(() => socket.emit({ type: "row_finished", site_id: "site-a", basket_item_id: 1 }));
    act(() => socket.emit({ type: "refresh_finished" }));

    // In the line's own cell, not just anywhere: the footer subtotal shows the
    // same number for a one-line basket, so an unscoped match would pass on a
    // screen where only the total updated.
    await waitFor(() =>
      expect(cellsOf(/Dior Sauvage EDP · 5 ml/)[2]).toHaveTextContent("199 ₺"),
    );
    expect(screen.queryByRole("progressbar")).not.toBeInTheDocument();
  });

  it("shows a shop's own explanation for dropping a price", async () => {
    server.reply("POST /api/basket/refresh", { refresh_id: "r1", total_rows: 1 });
    renderScreen(basket([basketRow({ age_days: 20 })]));

    await userEvent.click(await screen.findByRole("button", { name: "Fiyatları yenile" }));
    const socket = await server.socket("/api/basket/refresh/r1");

    act(() =>
      socket.emit({
        type: "price_excluded",
        site_id: "site-a",
        basket_item_id: 1,
        notice: "boy artık satılmıyor",
      }),
    );

    expect(
      await screen.findByText("Site A: boy artık satılmıyor"),
    ).toBeInTheDocument();
  });

  it("stays silent when a shop simply has nothing to say", async () => {
    // A null notice is the silent case on purpose: an empty answer is evidence
    // the shop stopped carrying the decant, not a failure to report.
    server.reply("POST /api/basket/refresh", { refresh_id: "r1", total_rows: 1 });
    renderScreen(basket([basketRow({ age_days: 20 })]));

    await userEvent.click(await screen.findByRole("button", { name: "Fiyatları yenile" }));
    const socket = await server.socket("/api/basket/refresh/r1");

    act(() =>
      socket.emit({
        type: "price_excluded",
        site_id: "site-a",
        basket_item_id: 1,
        notice: null,
      }),
    );

    expect(screen.queryByText(/Site A:/)).not.toBeInTheDocument();
  });

  it("refreshes one line without the bar across the window", async () => {
    // One row announces itself by spinning in its own cell. A bar across the
    // window for a single line reads as more work than it is.
    server.reply("POST /api/basket/refresh", { refresh_id: "r1", total_rows: 1 });
    renderScreen(basket([basketRow({ age_days: 20, label: "Dior Sauvage EDP 5 ml" })]));

    await userEvent.click(
      await screen.findByLabelText("Dior Sauvage EDP 5 ml fiyatları yenilensin"),
    );

    await waitFor(() =>
      expect(server.requestsTo("POST", "/api/basket/refresh")[0]?.body).toEqual({
        basket_item_id: 1,
      }),
    );
    await server.socket("/api/basket/refresh/r1");
    expect(screen.queryByRole("progressbar")).not.toBeInTheDocument();
  });

  it("stops offering a line that was just asked about", async () => {
    // A line whose stalest shop is unreachable never reports an age of zero no
    // matter how often it is refreshed, so age alone would leave its button
    // live for ever and the same question would be sent again and again.
    server.reply("POST /api/basket/refresh", { refresh_id: "r1", total_rows: 1 });
    renderScreen(basket([basketRow({ age_days: 20, label: "Dior Sauvage EDP 5 ml" })]));

    const button = await screen.findByLabelText(
      "Dior Sauvage EDP 5 ml fiyatları yenilensin",
    );
    await userEvent.click(button);
    const socket = await server.socket("/api/basket/refresh/r1");
    act(() => socket.emit({ type: "refresh_finished" }));

    await waitFor(() => expect(button).toBeDisabled());
    expect(button).toHaveAttribute("title", "Fiyatlar güncel");
  });

  it("offers no refresh for a line every shop answered today", async () => {
    renderScreen(basket([basketRow({ age_days: 0, label: "Dior Sauvage EDP 5 ml" })]));
    const button = await screen.findByLabelText(
      "Dior Sauvage EDP 5 ml fiyatları yenilensin",
    );
    expect(button).toBeDisabled();
  });

  it("keeps a cached empty basket visible with a stale retry after refresh fails", async () => {
    renderScreen(basket([]));
    expect(await screen.findByText("Sepet boş.")).toBeInTheDocument();
    server.on("GET /api/basket", () => ({
      status: 503,
      body: { detail: "sepet yenilenemedi" },
    }));

    await expect(refreshBasket()).rejects.toThrow("sepet yenilenemedi");
    expect(await screen.findByText(/Sepet güncellenemedi: sepet yenilenemedi/)).toBeInTheDocument();
    const retry = screen.getByRole("button", { name: "Tekrar dene" });

    server.on("GET /api/basket", () => ({ body: basket([]) }));
    await userEvent.click(retry);
    await waitFor(() =>
      expect(screen.queryByText(/Sepet güncellenemedi/)).not.toBeInTheDocument(),
    );
    expect(screen.getByText("Sepet boş.")).toBeInTheDocument();
  });

  it("clears the progress bar when the refresh socket is refused", async () => {
    // A refused socket never sends refresh_finished, so without this the bar
    // would sit there for good with nothing said.
    server.reply("POST /api/basket/refresh", { refresh_id: "r1", total_rows: 1 });
    const { notify } = renderScreen(basket([basketRow({ age_days: 20 })]));

    await userEvent.click(await screen.findByRole("button", { name: "Fiyatları yenile" }));
    const socket = await server.socket("/api/basket/refresh/r1");

    act(() => socket.refuse(4401));

    await waitFor(() =>
      expect(notify).toHaveBeenCalledWith(
        "Fiyat tazeleme başlamadı: kimlik doğrulaması reddedildi",
        "error",
      ),
    );
    expect(screen.queryByRole("progressbar")).not.toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Fiyatları yenile" })).toBeEnabled();
  });
});

describe("BasketScreen plans", () => {
  it("previews the assigned store cart from the combination card", async () => {
    // The combination is only actionable when every store name reveals the
    // items that belong in that store's cart, including the quantity and price.
    const user = userEvent.setup();
    renderScreen(
      basket(
        [
          basketRow({ prices: { "site-a": 25000 } }),
          basketRow({
            basket_item_id: 2,
            brand: "Creed",
            name: "Aventus",
            label: "Creed Aventus EDP 5 ml",
            qty: 2,
            prices: { "site-b": 10000 },
          }),
        ],
        {
          best_combination: splitCombination([
            { scenario: scenario({ site_id: "site-a", subtotal_kurus: 25000 }), item_ids: [1] },
            {
              scenario: scenario({ site_id: "site-b", subtotal_kurus: 20000, total_kurus: 30000 }),
              item_ids: [2],
            },
          ]),
        },
      ),
    );

    await user.click(await screen.findByRole("button", { name: "Site B" }));
    const dialog = screen.getByRole("dialog", { name: "Site B için sepet" });
    expect(within(dialog).getByText("Creed Aventus EDP 5 ml")).toBeInTheDocument();
    expect(within(dialog).getByText("× 2")).toBeInTheDocument();
    expect(within(dialog).getAllByText("200.00 ₺")).toHaveLength(2);
    expect(within(dialog).getByText("300.00 ₺")).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Sepet önizlemesini kapat" }));
    expect(dialog).toHaveClass("is-closing");
  });

  it("opens every product page assigned to the selected store", async () => {
    // A split plan is only actionable when the shopper can move from one leg
    // to every real product page in that shop without reconstructing the list.
    const user = userEvent.setup();
    const open = vi.spyOn(window, "open").mockImplementation(() => null);
    renderScreen(
      basket(
        [
          basketRow({
            product_urls: { "site-a": "https://site-a.example/sauvage" },
          }),
          basketRow({
            basket_item_id: 2,
            label: "Creed Aventus EDP 5 ml",
            prices: { "site-a": 21000 },
            product_urls: { "site-a": "https://site-a.example/aventus" },
          }),
          basketRow({
            basket_item_id: 3,
            label: "Le Labo Santal 33 EDP 5 ml",
            prices: { "site-b": 24000 },
            product_urls: { "site-b": "https://site-b.example/santal" },
          }),
        ],
        {
          best_combination: splitCombination([
            {
              scenario: scenario({ site_id: "site-a", covered: 2, total_items: 3 }),
              item_ids: [1, 2],
            },
            {
              scenario: scenario({ site_id: "site-b", total_items: 3 }),
              item_ids: [3],
            },
          ]),
        },
      ),
    );

    await user.click(await screen.findByRole("button", { name: "Site A" }));
    await user.click(screen.getByRole("button", { name: "Tüm ürün sayfalarını aç" }));

    expect(open).toHaveBeenCalledTimes(2);
    expect(open).toHaveBeenNthCalledWith(
      1,
      "https://site-a.example/sauvage",
      "_blank",
      "noopener,noreferrer",
    );
    expect(open).toHaveBeenNthCalledWith(
      2,
      "https://site-a.example/aventus",
      "_blank",
      "noopener,noreferrer",
    );
    open.mockRestore();
  });

  it("does not offer a one-shop combination as a second plan", async () => {
    // A one-leg combination is the single-site plan under another name, and two
    // cards saying the same thing is not a comparison.
    renderScreen(
      basket([basketRow()], {
        report: { full: [scenario()], partial: [], unavailable: [] },
        best_combination: splitCombination([
          { scenario: scenario(), item_ids: [1] },
        ]),
      }),
    );

    await screen.findByText("Tek siteden");
    expect(screen.queryByText("Bulunan en iyi kombinasyon")).not.toBeInTheDocument();
  });

  it("says how much a genuine split saves", async () => {
    renderScreen(
      basket([basketRow(), basketRow({ basket_item_id: 2 })], {
        report: {
          full: [scenario({ subtotal_kurus: 60000, shipping_kurus: 3000 })],
          partial: [],
          unavailable: [],
        },
        best_combination: splitCombination(
          [
            { scenario: scenario({ site_id: "site-a" }), item_ids: [1] },
            { scenario: scenario({ site_id: "site-b" }), item_ids: [2] },
          ],
          { diff_kurus: -6000 },
        ),
      }),
    );

    expect(await screen.findByText("Bulunan en iyi kombinasyon")).toBeInTheDocument();
    expect(screen.getByText("60.00 ₺ daha ucuz")).toBeInTheDocument();
  });

  it("gives a tie to the single-shop plan", async () => {
    // One parcel from one shop for the same money is the easier order, so the
    // split has to actually be cheaper to win.
    renderScreen(
      basket([basketRow(), basketRow({ basket_item_id: 2 })], {
        report: { full: [scenario()], partial: [], unavailable: [] },
        best_combination: splitCombination(
          [
            { scenario: scenario({ site_id: "site-a" }), item_ids: [1] },
            { scenario: scenario({ site_id: "site-b" }), item_ids: [2] },
          ],
          { diff_kurus: 0 },
        ),
      }),
    );

    await screen.findByText("Bulunan en iyi kombinasyon");
    expect(screen.queryByText(/daha ucuz/)).not.toBeInTheDocument();
    const single = screen.getByText("Tek siteden").closest(".plan-card");
    expect(single).toHaveClass("win");
  });

  it("says plainly when no single shop can supply the basket", async () => {
    renderScreen(
      basket([basketRow()], {
        report: { full: [], partial: [scenario({ covered: 0 })], unavailable: [] },
      }),
    );

    expect(
      await screen.findByText("Sepetin tamamını tek başına karşılayan site yok."),
    ).toBeInTheDocument();
  });

  it("names what nothing on the list stocks at all", async () => {
    renderScreen(
      basket([basketRow()], {
        report: { full: [], partial: [], unavailable: ["Creed Aventus EDP 5 ml"] },
      }),
    );

    expect(
      await screen.findByText("Hiçbir sitede bulunamayan: Creed Aventus EDP 5 ml"),
    ).toBeInTheDocument();
  });

  it("reports a basket it could not read at all and offers a retry", async () => {
    server.on("GET /api/basket", () => ({ status: 500 }));
    render(
      <BasketScreen
        config={DEFAULT_CONFIG}
        siteNames={SITE_NAMES}
        notify={vi.fn()}
      />,
    );

    expect(await screen.findByText(/Sepet okunamadı: 500/)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Tekrar dene" })).toBeEnabled();
  });
});
