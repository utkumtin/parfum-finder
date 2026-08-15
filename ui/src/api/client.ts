// Every call to the backend goes through here, so the token is attached in one
// place and an error carries its status code instead of collapsing into a
// string. The basket screen has to tell a 409 (needs confirming) from a 422
// (cannot be added at all), and it can only do that if the status survives.

import type {
  AppConfig,
  BasketResponse,
  RecentSearch,
  RefreshStart,
  ResultsResponse,
  SearchStart,
  SiteSummary,
  SortKey,
} from "../types";

declare global {
  interface Window {
    // The packaged app injects the process's token into the window before the
    // page loads. In development nothing does, and the Vite env var stands in.
    __PARFUM_TOKEN__?: string;
  }
}

export function authToken(): string {
  return window.__PARFUM_TOKEN__ ?? import.meta.env.VITE_AUTH_TOKEN ?? "";
}

export class ApiError extends Error {
  readonly status: number;

  constructor(status: number, detail: string) {
    super(detail);
    this.name = "ApiError";
    this.status = status;
  }
}

async function request<T>(
  path: string,
  init: RequestInit & { json?: unknown } = {},
): Promise<T> {
  const { json, ...rest } = init;
  const headers: Record<string, string> = { "X-Auth-Token": authToken() };
  if (json !== undefined) headers["Content-Type"] = "application/json";
  const response = await fetch(path, {
    ...rest,
    headers: { ...headers, ...(rest.headers as Record<string, string>) },
    body: json !== undefined ? JSON.stringify(json) : rest.body,
  });
  if (!response.ok) {
    throw new ApiError(response.status, await readDetail(response));
  }
  if (response.status === 204) return undefined as T;
  return (await response.json()) as T;
}

async function readDetail(response: Response): Promise<string> {
  // FastAPI puts the message in "detail", but a validation error puts a list
  // of field problems there instead, and neither shape may arrive at all if
  // something upstream of the app failed.
  try {
    const body = (await response.json()) as { detail?: unknown };
    if (typeof body.detail === "string") return body.detail;
    if (body.detail !== undefined) return JSON.stringify(body.detail);
  } catch {
    /* not JSON */
  }
  return `${response.status} ${response.statusText}`;
}

export const api = {
  config: () => request<AppConfig>("/api/config"),

  sites: () => request<SiteSummary[]>("/api/sites"),

  startSearch: (query: string, force: boolean) =>
    request<SearchStart>("/api/search", {
      method: "POST",
      json: { query, force },
    }),

  recentSearches: () => request<RecentSearch[]>("/api/searches/recent"),

  results: (searchId: string, sort: SortKey | null) => {
    const suffix = sort ? `?sort=${sort}` : "";
    return request<ResultsResponse>(`/api/results/${searchId}${suffix}`);
  },

  basket: () => request<BasketResponse>("/api/basket"),

  addBasketItem: (item: {
    brand: string;
    name: string;
    concentration: string;
    size_ml_x10: number;
    qty: number;
    own_identity: boolean;
    clone_of: string;
    confident: boolean;
    confirmed: boolean;
  }) =>
    request<{ basket_item_id: number }>("/api/basket/items", {
      method: "POST",
      json: item,
    }),

  setBasketQty: (itemId: number, qty: number) =>
    request<{ basket_item_id: number; qty: number }>(
      `/api/basket/items/${itemId}`,
      { method: "PATCH", json: { qty } },
    ),

  removeBasketItem: (itemId: number) =>
    request<void>(`/api/basket/items/${itemId}`, { method: "DELETE" }),

  startBasketRefresh: () =>
    request<RefreshStart>("/api/basket/refresh", { method: "POST" }),
};
