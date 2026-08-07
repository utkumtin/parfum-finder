"""The fetch escalation ladder: one interface over httpx, curl_cffi, and playwright.

Which strategy a given site needs is recorded on that site's profile, and that value
comes from measurement, not a guess. Playwright is an optional extra. If a profile
requires it and it isn't installed, this must raise a clear error rather than
silently falling back to something weaker.

TODO: this is the foundation for a `probe <url>` command that tries each strategy in
turn and reports which one actually works.
"""
