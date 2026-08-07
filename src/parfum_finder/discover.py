"""Site discovery: turns a URL into a profile, with human review. Not fully automatic.

Flow: measure which fetch strategy the site needs, fingerprint the platform if it's
recognizable, walk the extraction ladder to find the most durable layer that works,
then run an end-to-end trial (a sample search plus a sample product page) and show
the extracted fields with evidence and a confidence score. Low-confidence fields get
flagged for manual review, and shipping data is never guessed. It's always entered
by hand afterward.

TODO: this can't be implemented yet. It needs real target site URLs to run against,
and those haven't been provided yet. Once they are: strategy measurement, JSON-LD
detection, and an end-to-end trial report come first; platform fingerprinting and
template matching come after that.
"""
