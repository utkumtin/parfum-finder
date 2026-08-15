import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { ApiError, api } from "../api/client";
import { refusalReason, useEventStream } from "../api/ws";
import { AddButton } from "../components/AddButton";
import { Badge } from "../components/Badge";
import { ConfirmDialog } from "../components/ConfirmDialog";
import { ProgressBar } from "../components/ProgressBar";
import { formatAge, formatMl, formatPerMl, formatPrice } from "../lib/format";
import type {
  AcceptedSearch,
  AppConfig,
  ResultRow,
  ScanEvent,
  SortKey,
} from "../types";

interface Notice {
  kind: "warn" | "error" | "info";
  text: string;
}

interface Block {
  queryIndex: number;
  product: string;
  rows: ResultRow[];
}

/**
 * Rows into the blocks the table draws, by walking them in the order the
 * server sent.
 *
 * Both orders ranking.py can return keep (query_index, product) as their two
 * outermost keys, so a block is always a run of neighbours. Re-grouping with a
 * map would throw away the very ordering the request was made for.
 */
function toBlocks(rows: ResultRow[]): Block[] {
  const blocks: Block[] = [];
  for (const row of rows) {
    const last = blocks[blocks.length - 1];
    if (last && last.queryIndex === row.query_index && last.product === row.product) {
      last.rows.push(row);
    } else {
      blocks.push({ queryIndex: row.query_index, product: row.product, rows: [row] });
    }
  }
  return blocks;
}

const SORT_LABELS: { key: SortKey; label: string; numeric: boolean }[] = [
  { key: "ml", label: "ml", numeric: true },
  { key: "price", label: "Fiyat", numeric: true },
  { key: "per_ml", label: "₺/ml", numeric: true },
];

