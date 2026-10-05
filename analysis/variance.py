"""How much does a model's result move between runs of the same questions?

Usage:
    python analysis/variance.py

Every complete from-memory run on disk (all 125 questions answered, task version 2 or
later, so the same questions and the same grading) is scored with date_the_clock's own
scorer. For each model with two or more such runs this reports the score range, the
release its clock is dated to in each run, and whether it put Calgary on -07:00 every
time. Writes results/variance.json and prints a table.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from date_the_clock import score_file  # noqa: E402
from render_tables import display  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent


def runs_by_model() -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {}
    for p in sorted((ROOT / "results" / "raw" / "world-clock-from-memory").glob("*/*/*/world_clock_answers.json")):
        version = int(p.parts[-4])
        if version < 2:
            continue
        d = json.loads(p.read_text(encoding="utf-8"))
        if len(d.get("rows", [])) != 125 or d.get("errored"):
            continue
        s = score_file(p)
        out.setdefault(display(s["model"]), []).append({
            "version": version,
            "run_id": int(p.parts[-2]),
            "score": s["graded_correct"],
            "clock": f"{s['clock']['earliest']['iana']}..{s['clock']['latest']['iana']}" if s["clock"] else None,
            "peak": s["clock"]["best_agreement"] if s["clock"] else None,
            "calgary_minus_7": s["calgary_on_standard_time_nov_15"],
        })
    return out


def summary() -> dict:
    per_model = {}
    for name, runs in runs_by_model().items():
        if len(runs) < 2:
            continue
        scores = [r["score"] for r in runs]
        per_model[name] = {
            "runs": runs,
            "n_runs": len(runs),
            "min": min(scores),
            "max": max(scores),
            "spread": max(scores) - min(scores),
            "clocks": sorted({r["clock"] for r in runs}),
            "calgary_minus_7_every_run": all(r["calgary_minus_7"] for r in runs),
        }
    spreads = [m["spread"] for m in per_model.values()]
    return {
        "models": per_model,
        "n_models": len(per_model),
        "n_runs": sum(m["n_runs"] for m in per_model.values()),
        "max_spread": max(spreads) if spreads else None,
        "max_spread_model": max(per_model, key=lambda n: per_model[n]["spread"]) if per_model else None,
        "median_spread": sorted(spreads)[len(spreads) // 2] if spreads else None,
        "same_clock_every_run": sorted(n for n, m in per_model.items() if len(m["clocks"]) == 1),
        "calgary_minus_7_every_run_all_models": all(m["calgary_minus_7_every_run"] for m in per_model.values()),
    }


if __name__ == "__main__":
    s = summary()
    (ROOT / "results" / "variance.json").write_text(json.dumps(s, indent=1), encoding="utf-8")
    print(f"{s['n_models']} models with 2+ complete runs, {s['n_runs']} runs")
    for name, m in sorted(s["models"].items(), key=lambda kv: -kv[1]["spread"]):
        print(f"  {name:26s} runs={m['n_runs']} scores {m['min']}..{m['max']} (spread {m['spread']}) clocks {m['clocks']} calgary -07 every run: {m['calgary_minus_7_every_run']}")
    print(f"max spread {s['max_spread']} ({s['max_spread_model']}), median {s['median_spread']}; same clock every run: {len(s['same_clock_every_run'])}; Calgary -07:00 in every run of every model: {s['calgary_minus_7_every_run_all_models']}")
