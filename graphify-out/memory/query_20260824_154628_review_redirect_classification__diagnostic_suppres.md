---
type: "query"
date: "2026-08-24T15:46:28.891292+00:00"
question: "Review redirect classification, diagnostic suppression, and shared attempt cache and pacing"
contributor: "graphify"
outcome: "useful"
source_nodes: ["engine.py", "run_site_attempts()", "snapshot_rows()", "search_spellings()"]
---

# Q: Review redirect classification, diagnostic suppression, and shared attempt cache and pacing

## Answer

Expanded from graph vocabulary: redirect, canonical, product, metadata, diagnostic, attempt, matcher, cache, pacer, scan, basket, cli. The graph led to engine.py, matcher.py, store.py, scan.py, and CLI call sites. Review confirmed the shared service and revealed three corrected defects: reserved percent escapes were collapsed, hooks_dir was dropped, and validation mislabeled unclassified redirects.

## Outcome

- Signal: useful

## Source Nodes

- engine.py
- run_site_attempts()
- snapshot_rows()
- search_spellings()