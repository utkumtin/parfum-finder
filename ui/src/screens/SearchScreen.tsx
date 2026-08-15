import { useEffect, useMemo, useState } from "react";
import { ApiError, api } from "../api/client";
import { formatAge } from "../lib/format";
import type { AppConfig, RecentSearch, SearchStart } from "../types";

/**
 * Splits a half-typed line the way the backend will.
 *
 * The separator pattern comes from /api/config rather than being written out
 * again here, so the rule that keeps "Jean-Paul Gaultier" one perfume has one
 * definition. The de-duplication is a near-miss of the server's, which
 * compares tokenised forms: this is a live counter, and the request's own 422
 * is what actually decides.
 */
function splitParts(text: string, separator: RegExp): string[] {
  const seen = new Set<string>();
  const parts: string[] = [];
  for (const raw of text.split(separator)) {
    const part = raw.replace(/^[\s\t-]+|[\s\t-]+$/g, "");
    if (!part) continue;
    const key = part.toLocaleLowerCase("tr").replace(/\s+/g, " ");
    if (seen.has(key)) continue;
    seen.add(key);
    parts.push(part);
  }
  return parts;
}

/**
 * How long ago a recorded search was run, in whole days.
 *
 * Rounded down to a day so the recents list speaks the same vocabulary as the
 * age column, rather than putting "4 saat" next to "18 gün" in one screen.
 */
function daysSince(iso: string): number {
  const then = Date.parse(iso);
  if (Number.isNaN(then)) return 0;
  return Math.max(0, Math.floor((Date.now() - then) / 86_400_000));
}

export function SearchScreen({
  config,
  onStarted,
}: {
  config: AppConfig;
  onStarted: (start: SearchStart, force: boolean) => void;
}) {
  const [text, setText] = useState("");
  const [force, setForce] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [starting, setStarting] = useState(false);
  const [recents, setRecents] = useState<RecentSearch[]>([]);

  useEffect(() => {
    let cancelled = false;
    // A history nobody could read is a missing convenience, not a broken
    // screen: the input above it works either way, so this failure stays quiet.
    api
      .recentSearches()
      .then((rows) => {
        if (!cancelled) setRecents(rows);
      })
      .catch(() => {
        if (!cancelled) setRecents([]);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const separator = useMemo(
    () => new RegExp(config.query_separator_pattern),
    [config.query_separator_pattern],
  );
  const parts = useMemo(() => splitParts(text, separator), [text, separator]);
  const overLimit = parts.length > config.max_queries;

  const submit = async () => {
    // Refused rather than trimmed to the first ten, the same call the TUI
    // makes: a scan that quietly answered a shorter question is worse than no
    // scan, because nothing on screen says which perfumes were dropped.
    if (overLimit || parts.length === 0 || starting) return;
    setStarting(true);
    setError(null);
    try {
      onStarted(await api.startSearch(text, force), force);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : String(e));
    } finally {
      setStarting(false);
    }
  };

  return (
    <div className="page search-page">
      <div>
        <h1 className="search-heading">Parfüm ara</h1>
        <p className="search-sub">
          Birden fazla parfümü <code>{" - "}</code> ile ayırın. En fazla{" "}
          {config.max_queries} parfüm.
        </p>
      </div>

      <div className={`search-field${overLimit ? " over-limit" : ""}`}>
        <input
          type="text"
          value={text}
          autoFocus
          placeholder="Dior Sauvage EDP - Creed Aventus"
          aria-label="Aranacak parfümler"
          onChange={(e) => setText(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") void submit();
          }}
        />
        <span className={`search-count${overLimit ? " over-limit" : ""}`}>
          {parts.length} / {config.max_queries}
        </span>
      </div>

      {parts.length > 0 && (
        <div className="chips">
          {parts.map((part, i) => (
            <span
              key={`${part}-${i}`}
              className={`chip${i >= config.max_queries ? " rejected" : ""}`}
            >
              {part}
              {/* Rewriting the line from the parts, rather than cutting the
                  typed text, is what makes this safe: the parts are what the
                  request is built from anyway, so dropping one cannot leave a
                  stray separator behind for the server to reject. */}
              <button
                type="button"
                className="chip-remove"
                aria-label={`${part} aramadan çıkarılsın`}
                onClick={() =>
                  setText(parts.filter((_, j) => j !== i).join(" - "))
                }
              >
                ×
              </button>
            </span>
          ))}
        </div>
      )}

      {overLimit && (
        <div className="notice error">
          en fazla {config.max_queries} parfüm aranabilir, bu satırda{" "}
          {parts.length} var
        </div>
      )}
      {error && <div className="notice error">{error}</div>}

      <div className="search-actions">
        <button
          type="button"
          className="button primary"
          disabled={overLimit || parts.length === 0 || starting}
          onClick={() => void submit()}
        >
          {starting ? "Başlatılıyor…" : "Ara"}
        </button>
        <label className="checkbox">
          <input
            type="checkbox"
            checked={force}
            onChange={(e) => setForce(e.target.checked)}
          />
          {/* The TUI's [r]. Without it a perfume already in storage is never
              asked for again, and a table mixing two moments is not a
              comparison. */}
          Kayıttakileri de yeniden tara
        </label>
      </div>

      {recents.length > 0 && (
        <div className="recents">
          <span className="recents-label">Son aramalar</span>
          {recents.map((recent) => (
            <button
              key={recent.text}
              type="button"
              className="recent"
              onClick={() => setText(recent.text)}
            >
              <span className="recent-text">{recent.text}</span>
              <span className="recent-when">
                {formatAge(daysSince(recent.searched_at))}
              </span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
