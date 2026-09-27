"""Fail if the prose and the data disagree.

Usage:
    python check_claims.py

Reads every number the README and the post are allowed to state about the case set and
the results, recomputes each from `cases/cases.json` and `results/summary.json`, and exits
non-zero on the first mismatch. Run it before every commit that touches prose.

Claims are written in the prose as plain numbers; this script knows which sentence each
number lives in by a short anchor phrase, so a stale number cannot survive a re-run of the
pipeline unnoticed.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CASES = json.loads((ROOT / "cases" / "cases.json").read_text(encoding="utf-8"))
PROSE_FILES = [ROOT / "README.md", ROOT / "POST.md", ROOT / "tasks" / "render_task.py"]

failures: list[str] = []


def expect(anchor_regex: str, value: int | str, files=PROSE_FILES) -> None:
    """Every occurrence of the anchor in the prose must carry `value`."""
    pattern = re.compile(anchor_regex)
    seen = False
    for path in files:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for m in pattern.finditer(text):
            seen = True
            if str(value) not in m.group(0):
                failures.append(f"{path.name}: '{m.group(0)}' should carry {value}")
    if not seen:
        # Not stated anywhere: nothing to check. Silence is allowed; wrongness is not.
        return


def main() -> int:
    n_cases = len(CASES)
    n_graded = sum(1 for c in CASES if c["graded"])
    n_ladder = sum(1 for c in CASES if c["discriminates"])
    n_unresolved = n_cases - n_graded

    expect(r"\b\d+ (?:time-zone )?questions\b", n_cases)
    expect(r"\b\d+ cases\b(?! whose)", n_cases)
    expect(r"\b\d+ graded cases\b", n_graded)
    expect(r"over the \d+ graded", n_graded)
    expect(r"\b\d+ of them change answer", n_ladder)
    expect(r"\b\d+ Manitoba cases\b", n_unresolved)
    expect(r"those \w+ cases are recorded", {1: "one", 2: "two", 3: "three", 4: "four"}.get(n_unresolved, str(n_unresolved)))

    summary_path = ROOT / "results" / "summary.json"
    if summary_path.exists():
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        # The post may state each model's graded score as "N of 122" or "N/122" only if it matches.
        for r in summary:
            model = re.escape(r["model"].split("/")[-1])
            expect(rf"{model}[^.\n]{{0,80}}?\b\d+ ?(?:of|/) ?{r['graded_total']}\b", r["graded_correct"], [ROOT / "POST.md"])
        # Headline: how many models fall back Calgary on Nov 1 (memory condition).
        memory = [r for r in summary if r["condition"] == "memory"]
        if memory:
            still_fall_back = 0
            for r in memory:
                for w in r["wrong"]:
                    if w["id"] == "change_day:calgary:2026-11-01":
                        still_fall_back += 1
            expect(r"\b\d+ of \d+ frontier models still turn", f"{still_fall_back} of {len(memory)}", [ROOT / "POST.md", ROOT / "SCRIPT.md"])

    if failures:
        print("CLAIM CHECK FAILED")
        for f in failures:
            print("  " + f)
        return 1
    print(f"claims OK: {n_cases} cases, {n_graded} graded, {n_ladder} ladder, {n_unresolved} unresolved")
    return 0


if __name__ == "__main__":
    sys.exit(main())
