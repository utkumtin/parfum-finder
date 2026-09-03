import { motion, useAnimation } from "motion/react";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { ApiError, api } from "../api/client";
import { refusalReason, useEventStream } from "../api/ws";
import { Badge } from "../components/Badge";
import { ProgressBar } from "../components/ProgressBar";
import {
  formatAge,
  formatMl,
  formatPrice,
  formatPriceWhole,
} from "../lib/format";
import type {
  AppConfig,
  BasketRefreshEvent,
  BasketResponse,
  BasketRow,
  SiteScenario,
  SplitLeg,
} from "../types";

/**
 * The cheapest site for one basket line, or null when nothing prices it.
 *
 * Ties keep the first site in column order rather than picking arbitrarily:
 * two shops at the same price are the same answer, and highlighting whichever
 * one a Set happened to yield would move the mark between reloads.
 */
function cheapestSite(prices: Record<string, number>, columns: string[]): string | null {
  let best: string | null = null;
  for (const id of columns) {
    const price = prices[id];
    if (price === undefined) continue;
    if (best === null || price < prices[best]!) best = id;
  }
  return best;
}

/** The circular arrow the row refresh button spins. */
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

const xMarkPathVariants = {
  normal: {
    opacity: 1,
    pathLength: 1,
  },
  animate: {
    opacity: [0, 1],
    pathLength: [0, 1],
  },
};

function CartPreviewCloseIcon() {
  const controls = useAnimation();

  return (
    <svg
      className="cart-preview-close-icon"
      fill="none"
      viewBox="0 0 24 24"
      aria-hidden="true"
      focusable="false"
      onMouseEnter={() => controls.start("animate")}
      onMouseLeave={() => controls.start("normal")}
    >
      <motion.path
        animate={controls}
        d="M6 6l12 12"
        stroke="currentColor"
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth="1.5"
        variants={xMarkPathVariants}
      />
      <motion.path
        animate={controls}
        d="M18 6l-12 12"
        stroke="currentColor"
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth="1.5"
        transition={{ delay: 0.2 }}
        variants={xMarkPathVariants}
      />
    </svg>
  );
}

