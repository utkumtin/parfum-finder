import { useCallback, useEffect, useMemo, useState } from "react";
import { ApiError, api } from "../api/client";
import { AddButton } from "../components/AddButton";
import { Badge } from "../components/Badge";
import { ConfirmDialog } from "../components/ConfirmDialog";
import { WishlistButton } from "../components/WishlistButton";
import { basketKey } from "../lib/basket";
import { formatAge, formatMl, formatPerMl, formatPrice } from "../lib/format";
import { wishlistKey } from "../lib/wishlist";
import type { AppConfig, ResultRow } from "../types";

export function WishlistScreen({
  rows,
  wishlistReady,
  pendingWishlistKeys,
  config,
  notify,
  onBasketChanged,
  onWishlistToggle,
}: {
  rows: ResultRow[];
  wishlistReady: boolean;
  pendingWishlistKeys: Set<string>;
  config: AppConfig;
  notify: (message: string, kind: "info" | "error") => void;
  onBasketChanged: () => void;
  onWishlistToggle: (row: ResultRow) => void | Promise<void>;
}) {
  const [basketKeys, setBasketKeys] = useState<Set<string>>(new Set());
  const [confirming, setConfirming] = useState<ResultRow | null>(null);
  const [sort, setSort] = useState<"price" | "per_ml" | null>(null);

  const sortedRows = useMemo(() => {
    if (sort === null) return rows;
    return rows
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
  }, [rows, sort]);

  useEffect(() => {
    let cancelled = false;
    api
      .basket()
      .then((response) => {
        if (!cancelled) setBasketKeys(new Set(response.rows.map(basketKey)));
      })
      .catch(() => {});
    return () => {
      cancelled = true;
    };
  }, []);

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
        setBasketKeys((current) => new Set(current).add(basketKey(row)));
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
          {rows.length > 0 && <span className="section-count">{rows.length} ürün</span>}
        </div>

        {!wishlistReady ? (
          <p className="dim">İstek listesi yükleniyor…</p>
        ) : rows.length === 0 ? (
          <p className="dim">Henüz istek listenize ürün eklemediniz.</p>
        ) : (
          <div className="tray table-tray">
            <div className="core">
              <table className="rows wishlist-rows">
                <colgroup>
                  <col style={{ width: "33%" }} />
                  <col style={{ width: "16%" }} />
                  <col style={{ width: "9%" }} />
                  <col style={{ width: "14%" }} />
                  <col style={{ width: "12%" }} />
                  <col style={{ width: "7%" }} />
                  <col style={{ width: "9%" }} />
                </colgroup>
                <thead>
                  <tr>
                    <th>Ürün</th>
                    <th>Site</th>
                    <th className="num">ml</th>
                    <th
                      className="num sortable"
                      aria-sort={sort === "price" ? "ascending" : "none"}
                      onClick={() => setSort((current) => (current === "price" ? null : "price"))}
                    >
                      Fiyat<span className="sort-arrow" aria-hidden="true">▲</span>
                    </th>
                    <th
                      className="num sortable"
                      aria-sort={sort === "per_ml" ? "ascending" : "none"}
                      onClick={() => setSort((current) => (current === "per_ml" ? null : "per_ml"))}
                    >
                      ₺/ml<span className="sort-arrow" aria-hidden="true">▲</span>
                    </th>
                    <th>Güncellik</th>
                    <th />
                  </tr>
                </thead>
                <tbody>
                  {sortedRows.map((row) => (
                    <tr
                      key={wishlistKey(row)}
                      className={row.product_url ? "clickable" : ""}
                      onClick={() => {
                        if (row.product_url)
                          window.open(row.product_url, "_blank", "noopener");
                      }}
                    >
                      <td className="title-cell" title={row.raw_title}>
                        <span className="title-inner">
                          <span className="title-text">{row.raw_title}</span>
                          {row.product_url && (
                            <span className="row-go" aria-hidden="true">
                              <svg viewBox="0 0 12 12" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round">
                                <path d="M3 9 9 3M4.5 3H9v4.5" />
                              </svg>
                            </span>
                          )}
                        </span>
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
                      <td className="add-cell">
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
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
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
