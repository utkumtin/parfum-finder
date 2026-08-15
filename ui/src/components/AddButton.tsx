import { useCallback, useEffect, useRef, useState } from "react";

type Status = "idle" | "pending" | "done";

// How long the checkmark stays up before the button settles back to "+". Long
// enough to register as feedback, short enough that a second add on the same
// row does not feel blocked.
const DONE_DURATION_MS = 1400;

/**
 * Sepete ekle butonu. Sadece "+" gösterir; tıklanınca ekleme biterse yeşil
 * tike döner ve bir süre sonra "+"ya geri geçer.
 */
export function AddButton({ onAdd }: { onAdd: () => Promise<boolean> }) {
  const [status, setStatus] = useState<Status>("idle");
  const timerRef = useRef<number | null>(null);

  useEffect(() => {
    return () => {
      if (timerRef.current !== null) window.clearTimeout(timerRef.current);
    };
  }, []);

  const handleClick = useCallback(
    async (e: React.MouseEvent<HTMLButtonElement>) => {
      e.stopPropagation();
      if (status !== "idle") return;
      setStatus("pending");
      const added = await onAdd();
      if (!added) {
        setStatus("idle");
        return;
      }
      setStatus("done");
      timerRef.current = window.setTimeout(() => setStatus("idle"), DONE_DURATION_MS);
    },
    [onAdd, status],
  );

  return (
    <button
      type="button"
      className={`button quiet add-button${status === "done" ? " done" : ""}`}
      onClick={(e) => void handleClick(e)}
      disabled={status === "pending"}
      aria-label="Sepete ekle"
    >
      <span className="add-icon" aria-hidden="true">
        {status === "done" ? "✓" : "+"}
      </span>
    </button>
  );
}
