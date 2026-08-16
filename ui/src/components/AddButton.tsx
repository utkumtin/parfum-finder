import { useCallback, useState } from "react";

/**
 * Sepete ekle butonu. Ürün sepetteyken yeşil tik gösterir, sepette
 * değilken "+"; sepetten çıkarılınca otomatik olarak "+"ya döner. Tik
 * bir zamanlayıcıyla değil, sepetin gerçek durumuyla (inBasket) belirlenir.
 */
export function AddButton({
  onAdd,
  inBasket,
}: {
  onAdd: () => Promise<boolean>;
  inBasket: boolean;
}) {
  const [pending, setPending] = useState(false);

  const handleClick = useCallback(
    async (e: React.MouseEvent<HTMLButtonElement>) => {
      e.stopPropagation();
      if (pending) return;
      setPending(true);
      await onAdd();
      setPending(false);
    },
    [onAdd, pending],
  );

  return (
    <button
      type="button"
      className={`button quiet add-button${inBasket ? " done" : ""}`}
      onClick={(e) => void handleClick(e)}
      disabled={pending}
      aria-label="Sepete ekle"
    >
      {/* An SVG cross/check instead of a text glyph: a font character's ink
          doesn't sit at the center of its own box, so it never lands in the
          middle of the circle, and animating a glyph's box through the
          hover scale forces the browser to re-hint and re-rasterize the
          text each frame, which is what read as the laggy upward jump. A
          drawn path has neither problem. */}
      <svg
        className="add-icon"
        viewBox="0 0 12 12"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
        aria-hidden="true"
      >
        {inBasket ? <path d="M2.5 6.3 5 8.8 9.5 3.5" /> : <path d="M6 1.5v9M1.5 6h9" />}
      </svg>
    </button>
  );
}
