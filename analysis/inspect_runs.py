"""Quick look at every downloaded answers file: score, row count, errors.

Usage:
    python analysis/inspect_runs.py [results/raw] [--wrong MODEL_SUBSTRING]
"""

from __future__ import annotations

import glob
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
root = Path(sys.argv[1]) if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else ROOT / "results" / "raw"
wrong_for = None
if "--wrong" in sys.argv:
    wrong_for = sys.argv[sys.argv.index("--wrong") + 1]
show_errors = "--errors" in sys.argv

for p in sorted(glob.glob(str(root / "**" / "world_clock_answers.json"), recursive=True)):
    d = json.load(open(p, encoding="utf-8"))
    err = d.get("errored", [])
    first_err = (err[0]["error"][:160] if err else "")
    print(
        f"{d.get('task', ''):24s} {d['model']:40s} {d['graded_correct']:3d}/{d['graded_total']:<3d} "
        f"rows={len(d['rows']):3d} errored={len(err):3d} {first_err}"
    )
    if show_errors and err:
        tails: dict[str, int] = {}
        for e in err:
            tail = e["error"].strip().splitlines()[-1][:200] if e["error"].strip() else "(empty)"
            tails[tail] = tails.get(tail, 0) + 1
        for tail, n in sorted(tails.items(), key=lambda kv: -kv[1])[:4]:
            print(f"   x{n:3d} {tail}")
    if wrong_for and wrong_for in d["model"]:
        for r in d["rows"]:
            if r["graded"] and not r["correct"]:
                print(f"   - {r['id']:45s} expected {json.dumps(r['expected'])} got {json.dumps(r['answer'])} | {r['note'][:120]}")
        for r in d["rows"]:
            if not r["graded"]:
                print(f"   ~ {r['id']:45s} got {json.dumps(r['answer'])} | {r['note'][:120]}")
