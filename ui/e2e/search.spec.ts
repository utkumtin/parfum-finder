// The search journey through a real browser, a real scan and a real database.
// What this catches that the jsdom suite cannot: the page actually being served
// with its token, the WebSocket actually upgrading, and the scan's events
// actually arriving in the order the screen assumes.

import { expect, test } from "@playwright/test";
import { openApp, search, searchButton, tab } from "./helpers";

test("a search fills the table from the shops that stock the perfume", async ({
  page,
}) => {
  await openApp(page);
  await search(page, "Dior Sauvage EDP");

  const table = page.getByRole("table").first();
  // Both fixture shops carry it, at three sizes between them.
  await expect(table.getByText("Alfa Dekant").first()).toBeVisible();
  await expect(table.getByText("Beta Dekant").first()).toBeVisible();
});

test("the results and wishlist action buttons stay inside their tables", async ({
  page,
}) => {
  await openApp(page);
  await search(page, "Dior Sauvage EDP");

  const resultTable = page.getByRole("table").first();
  const resultActions = resultTable.locator(".row-actions").first();
  await expect(resultActions).toBeVisible();

  const resultBounds = await resultTable.boundingBox();
  const resultActionBounds = await resultActions.boundingBox();
  if (resultBounds === null || resultActionBounds === null)
    throw new Error("the results table actions are not measurable");
  expect(resultActionBounds.x + resultActionBounds.width).toBeLessThanOrEqual(
    resultBounds.x + resultBounds.width,
  );

  const wishlistButtons = resultTable.getByRole("button", { name: "İstek listesine ekle" });
  await wishlistButtons.first().click();
  await wishlistButtons.last().click();
  await tab(page, "İstek listesi").click();

  const wishlistTable = page.getByRole("table");
  const wishlistActions = wishlistTable.locator(".row-actions").first();
  await expect(wishlistActions).toBeVisible();

  const wishlistBounds = await wishlistTable.boundingBox();
  const wishlistActionBounds = await wishlistActions.boundingBox();
  if (wishlistBounds === null || wishlistActionBounds === null)
    throw new Error("the wishlist table actions are not measurable");
  expect(wishlistActionBounds.x + wishlistActionBounds.width).toBeLessThanOrEqual(
    wishlistBounds.x + wishlistBounds.width,
  );

  const wishlistSearch = page.getByRole("searchbox", { name: "İstek listesinde ara" });
  await wishlistSearch.fill("Beta");
  await expect(wishlistTable.getByText("Beta Dekant").first()).toBeVisible();
  await expect(wishlistTable.getByText("Alfa Dekant").first()).toBeHidden();

  await page.getByRole("button", { name: "Aramayı temizle" }).click();
  await expect(wishlistSearch).toBeFocused();
  await expect(wishlistTable.getByText("Alfa Dekant").first()).toBeVisible();
});

test("the recommendation names a sample size and the shop selling it", async ({
  page,
}) => {
  await openApp(page);
  await search(page, "Dior Sauvage EDP");

  // Alfa's 3 ml at 120.00 ₺ is the cheapest sample in the fixture catalogue.
  await expect(page.getByText("En iyi 3 ml fiyatı")).toBeVisible();
  const card = page.locator(".verdict");
  await expect(card).toContainText("120.00 ₺");
  await expect(card).toContainText("Alfa Dekant");
  await expect(page.getByText(/^önerilen/).first()).toBeVisible();
});

test("a second search of the same perfume is answered from storage", async ({
  page,
}) => {
  // The whole point of the price history: a perfume searched a moment ago is
  // not worth a second round of requests, and the screen has to say the answer
  // came from storage rather than pass it off as fresh.
  await openApp(page);
  await search(page, "Dior Sauvage EDP");
  await tab(page, "Arama").click();
  await search(page, "Dior Sauvage EDP");

  await expect(page.getByText(/Kayıttan geldi/)).toBeVisible();
});

test("a perfume nobody stocks is reported as not found, not as an error", async ({
  page,
}) => {
  await openApp(page);
  await page.getByLabel("Aranacak parfümler").fill("Bilinmeyen Parfüm XZ");
  await searchButton(page).click();

  await expect(page.getByText("Hiçbir sitede bulunamadı.")).toBeVisible({
    timeout: 20_000,
  });
  await expect(page.getByText(/hata ile bitti/)).toBeHidden();
});

test("two perfumes in one line get a section each", async ({ page }) => {
  await openApp(page);
  await search(page, "Dior Sauvage EDP - Creed Aventus EDP");

  await expect(page.getByRole("heading", { name: "Dior Sauvage EDP" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Creed Aventus EDP" })).toBeVisible();
});

test("the line is refused over the perfume limit before anything is scanned", async ({
  page,
}) => {
  await openApp(page);
  const line = Array.from({ length: 11 }, (_, i) => `Parfum ${i}`).join(" - ");
  await page.getByLabel("Aranacak parfümler").fill(line);

  await expect(searchButton(page)).toBeDisabled();
  await expect(page.getByText(/en fazla 10 parfüm aranabilir/)).toBeVisible();
});

test("a row opens the shop's own product page", async ({ page, context }) => {
  // The fixture shops have no real host behind them, so the new tab is served a
  // stub. Without it the tab would land on a DNS error and the URL the app
  // actually asked for would be lost.
  await context.route("**/urun/**", (route) =>
    route.fulfill({ status: 200, contentType: "text/html", body: "shop" }),
  );
  await openApp(page);
  await search(page, "Dior Sauvage EDP");

  const opened = context.waitForEvent("page");
  await page.getByRole("table").first().getByText(/Dekant 3 ml/).first().click();
  const shop = await opened;
  await shop.waitForLoadState();
  expect(shop.url()).toContain("/urun/dior-sauvage");
});
