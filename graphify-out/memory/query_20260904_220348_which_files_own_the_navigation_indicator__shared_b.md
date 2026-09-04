---
type: "query"
date: "2026-09-04T22:03:48.842358+00:00"
question: "Which files own the navigation indicator, shared basket data, and wishlist lazy details?"
contributor: "graphify"
source_nodes: ["App()", "basketStore.ts", "BasketScreen.tsx", "ResultsScreen.tsx", "WishlistScreen.tsx"]
---

# Q: Which files own the navigation indicator, shared basket data, and wishlist lazy details?

## Answer

App.tsx owns navigation geometry and the shared basket entry point. basketStore.ts owns cached basket reads, invalidation, request deduplication, and stale snapshots. BasketScreen.tsx, ResultsScreen.tsx, and WishlistScreen.tsx consume that shared state. WishlistScreen.tsx also owns generation-guarded lazy detail mounting and stable panel identity.

## Source Nodes

- App()
- basketStore.ts
- BasketScreen.tsx
- ResultsScreen.tsx
- WishlistScreen.tsx