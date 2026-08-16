import { useCallback, useEffect, useMemo, useState } from "react";
import { ApiError, api } from "../api/client";
import { refusalReason, useEventStream } from "../api/ws";
import { AddButton } from "../components/AddButton";
import { Badge } from "../components/Badge";
import { ConfirmDialog } from "../components/ConfirmDialog";
import { ScanStatus } from "../components/ScanStatus";
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

/** The sizes a trial buy is offered in, smallest first, in tenths of a ml. */
const TRIAL_SIZES_ML_X10 = [30, 50];

/**
 * Identifies a row against a basket line the same way store.py's
 * add_basket_item does: brand, name, concentration and size together are
 * the basket's own uniqueness key, so matching on anything narrower could
 * mark the wrong size as already added.
 */
function basketKey(
  item: Pick<ResultRow, "brand" | "name" | "concentration" | "size_ml_x10">,
): string {
  return `${item.brand}|${item.name}|${item.concentration}|${item.size_ml_x10}`;
}

interface Verdicts {
  /** Lowest price per ml: what to buy when the intent is to wear it. */
  rate: ResultRow | null;
  /** Least money that answers "what does this smell like", and its size. */
  trial: ResultRow | null;
}

/**
 * The two rows a block's answer reduces to.
 *
 * Scoped to one block rather than to everything a query matched, because a
 * block is one bottle: a search for "Dior Sauvage EDP" also turns up Sauvage
 * Elixir, and letting the Elixir win this comparison would be answering a
 * question nobody asked. Clones are out for the same reason, and they would
 * win every time on rate alone.
 *
 * `trial` walks 3 ml then 5 ml, the two sizes the shops sell as samples. When
 * neither exists there is nothing to recommend that the rate verdict does not
 * already say, so it stays null and the card does not render.
 */
