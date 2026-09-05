import { expect, test } from "@playwright/test";
import type { CDPSession, Page } from "@playwright/test";
import {
  clearBasket,
  clearWishlist,
  openApp,
  performanceSnapshot,
  search,
  seedWishlist,
  tab,
  watchPageDiagnostics,
} from "./helpers";

type TabName = "Arama" | "Sonuçlar" | "İstek listesi" | "Sepet";

type PillBox = {
  left: number;
  top: number;
  width: number;
  height: number;
};

type PillTransitionTrace = {
  from: PillBox;
  destination: PillBox;
  samples: PillBox[];
};

async function waitForSettledAnimations(page: Page): Promise<void> {
  await expect
    .poll(() =>
      page.evaluate(() =>
        document.getAnimations().every((animation) => animation.playState === "finished"),
      ),
    )
    .toBe(true);
}

async function tracePillTransition(
  page: Page,
  destinationName: Exclude<TabName, "Sonuçlar">,
): Promise<PillTransitionTrace> {
  return page.evaluate(async (name) => {
    const nav = document.querySelector("nav.tabs");
    const pill = nav?.querySelector<HTMLElement>(".tab-pill");
    const destinationButton = [...(nav?.querySelectorAll<HTMLButtonElement>("button.tab") ?? [])].find(
      (button) =>
        button.getAttribute("aria-label") === name || button.textContent?.includes(name) === true,
    );
    if (nav === null || pill === null || pill === undefined || destinationButton === undefined)
      throw new Error("the destination tab geometry is missing");

    const box = (element: HTMLElement): PillBox => {
      const rect = element.getBoundingClientRect();
      return { left: rect.left, top: rect.top, width: rect.width, height: rect.height };
    };
    const from = box(pill);
    const destination = box(destinationButton);
    destinationButton.click();

    // Let React commit the new active tab, then freeze the CSS transitions and
    // sample them at normalized progress values. This keeps the regression
    // independent of elapsed wall time and captures the initial rendered frame.
    await new Promise<void>((resolve) => requestAnimationFrame(() => resolve()));
    void pill.offsetWidth;
    const transitions = pill
      .getAnimations()
      .filter((animation) => "transitionProperty" in animation)
      .filter((animation) => {
        const propertyName = (animation as Animation & { transitionProperty?: string })
          .transitionProperty;
        return propertyName === "transform" || propertyName === "width";
      });
    if (transitions.length === 0) throw new Error("the pill has no position/width transition");
    for (const animation of transitions) animation.pause();
    const duration = Math.max(
      1,
      ...transitions.map((animation) => {
        const timing = animation.effect?.getComputedTiming();
        return typeof timing?.duration === "number" ? timing.duration : 1;
      }),
    );
    const samples: PillBox[] = [];
    for (const progress of [0, 0.1, 0.25, 0.5, 0.75, 1]) {
      for (const animation of transitions) animation.currentTime = duration * progress;
      samples.push(box(pill));
    }
    for (const animation of transitions) {
      animation.currentTime = duration;
      animation.play();
    }
    return { from, destination, samples };
  }, destinationName);
}

