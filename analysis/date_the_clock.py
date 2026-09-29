"""Score downloaded runs and date each model's world clock.

Usage:
    python analysis/date_the_clock.py [results/raw]

Finds every `world_clock_answers.json` under the given directory (the layout that
`kaggle b t download` produces, or a flat folder), joins each answer to the per-release
answer key in `cases/cases.json`, and writes:

    results/summary.json   everything below, machine-readable, the only source the post may quote
    results/summary.md     the same as tables

For each (model, condition):
    accuracy overall and per family, on graded cases only
    agreement with every tzdata release since 2022a, on the ladder cases (the ones whose
        answer changed between releases); the release(s) with the highest agreement is the
        date of the model's world clock
    the unresolved Manitoba answers beside the official announcement
    tool-call counts, for the tool condition
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CASES = {c["id"]: c for c in json.loads((ROOT / "cases" / "cases.json").read_text(encoding="utf-8"))}
INDEX = json.loads((ROOT / "tzhist" / "releases" / "index.json").read_text())
RELEASES = sorted(INDEX, key=lambda v: tuple(int(x) for x in v.split(".")))

# Release dates from the tz NEWS file, for the sentence "this model's clock stopped in ...".
RELEASE_DATES = {
    "2022a": "2022-03-15", "2022b": "2022-08-10", "2022c": "2022-08-15", "2022d": "2022-09-23",
    "2022e": "2022-10-11", "2022f": "2022-10-28", "2022g": "2022-11-29",
    "2023a": "2023-03-22", "2023b": "2023-03-23", "2023c": "2023-03-28", "2023d": "2023-12-21",
    "2024a": "2024-02-01", "2024b": "2024-09-04",
    "2025a": "2025-01-15", "2025b": "2025-03-22", "2025c": "2025-12-10",
    "2026a": "2026-03-01", "2026b": "2026-04-22", "2026c": "2026-07-08", "2026d": "2026-09-11",
}


def canon(d: dict) -> str:
    return json.dumps(d, sort_keys=True)


CARDS_PATH = HERE / "model_cards.json"
CARDS = {k: v for k, v in json.loads(CARDS_PATH.read_text(encoding="utf-8")).items() if not k.startswith("_")} if CARDS_PATH.exists() else {}


def card_key(model: str) -> str:
    """Reduce a proxy model string to the shape used in model_cards.json.

    'anthropic/claude-opus-5@default' -> 'claude-opus-5'
    'openai/gpt-5.5-2026-04-23'       -> 'gpt-5.5'
    'xai/grok-4.20-0309-reasoning'    -> 'grok-4.20-reasoning'
    """
    import re as _re

    name = model.split("/")[-1].split("@")[0].lower()
    name = name.replace("-default", "")
    name = _re.sub(r"-\d{4}-\d{2}-\d{2}", "", name)
    name = _re.sub(r"-\d{8}", "", name)
    name = _re.sub(r"-\d{4}(?=-|$)", "", name)
    return name


def card_for(model: str) -> dict | None:
    want = card_key(model)
    for key, card in CARDS.items():
        if card_key(key) == want:
            return card
    return None


# Versions below these ran with a broken harness (no retry, per-job timeout) and are history.
MIN_VERSION = {"world-clock-from-memory": 2, "world-clock-tool-v2": 1}


def find_answer_files(root: Path) -> list[Path]:
    """One run per (task, model): the most complete, then the latest.

    The download layout is results/raw/<task>/<version>/<model>/<run_id>/... . Task
    versions 2 and 3 of the from-memory task ask identical questions and grade them the
    same way; they differ only in how the harness survives proxy errors. So a model is
    represented by whichever of its runs completed the most graded cases, and only by a
    later run when it completed at least as many. Versions below MIN_VERSION are skipped.
    """
    files = sorted(root.rglob("world_clock_answers.json"))
    best: dict[tuple[str, str], tuple[int, int, int, Path]] = {}
    for p in files:
        parts = p.parts
        try:
            run_id = int(parts[-2])
            model = parts[-3]
            version = int(parts[-4])
            task = parts[-5]
        except (ValueError, IndexError):
            best[(str(p), "")] = (0, 0, 0, p)
            continue
        if version < MIN_VERSION.get(task, 1):
            continue
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            completed = len(data.get("rows", []))
        except (OSError, ValueError):
            completed = 0
        key = (task, model)
        cur = best.get(key)
        if cur is None or (completed, version, run_id) > (cur[0], cur[1], cur[2]):
            best[key] = (completed, version, run_id, p)
    return sorted(p for (_c, _v, _r, p) in best.values())


def score_file(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    model = data.get("model") or path.parent.name
    condition = data.get("condition", "memory")
    task = data.get("task", "")
    rows = data.get("rows", [])
    calgary_falls_back = None
    for row in rows:
        if row["id"] == "change_day:calgary:2026-11-01":
            calgary_falls_back = bool(row["answer"].get("changes"))

    per_family = defaultdict(lambda: {"correct": 0, "total": 0})
    ladder_agree = {r: 0 for r in RELEASES}
    ladder_total = 0
    all_agree = {r: 0 for r in RELEASES}
    all_total = 0
    unresolved = []
    tool_calls = []
    wrong = []

    unparsed = 0
    for row in rows:
        case = CASES.get(row["id"])
        if case is None:
            continue
        if any(str(v).startswith("unparsed") for v in row["answer"].values()):
            unparsed += 1
        got = canon(row["answer"])
        if not case["graded"]:
            unresolved.append(
                {
                    "id": row["id"],
                    "prompt": case["prompt"],
                    "model_answer": row["answer"],
                    "tzdata_2026d": case["expected"],
                    "official": case.get("official_answer"),
                    "note": row.get("note", ""),
                }
            )
            continue
        fam = per_family[case["family"]]
        fam["total"] += 1
        fam["correct"] += int(row["correct"])
        if not row["correct"]:
            wrong.append({"id": row["id"], "family": case["family"], "expected": case["expected"], "got": row["answer"], "note": row.get("note", "")})
        all_total += 1
        for r in RELEASES:
            if canon(case["by_release"][r]) == got:
                all_agree[r] += 1
        if case["discriminates"]:
            ladder_total += 1
            for r in RELEASES:
                if canon(case["by_release"][r]) == got:
                    ladder_agree[r] += 1
        if condition == "tool":
            tool_calls.append(int(row.get("tool_calls") or 0))

    graded_total = sum(f["total"] for f in per_family.values())
    graded_correct = sum(f["correct"] for f in per_family.values())

    # Date the clock: releases tied at the maximum agreement on ladder cases.
    if ladder_total:
        best = max(ladder_agree.values())
        tied = [r for r in RELEASES if ladder_agree[r] == best]
        earliest, latest = tied[0], tied[-1]
        clock = {
            "ladder_cases": ladder_total,
            "best_agreement": best,
            "best_agreement_pct": round(100 * best / ladder_total, 1),
            "releases_tied": [f"{r} ({INDEX[r]['iana']}, {RELEASE_DATES[INDEX[r]['iana']]})" for r in tied],
            "earliest": {"pypi": earliest, "iana": INDEX[earliest]["iana"], "date": RELEASE_DATES[INDEX[earliest]["iana"]]},
            "latest": {"pypi": latest, "iana": INDEX[latest]["iana"], "date": RELEASE_DATES[INDEX[latest]["iana"]]},
            "current": latest == RELEASES[-1],
            "agreement_by_release": {f"{r} ({INDEX[r]['iana']})": ladder_agree[r] for r in RELEASES},
        }
    else:
        clock = None

    card = card_for(model)
    return {
        "model": model,
        "condition": condition,
        "task": task,
        "card": card,
        "calgary_still_falls_back_nov_1": calgary_falls_back,
        "source": str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path),
        "graded_correct": graded_correct,
        "graded_total": graded_total,
        "unparsed_answers": unparsed,
        "accuracy_pct": round(100 * graded_correct / graded_total, 1) if graded_total else None,
        "per_family": {k: {**v, "pct": round(100 * v["correct"] / v["total"], 1) if v["total"] else None} for k, v in sorted(per_family.items())},
        "clock": clock,
        "tool_calls": {
            "cases": len(tool_calls),
            "cases_with_a_call": sum(1 for t in tool_calls if t > 0),
            "total_calls": sum(tool_calls),
        } if condition == "tool" else None,
        "unresolved": unresolved,
        "wrong": wrong,
        "errored": data.get("errored", []),
    }


def to_markdown(results: list[dict]) -> str:
    lines = ["# World Clock results", ""]
    lines.append("| Model | Condition | Graded | Accuracy | Clock dated to | Ladder agreement | Vendor says cutoff | Calgary falls back Nov 1? |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for r in results:
        clock = r["clock"]
        dated = "n/a"
        agree = "n/a"
        if clock:
            if clock["current"] and clock["earliest"] == clock["latest"]:
                dated = f"current ({clock['latest']['iana']})"
            elif clock["current"]:
                dated = f"{clock['earliest']['iana']} to current"
            else:
                dated = f"{clock['earliest']['iana']} ({clock['earliest']['date']}) to {clock['latest']['iana']} ({clock['latest']['date']})"
            agree = f"{clock['best_agreement']}/{clock['ladder_cases']}"
        card = r.get("card") or {}
        stated = card.get("stated_cutoff") or "not published"
        calgary = {True: "yes (wrong)", False: "no (right)", None: "n/a"}[r.get("calgary_still_falls_back_nov_1")]
        lines.append(
            f"| {r['model']} | {r['condition']} | {r['graded_correct']}/{r['graded_total']} | "
            f"{r['accuracy_pct']}% | {dated} | {agree} | {stated} | {calgary} |"
        )
    lines.append("")
    families = sorted({fam for r in results for fam in r["per_family"]})
    lines.append("## Accuracy by family")
    lines.append("")
    lines.append("| Model | Condition | " + " | ".join(families) + " |")
    lines.append("|---|---|" + "---|" * len(families))
    for r in results:
        cells = []
        for fam in families:
            f = r["per_family"].get(fam)
            cells.append(f"{f['correct']}/{f['total']}" if f else "")
        lines.append(f"| {r['model']} | {r['condition']} | " + " | ".join(cells) + " |")
    lines.append("")
    lines.append("## Manitoba (announced, not yet in tzdata)")
    lines.append("")
    for r in results:
        for u in r["unresolved"]:
            lines.append(f"- {r['model']} [{r['condition']}] {u['id']}: model {json.dumps(u['model_answer'])}; tzdata 2026d {json.dumps(u['tzdata_2026d'])}; official {json.dumps(u['official'])}. Note: {u['note']}")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "results" / "raw"
    files = find_answer_files(root)
    if not files:
        raise SystemExit(f"no world_clock_answers.json under {root}")
    include_smoke = "--include-smoke" in sys.argv
    results = [score_file(p) for p in files]
    if not include_smoke:
        results = [r for r in results if "smoke" not in (r.get("task") or "")]
    # A run with no completed cases is a model the proxy could not serve at all (404, or
    # tool calling unsupported). Report it once on stderr and keep it out of the tables.
    empty = [r for r in results if r["graded_total"] == 0]
    for r in empty:
        first = r["errored"][0]["error"] if r["errored"] else "no rows"
        print(f"skipping {r['model']} [{r['condition']}]: {first[:120]}", file=sys.stderr)
    results = [r for r in results if r["graded_total"] > 0]
    results.sort(key=lambda r: (r["condition"], -(r["accuracy_pct"] or 0)))
    out_dir = ROOT / "results"
    out_dir.mkdir(exist_ok=True)
    (out_dir / "summary.json").write_text(json.dumps(results, indent=1, ensure_ascii=False), encoding="utf-8")
    (out_dir / "summary.md").write_text(to_markdown(results), encoding="utf-8")
    for r in results:
        clock = r["clock"]
        dated = "n/a" if not clock else f"{clock['earliest']['iana']}..{clock['latest']['iana']}"
        flag = f"  unparsed={r['unparsed_answers']}" if r["unparsed_answers"] else ""
        print(f"{r['model']:40s} {r['condition']:7s} {r['graded_correct']:3d}/{r['graded_total']}  clock {dated}{flag}")


if __name__ == "__main__":
    main()
