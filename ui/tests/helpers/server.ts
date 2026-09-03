// A stand-in for the backend, at the two seams the frontend actually has: the
// global `fetch` every call in api/client.ts goes through, and the global
// `WebSocket` api/ws.ts opens.
//
// Faked here rather than with a request-interception library because those two
// seams are the whole surface. What a test needs beyond a canned answer is to
// decide *when* an event arrives -- a scan that finishes before the table is
// read is not the sequence the bugs live in -- and that means holding the
// socket, not describing it.

import { vi } from "vitest";
import type {
  AppConfig,
  BasketResponse,
  RecentSearch,
  ResultsResponse,
  SearchStart,
  SiteSummary,
  UpdateInfo,
  UpdateProgress,
  WishlistResponse,
} from "../../src/types";

export interface RecordedRequest {
  method: string;
  path: string;
  /** The query string as sent, since the sort is only visible there. */
  search: string;
  /** The parsed JSON body, or undefined for a request that carried none. */
  body: unknown;
  headers: Record<string, string>;
}

/** What a route answers with. A bare object is a 200 carrying that object. */
export interface Reply {
  status?: number;
  body?: unknown;
}

export interface RouteRequest extends RecordedRequest {
  /** The `:name` pieces of the route pattern, as strings. */
  params: Record<string, string>;
  /** The query string, without the leading "?". */
  query: URLSearchParams;
}

export type RouteHandler = (request: RouteRequest) => Reply | Promise<Reply>;

interface Route {
  method: string;
  pattern: string;
  matcher: RegExp;
  names: string[];
  handler: RouteHandler;
}

function compile(pattern: string): { matcher: RegExp; names: string[] } {
  const names: string[] = [];
  const source = pattern.replace(/:([A-Za-z_]+)/g, (_all, name: string) => {
    names.push(name);
    return "([^/]+)";
  });
  return { matcher: new RegExp(`^${source}$`), names };
}

/**
 * The default answers: a working backend with nothing in it.
 *
 * Every screen reads several of these on mount, and a test about one of them
 * should not have to describe the others. The numbers match
 * src/parfum_finder/matcher.py and store.py, since /api/config is where the
 * frontend gets them from for real.
 */
export const DEFAULT_CONFIG: AppConfig = {
  stale_price_days: 14,
  max_queries: 10,
  query_separator_pattern: "\\s+-\\s+|,|;|\\n",
};

export const DEFAULT_SITES: SiteSummary[] = [
  {
    id: "site-a",
    name: "Alfa Dekant",
    enabled: true,
    needs_review: false,
    discovered_at: "2026-08-01T00:00:00Z",
  },
];

export const EMPTY_BASKET: BasketResponse = {
  rows: [],
  report: { full: [], partial: [], unavailable: [] },
  best_combination: null,
};

export const NO_UPDATE: UpdateInfo = {
  current_version: "0.1.0",
  latest_version: "0.1.0",
  update_available: false,
  notes: "",
  release_url: "https://example.com/releases",
  download_url: null,
};

export class FakeServer {
  readonly requests: RecordedRequest[] = [];
  readonly sockets: FakeWebSocket[] = [];
  private readonly routes: Route[] = [];

  /**
   * Register (or replace) one route.
   *
   * The newest matching route wins, so a test overrides a default by naming
   * the same method and pattern again.
   */
  on(spec: string, handler: RouteHandler): this {
    const [method, pattern] = spec.split(" ", 2);
    if (method === undefined || pattern === undefined) {
      throw new Error(`route needs a method and a path, got "${spec}"`);
    }
    const { matcher, names } = compile(pattern);
    this.routes.unshift({ method, pattern, matcher, names, handler });
    return this;
  }

  /** Answer this route with a canned body, the common case. */
  reply(spec: string, body: unknown, status = 200): this {
    return this.on(spec, () => ({ status, body }));
  }

  /** The requests made to one route so far, oldest first. */
  requestsTo(method: string, path: string): RecordedRequest[] {
    return this.requests.filter((r) => r.method === method && r.path === path);
  }

  /**
   * The socket opened for `path`, once one has been.
   *
   * Streams open inside an effect, so a test that asks for the socket in the
   * same tick as the click that starts it finds nothing. Await this instead of
   * sleeping.
   */
  async socket(path: string): Promise<FakeWebSocket> {
    for (let attempt = 0; attempt < 100; attempt += 1) {
      const found = this.sockets.find((s) => s.path === path);
      if (found !== undefined) return found;
      await new Promise((resolve) => setTimeout(resolve, 5));
    }
    const opened = this.sockets.map((s) => s.path).join(", ") || "none";
    throw new Error(`no socket opened for ${path} (opened: ${opened})`);
  }

