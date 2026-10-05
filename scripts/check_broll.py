"""Check every number and quotation the demo video's b-roll puts on screen.

Usage:
    python scripts/check_broll.py

The animated clips are drawn from the data by scripts/make_broll.py, but a few strings in
it are typed by hand (chart notes, the Opus 5 quotation, card subtitles). This recomputes
each of those from the data and fails if any disagrees, so the video can be rebuilt after
new runs without an on-screen claim going stale.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "analysis"))
sys.path.insert(0, str(ROOT / "scripts"))

from date_the_clock import RELEASE_DATES  # noqa: E402
from render_tables import SUMMARY, display  # noqa: E402
from tool_facts import facts  # noqa: E402
import make_broll as mb  # noqa: E402

failures: list[str] = []
src = (ROOT / "scripts" / "make_broll.py").read_text(encoding="utf-8")


def check(ok: bool, msg: str) -> None:
    print(("ok    " if ok else "WRONG ") + msg)
    if not ok:
        failures.append(msg)


mem = {display(r["model"]): r for r in SUMMARY if r["condition"] == "memory" and r["graded_total"]}

# b03: "19 of 19 models" and 11:00 vs 10:00
hook = "convert:calgary:toronto:2026-11-15:09:00"
from date_the_clock import find_answer_files  # noqa: E402

said = []
for p in find_answer_files(ROOT / "results" / "raw"):
    d = json.loads(p.read_text(encoding="utf-8"))
    if d.get("condition") == "memory" and d.get("graded_total") and "smoke" not in d.get("task", ""):
        row = next(r for r in d["rows"] if r["id"] == hook)
        said.append(row["answer"].get("time"))
check(len(said) == len(mem) and set(said) == {"11:00"}, f"b03: all {len(mem)} models said 11:00 from memory ({len(said)} answers, {set(said)})")
cases = {c["id"]: c for c in json.loads((ROOT / "cases" / "cases.json").read_text(encoding="utf-8"))}
check(cases[hook]["expected"]["time"] == "10:00", "b03: tzdata 2026d says 10:00")

# b07 / b08: changed 2026 answers per model, and the zero count spoken in the narration
cr = mb._changed_right()
zero = sum(1 for v in cr.values() if v == 0)
check(zero == 13 and len(cr) == 19, f"b08 and narration: 13 of 19 got none of the changed answers (data: {zero} of {len(cr)})")
check(all(mem[n]["per_family"]["control"]["total"] == 26 for n in mem), "b07: control share is out of 26 for every model")

# b10: Astra
a = mem["GPT-6 Astra"]["clock"]
check(a["earliest"]["iana"] == a["latest"]["iana"] == "2026b", "b10: Astra's clock dates to 2026b")
check(RELEASE_DATES["2026b"] == "2026-04-22" and "released April 22, 2026" in src, "b10: 2026b released April 22, 2026")
check(mem["GPT-6 Astra"]["card"]["stated_cutoff"] == "2026-04-30" and "April 30, 2026" in src, "b10: OpenAI's stated cutoff April 30, 2026")

# b11: Gemini
for n in ("Gemini 2.5 Pro", "Gemini 3.7 Flash", "Gemini 3.8 Flash"):
    c = mem[n]["clock"]
    check(c["earliest"]["iana"] == c["latest"]["iana"] == "2025a", f"b11: {n} peaks at 2025a")
check(RELEASE_DATES["2025a"].startswith("2025-01") and "All three peak at tzdata 2025a, January 2025" in src, "b11: 2025a is January 2025")

# b12 / b13: tool
f = facts()
check(len(f["hook_said_11"]) == 8 and f["n_full"] == 16, f"b13 and narration: half (8 of 16) said 11:00 with the tool (data: {len(f['hook_said_11'])} of {f['n_full']})")
check(sum(1 for v in f["asked"].values() if v >= 40) >= 14, "narration: nearly all used the tool (at least 14 of 16 on 40+ questions)")

# b14: the quotation must be in Opus 5's own words, verbatim
t = json.loads((ROOT / "results" / "tool_trace.json").read_text(encoding="utf-8"))
m = next(k for k in t if "opus-5" in k)
words = next(x for x in t[m]["cases"] if x["id"] == "offset:calgary:2026-11-15:12:00")["free_text"]
quote = "the tool reports -06:00 with abbreviation CST, which does not match Alberta's actual rules"
check(quote in words and quote in src.replace("\\'", "'"), "b14: Opus 5 quotation is verbatim from its own words")

# Lower thirds: every verified source in broll/_sources.json is on screen
plan = json.loads((ROOT / "demo.edit-plan.json").read_text(encoding="utf-8"))
thirds = {s["lower_third"] for s in plan["segments"]}
for s in json.loads((ROOT / "broll" / "_sources.json").read_text(encoding="utf-8")):
    if s["status"] == "verified" and s["lower_third"]:
        check(s["lower_third"] in thirds, f"lower third present: {s['lower_third']}")

print("\nb-roll check:", "FAILED" if failures else "OK")
sys.exit(1 if failures else 0)
