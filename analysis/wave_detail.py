"""Which of the 25 questions about 2026 did each model get right, and which of those
are the five whose answer did not change (the controls inside the wave family)?

Usage:
    python analysis/wave_detail.py [--condition memory]
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from date_the_clock import find_answer_files  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
CASES = {c["id"]: c for c in json.loads((ROOT / "cases" / "cases.json").read_text(encoding="utf-8"))}
condition = "memory"
if "--condition" in sys.argv:
    condition = sys.argv[sys.argv.index("--condition") + 1]

wave = [cid for cid, c in CASES.items() if c["family"] == "wave_2026"]
unchanged = [cid for cid in wave if not CASES[cid]["discriminates"]]
changed = [cid for cid in wave if CASES[cid]["discriminates"]]
print(f"wave cases: {len(wave)}; unchanged (controls inside the family): {len(unchanged)}; changed: {len(changed)}")
for cid in unchanged:
    print(f"  unchanged: {cid}")

for p in find_answer_files(ROOT / "results" / "raw"):
    d = json.loads(p.read_text(encoding="utf-8"))
    if d.get("condition") != condition or "smoke" in d.get("task", "") or not d.get("graded_total"):
        continue
    rows = {r["id"]: r for r in d["rows"]}
    right_changed = [cid for cid in changed if cid in rows and rows[cid]["correct"]]
    right_unchanged = [cid for cid in unchanged if cid in rows and rows[cid]["correct"]]
    model = d["model"].split("/")[-1].split("@")[0]
    print(f"\n{model}: {len(right_unchanged)}/{len(unchanged)} unchanged right, {len(right_changed)}/{len(changed)} changed right")
    for cid in right_changed:
        print(f"    + {cid}  | {rows[cid]['note'][:150]}")
