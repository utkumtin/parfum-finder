"""PyInstaller entry point for the packaged desktop app.

Kept outside src/parfum_finder/ because it is packaging plumbing, not
library code: PyInstaller's `Analysis` needs one script to start from, and
this is it. Everything it does is already implemented in
`parfum_finder.gui` -- this just forwards to it, the same way
`packaging/parfum-finder.spec` forwards this file to PyInstaller.
"""

import os
import sys

# The packaged exe is built with console=False, so Windows gives it no
# stdout/stderr and leaves both as None. uvicorn's logging setup (and
# anything else that assumes a stream is there) crashes the moment it
# touches them, so stand in dummy streams before importing anything that
# might write to them.
if sys.stdout is None:
    sys.stdout = open(os.devnull, "w")  # noqa: SIM115
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w")  # noqa: SIM115

from parfum_finder.gui import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main(selftest="--selftest" in sys.argv[1:]))
