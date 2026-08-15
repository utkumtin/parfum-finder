import { useCallback, useEffect, useMemo, useState } from "react";
import { ApiError, api } from "../api/client";
import { refusalReason, useEventStream } from "../api/ws";
import { Badge } from "../components/Badge";
import { ProgressBar } from "../components/ProgressBar";
import { formatAge, formatMl, formatPrice } from "../lib/format";
import type {
  AppConfig,
  BasketRefreshEvent,
  BasketResponse,
  SiteScenario,
} from "../types";

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

  if (data === null) {
    return <div className="page empty">Sepet okunuyor…</div>;
  }

  if (data.rows.length === 0) {
    return <div className="page empty">Sepet boş.</div>;
  }

  const best = data.best_combination;
  const bestFull = data.report.full[0] ?? null;

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

        <div className="matrix-wrap section">
          <table className="rows">
            <thead>
              <tr>
                <th>Ürün</th>
                <th className="num">Adet</th>
                {siteColumns.map((id) => (
                  <th key={id} className="num">
                    {siteName(id)}
                  </th>
                ))}
                <th>Güncellik</th>
                <th />
              </tr>
            </thead>
            <tbody>
              {data.rows.map((row) => (
                <tr key={row.basket_item_id}>
                  <td className="title-cell" title={row.label}>
                    {row.brand} {row.name} {row.concentration}{" "}
                    <span className="dim">{formatMl(row.size_ml_x10)}</span>
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
                    <td key={id} className="num">
                      {row.prices[id] === undefined ? (
                        <span className="dim">—</span>
                      ) : (
                        formatPrice(row.prices[id] ?? null)
                      )}
                    </td>
                  ))}
                  <td>
                    {/* A row is only as fresh as its stalest cell, which is
                        what the service already reduced these prices to. */}
                    {row.age_days !== null && row.age_days >= config.stale_price_days ? (
                      <Badge kind="stale">{formatAge(row.age_days)}</Badge>
                    ) : (
                      <span className="dim">{formatAge(row.age_days)}</span>
                    )}
                  </td>
                  <td className="add-cell">
                    <button
                      type="button"
                      className="button quiet"
                      onClick={() => void remove(row.basket_item_id)}
                    >
                      sil
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <section className="section">
          <div className="section-head">
            <h2>Tek siteden alırsanız</h2>
          </div>
          {bestFull === null ? (
            <div className="notice">Sepetin tamamını tek başına karşılayan site yok.</div>
          ) : (
            <Scenario scenario={bestFull} siteName={siteName} highlight />
          )}
          {data.report.unavailable.length > 0 && (
            <div className="notice warn">
              Hiçbir sitede bulunamayan: {data.report.unavailable.join(", ")}
            </div>
          )}
        </section>

        {best !== null && best.legs.length > 0 && (
          <section className="section">
            <div className="section-head">
              {/* Never "en ucuz": this is a heuristic search's best find, and
                  claiming optimality would be claiming a proof we do not have. */}
              <h2>Bulunan en iyi kombinasyon</h2>
            </div>
            {best.legs.map((leg) => (
              <Scenario
                key={leg.scenario.site_id}
                scenario={leg.scenario}
                siteName={siteName}
              />
            ))}
            <div className="scenario">
              <div className="scenario-head">
                <span>Toplam</span>
                <span className="scenario-total">{formatPrice(best.total_kurus)}</span>
              </div>
              {best.diff_kurus !== null && best.best_full_site !== null && (
                <div className="scenario-note">
                  {best.diff_kurus < 0
                    ? `${siteName(best.best_full_site.site_id)} tek başına aldığınızdan ${formatPrice(-best.diff_kurus)} DAHA UCUZ`
                    : best.diff_kurus > 0
                      ? `${siteName(best.best_full_site.site_id)} tek başına aldığınızdan ${formatPrice(best.diff_kurus)} DAHA PAHALI`
                      : `${siteName(best.best_full_site.site_id)} tek başına aldığınızla aynı fiyat`}
                </div>
              )}
              {best.omitted_sites.length > 0 && (
                <div className="scenario-note">
                  Aramaya girmeyen siteler: {best.omitted_sites.map(siteName).join(", ")}
                </div>
              )}
            </div>
          </section>
        )}

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
