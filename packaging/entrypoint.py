"""PyInstaller entry point for the packaged desktop app.

Kept outside src/parfum_finder/ because it is packaging plumbing, not
library code: PyInstaller's `Analysis` needs one script to start from, and
this is it. Everything it does is already implemented in
`parfum_finder.gui` -- this just forwards to it, the same way
`packaging/parfum-finder.spec` forwards this file to PyInstaller.
"""

import sys

from parfum_finder.gui import main

if __name__ == "__main__":
    sys.exit(main(selftest="--selftest" in sys.argv[1:]))
