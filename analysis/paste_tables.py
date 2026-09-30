"""Paste the generated tables into POST.md, replacing the ones already there.

Usage:
    python analysis/paste_tables.py

Finds each table by its header row and replaces everything up to the next blank line with
what render_tables.py generates now. check_claims.py then confirms the two agree.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from render_tables import SUMMARY, post_table, tool_vs_memory  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
POST = ROOT / "POST.md"

HEADERS = {
    "| Model | Released | Score": post_table("memory"),
    "| Model | From memory (of": tool_vs_memory() if any(r["condition"] == "tool" and r["graded_total"] for r in SUMMARY) else None,
}


def main() -> int:
    text = POST.read_text(encoding="utf-8")
    for header, table in HEADERS.items():
        if table is None:
            continue
        rx = re.compile(rf"^{re.escape(header)}.*?(?=\n\s*\n|\Z)", re.MULTILINE | re.DOTALL)
        text, n = rx.subn(lambda _m: table, text, count=1)
        print(f"{'replaced' if n else 'not found'}: {header}")
    POST.write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
