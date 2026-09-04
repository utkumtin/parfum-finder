import { useSyncExternalStore } from "react";
import { api } from "../api/client";
import type { BasketResponse } from "../types";

export type BasketSnapshot = {
  data: BasketResponse | null;
  error: unknown | null;
  loading: boolean;
  refreshing: boolean;
  stale: boolean;
  status: "idle" | "loading" | "ready" | "refreshing" | "error";
};

type Listener = () => void;
type Deferred<T> = {
  promise: Promise<T>;
  resolve: (value: T) => void;
  reject: (reason?: unknown) => void;
};
type ActiveRequest = {
  generation: number;
  promise: Promise<BasketResponse>;
};

const listeners = new Set<Listener>();
const initialSnapshot: BasketSnapshot = {
  data: null,
  error: null,
  loading: false,
  refreshing: false,
  stale: false,
  status: "idle",
};

let snapshot = initialSnapshot;
let generation = 0;
let activeRequest: ActiveRequest | null = null;
let queuedFollowUp: Deferred<BasketResponse> | null = null;

function notify(): void {
  for (const listener of listeners) listener();
}

function setSnapshot(
  data: BasketResponse | null,
  error: unknown | null,
  stale: boolean,
): void {
  const loading = activeRequest !== null && data === null;
  const refreshing = activeRequest !== null && data !== null;
  const status =
    error !== null
      ? "error"
      : loading
        ? "loading"
        : refreshing
          ? "refreshing"
          : data === null
            ? "idle"
            : "ready";

  if (
    snapshot.data === data &&
    snapshot.error === error &&
    snapshot.loading === loading &&
    snapshot.refreshing === refreshing &&
    snapshot.stale === stale &&
    snapshot.status === status
  ) {
    return;
  }

  snapshot = { data, error, loading, refreshing, stale, status };
  notify();
}

function deferred<T>(): Deferred<T> {
  let resolve!: (value: T) => void;
  let reject!: (reason?: unknown) => void;
  const promise = new Promise<T>((promiseResolve, promiseReject) => {
    resolve = promiseResolve;
    reject = promiseReject;
  });
  // A queued retry may be created by invalidateBasket without a caller. Keep
  // its rejection handled while still returning the original promise to any
  // caller that explicitly asks for the follow-up.
  promise.catch(() => {});
  return { promise, resolve, reject };
}

function startQueuedFollowUp(): void {
  if (activeRequest !== null || queuedFollowUp === null) return;

  const waiting = queuedFollowUp;
  queuedFollowUp = null;
  const request = startRequest();
  request.then(waiting.resolve, waiting.reject);
}

function settleActiveRequest(request: ActiveRequest): void {
  if (activeRequest !== request) return;
  activeRequest = null;

  setSnapshot(snapshot.data, snapshot.error, snapshot.stale);

  if (request.generation !== generation) {
    setSnapshot(snapshot.data, snapshot.error, true);
    startQueuedFollowUp();
  }
}

function startRequest(): Promise<BasketResponse> {
  const requestGeneration = generation;
  let resolveRequest!: (value: BasketResponse) => void;
  let rejectRequest!: (reason?: unknown) => void;
  const promise = new Promise<BasketResponse>((resolve, reject) => {
    resolveRequest = resolve;
    rejectRequest = reject;
  });
  const request: ActiveRequest = { generation: requestGeneration, promise };
  activeRequest = request;
  setSnapshot(snapshot.data, null, snapshot.data !== null && snapshot.stale);

  Promise.resolve()
    .then(() => api.basket())
    .then(
      (response) => {
        const obsolete = request.generation !== generation;
        if (!obsolete) {
          setSnapshot(response, null, false);
        }
        settleActiveRequest(request);
        if (obsolete) {
          rejectRequest(new Error("Obsolete basket response"));
        } else {
          resolveRequest(response);
        }
      },
      (error: unknown) => {
        const obsolete = request.generation !== generation;
        if (!obsolete) {
          setSnapshot(snapshot.data, error, snapshot.data !== null);
        }
        settleActiveRequest(request);
        rejectRequest(obsolete ? new Error("Obsolete basket response") : error);
      },
    );

  return promise;
}

function queuedRequest(): Promise<BasketResponse> {
  if (queuedFollowUp === null) queuedFollowUp = deferred<BasketResponse>();
  return queuedFollowUp.promise;
}

export function subscribeBasket(listener: Listener): () => void {
  listeners.add(listener);
  return () => listeners.delete(listener);
}

export function getBasketSnapshot(): BasketSnapshot {
  return snapshot;
}

export function useBasketSnapshot(): BasketSnapshot {
  return useSyncExternalStore(subscribeBasket, getBasketSnapshot, getBasketSnapshot);
}

/** Read once, sharing an in-flight request and preferring a successful cache. */
export function ensureBasket(): Promise<BasketResponse> {
  if (snapshot.data !== null && !snapshot.stale && snapshot.error === null) {
    return Promise.resolve(snapshot.data);
  }
  if (activeRequest !== null) {
    if (activeRequest.generation === generation) return activeRequest.promise;
    return queuedRequest();
  }
  return startRequest();
}

/** Fetch a fresh response even when a cached response is already available. */
export function refreshBasket(): Promise<BasketResponse> {
  if (activeRequest !== null) {
    if (activeRequest.generation === generation) return activeRequest.promise;
    return queuedRequest();
  }

  setSnapshot(snapshot.data, null, snapshot.data !== null);
  return startRequest();
}

/** Mark the current read obsolete and ensure one latest response is fetched. */
export function invalidateBasket(): void {
  generation += 1;
  setSnapshot(snapshot.data, null, snapshot.data !== null);
  if (activeRequest !== null) {
    queuedRequest();
    return;
  }
  void startRequest().catch(() => {});
}

/** Reset only for isolated tests. The production store intentionally persists. */
export function resetBasketStoreForTests(): void {
  generation += 1;
  if (queuedFollowUp !== null) {
    queuedFollowUp.reject(new Error("Basket store reset"));
    queuedFollowUp = null;
  }
  activeRequest = null;
  snapshot = initialSnapshot;
  notify();
}
