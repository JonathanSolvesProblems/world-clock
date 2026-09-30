"""What did each downloaded run cost, and when?

Usage:
    python analysis/run_costs.py [results/raw]

The Model Proxy bills per request and the account has a quota, so a lineup has to be
planned against it. Every request in a .run.json carries its token counts and its cost in
nanodollars. This sums them per run, with the run's start time, and totals per UTC day.
"""

from __future__ import annotations

import glob
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def walk_requests(node, out: list) -> None:
    """Collect the metrics of every model request in a run file.

    Only members of a `requests` list count. A conversation also carries a `metrics` block
    that totals its own requests, and counting both doubles every cost. That is what the
    first version of this script did; the account's quota (analysis/quota.py) read half
    of what it reported, which is how the mistake was found.
    """
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "requests" and isinstance(value, list):
                for req in value:
                    if isinstance(req, dict):
                        metrics = req.get("metrics")
                        if isinstance(metrics, dict) and ("inputTokensCostNanodollars" in metrics or "outputTokensCostNanodollars" in metrics):
                            out.append(metrics)
                        for k2, v2 in req.items():
                            if k2 != "metrics":
                                walk_requests(v2, out)
            else:
                walk_requests(value, out)
    elif isinstance(node, list):
        for v in node:
            walk_requests(v, out)


def first_key(node, key: str):
    if isinstance(node, dict):
        if key in node and isinstance(node[key], str):
            return node[key]
        for v in node.values():
            r = first_key(v, key)
            if r:
                return r
    elif isinstance(node, list):
        for v in node:
            r = first_key(v, key)
            if r:
                return r
    return None


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "results" / "raw"
    rows = []
    for p in sorted(glob.glob(str(root / "**" / "*.run.json"), recursive=True)):
        path = Path(p)
        try:
            run = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            print(f"unreadable {path}: {exc}")
            continue
        reqs: list = []
        walk_requests(run, reqs)
        nano = sum(int(m.get("inputTokensCostNanodollars", 0) or 0) + int(m.get("outputTokensCostNanodollars", 0) or 0) for m in reqs)
        tin = sum(int(m.get("inputTokens", 0) or 0) for m in reqs)
        tout = sum(int(m.get("outputTokens", 0) or 0) for m in reqs)
        start = first_key(run, "startTime") or ""
        parts = path.relative_to(root).parts  # task / version / model / run id / file
        task, version, model = parts[0], parts[1], parts[2]
        answers = path.parent / "world_clock_answers.json"
        done = ""
        if answers.exists():
            a = json.loads(answers.read_text(encoding="utf-8"))
            done = f"{len(a.get('rows', []))} cases"
        rows.append((start, task, version, model, len(reqs), tin, tout, nano / 1e9, done))

    rows.sort()
    per_day: dict[str, float] = defaultdict(float)
    print(f"{'start (UTC)':20s} {'task':24s} v  {'model':30s} {'requests':>8s} {'in tok':>9s} {'out tok':>8s} {'cost $':>8s}  done")
    for start, task, version, model, n, tin, tout, cost, done in rows:
        per_day[start[:10]] += cost
        print(f"{start[:19]:20s} {task:24s} {version:2s} {model:30s} {n:8d} {tin:9d} {tout:8d} {cost:8.3f}  {done}")
    print()
    for day in sorted(per_day):
        print(f"{day or 'unknown':12s} total ${per_day[day]:.2f}")
    print(f"all runs     total ${sum(per_day.values()):.2f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