function OpenAllIcon() {
  return (
    <svg viewBox="0 0 12 12" fill="none" aria-hidden="true" focusable="false">
      <path
        d="M3 9 9 3M4.5 3H9v4.5"
        stroke="currentColor"
        strokeWidth="1.25"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

function Scenario({
  scenario,
  siteName,
  highlight,
}: {
  scenario: SiteScenario;
  siteName: (id: string) => string;
  highlight?: boolean;
}) {
  return (
    <div className="scenario">
      <div className="scenario-head">
        <span className={highlight ? "best-site" : undefined}>
          {siteName(scenario.site_id)}
        </span>
        <span className="dim">
          {scenario.covered}/{scenario.total_items} ürün
        </span>
        <span className="scenario-total">{formatPrice(scenario.total_kurus)}</span>
      </div>
      <div className="scenario-note">
        Ara toplam {formatPrice(scenario.subtotal_kurus)} + kargo{" "}
        {formatPrice(scenario.shipping_kurus)}
        {scenario.free_shipping_gap_kurus !== null &&
          !scenario.free_shipping_met &&
          ` — ${formatPrice(scenario.free_shipping_gap_kurus)} daha eklerseniz kargo bedava`}
        {scenario.notes && ` — ${scenario.notes}`}
      </div>
      {scenario.missing.length > 0 && (
        <div className="scenario-note">Eksik: {scenario.missing.join(", ")}</div>
      )}
    </div>
  );
}

export function BasketScreen({
  version,
  config,
  siteNames,
  notify,
  onBasketChanged,
}: {
  version: number;
  config: AppConfig;
  siteNames: Record<string, string>;
  notify: (message: string, kind: "info" | "error") => void;
  // Adding and removing here changes the count on the Sepet tab, which is
  // owned a level up. Without this the tab keeps the number it had before.
  onBasketChanged: () => void;
}) {
  const [data, setData] = useState<BasketResponse | null>(null);
  const [refreshId, setRefreshId] = useState<string | null>(null);
  const [refreshTotal, setRefreshTotal] = useState(0);
  const [refreshDone, setRefreshDone] = useState(0);
  const [refreshNotices, setRefreshNotices] = useState<string[]>([]);
  const [reloads, setReloads] = useState(0);
  // Which line the running refresh is for, or null when it is the whole
  // basket. Both go through the same session, so this is what tells the row
  // button to spin instead of the bar across the top.
  const [refreshItem, setRefreshItem] = useState<number | null>(null);
  // Lines asked about since this screen was opened. A row whose stalest shop
  // is unreachable never reports an age of zero no matter how often it is
  // refreshed, so age alone would leave its button live forever.
  const [justRefreshed, setJustRefreshed] = useState<Set<number>>(new Set());
  const [undo, setUndo] = useState<BasketRow | null>(null);
  const [cartPreview, setCartPreview] = useState<SplitLeg | null>(null);
  const [cartPreviewClosing, setCartPreviewClosing] = useState(false);
  const cartPreviewCloseTimer = useRef<number | null>(null);

  const siteName = useCallback(
    (id: string) => siteNames[id] ?? id,
    [siteNames],
  );

  useEffect(() => {
    let cancelled = false;
    api
      .basket()
      .then((response) => {
        if (!cancelled) setData(response);
      })
      .catch((e: unknown) => {
        if (!cancelled) notify(e instanceof ApiError ? e.message : String(e), "error");
      });
    return () => {
      cancelled = true;
    };
  }, [reloads, version, notify]);

  const reload = useCallback(() => setReloads((r) => r + 1), []);

  const openCartPreview = useCallback((leg: SplitLeg) => {
    if (cartPreviewCloseTimer.current !== null) {
      window.clearTimeout(cartPreviewCloseTimer.current);
      cartPreviewCloseTimer.current = null;
    }
    setCartPreviewClosing(false);
    setCartPreview(leg);
  }, []);

  const closeCartPreview = useCallback(() => {
    if (cartPreviewCloseTimer.current !== null) return;
    setCartPreviewClosing(true);
    const closeMs = parseFloat(
      getComputedStyle(document.documentElement).getPropertyValue("--modal-close-dur"),
    ) || 150;
    cartPreviewCloseTimer.current = window.setTimeout(() => {
      setCartPreview(null);
      setCartPreviewClosing(false);
      cartPreviewCloseTimer.current = null;
    }, closeMs);
  }, []);

  useEffect(
    () => () => {
      if (cartPreviewCloseTimer.current !== null)
        window.clearTimeout(cartPreviewCloseTimer.current);
    },
    [],
  );

  useEffect(() => {
    if (cartPreview === null) return;
    const onKey = (event: KeyboardEvent) => {
      if (event.key === "Escape") closeCartPreview();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [cartPreview, closeCartPreview]);

  const onRefreshEvent = useCallback(
    (event: BasketRefreshEvent) => {
      switch (event.type) {
        case "refresh_started":
          setRefreshTotal(event.total);
          break;
        case "price_excluded":
          // A null notice is the silent case, and it is silent on purpose: an
          // empty answer is evidence the shop stopped carrying the decant, not
          // a failure to report.
          if (event.notice)
            setRefreshNotices((n) => [...n, `${siteName(event.site_id)}: ${event.notice}`]);
          break;
        case "write_failed":
          setRefreshNotices((n) => [...n, `${siteName(event.site_id)}: ${event.notice}`]);
          break;
        case "row_finished":
          setRefreshDone((d) => d + 1);
          break;
        case "refresh_finished":
          if (refreshItem !== null) {
            const item = refreshItem;
            setJustRefreshed((seen) => new Set(seen).add(item));
          }
          setRefreshId(null);
          setRefreshItem(null);
          reload();
          break;
      }
    },
    [refreshItem, reload, siteName],
  );

  useEventStream<BasketRefreshEvent>(
    refreshId === null ? null : `/api/basket/refresh/${refreshId}`,
    onRefreshEvent,
    useCallback(
      (code: number) => {
        // A refused socket never sends refresh_finished, so without this the
        // progress bar would sit there for good with nothing said.
        const reason = refusalReason(code);
        if (reason === null) return;
        setRefreshId(null);
        setRefreshItem(null);
        notify(`Fiyat tazeleme başlamadı: ${reason}`, "error");
      },
      [notify],
    ),
  );

  const startRefresh = async (itemId?: number) => {
    setRefreshNotices([]);
    setRefreshDone(0);
    setRefreshTotal(0);
    setRefreshItem(itemId ?? null);
    try {
      const start = await api.startBasketRefresh(itemId);
      setRefreshTotal(start.total_rows);
      setRefreshId(start.refresh_id);
    } catch (e) {
      setRefreshItem(null);
      notify(e instanceof ApiError ? e.message : String(e), "error");
    }
  };

  // Dropping below one is what removes a line now that the row has no delete
  // button of its own. The step down from 1 is the destructive one, so it is
  // the press that arms the undo.
  const changeQty = async (row: BasketRow, qty: number) => {
    try {
      if (qty <= 0) {
        await api.removeBasketItem(row.basket_item_id);
        setUndo(row);
      } else {
        await api.setBasketQty(row.basket_item_id, qty);
      }
      reload();
      onBasketChanged();
    } catch (e) {
      notify(e instanceof ApiError ? e.message : String(e), "error");
    }
  };

  // Putting the line back rather than un-deleting it: the prices are stored
  // against the perfume and its size, not against the basket row, so a line
  // added again comes back with everything the table was showing. It lands at
  // the end of the basket, since what it gets back is a fresh added_at.
  const undoRemove = async (row: BasketRow) => {
    try {
      await api.addBasketItem({
        brand: row.brand,
        name: row.name,
        concentration: row.concentration,
        size_ml_x10: row.size_ml_x10,
        qty: row.qty,
        own_identity: true,
        clone_of: "",
        confident: true,
        // Already confirmed once, when it was added the first time.
        confirmed: true,
      });
      setUndo(null);
      reload();
      onBasketChanged();
    } catch (e) {
      notify(e instanceof ApiError ? e.message : String(e), "error");
    }
  };

  // One column per site that can supply at least one line. Sites nobody
  // stocks a line at would be a column of dashes.
  const siteColumns = useMemo(() => {
    const ids = new Set<string>();
    for (const row of data?.rows ?? []) {
      for (const id of Object.keys(row.prices)) ids.add(id);
    }
    return [...ids].sort((a, b) => siteName(a).localeCompare(siteName(b), "tr"));
  }, [data, siteName]);

  // What each column would cost on its own, at the quantities in the basket.
  // Shipping is deliberately not in here: this is the arithmetic of the cells
  // directly above it, and a total nobody can add up by eye is a total that
  // reads as a different number than the one the plan cards quote.
  const siteTotals = useMemo(() => {
    const totals: Record<string, { subtotal: number; covered: number }> = {};
    for (const id of siteColumns) totals[id] = { subtotal: 0, covered: 0 };
    for (const row of data?.rows ?? []) {
      for (const id of siteColumns) {
        const price = row.prices[id];
        if (price === undefined) continue;
        totals[id]!.subtotal += price * row.qty;
        totals[id]!.covered += 1;
      }
    }
    return totals;
  }, [data, siteColumns]);

  // A line nobody could usefully re-price right now: either every shop that
  // stocks it answered today, or we asked them all a moment ago. Greying the
  // button out here is what stops the same question being sent twice.
  const isFresh = (row: BasketRow) =>
    row.age_days === 0 || justRefreshed.has(row.basket_item_id);

  const undoBar = undo !== null && (
    <div className="notice undo">
      <span>{undo.label} sepetten çıkarıldı.</span>
      <button type="button" className="link" onClick={() => void undoRemove(undo)}>
        Geri al
      </button>
    </div>
  );

  if (data === null) {
    return <div className="page empty">Sepet okunuyor…</div>;
  }

  if (data.rows.length === 0) {
    return (
      <div className="page">
        {undoBar}
        <div className="empty">Sepet boş.</div>
      </div>
    );
  }

  const best = data.best_combination;
  const bestFull = data.report.full[0] ?? null;
  // A one-leg combination is the single-site plan under another name, and two
  // cards saying the same thing is not a comparison.
  const split = best !== null && best.legs.length > 1 ? best : null;
  // Ties go to the single-site plan: one parcel from one shop for the same
  // money is the easier order, so the split has to actually be cheaper to win.
  const splitWins = split !== null && split.diff_kurus !== null && split.diff_kurus < 0;
  const cartPreviewRows =
    cartPreview === null
      ? []
      : data.rows.filter((row) => cartPreview.item_ids.includes(row.basket_item_id));
  const cartPreviewProductUrls =
    cartPreview === null
      ? []
      : cartPreviewRows.map((row) => row.product_urls[cartPreview.scenario.site_id]);
  const cartPreviewUrls = [
    ...new Set(
      cartPreviewProductUrls.filter((url): url is string => url !== undefined),
    ),
  ];

  const openCartPreviewItems = () => {
    for (const url of cartPreviewUrls) window.open(url, "_blank", "noopener,noreferrer");
    const missing = cartPreviewProductUrls.filter((url) => url === undefined).length;
    if (missing > 0) {
      notify(
        `${missing} ürünün sayfa bağlantısı bulunamadı.`,
        "error",
      );
    }
  };

  return (
    <>
      {/* Only for the whole basket. One row announces itself by spinning in
          its own cell, and a bar across the window for a single line reads as
          more work than it is. */}
      {refreshId !== null && refreshItem === null && (
        <ProgressBar value={refreshTotal === 0 ? 0 : refreshDone / refreshTotal} />
      )}
      <div className="page">
        <div className="section-head">
          <h2>Sepet</h2>
          <button
            type="button"
            className="button"
            disabled={refreshId !== null}
            onClick={() => void startRefresh()}
          >
            {refreshId !== null ? "Fiyatlar yenileniyor…" : "Fiyatları yenile"}
          </button>
        </div>

        {undoBar}

        {refreshNotices.map((notice, i) => (
          <div key={i} className="notice warn">
            {notice}
          </div>
        ))}

        {/* One site or two is this screen's only question, so its two answers
            sit side by side above the evidence instead of in two sections
            with the matrix between them. */}
        <div className={`plans${split === null || bestFull === null ? " alone" : ""}`}>
          {split !== null && (
            <div className={`tray plan-card${splitWins ? " win" : ""}`}>
              <div className="core">
              <div className="plan-card-head">
                {/* Never "en ucuz": this is a heuristic search's best find, and
                    claiming optimality would be claiming a proof we do not
                    have. */}
                <h3>Bulunan en iyi kombinasyon</h3>
                {splitWins && split.diff_kurus !== null && (
                  <Badge kind="good">{formatPrice(-split.diff_kurus)} daha ucuz</Badge>
                )}
                <span className="plan-total">{formatPrice(split.total_kurus)}</span>
              </div>
              {split.legs.map((leg) => (
                <div key={leg.scenario.site_id} className="plan-leg">
                  <button
                    type="button"
                    className="plan-leg-store"
                    onClick={() => openCartPreview(leg)}
                  >
                    {siteName(leg.scenario.site_id)}
                  </button>
                  <span className="dim">{leg.scenario.covered} ürün</span>
                  <span className="plan-leg-total">
                    {formatPrice(leg.scenario.total_kurus)}
                  </span>
                </div>
              ))}
              {split.omitted_sites.length > 0 && (
                <p className="plan-note">
                  Aramaya girmeyen siteler: {split.omitted_sites.map(siteName).join(", ")}
                </p>
              )}
              </div>
            </div>
          )}

          {bestFull === null ? (
            <div className="tray plan-card">
              <div className="core">
                <div className="plan-card-head">
                  <h3>Tek siteden</h3>
                </div>
                <p className="plan-note">
                  Sepetin tamamını tek başına karşılayan site yok.
                </p>
              </div>
            </div>
          ) : (
            <div className={`tray plan-card${splitWins ? "" : " win"}`}>
              <div className="core">
              <div className="plan-card-head">
                <h3>Tek siteden</h3>
                <button
                  type="button"
                  className="plan-leg-store"
                  onClick={() =>
                    openCartPreview({
                      scenario: bestFull,
                      item_ids: data.rows.map((row) => row.basket_item_id),
                    })
                  }
                >
                  {siteName(bestFull.site_id)}
                </button>
                <span className="plan-total">{formatPrice(bestFull.total_kurus)}</span>
              </div>
              <div className="plan-leg">
                <span>Ara toplam</span>
                <span className="plan-leg-total">
                  {formatPrice(bestFull.subtotal_kurus)}
                </span>
              </div>
              <div className="plan-leg">
                <span>Kargo</span>
                <span className="plan-leg-total">
                  {formatPrice(bestFull.shipping_kurus)}
                </span>
              </div>
              {bestFull.free_shipping_gap_kurus !== null &&
                !bestFull.free_shipping_met && (
                  <p className="plan-note gap">
                    {formatPrice(bestFull.free_shipping_gap_kurus)} daha eklerseniz
                    kargo bedava.
                  </p>
                )}
              {bestFull.notes && <p className="plan-note">{bestFull.notes}</p>}
              </div>
            </div>
          )}
        </div>

        {data.report.unavailable.length > 0 && (
          <div className="notice warn">
            Hiçbir sitede bulunamayan: {data.report.unavailable.join(", ")}
          </div>
        )}

        <div className="section">
          <div className="tray matrix-wrap">
            <div className="core">
          <table className="matrix">
            <colgroup>
              <col className="c-item" />
              <col className="c-qty" />
              {siteColumns.map((id) => (
                <col key={id} />
              ))}
              <col className="c-refresh" />
            </colgroup>
            <thead>
              <tr>
                <th>Ürün</th>
                <th className="num">Adet</th>
                {siteColumns.map((id) => (
                  <th key={id} className="num">
                    {siteName(id)}
                  </th>
                ))}
                <th />
              </tr>
            </thead>
            <tbody>
              {data.rows.map((row) => {
                const cheapest = cheapestSite(row.prices, siteColumns);
                return (
                  <tr key={row.basket_item_id}>
                    <td title={row.label}>
                      <span className="matrix-name">
                        {row.brand} {row.name} {row.concentration} ·{" "}
                        {formatMl(row.size_ml_x10)}
                      </span>
                      {/* A row is only as fresh as its stalest cell, which is
                          what the service already reduced these prices to.
                          Under the name rather than in a column of its own:
                          seven shops need every column the window has. */}
                      <span className="matrix-sub">
                        {row.age_days !== null &&
                        row.age_days >= config.stale_price_days ? (
                          <Badge kind="stale">
                            {formatAge(row.age_days)} güncellendi
                          </Badge>
                        ) : (
                          `${formatAge(row.age_days)} güncellendi`
                        )}
                      </span>
                    </td>
                    <td className="num">
                      <span className="qty">
                        {/* At one, this is the delete: the row has no button
                            of its own for that any more. Saying so in the
                            label is the only warning a screen reader gets. */}
                        {/* A drawn path instead of the "−"/"+" characters: the
                            minus sign and the plus glyph don't share a
                            fallback font, so each one's ink landed at a
                            different height inside the same button box and
                            the stepper looked misaligned from row to row. */}
                        <button
                          type="button"
                          className={row.qty === 1 ? "remove" : undefined}
                          aria-label={row.qty === 1 ? "sepetten çıkar" : "azalt"}
                          title={row.qty === 1 ? "Sepetten çıkar" : undefined}
                          onClick={() => void changeQty(row, row.qty - 1)}
                        >
                          <svg
                            className="qty-icon"
                            viewBox="0 0 12 12"
                            fill="none"
                            stroke="currentColor"
                            strokeWidth="1.5"
                            strokeLinecap="round"
                            aria-hidden="true"
                          >
                            <path d="M1.5 6h9" />
                          </svg>
                        </button>
                        <span className="qty-value">{row.qty}</span>
                        <button
                          type="button"
                          aria-label="artır"
                          onClick={() => void changeQty(row, row.qty + 1)}
                        >
                          <svg
                            className="qty-icon"
                            viewBox="0 0 12 12"
                            fill="none"
                            stroke="currentColor"
                            strokeWidth="1.5"
                            strokeLinecap="round"
                            aria-hidden="true"
                          >
                            <path d="M6 1.5v9M1.5 6h9" />
                          </svg>
                        </button>
                      </span>
                    </td>
                    {siteColumns.map((id) => (
                      <td
                        key={id}
                        className={`num${id === cheapest ? " cheap" : ""}`}
                      >
                        {row.prices[id] === undefined ? (
                          <span className="dim">—</span>
                        ) : id === cheapest ? (
                          // The mark needs something to sit on: a tinted pill
                          // around the number, not a tint on the whole cell,
                          // which at this column width reads as a stripe.
                          <span className="cell">
                            {formatPriceWhole(row.prices[id] ?? null)}
                          </span>
                        ) : (
                          formatPriceWhole(row.prices[id] ?? null)
                        )}
                      </td>
                    ))}
                    <td>
                      {(() => {
                        const spinning =
                          refreshId !== null && refreshItem === row.basket_item_id;
                        const fresh = isFresh(row);
                        return (
                          <button
                            type="button"
                            className={`refresh-button${spinning ? " spinning" : ""}`}
                            disabled={refreshId !== null || fresh}
                            aria-label={`${row.label} fiyatları yenilensin`}
                            title={
                              fresh
                                ? "Fiyatlar güncel"
                                : "Bu satırın fiyatlarını yenile"
                            }
                            onClick={() => void startRefresh(row.basket_item_id)}
                          >
                            <RefreshIcon />
                          </button>
                        );
                      })()}
                    </td>
                  </tr>
                );
              })}
            </tbody>
            <tfoot>
              <tr>
                <td>Ara toplam</td>
                <td />
                {siteColumns.map((id) => {
                  const total = siteTotals[id];
                  const full = total !== undefined && total.covered === data.rows.length;
                  return (
                    <td key={id} className={`num${full ? " full" : ""}`}>
                      {formatPriceWhole(total?.subtotal ?? 0)}
                      <span className="matrix-cover">
                        {total?.covered ?? 0}/{data.rows.length} ürün
                      </span>
                    </td>
                  );
                })}
                <td />
              </tr>
            </tfoot>
          </table>
            </div>
          </div>
          <p className="matrix-note">
            Ara toplamlar adetle çarpılmıştır ve kargo hariçtir; yukarıdaki
            toplamlar kargoyu içerir.
          </p>
        </div>

        {(data.report.full.length > 1 || data.report.partial.length > 0) && (
          <details className="more">
            <summary>Diğer senaryolar</summary>
            {data.report.full.slice(1).map((scenario) => (
              <Scenario key={scenario.site_id} scenario={scenario} siteName={siteName} />
            ))}
            {data.report.partial.map((scenario) => (
              <Scenario key={scenario.site_id} scenario={scenario} siteName={siteName} />
            ))}
          </details>
        )}
      </div>
      {cartPreview !== null && (
        <div className="scrim" onClick={closeCartPreview}>
          <section
            className={`dialog cart-preview-dialog t-modal${
              cartPreviewClosing ? " is-closing" : " is-open"
            }`}
            role="dialog"
            aria-modal="true"
            aria-labelledby="cart-preview-title"
            onClick={(event) => event.stopPropagation()}
          >
            <div className="cart-preview-core">
              <div className="cart-preview-head">
                <div>
                  <p className="cart-preview-kicker">MAĞAZA SEPETİ</p>
                  <h2 id="cart-preview-title">
                    {siteName(cartPreview.scenario.site_id)} için sepet
                  </h2>
                </div>
                <button
                  type="button"
                  className="cart-preview-close"
                  aria-label="Sepet önizlemesini kapat"
                  onClick={closeCartPreview}
                >
                  <CartPreviewCloseIcon />
                </button>
              </div>
              <p className="cart-preview-intro">
                Bu kombinasyonda bu mağazadan alınacak ürünler.
              </p>
              <ul className="cart-preview-items" aria-label="Sepetteki ürünler">
                {cartPreviewRows.map((row) => {
                  const price = row.prices[cartPreview.scenario.site_id];
                  return (
                    <li key={row.basket_item_id}>
                      <span>
                        {row.label}
                        {row.qty > 1 && <small> × {row.qty}</small>}
                      </span>
                      <span>
                        {price === undefined ? "Fiyat bulunamadı" : formatPrice(price * row.qty)}
                      </span>
                    </li>
                  );
                })}
              </ul>
              <dl className="cart-preview-summary">
                <div>
                  <dt>Ara toplam</dt>
                  <dd>{formatPrice(cartPreview.scenario.subtotal_kurus)}</dd>
                </div>
                <div>
                  <dt>Kargo</dt>
                  <dd>{formatPrice(cartPreview.scenario.shipping_kurus)}</dd>
                </div>
                <div className="cart-preview-total">
                  <dt>Toplam</dt>
                  <dd>{formatPrice(cartPreview.scenario.total_kurus)}</dd>
                </div>
              </dl>
              <div className="cart-preview-actions">
                <button
                  type="button"
                  className="button primary cart-preview-open-all"
                  disabled={cartPreviewUrls.length === 0}
                  onClick={openCartPreviewItems}
                >
                  Tüm ürün sayfalarını aç
                  <span className="button-pip">
                    <OpenAllIcon />
                  </span>
                </button>
              </div>
            </div>
          </section>
        </div>
      )}
    </>
  );
}
