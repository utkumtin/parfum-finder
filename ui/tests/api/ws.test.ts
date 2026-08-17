// Connecting is what starts the work on the backend, so "exactly once per
// path" is not an optimisation here -- a second socket for the same search is
// refused with 4409 and the scan is dead. These tests are about that rule.

import { act, renderHook } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { refusalReason, streamUrl, useEventStream } from "../../src/api/ws";
import { installFakeServer, type FakeServer } from "../helpers/server";

let server: FakeServer;

beforeEach(() => {
  server = installFakeServer();
  window.__PARFUM_TOKEN__ = "test-token";
});

describe("streamUrl", () => {
  it("carries the token and matches the page's scheme", () => {
    // The socket cannot send a header, so the token goes on the URL. A page
    // served over http gets ws, not wss.
    const url = new URL(streamUrl("/api/search/search-1"));
    expect(url.protocol).toBe("ws:");
    expect(url.pathname).toBe("/api/search/search-1");
    expect(url.searchParams.get("token")).toBe("test-token");
  });

  it("escapes a token that would otherwise break the query string", () => {
    window.__PARFUM_TOKEN__ = "a&b=c";
    const url = new URL(streamUrl("/api/search/search-1"));
    expect(url.searchParams.get("token")).toBe("a&b=c");
  });
});

describe("refusalReason", () => {
  it("puts words to each way the backend refuses a socket", () => {
    expect(refusalReason(4401)).toBe("kimlik doğrulaması reddedildi");
    expect(refusalReason(4404)).toBe("bu arama artık sunucuda yok");
    expect(refusalReason(4409)).toBe("bu arama zaten başlatılmış");
  });

  it("has nothing to say about an ordinary close", () => {
    // The screen leaving closes the socket itself with 1000. Reporting that as
    // a refusal would put an error on a screen where nothing went wrong.
    expect(refusalReason(1000)).toBeNull();
    expect(refusalReason(1006)).toBeNull();
  });
});

describe("useEventStream", () => {
  it("opens nothing while there is nothing to listen to", () => {
    renderHook(() => useEventStream(null, () => {}));
    expect(server.sockets).toHaveLength(0);
  });

  it("opens one socket and keeps it across re-renders", async () => {
    // The screen re-renders on every event it receives. If that tore the
    // socket down and opened a second one, the scan behind it would be refused
    // with 4409 halfway through.
    const onEvent = vi.fn();
    const { rerender } = renderHook(() => useEventStream("/api/search/s1", onEvent));
    const socket = await server.socket("/api/search/s1");

    rerender();
    rerender();
    expect(server.sockets).toHaveLength(1);
    expect(socket.readyState).toBe(1);
  });

  it("delivers each event as the parsed object", async () => {
    const onEvent = vi.fn();
    renderHook(() => useEventStream("/api/search/s1", onEvent));
    const socket = await server.socket("/api/search/s1");

    act(() => socket.emit({ type: "scan_started", total_sites: 2, total_perfumes: 1 }));
    expect(onEvent).toHaveBeenCalledWith({
      type: "scan_started",
      total_sites: 2,
      total_perfumes: 1,
    });
  });

  it("calls the newest handler without reconnecting to reach it", async () => {
    // The handlers are held in refs precisely so a screen may pass a fresh
    // closure on every render. The point of the ref is that doing so costs no
    // socket.
    const first = vi.fn();
    const second = vi.fn();
    const { rerender } = renderHook(
      ({ handler }: { handler: (e: unknown) => void }) =>
        useEventStream("/api/search/s1", handler),
      { initialProps: { handler: first as (e: unknown) => void } },
    );
    const socket = await server.socket("/api/search/s1");

    rerender({ handler: second as (e: unknown) => void });
    act(() => socket.emit({ type: "scan_finished", error_count: 0 }));

    expect(first).not.toHaveBeenCalled();
    expect(second).toHaveBeenCalledOnce();
    expect(server.sockets).toHaveLength(1);
  });

  it("closes the socket when the screen goes away", async () => {
    // Closing is what tells the backend to unwind the scan's TaskGroup and its
    // browser session. Without it a screen nobody is on keeps scraping.
    const { unmount } = renderHook(() => useEventStream("/api/search/s1", () => {}));
    const socket = await server.socket("/api/search/s1");

    unmount();
    expect(socket.closedByClient).toBe(true);
    expect(socket.readyState).toBe(3);
  });

  it("reports the close code the backend refused with", async () => {
    const onClosed = vi.fn();
    renderHook(() => useEventStream("/api/search/s1", () => {}, onClosed));
    const socket = await server.socket("/api/search/s1");

    act(() => socket.refuse(4409));
    expect(onClosed).toHaveBeenCalledWith(4409);
  });

  it("opens a second socket only when the path itself changes", async () => {
    const { rerender } = renderHook(
      ({ path }: { path: string }) => useEventStream(path, () => {}),
      { initialProps: { path: "/api/basket/refresh/r1" } },
    );
    await server.socket("/api/basket/refresh/r1");

    rerender({ path: "/api/basket/refresh/r2" });
    await server.socket("/api/basket/refresh/r2");
    expect(server.sockets).toHaveLength(2);
    expect(server.sockets[0]?.closedByClient).toBe(true);
  });
});
