"""Render the post's tables from results/summary.json.

Usage:
    python analysis/render_tables.py > results/tables.md

Every number the post shows comes out of here, so a re-run of the pipeline changes the
tables and check_claims.py catches any sentence that did not follow.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SUMMARY = json.loads((ROOT / "results" / "summary.json").read_text(encoding="utf-8"))
INDEX = json.loads((ROOT / "tzhist" / "releases" / "index.json").read_text())
RELEASES = sorted(INDEX, key=lambda v: tuple(int(x) for x in v.split(".")))

FAMILY_LABEL = {
    "control": "Controls",
    "awkward_offset": "Awkward offsets",
    "southern": "Southern DST",
    "legislated_2022_2025": "Changes 2022 to 2025",
    "wave_2026": "2026 wave",
}


def short(model: str) -> str:
    return model.split("/")[-1].split("@")[0]


def dated(r: dict) -> str:
    c = r.get("clock")
    if not c:
        return "n/a"
    if c["current"]:
        return "current (2026d)" if c["earliest"]["iana"] == "2026d" else f"{c['earliest']['iana']} to current"
    if c["earliest"]["iana"] == c["latest"]["iana"]:
        return f"{c['earliest']['iana']} ({c['earliest']['date'][:7]})"
    return f"{c['earliest']['iana']} to {c['latest']['iana']} ({c['earliest']['date'][:7]} to {c['latest']['date'][:7]})"


def headline(condition: str) -> str:
    rows = [r for r in SUMMARY if r["condition"] == condition and r["graded_total"]]
    rows.sort(key=lambda r: -r["graded_correct"])
    out = ["| Model | Score (of 122) | 2026 wave (of 25) | Clock dated by the ladder | Vendor's stated cutoff | Falls back Calgary on Nov 1? |", "|---|---|---|---|---|---|"]
    for r in rows:
        wave = r["per_family"].get("wave_2026", {})
        card = r.get("card") or {}
        calgary = {True: "yes", False: "no", None: "n/a"}[r.get("calgary_still_falls_back_nov_1")]
        score = str(r["graded_correct"])
        if r["graded_total"] != 122:
            score += f" (of {r['graded_total']}, {len(r.get('errored', []))} errored)"
        out.append(
            f"| {short(r['model'])} | {score} | {wave.get('correct', 0)}/{wave.get('total', 0)} | {dated(r)} | "
            f"{card.get('stated_cutoff') or 'not published'} | {calgary} |"
        )
    return "\n".join(out)


def by_family(condition: str) -> str:
    rows = [r for r in SUMMARY if r["condition"] == condition and r["graded_total"]]
    rows.sort(key=lambda r: -r["graded_correct"])
    fams = [f for f in FAMILY_LABEL if any(f in r["per_family"] for r in rows)]
    out = ["| Model | " + " | ".join(FAMILY_LABEL[f] for f in fams) + " |", "|---|" + "---|" * len(fams)]
    for r in rows:
        cells = []
        for f in fams:
            v = r["per_family"].get(f)
            cells.append(f"{v['correct']}/{v['total']}" if v else "")
        out.append(f"| {short(r['model'])} | " + " | ".join(cells) + " |")
    return "\n".join(out)


def ladder(condition: str) -> str:
    """Agreement with each tzdata release, ladder cases only. The max is the dated clock."""
    rows = [r for r in SUMMARY if r["condition"] == condition and r.get("clock")]
    rows.sort(key=lambda r: -r["graded_correct"])
    cols = [f"{v} ({INDEX[v]['iana']})" for v in RELEASES]
    out = ["| Model | " + " | ".join(INDEX[v]["iana"] for v in RELEASES) + " |", "|---|" + "---|" * len(RELEASES)]
    for r in rows:
        agree = r["clock"]["agreement_by_release"]
        best = r["clock"]["best_agreement"]
        cells = []
        for col in cols:
            n = agree[col]
            cells.append(f"**{n}**" if n == best else str(n))
        out.append(f"| {short(r['model'])} | " + " | ".join(cells) + " |")
    return "\n".join(out)


def manitoba(condition: str) -> str:
    rows = [r for r in SUMMARY if r["condition"] == condition and r["unresolved"]]
    rows.sort(key=lambda r: -r["graded_correct"])
    out = ["| Model | Winnipeg offset, Nov 15 | Clocks change Nov 1? | 09:00 Winnipeg in Toronto |", "|---|---|---|---|"]
    for r in rows:
        u = {x["id"]: x for x in r["unresolved"]}
        off = u.get("offset:winnipeg:2026-11-15:12:00", {}).get("model_answer", {}).get("utc_offset", "")
        ch = u.get("change_day:winnipeg:2026-11-01", {}).get("model_answer", {})
        conv = u.get("convert:winnipeg:toronto:2026-11-15:09:00", {}).get("model_answer", {}).get("time", "")
        ch_s = ("yes, " + ch.get("direction", "")) if ch.get("changes") else "no"
        out.append(f"| {short(r['model'])} | {off} | {ch_s} | {conv} |")
    out.append("| tzdata 2026d says | -06:00 | yes, back | 10:00 |")
    out.append("| Manitoba says | -05:00 | no | 09:00 |")
    return "\n".join(out)


def tool_vs_memory() -> str:
    mem = {short(r["model"]): r for r in SUMMARY if r["condition"] == "memory" and r["graded_total"]}
    tool = {short(r["model"]): r for r in SUMMARY if r["condition"] == "tool" and r["graded_total"]}
    out = ["| Model | From memory | With the tool | Cases where it called the tool | Total tool calls |", "|---|---|---|---|---|"]
    for name in sorted(tool, key=lambda n: -tool[n]["graded_correct"]):
        t = tool[name]
        m = mem.get(name)
        tc = t.get("tool_calls") or {}
        out.append(
            f"| {name} | {m['graded_correct'] if m else 'n/a'} | {t['graded_correct']} | "
            f"{tc.get('cases_with_a_call', 0)}/{tc.get('cases', 0)} | {tc.get('total_calls', 0)} |"
        )
    return "\n".join(out)


def counts() -> str:
    mem = [r for r in SUMMARY if r["condition"] == "memory" and r["graded_total"]]
    fall = sum(1 for r in mem if r.get("calgary_still_falls_back_nov_1"))
    current = sum(1 for r in mem if r.get("clock") and r["clock"]["current"])
    return (
        f"Models scored from memory: {len(mem)}. Still fall back Calgary on November 1: {fall} of {len(mem)}. "
        f"Clocks dated current: {current} of {len(mem)}."
    )


if __name__ == "__main__":
    print("## Counts\n")
    print(counts())
    print("\n## Headline, from memory\n")
    print(headline("memory"))
    print("\n## By family, from memory\n")
    print(by_family("memory"))
    print("\n## Ladder agreement, from memory (bold = the release the clock is dated to)\n")
    print(ladder("memory"))
    print("\n## Manitoba, from memory\n")
    print(manitoba("memory"))
    if any(r["condition"] == "tool" for r in SUMMARY):
        print("\n## With the tool\n")
        print(tool_vs_memory())
        print("\n## By family, with the tool\n")
        print(by_family("tool"))
