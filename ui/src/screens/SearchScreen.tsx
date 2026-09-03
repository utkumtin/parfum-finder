import { useEffect, useMemo, useState } from "react";
import { motion, useReducedMotion } from "motion/react";
import { ApiError, api } from "../api/client";
import { formatAge } from "../lib/format";
import type { AppConfig, RecentSearch, SearchStart, SiteSummary } from "../types";

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
  sites,
  onStarted,
}: {
  config: AppConfig;
  sites: SiteSummary[];
  onStarted: (start: SearchStart, force: boolean) => void;
}) {
  const [text, setText] = useState("");
  const [force, setForce] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [starting, setStarting] = useState(false);
  const [recents, setRecents] = useState<RecentSearch[]>([]);
  const [focused, setFocused] = useState(false);
  const enabledSites = useMemo(() => sites.filter((site) => site.enabled), [sites]);
  const [selectedSiteIds, setSelectedSiteIds] = useState(
    () => new Set(enabledSites.map((site) => site.id)),
  );
  const reducedMotion = useReducedMotion();

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
  const raisedLabel = focused || text.length > 0;

  const submit = async () => {
    // Refused rather than trimmed to the first ten, the same call the TUI
    // makes: a scan that quietly answered a shorter question is worse than no
    // scan, because nothing on screen says which perfumes were dropped.
    if (overLimit || parts.length === 0 || selectedSiteIds.size === 0 || starting) return;
    setStarting(true);
    setError(null);
    try {
      onStarted(await api.startSearch(text, force, [...selectedSiteIds]), force);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : String(e));
    } finally {
      setStarting(false);
    }
  };

  return (
    <div className="page search-page">
      <div className={`tray search-field${overLimit ? " over-limit" : ""}`}>
        <motion.label
          htmlFor="perfume-search"
          initial={false}
          animate={{
            x: raisedLabel ? -12 : 0,
            y: raisedLabel ? -52 : 0,
            scale: raisedLabel ? 0.8 : 1,
          }}
          transition={reducedMotion ? { duration: 0 } : { duration: 0.2, ease: "easeOut" }}
          style={{ originX: 0, originY: 0, willChange: "transform" }}
          className={`search-field-label${raisedLabel ? " raised" : ""}`}
        >
          Birden fazla parfümü - ile ayırın. En fazla 10 parfüm.
        </motion.label>
        <div className="core">
          <input
            id="perfume-search"
            type="text"
            value={text}
            autoFocus
            aria-label="Aranacak parfümler"
            onFocus={() => setFocused(true)}
            onBlur={() => setFocused(false)}
            onChange={(e) => setText(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") void submit();
            }}
          />
          <span className={`search-count${overLimit ? " over-limit" : ""}`}>
            {parts.length} / {config.max_queries}
          </span>
          {/* Inside the field rather than under it: the button belongs to the
              line it acts on, and a shopper hitting Enter and a shopper
              reaching for the button are doing the same thing. */}
          <button
            type="button"
            className="button primary"
            disabled={overLimit || parts.length === 0 || selectedSiteIds.size === 0 || starting}
            onClick={() => void submit()}
          >
            {starting ? "Başlatılıyor…" : "Ara"}
            <span className="button-pip" aria-hidden="true">
              <svg viewBox="0 0 12 12" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round">
                <path d="M2.5 9.5 9.5 2.5M4 2.5h5.5V8" />
              </svg>
            </span>
          </button>
        </div>
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

      <motion.div
        className="tray site-picker"
        aria-labelledby="site-picker-label"
        initial={reducedMotion ? false : { opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={
          reducedMotion
            ? { duration: 0 }
            : { duration: 0.6, ease: [0.32, 0.72, 0, 1] }
        }
      >
        <div className="core">
          <div className="site-picker-heading">
            <span id="site-picker-label" className="eyebrow">Aranacak mağazalar</span>
            <span className="site-picker-count">
              {selectedSiteIds.size} / {enabledSites.length} seçili
            </span>
          </div>
          <div className="site-picker-options" role="group" aria-labelledby="site-picker-label">
            {enabledSites.map((site) => (
              <label className="site-choice" key={site.id}>
                <input
                  type="checkbox"
                  checked={selectedSiteIds.has(site.id)}
                  onChange={(event) => {
                    setSelectedSiteIds((current) => {
                      const next = new Set(current);
                      if (event.target.checked) next.add(site.id);
                      else next.delete(site.id);
                      return next;
                    });
                  }}
                />
                <span className="site-choice-mark" aria-hidden="true">
                  <svg viewBox="0 0 10 10" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M1.5 5.2 4 7.5 8.5 2.5" />
                  </svg>
                </span>
                <span>{site.name}</span>
              </label>
            ))}
          </div>
          {selectedSiteIds.size === 0 && (
            <span className="site-picker-warning" role="status">Aramak için en az bir mağaza seçin.</span>
          )}
        </div>
      </motion.div>

      <div className="search-actions">
        <label className="checkbox">
          <input
            type="checkbox"
            checked={force}
            onChange={(e) => setForce(e.target.checked)}
          />
          <span className="checkbox-box" aria-hidden="true">
            <svg viewBox="0 0 10 10" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
              <path d="M1.5 5.2 4 7.5 8.5 2.5" />
            </svg>
          </span>
          {/* The TUI's [r]. Without it a perfume already in storage is never
              asked for again, and a table mixing two moments is not a
              comparison. */}
          Kayıttakileri de yeniden tara
        </label>
        <span className="search-hint">
          Kapalıyken {config.stale_price_days} günden yeni fiyatlar kayıttan
          gelir.
        </span>
      </div>

      {recents.length > 0 && (
        <div className="recents">
          <span className="eyebrow recents-label">Son aramalar</span>
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
              <span className="recent-go" aria-hidden="true">
                <svg viewBox="0 0 12 12" fill="none" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round">
                  <path d="M4 2.5 7.5 6 4 9.5" />
                </svg>
              </span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
