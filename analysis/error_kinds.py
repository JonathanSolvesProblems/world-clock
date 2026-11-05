"""Does the ladder date what a model remembers, or only what it answers?

Usage:
    python analysis/error_kinds.py

The test comes from Arhan Canli's comment on the DEV post. Sonnet 5 says "Almaty has used
the UTC+6 time zone year-round since 2024-03-01": the right date with the wrong value. A
model with stale knowledge would not know the date at all, so a wrong answer that names the
real change may be holding a ladder position down for the wrong reason.

Every wrong answer on the changes legislated between 2022 and 2025 was read by hand (153 of
them), and the ones whose note names the real change are listed in NAMED below, each with
the words that show it, so the labels can be checked and argued with. The kinds:

    no mention   the note does not name the change that flips this answer
    wrong date   the note names the change, with a wrong date or no date
    right date   the note names the change with the right date, and the answer is still wrong

"Since 2005" for Almaty is not a mention: that is the previous change, stated as current.
Answers that restate the old rule (Morocco's permanent +01:00) are no mention either, and no
wrong answer on the 2026 wave names the 2026 change.

For each model this reruns the ladder two ways: without the questions it named the change
on, and without every question in those jurisdictions. It also dates each model by legal
change instead of by question, since 46 questions come from 16 places and 12 changes, and
reports how far each peak stands above the best release outside it. Last, it checks what the
with-the-tool runs did on the questions a model got wrong from memory.

Writes results/error_kinds.json and results/error_kinds.md.
"""

from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from date_the_clock import CASES, INDEX, RELEASES, canon  # noqa: E402
from render_tables import display  # noqa: E402

ROOT = HERE.parent

# One legal change can cover several places.
JURISDICTION = {
    "calgary": "alberta",
    "edmonton": "alberta",
    "inuvik": "northwest_territories",
    "yellowknife": "northwest_territories",
    "mexico_city": "mexico",
    "chihuahua": "mexico",
    "nuuk": "greenland",
    "ittoqqortoormiit": "greenland",
}

# Hand labels: (text in the model name, kind, text in the note on a wrong answer).
NAMED = [
    ("sonnet-5", "wrong date", "before abolishing DST later that year"),
    ("sonnet-5", "right date", "brief 2023 reinstatement"),
    ("sonnet-5", "right date", "since 2024-03-01"),
    ("sonnet-5", "right date", "two-zone system"),
    ("qwen", "right date", "permanently observes daylight saving time (UTC+4:30) since 2022"),
    ("qwen", "right date", "eliminated daylight saving time nationwide effective October 30, 2022"),
    ("qwen", "right date", "Greenland abolished daylight saving time in 2023"),
    ("qwen", "wrong date", "Paraguay abolished daylight saving time in 2022"),
    ("qwen", "wrong date", "Paraguay abolished daylight saving time in 2023"),
    ("glm-5", "right date", "elimination of Daylight Saving Time in most of Mexico"),
    ("glm-5", "wrong date", "abolished Daylight Saving Time in March 2024"),
    ("glm-5", "wrong date", "cancelled daylight saving time for 2024"),
    ("gemini-2.5-pro", "right date", "starting in March 2023"),
    ("gemini-3.7-flash", "right date", "2023 time zone reform"),
    ("gemini-3.7-flash", "right date", "on March 31, 2024"),
    ("gemini-3.1-pro", "right date", "November 2022 amendment"),
    ("gemini-3.1-pro", "right date", "On March 31, 2024"),
    ("gemini-3.5-flash-lite", "right date", "changes enacted in late 2022"),
    ("gemini-3.5-flash-lite", "wrong date", "starting in November 2023"),
    ("gemma", "right date", "abolished daylight saving time in 2022"),
    ("4.20-0309-reasoning", "right date", "2022 DST elimination rule"),
    ("opus-4-5", "right date", "ended daylight saving time in most of the country in 2022"),
    ("opus-4-5", "right date", "abolished daylight saving time in 2023 and moved"),
    ("deepseek", "right date", "Mexico's 2022 time zone reform"),
    ("non-reasoning", "right date", "post-2023 rules"),
    ("haiku", "wrong date", "daylight saving time was abolished in Greenland"),
]


