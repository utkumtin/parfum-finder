import { motion } from "motion/react";
import { useEffect } from "react";

/**
 * The modal a low-scoring match or a clone has to pass before it can be added.
 *
 * The backend refuses such an add with 409 whether or not this was shown, so
 * the dialog is the explanation, not the gate. What it must never become is a
 * step that gets skipped for being in the way.
 */
export function ConfirmDialog({
  title,
  body,
  confirmLabel,
  onConfirm,
  onCancel,
}: {
  title: string;
  body: string;
  confirmLabel: string;
  onConfirm: () => void;
  onCancel: () => void;
}) {
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onCancel();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onCancel]);

  return (
    <div className="scrim" onClick={onCancel}>
      <motion.div
        className="dialog"
        role="dialog"
        aria-modal="true"
        aria-label={title}
        initial={{ opacity: 0, scale: 0.97 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ type: "spring", bounce: 0, duration: 0.3 }}
        onClick={(e) => e.stopPropagation()}
      >
        <h2>{title}</h2>
        <p>{body}</p>
        <div className="dialog-actions">
          <button type="button" className="button" onClick={onCancel}>
            Vazgeç
          </button>
          <button
            type="button"
            className="button primary"
            onClick={onConfirm}
            autoFocus
          >
            {confirmLabel}
          </button>
        </div>
      </motion.div>
    </div>
  );
}
