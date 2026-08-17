import { defineConfig, mergeConfig } from "vitest/config";
import viteConfig from "./vite.config";

// Merged into the build config rather than written out again, so the react
// plugin and everything else the app is compiled with is the same here as it
// is in `npm run build`. A second standalone config is how a test suite starts
// passing against a transform the shipped bundle never used.
//
// The e2e directory is excluded: those specs are driven by playwright against
// a real browser and a real backend, and vitest picking them up would run
// them in jsdom with no page to talk to.
export default mergeConfig(
  viteConfig,
  defineConfig({
    test: {
      environment: "jsdom",
      setupFiles: ["./tests/setup.ts"],
      include: ["tests/**/*.test.{ts,tsx}"],
      restoreMocks: true,
      coverage: {
        include: ["src/**/*.{ts,tsx}"],
        // Nothing to assert about: the mount point and the stylesheet.
        exclude: ["src/main.tsx"],
        reporter: ["text"],
      },
    },
  }),
);
