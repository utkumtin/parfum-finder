/**
 * The "Sepete ekle" action on the recommendation card's headline verdict.
 *
 * Kept as one component rather than a label sitting next to a separately
 * animated icon: the button used to lift on hover while its plus glyph
 * scaled up on its own, and those two motions drifting out of step is what
 * read as the plus blurring and slipping off-center mid-hover. Here the
 * button owns a single highlight, a shadow ring plus the same lift the rest
 * of the app's primary buttons use, and the plus is the only thing that
 * still moves independently: a full turn in place, which can't throw its
 * own alignment off since it always ends exactly where it started.
 */
export function VerdictAddButton({ onAdd }: { onAdd: () => void }) {
  return (
    <button type="button" className="verdict-add" onClick={onAdd}>
      Sepete ekle
      <span className="verdict-add-pip" aria-hidden="true">
        <svg
          viewBox="0 0 12 12"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.6"
          strokeLinecap="round"
        >
          <path d="M6 2.5v7M2.5 6h7" />
        </svg>
      </span>
    </button>
  );
}
