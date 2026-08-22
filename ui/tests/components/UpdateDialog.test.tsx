// This dialog hands the running app over to an installer and then the window
// closes itself. Two rules follow from that and neither is cosmetic: the
// handover happens exactly once, and the dialog cannot be dismissed while a
// download nobody is watching would be left running.

import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { UpdateDialog } from "../../src/components/UpdateDialog";
import type { UpdateInfo } from "../../src/types";
import {
  installFakeServer,
  updateProgress,
  type FakeServer,
} from "../helpers/server";

let server: FakeServer;

const INFO: UpdateInfo = {
  current_version: "0.1.0",
  latest_version: "0.2.0",
  update_available: true,
  notes: "Yeni: sepet matrisi",
  release_url: "https://example.com/releases/0.2.0",
  download_url: "https://example.com/setup.exe",
};

beforeEach(() => {
  server = installFakeServer();
  window.__PARFUM_TOKEN__ = "test-token";
});

function renderDialog(info: UpdateInfo = INFO) {
  const onDismiss = vi.fn();
  render(<UpdateDialog info={info} onDismiss={onDismiss} />);
  return { onDismiss };
}

describe("UpdateDialog", () => {
  it("uses symmetric modal-action spacing for the update label", () => {
    renderDialog();

    expect(screen.getByRole("button", { name: "Güncelle" })).toHaveClass(
      "update-action",
    );
  });

  it("shows the release notes as the text GitHub stores, not as markup", async () => {
    // A changelog is not worth a Markdown dependency, and it is certainly not
    // worth injecting remote HTML into the app.
    renderDialog({ ...INFO, notes: "## Yeni\n- sepet matrisi" });
    expect(screen.getByText("## Yeni - sepet matrisi")).toBeInTheDocument();
  });

  it("says so when the release has no notes at all", () => {
    renderDialog({ ...INFO, notes: "" });
    expect(screen.getByText("Bu sürüm için not yazılmamış.")).toBeInTheDocument();
  });

  it("never sends the download URL it was given", async () => {
    // The backend re-checks the release and downloads what it found itself, so
    // nothing a page could tamper with decides what gets run.
    server.reply("POST /api/update/download", updateProgress({ state: "downloading" }));
    renderDialog();

    await userEvent.click(screen.getByRole("button", { name: "Güncelle" }));
    await waitFor(() =>
      expect(server.requestsTo("POST", "/api/update/download")).toHaveLength(1),
    );
    expect(server.requestsTo("POST", "/api/update/download")[0]?.body).toBeUndefined();
  });

  it("cannot be dismissed while the download is running", async () => {
    // Closing it would leave a download nobody is watching, finishing into a
    // window that shuts itself.
    server.reply(
      "POST /api/update/download",
      updateProgress({ state: "downloading", received: 1024, total: 4096 }),
    );
    const { onDismiss } = renderDialog();

    await userEvent.click(screen.getByRole("button", { name: "Güncelle" }));

    const later = await screen.findByRole("button", { name: "Şimdi değil" });
    await waitFor(() => expect(later).toBeDisabled());
    await userEvent.keyboard("{Escape}");
    expect(onDismiss).not.toHaveBeenCalled();
  });

  it("hands the installer over once, however often the progress poll answers ready", async () => {
    // A poll still in flight when the download finishes writes a second
    // "ready", and asking twice means a 409 painted as a failure over a window
    // that is already closing.
    server.reply("POST /api/update/download", updateProgress({ state: "downloading" }));
    server.reply("GET /api/update/progress", updateProgress({ state: "ready" }));
    server.reply("POST /api/update/install", { installing: true });
    renderDialog();

    await userEvent.click(screen.getByRole("button", { name: "Güncelle" }));

    expect(await screen.findByText(/Kurulum başlatılıyor/)).toBeInTheDocument();
    // Long enough for several more 400 ms polls to have come back "ready".
    await new Promise((resolve) => setTimeout(resolve, 900));
    expect(server.requestsTo("POST", "/api/update/install")).toHaveLength(1);
  });

  it("reports the backend's own failure message and offers a retry", async () => {
    server.reply("POST /api/update/download", updateProgress({ state: "downloading" }));
    server.reply(
      "GET /api/update/progress",
      updateProgress({ state: "error", message: "indirme yarıda kesildi" }),
    );
    renderDialog();

    await userEvent.click(screen.getByRole("button", { name: "Güncelle" }));

    expect(
      await screen.findByText("Güncelleme başarısız: indirme yarıda kesildi"),
    ).toBeInTheDocument();
    // Not "Güncelle" any more: the button has to say that pressing it again is
    // a retry, and it has to be pressable.
    expect(screen.getByRole("button", { name: "Tekrar dene" })).toBeEnabled();
    expect(screen.getByRole("button", { name: "Şimdi değil" })).toBeEnabled();
  });

  it("reports a download that could not even be started", async () => {
    server.reply("POST /api/update/download", { detail: "disk dolu" }, 500);
    renderDialog();

    await userEvent.click(screen.getByRole("button", { name: "Güncelle" }));
    expect(
      await screen.findByText("Güncelleme başarısız: disk dolu"),
    ).toBeInTheDocument();
  });

  it("closes on Escape while nothing is running", async () => {
    const { onDismiss } = renderDialog();
    await userEvent.keyboard("{Escape}");
    expect(onDismiss).toHaveBeenCalled();
  });
});
