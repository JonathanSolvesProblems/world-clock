"""Print the distinct final lines of every sub-run error in the downloaded .run.json files.

Usage:
    python analysis/error_tails.py [results/raw/<task>]
"""

from __future__ import annotations

import glob
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
root = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "results" / "raw" / "world-clock-from-memory"


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
    data = json.load(open(p, encoding="utf-8"))
    msgs: list[str] = []
    walk(data, msgs)
    if not msgs:
        continue
    model = Path(p).parts[-3]
    tails = Counter(m.strip().splitlines()[-1][:260] for m in msgs)
    print(f"\n== {model}: {len(msgs)} errors")
    for tail, n in tails.most_common(3):
        print(f"   x{n:3d} {tail}")
