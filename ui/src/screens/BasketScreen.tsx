import { useCallback, useEffect, useMemo, useState } from "react";
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
  SiteScenario,
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
}: {
  version: number;
  config: AppConfig;
  siteNames: Record<string, string>;
  notify: (message: string, kind: "info" | "error") => void;
}) {
  const [data, setData] = useState<BasketResponse | null>(null);
  const [refreshId, setRefreshId] = useState<string | null>(null);
  const [refreshTotal, setRefreshTotal] = useState(0);
  const [refreshDone, setRefreshDone] = useState(0);
  const [refreshNotices, setRefreshNotices] = useState<string[]>([]);
  const [reloads, setReloads] = useState(0);

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
          setRefreshId(null);
          reload();
          break;
      }
    },
    [reload, siteName],
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
        notify(`Fiyat tazeleme başlamadı: ${reason}`, "error");
      },
      [notify],
    ),
  );

  const startRefresh = async () => {
    setRefreshNotices([]);
    setRefreshDone(0);
    setRefreshTotal(0);
    try {
      const start = await api.startBasketRefresh();
      setRefreshTotal(start.total_rows);
      setRefreshId(start.refresh_id);
    } catch (e) {
      notify(e instanceof ApiError ? e.message : String(e), "error");
    }
  };

  const changeQty = async (itemId: number, qty: number) => {
    try {
      if (qty <= 0) await api.removeBasketItem(itemId);
      else await api.setBasketQty(itemId, qty);
      reload();
    } catch (e) {
      notify(e instanceof ApiError ? e.message : String(e), "error");
    }
  };

  const remove = async (itemId: number) => {
    try {
      await api.removeBasketItem(itemId);
      reload();
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

  if (data === null) {
    return <div className="page empty">Sepet okunuyor…</div>;
  }

  if (data.rows.length === 0) {
    return <div className="page empty">Sepet boş.</div>;
  }

  const best = data.best_combination;
  const bestFull = data.report.full[0] ?? null;
  // A one-leg combination is the single-site plan under another name, and two
  // cards saying the same thing is not a comparison.
  const split = best !== null && best.legs.length > 1 ? best : null;
  // Ties go to the single-site plan: one parcel from one shop for the same
  // money is the easier order, so the split has to actually be cheaper to win.
  const splitWins = split !== null && split.diff_kurus !== null && split.diff_kurus < 0;

  return (
    <>
      {refreshId !== null && (
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
            <div className={`plan-card${splitWins ? " win" : ""}`}>
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
                  <span>{siteName(leg.scenario.site_id)}</span>
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
          )}

          {bestFull === null ? (
            <div className="plan-card">
              <div className="plan-card-head">
                <h3>Tek siteden</h3>
              </div>
              <p className="plan-note">
                Sepetin tamamını tek başına karşılayan site yok.
              </p>
            </div>
          ) : (
            <div className={`plan-card${splitWins ? "" : " win"}`}>
              <div className="plan-card-head">
                <h3>Tek siteden</h3>
                <span className="dim">{siteName(bestFull.site_id)}</span>
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
          )}
        </div>

        {data.report.unavailable.length > 0 && (
          <div className="notice warn">
            Hiçbir sitede bulunamayan: {data.report.unavailable.join(", ")}
          </div>
        )}

        <div className="section">
          <table className="matrix">
            <colgroup>
              <col className="c-item" />
              <col className="c-qty" />
              {siteColumns.map((id) => (
                <col key={id} />
              ))}
              <col className="c-remove" />
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
                        <button
                          type="button"
                          aria-label="azalt"
                          onClick={() => void changeQty(row.basket_item_id, row.qty - 1)}
                        >
                          −
                        </button>
                        <span className="qty-value">{row.qty}</span>
                        <button
                          type="button"
                          aria-label="artır"
                          onClick={() => void changeQty(row.basket_item_id, row.qty + 1)}
                        >
                          +
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
                        ) : (
                          formatPriceWhole(row.prices[id] ?? null)
                        )}
                      </td>
                    ))}
                    <td>
                      <button
                        type="button"
                        className="remove-button"
                        aria-label={`${row.label} sepetten çıkarılsın`}
                        onClick={() => void remove(row.basket_item_id)}
                      >
                        ×
                      </button>
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
    </>
  );
}
