"""Print the full text of the first few sub-run errors for one model.

Usage:
    python analysis/error_full.py <task-dir> <model-substring> [count]
"""

from __future__ import annotations

import glob
import json
import sys
from pathlib import Path

root = Path(sys.argv[1])
needle = sys.argv[2]
count = int(sys.argv[3]) if len(sys.argv) > 3 else 2


def walk(obj, out: list[str]):
    if isinstance(obj, dict):
        msg = obj.get("errorMessage")
        if isinstance(msg, str) and msg.strip():
            out.append(msg)
        for v in obj.values():
            walk(v, out)
    elif isinstance(obj, list):
        for v in obj:
            walk(v, out)


for p in sorted(glob.glob(str(root / "**" / "*.run.json"), recursive=True)):
    if needle not in p:
        continue
    msgs: list[str] = []
    walk(json.load(open(p, encoding="utf-8")), msgs)
    seen: set[str] = set()
    shown = 0
    for m in msgs:
        key = m.strip().splitlines()[-1][:80]
        if key in seen:
            continue
        seen.add(key)
        print(f"===== {Path(p).name}\n{m[-1500:]}\n")
        shown += 1
        if shown >= count:
            break
