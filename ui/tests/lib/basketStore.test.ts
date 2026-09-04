import { beforeEach, describe, expect, it } from "vitest";
import {
  ensureBasket,
  getBasketSnapshot,
  invalidateBasket,
  resetBasketStoreForTests,
  refreshBasket,
} from "../../src/lib/basketStore";
import { basket, basketRow } from "../helpers/fixtures";
import { installFakeServer, type FakeServer } from "../helpers/server";

let server: FakeServer;

beforeEach(() => {
  server = installFakeServer();
  resetBasketStoreForTests();
  window.__PARFUM_TOKEN__ = "test-token";
});

describe("basket store", () => {
  it("deduplicates concurrent reads and reuses the successful response", async () => {
    const response = basket([basketRow()]);
    server.reply("GET /api/basket", response);

    const first = ensureBasket();
    const second = ensureBasket();
    expect(first).toBe(second);
    await expect(first).resolves.toEqual(response);
    await expect(ensureBasket()).resolves.toEqual(response);
    expect(server.requestsTo("GET", "/api/basket")).toHaveLength(1);
  });

  it("keeps cached data visible while a refresh is in flight", async () => {
    const response = basket([basketRow()]);
    let finish!: () => void;
    const held = new Promise<void>((resolve) => {
      finish = resolve;
    });
    let requestCount = 0;
    server.on("GET /api/basket", async () => {
      requestCount += 1;
      if (requestCount === 2) await held;
      return { body: requestCount === 1 ? response : basket([]) };
    });

    await ensureBasket();
    const refresh = refreshBasket();
    expect(getBasketSnapshot().data).toEqual(response);
    expect(getBasketSnapshot().refreshing).toBe(true);
    expect(getBasketSnapshot().stale).toBe(true);

    finish();
    await expect(refresh).resolves.toEqual(basket([]));
    expect(getBasketSnapshot().data).toEqual(basket([]));
    expect(getBasketSnapshot().refreshing).toBe(false);
  });

  it("queues one latest read when invalidated during an in-flight request", async () => {
    let firstFinish!: () => void;
    const firstHeld = new Promise<void>((resolve) => {
      firstFinish = resolve;
    });
    let requestCount = 0;
    const firstResponse = basket([basketRow({ label: "old" })]);
    const latestResponse = basket([basketRow({ label: "latest" })]);
    server.on("GET /api/basket", async () => {
      requestCount += 1;
      if (requestCount === 1) await firstHeld;
      return { body: requestCount === 1 ? firstResponse : latestResponse };
    });

    const first = ensureBasket();
    invalidateBasket();
    invalidateBasket();
    firstFinish();

    await expect(first).rejects.toThrow("Obsolete basket response");
    await expect(ensureBasket()).resolves.toEqual(latestResponse);
    expect(requestCount).toBe(2);
    expect(getBasketSnapshot().data).toEqual(latestResponse);
  });

  it("retains cached data and exposes a retryable error after refresh fails", async () => {
    const response = basket([basketRow()]);
    server.reply("GET /api/basket", response);
    await ensureBasket();
    server.on("GET /api/basket", () => ({ status: 503, body: { detail: "ulaşılamadı" } }));

    await expect(refreshBasket()).rejects.toThrow("ulaşılamadı");
    expect(getBasketSnapshot().data).toEqual(response);
    expect(getBasketSnapshot().stale).toBe(true);
    expect(getBasketSnapshot().error).toBeTruthy();
  });
});
