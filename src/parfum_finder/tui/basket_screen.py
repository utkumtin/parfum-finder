"""The basket screen: the shopping list, a scenario per site, and the best split.

Sites that cover the whole list are shown separately from sites that only cover
part of it, and listed above them. A partial site is tagged, e.g. "4/5 items", and
never compared directly against a full-coverage total. Each scenario shows how much
more is needed to unlock free shipping. The split-across-sites result is always
labeled as the best combination found, not the mathematically cheapest.

TODO: add/remove/quantity controls, single-site scenario blocks, price-age display,
a refresh command with a progress indicator, and the split-combination row.
"""
