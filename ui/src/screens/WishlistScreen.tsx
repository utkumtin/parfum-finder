import {
  Fragment,
  useCallback,
  useEffect,
  useLayoutEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import { ApiError, api } from "../api/client";
import { refusalReason, useEventStream } from "../api/ws";
import { AddButton } from "../components/AddButton";
import { Badge } from "../components/Badge";
import { ConfirmDialog } from "../components/ConfirmDialog";
import { WishlistButton } from "../components/WishlistButton";
import { basketKey } from "../lib/basket";
import { useBasketSnapshot, type BasketSnapshot } from "../lib/basketStore";
import { formatAge, formatMl, formatPerMl, formatPrice } from "../lib/format";
import { wishlistKey } from "../lib/wishlist";
import type { AppConfig, ResultRow, ScanEvent, WishlistRow } from "../types";

function RefreshIcon() {
  return (
    <svg viewBox="0 0 16 16" aria-hidden="true" focusable="false">
      <path
        d="M13.5 8a5.5 5.5 0 1 1-1.6-3.9"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
      />
      <path d="M13.5 1.8v3.2h-3.2z" fill="currentColor" />
    </svg>
  );
}

function normalizeSearchText(value: string): string {
  return value
    .toLocaleLowerCase("tr-TR")
    .normalize("NFD")
    .replace(/\p{M}/gu, "");
}

const DEFAULT_ACC_COLLAPSE_MS = 250;
const ACCORDION_FRAME_ALLOWANCE_MS = 32;

function wishlistPanelId(key: string): string {
  return `wishlist-offers-${encodeURIComponent(key)}`;
}

function parseCssTimeList(value: string | undefined): number[] {
  if (typeof value !== "string") return [];
  return value.split(",").flatMap((part) => {
    const match = part.trim().match(/^(-?(?:\d+\.?\d*|\.\d+))(ms|s)$/i);
    if (!match) return [];
    const amount = Number(match[1]);
    return [match[2]?.toLowerCase() === "s" ? amount * 1000 : amount];
  });
}

function transitionTimeMs(styles: CSSStyleDeclaration | null): number | null {
  if (styles === null) return null;
  const durations = parseCssTimeList(styles.transitionDuration);
  if (durations.length === 0) return null;
  const delays = parseCssTimeList(styles.transitionDelay);
  return Math.max(
    0,
    ...durations.map((duration, index) =>
      Math.max(0, duration + (delays[index % Math.max(1, delays.length)] ?? 0)),
    ),
  );
}

function prefersReducedMotion(): boolean {
  try {
    const media = window.matchMedia?.("(prefers-reduced-motion: reduce)");
    return media?.matches ?? false;
  } catch {
    return false;
  }
}

function accordionCloseDelay(panel: HTMLElement | null): number {
  if (prefersReducedMotion()) return 0;

  const rootStyles = getComputedStyle(document.documentElement);
  const fallback = parseCssTimeList(rootStyles.getPropertyValue("--acc-collapse"))[0];
  const panelStyles = panel === null ? null : getComputedStyle(panel);
  const panelTime = transitionTimeMs(panelStyles);
  const panelTransition =
    panelStyles === null || typeof panelStyles.transition !== "string"
      ? null
      : panelStyles.transition.trim();
  if (
    panelTime !== null &&
    (panelTime > 0 || panelTransition === null || panelTransition.length > 0 || fallback === 0)
  ) {
    return panelTime;
  }
  return fallback ?? DEFAULT_ACC_COLLAPSE_MS;
}

export function WishlistScreen({
  rows,
  wishlistReady,
  pendingWishlistKeys,
  config,
  siteNames,
  basketSnapshot: suppliedBasketSnapshot,
  query: controlledQuery,
  onQueryChange,
  sort: controlledSort,
  onSortChange,
  notify,
  onBasketChanged,
  onWishlistChanged,
  onWishlistToggle,
}: {
  rows: WishlistRow[];
  wishlistReady: boolean;
  pendingWishlistKeys: Set<string>;
  config: AppConfig;
  siteNames: Record<string, string>;
  basketSnapshot?: BasketSnapshot;
  query?: string;
  onQueryChange?: (query: string) => void;
  sort?: "price" | "per_ml" | null;
  onSortChange?: (sort: "price" | "per_ml" | null) => void;
  notify: (message: string, kind: "info" | "error") => void;
  onBasketChanged: () => void;
  onWishlistChanged: () => void | Promise<void>;
  onWishlistToggle: (row: ResultRow) => void | Promise<void>;
}) {
  const storeBasketSnapshot = useBasketSnapshot();
  const basketSnapshot = suppliedBasketSnapshot ?? storeBasketSnapshot;
  const basketKeys = useMemo(
    () => new Set(basketSnapshot.data?.rows.map(basketKey) ?? []),
    [basketSnapshot.data],
  );
  const [confirming, setConfirming] = useState<ResultRow | null>(null);
  const [localSort, setLocalSort] = useState<"price" | "per_ml" | null>(null);
  const [localQuery, setLocalQuery] = useState("");
  const [openRows, setOpenRows] = useState<Set<string>>(new Set());
  const [mountedRows, setMountedRows] = useState<Set<string>>(new Set());
  const [refreshId, setRefreshId] = useState<string | null>(null);
  const [refreshKey, setRefreshKey] = useState<string | null>(null);
  const [justRefreshed, setJustRefreshed] = useState<Set<string>>(new Set());
  const searchInputRef = useRef<HTMLInputElement>(null);
  const closeTimersRef = useRef<Map<string, number>>(new Map());
  const accordionGenerationsRef = useRef<Map<string, number>>(new Map());
  const openRowsRef = useRef<Set<string>>(new Set());
  const liveWishlistKeysRef = useRef<Set<string>>(new Set());
  const sort = controlledSort === undefined ? localSort : controlledSort;
  const updateSort = onSortChange ?? setLocalSort;
  const query = controlledQuery === undefined ? localQuery : controlledQuery;
  const updateQuery = onQueryChange ?? setLocalQuery;

  const bumpAccordionGeneration = useCallback((key: string): number => {
    const next = (accordionGenerationsRef.current.get(key) ?? 0) + 1;
    accordionGenerationsRef.current.set(key, next);
    return next;
  }, []);

  const cancelCloseTimer = useCallback((key: string) => {
    const timer = closeTimersRef.current.get(key);
    if (timer === undefined) return;
    window.clearTimeout(timer);
    closeTimersRef.current.delete(key);
  }, []);

  const toggleRow = (row: WishlistRow) => {
    const key = wishlistKey(row);
    if (openRowsRef.current.has(key)) {
      const nextOpenRows = new Set(openRowsRef.current);
      nextOpenRows.delete(key);
      openRowsRef.current = nextOpenRows;
      bumpAccordionGeneration(key);
      setOpenRows((current) => {
        if (!current.has(key)) return current;
        const next = new Set(current);
        next.delete(key);
        return next;
      });
      return;
    }

    cancelCloseTimer(key);
    bumpAccordionGeneration(key);
    const nextOpenRows = new Set(openRowsRef.current);
    nextOpenRows.add(key);
    openRowsRef.current = nextOpenRows;
    setMountedRows((current) => {
      if (current.has(key)) return current;
      const next = new Set(current);
      next.add(key);
      return next;
    });
    setOpenRows((current) => {
      if (current.has(key)) return current;
      const next = new Set(current);
      next.add(key);
      return next;
    });
  };

  useLayoutEffect(() => {
    liveWishlistKeysRef.current = new Set(rows.map(wishlistKey));
  }, [rows]);

  useEffect(() => {
    const liveKeys = new Set(rows.map(wishlistKey));
    for (const [key, timer] of closeTimersRef.current) {
      if (!liveKeys.has(key)) {
        window.clearTimeout(timer);
        closeTimersRef.current.delete(key);
      }
    }
    for (const key of accordionGenerationsRef.current.keys()) {
      if (!liveKeys.has(key)) accordionGenerationsRef.current.delete(key);
    }
    openRowsRef.current = new Set(
      [...openRowsRef.current].filter((key) => liveKeys.has(key)),
    );
    setOpenRows((current) => {
      const next = new Set([...current].filter((key) => liveKeys.has(key)));
      return next.size === current.size ? current : next;
    });
    setMountedRows((current) => {
      const next = new Set([...current].filter((key) => liveKeys.has(key)));
      return next.size === current.size ? current : next;
    });
  }, [rows]);

  useEffect(() => {
    const liveKeys = new Set(rows.map(wishlistKey));
    for (const key of mountedRows) {
      if (openRows.has(key) || !liveKeys.has(key) || closeTimersRef.current.has(key)) continue;
      const generation = accordionGenerationsRef.current.get(key);
      if (generation === undefined) continue;

      const panel = document.getElementById(wishlistPanelId(key));
      const closeDelay = accordionCloseDelay(panel?.parentElement ?? panel);
      const timeout = closeDelay === 0 ? 0 : closeDelay + ACCORDION_FRAME_ALLOWANCE_MS;
      const timer = window.setTimeout(() => {
        closeTimersRef.current.delete(key);
        if (
          accordionGenerationsRef.current.get(key) !== generation ||
          openRowsRef.current.has(key) ||
          !liveWishlistKeysRef.current.has(key)
        ) {
          return;
        }
        setMountedRows((current) => {
          if (!current.has(key)) return current;
          const next = new Set(current);
          next.delete(key);
          return next;
        });
      }, timeout);
      closeTimersRef.current.set(key, timer);
    }
  }, [mountedRows, openRows, rows]);

  useEffect(
    () => () => {
      for (const timer of closeTimersRef.current.values()) window.clearTimeout(timer);
      closeTimersRef.current.clear();
    },
    [],
  );

  const queryTokens = useMemo(
    () =>
      normalizeSearchText(query)
        .trim()
        .split(/\s+/)
        .filter(Boolean),
    [query],
  );

  const filteredRows = useMemo(() => {
    if (queryTokens.length === 0) return rows;
    return rows.filter((row) => {
      const searchable = normalizeSearchText(`${row.raw_title} ${row.site_label}`);
      return queryTokens.every((token) => searchable.includes(token));
    });
  }, [queryTokens, rows]);

  const sortedRows = useMemo(() => {
    if (sort === null) return filteredRows;
    return filteredRows
      .map((row, index) => ({ row, index }))
      .sort((left, right) => {
        const a = left.row;
        const b = right.row;
        const aMissing =
          sort === "price"
            ? a.price_kurus === null
            : a.price_kurus === null || a.price_per_ml_kurus === null;
        const bMissing =
          sort === "price"
            ? b.price_kurus === null
            : b.price_kurus === null || b.price_per_ml_kurus === null;
        if (aMissing !== bMissing) return aMissing ? 1 : -1;
        if (aMissing) return left.index - right.index;

        if (sort === "price") {
          const comparison = (a.price_kurus ?? 0) - (b.price_kurus ?? 0);
          return comparison || left.index - right.index;
        }

        const aRate = BigInt(a.price_kurus ?? 0) * BigInt(b.size_ml_x10);
        const bRate = BigInt(b.price_kurus ?? 0) * BigInt(a.size_ml_x10);
        return aRate < bRate ? -1 : aRate > bRate ? 1 : left.index - right.index;
      })
      .map(({ row }) => row);
  }, [filteredRows, sort]);

  const finishRefresh = useCallback(async () => {
    if (refreshKey === null) return;
    try {
      await onWishlistChanged();
      setJustRefreshed((current) => new Set(current).add(refreshKey));
    } catch (error) {
      notify(error instanceof ApiError ? error.message : String(error), "error");
    } finally {
      setRefreshId(null);
      setRefreshKey(null);
    }
  }, [notify, onWishlistChanged, refreshKey]);

  const onRefreshEvent = useCallback(
    (event: ScanEvent) => {
      if (event.type === "scan_finished") void finishRefresh();
    },
    [finishRefresh],
  );

  const onRefreshClosed = useCallback(
    (code: number) => {
      const reason = refusalReason(code);
      if (reason === null) return;
      notify(reason, "error");
      setRefreshId(null);
      setRefreshKey(null);
    },
    [notify],
  );

  useEventStream<ScanEvent>(
    refreshId === null ? null : `/api/search/${refreshId}`,
    onRefreshEvent,
    onRefreshClosed,
  );

  const startRefresh = useCallback(
    async (row: WishlistRow) => {
      if (refreshKey !== null) return;
      const key = wishlistKey(row);
      setRefreshKey(key);
      try {
        const start = await api.refreshWishlistItem(row);
        setRefreshId(start.search_id);
      } catch (error) {
        notify(error instanceof ApiError ? error.message : String(error), "error");
        setRefreshKey(null);
      }
    },
    [notify, refreshKey],
  );

  const addToBasket = useCallback(
    async (row: ResultRow, confirmed: boolean): Promise<boolean> => {
      try {
        await api.addBasketItem({
          brand: row.brand,
          name: row.name,
          concentration: row.concentration,
          size_ml_x10: row.size_ml_x10,
          qty: 1,
          own_identity: row.own_identity,
          clone_of: row.clone_of,
          confident: row.confident,
          confirmed,
        });
        setConfirming(null);
        notify(`${row.brand} ${row.name} sepete eklendi`, "info");
        onBasketChanged();
        return true;
      } catch (error) {
        if (error instanceof ApiError && error.status === 409) {
          setConfirming(row);
          return false;
        }
        setConfirming(null);
        notify(error instanceof ApiError ? error.message : String(error), "error");
        return false;
      }
    },
    [notify, onBasketChanged],
  );

  return (
    <>
      <section className="page wishlist-page" aria-labelledby="wishlist-heading">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Kaydedilenler</p>
            <h1 id="wishlist-heading">İstek listesi</h1>
          </div>
          {rows.length > 0 && (
            <span className="section-count">
              {queryTokens.length > 0 ? `${filteredRows.length} / ${rows.length}` : rows.length} ürün
            </span>
          )}
        </div>

        {!wishlistReady ? (
          <p className="dim">İstek listesi yükleniyor…</p>
        ) : rows.length === 0 ? (
          <p className="dim">Henüz istek listenize ürün eklemediniz.</p>
        ) : (
          <>
            <div className="tray wishlist-filter">
              <div className="core">
                <svg
                  className="wishlist-filter-icon"
                  viewBox="0 0 20 20"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="1.5"
                  aria-hidden="true"
                >
                  <circle cx="8.5" cy="8.5" r="5.25" />
                  <path d="m12.5 12.5 4 4" strokeLinecap="round" />
                </svg>
                <input
                  ref={searchInputRef}
                  type="search"
                  value={query}
                  aria-label="İstek listesinde ara"
                  placeholder="Ürün veya mağaza ara"
                  onChange={(event) => updateQuery(event.target.value)}
                />
                {query.length > 0 && (
                  <button
                    type="button"
                    className="wishlist-filter-clear"
                    aria-label="Aramayı temizle"
                    onClick={() => {
                      updateQuery("");
                      searchInputRef.current?.focus();
                    }}
                  >
                    <svg
                      viewBox="0 0 12 12"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="1.5"
                      strokeLinecap="round"
                      aria-hidden="true"
                    >
                      <path d="m2.5 2.5 7 7m0-7-7 7" />
                    </svg>
                  </button>
                )}
              </div>
            </div>

            {filteredRows.length === 0 ? (
              <p className="dim wishlist-filter-empty" role="status">
                Aramanızla eşleşen ürün bulunamadı.
              </p>
            ) : (
              <div className="tray table-tray">
                <div className="core">
                  <table className="rows wishlist-rows">
                <colgroup>
                  <col style={{ width: "27%" }} />
                  <col style={{ width: "16%" }} />
                  <col style={{ width: "9%" }} />
                  <col style={{ width: "14%" }} />
                  <col style={{ width: "12%" }} />
                  <col style={{ width: "10%" }} />
                  <col style={{ width: "12%" }} />
                </colgroup>
                <thead>
                  <tr>
                    <th>Ürün</th>
                    <th>Site</th>
                    <th className="num">ml</th>
                    <th
                      className="num sortable"
                      aria-sort={sort === "price" ? "ascending" : "none"}
                      onClick={() => updateSort(sort === "price" ? null : "price")}
                    >
                      Fiyat<span className="sort-arrow" aria-hidden="true">▲</span>
                    </th>
                    <th
                      className="num sortable"
                      aria-sort={sort === "per_ml" ? "ascending" : "none"}
                      onClick={() => updateSort(sort === "per_ml" ? null : "per_ml")}
                    >
                      ₺/ml<span className="sort-arrow" aria-hidden="true">▲</span>
                    </th>
                    <th>Güncellik</th>
                    <th />
                  </tr>
                </thead>
                <tbody>
                  {sortedRows.map((row) => {
                    const key = wishlistKey(row);
                    const isOpen = openRows.has(key);
                    const isMounted = mountedRows.has(key);
                    const spinning = refreshKey === key;
                    const fresh =
                      row.age_days < config.stale_price_days || justRefreshed.has(key);
                    const panelId = wishlistPanelId(key);
                    const otherPrices = Object.entries(row.prices)
                      .filter(([siteId]) => siteId !== row.site_id)
                      .sort((left, right) => left[1] - right[1]);
                    return (
                    <Fragment key={key}>
                    <tr
                      className="clickable t-acc wishlist-summary-row"
                      data-open={String(isOpen)}
                      data-wishlist-summary
                      onClick={() => toggleRow(row)}
                    >
                      <td className="title-cell" title={row.raw_title}>
                        <button
                          type="button"
                          className="wishlist-accordion-trigger t-acc-head"
                          aria-expanded={isOpen}
                          aria-controls={isMounted ? panelId : undefined}
                          aria-label={`${row.raw_title} diğer mağaza fiyatları`}
                          onClick={(event) => {
                            event.stopPropagation();
                            toggleRow(row);
                          }}
                        >
                          <span className="t-acc-chevron" aria-hidden="true">
                            <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                              <path d="M4 6.5L8 10.5L12 6.5" />
                            </svg>
                          </span>
                          <span className="title-text">{row.raw_title}</span>
                        </button>
                      </td>
                      <td className="site-cell">{row.site_label}</td>
                      <td className="num">{formatMl(row.size_ml_x10)}</td>
                      <td className="num">{formatPrice(row.price_kurus)}</td>
                      <td className="num perml">{formatPerMl(row.price_per_ml_kurus)}</td>
                      <td className="age-cell">
                        {row.age_days >= config.stale_price_days ? (
                          <Badge kind="stale">{formatAge(row.age_days)}</Badge>
                        ) : (
                          <span className="dim">{formatAge(row.age_days)}</span>
                        )}
                      </td>
                      <td className="add-cell" onClick={(event) => event.stopPropagation()}>
                        <div className="row-actions">
                          <WishlistButton
                            inWishlist
                            disabled={pendingWishlistKeys.has(wishlistKey(row))}
                            pending={pendingWishlistKeys.has(wishlistKey(row))}
                            onToggle={() => void onWishlistToggle(row)}
                          />
                           <AddButton
                             onAdd={() => addToBasket(row, false)}
                             inBasket={basketKeys.has(basketKey(row))}
                           />
                           <button
                             type="button"
                             className={`refresh-button${spinning ? " spinning" : ""}`}
                             disabled={refreshKey !== null || fresh}
                             aria-label={`${row.raw_title} fiyatları yenilensin`}
                             title={
                               fresh
                                 ? "Fiyatlar güncel"
                                 : "Bu satırın fiyatlarını yenile"
                             }
                             onClick={() => void startRefresh(row)}
                           >
                             <RefreshIcon />
                           </button>
                         </div>
                      </td>
                    </tr>
                    {isMounted && <tr className="t-acc wishlist-offers-row" data-open={String(isOpen)}>
                      <td colSpan={7}>
                        <div className="t-acc-panel">
                          <div
                            id={panelId}
                            className="t-acc-panel-inner wishlist-offers"
                            role="region"
                            aria-label={`${row.raw_title} diğer mağaza fiyatları`}
                            aria-hidden={!isOpen}
                          >
                            <div className="wishlist-offers-head">
                              <span className="wishlist-offers-label">Diğer mağazalardaki fiyatlar</span>
                              <span className="wishlist-offer-ml">ml</span>
                              <span className="wishlist-offer-price">Fiyat</span>
                            </div>
                            {otherPrices.length > 0 ? (
                              <ul className="wishlist-offer-list">
                                {otherPrices.map(([siteId, price]) => (
                                  <li key={siteId}>
                                    <span className="wishlist-offer-site">
                                      {siteNames[siteId] ?? siteId}
                                    </span>
                                    <span className="wishlist-offer-ml">
                                      {formatMl(row.size_ml_x10)}
                                    </span>
                                    <strong className="wishlist-offer-price">
                                      {formatPrice(price)}
                                    </strong>
                                  </li>
                                ))}
                              </ul>
                            ) : (
                              <p className="dim wishlist-offers-empty">
                                Bu varyasyon için başka mağaza fiyatı bulunamadı.
                              </p>
                            )}
                            {row.product_url && (
                              <a
                                className="wishlist-product-link"
                                href={row.product_url}
                                target="_blank"
                                rel="noreferrer"
                                tabIndex={isOpen ? 0 : -1}
                              >
                                {row.site_label} ürün sayfasını aç
                                <svg viewBox="0 0 12 12" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" aria-hidden="true">
                                  <path d="M3 9 9 3M4.5 3H9v4.5" />
                                </svg>
                              </a>
                            )}
                          </div>
                        </div>
                      </td>
                    </tr>
                    }
                    </Fragment>
                    );
                  })}
                </tbody>
                  </table>
                </div>
              </div>
            )}
          </>
        )}
      </section>

      {confirming && (
        <ConfirmDialog
          title={confirming.clone_of ? "Bu bir klon" : "Düşük eşleşme skoru"}
          body={
            confirming.clone_of
              ? `${confirming.raw_title}, ${confirming.clone_of} klonu olarak bulundu ve sepete kendi kimliğiyle eklenecek. Eklensin mi?`
              : `${confirming.raw_title}, aradığınızla %${confirming.match_score} eşleşti. Yine de eklensin mi?`
          }
          confirmLabel="Sepete ekle"
          onConfirm={() => void addToBasket(confirming, true)}
          onCancel={() => setConfirming(null)}
        />
      )}
    </>
  );
}
