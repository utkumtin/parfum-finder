import { defineConfig, devices } from "@playwright/test";

// The frontend is built and then served by the backend itself, which is how the
// packaged Windows app serves it too: one origin, no dev-server proxy, and the
// auth token already on the page. A test driving the Vite dev server instead
// would be exercising a setup that never ships.
//
// Chromium stands in for WebView2. It is not the same engine build, but it is
// the same one Edge is, and it is what a Linux CI runner can install.
const PORT = 8765;

// tsc is configured for the browser here (types: ["vite/client"]), so node's
// globals are not declared. Declaring the one thing this file reads keeps it
// that way: pulling in @types/node would put `process` on src/'s global type
// too, where nothing may use it.
declare const process: { env: Record<string, string | undefined> };
const CI = process.env.CI !== undefined;

export default defineConfig({
  testDir: "./e2e",
  // Serial: every spec shares the one backend process and the one basket
  // inside it, and two workers adding lines at once would each be asserting
  // against the other's rows.
  workers: 1,
  fullyParallel: false,
  forbidOnly: CI,
  retries: CI ? 1 : 0,
  reporter: CI ? "line" : "list",
  timeout: 30_000,
  use: {
    baseURL: `http://127.0.0.1:${PORT}`,
    trace: "retain-on-failure",
  },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
  webServer: {
    // Built here rather than assumed: a stale dist is a suite that passes
    // against the previous version of the screen it is testing.
    command: "npm run build && uv run --extra gui python e2e/backend.py",
    url: `http://127.0.0.1:${PORT}/`,
    reuseExistingServer: false,
    timeout: 120_000,
    stdout: "pipe",
    stderr: "pipe",
    env: { PARFUM_FINDER_E2E_PORT: String(PORT) },
  },
});
