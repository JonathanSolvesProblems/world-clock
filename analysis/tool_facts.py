"""The numbers the post's tool section states, computed in one place.

Usage:
    python analysis/tool_facts.py

Reads results/summary.json and results/tool_trace.json (run date_the_clock.py and
tool_trace.py first). check_claims.py imports `facts()` and holds the prose to it.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from render_tables import N_SUBSET_GRADED, SUMMARY, display, tool_rows  # noqa: E402
from cases.specs import in_tool_subset  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
HOOK = "convert:calgary:toronto:2026-11-15:09:00"
COYHAIQUE = "offset:coyhaique:2025-07-15:12:00"


def _minus(s: str) -> str:
    return (s or "").replace("−", "-")


def facts() -> dict:
    trace = json.loads((ROOT / "results" / "tool_trace.json").read_text(encoding="utf-8"))
    mem = {display(r["model"]): r for r in SUMMARY if r["condition"] == "memory" and r["graded_total"]}
    full = {display(t["model"]): t for t in tool_rows() if t["graded_total"] == N_SUBSET_GRADED}
    summ = {n: trace[t["model"]]["summary"] for n, t in full.items()}
    cases = {n: {c["id"]: c for c in trace[t["model"]]["cases"] if c["graded"]} for n, t in full.items()}

    hook = {n: cases[n].get(HOOK) for n in full}
    said_11 = sorted(n for n, c in hook.items() if c and c["structured_value"] == "11:00")
    right_offsets = sorted(n for n in said_11 if "06:00" in _minus(hook[n]["note"]) and "05:00" in _minus(hook[n]["note"]))

    runs_37 = []
    for ver in ("4", "5", "6"):
        for p in sorted((ROOT / "results" / "raw" / "world-clock-tool-v2" / ver / "gemini-3.7-flash").glob("*/world_clock_answers.json")):
            d = json.loads(p.read_text(encoding="utf-8"))
            rows = [r for r in d["rows"] if r["graded"] and in_tool_subset(r["id"], r["family"])]
            if len(rows) == N_SUBSET_GRADED:
                runs_37.append(sum(1 for r in rows if r["correct"]))

    return {
        "n_full": len(full),
        "models": sorted(full),
        "asked_every_question": sorted(n for n in full if summ[n]["with_call"] == N_SUBSET_GRADED),
        "asked": {n: summ[n]["with_call"] for n in full},
        "tool_score": {n: full[n]["graded_correct"] for n in full},
        "memory_score": {n: mem[n]["tool_subset"]["correct"] for n in full if n in mem},
        "perfect": sorted(n for n in full if full[n]["graded_correct"] == N_SUBSET_GRADED),
        "at_least_34": sorted(n for n in full if full[n]["graded_correct"] >= 34),
        "max_memory": max(mem[n]["tool_subset"]["correct"] for n in full if n in mem),
        "hook_said_11": said_11,
        "hook_said_11_with_right_offsets": right_offsets,
        "overrode": {n: summ[n]["overrode"] for n in full},
        "overrode_total": sum(summ[n]["overrode"] for n in full),
        "right_before_restating": sum(summ[n]["right_before_restating"] for n in full),
        "fixed_by_restating": sum(1 for n in full for c in cases[n].values() if c["changed_when_restated"] and c["correct"]),
        "coyhaique_missed": sorted(n for n in full if cases[n].get(COYHAIQUE) and not cases[n][COYHAIQUE]["correct"]),
        "coyhaique_never_asked_the_zone": sorted(n for n in full if cases[n].get(COYHAIQUE) and cases[n][COYHAIQUE]["own_place_calls"] == 0),
        "coyhaique_right_via_other_zone": sorted(n for n in full if cases[n].get(COYHAIQUE) and cases[n][COYHAIQUE]["correct"] and cases[n][COYHAIQUE]["own_place_calls"] == 0),
        "clock_current": sorted(n for n in full if full[n].get("clock") and full[n]["clock"]["current"]),
        "gemini_3_7_flash_three_runs": runs_37,
        "reasoning_off": sorted(
            n for n, t in full.items()
            if any(r.get("reasoning_off") for r in json.loads((ROOT / t["source"]).read_text(encoding="utf-8"))["rows"])
        ) if all((ROOT / t["source"]).exists() for t in full.values()) else None,
    }


if __name__ == "__main__":
    print(json.dumps(facts(), indent=1))
