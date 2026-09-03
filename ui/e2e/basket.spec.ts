// The basket journey, end to end: a row added from the results table, priced by
// both fixture shops, and the plan cards the real optimiser produced from it.
//
// The arithmetic here is the app's whole reason to exist, and it is the part a
// jsdom test can only check against numbers a test wrote itself. Here the
// subtotals, the shipping and the free-shipping gap all come from basket.py.

import type { Page } from "@playwright/test";
import { expect, test } from "@playwright/test";
import { clearBasket, openApp, search, tab } from "./helpers";

test.beforeEach(async ({ page, request }) => {
  await openApp(page);
  await clearBasket(page, request);
});

/** Search for one perfume, add its first row, and open the basket. */
async function addFirstRow(page: Page, query: string): Promise<void> {
  await search(page, query);
  await page
    .getByRole("table")
    .first()
    .getByRole("button", { name: "Sepete ekle" })
    .first()
    .click();
  await tab(page, "Sepet").click();
  await expect(page.locator("table.matrix")).toBeVisible();
}

test("a row added from the results table appears in the matrix priced by both shops", async ({
  page,
}) => {
  await addFirstRow(page, "Dior Sauvage EDP");

  const row = page.locator("table.matrix tbody tr").filter({ hasText: "Dior Sauvage" });
  await expect(row).toHaveCount(1);
  // Alfa 120 ₺ against Beta 135 ₺ for the 3 ml, so the mark belongs to Alfa.
  await expect(row.getByText("120 ₺")).toBeVisible();
  await expect(row.getByText("135 ₺")).toBeVisible();
  await expect(row.locator("td.cheap")).toContainText("120 ₺");
});

test("the single-shop plan quotes the shipping the profile charges", async ({
  page,
}) => {
  await addFirstRow(page, "Dior Sauvage EDP");

  const plan = page.locator(".plan-card").filter({ hasText: "Tek siteden" });
  // Beta posts for 15.00 ₺ flat and Alfa for 40.00 ₺ unless the order clears
  // 500.00 ₺, so one 3 ml decant is cheapest all in from Beta: 135 + 15.
  await expect(plan).toContainText("Beta Dekant");
  await expect(plan).toContainText("150.00 ₺");
});

test("the selected shop cart opens all of its product pages", async ({ page }) => {
  await addFirstRow(page, "Dior Sauvage EDP");
  await page.evaluate(() => {
    const opened: string[] = [];
    Object.defineProperty(window, "__openedProductPages", { value: opened });
    window.open = ((url?: string | URL) => {
      if (url !== undefined) opened.push(String(url));
      return null;
    }) as typeof window.open;
  });

  const plan = page.locator(".plan-card").filter({ hasText: "Tek siteden" });
  await plan.getByRole("button", { name: "Beta Dekant" }).click();
  const dialog = page.getByRole("dialog", { name: "Beta Dekant için sepet" });
  const openAll = dialog.getByRole("button", { name: "Tüm ürün sayfalarını aç" });
  await expect(dialog).toBeVisible();
  await expect(openAll).toBeVisible();
  const layout = await Promise.all([dialog.boundingBox(), openAll.boundingBox()]);
  expect(layout[0]).not.toBeNull();
  expect(layout[1]).not.toBeNull();
  expect(layout[1]!.x).toBeGreaterThanOrEqual(layout[0]!.x);
  expect(layout[1]!.x + layout[1]!.width).toBeLessThanOrEqual(
    layout[0]!.x + layout[0]!.width,
  );
  expect(layout[1]!.y + layout[1]!.height).toBeLessThanOrEqual(
    layout[0]!.y + layout[0]!.height,
  );
  await openAll.click();

  const opened = await page.evaluate(
    () => (window as Window & { __openedProductPages?: string[] }).__openedProductPages,
  );
  expect(opened).toEqual(["https://beta.example/urun/dior-sauvage-edp"]);
});

test("the gap to free shipping is offered as a number, not as a hint", async ({
  page,
}) => {
  // Alfa's threshold is 500.00 ₺, and it is the runner-up plan for this basket.
  // Saying how much more would clear it is a decision a shopper can act on;
  // saying "kargo bedava değil" is not.
  await addFirstRow(page, "Dior Sauvage EDP");

  await page.getByText("Diğer senaryolar").click();
  await expect(
    page.getByText(/380.00 ₺ daha eklerseniz kargo bedava/),
  ).toBeVisible();
});

test("the quantity stepper changes the column subtotals", async ({ page }) => {
  await addFirstRow(page, "Dior Sauvage EDP");

  const footer = page.locator("table.matrix tfoot");
  await expect(footer).toContainText("120 ₺");

  await page.getByLabel("artır").click();

  // Doubled below, unchanged above: the subtotal is the one number on this
  // screen that carries the quantity.
  await expect(footer).toContainText("240 ₺");
  const row = page.locator("table.matrix tbody tr").filter({ hasText: "Dior Sauvage" });
  await expect(row.getByText("120 ₺")).toBeVisible();
});

test("dropping the last one removes the line and offers it back", async ({ page }) => {
  await addFirstRow(page, "Dior Sauvage EDP");

  await page.getByLabel("sepetten çıkar").click();
  await expect(page.getByText("Sepet boş.")).toBeVisible();

  await page.getByRole("button", { name: "Geri al" }).click();
  await expect(
    page.locator("table.matrix tbody tr").filter({ hasText: "Dior Sauvage" }),
  ).toHaveCount(1);
});

test("two perfumes make the split plan a real comparison", async ({ page }) => {
  // Alfa is cheaper on Sauvage and Beta on Aventus, so the optimiser has an
  // actual choice to report rather than one shop that wins everything.
  await search(page, "Dior Sauvage EDP - Creed Aventus EDP");
  for (const perfume of ["Dior Sauvage", "Creed Aventus"]) {
    await page
      .getByRole("table")
      .filter({ hasText: perfume })
      .getByRole("button", { name: "Sepete ekle" })
      .first()
      .click();
  }

  await tab(page, "Sepet").click();
  const rows = page.locator("table.matrix tbody tr");
  await expect(rows.filter({ hasText: "Dior Sauvage" })).toHaveCount(1);
  await expect(rows.filter({ hasText: "Creed Aventus" })).toHaveCount(1);

  // Which plan wins is the optimiser's call; the point is that exactly one card
  // claims it, because two cards marked as the answer is not a comparison.
  await expect(page.locator(".plan-card.win")).toHaveCount(1);
});

test("the basket tab counts its lines from the first screen", async ({ page }) => {
  await search(page, "Dior Sauvage EDP");
  await page
    .getByRole("table")
    .first()
    .getByRole("button", { name: "Sepete ekle" })
    .first()
    .click();

  await expect(tab(page, "Sepet")).toContainText("1");
});

test("a line read today is not offered for refreshing", async ({ page }) => {
  // The prices were written by the scan a moment ago, so nothing could come
  // back different and the button must not invite the request.
  await addFirstRow(page, "Dior Sauvage EDP");

  const refresh = page.locator("button.refresh-button").first();
  await expect(refresh).toBeDisabled();
  await expect(refresh).toHaveAttribute("title", "Fiyatlar güncel");
});
