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
      <span className="add-icon" aria-hidden="true">
        {inBasket ? "✓" : "+"}
      </span>
    </button>
  );
}
