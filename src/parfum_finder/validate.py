"""Profile staleness checks. Two modes: offline (against saved fixtures) and live
(against the real site).

Offline mode runs against saved HTML fixtures and needs no network access. Live
mode hits the real site and, if something broke, reports which extraction layer
failed and whether falling back to a lower layer would still work.

TODO: offline mode, --live mode, marking a site "suspect" when checks fail, and an
age badge based on when a profile was last (re)discovered.
"""
