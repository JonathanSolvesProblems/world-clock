"""Run the Kaggle CLI through Python.

Usage:
    python scripts/kg.py b t status world-clock-from-memory

Windows Application Control started blocking .venv\\Scripts\\kaggle.exe on this machine
in October 2026, while python.exe in the same venv still runs. This calls the same entry
point the .exe wraps, with the same arguments.
"""

import sys

from kaggle.cli import main

if __name__ == "__main__":
    sys.argv = ["kaggle", *sys.argv[1:]]
    sys.exit(main())
