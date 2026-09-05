// The shell: what gates the window opening, what each tab is allowed to be,
// and which failures are allowed to be fatal. Only one of them is.

import { act, render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { App } from "../src/App";
import {
  ensureBasket,
  invalidateBasket,
  resetBasketStoreForTests,
} from "../src/lib/basketStore";
import { basket, basketRow, resultRow } from "./helpers/fixtures";
import {
  NO_UPDATE,
  installFakeServer,
  searchStart,
  type FakeServer,
} from "./helpers/server";

let server: FakeServer;
let restoreGetAnimations: (() => void) | null = null;

afterEach(() => {
  restoreGetAnimations?.();
  restoreGetAnimations = null;
});

beforeEach(() => {
  server = installFakeServer();
  resetBasketStoreForTests();
  window.__PARFUM_TOKEN__ = "test-token";
});

describe("App startup", () => {
  it("waits for the constants before drawing anything that depends on them", async () => {
    // The separator pattern, the perfume limit and the staleness threshold all
    // come from /api/config. A screen drawn before they arrive would have to
    // keep a second copy of them, which is how the two sides drift apart.
    render(<App />);
    expect(screen.getByText("Yükleniyor…")).toBeInTheDocument();
    expect(await screen.findByRole("button", { name: /^Ara$/ })).toBeInTheDocument();
  });

  it("says the backend could not be reached rather than showing an empty app", async () => {
    server.on("GET /api/config", () => ({ status: 500, body: { detail: "boom" } }));
    render(<App />);
    expect(await screen.findByText(/Arka uca bağlanılamadı: boom/)).toBeInTheDocument();
  });

  it("still opens when the update check fails", async () => {
    // An offline machine or a GitHub outage must not turn into a window that
    // refuses to open, which is why the check is not part of the startup read.
    server.on("GET /api/update", () => ({ status: 503 }));
    render(<App />);
    expect(await screen.findByRole("button", { name: /^Ara$/ })).toBeInTheDocument();
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  });

  it("still opens when the basket count cannot be read", async () => {
    // A count nobody could read is a missing convenience, not a broken screen.
    server.on("GET /api/basket", () => ({ status: 500 }));
    render(<App />);
    await screen.findByRole("button", { name: /^Ara$/ });
    expect(screen.getByRole("button", { name: "Sepet" })).toBeInTheDocument();
  });
});

describe("App tabs", () => {
  it("animates position and width together, and corrects observed resizes", async () => {
    const observed: Element[] = [];
    let observerCallback: ResizeObserverCallback | null = null;
    let widthCorrection = 0;
    let animationState: "idle" | "running" | "pending" = "idle";
    class FakeResizeObserver {
      constructor(callback: ResizeObserverCallback) {
        observerCallback = callback;
      }
      observe = vi.fn((target: Element) => observed.push(target));
      disconnect = vi.fn();
    }
    vi.stubGlobal("ResizeObserver", FakeResizeObserver);
    const originalGetAnimations = Object.getOwnPropertyDescriptor(
      HTMLElement.prototype,
      "getAnimations",
    );
    restoreGetAnimations = () => {
      if (originalGetAnimations) {
        Object.defineProperty(HTMLElement.prototype, "getAnimations", originalGetAnimations);
      } else {
        Reflect.deleteProperty(HTMLElement.prototype, "getAnimations");
      }
    };
    Object.defineProperty(HTMLElement.prototype, "getAnimations", {
      configurable: true,
      value: vi.fn(() =>
        animationState === "idle"
          ? []
          : [
              {
                playState: animationState === "running" ? "running" : "idle",
                pending: animationState === "pending",
              },
            ],
      ),
    });
    vi.spyOn(HTMLElement.prototype, "offsetLeft", "get").mockImplementation(function (
      this: HTMLElement,
    ) {
      if (!this.classList.contains("tab")) return 0;
      const tabs = Array.from(this.parentElement?.querySelectorAll(".tab") ?? []);
      return tabs.indexOf(this) * 100 + 8;
    });
    vi.spyOn(HTMLElement.prototype, "offsetWidth", "get").mockImplementation(function (
      this: HTMLElement,
    ) {
      if (this.classList.contains("tab")) {
        return 48 + (this.textContent?.length ?? 0) * 4 + widthCorrection;
      }
      return Number.parseFloat(this.style.width) || 0;
    });

    render(<App />);
    await screen.findByRole("button", { name: /^Ara$/ });

    await waitFor(() => expect(observed).toHaveLength(5));
    const tabs = screen.getByRole("navigation");
    const tabButtons = within(tabs).getAllByRole("button");
    const firstTab = tabButtons[0];
    const pill = tabs.querySelector<HTMLElement>(".tab-pill");
    if (pill === null || firstTab === undefined) throw new Error("tab geometry is missing");
    const transitionSetter = vi.spyOn(pill.style, "transition", "set");
    expect(observed).toEqual([tabs, ...tabButtons]);
    expect(observed).not.toContain(pill);
    expect(pill.style.transform).toBe("translateX(8px)");
    expect(pill.style.width).toBe(`${firstTab.offsetWidth}px`);

    animationState = "running";
    await userEvent.click(screen.getByRole("button", { name: "İstek listesi" }));
    expect(pill.style.transform).toBe("translateX(208px)");
    expect(pill.style.width).toBe(
      `${screen.getByRole("button", { name: "İstek listesi" }).offsetWidth}px`,
    );
    expect(pill.style.transition).toBe("");

    transitionSetter.mockClear();
    widthCorrection = 12;
    act(() => observerCallback?.([], {} as ResizeObserver));
    expect(pill.style.width).toBe(
      `${screen.getByRole("button", { name: "İstek listesi" }).offsetWidth}px`,
    );
    expect(pill.style.transition).toBe("");
    expect(transitionSetter).not.toHaveBeenCalled();

    animationState = "pending";
    widthCorrection = 18;
    act(() => observerCallback?.([], {} as ResizeObserver));
    expect(transitionSetter).not.toHaveBeenCalled();

    animationState = "idle";
    widthCorrection = 24;
    act(() => observerCallback?.([], {} as ResizeObserver));
    expect(transitionSetter.mock.calls.map(([value]) => value)).toEqual(["none", ""]);

  });

  it("corrects active pill geometry across basket and wishlist digit boundaries", async () => {
    let currentBasket = basket(
      Array.from({ length: 9 }, (_, index) =>
        basketRow({ basket_item_id: index + 1, label: `Basket row ${index + 1}` }),
      ),
    );
    const wishlistRows = Array.from({ length: 100 }, (_, index) => ({
      ...resultRow({
        name: `Wishlist ${index + 1}`,
        raw_title: `Wishlist row ${index + 1}`,
        size_ml_x10: index + 1,
      }),
      prices: {},
    }));
    server.on("GET /api/basket", () => ({ body: currentBasket }));
    server.reply("GET /api/wishlist", { rows: wishlistRows });
    vi.spyOn(HTMLElement.prototype, "offsetLeft", "get").mockImplementation(function (
      this: HTMLElement,
    ) {
      if (!this.classList.contains("tab")) return 0;
      const tabs = Array.from(this.parentElement?.querySelectorAll(".tab") ?? []);
      return tabs.indexOf(this) * 100;
    });
    vi.spyOn(HTMLElement.prototype, "offsetWidth", "get").mockImplementation(function (
      this: HTMLElement,
    ) {
      if (this.classList.contains("tab")) return 40 + (this.textContent?.length ?? 0) * 5;
      return Number.parseFloat(this.style.width) || 0;
    });

    render(<App />);
    const basketTab = await screen.findByRole("button", { name: /^Sepet/ });
    await waitFor(() => expect(basketTab).toHaveTextContent("9"));
    await userEvent.click(basketTab);
    const pill = screen.getByRole("navigation").querySelector<HTMLElement>(".tab-pill");
    if (pill === null) throw new Error("tab pill is missing");
    expect(pill.style.width).toBe(`${basketTab.offsetWidth}px`);
    await waitFor(() => expect(server.requestsTo("GET", "/api/basket").length).toBeGreaterThan(1));

    currentBasket = basket(
      Array.from({ length: 10 }, (_, index) =>
        basketRow({ basket_item_id: index + 1, label: `Basket row ${index + 1}` }),
      ),
    );
    await act(async () => {
      invalidateBasket();
      await ensureBasket();
    });
    expect(basketTab).toHaveTextContent("10");
    expect(pill.style.width).toBe(`${basketTab.offsetWidth}px`);

    const wishlistTab = screen.getByRole("button", { name: /^İstek listesi/ });
    await userEvent.click(wishlistTab);
    expect(wishlistTab).toHaveTextContent("100");
    expect(pill.style.width).toBe(`${wishlistTab.offsetWidth}px`);
    const removeButton = screen.getAllByRole("button", {
      name: "İstek listesinden çıkar",
    })[0];
    if (removeButton === undefined) throw new Error("wishlist remove button is missing");
    await userEvent.click(removeButton);
    await waitFor(() => expect(wishlistTab).toHaveTextContent("99"));
    expect(pill.style.width).toBe(`${wishlistTab.offsetWidth}px`);
  });

  it("loads saved items from the backend before enabling wishlist actions", async () => {
    const row = resultRow({ product_url: null });
    server.reply("GET /api/wishlist", { rows: [{ ...row, prices: {} }] });

    render(<App />);
    await screen.findByRole("button", { name: /^Ara$/ });

    const tab = screen.getByRole("button", { name: "İstek listesi" });
    expect(tab).toHaveTextContent("1");
    await userEvent.click(tab);
    expect(await screen.findByText(row.raw_title)).toBeInTheDocument();
  });

  it("keeps wishlist actions unavailable when saved items cannot be loaded", async () => {
    server.on("GET /api/wishlist", () => ({ status: 500, body: { detail: "wishlist yok" } }));

    render(<App />);
    await screen.findByRole("button", { name: /^Ara$/ });
    await userEvent.click(screen.getByRole("button", { name: "İstek listesi" }));

    expect(await screen.findByText("İstek listesi yükleniyor…")).toBeInTheDocument();
    expect(screen.getByText("wishlist yok")).toBeInTheDocument();
  });

  it("opens the wishlist from the bookmark tab", async () => {
    render(<App />);
    await screen.findByRole("button", { name: /^Ara$/ });

    await userEvent.click(screen.getByRole("button", { name: "İstek listesi" }));

    expect(
      screen.getByRole("heading", { name: "İstek listesi" }),
    ).toBeInTheDocument();
    expect(screen.getByText("Henüz istek listenize ürün eklemediniz.")).toBeInTheDocument();
  });

  it("adds a result to the wishlist and shows it on the saved-products screen", async () => {
    const row = resultRow({ product_url: null });
    server.reply("POST /api/search", searchStart(["Dior Sauvage EDP"]));
    server.on("GET /api/results/:searchId", () => ({
      body: { rows: [row], hidden_out_of_stock: 0, finished: true },
    }));
    server.on("GET /api/wishlist", () => ({
      body: {
        rows:
          server.requestsTo("PUT", "/api/wishlist/items").length > 0
            ? [{ ...row, prices: { [row.site_id]: row.price_kurus } }]
            : [],
      },
    }));
    render(<App />);
    await screen.findByRole("button", { name: /^Ara$/ });

    await userEvent.type(
      screen.getByLabelText("Aranacak parfümler"),
      "Dior Sauvage EDP{Enter}",
    );
    await userEvent.click(
      await screen.findByRole("button", { name: "İstek listesine ekle" }),
    );

    expect(server.requestsTo("PUT", "/api/wishlist/items")).toHaveLength(1);

    const tab = screen.getByRole("button", { name: "İstek listesi" });
    await waitFor(() => expect(tab).toHaveTextContent("1"));
    await userEvent.click(tab);
    expect(await screen.findByText(row.raw_title)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "İstek listesinden çıkar" })).toBeInTheDocument();
  });

  it("removes a hydrated item using its complete identity", async () => {
    const row = resultRow({ product_url: null });
    server.reply("GET /api/wishlist", { rows: [{ ...row, prices: {} }] });

    render(<App />);
    await screen.findByRole("button", { name: /^Ara$/ });
    const tab = screen.getByRole("button", { name: "İstek listesi" });
    await userEvent.click(tab);
    await userEvent.click(
      await screen.findByRole("button", { name: "İstek listesinden çıkar" }),
    );

    await screen.findByText("Henüz istek listenize ürün eklemediniz.");
    expect(server.requestsTo("DELETE", "/api/wishlist/items")[0]?.body).toEqual({
      site_id: row.site_id,
      brand: row.brand,
      name: row.name,
      concentration: row.concentration,
      size_ml_x10: row.size_ml_x10,
    });
    expect(tab).not.toHaveTextContent("1");
  });

  it("keeps local state unchanged when a wishlist mutation fails", async () => {
    const row = resultRow({ product_url: null });
    server.reply("PUT /api/wishlist/items", { detail: "kaydedilemedi" }, 500);
    server.reply("POST /api/search", searchStart(["Dior Sauvage EDP"]));
    server.on("GET /api/results/:searchId", () => ({
      body: { rows: [row], hidden_out_of_stock: 0, finished: true },
    }));

    render(<App />);
    await userEvent.type(
      await screen.findByLabelText("Aranacak parfümler"),
      "Dior Sauvage EDP{Enter}",
    );
    const button = await screen.findByRole("button", { name: "İstek listesine ekle" });
    await userEvent.click(button);

    expect(await screen.findByText("kaydedilemedi")).toBeInTheDocument();
    expect(button).toHaveAttribute("aria-pressed", "false");
    expect(screen.getByRole("button", { name: "İstek listesi" })).not.toHaveTextContent(
      "1",
    );
  });

  it("allows only one wishlist mutation per item at a time", async () => {
    const row = resultRow({ product_url: null });
    let finish!: () => void;
    const held = new Promise<void>((resolve) => {
      finish = resolve;
    });
    server.on("PUT /api/wishlist/items", async () => {
      await held;
      return { status: 204 };
    });
    server.reply("POST /api/search", searchStart(["Dior Sauvage EDP"]));
    server.on("GET /api/results/:searchId", () => ({
      body: { rows: [row], hidden_out_of_stock: 0, finished: true },
    }));

    render(<App />);
    await userEvent.type(
      await screen.findByLabelText("Aranacak parfümler"),
      "Dior Sauvage EDP{Enter}",
    );
    const button = await screen.findByRole("button", { name: "İstek listesine ekle" });

    await userEvent.click(button);
    expect(button).toBeDisabled();
    await userEvent.click(button);
    expect(server.requestsTo("PUT", "/api/wishlist/items")).toHaveLength(1);

    finish();
    await waitFor(() => expect(button).not.toBeDisabled());
  });

  it("keeps the results tab shut until there is a search to show", async () => {
    render(<App />);
    await screen.findByRole("button", { name: /^Ara$/ });
    expect(screen.getByRole("button", { name: "Sonuçlar" })).toBeDisabled();
  });

  it("keeps the typed search line when navigating away and back", async () => {
    render(<App />);
    const field = await screen.findByLabelText("Aranacak parfümler");

    await userEvent.type(field, "Dior Sauvage EDP - Creed Aventus");
    await userEvent.click(screen.getByRole("button", { name: "Sepet" }));
    await userEvent.click(screen.getByRole("button", { name: "Arama" }));

    expect(screen.getByLabelText("Aranacak parfümler")).toHaveValue(
      "Dior Sauvage EDP - Creed Aventus",
    );
  });

  it("clears the search line after starting a search", async () => {
    server.reply("POST /api/search", searchStart(["Dior Sauvage EDP"]));
    render(<App />);
    const field = await screen.findByLabelText("Aranacak parfümler");

    await userEvent.type(field, "Dior Sauvage EDP{Enter}");
    await screen.findByRole("heading", { name: "Dior Sauvage EDP" });
    await userEvent.click(screen.getByRole("button", { name: "Arama" }));

    expect(screen.getByLabelText("Aranacak parfümler")).toHaveValue("");
  });

  it("keeps the wishlist sort when switching screens", async () => {
    const row = { ...resultRow(), prices: { "site-a": 25000 } };
    server.reply("GET /api/wishlist", { rows: [row] });
    render(<App />);
    await screen.findByRole("button", { name: /^Ara$/ });

    await userEvent.click(screen.getByRole("button", { name: "İstek listesi" }));
    const price = await screen.findByRole("columnheader", { name: /Fiyat/ });
    await userEvent.click(price);
    expect(price).toHaveAttribute("aria-sort", "ascending");

    await userEvent.click(screen.getByRole("button", { name: "Arama" }));
    await userEvent.click(screen.getByRole("button", { name: "İstek listesi" }));

    expect(await screen.findByRole("columnheader", { name: /Fiyat/ })).toHaveAttribute(
      "aria-sort",
      "ascending",
    );
  });

  it("keeps the results sort when switching screens", async () => {
    server.reply("POST /api/search", searchStart(["Dior Sauvage EDP"]));
    server.on("GET /api/results/:searchId", () => ({
      body: { rows: [resultRow()], hidden_out_of_stock: 0, finished: true },
    }));
    render(<App />);
    await userEvent.type(
      await screen.findByLabelText("Aranacak parfümler"),
      "Dior Sauvage EDP{Enter}",
    );

    const price = await screen.findByRole("columnheader", { name: /₺\/ml/ });
    await userEvent.click(price);
    await waitFor(() => expect(price).toHaveAttribute("aria-sort", "ascending"));

    await userEvent.click(screen.getByRole("button", { name: "Arama" }));
    await userEvent.click(screen.getByRole("button", { name: "Sonuçlar" }));

    expect(await screen.findByRole("columnheader", { name: /₺\/ml/ })).toHaveAttribute(
      "aria-sort",
      "ascending",
    );
  });

  it("opens the results the moment a search starts", async () => {
    server.reply("POST /api/search", searchStart(["Dior Sauvage EDP"]));
    render(<App />);
    await screen.findByRole("button", { name: /^Ara$/ });

    await userEvent.type(
      screen.getByLabelText("Aranacak parfümler"),
      "Dior Sauvage EDP{Enter}",
    );

    // The heading of the results section, which only that screen draws.
    expect(
      await screen.findByRole("heading", { name: "Dior Sauvage EDP" }),
    ).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Sonuçlar/ })).toHaveAttribute(
      "aria-current",
      "page",
    );
  });

  it("counts the basket on its tab before that screen has ever been opened", async () => {
    server.reply(
      "GET /api/basket",
      basket([basketRow(), basketRow({ basket_item_id: 2 })]),
    );
    render(<App />);
    const tab = await screen.findByRole("button", { name: /Sepet/ });
    await waitFor(() => expect(tab).toHaveTextContent("2"));
  });

  it("re-counts the basket after something was added to it", async () => {
    // The count is owned here, so a screen that changed the basket has to say
    // so. Without that the tab keeps the number it had before.
    let rows = [basketRow()];
    server.on("GET /api/basket", () => ({ body: basket(rows) }));
    server.reply("POST /api/search", searchStart(["Dior Sauvage EDP"]));
    server.on("GET /api/results/:searchId", () => ({
      body: {
        rows: [resultRow({ product_url: null })],
        hidden_out_of_stock: 0,
        finished: true,
      },
    }));
    server.reply("POST /api/basket/items", { basket_item_id: 2 });
    render(<App />);
    await screen.findByRole("button", { name: /^Ara$/ });

    const tab = screen.getByRole("button", { name: /Sepet/ });
    await waitFor(() => expect(tab).toHaveTextContent("1"));

    await userEvent.type(
      screen.getByLabelText("Aranacak parfümler"),
      "Dior Sauvage EDP{Enter}",
    );
    rows = [basketRow(), basketRow({ basket_item_id: 2 })];
    await userEvent.click(
      (await screen.findAllByRole("button", { name: "Sepete ekle" }))[0]!,
    );

    await waitFor(() => expect(tab).toHaveTextContent("2"));
  });

  it("shows a basket read error with a retry action", async () => {
    server.on("GET /api/basket", ({ headers }) =>
      headers["X-Auth-Token"] === "test-token"
        ? { status: 500, body: { detail: "sepet okunamadı" } }
        : { status: 401 },
    );
    render(<App />);
    await screen.findByRole("button", { name: /^Ara$/ });

    await userEvent.click(screen.getByRole("button", { name: /Sepet/ }));
    expect(await screen.findByText(/Sepet okunamadı: sepet okunamadı/)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Tekrar dene" })).toBeEnabled();
  });
});

describe("App update prompt", () => {
  it("offers the new version once the check finds one", async () => {
    server.reply("GET /api/update", {
      ...NO_UPDATE,
      latest_version: "0.2.0",
      update_available: true,
      notes: "Yeni: sepet matrisi",
      download_url: "https://example.com/setup.exe",
    });
    render(<App />);

    const dialog = await screen.findByRole("dialog", { name: "Yeni sürüm" });
    expect(dialog).toHaveTextContent("0.2.0");
    expect(dialog).toHaveTextContent("Yeni: sepet matrisi");
  });

  it("says nothing when this is already the newest version", async () => {
    render(<App />);
    await screen.findByText("PARFUM FINDER");
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  });
});
