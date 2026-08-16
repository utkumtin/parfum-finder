# Graph Report - ui  (2026-08-16)

## Corpus Check
- 17 files · ~8,500 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 126 nodes · 215 edges · 8 communities
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS · INFERRED: 1 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `ae09254c`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- compilerOptions
- BasketScreen.tsx
- ResultsScreen.tsx
- package.json
- App.tsx
- types.ts
- devDependencies

## God Nodes (most connected - your core abstractions)
1. `compilerOptions` - 16 edges
2. `ResultsScreen()` - 11 edges
3. `BasketScreen()` - 9 edges
4. `formatAge()` - 7 edges
5. `ApiError` - 6 edges
6. `useEventStream()` - 6 edges
7. `formatPrice()` - 6 edges
8. `AppConfig` - 6 edges
9. `scripts` - 5 edges
10. `api` - 5 edges

## Surprising Connections (you probably didn't know these)
- `ResultsScreen()` --calls--> `refusalReason()`  [EXTRACTED]
  src/screens/ResultsScreen.tsx → src/api/ws.ts
- `ResultsScreen()` --calls--> `useEventStream()`  [EXTRACTED]
  src/screens/ResultsScreen.tsx → src/api/ws.ts
- `Scenario()` --calls--> `formatPrice()`  [EXTRACTED]
  src/screens/BasketScreen.tsx → src/lib/format.ts
- `ResultsScreen()` --calls--> `formatPrice()`  [EXTRACTED]
  src/screens/ResultsScreen.tsx → src/lib/format.ts
- `ResultsScreen()` --calls--> `formatMl()`  [EXTRACTED]
  src/screens/ResultsScreen.tsx → src/lib/format.ts

## Import Cycles
- None detected.

## Communities (8 total, 0 thin omitted)

### Community 0 - "compilerOptions"
Cohesion: 0.08
Nodes (23): DOM, DOM.Iterable, ES2022, src, vite/client, vite.config.ts, compilerOptions, isolatedModules (+15 more)

### Community 1 - "BasketScreen.tsx"
Cohesion: 0.18
Nodes (15): authToken(), refusalReason(), streamUrl(), useEventStream(), ProgressBar(), formatMl(), formatPerMl(), formatPrice() (+7 more)

### Community 2 - "ResultsScreen.tsx"
Cohesion: 0.15
Nodes (15): AddButton(), Badge(), BadgeKind, ConfirmDialog(), ScanStatus(), basketKey(), Block, Notice (+7 more)

### Community 3 - "package.json"
Cohesion: 0.12
Nodes (16): motion, dependencies, motion, react, react-dom, name, private, scripts (+8 more)

### Community 4 - "App.tsx"
Cohesion: 0.18
Nodes (13): api, ApiError, App(), Toast, View, formatAge(), root, daysSince() (+5 more)

### Community 5 - "types.ts"
Cohesion: 0.17
Nodes (14): readDetail(), request(), Window, AcceptedSearch, BasketReport, BasketResponse, BestCombination, RefreshStart (+6 more)

### Community 6 - "devDependencies"
Cohesion: 0.18
Nodes (11): devDependencies, @types/react, @types/react-dom, typescript, vite, @vitejs/plugin-react, @types/react, @types/react-dom (+3 more)

## Knowledge Gaps
- **47 isolated node(s):** `name`, `private`, `version`, `type`, `dev` (+42 more)
  These have ≤1 connection - possible missing edges or undocumented components.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `devDependencies` connect `devDependencies` to `package.json`?**
  _High betweenness centrality (0.027) - this node is a cross-community bridge._
- **What connects `name`, `private`, `version` to the rest of the system?**
  _47 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `compilerOptions` be split into smaller, more focused modules?**
  _Cohesion score 0.08333333333333333 - nodes in this community are weakly interconnected._
- **Should `ResultsScreen.tsx` be split into smaller, more focused modules?**
  _Cohesion score 0.14736842105263157 - nodes in this community are weakly interconnected._
- **Should `package.json` be split into smaller, more focused modules?**
  _Cohesion score 0.11764705882352941 - nodes in this community are weakly interconnected._