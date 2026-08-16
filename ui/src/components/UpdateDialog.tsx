import { motion } from "motion/react";
import { useCallback, useEffect, useRef, useState } from "react";
import { ApiError, api } from "../api/client";
import type { UpdateInfo, UpdateProgress } from "../types";

/**
 * The "there is a newer version" modal, shown once per launch.
 *
 * It owns the whole update from here on: pressing the button downloads the
 * installer, and the moment the file is on disk the backend hands over to it
 * and closes this window. That is why the dialog cannot be dismissed while
 * the download runs. Closing it would leave a download nobody is watching,
 * finishing into a window that shuts itself.
 *
 * The release notes are GitHub's Markdown source rendered as plain text. A
 * changelog is not worth a Markdown dependency, and it is certainly not worth
 * injecting remote HTML into the app.
 */
export function UpdateDialog({
  info,
  onDismiss,
}: {
  info: UpdateInfo;
  onDismiss: () => void;
}) {
  const [progress, setProgress] = useState<UpdateProgress | null>(null);
  const [error, setError] = useState<string | null>(null);
  // The installer is handed over exactly once. A poll still in flight when the
  // download finishes writes a second "ready" state, and asking twice means a
  // 409 painted as a failure over a window that is already closing.
  const handedOver = useRef(false);

  const busy =
    progress !== null &&
    (progress.state === "downloading" || progress.state === "installing");

  const fail = useCallback((e: unknown) => {
    setError(e instanceof ApiError ? e.message : String(e));
    setProgress(null);
  }, []);

  useEffect(() => {
    if (progress?.state !== "downloading") return;
    const id = window.setInterval(() => {
      // A single missed poll is not a failed update: the next tick reads the
      // same state anyway, so only a failing start or install is surfaced.
      api.updateProgress().then(setProgress).catch(() => {});
    }, 400);
    return () => window.clearInterval(id);
  }, [progress?.state]);

  useEffect(() => {
    if (progress?.state === "ready" && !handedOver.current) {
      handedOver.current = true;
      api
        .installUpdate()
        .then(() => setProgress({ ...progress, state: "installing" }))
        .catch(fail);
    }
    if (progress?.state === "error") {
      setError(progress.message);
      setProgress(null);
    }
  }, [progress, fail]);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape" && !busy) onDismiss();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onDismiss, busy]);

  const start = () => {
    setError(null);
    handedOver.current = false;
    api.startUpdateDownload().then(setProgress).catch(fail);
  };

  return (
    <div className="scrim" onClick={busy ? undefined : onDismiss}>
      <motion.div
        className="dialog update-dialog"
        role="dialog"
        aria-modal="true"
        aria-label="Yeni sürüm"
        initial={{ opacity: 0, scale: 0.97 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ type: "spring", bounce: 0, duration: 0.3 }}
        onClick={(e) => e.stopPropagation()}
      >
        <h2>Yeni sürüm hazır</h2>
        <p>
          Sürüm {info.latest_version} yayınlandı. Şu an {info.current_version}
          {" "}kullanıyorsunuz.
        </p>

        <div className="update-notes" tabIndex={0}>
          {info.notes || "Bu sürüm için not yazılmamış."}
        </div>

        {progress?.state === "downloading" && (
          <DownloadLine received={progress.received} total={progress.total} />
        )}
        {progress?.state === "installing" && (
          <p className="update-line">
            Kurulum başlatılıyor. Uygulama kapanacak ve yeni sürümle açılacak.
          </p>
        )}
        {error !== null && (
          <p className="update-line error">Güncelleme başarısız: {error}</p>
        )}

        <div className="dialog-actions">
          <button
            type="button"
            className="button"
            onClick={onDismiss}
            disabled={busy}
          >
            Şimdi değil
          </button>
          <button
            type="button"
            className="button primary"
            onClick={start}
            disabled={busy}
            autoFocus
          >
            {error !== null ? "Tekrar dene" : "Güncelle"}
          </button>
        </div>
      </motion.div>
    </div>
  );
}

function DownloadLine({ received, total }: { received: number; total: number }) {
  const mb = (bytes: number) => (bytes / 1024 / 1024).toFixed(1);
  return (
    <p className="update-line">
      İndiriliyor: {mb(received)} MB
      {total > 0 && ` / ${mb(total)} MB`}
    </p>
  );
}
