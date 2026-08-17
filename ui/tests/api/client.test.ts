// The one place a request is built and an error is read. What matters here is
// that the status code survives: the results screen tells a 409 (needs
// confirming) from a 422 (cannot be added at all) by nothing else.

import { beforeEach, describe, expect, it } from "vitest";
import { ApiError, api, authToken } from "../../src/api/client";
import { installFakeServer, searchStart, type FakeServer } from "../helpers/server";

let server: FakeServer;

beforeEach(() => {
  server = installFakeServer();
  window.__PARFUM_TOKEN__ = "test-token";
});

describe("authToken", () => {
  it("prefers the token the packaged window injected", () => {
    // The shipped app generates a random token per process and puts it on the
    // window; the Vite env var is only the development stand-in.
    expect(authToken()).toBe("test-token");
  });
});

describe("request", () => {
  it("sends the token on every call", async () => {
    await api.config();
    const [request] = server.requestsTo("GET", "/api/config");
    expect(request?.headers["X-Auth-Token"]).toBe("test-token");
  });

  it("declares a JSON body only when it is sending one", async () => {
    server.reply("POST /api/search", searchStart(["Dior Sauvage EDP"]));
    await api.startSearch("Dior Sauvage EDP", false);
    const [post] = server.requestsTo("POST", "/api/search");
    expect(post?.headers["Content-Type"]).toBe("application/json");
    expect(post?.body).toEqual({ query: "Dior Sauvage EDP", force: false });

    const [get] = server.requestsTo("GET", "/api/config");
    expect(get).toBeUndefined();
  });

  it("puts the sort on the query string, and omits it for the default order", async () => {
    // No sort means the grouped order ranking.py produces, which is not one of
    // the three column sorts. Sending sort= for it would ask for a fourth.
    server.on("GET /api/results/:searchId", ({ query }) => ({
      body: { rows: [], hidden_out_of_stock: 0, finished: true, sort: query.get("sort") },
    }));
    await api.results("search-1", "per_ml");
    await api.results("search-1", null);
    expect(server.requestsTo("GET", "/api/results/search-1")).toHaveLength(2);
  });

  it("keeps the status code on a failure", async () => {
    server.reply("POST /api/basket/items", { detail: "needs confirming" }, 409);
    const failure = await api
      .addBasketItem({
        brand: "Dior",
        name: "Sauvage",
        concentration: "EDP",
        size_ml_x10: 50,
        qty: 1,
        own_identity: true,
        clone_of: "",
        confident: false,
        confirmed: false,
      })
      .catch((e: unknown) => e);
    expect(failure).toBeInstanceOf(ApiError);
    expect((failure as ApiError).status).toBe(409);
    expect((failure as ApiError).message).toBe("needs confirming");
  });

  it("reads a validation error's list of field problems as text", async () => {
    // FastAPI puts a string in "detail" for an HTTPException and a list of
    // objects there for a 422. Neither may be shown as "[object Object]".
    server.reply("POST /api/basket/items", { detail: [{ loc: ["body", "qty"] }] }, 422);
    const failure = (await api
      .addBasketItem({
        brand: "Dior",
        name: "Sauvage",
        concentration: "EDP",
        size_ml_x10: 50,
        qty: 0,
        own_identity: true,
        clone_of: "",
        confident: true,
        confirmed: false,
      })
      .catch((e: unknown) => e)) as ApiError;
    expect(failure.message).toContain("qty");
  });

  it("falls back to the status line when the failure is not JSON at all", async () => {
    // Something upstream of the app failing means no "detail" shape arrives,
    // and an empty error message would tell the user nothing.
    server.on("GET /api/basket", () => ({ status: 502 }));
    const failure = (await api.basket().catch((e: unknown) => e)) as ApiError;
    expect(failure.status).toBe(502);
    expect(failure.message).toContain("502");
  });

  it("returns nothing for a 204 instead of trying to parse an empty body", async () => {
    // DELETE answers 204. Parsing that as JSON throws, and the caller would
    // report a removal that actually succeeded as a failure.
    server.on("DELETE /api/basket/items/:id", () => ({ status: 204 }));
    await expect(api.removeBasketItem(7)).resolves.toBeUndefined();
  });
});
