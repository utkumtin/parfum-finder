import { useCallback, useEffect, useLayoutEffect, useRef, useState } from "react";
import { ApiError, api } from "./api/client";
import { UpdateDialog } from "./components/UpdateDialog";
import { BookmarkIcon } from "./components/BookmarkIcon";
import { BasketScreen } from "./screens/BasketScreen";
import { ResultsScreen } from "./screens/ResultsScreen";
import { SearchScreen } from "./screens/SearchScreen";
import { WishlistScreen } from "./screens/WishlistScreen";
import { wishlistKey } from "./lib/wishlist";
import type { AppConfig, ResultRow, SearchStart, SiteSummary, UpdateInfo, WishlistRow } from "./types";

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
  const [wishlist, setWishlist] = useState<WishlistRow[]>([]);
  const [wishlistReady, setWishlistReady] = useState(false);
  const [pendingWishlistKeys, setPendingWishlistKeys] = useState<Set<string>>(
    new Set(),
  );
  const [toast, setToast] = useState<Toast | null>(null);
  // Bumped whenever the basket changed under the basket screen's feet, so
  // switching to it shows the addition rather than a stale read.
  const [basketVersion, setBasketVersion] = useState(0);
  // How many lines the basket holds, for the count on its tab. Read here
  // rather than lifted out of BasketScreen because the number has to be there
  // before that screen has ever been opened.
  const [basketCount, setBasketCount] = useState(0);
  const [update, setUpdate] = useState<UpdateInfo | null>(null);
  const tabsRef = useRef<HTMLElement>(null);
  const pendingWishlistRef = useRef<Set<string>>(new Set());
  const hasPositionedTabPill = useRef(false);
  const lastPillView = useRef<View | null>(null);

  const notify = useCallback((message: string, kind: "info" | "error") => {
    setToast({ message, kind });
    window.setTimeout(() => setToast(null), 3000);
  }, []);

  useLayoutEffect(() => {
    const tabs = tabsRef.current;
    const pill = tabs?.querySelector<HTMLElement>(".tab-pill");
    const activeTab = tabs?.querySelector<HTMLButtonElement>(
      '.tab[aria-current="page"]',
    );

    if (!pill || !activeTab) return;

    const animate = hasPositionedTabPill.current && lastPillView.current !== view;
    const previousTransition = pill.style.transition;

    if (!animate) pill.style.transition = "none";
    pill.style.transform = `translateX(${activeTab.offsetLeft}px)`;
    pill.style.width = `${activeTab.offsetWidth}px`;

    if (!animate) {
      void pill.offsetWidth;
      pill.style.transition = previousTransition;
    }

    hasPositionedTabPill.current = true;
    lastPillView.current = view;
  }, [basketCount, search, view]);

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
    let cancelled = false;
    // A count nobody could read is a missing convenience, not a broken screen:
    // the tab works either way, so this failure stays quiet.
    api
      .basket()
      .then((response) => {
        if (!cancelled) setBasketCount(response.rows.length);
      })
      .catch(() => {
        if (!cancelled) setBasketCount(0);
      });
    return () => {
      cancelled = true;
    };
  }, [basketVersion]);

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

  const onBasketChanged = useCallback(() => setBasketVersion((v) => v + 1), []);
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
            notify={notify}
            onBasketChanged={onBasketChanged}
            onWishlistChanged={reloadWishlist}
            onWishlistToggle={onWishlistToggle}
          />
        )}
        {view === "basket" && (
          <BasketScreen
            // Not a key: remounting on every change would throw away the
            // refresh warnings at the moment the refresh that produced them
            // ends. It is a dependency of the screen's own read instead.
            version={basketVersion}
            config={config}
            siteNames={siteNames}
            notify={notify}
            onBasketChanged={onBasketChanged}
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
