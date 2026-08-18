// The screen that answers "what should I buy". Two things it must never get
// wrong: which bottle the recommendation card is about, and which row the
// "önerilen" mark sits on. Both have already been shipped wrong once.

import { act, render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { ResultsScreen } from "../../src/screens/ResultsScreen";
import type { ResultRow } from "../../src/types";
import { basket, basketRow, resultRow } from "../helpers/fixtures";
import {
  DEFAULT_CONFIG,
  installFakeServer,
  type FakeServer,
} from "../helpers/server";

let server: FakeServer;
const SEARCH_ID = "search-1";
const STREAM = `/api/search/${SEARCH_ID}`;

beforeEach(() => {
  server = installFakeServer();
  window.__PARFUM_TOKEN__ = "test-token";
});

function renderScreen(
  rows: ResultRow[],
  options: {
    searches?: { index: number; text: string }[];
    rejected?: string[];
    finished?: boolean;
  } = {},
) {
  const notify = vi.fn();
  const onBasketChanged = vi.fn();
  server.on("GET /api/results/:searchId", () => ({
    body: {
      rows,
      hidden_out_of_stock: 0,
      finished: options.finished ?? true,
    },
  }));
  render(
    <ResultsScreen
      searchId={SEARCH_ID}
      searches={options.searches ?? [{ index: 0, text: "Dior Sauvage EDP" }]}
      rejected={options.rejected ?? []}
      config={DEFAULT_CONFIG}
      onBasketChanged={onBasketChanged}
      notify={notify}
    />,
  );
  return { notify, onBasketChanged };
}

/** The row the table marked as the answer, by its title cell. */
function recommendedRow(): HTMLElement {
  const badge = screen.getByText(/^önerilen/);
  const row = badge.closest("tr");
  if (row === null) throw new Error("the önerilen badge is not inside a row");
  return row;
}

/**
 * The add buttons in the table, in row order.
 *
 * Scoped to the table because the recommendation card above it has a button
 * with the same name, and an unscoped query would silently be about that one.
 */
async function rowAddButtons(): Promise<HTMLElement[]> {
  const table = await screen.findByRole("table");
  return within(table).getAllByRole("button", { name: "Sepete ekle" });
}

/**
 * The recommendation card's own "Sepete ekle" button, scoped to the verdict
 * card for the same reason rowAddButtons() is scoped to the table: the two
 * buttons share an accessible name, and an unscoped query would be about
 * whichever one testing-library happens to find first.
 */
function verdictAddButton(): HTMLElement {
  const card = screen.getByText(/^En iyi .* fiyatı$/).closest(".verdict");
  if (card === null) throw new Error("the verdict card is not in the document");
  return within(card as HTMLElement).getByRole("button", { name: "Sepete ekle" });
}

describe("ResultsScreen blocks", () => {
  it("keeps the server's order and groups neighbouring rows into one block", async () => {
    // ranking.py orders every row at once and keeps (query_index, product) as
    // its outer keys, so a block is a run of neighbours. Re-grouping with a map
    // would throw away the very ordering the request was made for.
    renderScreen([
      resultRow({ product: "Sauvage Elixir", size_ml_x10: 30, match_score: 60 }),
      resultRow({ product: "Sauvage Elixir", size_ml_x10: 50, match_score: 60 }),
      resultRow({ product: "Dior Sauvage EDP", size_ml_x10: 30 }),
    ]);

    await waitFor(() => expect(screen.getAllByText(/ boy$/)).toHaveLength(2));
    const notes = screen.getAllByText(/ boy$/);
    expect(notes.map((n) => n.textContent)).toEqual(["2 boy", "1 boy"]);
    expect(notes.map((n) => n.previousElementSibling?.textContent)).toEqual([
      "Sauvage Elixir",
      "Dior Sauvage EDP",
    ]);
  });
});

describe("ResultsScreen recommendation", () => {
  it("recommends from the best-matching bottle, not the first one alphabetically", async () => {
    // One query legitimately turns up a base scent and a flanker, and the
    // grouped order sorts those blocks by product name. A cheaper Elixir would
    // otherwise answer a question nobody asked.
    renderScreen([
      resultRow({
        product: "Sauvage Elixir",
        raw_title: "Sauvage Elixir 5 ml",
        name: "Sauvage Elixir",
        match_score: 62,
        price_kurus: 10000,
      }),
      resultRow({
        product: "Dior Sauvage EDP",
        raw_title: "Dior Sauvage EDP 5 ml",
        match_score: 97,
        price_kurus: 25000,
      }),
    ]);

    expect(await screen.findByText("En iyi 5 ml fiyatı")).toBeInTheDocument();
    expect(within(recommendedRow()).getByText("Dior Sauvage EDP 5 ml")).toBeInTheDocument();
  });

  it("leads with a sample size over the cheapest rate", async () => {
    // A shopper skimming the top reads "3 ml" as the answer to "what would
    // trying this cost me". The true cheapest ₺/ml keeps its own marker below.
    renderScreen([
      resultRow({
        raw_title: "Dior Sauvage EDP 10 ml",
        size_ml_x10: 100,
        price_kurus: 40000,
      }),
      resultRow({
        raw_title: "Dior Sauvage EDP 3 ml",
        size_ml_x10: 30,
        price_kurus: 18000,
      }),
    ]);

    expect(await screen.findByText("En iyi 3 ml fiyatı")).toBeInTheDocument();
    const marked = recommendedRow();
    expect(within(marked).getByText("Dior Sauvage EDP 3 ml")).toBeInTheDocument();
    // Two separate facts about two separate rows, so two separate badges.
    expect(screen.getByText("en iyi ₺/ml")).toBeInTheDocument();
    expect(screen.queryByText("önerilen · en iyi ₺/ml")).not.toBeInTheDocument();
  });

  it("says both facts in one badge when they are true of the same row", async () => {
    // Two badges side by side read as two different rows' marks.
    renderScreen([
      resultRow({ raw_title: "Dior Sauvage EDP 5 ml", size_ml_x10: 50, price_kurus: 20000 }),
      resultRow({ raw_title: "Dior Sauvage EDP 10 ml", size_ml_x10: 100, price_kurus: 60000 }),
    ]);

    expect(await screen.findByText("önerilen · en iyi ₺/ml")).toBeInTheDocument();
    expect(screen.queryByText("en iyi ₺/ml")).not.toBeInTheDocument();
  });

  it("never recommends a clone", async () => {
    // A clone wins on rate every time, and it is not the perfume that was
    // asked for.
    renderScreen([
      resultRow({
        raw_title: "Sauvage klonu 5 ml",
        clone_of: "Dior Sauvage",
        price_kurus: 5000,
      }),
      resultRow({ raw_title: "Dior Sauvage EDP 5 ml", price_kurus: 25000 }),
    ]);

    expect(await screen.findByText("En iyi 5 ml fiyatı")).toBeInTheDocument();
    expect(within(recommendedRow()).getByText("Dior Sauvage EDP 5 ml")).toBeInTheDocument();
  });

  it("ignores a price of zero instead of calling it the best deal", async () => {
    // Nothing stops a misread page storing a price of 0, and a free bottle
    // would win both verdicts outright and divide the rate by zero.
    renderScreen([
      resultRow({
        raw_title: "Dior Sauvage EDP 5 ml (bozuk okuma)",
        price_kurus: 0,
        price_per_ml_kurus: "0",
      }),
      resultRow({ raw_title: "Dior Sauvage EDP 5 ml", price_kurus: 25000 }),
    ]);

    expect(await screen.findByText("En iyi 5 ml fiyatı")).toBeInTheDocument();
    expect(within(recommendedRow()).getByText("Dior Sauvage EDP 5 ml")).toBeInTheDocument();
  });

  it("shows no card at all when nothing in the block has a price", async () => {
    renderScreen([
      resultRow({ price_kurus: null, price_per_ml_kurus: null, in_stock: false }),
    ]);

    await screen.findByText("Dior Sauvage EDP");
    expect(screen.queryByText(/En iyi .* fiyatı/)).not.toBeInTheDocument();
  });
});

describe("ResultsScreen basket", () => {
  it("sends the row's own identity, not the shop's title", async () => {
    // store.py's add_basket_item keys a line on brand, name, concentration and
    // size. Sending the raw title would make every shop's wording a new line.
    server.reply("POST /api/basket/items", { basket_item_id: 1 });
    const { onBasketChanged } = renderScreen([
      resultRow({ raw_title: "Dior Sauvage EDP Dekant 5 ml" }),
    ]);

    await userEvent.click((await rowAddButtons())[0]!);

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
        confirmed: false,
      }),
    );
    expect(onBasketChanged).toHaveBeenCalled();
  });

  it("explains a 409 in a dialog and re-sends the add as confirmed", async () => {
    // The backend refuses a weak match whether or not the modal was shown, so
    // the dialog is the explanation, not the gate.
    let calls = 0;
    server.on("POST /api/basket/items", () => {
      calls += 1;
      return calls === 1
        ? { status: 409, body: { detail: "confirm required" } }
        : { status: 200, body: { basket_item_id: 1 } };
    });
    renderScreen([
      resultRow({ raw_title: "Sauvage Elixir 5 ml", confident: false, match_score: 61 }),
    ]);

    await userEvent.click((await rowAddButtons())[0]!);

    const dialog = await screen.findByRole("dialog");
    expect(within(dialog).getByText(/%61 eşleşti/)).toBeInTheDocument();

    await userEvent.click(within(dialog).getByRole("button", { name: "Sepete ekle" }));

    await waitFor(() =>
      expect(server.requestsTo("POST", "/api/basket/items")).toHaveLength(2),
    );
    expect(server.requestsTo("POST", "/api/basket/items")[1]?.body).toMatchObject({
      confirmed: true,
    });
  });

  it("names the clone in the dialog rather than the match score", async () => {
    server.reply("POST /api/basket/items", { detail: "confirm required" }, 409);
    renderScreen([
      resultRow({ raw_title: "Sauvage klonu 5 ml", clone_of: "Dior Sauvage" }),
    ]);

    await userEvent.click((await rowAddButtons())[0]!);
    const dialog = await screen.findByRole("dialog");
    expect(within(dialog).getByText(/Dior Sauvage klonu olarak bulundu/)).toBeInTheDocument();
  });

  it("reports any other refusal as a toast and adds nothing", async () => {
    server.reply("POST /api/basket/items", { detail: "boy sepete eklenemez" }, 422);
    const { notify, onBasketChanged } = renderScreen([resultRow()]);

    await userEvent.click((await rowAddButtons())[0]!);

    await waitFor(() =>
      expect(notify).toHaveBeenCalledWith("boy sepete eklenemez", "error"),
    );
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
    expect(onBasketChanged).not.toHaveBeenCalled();
  });

  it("marks a row that is already in the basket", async () => {
    // The check comes from the basket's real state, not from a timer, so it is
    // still right after a reload and still right for a line added elsewhere.
    // "done" is the class the check is drawn from; there is nothing else on the
    // button that distinguishes the two states.
    server.reply(
      "GET /api/basket",
      basket([basketRow({ brand: "Dior", name: "Sauvage", concentration: "EDP" })]),
    );
    renderScreen([
      resultRow({ size_ml_x10: 50 }),
      resultRow({ site_id: "site-b", site_label: "Site B", size_ml_x10: 100 }),
    ]);

    const buttons = await rowAddButtons();
    await waitFor(() => expect(buttons[0]).toHaveClass("done"));
    // Same perfume, different size: a different basket line, so still a plus.
    expect(buttons[1]).not.toHaveClass("done");
  });

  it("marks the recommendation card's own button from the same basket state", async () => {
    // The headline verdict has a second, separate "Sepete ekle" button next
    // to the table's. It reads the basket the same real way, not a timer, so
    // a line added elsewhere still shows the check here on load.
    server.reply(
      "GET /api/basket",
      basket([basketRow({ brand: "Dior", name: "Sauvage", concentration: "EDP" })]),
    );
    renderScreen([resultRow()]);

    await screen.findByText(/^En iyi .* fiyatı$/);
    await waitFor(() => expect(verdictAddButton()).toHaveClass("done"));
  });

  it("turns the recommendation card's plus into a check once the add succeeds", async () => {
    // The task this button exists for: pressing it must show the same
    // confirmation the table's plus-to-check button shows, not just fire the
    // request silently.
    server.reply("POST /api/basket/items", { basket_item_id: 1 });
    renderScreen([resultRow()]);

    await screen.findByText(/^En iyi .* fiyatı$/);
    const button = verdictAddButton();
    expect(button).not.toHaveClass("done");

    await userEvent.click(button);

    await waitFor(() => expect(verdictAddButton()).toHaveClass("done"));
  });
});

