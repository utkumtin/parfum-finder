// Runs before every test file. Three jobs: the DOM matchers, tearing the
// rendered tree down between tests, and filling the handful of holes jsdom
// leaves that this app walks into on mount.

import "@testing-library/jest-dom/vitest";

import { cleanup } from "@testing-library/react";
import { afterEach, beforeEach, vi } from "vitest";

// Registered by hand because the suite runs without vitest's globals: the
// automatic teardown testing-library ships only fires when it can find a
// global afterEach, and without it every test would render into the DOM the
// previous one left behind.
afterEach(() => {
  cleanup();
});

// motion reads the reduced-motion preference the moment a motion component
// mounts, and jsdom has no matchMedia at all. Answering "no preference" is the
// same answer a normal desktop gives.
if (!("matchMedia" in window)) {
  Object.defineProperty(window, "matchMedia", {
    writable: true,
    value: (query: string): MediaQueryList =>
      ({
        matches: false,
        media: query,
        onchange: null,
        addEventListener: () => {},
        removeEventListener: () => {},
        addListener: () => {},
        removeListener: () => {},
        dispatchEvent: () => false,
      }) as unknown as MediaQueryList,
  });
}

// A results row opens the shop in a new tab. jsdom's own window.open prints a
// "not implemented" error to the console for every click, which buries the
// output a failing test needs; tests that care assert on this spy instead.
// Re-installed per test rather than once per file, because restoreMocks puts
// the original back after each one.
beforeEach(() => {
  vi.spyOn(window, "open").mockImplementation(() => null);
});