function assertContinuousPillTransition(trace: PillTransitionTrace): void {
  expect(trace.samples.length).toBeGreaterThanOrEqual(6);
  const first = trace.samples[0]!;
  const last = trace.samples[trace.samples.length - 1]!;
  const widthDelta = Math.abs(trace.destination.width - trace.from.width);
  const leftDelta = Math.abs(trace.destination.left - trace.from.left);
  expect(widthDelta).toBeGreaterThan(1);
  expect(leftDelta).toBeGreaterThan(1);

  // The first rendered frame must still be near the departing geometry. This
  // catches the old width snap while allowing one frame of interpolation.
  expect(Math.abs(first.width - trace.from.width)).toBeLessThanOrEqual(
    Math.max(2, widthDelta * 0.2),
  );
  expect(Math.abs(first.left - trace.from.left)).toBeLessThanOrEqual(
    Math.max(2, leftDelta * 0.2),
  );

  const widthMin = Math.min(trace.from.width, trace.destination.width) - 2;
  const widthMax = Math.max(trace.from.width, trace.destination.width) + 2;
  const leftMin = Math.min(trace.from.left, trace.destination.left) - 2;
  const leftMax = Math.max(trace.from.left, trace.destination.left) + 2;
  const widthDirection = Math.sign(trace.destination.width - trace.from.width);
  const leftDirection = Math.sign(trace.destination.left - trace.from.left);
  for (let index = 0; index < trace.samples.length; index += 1) {
    const sample = trace.samples[index]!;
    expect(sample.width).toBeGreaterThanOrEqual(widthMin);
    expect(sample.width).toBeLessThanOrEqual(widthMax);
    expect(sample.left).toBeGreaterThanOrEqual(leftMin);
    expect(sample.left).toBeLessThanOrEqual(leftMax);
    if (index > 0) {
      const previous = trace.samples[index - 1]!;
      expect((sample.width - previous.width) * widthDirection).toBeGreaterThanOrEqual(-1.5);
      expect((sample.left - previous.left) * leftDirection).toBeGreaterThanOrEqual(-1.5);
    }
  }

  expect(last.width).toBeCloseTo(trace.destination.width, 0);
  expect(last.left).toBeCloseTo(trace.destination.left, 0);
}

async function traceRapidReversals(page: Page): Promise<{
  origins: PillBox[];
  destinations: PillBox[];
  afterClicks: PillBox[];
}> {
  return page.evaluate(async () => {
    const nav = document.querySelector("nav.tabs");
    const pill = nav?.querySelector<HTMLElement>(".tab-pill");
    if (nav === null || pill === null || pill === undefined)
      throw new Error("the navigation pill is unavailable for reversal sampling");
    const targets = ["İstek listesi", "Sepet", "İstek listesi", "Sepet"];
    const origins: PillBox[] = [];
    const destinations: PillBox[] = [];
    const afterClicks: PillBox[] = [];
    const box = (element: HTMLElement): PillBox => {
      const rect = element.getBoundingClientRect();
      return { left: rect.left, top: rect.top, width: rect.width, height: rect.height };
    };
    const frame = () => new Promise<void>((resolve) => requestAnimationFrame(() => resolve()));
    const transitionsForPill = () =>
      pill
        .getAnimations()
        .filter((animation) => "transitionProperty" in animation)
        .filter((animation) => {
          const propertyName = (animation as Animation & { transitionProperty?: string })
            .transitionProperty;
          return propertyName === "transform" || propertyName === "width";
        });
    const durationFor = (animation: Animation): number => {
      const timing = animation.effect?.getComputedTiming();
      return typeof timing?.duration === "number" ? timing.duration : 1;
    };
    const findTab = (name: string): HTMLButtonElement | undefined =>
      [...nav.querySelectorAll<HTMLButtonElement>("button.tab")].find(
        (button) =>
          button.getAttribute("aria-label") === name || button.textContent?.includes(name) === true,
      );

    for (const [index, name] of targets.entries()) {
      const target = findTab(name);
      if (target === undefined) throw new Error(`missing reversal target ${name}`);
      origins.push(box(pill));
      destinations.push(box(target));
      target.click();
      await frame();
      void pill.offsetWidth;
      const transitions = transitionsForPill();
      if (transitions.length === 0) throw new Error("the reversal has no pill transition");
      const duration = Math.max(...transitions.map(durationFor));
      for (const animation of transitions) {
        animation.pause();
        animation.currentTime = 0;
      }
      afterClicks.push(box(pill));

      // Leave the pill part-way through this transition before the next click.
      // The next iteration then verifies that its new transition starts from
      // this rendered frame instead of snapping to either tab.
      if (index < targets.length - 1) {
        for (const animation of transitions) {
          animation.currentTime = duration * 0.5;
          animation.play();
        }
      } else {
        for (const animation of transitions) {
          animation.currentTime = duration;
          animation.play();
        }
      }
    }
    return { origins, destinations, afterClicks };
  });
}

