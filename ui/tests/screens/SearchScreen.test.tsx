// The screen's job is to say, before the request is sent, what the backend is
// going to read the line as. A counter that disagrees with the server is worse
// than no counter, so most of this is about the split rule.

import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { SearchScreen } from "../../src/screens/SearchScreen";
import type { SiteSummary } from "../../src/types";
import {
  DEFAULT_CONFIG,
  installFakeServer,
  searchStart,
  type FakeServer,
} from "../helpers/server";

let server: FakeServer;

const SITES: SiteSummary[] = [
  {
    id: "alpha",
    name: "Alfa Dekant",
    enabled: true,
    needs_review: false,
    discovered_at: "2026-08-01T00:00:00Z",
  },
  {
    id: "beta",
    name: "Beta Parfüm",
    enabled: true,
    needs_review: false,
    discovered_at: "2026-08-01T00:00:00Z",
  },
];

beforeEach(() => {
  server = installFakeServer();
  window.__PARFUM_TOKEN__ = "test-token";
});

function renderScreen(onStarted = vi.fn()) {
  render(<SearchScreen config={DEFAULT_CONFIG} sites={SITES} onStarted={onStarted} />);
  return { onStarted, field: screen.getByLabelText("Aranacak parfümler") };
}

describe("SearchScreen", () => {
  it("uses the floating label instead of a sample perfume placeholder", () => {
    const { field } = renderScreen();

    expect(
      screen.getByText("Birden fazla parfümü - ile ayırın. En fazla 10 parfüm."),
    ).toBeInTheDocument();
    expect(field).not.toHaveAttribute("placeholder");
  });

  it("counts one perfume for a hyphenated brand", async () => {
    // The separator is " - " with spaces, which is what keeps "Jean-Paul
    // Gaultier" from being read as two perfumes. The pattern comes from
    // /api/config so this rule has exactly one definition.
    const { field } = renderScreen();
    await userEvent.type(field, "Jean-Paul Gaultier Le Male");
    expect(screen.getByText("1 / 10")).toBeInTheDocument();
  });

  it("splits on the separator and shows a chip per perfume", async () => {
    const { field } = renderScreen();
    await userEvent.type(field, "Dior Sauvage EDP - Creed Aventus");
    expect(screen.getByText("2 / 10")).toBeInTheDocument();
    expect(screen.getByText("Dior Sauvage EDP")).toBeInTheDocument();
    expect(screen.getByText("Creed Aventus")).toBeInTheDocument();
  });

  it("counts a repeat typed in two casings once", async () => {
    // Turkish casing, so a dotted İ folds the way the server folds it. Two
    // chips for one perfume would promise a scan that never happens.
    const { field } = renderScreen();
    await userEvent.type(field, "Dior Sauvage - dior sauvage");
    expect(screen.getByText("1 / 10")).toBeInTheDocument();
  });

  it("removes a chip by rewriting the line from the remaining parts", async () => {
    // Cutting the typed text instead would leave a stray separator behind for
    // the server to reject.
    const { field } = renderScreen();
    await userEvent.type(field, "Dior Sauvage - Creed Aventus - Tom Ford Oud");
    await userEvent.click(screen.getByLabelText("Creed Aventus aramadan çıkarılsın"));

    expect(field).toHaveValue("Dior Sauvage - Tom Ford Oud");
    expect(screen.getByText("2 / 10")).toBeInTheDocument();
  });

  it("refuses the whole line over the limit instead of scanning the first ten", async () => {
    // A scan that quietly answered a shorter question is worse than no scan:
    // nothing on the results screen would say which perfumes were dropped.
    const { field, onStarted } = renderScreen();
    await userEvent.type(
      field,
      Array.from({ length: 11 }, (_, i) => `Parfum ${i}`).join(" - "),
    );

    const button = screen.getByRole("button", { name: /Ara/ });
    expect(button).toBeDisabled();
    expect(screen.getByText(/en fazla 10 parfüm aranabilir/)).toBeInTheDocument();

    await userEvent.click(button);
    expect(onStarted).not.toHaveBeenCalled();
    expect(server.requestsTo("POST", "/api/search")).toHaveLength(0);
  });

  it("will not start on an empty line", async () => {
    renderScreen();
    expect(screen.getByRole("button", { name: /Ara/ })).toBeDisabled();
  });

  it("starts the search on Enter, with the line as typed", async () => {
    // The request carries the raw line, not the chips: the server does its own
    // splitting, and sending a re-joined line would make this screen's
    // near-miss de-duplication the authority.
    server.reply("POST /api/search", searchStart(["Dior Sauvage EDP"]));
    const { field, onStarted } = renderScreen();

    await userEvent.type(field, "Dior Sauvage EDP{Enter}");

    await waitFor(() => expect(onStarted).toHaveBeenCalled());
    expect(server.requestsTo("POST", "/api/search")[0]?.body).toEqual({
      query: "Dior Sauvage EDP",
      force: false,
      site_ids: ["alpha", "beta"],
    });
  });

  it("sends only the shops the user keeps selected", async () => {
    server.reply("POST /api/search", searchStart(["Dior Sauvage EDP"]));
    const { field } = renderScreen();

    expect(screen.getByText("2 / 2 seçili")).toBeInTheDocument();
    await userEvent.click(screen.getByRole("checkbox", { name: "Beta Parfüm" }));
    await userEvent.type(field, "Dior Sauvage EDP{Enter}");

    await waitFor(() =>
      expect(server.requestsTo("POST", "/api/search")[0]?.body).toEqual({
        query: "Dior Sauvage EDP",
        force: false,
        site_ids: ["alpha"],
      }),
    );
  });

  it("requires at least one selected shop before starting", async () => {
    const { field, onStarted } = renderScreen();
    await userEvent.click(screen.getByRole("checkbox", { name: "Alfa Dekant" }));
    await userEvent.click(screen.getByRole("checkbox", { name: "Beta Parfüm" }));
    await userEvent.type(field, "Dior Sauvage EDP");

    expect(screen.getByText("Aramak için en az bir mağaza seçin.")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Ara/ })).toBeDisabled();
    expect(onStarted).not.toHaveBeenCalled();
  });

  it("passes the rescan choice to the request", async () => {
    server.reply("POST /api/search", searchStart(["Dior Sauvage EDP"]));
    const { field } = renderScreen();

    await userEvent.type(field, "Dior Sauvage EDP");
    await userEvent.click(
      screen.getByRole("checkbox", { name: /Kayıttakileri de yeniden tara/ }),
    );
    await userEvent.click(screen.getByRole("button", { name: /Ara/ }));

    await waitFor(() =>
      expect(server.requestsTo("POST", "/api/search")[0]?.body).toEqual({
        query: "Dior Sauvage EDP",
        force: true,
        site_ids: ["alpha", "beta"],
      }),
    );
  });

  it("shows the server's refusal and stays on the screen", async () => {
    server.reply("POST /api/search", { detail: "aynı parfüm iki kez yazılmış" }, 422);
    const { field, onStarted } = renderScreen();

    await userEvent.type(field, "Dior Sauvage EDP{Enter}");

    expect(
      await screen.findByText("aynı parfüm iki kez yazılmış"),
    ).toBeInTheDocument();
    expect(onStarted).not.toHaveBeenCalled();
    // Re-enabled: a refused start has to be fixable without a reload.
    expect(screen.getByRole("button", { name: /Ara/ })).toBeEnabled();
  });

  it("replays a recent search as the whole line it was typed as", async () => {
    // Selecting one has to bring back the multi-perfume query, not a single
    // piece of it.
    server.reply("GET /api/searches/recent", [
      { text: "Dior Sauvage EDP - Creed Aventus", searched_at: "2026-08-01T00:00:00Z" },
    ]);
    const { field } = renderScreen();

    await userEvent.click(
      await screen.findByText("Dior Sauvage EDP - Creed Aventus"),
    );
    expect(field).toHaveValue("Dior Sauvage EDP - Creed Aventus");
  });

  it("still takes a search when the history cannot be read", async () => {
    // A history nobody could read is a missing convenience, not a broken
    // screen.
    server.on("GET /api/searches/recent", () => ({ status: 500 }));
    server.reply("POST /api/search", searchStart(["Dior Sauvage EDP"]));
    const { field, onStarted } = renderScreen();

    await userEvent.type(field, "Dior Sauvage EDP{Enter}");
    await waitFor(() => expect(onStarted).toHaveBeenCalled());
    expect(screen.queryByText("Son aramalar")).not.toBeInTheDocument();
  });
});