describe("ResultsScreen scan progress", () => {
  it("warns about a site whose profile could not read the answer", async () => {
    // An empty answer and an unreadable one are different facts. Left silent,
    // the missing prices would read as "not sold here".
    renderScreen([resultRow()], { finished: false });
    const socket = await server.socket(STREAM);

    act(() =>
      socket.emit({
        type: "site_finished",
        site_id: "site-b",
        query_index: 0,
        status: "suspect",
        detail: "0 sonuç",
        has_rows: false,
      }),
    );

    expect(
      await screen.findByText(/site-b: bu profil bozulmuş olabilir — 0 sonuç/),
    ).toBeInTheDocument();
  });

  it("lists the shops that simply had nothing, without calling it an error", async () => {
    renderScreen([resultRow()], { finished: false });
    const socket = await server.socket(STREAM);

    act(() =>
      socket.emit({
        type: "site_finished",
        site_id: "site-c",
        query_index: 0,
        status: "empty",
        detail: null,
        has_rows: false,
      }),
    );

    expect(await screen.findByText("Bulunamadı: site-c")).toBeInTheDocument();
    expect(screen.queryByText(/hata ile bitti/)).not.toBeInTheDocument();
  });

  it("says a cached reading was cached, and how to force a rescan", async () => {
    renderScreen([resultRow()], { finished: false });
    const socket = await server.socket(STREAM);

    act(() => socket.emit({ type: "cache_hit", query_index: 0, age_days: 3 }));

    expect(
      await screen.findByText(/Kayıttan geldi, 3 gün önce okundu/),
    ).toBeInTheDocument();
  });

  it("re-reads the table when the scan finishes", async () => {
    // Rows land once, all together: a table reshuffling as sites trickle in
    // cannot be read. So the finish event is the only thing that fills it.
    let rows: ResultRow[] = [];
    server.on("GET /api/results/:searchId", () => ({
      body: { rows, hidden_out_of_stock: 0, finished: rows.length > 0 },
    }));
    render(
      <ResultsScreen
        searchId={SEARCH_ID}
        searches={[{ index: 0, text: "Dior Sauvage EDP" }]}
        rejected={[]}
        config={DEFAULT_CONFIG}
        onBasketChanged={vi.fn()}
        notify={vi.fn()}
      />,
    );

    expect(await screen.findByText("Aranıyor…")).toBeInTheDocument();

    const socket = await server.socket(STREAM);
    rows = [resultRow({ raw_title: "Dior Sauvage EDP 5 ml" })];
    act(() => socket.emit({ type: "scan_finished", error_count: 0 }));

    expect(await screen.findByText("Dior Sauvage EDP 5 ml")).toBeInTheDocument();
  });

  it("stops claiming to be working when the stream was refused", async () => {
    // A refused socket means the scan never started. A progress bar left
    // running would be the screen saying it is still working when it is not.
    renderScreen([], { finished: false });
    const socket = await server.socket(STREAM);
    // Waited for on purpose: the point is that the refusal stops a bar that
    // was already running, not that it beat the first read of the table.
    await screen.findByRole("status");

    act(() => socket.refuse(4409));

    expect(
      await screen.findByText("Tarama başlamadı: bu arama zaten başlatılmış"),
    ).toBeInTheDocument();
    expect(screen.queryByRole("status")).not.toBeInTheDocument();
  });

  it("keeps the bar down when the table is read after the refusal", async () => {
    // The read of the table can answer after the socket was refused, and it
    // carries finished=false while another socket drives the scan. Letting
    // that answer win puts back a bar this screen can never advance, since
    // the events that would move it are going somewhere else.
    let release: () => void = () => undefined;
    const held = new Promise<void>((resolve) => {
      release = resolve;
    });
    server.on("GET /api/results/:searchId", async () => {
      await held;
      return { body: { rows: [], hidden_out_of_stock: 0, finished: false } };
    });
    render(
      <ResultsScreen
        searchId={SEARCH_ID}
        searches={[{ index: 0, text: "Dior Sauvage EDP" }]}
        rejected={[]}
        config={DEFAULT_CONFIG}
        onBasketChanged={vi.fn()}
        notify={vi.fn()}
      />,
    );
    const socket = await server.socket(STREAM);

    act(() => socket.refuse(4409));
    await screen.findByText("Tarama başlamadı: bu arama zaten başlatılmış");
    await act(async () => {
      release();
      await held;
    });

    await screen.findByText("Bu ekrana sonuç gelmedi.");
    expect(screen.queryByRole("status")).not.toBeInTheDocument();
  });

  it("shows the pieces of the line the server could not read", async () => {
    renderScreen([], { rejected: ["- - -"] });
    expect(
      await screen.findByText("Okunamayan parça atlandı: - - -"),
    ).toBeInTheDocument();
  });
});