function pickVerdicts(rows: ResultRow[]): Verdicts {
  // Zero is filtered, not just null: nothing stops a misread page from
  // storing a price of 0, and a free bottle would win both verdicts outright
  // while making the rate the trial card divides by a zero.
  const priced = rows.filter(
    (r) =>
      r.price_kurus !== null &&
      r.price_kurus > 0 &&
      r.price_per_ml_kurus !== null &&
      Number(r.price_per_ml_kurus) > 0 &&
      !r.clone_of,
  );
  if (priced.length === 0) return { rate: null, trial: null };

  const rate = priced.reduce((best, row) =>
    Number(row.price_per_ml_kurus) < Number(best.price_per_ml_kurus) ? row : best,
  );

  let trial: ResultRow | null = null;
  for (const size of TRIAL_SIZES_ML_X10) {
    const sized = priced.filter((r) => r.size_ml_x10 === size);
    if (sized.length === 0) continue;
    trial = sized.reduce((best, row) =>
      (row.price_kurus ?? 0) < (best.price_kurus ?? 0) ? row : best,
    );
    break;
  }
  // The same row twice is one fact stated twice, so the second card goes.
  return { rate, trial: trial === rate ? null : trial };
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
  // Which rows already sit in the basket, so the add button can show a
  // checkmark that reflects the basket's real state instead of a timer.
  const [basketKeys, setBasketKeys] = useState<Set<string>>(new Set());

  useEffect(() => {
    let cancelled = false;
    api
      .basket()
      .then((response) => {
        if (cancelled) return;
        setBasketKeys(new Set(response.rows.map(basketKey)));
      })
      .catch(() => {
        // Not fatal: rows just show "+" until the next mount re-checks.
      });
    return () => {
      cancelled = true;
    };
  }, []);

  // Rows land once, all together, when the scan is done -- the same table
  // the TUI paints in one go rather than one site at a time. A block's
  // ordering is computed over every row at once by ranking.py and cannot be
  // reproduced from a stream, and a table reshuffling under a reader as
  // sites trickle in cannot be read: the cheapest row keeps changing, and
  // the row someone is looking at keeps moving out from under them.
  const refresh = useCallback(() => setRevision((r) => r + 1), []);

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
          break;
        case "rows_ready":
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
          refresh();
          break;
      }
    },
    [addNotice, refresh],
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
        setBasketKeys((prev) => new Set(prev).add(basketKey(row)));
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

  const toggleSort = (key: SortKey) => setSort((current) => (current === key ? null : key));

  return (
    <>
      <div className="page">
        {rejected.length > 0 && (
          <div className="notice error">
            Okunamayan parça atlandı: {rejected.join("; ")}
          </div>
        )}
        {streamRefusal !== null && (
          <div className="notice error">Tarama başlamadı: {streamRefusal}</div>
        )}
        {!finished && (
          <ScanStatus done={done} total={totalUnits} errorCount={errorCount} />
        )}
        {finished && errorCount > 0 && (
          <div className="notice warn">{errorCount} hata ile bitti</div>
        )}

        {searches.map((search) => {
          const searchBlocks = blocks.filter((b) => b.queryIndex === search.index);
          const searchNotices = notices[search.index] ?? [];
          const notFound = missing[search.index] ?? [];
          // The leading block is the bottle ranking.py decided the query was
          // asking about, so it is the one the verdicts speak for.
          const verdicts = pickVerdicts(searchBlocks[0]?.rows ?? []);
          const cheapestPerMl =
            verdicts.rate === null ? null : Number(verdicts.rate.price_per_ml_kurus);
          // The headline card leads with a sample size over the raw best
          // rate: a shopper skimming the top of the screen reads "3 ml" as an
          // answer to "what would trying this cost me", while the true
          // cheapest ₺/ml stays the table's own cheapest-row marker below.
          // Falls back to the true rate only when nothing is sold at 3 ml or
          // 5 ml at all. This absorbs the old separate trial card: whenever a
          // 3 ml or 5 ml row exists, headline already is that row, so a
          // second "en ucuz Xml" card would only repeat it.
          const headline = verdicts.trial ?? verdicts.rate;
          return (
            <section key={search.index} className="section">
              <div className="section-head">
                <h2>{search.text}</h2>
              </div>

              {headline && (
                <div className="verdicts alone">
                  <div className="verdict rate">
                    <span className="verdict-body">
                      <span className="verdict-kicker">
                        En iyi {formatMl(headline.size_ml_x10)} fiyatı
                      </span>
                      <span className="verdict-figure">
                        <b>{formatPrice(headline.price_kurus)}</b>
                      </span>
                      <span className="verdict-where">
                        {headline.site_label} ·{" "}
                        {formatPerMl(headline.price_per_ml_kurus)}
                      </span>
                    </span>
                    <button
                      type="button"
                      className="button small"
                      onClick={() => void addToBasket(headline, false)}
                    >
                      Sepete ekle
                    </button>
                  </div>
                </div>
              )}
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
                          {sort === key && <span className="sort-arrow" aria-hidden="true">▲</span>}
                        </th>
                      ))}
                      <th>Güncellik</th>
                      <th />
                    </tr>
                  </thead>
                  {searchBlocks.map((block) => (
                    <tbody key={`${block.queryIndex}-${block.product}`}>
                      <tr className="block-head-row">
                        <th colSpan={7} scope="colgroup">
                          <span className="block-title">{block.product}</span>
                          <span className="block-note">{block.rows.length} boy</span>
                        </th>
                      </tr>
                      {block.rows.map((row) => (
                          <tr
                            // The identity the backend already dedupes rows on,
                            // not the title: two different perfumes can share a
                            // raw title on the same site and size, and a
                            // colliding key is what makes React reuse a row's
                            // DOM node for another row instead of rendering it,
                            // which reads as a duplicate that won't reorder.
                            key={`${row.query_index}-${row.site_id}-${row.brand}-${row.name}-${row.concentration}-${row.size_ml_x10}`}
                            className={[
                              row.product_url ? "clickable" : "",
                              row === verdicts.rate ? "cheapest" : "",
                            ]
                              .filter(Boolean)
                              .join(" ")}
                            onClick={() => {
                              if (row.product_url)
                                window.open(row.product_url, "_blank", "noopener");
                            }}
                          >
                            <td className="title-cell" title={row.raw_title}>
                              {/* The title truncates, the badges do not: a
                                  shop title long enough to need an ellipsis
                                  was swallowing the very mark that says this
                                  row is the answer. */}
                              <span className="title-inner">
                              <span className="title-text">{row.raw_title}</span>
                              {row === verdicts.rate && (
                                <Badge kind="value">en iyi ₺/ml</Badge>
                              )}
                              {row === verdicts.trial && (
                                <Badge kind="value">
                                  en ucuz {formatMl(row.size_ml_x10)}
                                </Badge>
                              )}
                              {row.clone_of && (
                                <Badge kind="clone">klon: {row.clone_of}</Badge>
                              )}
                              {!row.confident && (
                                <Badge kind="weak" title="düşük eşleşme skoru">
                                  zayıf eşleşme
                                </Badge>
                              )}
                              </span>
                            </td>
                            <td className="site-cell">{row.site_label}</td>
                            <td className="num">{formatMl(row.size_ml_x10)}</td>
                            <td className="num">{formatPrice(row.price_kurus)}</td>
                            <td className="num perml">
                              {/* Sized against the block's own cheapest row, so
                                  the bar compares bottles that are actually
                                  comparable rather than the whole screen. */}
                              <span
                                className={`perml-bar${row.clone_of ? " clone-bar" : ""}`}
                                aria-hidden="true"
                                style={{
                                  width:
                                    cheapestPerMl === null ||
                                    row.price_per_ml_kurus === null
                                      ? 0
                                      : `${Math.min(
                                          100,
                                          (cheapestPerMl /
                                            Number(row.price_per_ml_kurus)) *
                                            100,
                                        )}%`,
                                }}
                              />
                              <span
                                className={`perml-value${row.clone_of ? " dim" : ""}`}
                              >
                                {formatPerMl(row.price_per_ml_kurus)}
                              </span>
                            </td>
                            <td>
                              {row.age_days >= config.stale_price_days ? (
                                <Badge kind="stale">{formatAge(row.age_days)}</Badge>
                              ) : (
                                <span className="dim">{formatAge(row.age_days)}</span>
                              )}
                            </td>
                            <td className="add-cell">
                              <AddButton
                                onAdd={() => addToBasket(row, false)}
                                inBasket={basketKeys.has(basketKey(row))}
                              />
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