export function ResultsScreen({
  searchId,
  searches,
  rejected,
  config,
  onBasketChanged,
  notify,
}: {
  searchId: string;
  searches: AcceptedSearch[];
  rejected: string[];
  config: AppConfig;
  onBasketChanged: () => void;
  notify: (message: string, kind: "info" | "error") => void;
}) {
  const [rows, setRows] = useState<ResultRow[]>([]);
  const [finished, setFinished] = useState(false);
  const [sort, setSort] = useState<SortKey | null>(null);
  const [revision, setRevision] = useState(0);
  const [totals, setTotals] = useState({ sites: 0, perfumes: 0 });
  const [done, setDone] = useState(0);
  const [errorCount, setErrorCount] = useState(0);
  const [notices, setNotices] = useState<Record<number, Notice[]>>({});
  const [missing, setMissing] = useState<Record<number, string[]>>({});
  const [confirming, setConfirming] = useState<ResultRow | null>(null);
  const [streamRefusal, setStreamRefusal] = useState<string | null>(null);

  const timerRef = useRef<number | null>(null);

  // Rows arrive site by site, and each arrival can change which site a block
  // leads with -- that order is computed over every row at once by ranking.py
  // and cannot be reproduced from a stream. So the table is re-read from the
  // server instead, coalesced to a quarter second so a fast scan does not turn
  // into one request per request.
  const scheduleRefresh = useCallback((immediate = false) => {
    if (immediate) {
      if (timerRef.current !== null) window.clearTimeout(timerRef.current);
      timerRef.current = null;
      setRevision((r) => r + 1);
      return;
    }
    if (timerRef.current !== null) return;
    timerRef.current = window.setTimeout(() => {
      timerRef.current = null;
      setRevision((r) => r + 1);
    }, 250);
  }, []);

  useEffect(() => {
    return () => {
      if (timerRef.current !== null) window.clearTimeout(timerRef.current);
    };
  }, []);

  const addNotice = useCallback((queryIndex: number, notice: Notice) => {
    setNotices((current) => ({
      ...current,
      [queryIndex]: [...(current[queryIndex] ?? []), notice],
    }));
  }, []);

  const onEvent = useCallback(
    (event: ScanEvent) => {
      switch (event.type) {
        case "scan_started":
          setTotals({ sites: event.total_sites, perfumes: event.total_perfumes });
          break;
        case "site_started":
          break;
        case "cache_hit":
          addNotice(event.query_index, {
            kind: "info",
            text: `Kayıttan geldi, ${formatAge(event.age_days)} okundu. Yeniden taramak için aramayı "kayıttakileri de yeniden tara" ile başlatın.`,
          });
          scheduleRefresh();
          break;
        case "rows_ready":
          scheduleRefresh();
          break;
        case "site_finished":
          setDone((d) => d + 1);
          if (event.status === "suspect") {
            // Never a silent empty answer: a site that answered in a shape we
            // could not read is a profile that may have gone stale, and that
            // has to be visible or the missing prices read as "not sold here".
            setErrorCount((c) => c + 1);
            addNotice(event.query_index, {
              kind: "warn",
              text: `${event.site_id}: bu profil bozulmuş olabilir${
                event.detail ? ` — ${event.detail}` : ""
              }`,
            });
          } else if (event.status === "error") {
            setErrorCount((c) => c + 1);
            addNotice(event.query_index, {
              kind: "error",
              text: `${event.site_id}: aranamadı${
                event.detail ? ` — ${event.detail}` : ""
              }`,
            });
          } else if (!event.has_rows) {
            setMissing((current) => ({
              ...current,
              [event.query_index]: [
                ...(current[event.query_index] ?? []),
                event.site_id,
              ],
            }));
          }
          break;
        case "write_failed":
          setErrorCount((c) => c + 1);
          addNotice(event.query_index, {
            kind: "warn",
            text: `${event.site_id}: fiyatlar tabloya geldi ama kayda yazılamadı`,
          });
          break;
        case "scan_finished":
          setErrorCount(event.error_count);
          scheduleRefresh(true);
          break;
      }
    },
    [addNotice, scheduleRefresh],
  );

  const onStreamClosed = useCallback((code: number) => {
    // A refused socket means the scan never started. Nothing further is
    // coming, and a progress bar left running would be the screen's way of
    // saying it is still working when it is not.
    const reason = refusalReason(code);
    if (reason === null) return;
    setStreamRefusal(reason);
    setFinished(true);
  }, []);

  useEventStream<ScanEvent>(`/api/search/${searchId}`, onEvent, onStreamClosed);

  useEffect(() => {
    let cancelled = false;
    api
      .results(searchId, sort)
      .then((response) => {
        if (cancelled) return;
        setRows(response.rows);
        setFinished(response.finished);
      })
      .catch((e: unknown) => {
        if (!cancelled) notify(e instanceof ApiError ? e.message : String(e), "error");
      });
    return () => {
      cancelled = true;
    };
  }, [searchId, sort, revision, notify]);

  const blocks = useMemo(() => toBlocks(rows), [rows]);

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
      } catch (e) {
        if (e instanceof ApiError && e.status === 409) {
          // The server refuses a clone or a weak match that has not been
          // acknowledged. It does so whether or not this screen asked first,
          // so the modal explains the refusal rather than guarding it.
          setConfirming(row);
          return false;
        }
        setConfirming(null);
        notify(e instanceof ApiError ? e.message : String(e), "error");
        return false;
      }
    },
    [notify, onBasketChanged],
  );

  const totalUnits = totals.sites * totals.perfumes;
  const progress = totalUnits === 0 ? (finished ? 1 : 0) : Math.min(1, done / totalUnits);

  const toggleSort = (key: SortKey) => setSort((current) => (current === key ? null : key));

  return (
    <>
      {!finished && <ProgressBar value={progress} />}
      <div className="page">
        {rejected.length > 0 && (
          <div className="notice error">
            Okunamayan parça atlandı: {rejected.join("; ")}
          </div>
        )}
        {streamRefusal !== null && (
          <div className="notice error">Tarama başlamadı: {streamRefusal}</div>
        )}
        {finished && errorCount > 0 && (
          <div className="notice warn">{errorCount} hata ile bitti</div>
        )}

        {searches.map((search) => {
          const searchBlocks = blocks.filter((b) => b.queryIndex === search.index);
          const searchNotices = notices[search.index] ?? [];
          const notFound = missing[search.index] ?? [];
          return (
            <section key={search.index} className="section">
              <div className="section-head">
                <h2>{search.text}</h2>
              </div>
              {searchNotices.map((notice, i) => (
                <div
                  key={i}
                  className={`notice${notice.kind === "info" ? "" : ` ${notice.kind}`}`}
                >
                  {notice.text}
                </div>
              ))}
              {notFound.length > 0 && (
                <div className="notice">
                  Bulunamadı: {[...new Set(notFound)].join(", ")}
                </div>
              )}
              {searchBlocks.length === 0 ? (
                <p className="dim">
                  {finished ? "Hiçbir sitede bulunamadı." : "Aranıyor…"}
                </p>
              ) : (
                /* One table for every block of a perfume, not one per block:
                   a table sizes its own columns, so separate tables would put
                   each block's prices at a different place on the line and
                   nothing could be read down a column. */
                <table className="rows">
                  <thead>
                    <tr>
                      <th>Ürün</th>
                      <th>Site</th>
                      {SORT_LABELS.map(({ key, label }) => (
                        <th
                          key={key}
                          className="num sortable"
                          aria-sort={sort === key ? "ascending" : "none"}
                          onClick={() => toggleSort(key)}
                        >
                          {label}
                        </th>
                      ))}
                      <th className="num">%</th>
                      <th>Güncellik</th>
                      <th />
                    </tr>
                  </thead>
                  {searchBlocks.map((block) => (
                    <tbody key={`${block.queryIndex}-${block.product}`}>
                      <tr className="block-head-row">
                        <th colSpan={8} scope="colgroup">
                          <span className="block-title">{block.product}</span>
                          <span className="block-note">{block.rows.length} boy</span>
                        </th>
                      </tr>
                      {block.rows.map((row) => (
                          <tr
                            key={`${row.site_id}-${row.raw_title}-${row.size_ml_x10}`}
                            className={row.product_url ? "clickable" : ""}
                            onClick={() => {
                              if (row.product_url)
                                window.open(row.product_url, "_blank", "noopener");
                            }}
                          >
                            <td className="title-cell" title={row.raw_title}>
                              {row.raw_title}{" "}
                              {row.clone_of && (
                                <Badge kind="clone">klon: {row.clone_of}</Badge>
                              )}
                              {!row.confident && (
                                <Badge kind="weak" title="düşük eşleşme skoru">
                                  zayıf eşleşme
                                </Badge>
                              )}
                            </td>
                            <td className="site-cell">{row.site_label}</td>
                            <td className="num">{formatMl(row.size_ml_x10)}</td>
                            <td className="num">{formatPrice(row.price_kurus)}</td>
                            <td className="num">{formatPerMl(row.price_per_ml_kurus)}</td>
                            <td className="num dim">{row.match_score}</td>
                            <td>
                              {row.age_days >= config.stale_price_days ? (
                                <Badge kind="stale">{formatAge(row.age_days)}</Badge>
                              ) : (
                                <span className="dim">{formatAge(row.age_days)}</span>
                              )}
                            </td>
                            <td className="add-cell">
                              <AddButton onAdd={() => addToBasket(row, false)} />
                            </td>
                          </tr>
                      ))}
                    </tbody>
                  ))}
                </table>
              )}
            </section>
          );
        })}
      </div>

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
