import type { APIRequestContext, CDPSession, Locator, Page } from "@playwright/test";
import { expect } from "@playwright/test";

/**
 * One of the toolbar tabs.
 *
 * Scoped to the header because "Sepet" also starts the name of every "Sepete
 * ekle" button in the table, and the tab's own name grows a count when the
 * basket is not empty.
 */
export function tab(
  page: Page,
  name: "Arama" | "Sonuçlar" | "İstek listesi" | "Sepet",
): Locator {
  return page.locator("header.toolbar").getByRole("button", { name });
}

/**
 * Open the app and wait until it has its constants.
 *
 * Every screen is gated on /api/config, so a test that starts typing before
 * the toolbar exists is racing the app's own startup rather than testing it.
 */
export async function openApp(page: Page): Promise<void> {
  await page.goto("/");
  await expect(searchButton(page)).toBeVisible();
}

/** The button that starts a scan. Exact, because the Arama tab is also "Ara…". */
export function searchButton(page: Page): Locator {
  return page.getByRole("button", { name: "Ara", exact: true });
}

/** Run one search and wait for the table the scan fills in one go. */
export async function search(page: Page, query: string): Promise<void> {
  await page.getByLabel("Aranacak parfümler").fill(query);
  await searchButton(page).click();
  // A scan of the fixture shops is quick, but it is still a real scan through
  // the service, the matcher and a sqlite write.
  await expect(page.getByRole("table").first()).toBeVisible({ timeout: 20_000 });
}

/**
 * The token the backend injected into the page, so a test can talk to the API
 * directly. Reading it from the window is the only way to have it: it is a
 * fresh random string per backend process.
 */
export async function authToken(page: Page): Promise<string> {
  const token = await page.evaluate(
    () => (window as { __PARFUM_TOKEN__?: string }).__PARFUM_TOKEN__,
  );
  if (token === undefined) throw new Error("the page was served without a token");
  return token;
}

/**
 * Empty the basket over the API.
 *
 * The specs share one backend process and one database, so a spec that assumed
 * an empty basket would otherwise be asserting against whatever the previous
 * one left behind.
 */
export async function clearBasket(
  page: Page,
  request: APIRequestContext,
): Promise<void> {
  const headers = { "X-Auth-Token": await authToken(page) };
  const response = await request.get("/api/basket", { headers });
  const body = (await response.json()) as { rows: { basket_item_id: number }[] };
  for (const row of body.rows) {
    await request.delete(`/api/basket/items/${row.basket_item_id}`, { headers });
  }
}

type WishlistIdentity = {
  site_id: string;
  brand: string;
  name: string;
  concentration: string;
  size_ml_x10: number;
};

/** Remove every saved offer so scale tests start from a known database state. */
export async function clearWishlist(
  page: Page,
  request: APIRequestContext,
): Promise<void> {
  const headers = { "X-Auth-Token": await authToken(page) };
  const response = await request.get("/api/wishlist", { headers });
  if (!response.ok()) throw new Error(`wishlist read failed with ${response.status()}`);
  const body = (await response.json()) as { rows: WishlistIdentity[] };
  for (const row of body.rows) {
    const identity: WishlistIdentity = {
      site_id: row.site_id,
      brand: row.brand,
      name: row.name,
      concentration: row.concentration,
      size_ml_x10: row.size_ml_x10,
    };
    const deleted = await request.delete("/api/wishlist/items", {
      headers,
      data: identity,
    });
    if (!deleted.ok())
      throw new Error(`wishlist delete failed with ${deleted.status()}`);
  }
}

/** Seed deterministic rows through the same API the browser uses. */
export interface WishlistSeedOptions {
  ageDays?: number;
}

