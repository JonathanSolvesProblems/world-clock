"""Pull each model's own one-sentence note for the cases the post talks about.

Usage:
    python analysis/quotes.py [--condition memory] [case_id ...]

Defaults to the Calgary, Vancouver, Casablanca, Coyhaique and Manitoba cases. Notes are
the model's words, recorded by the task and never graded; the post quotes them verbatim.
"""

from __future__ import annotations

import glob
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from date_the_clock import find_answer_files  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent

DEFAULT_CASES = [
    "change_day:calgary:2026-11-01",
    "offset:calgary:2026-11-15:12:00",
    "offset:vancouver:2026-12-15:12:00",
    "offset:casablanca:2026-10-15:12:00",
    "change_day:casablanca:2026-09-20",
    "offset:coyhaique:2025-07-15:12:00",
    "offset:almaty:2024-07-15:12:00",
    "change_day:winnipeg:2026-11-01",
]

condition = "memory"
args = sys.argv[1:]
if "--condition" in args:
    i = args.index("--condition")
    condition = args[i + 1]
    args = args[:i] + args[i + 2:]
cases = args or DEFAULT_CASES

files = find_answer_files(ROOT / "results" / "raw")
runs = []
for p in files:
    d = json.loads(p.read_text(encoding="utf-8"))
    if d.get("condition") != condition or "smoke" in d.get("task", ""):
        continue
    runs.append(d)
runs.sort(key=lambda d: -d["graded_correct"])

for cid in cases:
    print(f"\n### {cid}")
    for d in runs:
        row = next((r for r in d["rows"] if r["id"] == cid), None)
        if row is None:
            continue
        mark = "~  " if not row["graded"] else ("ok " if row["correct"] else "X  ")
        model = d["model"].split("/")[-1].split("@")[0]
        print(f"{mark}{model:28s} {json.dumps(row['answer']):40s} {row['note']}")
