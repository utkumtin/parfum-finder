import type { APIRequestContext, Locator, Page } from "@playwright/test";
import { expect } from "@playwright/test";

/**
 * One of the three tabs in the toolbar.
 *
 * Scoped to the header because "Sepet" also starts the name of every "Sepete
 * ekle" button in the table, and the tab's own name grows a count when the
 * basket is not empty.
 */
export function tab(page: Page, name: "Arama" | "Sonuçlar" | "Sepet"): Locator {
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