export async function seedWishlist(
  page: Page,
  request: APIRequestContext,
  count: number,
  options: WishlistSeedOptions = {},
): Promise<void> {
  if (!Number.isInteger(count) || count < 1)
    throw new Error(`wishlist seed count must be a positive integer, got ${count}`);
  await clearWishlist(page, request);
  const headers = { "X-Auth-Token": await authToken(page) };
  const ageDays = options.ageDays ?? 0;
  for (let index = 0; index < count; index += 1) {
    const size_ml_x10 = index + 1;
    const title = `Benchmark perfume ${String(index + 1).padStart(3, "0")} 5 ml`;
    const response = await request.put("/api/wishlist/items", {
      headers,
      data: {
        site_id: "site-a",
        site_label: "Alfa Dekant",
        query_index: 0,
        product: `Benchmark perfume ${index + 1}`,
        raw_title: title,
        price_kurus: null,
        price_per_ml_kurus: null,
        in_stock: true,
        match_score: 95,
        confident: true,
        brand: "Benchmark",
        name: `Perfume ${index + 1}`,
        concentration: "EDP",
        size_ml_x10,
        product_url: null,
        clone_of: "",
        own_identity: true,
        age_days: ageDays,
      },
    });
    if (!response.ok())
      throw new Error(`wishlist seed failed at ${index + 1}: ${response.status()}`);
  }
  await page.reload();
  await expect(searchButton(page)).toBeVisible();
}

export interface BrowserPerformanceSnapshot {
  domNodeCount: number;
  heapUsedBytes: number | null;
  layoutCount: number | null;
  recalcStyleCount: number | null;
  taskDurationSeconds: number | null;
}

/** Read stable browser counters without making timing a pass/fail criterion. */
export async function performanceSnapshot(
  page: Page,
  performanceClient?: CDPSession,
): Promise<BrowserPerformanceSnapshot> {
  const browserValues = await page.evaluate(() => {
    const performanceWithMemory = performance as Performance & {
      memory?: { usedJSHeapSize?: number };
    };
    return {
      domNodeCount: document.querySelectorAll("*").length,
      heapUsedBytes: performanceWithMemory.memory?.usedJSHeapSize ?? null,
    };
  });

  let metrics: Record<string, number> = {};
  let ownClient = false;
  let client = performanceClient;
  try {
    if (client === undefined) {
      client = await page.context().newCDPSession(page);
      ownClient = true;
    }
    try {
      await client.send("Performance.enable");
      const result = (await client.send("Performance.getMetrics")) as {
        metrics?: { name: string; value: number }[];
      };
      metrics = Object.fromEntries(
        (result.metrics ?? []).map(({ name, value }) => [name, value]),
      );
    } finally {
      if (ownClient) await client.detach();
    }
  } catch {
    // Firefox and non-Chromium WebViews do not expose the DevTools counters.
  }

  return {
    ...browserValues,
    heapUsedBytes:
      metrics.JSHeapUsedSize ?? browserValues.heapUsedBytes ?? null,
    layoutCount: metrics.LayoutCount ?? null,
    recalcStyleCount: metrics.RecalcStyleCount ?? null,
    taskDurationSeconds: metrics.TaskDuration ?? null,
  };
}

export interface PageDiagnostics {
  consoleErrors: string[];
  pageErrors: string[];
  failedRequests: string[];
  requests: string[];
  stop: () => void;
}

/** Capture browser failures and request URLs around a targeted E2E journey. */
export function watchPageDiagnostics(page: Page): PageDiagnostics {
  const consoleErrors: string[] = [];
  const pageErrors: string[] = [];
  const failedRequests: string[] = [];
  const requests: string[] = [];
  const onConsole = (message: { type(): string; text(): string }) => {
    if (message.type() === "error") consoleErrors.push(message.text());
  };
  const onPageError = (error: Error) => pageErrors.push(error.message);
  const onRequestFailed = (request: { url(): string; failure(): { errorText?: string } | null }) => {
    failedRequests.push(`${request.url()} ${request.failure()?.errorText ?? "unknown"}`);
  };
  const onRequest = (request: { url(): string }) => requests.push(request.url());
  page.on("console", onConsole);
  page.on("pageerror", onPageError);
  page.on("requestfailed", onRequestFailed);
  page.on("request", onRequest);
  return {
    consoleErrors,
    pageErrors,
    failedRequests,
    requests,
    stop: () => {
      page.off("console", onConsole);
      page.off("pageerror", onPageError);
      page.off("requestfailed", onRequestFailed);
      page.off("request", onRequest);
    },
  };
}
