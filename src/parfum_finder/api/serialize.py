"""ScanEvent, BasketRefreshEvent and viewmodel dataclasses as JSON-safe dicts.

Every event union is a plain frozen dataclass with no discriminator field of
its own, and `Decimal` (ResultRow.price_per_ml_kurus) is not JSON-serialisable
at all. This module is the one place that adds a "type" tag and turns Decimal
into a string, so a route handler never hand-rolls either.
"""

from __future__ import annotations

from typing import Any

from parfum_finder.basket import (
    BasketReport,
    SiteScenario,
    SplitLeg,
    SplitPlan,
    compare_split_to_best_full,
)
from parfum_finder.services.scan import (
    BasketPriceExcluded,
    BasketRefreshEvent,
    BasketRefreshFinished,
    BasketRefreshStarted,
    BasketRowFinished,
    BasketWriteFailed,
    CacheHit,
    RowsReady,
    ScanEvent,
    ScanFinished,
    ScanStarted,
    SiteFinished,
    SiteStarted,
    WriteFailed,
)
from parfum_finder.viewmodels import BasketRow, ResultRow


def encode_result_row(row: ResultRow) -> dict[str, Any]:
    per_ml = row.price_per_ml_kurus
    return {
        "site_id": row.site_id,
        "site_label": row.site_label,
        "query_index": row.query_index,
        "product": row.product,
        "raw_title": row.raw_title,
        "size_ml_x10": row.size_ml_x10,
        "price_kurus": row.price_kurus,
        # Exact, not floated: a display layer that needs to compare two of
        # these has to see the same value the sort itself used.
        "price_per_ml_kurus": str(per_ml) if per_ml is not None else None,
        "in_stock": row.in_stock,
        "match_score": row.match_score,
        "confident": row.confident,
        "brand": row.brand,
        "name": row.name,
        "concentration": row.concentration,
        "product_url": row.product_url,
        "clone_of": row.clone_of,
        "own_identity": row.own_identity,
        "age_days": row.age_days,
    }


def encode_scan_event(event: ScanEvent) -> dict[str, Any]:
    match event:
        case ScanStarted(total_sites=total_sites, total_perfumes=total_perfumes):
            return {
                "type": "scan_started",
                "total_sites": total_sites,
                "total_perfumes": total_perfumes,
            }
        case SiteStarted(site_id=site_id):
            return {"type": "site_started", "site_id": site_id}
        case CacheHit(query_index=query_index, age_days=age_days):
            return {
                "type": "cache_hit",
                "query_index": query_index,
                "age_days": age_days,
            }
        case RowsReady(rows=rows):
            return {"type": "rows_ready", "rows": [encode_result_row(r) for r in rows]}
        case SiteFinished(
            site_id=site_id,
            query_index=query_index,
            status=status,
            detail=detail,
            has_rows=has_rows,
        ):
            return {
                "type": "site_finished",
                "site_id": site_id,
                "query_index": query_index,
                "status": status,
                "detail": detail,
                "has_rows": has_rows,
            }
        case WriteFailed(site_id=site_id, query_index=query_index):
            return {
                "type": "write_failed",
                "site_id": site_id,
                "query_index": query_index,
            }
        case ScanFinished(error_count=error_count):
            return {"type": "scan_finished", "error_count": error_count}
    raise TypeError(f"unhandled scan event: {event!r}")


def encode_basket_refresh_event(event: BasketRefreshEvent) -> dict[str, Any]:
    match event:
        case BasketRefreshStarted(total=total):
            return {"type": "refresh_started", "total": total}
        case BasketPriceExcluded(
            site_id=site_id, basket_item_id=basket_item_id, notice=notice
        ):
            return {
                "type": "price_excluded",
                "site_id": site_id,
                "basket_item_id": basket_item_id,
                "notice": notice,
            }
        case BasketWriteFailed(site_id=site_id, notice=notice):
            return {"type": "write_failed", "site_id": site_id, "notice": notice}
        case BasketRowFinished(site_id=site_id, basket_item_id=basket_item_id):
            return {
                "type": "row_finished",
                "site_id": site_id,
                "basket_item_id": basket_item_id,
            }
        case BasketRefreshFinished():
            return {"type": "refresh_finished"}
    raise TypeError(f"unhandled basket refresh event: {event!r}")


def encode_basket_row(row: BasketRow) -> dict[str, Any]:
    return {
        "basket_item_id": row.line.basket_item_id,
        "brand": row.line.brand,
        "name": row.line.name,
        "concentration": row.line.concentration,
        "size_ml_x10": row.line.size_ml_x10,
        "qty": row.line.qty,
        "label": row.label,
        "prices": dict(row.prices),
        "age_days": row.age_days,
    }


def encode_site_scenario(scenario: SiteScenario) -> dict[str, Any]:
    return {
        "site_id": scenario.site_id,
        "name": scenario.name,
        "subtotal_kurus": scenario.subtotal_kurus,
        "shipping_kurus": scenario.shipping_kurus,
        "total_kurus": scenario.total_kurus,
        "covered": scenario.covered,
        "total_items": scenario.total_items,
        "missing": list(scenario.missing),
        "free_shipping_gap_kurus": scenario.free_shipping_gap_kurus,
        "free_shipping_met": scenario.free_shipping_met,
        "notes": scenario.notes,
        "is_full": scenario.is_full,
    }


def encode_basket_report(report: BasketReport) -> dict[str, Any]:
    return {
        "full": [encode_site_scenario(s) for s in report.full],
        "partial": [encode_site_scenario(s) for s in report.partial],
        "unavailable": list(report.unavailable),
    }


def _encode_split_leg(leg: SplitLeg) -> dict[str, Any]:
    return {
        "scenario": encode_site_scenario(leg.scenario),
        "item_ids": list(leg.item_ids),
    }


def encode_split_plan(plan: SplitPlan, report: BasketReport) -> dict[str, Any]:
    """The split plan plus its verdict against the best full-coverage site.

    Named `best_combination` at the call site, never `cheapest`: the plan is a
    heuristic search's best find, not a proof, and the wording that keeps that
    honest belongs in the API contract too, not only in the TUI's own strings.
    """
    verdict = compare_split_to_best_full(plan, report)
    return {
        "legs": [_encode_split_leg(leg) for leg in plan.legs],
        "total_kurus": plan.total_kurus,
        "omitted_sites": list(plan.omitted_sites),
        "best_full_site": (
            encode_site_scenario(verdict.best_full)
            if verdict.best_full is not None
            else None
        ),
        "diff_kurus": verdict.diff_kurus,
    }
