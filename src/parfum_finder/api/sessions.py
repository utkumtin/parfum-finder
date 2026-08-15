"""In-memory session state for the two streamed operations: a search scan and
a basket refresh.

`POST /api/search` only parses the typed line and registers a session; it is
the WebSocket handler that actually drives `run_scan`, so no event is ever
lost to a scan that started before anything was listening. `started` is what
stops a second WebSocket connect from running the same scan twice -- both
`run_scan` and `run_basket_refresh` write to the database as they go, and a
duplicate run would double every price snapshot.

Sessions live only for the process's lifetime, matching the plan's port-0 +
per-process token: nothing here is meant to survive a restart.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from parfum_finder.services.scan import Search
from parfum_finder.viewmodels import BasketRow, ResultRow


@dataclass
class ScanSession:
    id: str
    searches: list[Search]
    rejected: list[str]
    force: bool = False
    rows: list[ResultRow] = field(default_factory=list)
    started: bool = False
    # False while the WS is still streaming (or hasn't connected yet), so
    # /api/results can tell "3 rows is the answer" apart from "3 rows so
    # far" -- a client that polls mid-scan, or a socket that died partway,
    # would otherwise get a 200 with a silently partial table.
    finished: bool = False


@dataclass
class BasketRefreshSession:
    id: str
    rows: list[BasketRow]
    started: bool = False
