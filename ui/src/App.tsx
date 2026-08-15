import { useCallback, useEffect, useState } from "react";
import { ApiError, api } from "./api/client";
import { BasketScreen } from "./screens/BasketScreen";
import { ResultsScreen } from "./screens/ResultsScreen";
import { SearchScreen } from "./screens/SearchScreen";
import type { AppConfig, SearchStart } from "./types";

type View = "search" | "results" | "basket";

interface Toast {
  message: string;
  kind: "info" | "error";
}

export function App() {
  const [config, setConfig] = useState<AppConfig | null>(null);
  const [siteNames, setSiteNames] = useState<Record<string, string>>({});
  const [startupError, setStartupError] = useState<string | null>(null);
  const [view, setView] = useState<View>("search");
  const [search, setSearch] = useState<SearchStart | null>(null);
  const [toast, setToast] = useState<Toast | null>(null);
  // Bumped whenever the basket changed under the basket screen's feet, so
  // switching to it shows the addition rather than a stale read.
  const [basketVersion, setBasketVersion] = useState(0);

  useEffect(() => {
    Promise.all([api.config(), api.sites()])
      .then(([loadedConfig, sites]) => {
        setConfig(loadedConfig);
        setSiteNames(Object.fromEntries(sites.map((s) => [s.id, s.name])));
      })
      .catch((e: unknown) => {
        setStartupError(e instanceof ApiError ? e.message : String(e));
      });
  }, []);

  const notify = useCallback((message: string, kind: "info" | "error") => {
    setToast({ message, kind });
    window.setTimeout(() => setToast(null), 3000);
  }, []);

  const onBasketChanged = useCallback(() => setBasketVersion((v) => v + 1), []);

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
      <header className="toolbar">
        <span className="toolbar-title">parfum-finder</span>
        <span className="toolbar-spacer" />
        <nav className="tabs">
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
            className="tab"
            aria-current={view === "basket" ? "page" : undefined}
            onClick={() => setView("basket")}
          >
            Sepet
          </button>
        </nav>
      </header>

      <main className="content">
        {view === "search" && (
          <SearchScreen
            config={config}
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
            />
          ))}
        {view === "basket" && (
          <BasketScreen
            // Not a key: remounting on every change would throw away the
            // refresh warnings at the moment the refresh that produced them
            // ends. It is a dependency of the screen's own read instead.
            version={basketVersion}
            config={config}
            siteNames={siteNames}
            notify={notify}
          />
        )}
      </main>

      {toast && (
        <div className={`toast${toast.kind === "error" ? " error" : ""}`}>
          {toast.message}
        </div>
      )}
    </div>
  );
}
