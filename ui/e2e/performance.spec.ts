import { expect, test } from "@playwright/test";
import type { CDPSession, Page } from "@playwright/test";
import {
  clearBasket,
  clearWishlist,
  openApp,
  performanceSnapshot,
  seedWishlist,
  tab,
  watchPageDiagnostics,
} from "./helpers";

async function waitForSettledAnimations(page: Page): Promise<void> {
  await expect
    .poll(() =>
      page.evaluate(() =>
        document.getAnimations().every((animation) => animation.playState === "finished"),
      ),
    )
    .toBe(true);
}

test.describe("navigation and wishlist rendering regressions", () => {
  test("keeps the navigation pill inside the tabs at supported viewports", async ({
    page,
    request,
  }) => {
    await page.setViewportSize({ width: 1280, height: 900 });
    await openApp(page);
    await seedWishlist(page, request, 100);

    for (const width of [900, 1280]) {
      await page.setViewportSize({ width, height: 800 });
      await tab(page, "Arama").click();
      await tab(page, "İstek listesi").click();
      await expect(page.locator("[data-wishlist-summary]")).toHaveCount(100);
      await expect
        .poll(async () =>
          page.locator("nav.tabs").evaluate((nav) => {
            const pill = nav.querySelector<HTMLElement>(".tab-pill");
            const active = nav.querySelector<HTMLElement>('.tab[aria-current="page"]');
            if (!pill || !active) return false;
            const pillBox = pill.getBoundingClientRect();
            const activeBox = active.getBoundingClientRect();
            return Math.abs(pillBox.left - activeBox.left) < 0.5;
          }),
        )
        .toBe(true);

      const geometry = await page.locator("nav.tabs").evaluate((nav) => {
        const navBox = nav.getBoundingClientRect();
        const pill = nav.querySelector<HTMLElement>(".tab-pill");
        const active = nav.querySelector<HTMLElement>('.tab[aria-current="page"]');
        if (!pill || !active) throw new Error("the active tab geometry is missing");
        const pillBox = pill.getBoundingClientRect();
        const activeBox = active.getBoundingClientRect();
        const style = getComputedStyle(pill);
        return {
          nav: { left: navBox.left, right: navBox.right, top: navBox.top, bottom: navBox.bottom },
          pill: {
            left: pillBox.left,
            right: pillBox.right,
            top: pillBox.top,
            bottom: pillBox.bottom,
            width: pillBox.width,
          },
          active: {
            left: activeBox.left,
            right: activeBox.right,
            width: activeBox.width,
          },
          transitionProperty: style.transitionProperty,
          transitionDuration: style.transitionDuration,
          willChange: style.willChange,
        };
      });

      expect(geometry.nav.left).toBeGreaterThanOrEqual(0);
      expect(geometry.nav.right).toBeLessThanOrEqual(width + 1);
      expect(geometry.pill.left).toBeGreaterThanOrEqual(geometry.nav.left);
      expect(geometry.pill.right).toBeLessThanOrEqual(geometry.nav.right);
      expect(geometry.pill.width).toBeCloseTo(geometry.active.width, 0);
      expect(geometry.pill.left).toBeCloseTo(geometry.active.left, 0);
      expect(geometry.pill.right).toBeCloseTo(geometry.active.right, 0);
      expect(geometry.pill.top).toBeGreaterThan(geometry.nav.top);
      expect(geometry.pill.bottom).toBeLessThan(geometry.nav.bottom);
      expect(geometry.transitionProperty).toBe("transform");
      expect(geometry.transitionDuration).toBe("0.25s");
      expect(geometry.willChange).toBe("transform");
    }

    await clearWishlist(page, request);
  });

  test("keeps warmed tab switches below the layout budget", async ({ page, request }) => {
    await page.setViewportSize({ width: 1280, height: 800 });
    await openApp(page);
    await clearBasket(page, request);
    await clearWishlist(page, request);
    await page.reload();
    await expect(tab(page, "Arama")).toBeVisible();
    const diagnostics = watchPageDiagnostics(page);
    let performanceClient: CDPSession | undefined;
    try {
      performanceClient = await page.context().newCDPSession(page);
      await performanceClient.send("Performance.enable");
    } catch {
      diagnostics.stop();
      test.skip(true, "Chromium CDP Performance domain is unavailable");
      return;
    }

    const switchTab = async (name: "Arama" | "İstek listesi" | "Sepet") => {
      await tab(page, name).click();
      await expect(tab(page, name)).toHaveAttribute("aria-current", "page");
      await waitForSettledAnimations(page);
    };

    try {
      // Warm the screen mounts and the browser's style/layout caches first.
      for (const name of ["İstek listesi", "Sepet", "Arama"] as const) {
        await switchTab(name);
      }

      const layoutDeltas: number[] = [];
      for (let index = 0; index < 10; index += 1) {
        const before = await performanceSnapshot(page, performanceClient);
        if (before.layoutCount === null) {
          test.skip(true, "Chromium CDP did not expose LayoutCount");
          return;
        }
        await switchTab(index % 2 === 0 ? "İstek listesi" : "Sepet");
        const after = await performanceSnapshot(page, performanceClient);
        if (after.layoutCount === null) {
          test.skip(true, "Chromium CDP did not expose LayoutCount");
          return;
        }
        const delta = after.layoutCount - before.layoutCount;
        expect(delta).toBeGreaterThanOrEqual(0);
        layoutDeltas.push(delta);
      }

      expect(layoutDeltas).toHaveLength(10);
      const averageLayoutDelta =
        layoutDeltas.reduce((total, delta) => total + delta, 0) / layoutDeltas.length;
      expect(averageLayoutDelta).toBeLessThanOrEqual(3);
      console.log(`tab layout deltas: ${JSON.stringify({ layoutDeltas, averageLayoutDelta })}`);
    } finally {
      diagnostics.stop();
      if (performanceClient !== undefined) await performanceClient.detach();
      await clearWishlist(page, request);
    }

    expect(diagnostics.consoleErrors).toEqual([]);
    expect(diagnostics.pageErrors).toEqual([]);
    expect(diagnostics.failedRequests).toEqual([]);
  });

  test("disables the navigation pill transition for reduced motion", async ({ page }, testInfo) => {
    await page.emulateMedia({ reducedMotion: "reduce" });
    await page.setViewportSize({ width: 1280, height: 800 });
    await openApp(page);
    const diagnostics = watchPageDiagnostics(page);

    try {
      const style = await page.locator(".tab-pill").evaluate((pill) => {
        const computed = getComputedStyle(pill);
        return {
          transitionProperty: computed.transitionProperty,
          transitionDuration: computed.transitionDuration,
          willChange: computed.willChange,
        };
      });
      expect(style.transitionProperty).toBe("none");
      expect(style.transitionDuration).toBe("0s");
      expect(style.willChange).toBe("transform");
      const screenshotPath = testInfo.outputPath("reduced-motion.png");
      await page.screenshot({ path: screenshotPath, fullPage: false });
      await testInfo.attach("reduced-motion", {
        path: screenshotPath,
        contentType: "image/png",
      });
    } finally {
      diagnostics.stop();
    }
    expect(diagnostics.consoleErrors).toEqual([]);
    expect(diagnostics.pageErrors).toEqual([]);
    expect(diagnostics.failedRequests).toEqual([]);
  });

  test("records 100 and 500 wishlist metrics without retaining collapsed details", async ({
    page,
    request,
  }, testInfo) => {
    await page.setViewportSize({ width: 1280, height: 800 });
    await openApp(page);
    await clearBasket(page, request);
    const diagnostics = watchPageDiagnostics(page);
    let performanceClient: CDPSession | undefined;
    try {
      performanceClient = await page.context().newCDPSession(page);
      await performanceClient.send("Performance.enable");
    } catch {
      performanceClient = undefined;
    }
    const metrics: {
      count: number;
      before: Awaited<ReturnType<typeof performanceSnapshot>>;
      afterExpand: Awaited<ReturnType<typeof performanceSnapshot>>;
      afterCollapse: Awaited<ReturnType<typeof performanceSnapshot>>;
      expandMilliseconds: number;
      basketMilliseconds: number;
    }[] = [];

    try {
      for (const count of [100, 500]) {
        await seedWishlist(page, request, count);
        await tab(page, "İstek listesi").click();
        const summaries = page.locator("[data-wishlist-summary]");
        await expect(summaries).toHaveCount(count);

        const before = await performanceSnapshot(page, performanceClient);
        const collapsedDetails = page.locator(
          '.wishlist-offers-row[data-open="false"] .t-acc-panel-inner',
        );
        await expect(collapsedDetails).toHaveCount(0);
        await waitForSettledAnimations(page);
        const screenshotPath = testInfo.outputPath(`wishlist-${count}-collapsed.png`);
        await page.screenshot({ path: screenshotPath, fullPage: false });
        await testInfo.attach(`wishlist-${count}-collapsed`, {
          path: screenshotPath,
          contentType: "image/png",
        });

        const expandStarted = Date.now();
        await summaries.first().click();
        await expect(page.locator('.wishlist-offers-row[data-open="true"]')).toHaveCount(1);
        await expect
          .poll(() =>
            page.locator('.wishlist-offers-row[data-open="true"] .t-acc-panel-inner').evaluate(
              (panel) => panel.getBoundingClientRect().height > 0,
            ),
          )
          .toBe(true);
        await waitForSettledAnimations(page);
        const expandMilliseconds = Date.now() - expandStarted;
        const afterExpand = await performanceSnapshot(page, performanceClient);
        expect(afterExpand.domNodeCount).toBeGreaterThan(before.domNodeCount);
        expect(expandMilliseconds).toBeLessThan(5_000);
        const expandedScreenshotPath = testInfo.outputPath(`wishlist-${count}-expanded.png`);
        await page.screenshot({ path: expandedScreenshotPath, fullPage: false });
        await testInfo.attach(`wishlist-${count}-expanded`, {
          path: expandedScreenshotPath,
          contentType: "image/png",
        });

        await summaries.first().click();
        await expect(collapsedDetails).toHaveCount(0);
        const afterCollapse = await performanceSnapshot(page, performanceClient);

        const basketStarted = Date.now();
        await tab(page, "Sepet").click();
        await expect(page.getByText("Sepet boş.")).toBeVisible();
        await waitForSettledAnimations(page);
        const basketMilliseconds = Date.now() - basketStarted;
        expect(basketMilliseconds).toBeLessThan(5_000);
        const basketScreenshotPath = testInfo.outputPath(`wishlist-${count}-basket.png`);
        await page.screenshot({ path: basketScreenshotPath, fullPage: false });
        await testInfo.attach(`wishlist-${count}-basket`, {
          path: basketScreenshotPath,
          contentType: "image/png",
        });

        metrics.push({
          count,
          before,
          afterExpand,
          afterCollapse,
          expandMilliseconds,
          basketMilliseconds,
        });
      }
    } finally {
      diagnostics.stop();
      if (performanceClient !== undefined) await performanceClient.detach();
      await clearWishlist(page, request);
    }

    expect(diagnostics.consoleErrors).toEqual([]);
    expect(diagnostics.pageErrors).toEqual([]);
    expect(diagnostics.failedRequests).toEqual([]);
    const wishlistRequests = diagnostics.requests.filter(
      (url) => new URL(url).pathname === "/api/wishlist",
    );
    expect(wishlistRequests.length).toBeGreaterThanOrEqual(2);
    console.log(`wishlist metrics: ${JSON.stringify(metrics)}`);
  });

  test("shows the cached stale-row refresh warning", async ({ page, request }, testInfo) => {
    await page.setViewportSize({ width: 1280, height: 800 });
    await openApp(page);
    const diagnostics = watchPageDiagnostics(page);

    try {
      await seedWishlist(page, request, 1, { ageDays: 30 });
      await tab(page, "İstek listesi").click();
      const row = page.locator("[data-wishlist-summary]").first();
      await expect(row.locator(".badge.stale")).toContainText(/hafta|gün|ay/);
      const refresh = row.locator("button.refresh-button");
      await expect(refresh).toBeEnabled();
      await expect(refresh).toHaveAttribute("title", "Bu satırın fiyatlarını yenile");
      await waitForSettledAnimations(page);
      const screenshotPath = testInfo.outputPath("wishlist-stale-refresh.png");
      await page.screenshot({ path: screenshotPath, fullPage: false });
      await testInfo.attach("wishlist-stale-refresh", {
        path: screenshotPath,
        contentType: "image/png",
      });
    } finally {
      diagnostics.stop();
      await clearWishlist(page, request);
    }

    expect(diagnostics.consoleErrors).toEqual([]);
    expect(diagnostics.pageErrors).toEqual([]);
    expect(diagnostics.failedRequests).toEqual([]);
    expect(
      diagnostics.requests.some((url) => new URL(url).pathname === "/api/wishlist"),
    ).toBe(true);
  });

  test("keeps a cached basket visible when its background refresh fails", async ({
    page,
    request,
  }, testInfo) => {
    await page.setViewportSize({ width: 1280, height: 800 });
    await openApp(page);
    await clearBasket(page, request);
    await page.reload();
    await expect(tab(page, "Arama")).toBeVisible();
    await tab(page, "Sepet").click();
    await expect(page.getByText("Sepet boş.")).toBeVisible();
    await tab(page, "Arama").click();

    const diagnostics = watchPageDiagnostics(page);
    const basketPattern = "**/api/basket";
    await page.route(basketPattern, async (route) => {
      await route.fulfill({
        status: 503,
        contentType: "application/json",
        body: JSON.stringify({ detail: "ölçüm için yenileme hatası" }),
      });
    });

    try {
      await tab(page, "Sepet").click();
      await expect(page.getByText("Sepet boş.")).toBeVisible();
      await expect(page.getByText(/Sepet güncellenemedi: ölçüm için yenileme hatası/)).toBeVisible();
      await expect(page.getByRole("button", { name: "Tekrar dene" })).toBeVisible();
      await waitForSettledAnimations(page);
      const screenshotPath = testInfo.outputPath("basket-stale-refresh.png");
      await page.screenshot({ path: screenshotPath, fullPage: false });
      await testInfo.attach("basket-stale-refresh", {
        path: screenshotPath,
        contentType: "image/png",
      });
    } finally {
      diagnostics.stop();
      await page.unroute(basketPattern);
    }

    expect(diagnostics.consoleErrors).toEqual([
      expect.stringContaining("503 (Service Unavailable)"),
    ]);
    expect(diagnostics.pageErrors).toEqual([]);
    expect(diagnostics.failedRequests).toEqual([]);
  });
});
