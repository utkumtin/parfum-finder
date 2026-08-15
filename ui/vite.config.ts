import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

// The backend is proxied rather than called across origins. Same-origin in dev
// means the request base URL is "" here and "" again in the packaged app, where
// FastAPI serves this build itself, so nothing about the client has to know
// which of the two it is running in. It also keeps the backend free of CORS
// middleware, which would be a permission the shipped app never wants.
//
// ws: true matters as much as the HTTP side: the search and basket refresh
// streams are WebSockets, and without it the upgrade request is proxied as a
// plain GET and the socket never opens.
const BACKEND = "http://127.0.0.1:8000";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: BACKEND,
        changeOrigin: true,
        ws: true,
      },
    },
  },
  build: {
    outDir: "dist",
    emptyOutDir: true,
  },
});