function assertRapidReversalContinuity(trace: {
  origins: PillBox[];
  destinations: PillBox[];
  afterClicks: PillBox[];
}): void {
  expect(trace.origins).toHaveLength(4);
  expect(trace.destinations).toHaveLength(4);
  expect(trace.afterClicks).toHaveLength(4);
  for (let index = 0; index < trace.origins.length; index += 1) {
    const origin = trace.origins[index]!;
    const destination = trace.destinations[index]!;
    const afterClick = trace.afterClicks[index]!;
    expect(Math.abs(destination.width - origin.width)).toBeGreaterThan(1);
    expect(Math.abs(afterClick.width - origin.width)).toBeLessThanOrEqual(
      Math.max(2, Math.abs(destination.width - origin.width) * 0.25),
    );
    expect(Math.abs(afterClick.left - origin.left)).toBeLessThanOrEqual(
      Math.max(2, Math.abs(destination.left - origin.left) * 0.25),
    );
  }
}

async function addFirstResultToBasket(page: Page): Promise<void> {
  await search(page, "Dior Sauvage EDP");
  await page
    .getByRole("table")
    .first()
    .getByRole("button", { name: "Sepete ekle" })
    .first()
    .click();
  await expect(tab(page, "Sepet")).toContainText("1");
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
      expect(Math.abs(geometry.pill.right - geometry.active.right)).toBeLessThanOrEqual(1);
      expect(geometry.pill.top).toBeGreaterThan(geometry.nav.top);
      expect(geometry.pill.bottom).toBeLessThan(geometry.nav.bottom);
      expect(geometry.transitionProperty.split(",").map((property) => property.trim())).toEqual(
        expect.arrayContaining(["transform", "width"]),
      );
      expect(geometry.transitionDuration.split(",").map((duration) => duration.trim())).toEqual(
        expect.arrayContaining(["0.25s"]),
      );
      expect(geometry.willChange).toBe("transform");
    }

    await clearWishlist(page, request);
  });

  test("keeps pill position and width continuous in every reported direction", async ({
    page,
    request,
  }) => {
    await page.setViewportSize({ width: 1280, height: 800 });
    await openApp(page);
    await clearBasket(page, request);
    await seedWishlist(page, request, 100);
    await addFirstResultToBasket(page);

    const directions: [Exclude<TabName, "Sonuçlar">, Exclude<TabName, "Sonuçlar">][] = [
      ["Arama", "İstek listesi"],
      ["İstek listesi", "Arama"],
      ["Arama", "Sepet"],
      ["Sepet", "Arama"],
      ["Arama", "İstek listesi"],
      ["İstek listesi", "Sepet"],
    ];

    try {
      for (const width of [900, 1280]) {
        await page.setViewportSize({ width, height: 800 });
        await tab(page, "Arama").click();
        await waitForSettledAnimations(page);
        for (const [from, destination] of directions) {
          await expect(tab(page, from)).toHaveAttribute("aria-current", "page");
          const trace = await tracePillTransition(page, destination);
          assertContinuousPillTransition(trace);
          await waitForSettledAnimations(page);
        }

        await tab(page, "Arama").click();
        await waitForSettledAnimations(page);
        const rapidTrace = await traceRapidReversals(page);
        assertRapidReversalContinuity(rapidTrace);
        await waitForSettledAnimations(page);
        await expect(tab(page, "Sepet")).toHaveAttribute("aria-current", "page");
      }
    } finally {
      await clearBasket(page, request);
      await clearWishlist(page, request);
    }
  });

  test("keeps empty and digit-changing wishlist counts measurable", async ({ page, request }) => {
    await page.setViewportSize({ width: 1280, height: 800 });
    await openApp(page);
    await clearBasket(page, request);

    try {
      await clearWishlist(page, request);
      await page.reload();
      await expect(page.getByRole("button", { name: "Ara", exact: true })).toBeVisible();
      await expect(tab(page, "İstek listesi")).not.toContainText(/\d/);
      await tab(page, "İstek listesi").click();
      await waitForSettledAnimations(page);

      for (const count of [9, 10, 99, 100]) {
        await seedWishlist(page, request, count);
        await expect(tab(page, "İstek listesi")).toContainText(String(count));
        const trace = await tracePillTransition(page, "İstek listesi");
        assertContinuousPillTransition(trace);
        await waitForSettledAnimations(page);
      }
    } finally {
      await clearWishlist(page, request);
    }
  });

  test("keeps keyboard-selected active tabs as the only hovered selection surface", async ({
    page,
    request,
  }) => {
    await page.setViewportSize({ width: 1280, height: 800 });
    await openApp(page);
    await clearBasket(page, request);
    await clearWishlist(page, request);
    await page.reload();
    await expect(page.getByRole("button", { name: "Ara", exact: true })).toBeVisible();

    try {
      const wishlistTab = tab(page, "İstek listesi");
      await wishlistTab.focus();
      await expect(wishlistTab).toBeFocused();
      await page.keyboard.press("Enter");
      await expect(wishlistTab).toHaveAttribute("aria-current", "page");

      const basketTab = tab(page, "Sepet");
      await basketTab.focus();
      await wishlistTab.hover();
      await basketTab.hover();
      await page.keyboard.press("Space");
      await expect(basketTab).toHaveAttribute("aria-current", "page");

      const background = await basketTab.evaluate(
        (element) => getComputedStyle(element).backgroundColor,
      );
      expect(background).toBe("rgba(0, 0, 0, 0)");
      await expect(page.locator(".tab-pill")).toBeVisible();
    } finally {
      await clearBasket(page, request);
      await clearWishlist(page, request);
    }
  });

  test("keeps warmed tab switches below the layout budget with reduced motion", async ({
    page,
    request,
  }) => {
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
      const normalMotionLayoutDeltas: number[] = [];
      for (const name of ["İstek listesi", "Sepet", "Arama"] as const) {
        await switchTab(name);
      }
      for (let index = 0; index < 4; index += 1) {
        const before = await performanceSnapshot(page, performanceClient);
        if (before.layoutCount === null) break;
        await switchTab(index % 2 === 0 ? "İstek listesi" : "Sepet");
        const after = await performanceSnapshot(page, performanceClient);
        if (after.layoutCount === null) break;
        const delta = after.layoutCount - before.layoutCount;
        expect(delta).toBeGreaterThanOrEqual(0);
        normalMotionLayoutDeltas.push(delta);
      }
      console.log(`normal-motion tab layout deltas: ${JSON.stringify(normalMotionLayoutDeltas)}`);

      await page.emulateMedia({ reducedMotion: "reduce" });
      await page.reload();
      await expect(tab(page, "Arama")).toBeVisible();

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

  test("keeps cached basket geometry stable during a slow background read", async ({
    page,
    request,
  }, testInfo) => {
    await page.setViewportSize({ width: 1280, height: 800 });
    await openApp(page);
    await clearBasket(page, request);
    await addFirstResultToBasket(page);
    await tab(page, "Sepet").click();
    const matrix = page.locator("table.matrix");
    await expect(matrix).toBeVisible();
    const baseline = await matrix.boundingBox();
    if (baseline === null) throw new Error("the cached basket matrix has no geometry");
    await tab(page, "Arama").click();

    let readStarted = false;
    let readSettled = false;
    let releaseResponse: () => void = () => {};
    const responseGate = new Promise<void>((resolve) => {
      releaseResponse = resolve;
    });
    const basketPattern = "**/api/basket";
    await page.route(basketPattern, async (route) => {
      readStarted = true;
      const response = await route.fetch();
      await responseGate;
      await route.fulfill({ response });
      readSettled = true;
    });
    const diagnostics = watchPageDiagnostics(page);

    try {
      await tab(page, "Sepet").click();
      await expect
        .poll(() => readStarted)
        .toBe(true);
      await expect(matrix).toBeVisible();
      await expect(page.getByRole("alert")).toHaveCount(0);
      const pending = await matrix.boundingBox();
      if (pending === null) throw new Error("the cached basket disappeared during revalidation");
      expect(Math.abs(pending.x - baseline.x)).toBeLessThanOrEqual(1);
      expect(Math.abs(pending.y - baseline.y)).toBeLessThanOrEqual(1);
      expect(Math.abs(pending.width - baseline.width)).toBeLessThanOrEqual(1);
      expect(Math.abs(pending.height - baseline.height)).toBeLessThanOrEqual(1);
      await waitForSettledAnimations(page);
      const screenshotPath = testInfo.outputPath("basket-cached-slow.png");
      await page.screenshot({ path: screenshotPath, fullPage: false });
      await testInfo.attach("basket-cached-slow", {
        path: screenshotPath,
        contentType: "image/png",
      });
      releaseResponse();
      await expect.poll(() => readSettled).toBe(true);
      await expect(matrix).toBeVisible();
      await expect(page.getByRole("alert")).toHaveCount(0);
      const settled = await matrix.boundingBox();
      if (settled === null) throw new Error("the basket matrix disappeared after revalidation");
      expect(Math.abs(settled.x - baseline.x)).toBeLessThanOrEqual(1);
      expect(Math.abs(settled.y - baseline.y)).toBeLessThanOrEqual(1);
      expect(Math.abs(settled.width - baseline.width)).toBeLessThanOrEqual(1);
      expect(Math.abs(settled.height - baseline.height)).toBeLessThanOrEqual(1);
    } finally {
      releaseResponse();
      if (readStarted) await expect.poll(() => readSettled).toBe(true);
      await page.unroute(basketPattern);
      diagnostics.stop();
      await clearBasket(page, request);
    }

    expect(diagnostics.consoleErrors).toEqual([]);
    expect(diagnostics.pageErrors).toEqual([]);
    expect(diagnostics.failedRequests).toEqual([]);
  });

  test("keeps a cached basket visible when its background refresh fails", async ({
    page,
    request,
  }, testInfo) => {
    await page.setViewportSize({ width: 1280, height: 800 });
    await openApp(page);
    await clearBasket(page, request);
    await addFirstResultToBasket(page);
    await tab(page, "Sepet").click();
    const matrix = page.locator("table.matrix");
    await expect(matrix).toBeVisible();
    await tab(page, "Arama").click();

    const diagnostics = watchPageDiagnostics(page);
    const basketPattern = "**/api/basket";
    let attempts = 0;
    await page.route(basketPattern, async (route) => {
      attempts += 1;
      if (attempts === 1) {
        await route.fulfill({
          status: 503,
          contentType: "application/json",
          body: JSON.stringify({ detail: "ölçüm için yenileme hatası" }),
        });
      } else await route.continue();
    });

    try {
      await tab(page, "Sepet").click();
      await expect(matrix).toBeVisible();
      await expect(page.getByText(/Sepet güncellenemedi: ölçüm için yenileme hatası/)).toBeVisible();
      await expect(page.getByRole("button", { name: "Tekrar dene" })).toBeVisible();
      await expect(matrix.locator(".matrix-name")).toContainText("dior sauvage");
      await page.getByRole("button", { name: "Tekrar dene" }).click();
      await expect(page.getByText(/Sepet güncellenemedi: ölçüm için yenileme hatası/)).toHaveCount(0);
      await expect(matrix).toBeVisible();
      await expect(matrix.locator(".matrix-name")).toContainText("dior sauvage");
      await expect.poll(() => attempts).toBeGreaterThanOrEqual(2);
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
      await clearBasket(page, request);
    }

    expect(diagnostics.consoleErrors).toEqual([
      expect.stringContaining("503 (Service Unavailable)"),
    ]);
    expect(diagnostics.pageErrors).toEqual([]);
    expect(diagnostics.failedRequests).toEqual([]);
  });
});
