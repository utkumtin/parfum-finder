"""Basket optimization. A pure function, no network access.

Input: the shopping list, a price matrix per (item, site) where a missing price
means out of stock or unavailable, and each site's shipping config (free-shipping
threshold and cost). Output: a per-site scenario (subtotal, shipping, grand total,
how many items are covered) plus the best split-across-sites combination found.

Why "cheapest site per item" isn't good enough: shipping cost isn't linear. It
drops to zero once a site's subtotal crosses its free-shipping threshold. Paying a
bit more for one item on a given site can lower the grand total overall by
unlocking free shipping there.

The algorithm enumerates site subsets and applies local-search improvement. This is
a heuristic, not a proof of optimality. The UI must present it as "best combination
found," never as "the cheapest possible."

TODO: single-site scenarios first, then the split-combination search. The
optimize() signature needs BasketItem / ShippingConfig / BasketReport types that
don't have a concrete field list anywhere yet, so they're deliberately left
undefined here instead of guessed.
"""