describe("ResultsScreen table", () => {
  it("badges a reading old enough to be stale and leaves a fresh one plain", async () => {
    renderScreen([
      resultRow({ raw_title: "Dior Sauvage EDP 5 ml", age_days: 20 }),
      resultRow({
        raw_title: "Dior Sauvage EDP 10 ml",
        site_id: "site-b",
        size_ml_x10: 100,
        age_days: 2,
      }),
    ]);

    const stale = await screen.findByText("2 hafta önce");
    expect(stale).toHaveClass("badge", "stale");
    expect(screen.getByText("2 gün önce")).not.toHaveClass("badge");
  });

  it("asks the server to re-sort, and clears the sort on a second click", async () => {
    // Sorting is the server's: re-deriving the order here from the decimal
    // strings would eventually disagree with what it sent.
    renderScreen([resultRow()]);
    const header = await screen.findByRole("columnheader", { name: /₺\/ml/ });

    await userEvent.click(header);
    await waitFor(() =>
      expect(
        server.requestsTo("GET", `/api/results/${SEARCH_ID}`).map((r) => r.search),
      ).toContain("?sort=per_ml"),
    );
    expect(header).toHaveAttribute("aria-sort", "ascending");

    await userEvent.click(header);
    await waitFor(() => expect(header).toHaveAttribute("aria-sort", "none"));
  });

  it("opens the shop's own page for a row that has one", async () => {
    renderScreen([
      resultRow({ raw_title: "Dior Sauvage EDP 5 ml", product_url: "https://shop/x" }),
    ]);

    await userEvent.click(await screen.findByText("Dior Sauvage EDP 5 ml"));
    expect(window.open).toHaveBeenCalledWith("https://shop/x", "_blank", "noopener");
  });

  it("keeps two perfumes that share a title, size and shop as two rows", async () => {
    // The row key is the identity the backend dedupes on, not the title: a
    // colliding key makes React reuse one row's DOM node for the other, which
    // reads as a duplicate that will not reorder.
    renderScreen([
      resultRow({ raw_title: "Sauvage 5 ml", name: "Sauvage" }),
      resultRow({ raw_title: "Sauvage 5 ml", name: "Sauvage Elixir" }),
    ]);

    expect(await screen.findAllByText("Sauvage 5 ml")).toHaveLength(2);
  });
});