def jurisdiction(case_id: str) -> str:
    place = case_id.split(":")[1]
    return JURISDICTION.get(place, place)


def iana(pypi: str) -> str:
    return INDEX[pypi]["iana"]


def ladder_rows(rows: list[dict]) -> list[dict]:
    return [r for r in rows if r["id"] in CASES and CASES[r["id"]]["discriminates"] and CASES[r["id"]]["graded"]]


def matches(row: dict, release: str) -> bool:
    return canon(CASES[row["id"]]["by_release"][release]) == canon(row["answer"])


def peak(rows: list[dict]) -> dict:
    agree = {rel: sum(matches(r, rel) for r in rows) for rel in RELEASES}
    best = max(agree.values())
    tied = [rel for rel in RELEASES if agree[rel] == best]
    return {"agree": best, "of": len(rows), "from": iana(tied[0]), "to": iana(tied[-1])}


def peak_by_change(rows: list[dict]) -> dict:
    """Each legal change counts once: its share of questions matching the release."""
    groups: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        groups[jurisdiction(r["id"])].append(r)
    score = {rel: sum(sum(matches(r, rel) for r in g) / len(g) for g in groups.values()) for rel in RELEASES}
    best = max(score.values())
    tied = [rel for rel in RELEASES if abs(score[rel] - best) < 1e-9]
    rest = max((v for rel, v in score.items() if rel not in tied), default=0.0)
    return {
        "score": round(best, 2),
        "of": len(groups),
        "from": iana(tied[0]),
        "to": iana(tied[-1]),
        "margin": round(best - rest, 2),
    }


def label(model: str, note: str) -> tuple[int, str] | None:
    for i, (who, kind, text) in enumerate(NAMED):
        if who in model and text in note:
            return i, kind
    return None


