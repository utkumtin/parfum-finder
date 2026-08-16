import { motion } from "motion/react";

/**
 * The scan's live status: sits where the results table will be, the same
 * place the TUI puts its progress bar. Rows only ever land once, all
 * together, once the scan is done -- a table that grows one site at a time
 * cannot be read, because the cheapest row keeps changing and the row
 * someone is looking at keeps moving out from under them. This is what says
 * the search is still working while nothing else on screen does.
 */
export function ScanStatus({
  done,
  total,
  errorCount,
}: {
  done: number;
  total: number;
  errorCount: number;
}) {
  const value = total === 0 ? 0 : Math.min(1, done / total);
  return (
    <div className="tray scan-status" role="status">
      <div className="core">
        <div className="scan-status-head">
          <span className="scan-live-dot" aria-hidden="true" />
          <span className="scan-status-label">Taranıyor…</span>
          <span className="scan-status-count">
            {done} / {total}
          </span>
        </div>
        <div
          className="scan-bar"
          role="progressbar"
          aria-valuemin={0}
          aria-valuemax={100}
          aria-valuenow={Math.round(value * 100)}
        >
          <motion.div
            className="scan-bar-fill"
            initial={{ width: 0 }}
            animate={{ width: `${value * 100}%` }}
            transition={{ type: "spring", bounce: 0, duration: 0.4 }}
          />
        </div>
        {errorCount > 0 && (
          <p className="scan-status-errors">{errorCount} hata</p>
        )}
      </div>
    </div>
  );
}
