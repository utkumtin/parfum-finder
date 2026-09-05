import { useCallback, useEffect, useLayoutEffect, useRef, useState } from "react";
import { ApiError, api } from "./api/client";
import { UpdateDialog } from "./components/UpdateDialog";
import { BookmarkIcon } from "./components/BookmarkIcon";
import { BasketScreen } from "./screens/BasketScreen";
import { ResultsScreen } from "./screens/ResultsScreen";
import { SearchScreen } from "./screens/SearchScreen";
import { WishlistScreen } from "./screens/WishlistScreen";
import {
  ensureBasket,
  invalidateBasket,
  useBasketSnapshot,
} from "./lib/basketStore";
import { wishlistKey } from "./lib/wishlist";
import type {
  AppConfig,
  ResultRow,
  SearchStart,
  SiteSummary,
  SortKey,
  UpdateInfo,
  WishlistRow,
} from "./types";

type View = "search" | "results" | "wishlist" | "basket";

interface Toast {
  message: string;
  kind: "info" | "error";
}

export function App() {
  const [config, setConfig] = useState<AppConfig | null>(null);
  const [sites, setSites] = useState<SiteSummary[]>([]);
  const [siteNames, setSiteNames] = useState<Record<string, string>>({});
  const [startupError, setStartupError] = useState<string | null>(null);
  const [view, setView] = useState<View>("search");
  const [searchText, setSearchText] = useState("");
  const [search, setSearch] = useState<SearchStart | null>(null);
  const [resultsSort, setResultsSort] = useState<SortKey | null>(null);
  const [wishlistQuery, setWishlistQuery] = useState("");
  const [wishlistSort, setWishlistSort] = useState<"price" | "per_ml" | null>(null);
  const [wishlist, setWishlist] = useState<WishlistRow[]>([]);
  const [wishlistReady, setWishlistReady] = useState(false);
  const [pendingWishlistKeys, setPendingWishlistKeys] = useState<Set<string>>(
    new Set(),
  );
  const [toast, setToast] = useState<Toast | null>(null);
  const basketSnapshot = useBasketSnapshot();
  const basketCount = basketSnapshot.data?.rows.length ?? 0;
  const [update, setUpdate] = useState<UpdateInfo | null>(null);
  const tabsRef = useRef<HTMLElement>(null);
  const pendingWishlistRef = useRef<Set<string>>(new Set());
  const hasPositionedTabPill = useRef(false);
  const lastPillView = useRef<View | null>(null);

  const notify = useCallback((message: string, kind: "info" | "error") => {
    setToast({ message, kind });
    window.setTimeout(() => setToast(null), 3000);
  }, []);

  const measureTabPill = useCallback((animate: boolean) => {
    const tabs = tabsRef.current;
    const pill = tabs?.querySelector<HTMLElement>(".tab-pill");
    const activeTab = tabs?.querySelector<HTMLButtonElement>(
      '.tab[aria-current="page"]',
    );

    if (!pill || !activeTab) return;

    const nextTransform = `translateX(${activeTab.offsetLeft}px)`;
    const nextWidth = `${activeTab.offsetWidth}px`;
    const transformChanged = pill.style.transform !== nextTransform;
    const widthChanged = pill.style.width !== nextWidth;
    if (!transformChanged && !widthChanged) return;

    // Browsers keep an in-flight transition's rendered value as the start
    // frame when both targets are changed together. ResizeObserver callbacks
    // therefore retarget the motion instead of cancelling it.
    const activeAnimations = pill.getAnimations?.().some(
      (animation) => animation.playState === "running" || animation.pending,
    );
    if (animate || activeAnimations) {
      pill.style.transform = nextTransform;
      pill.style.width = nextWidth;
      return;
    }

    // Settled geometry corrections are immediate, including count changes.
    const previousTransition = pill.style.transition;
    pill.style.transition = "none";
    pill.style.transform = nextTransform;
    pill.style.width = nextWidth;
    void pill.offsetWidth;
    pill.style.transition = previousTransition;
  }, []);

  useLayoutEffect(() => {
    const animate =
      hasPositionedTabPill.current &&
      lastPillView.current !== null &&
      lastPillView.current !== view;
    measureTabPill(animate);
    hasPositionedTabPill.current = true;
    lastPillView.current = view;
  }, [basketCount, config, measureTabPill, view, wishlist.length]);

  useEffect(() => {
    const tabs = tabsRef.current;
    if (!tabs || typeof ResizeObserver === "undefined") return;

    const observer = new ResizeObserver(() => measureTabPill(false));
    observer.observe(tabs);
    for (const tab of tabs.querySelectorAll<HTMLElement>(".tab")) {
      observer.observe(tab);
    }
    return () => observer.disconnect();
  }, [config, measureTabPill]);

  useEffect(() => {
    Promise.all([api.config(), api.sites()])
      .then(([loadedConfig, sites]) => {
        setConfig(loadedConfig);
        setSites(sites);
        setSiteNames(Object.fromEntries(sites.map((s) => [s.id, s.name])));
      })
      .catch((e: unknown) => {
        setStartupError(e instanceof ApiError ? e.message : String(e));
      });
  }, []);

  // Deliberately not part of the startup Promise.all above: that one gates the
  // whole app on its result, and an offline machine or a GitHub outage must
  // not turn into a window that refuses to open.
  useEffect(() => {
    let cancelled = false;
    api
      .update()
      .then((info) => {
        if (!cancelled && info.update_available) setUpdate(info);
      })
      .catch(() => {});
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    void ensureBasket().catch(() => {});
  }, []);

  useEffect(() => {
    let cancelled = false;
    api
      .wishlist()
      .then((response) => {
        if (cancelled) return;
        setWishlist(response.rows);
        setWishlistReady(true);
      })
      .catch((error: unknown) => {
        if (!cancelled)
          notify(error instanceof ApiError ? error.message : String(error), "error");
      });
    return () => {
      cancelled = true;
    };
  }, [notify]);

  const onBasketChanged = useCallback(() => invalidateBasket(), []);
  const reloadWishlist = useCallback(async () => {
    const response = await api.wishlist();
    setWishlist(response.rows);
  }, []);
  const onWishlistToggle = useCallback(
    async (row: ResultRow) => {
      const key = wishlistKey(row);
      if (!wishlistReady || pendingWishlistRef.current.has(key)) return;

      const removing = wishlist.some((saved) => wishlistKey(saved) === key);
      pendingWishlistRef.current.add(key);
      setPendingWishlistKeys((current) => new Set(current).add(key));
      try {
        if (removing) {
          await api.removeWishlistItem(row);
          setWishlist((current) =>
            current.filter((saved) => wishlistKey(saved) !== key),
          );
        } else {
          await api.saveWishlistItem(row);
          const response = await api.wishlist();
          setWishlist(response.rows);
        }
      } catch (error) {
        notify(error instanceof ApiError ? error.message : String(error), "error");
      } finally {
        pendingWishlistRef.current.delete(key);
        setPendingWishlistKeys((current) => {
          const next = new Set(current);
          next.delete(key);
          return next;
        });
      }
    },
    [notify, wishlist, wishlistReady],
  );

  if (startupError !== null) {
    return (
      <div className="page empty">
        Arka uca bağlanılamadı: {startupError}
      </div>
    );
  }
  if (config === null) {
    return <div className="page empty">Yükleniyor…</div>;
  }

  return (
    <div className="app">
      {/* Two fixed, non-interactive layers: a warm halo so the top of the
          window reads as lit, and a grain so the ground is not a flat sheet.
          Fixed keeps both off the scrolling content, where a repainting
          gradient would cost frames for nothing. */}
      <div className="ground" aria-hidden="true" />
      <div className="grain" aria-hidden="true" />

      <header className="toolbar">
        <span className="toolbar-title">PARFUM FINDER</span>
        <span className="toolbar-spacer" />
        <nav ref={tabsRef} className="tabs">
          <span className="tab-pill" aria-hidden="true" />
          <button
            type="button"
            className="tab"
            aria-current={view === "search" ? "page" : undefined}
            onClick={() => setView("search")}
          >
            Arama
          </button>
          <button
            type="button"
            className="tab"
            aria-current={view === "results" ? "page" : undefined}
            disabled={search === null}
            onClick={() => setView("results")}
          >
            Sonuçlar
          </button>
          <button
            type="button"
            className="tab wishlist-tab"
            aria-label="İstek listesi"
            title="İstek listesi"
            aria-current={view === "wishlist" ? "page" : undefined}
            onClick={() => setView("wishlist")}
          >
            <BookmarkIcon aria-hidden="true" />
            {wishlist.length > 0 && <span className="tab-count">{wishlist.length}</span>}
          </button>
          <button
            type="button"
            className="tab"
            aria-current={view === "basket" ? "page" : undefined}
            onClick={() => setView("basket")}
          >
            Sepet
            {basketCount > 0 && <span className="tab-count">{basketCount}</span>}
          </button>
        </nav>
      </header>

      <main className="content">
        {view === "search" && (
          <SearchScreen
            config={config}
            sites={sites}
            text={searchText}
            onTextChange={setSearchText}
            onStarted={(start) => {
              setSearchText("");
              setResultsSort(null);
              setSearch(start);
              setView("results");
            }}
          />
        )}
        {view === "results" &&
          (search === null ? (
            <div className="page empty">Henüz bir arama yapılmadı.</div>
          ) : (
            <ResultsScreen
              // Remounting per search is deliberate: every piece of this
              // screen's state belongs to one scan, and a stream that carried
              // the previous scan's notices into the next one would be showing
              // warnings about a search nobody is looking at.
              key={search.search_id}
              searchId={search.search_id}
              searches={search.searches}
              rejected={search.rejected}
              config={config}
              sort={resultsSort}
              onSortChange={setResultsSort}
              onBasketChanged={onBasketChanged}
              notify={notify}
              wishlist={wishlist}
              wishlistReady={wishlistReady}
              pendingWishlistKeys={pendingWishlistKeys}
              onWishlistToggle={onWishlistToggle}
            />
          ))}
        {view === "wishlist" && (
          <WishlistScreen
            rows={wishlist}
            wishlistReady={wishlistReady}
            pendingWishlistKeys={pendingWishlistKeys}
            config={config}
            siteNames={siteNames}
            query={wishlistQuery}
            onQueryChange={setWishlistQuery}
            sort={wishlistSort}
            onSortChange={setWishlistSort}
            notify={notify}
            basketSnapshot={basketSnapshot}
            onBasketChanged={onBasketChanged}
            onWishlistChanged={reloadWishlist}
            onWishlistToggle={onWishlistToggle}
          />
        )}
        {view === "basket" && (
          <BasketScreen
            config={config}
            siteNames={siteNames}
            notify={notify}
          />
        )}
      </main>

      {update !== null && (
        <UpdateDialog info={update} onDismiss={() => setUpdate(null)} />
      )}

      {toast && (
        <div className={`toast${toast.kind === "error" ? " error" : ""}`}>
          {toast.message}
        </div>
      )}
    </div>
  );
}
