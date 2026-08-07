"""The search screen: a results table that fills in as each site finishes.

Columns: site, raw product title, size (ml), price, price per ml, stock, match
score. Results from a site land as soon as that site is done. The screen never
waits for every site to finish before showing anything.

TODO: sortable columns, a stock filter, opening a result in the browser, price
history, and adding a result to the basket (with a confirmation prompt for
low-confidence matches).
"""
