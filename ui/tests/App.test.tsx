// The shell: what gates the window opening, what each tab is allowed to be,
// and which failures are allowed to be fatal. Only one of them is.

import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it } from "vitest";
import { App } from "../src/App";
import { basket, basketRow, resultRow } from "./helpers/fixtures";
import {
  NO_UPDATE,
  installFakeServer,
  searchStart,
  type FakeServer,
} from "./helpers/server";

let server: FakeServer;

beforeEach(() => {
  server = installFakeServer();
  window.__PARFUM_TOKEN__ = "test-token";
  window.localStorage.clear();
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
    render(<App />);
    await screen.findByRole("button", { name: /^Ara$/ });

    await userEvent.type(
      screen.getByLabelText("Aranacak parfümler"),
      "Dior Sauvage EDP{Enter}",
    );
    await userEvent.click(
      await screen.findByRole("button", { name: "İstek listesine ekle" }),
    );

    const tab = screen.getByRole("button", { name: "İstek listesi" });
    await waitFor(() => expect(tab).toHaveTextContent("1"));
    await userEvent.click(tab);
    expect(await screen.findByText(row.raw_title)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "İstek listesinden çıkar" })).toBeInTheDocument();
  });

  it("keeps the results tab shut until there is a search to show", async () => {
    render(<App />);
    await screen.findByRole("button", { name: /^Ara$/ });
    expect(screen.getByRole("button", { name: "Sonuçlar" })).toBeDisabled();
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

  it("shows a screen's error as a toast over whatever is on screen", async () => {
    server.on("GET /api/basket", ({ headers }) =>
      headers["X-Auth-Token"] === "test-token"
        ? { status: 500, body: { detail: "sepet okunamadı" } }
        : { status: 401 },
    );
    render(<App />);
    await screen.findByRole("button", { name: /^Ara$/ });

    await userEvent.click(screen.getByRole("button", { name: /Sepet/ }));
    expect(await screen.findByText("sepet okunamadı")).toBeInTheDocument();
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
