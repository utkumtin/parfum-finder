"""Dependency-boundary tests for shared search and persistence models."""

import ast
from pathlib import Path

import parfum_finder.engine as engine
import parfum_finder.store as store
from parfum_finder.search_models import (
    ProductCandidate,
    SearchHit,
    SiteResult,
    SiteStatus,
    Variant,
)


def test_engine_preserves_its_search_model_exports() -> None:
    assert engine.ProductCandidate is ProductCandidate
    assert engine.SearchHit is SearchHit
    assert engine.SiteResult is SiteResult
    assert engine.SiteStatus is SiteStatus
    assert engine.Variant is Variant


def test_store_imports_neither_engine_nor_matcher() -> None:
    source = Path(store.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported_modules = {
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module is not None
    }

    assert "parfum_finder.engine" not in imported_modules
    assert "parfum_finder.matcher" not in imported_modules