  async handle(input: string, init: RequestInit): Promise<Response> {
    const method = (init.method ?? "GET").toUpperCase();
    const url = new URL(input, window.location.origin);
    const body =
      typeof init.body === "string" ? (JSON.parse(init.body) as unknown) : undefined;
    const headers = (init.headers ?? {}) as Record<string, string>;
    this.requests.push({
      method,
      path: url.pathname,
      search: url.search,
      body,
      headers,
    });

    for (const route of this.routes) {
      if (route.method !== method) continue;
      const match = route.matcher.exec(url.pathname);
      if (match === null) continue;
      const params: Record<string, string> = {};
      route.names.forEach((name, i) => {
        params[name] = match[i + 1] ?? "";
      });
      const reply = await route.handler({
        method,
        path: url.pathname,
        search: url.search,
        body,
        headers,
        params,
        query: url.searchParams,
      });
      const status = reply.status ?? 200;
      if (status === 204 || reply.body === undefined) {
        return new Response(null, { status });
      }
      return new Response(JSON.stringify(reply.body), {
        status,
        headers: { "Content-Type": "application/json" },
      });
    }
    // Loud on purpose: a screen quietly reading an endpoint nobody described
    // is exactly the mismatch these tests exist to catch, and a 404 here would
    // be swallowed by the "this failure stays quiet" catch blocks.
    throw new Error(`no fake route for ${method} ${url.pathname}`);
  }
}

/**
 * One socket the app opened, held so the test can drive it.
 *
 * `emit` and `refuse` are the test's half; everything else is the surface
 * api/ws.ts uses.
 */
export class FakeWebSocket {
  static readonly OPEN = 1;
  static readonly CLOSED = 3;

  readyState = FakeWebSocket.OPEN;
  onmessage: ((event: { data: string }) => void) | null = null;
  onclose: ((event: { code: number }) => void) | null = null;
  onopen: (() => void) | null = null;
  onerror: (() => void) | null = null;

  /** The path without the token query string, which is what tests match on. */
  readonly path: string;
  /** The token the app put on the URL. */
  readonly token: string;
  closedByClient = false;

  constructor(readonly url: string) {
    const parsed = new URL(url.replace(/^ws/, "http"));
    this.path = parsed.pathname;
    this.token = parsed.searchParams.get("token") ?? "";
  }

  /** The app closing the socket: the screen was left, or unmounted. */
  close(code = 1000): void {
    if (this.readyState === FakeWebSocket.CLOSED) return;
    this.readyState = FakeWebSocket.CLOSED;
    this.closedByClient = true;
    this.onclose?.({ code });
  }

  /** One event down the wire, in the shape the backend sends it. */
  emit(event: unknown): void {
    this.onmessage?.({ data: JSON.stringify(event) });
  }

  /** The backend refusing the socket: 4401, 4404 or 4409. */
  refuse(code: number): void {
    this.readyState = FakeWebSocket.CLOSED;
    this.onclose?.({ code });
  }
}

/**
 * Put the fake backend in place for one test, with the defaults every screen
 * reads on mount already answered.
 *
 * `vi.stubGlobal` is undone by vitest between tests, so nothing has to be
 * restored by hand.
 */
export function installFakeServer(): FakeServer {
  const server = new FakeServer();

  server
    .reply("GET /api/config", DEFAULT_CONFIG)
    .reply("GET /api/sites", DEFAULT_SITES)
    .reply("GET /api/searches/recent", [] satisfies RecentSearch[])
    .reply("GET /api/wishlist", { rows: [] } satisfies WishlistResponse)
    .reply("PUT /api/wishlist/items", undefined, 204)
    .reply("DELETE /api/wishlist/items", undefined, 204)
    .reply("GET /api/basket", EMPTY_BASKET)
    .reply("GET /api/update", NO_UPDATE)
    .reply("GET /api/results/:searchId", {
      rows: [],
      hidden_out_of_stock: 0,
      finished: true,
    } satisfies ResultsResponse);

  server.sockets.length = 0;
  vi.stubGlobal("fetch", (input: string, init: RequestInit = {}) =>
    server.handle(input, init),
  );
  vi.stubGlobal(
    "WebSocket",
    class extends FakeWebSocket {
      constructor(url: string) {
        super(url);
        server.sockets.push(this);
      }
    },
  );
  return server;
}

/** A started search, as POST /api/search answers it. */
export function searchStart(
  texts: string[],
  overrides: Partial<SearchStart> = {},
): SearchStart {
  return {
    search_id: "search-1",
    rejected: [],
    searches: texts.map((text, index) => ({ index, text })),
    ...overrides,
  };
}

export function updateProgress(
  overrides: Partial<UpdateProgress> = {},
): UpdateProgress {
  return { state: "idle", received: 0, total: 0, message: "", ...overrides };
}
