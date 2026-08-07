"""Extraction ladder: JSON-LD -> platform JSON endpoint -> embedded JS state -> CSS.

Structured data is always preferred over CSS selectors, in order of how well each
layer survives a site redesign. Discovery tries these top-down and records whichever
layer actually worked on that site's profile.

TODO: implement the full ladder, plus profile-driven variant extraction, including
filtering out non-decant listings (testers, full bottles, sizes 30 ml and up).
"""
