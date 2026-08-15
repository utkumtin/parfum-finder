// The two event streams, both of which start their work on connect rather
// than on the POST that registers them. That makes connecting exactly once the
// whole contract: a second socket for the same id is refused with 4409 by the
// backend, because re-driving a scan would write every price snapshot twice.

import { useEffect, useRef } from "react";
import { authToken } from "./client";

export function streamUrl(path: string): string {
  const scheme = window.location.protocol === "https:" ? "wss" : "ws";
  const token = encodeURIComponent(authToken());
  return `${scheme}://${window.location.host}${path}?token=${token}`;
}

/** Close codes the backend uses to refuse a socket, as words. */
export function refusalReason(code: number): string | null {
  if (code === 4401) return "kimlik doğrulaması reddedildi";
  if (code === 4404) return "bu arama artık sunucuda yok";
  if (code === 4409) return "bu arama zaten başlatılmış";
  return null;
}

/**
 * Subscribe to one event stream for as long as `path` stays the same.
 *
 * Passing null means "nothing to listen to yet". The handlers are read through
 * refs so that a screen re-rendering (which it does on every event) cannot tear
 * the socket down and open a second one, which is the shape of mistake the
 * 4409 above turns into a dead search.
 */
export function useEventStream<T>(
  path: string | null,
  onEvent: (event: T) => void,
  onClosed?: (code: number) => void,
): void {
  const onEventRef = useRef(onEvent);
  const onClosedRef = useRef(onClosed);
  onEventRef.current = onEvent;
  onClosedRef.current = onClosed;
  const connectedRef = useRef<string | null>(null);

  useEffect(() => {
    if (path === null) return;
    // Belt and braces against a double-invoked effect: this path has already
    // had its one socket, and the scan behind it is already running.
    if (connectedRef.current === path) return;
    connectedRef.current = path;

    const socket = new WebSocket(streamUrl(path));
    socket.onmessage = (message) => {
      onEventRef.current(JSON.parse(message.data as string) as T);
    };
    socket.onclose = (event) => onClosedRef.current?.(event.code);
    return () => {
      // Closing here is what tells the backend to unwind the scan's TaskGroup
      // and browser session, so a screen the user left does not keep scraping.
      socket.close();
    };
  }, [path]);
}