def main() -> None:
    summary = json.loads((ROOT / "results" / "summary.json").read_text(encoding="utf-8"))
    memory = [r for r in summary if r["condition"] == "memory"]
    tool = {r["model"]: r for r in summary if r["condition"] == "tool"}

    used: set[int] = set()
    models = []
    named_rows = []
    wrong_total = legislated_wrong = 0
    tool_outcome = {"named": Counter(), "no mention": Counter()}

    for result in memory:
        rows = ladder_rows(json.loads((ROOT / result["source"]).read_text(encoding="utf-8"))["rows"])
        tool_rows = {}
        if result["model"] in tool:
            data = json.loads((ROOT / tool[result["model"]]["source"]).read_text(encoding="utf-8"))
            tool_rows = {r["id"]: r for r in data["rows"]}

        kinds: Counter = Counter()
        dropped = set()
        for row in rows:
            if row["correct"]:
                continue
            wrong_total += 1
            legislated = CASES[row["id"]]["family"] == "legislated_2022_2025"
            legislated_wrong += legislated
            found = label(result["model"], row.get("note") or "")
            if found:
                used.add(found[0])
                kinds[found[1]] += 1
                dropped.add(row["id"])
            with_tool = tool_rows.get(row["id"])
            if with_tool:
                with_tool_correct = bool(with_tool["correct"])
                calls = int(with_tool.get("tool_calls") or 0)
            if found:
                named_rows.append({
                    "model": display(result["model"]),
                    "case": row["id"],
                    "kind": found[1],
                    "answer": row["answer"],
                    "expected": CASES[row["id"]]["expected"],
                    "note": row.get("note") or "",
                    "with_tool": {"correct": with_tool_correct, "tool_calls": calls} if with_tool else None,
                })
            if legislated and with_tool:
                outcome = tool_outcome["named" if found else "no mention"]
                outcome["asked"] += 1
                outcome["fixed"] += with_tool_correct
                if found:
                    outcome["fixed_with_a_call"] += with_tool_correct and calls > 0
                    outcome["missed_without_a_call"] += (not with_tool_correct) and calls == 0

        places = {jurisdiction(i) for i in dropped}
        models.append({
            "model": display(result["model"]),
            "stated_cutoff": (result.get("card") or {}).get("stated_cutoff"),
            "named_wrong_date": kinds["wrong date"],
            "named_right_date": kinds["right date"],
            "ladder": peak(rows),
            "without_named_questions": peak([r for r in rows if r["id"] not in dropped]),
            "without_named_jurisdictions": peak([r for r in rows if jurisdiction(r["id"]) not in places]),
            "by_change": peak_by_change(rows),
        })

    unused = [NAMED[i] for i in range(len(NAMED)) if i not in used]
    if unused:
        raise SystemExit(f"labels that matched nothing: {unused}")

    ladder_cases = [c for c in CASES.values() if c["discriminates"] and c["graded"]]
    out = {
        "ladder_questions": len(ladder_cases),
        "places": len({c["id"].split(":")[1] for c in ladder_cases}),
        "legal_changes": len({jurisdiction(c["id"]) for c in ladder_cases}),
        "wrong_answers_on_ladder": wrong_total,
        "wrong_answers_legislated": legislated_wrong,
        "named_the_change": len(named_rows),
        "dated_the_same_by_change": sum(
            (m["by_change"]["from"], m["by_change"]["to"]) == (m["ladder"]["from"], m["ladder"]["to"]) for m in models
        ),
        "peak_won_by_at_most_one_change": sum(m["by_change"]["margin"] <= 1 for m in models),
        "peak_won_by_at_most_half_a_change": sum(m["by_change"]["margin"] <= 0.5 for m in models),
        "tool_on_legislated_questions_wrong_from_memory": {k: dict(v) for k, v in tool_outcome.items()},
        "models": models,
        "named": named_rows,
    }
    (ROOT / "results" / "error_kinds.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")

    def span(p: dict) -> str:
        return p["from"] if p["from"] == p["to"] else f"{p['from']} to {p['to']}"

    named, plain = tool_outcome["named"], tool_outcome["no mention"]
    lines = [
        "# What the wrong answers say",
        "",
        "From `analysis/error_kinds.py`, a test suggested by Arhan Canli on the DEV post. Every wrong "
        "answer on the 2022 to 2025 changes was read by hand; the labels are in the script.",
        "",
        f"- {out['named_the_change']} of {legislated_wrong} wrong answers on the 2022 to 2025 changes name the real change.",
        f"- {out['ladder_questions']} ladder questions come from {out['places']} places and {out['legal_changes']} legal changes.",
        f"- Counted by legal change, {out['dated_the_same_by_change']} of {len(models)} models land on the same releases.",
        f"- {out['peak_won_by_at_most_one_change']} of {len(models)} peaks are won by one change or less, "
        f"{out['peak_won_by_at_most_half_a_change']} by half a change or less.",
        f"- Wrong from memory and asked with the tool: {named['fixed']} of {named['asked']} fixed where the note named the change, "
        f"{plain['fixed']} of {plain['asked']} where it did not. All {named['fixed_with_a_call']} fixed had called the tool; "
        f"the {named['missed_without_a_call']} missed had not.",
        "",
        "| Model | Stated cutoff | Named, wrong date | Named, right date | Ladder | Without those questions | Without those jurisdictions | By legal change | Margin |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for m in models:
        lines.append(
            f"| {m['model']} | {m['stated_cutoff'] or 'not published'} | {m['named_wrong_date']} | {m['named_right_date']} "
            f"| {span(m['ladder'])} | {span(m['without_named_questions'])} | {span(m['without_named_jurisdictions'])} "
            f"| {span(m['by_change'])} | {m['by_change']['margin']} |"
        )
    lines += ["", "## The notes", ""]
    for n in named_rows:
        tool_part = ""
        if n["with_tool"]:
            verdict = "right" if n["with_tool"]["correct"] else "wrong"
            tool_part = f" With the tool: {verdict}, {n['with_tool']['tool_calls']} call(s)."
        lines.append(f"- **{n['model']}**, `{n['case']}`, {n['kind']}: \"{n['note'].strip()}\"{tool_part}")
    lines.append("")
    (ROOT / "results" / "error_kinds.md").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines[:16]))


if __name__ == "__main__":
    main()
