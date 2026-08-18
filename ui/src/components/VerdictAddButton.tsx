import { useCallback, useState } from "react";

/**
 * The "Sepete ekle" action on the recommendation card's headline verdict.
 *
 * Kept as one component rather than a label sitting next to a separately
 * animated icon: the button used to lift on hover while its plus glyph
 * scaled up on its own, and those two motions drifting out of step is what
 * read as the plus blurring and slipping off-center mid-hover. Here the
 * button owns a single highlight, a shadow ring plus the same lift the rest
 * of the app's primary buttons use. The plus is the only glyph that still
 * moves independently on hover, a full turn in place that can't throw its
 * own alignment off since it always ends exactly where it started; the
 * check does not turn, since a spinning confirmation would read as the add
 * undoing itself, so the highlight ring is the only feedback left once the
 * row is in the basket.
 *
 * The plus-to-check swap mirrors AddButton's: driven by the basket's real
 * state (inBasket), not a timer, so a reload or a line added from the table
 * still shows the right glyph here too.
 */
export function VerdictAddButton({
  onAdd,
  inBasket,
}: {
  onAdd: () => Promise<boolean>;
  inBasket: boolean;
}) {
  const [pending, setPending] = useState(false);

  const handleClick = useCallback(async () => {
    if (pending) return;
    setPending(true);
    await onAdd();
    setPending(false);
  }, [onAdd, pending]);

  return (
    <button
      type="button"
      className={`verdict-add${inBasket ? " done" : ""}`}
      onClick={() => void handleClick()}
      disabled={pending}
    >
      Sepete ekle
      <span className="verdict-add-pip" aria-hidden="true">
        <svg
          className="verdict-add-icon"
          viewBox="0 0 12 12"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.6"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          {inBasket ? <path d="M2.5 6.3 5 8.8 9.5 3.5" /> : <path d="M6 2.5v7M2.5 6h7" />}
        </svg>
      </span>
    </button>
  );
}
