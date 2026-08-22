import { useCallback } from "react";
import { BookmarkIcon } from "./BookmarkIcon";

export function WishlistButton({
  inWishlist,
  onToggle,
}: {
  inWishlist: boolean;
  onToggle: () => void;
}) {
  const handleClick = useCallback(
    (event: React.MouseEvent<HTMLButtonElement>) => {
      event.stopPropagation();
      onToggle();
    },
    [onToggle],
  );

  return (
    <button
      type="button"
      className={`button quiet wishlist-button${inWishlist ? " saved" : ""}`}
      aria-label={inWishlist ? "İstek listesinden çıkar" : "İstek listesine ekle"}
      aria-pressed={inWishlist}
      onClick={handleClick}
    >
      <BookmarkIcon filled={inWishlist} aria-hidden="true" />
    </button>
  );
}
