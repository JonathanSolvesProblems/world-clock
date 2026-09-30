"""Render the post's tables from results/summary.json.

Usage:
    python analysis/render_tables.py > results/tables.md

Every number the post shows comes out of here, so a re-run of the pipeline changes the
tables and check_claims.py catches any sentence that did not follow.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SUMMARY =json.loads((ROOT / "results" / "summary.json").read_text(encoding="utf-8"))
INDEX = json.loads((ROOT / "tzhist" / "releases" / "index.json").read_text(encoding="utf-8"))
CASES = json.loads((ROOT / "cases" / "cases.json").read_text(encoding="utf-8"))
RELEASES = sorted(INDEX, key=lambda v: tuple(int(x) for x in v.split(".")))

FAMILY_LABEL = {
    "control": "Controls",
    "awkward_offset": "Awkward offsets",
    "southern": "Southern DST",
    "legislated_2022_2025": "Changes 2022 to 2025",
    "wave_2026": "2026 wave",
}


N_GRADED = sum(1 for c in CASES if c["graded"])
N_WAVE = sum(1 for c in CASES if c["graded"] and c["family"] == "wave_2026")

sys.path.insert(0, str(ROOT))
from cases.specs import in_tool_subset  # noqa: E402

N_SUBSET = sum(1 for c in CASES if in_tool_subset(c["id"], c["family"]))
N_SUBSET_GRADED = sum(1 for c in CASES if c["graded"] and in_tool_subset(c["id"], c["family"]))

# How the post names each model. Anything not listed is shown by its slug.
DISPLAY = {
    "gpt-6-astra": "GPT-6 Astra",
    "gpt-5.6-terra": "GPT-5.6 Terra",
    "gpt-5.5-2026-04-23": "GPT-5.5",
    "gpt-5.4-mini-2026-03-17": "GPT-5.4 mini",
    "gpt-oss-120b": "gpt-oss-120b",
    "claude-opus-5": "Claude Opus 5",
    "claude-sonnet-5": "Claude Sonnet 5",
    "claude-haiku-4-5": "Claude Haiku 4.5",
    "claude-opus-4-5": "Claude Opus 4.5",
    "gemini-3.8-flash": "Gemini 3.8 Flash",
    "gemini-3.7-flash": "Gemini 3.7 Flash",
    "gemini-3.5-flash-lite": "Gemini 3.5 Flash-Lite",
    "gemini-3.1-pro-preview": "Gemini 3.1 Pro",
    "gemini-2.5-pro": "Gemini 2.5 Pro",
    "gemma-4-31b-it": "Gemma 4 31B",
    "gemma-4-31b": "Gemma 4 31B",
    "grok-4.20-0309-reasoning": "Grok 4.20 Reasoning",
    "grok-4.20-0309-non-reasoning": "Grok 4.20",
    "deepseek-r1-0528": "DeepSeek-R1",
    "glm-5": "GLM-5",
    "qwen3-next-80b-a3b-thinking": "Qwen3-Next 80B Thinking",
}

MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]


def short(model: str) -> str:
    return model.split("/")[-1].split("@")[0]


def display(model: str) -> str:
    return DISPLAY.get(short(model), short(model))


def month(date: str) -> str:
    """'2026-04-22' -> 'April 2026'; '2026-04' -> 'April 2026'; '2026' -> '2026'."""
    parts = date.split("-")
    if len(parts) == 1:
        return parts[0]
    return f"{MONTHS[int(parts[1]) - 1]} {parts[0]}"


def long_date(date: str) -> str:
    """'2026-04-22' -> 'April 22, 2026'."""
    y, m, d = date.split("-")
    return f"{MONTHS[int(m) - 1]} {int(d)}, {y}"


def dated_post(r: dict) -> str:
    """The clock cell as the post prints it, with month names."""
    c = r.get("clock")
    if not c:
        return "n/a"
    peak = f", agrees on {c['best_agreement']} of {c['ladder_cases']}"
    e, l = c["earliest"], c["latest"]
    if c["current"]:
        return ("current (2026d)" if e["iana"] == "2026d" else f"{e['iana']} to current") + peak
    if e["iana"] == l["iana"]:
        return f"{e['iana']} ({month(e['date'])})" + peak
    return f"{e['iana']} to {l['iana']} ({month(e['date'])} to {month(l['date'])})" + peak


def post_table(condition: str = "memory") -> str:
    """The headline table exactly as POST.md must carry it. check_claims.py compares them byte for byte."""
    rows = [r for r in SUMMARY if r["condition"] == condition and r["graded_total"]]
    rows.sort(key=lambda r: (-r["graded_correct"], short(r["model"])))
    out = [
        f"| Model | Released | Score (of {N_GRADED}) | 2026 questions right (of {N_WAVE}) | Clock dated by the ladder | Vendor's stated cutoff |",
        "|---|---|---|---|---|---|",
    ]
    for r in rows:
        wave = r["per_family"].get("wave_2026", {})
        card = r.get("card") or {}
        score = str(r["graded_correct"]) if r["graded_total"] == N_GRADED else f"{r['graded_correct']} of {r['graded_total']}"
        w = str(wave.get("correct", 0)) if wave.get("total") == N_WAVE else f"{wave.get('correct', 0)} of {wave.get('total', 0)}"
        out.append(
            f"| {display(r['model'])} | {card.get('released') or 'not published'} | {score} | {w} | {dated_post(r)} | "
            f"{card.get('stated_cutoff') or 'not published'} |"
        )
    return "\n".join(out)


def dated(r: dict) -> str:
    c = r.get("clock")
    if not c:
        return "n/a"
    peak = f", agrees on {c['best_agreement']} of {c['ladder_cases']}"
    if c["current"]:
        base = "current (2026d)" if c["earliest"]["iana"] == "2026d" else f"{c['earliest']['iana']} to current"
        return base + peak
    if c["earliest"]["iana"] == c["latest"]["iana"]:
        return f"{c['earliest']['iana']} ({c['earliest']['date'][:7]})" + peak
    return f"{c['earliest']['iana']} to {c['latest']['iana']} ({c['earliest']['date'][:7]} to {c['latest']['date'][:7]})" + peak


def headline(condition: str) -> str:
    rows = [r for r in SUMMARY if r["condition"] == condition and r["graded_total"]]
    rows.sort(key=lambda r: -r["graded_correct"])
    out = ["| Model | Released | Score (of 122) | 2026 wave (of 25) | Clock dated by the ladder | Vendor's stated cutoff | Calgary on Nov 15, 2026 |", "|---|---|---|---|---|---|---|"]
    for r in rows:
        wave = r["per_family"].get("wave_2026", {})
        card = r.get("card") or {}
        calgary = {True: "-07:00 (wrong)", False: "-06:00 (right)", None: "no answer"}[r.get("calgary_on_standard_time_nov_15")]
        score = str(r["graded_correct"])
        if r["graded_total"] != 122:
            score += f" (of {r['graded_total']}, {len(r.get('errored', []))} errored)"
        out.append(
            f"| {short(r['model'])} | {card.get('released') or '?'} | {score} | {wave.get('correct', 0)}/{wave.get('total', 0)} | {dated(r)} | "
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
        off = u.get("offset:winnipeg:2026-11-15:12:00", {}).get("model_answer", {}).get("utc_offset", "no answer")
        conv = u.get("convert:winnipeg:toronto:2026-11-15:09:00", {}).get("model_answer", {}).get("time", "no answer")
        if "change_day:winnipeg:2026-11-01" in u:
            ch = u["change_day:winnipeg:2026-11-01"].get("model_answer") or {}
            ch_s = ("yes, " + ch.get("direction", "")) if ch.get("changes") else "no"
        else:
            ch_s = "no answer"
        out.append(f"| {short(r['model'])} | {off} | {ch_s} | {conv} |")
    out.append("| tzdata 2026d says | -06:00 | yes, back | 10:00 |")
    out.append("| Manitoba says | -05:00 | no | 09:00 |")
    return "\n".join(out)


TRACE_PATH = ROOT / "results" / "tool_trace.json"
TRACE = json.loads(TRACE_PATH.read_text(encoding="utf-8")) if TRACE_PATH.exists() else {}

# A tool run that answered fewer graded questions than this before it died says nothing
# about the model and is left out of the tables and charts.
TOOL_MIN_CASES = 10


def tool_rows() -> list[dict]:
    return [r for r in SUMMARY if r["condition"] == "tool" and r["graded_total"] >= TOOL_MIN_CASES]


def tool_vs_memory() -> str:
    """The post's tool table. Scores are 'N' when every graded case was answered, else 'N of M'.

    The last four columns come from analysis/tool_trace.py, which reads the conversations:
    how many graded cases the model asked the tool about at all, how many times it asked
    about the right place and date and then answered something else, how many times it
    only asked about some other zone, and how many answers changed between the model's own
    words and the JSON it produced when the SDK asked it to restate the answer.
    """
    mem = {short(r["model"]): r for r in SUMMARY if r["condition"] == "memory" and r["graded_total"]}
    tool = {short(r["model"]): r for r in tool_rows()}

    def score(r: dict | None) -> str:
        """Score on the tool task's questions: 'N' when all of them were answered, else 'N of M'."""
        if not r:
            return "n/a"
        s = r.get("tool_subset") or {"correct": r["graded_correct"], "total": r["graded_total"]}
        return str(s["correct"]) if s["total"] == N_SUBSET_GRADED else f"{s['correct']} of {s['total']}"

    out = [
        f"| Model | From memory (of {N_SUBSET_GRADED}) | With the tool (of {N_SUBSET_GRADED}) | Asked the tool | Overrode it | Asked about another zone only | Answer changed when restated |",
        "|---|---|---|---|---|---|---|",
    ]
    for name in sorted(tool, key=lambda n: (-tool[n]["graded_total"], -tool[n]["graded_correct"], n)):
        t = tool[name]
        s = (TRACE.get(t["model"]) or {}).get("summary") or {}
        if s:
            asked = f"{s['with_call']} of {s['cases']}"
            trace_cells = f"{asked} | {s['overrode']} | {s['other_zone_only']} | {s['changed_when_restated']}"
        else:
            tc = t.get("tool_calls") or {}
            trace_cells = f"{tc.get('cases_with_a_call', 0)} of {tc.get('cases', 0)} | n/a | n/a | n/a"
        out.append(f"| {display(t['model'])} | {score(mem.get(name))} | {score(t)} | {trace_cells} |")
    return "\n".join(out)


def counts() -> str:
    mem = [r for r in SUMMARY if r["condition"] == "memory" and r["graded_total"]]
    fall = sum(1 for r in mem if r.get("calgary_still_falls_back_nov_1"))
    answered = [r for r in mem if r.get("calgary_on_standard_time_nov_15") is not None]
    standard = sum(1 for r in answered if r["calgary_on_standard_time_nov_15"])
    current = sum(1 for r in mem if r.get("clock") and r["clock"]["current"])
    return (
        f"Models scored from memory: {len(mem)}. Put Calgary on Mountain Standard Time (-07:00) on "
        f"November 15, 2026: {standard} of {len(answered)} that answered. Assert a fall-back on November 1: "
        f"{fall} of {len(mem)}. Clocks dated current: {current} of {len(mem)}."
    )


if __name__ == "__main__":
    print("## Counts\n")
    print(counts())
    print("\n## Headline, from memory\n")
    print(headline("memory"))
    print("\n## The post's table, from memory (POST.md must carry this verbatim)\n")
    print(post_table("memory"))
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
