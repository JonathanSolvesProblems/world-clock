"""Fail if the prose and the data disagree.

Usage:
    python check_claims.py

Every number the README and the post state about the case set and the results is
recomputed here from `cases/cases.json`, `results/summary.json` and the downloaded runs,
and the script exits non-zero if any of them disagree. Run it before every commit that
touches prose.

Three kinds of check:

1. Anchored numbers. A short phrase from the prose with <N> where a number sits, and the
   value the data says belongs there. Numbers may be written as digits or as words. The
   anchors for POST.md are required: if a sentence is reworded, this file has to follow,
   which is the point. A number that quietly stops being checked is the failure mode.
2. The post's tables must match what analysis/render_tables.py generates, byte for byte.
3. Every quotation in the post longer than a few words must appear verbatim in some
   model's recorded note. The post cannot put words in a model's mouth.
"""

from __future__ import annotations

import json
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "analysis"))

CASES = json.loads((ROOT / "cases" / "cases.json").read_text(encoding="utf-8"))
INDEX = json.loads((ROOT / "tzhist" / "releases" / "index.json").read_text(encoding="utf-8"))
POST = ROOT / "POST.md"
README = ROOT / "README.md"
TASK = ROOT / "tasks" / "render_task.py"
SUMMARY_PATH = ROOT / "results" / "summary.json"

WORDS = (
    "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen "
    "fifteen sixteen seventeen eighteen nineteen twenty"
).split()
WORD_TO_INT = {w: i for i, w in enumerate(WORDS)}

failures: list[str] = []
missing: list[str] = []


def as_int(token: str) -> int | None:
    token = token.lower().strip()
    if token.isdigit():
        return int(token)
    return WORD_TO_INT.get(token)


def squash(s: str) -> str:
    return re.sub(r"\s+", " ", s)[:160]


def expect(pattern: str, *values: int, files=(POST,), required: bool = True) -> None:
    """Every sentence matching `pattern` must carry `values` at its <N> slots."""
    rx = re.compile(pattern.replace("<N>", r"([\w-]+)").replace("<D>", r"(\d+)"), re.IGNORECASE)
    want = [int(v) for v in values]
    seen = False
    for path in files:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for m in rx.finditer(text):
            seen = True
            got = [as_int(g) for g in m.groups()]
            if got != want:
                failures.append(f"{path.name}: '{squash(m.group(0))}' should carry {want}, carries {got}")
    if required and not seen:
        missing.append(f"POST.md has no sentence matching /{pattern}/ (data says {want})")


def data(ok: bool, message: str) -> None:
    if not ok:
        failures.append(message)


def require_text(literal: str, path: Path = POST) -> None:
    if literal not in path.read_text(encoding="utf-8"):
        missing.append(f"{path.name} no longer contains '{literal}'")


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKC", s)
    for a, b in (("−", "-"), ("–", "-"), ("—", "-"), ("’", "'"), ("‘", "'"), ("“", '"'), ("”", '"')):
        s = s.replace(a, b)
    return re.sub(r"\s+", "", s)


def check_case_set() -> None:
    n_cases = len(CASES)
    n_graded = sum(1 for c in CASES if c["graded"])
    n_ladder = sum(1 for c in CASES if c["discriminates"])
    n_unresolved = n_cases - n_graded
    fam = Counter(c["family"] for c in CASES if c["graded"])
    wave_changed = sum(1 for c in CASES if c["family"] == "wave_2026" and c["discriminates"])

    # README and the task docstring.
    legacy = (README, TASK)
    expect(r"\b<D> (?:time-zone )?questions\b", n_cases, files=legacy, required=False)
    expect(r"\b<D> cases\b(?! whose)", n_cases, files=legacy, required=False)
    expect(r"\b<D> graded cases\b", n_graded, files=legacy, required=False)
    expect(r"over the <D> graded", n_graded, files=legacy, required=False)
    expect(r"\b<D> of them change answer", n_ladder, files=legacy, required=False)
    expect(r"\b<D> Manitoba cases\b", n_unresolved, files=legacy, required=False)
    expect(r"those <N> cases are recorded", n_unresolved, files=legacy, required=False)

    # The post.
    expect(r"<N> questions, three kinds", n_cases)
    expect(r"its <N> questions are asked, recorded, and never counted", n_unresolved)
    expect(r"That leaves <N> graded questions", n_graded)
    expect(r"Of the <N>, <N> have an answer that changed between one tzdata release and another", n_graded, n_ladder)
    expect(r"unpacked, <N> of them", len(INDEX))
    expect(r"<N> of the <N> questions about the 2026 wave have an answer that changed", wave_changed, fam["wave_2026"])
    expect(r"The other <N> are controls inside the family", fam["wave_2026"] - wave_changed)
    expect(r"all <N> control questions correctly", fam["control"])
    expect(r"on the <N> changed questions", wave_changed)

    data(INDEX["2026.2"]["iana"] == "2026b", "PyPI tzdata 2026.2 is no longer IANA 2026b in tzhist/releases/index.json")
    data(INDEX["2025.1"]["iana"] == "2025a", "PyPI tzdata 2025.1 is no longer IANA 2025a in tzhist/releases/index.json")
    require_text("tzdata 2026b was released on April 22, 2026")
    require_text("tzdata 2025a, released January 15, 2025")


def check_release_dates() -> None:
    """The release dates the post spells out must match what the ladder itself uses."""
    from date_the_clock import RELEASE_DATES  # type: ignore[attr-defined]

    data(RELEASE_DATES.get("2026b") == "2026-04-22", f"the ladder dates 2026b to {RELEASE_DATES.get('2026b')}, the post says April 22, 2026")
    data(RELEASE_DATES.get("2025a") == "2025-01-15", f"the ladder dates 2025a to {RELEASE_DATES.get('2025a')}, the post says January 15, 2025")
    data(RELEASE_DATES.get("2026c") == "2026-07-08", f"the ladder dates 2026c to {RELEASE_DATES.get('2026c')}, the post says July 8")
    require_text("the next release, 2026c, came on July 8")


def load_rows(condition: str) -> dict[str, dict[str, dict]]:
    """model -> case id -> row, for the run of each model that analysis/date_the_clock.py scored."""
    from date_the_clock import find_answer_files

    out: dict[str, dict[str, dict]] = {}
    for p in find_answer_files(ROOT / "results" / "raw"):
        d = json.loads(p.read_text(encoding="utf-8"))
        if d.get("condition") != condition or "smoke" in d.get("task", "") or not d.get("graded_total"):
            continue
        out[d["model"]] = {r["id"]: r for r in d["rows"]}
    return out


def check_results() -> None:
    from render_tables import display, month, post_table, tool_vs_memory

    summary = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))
    mem = [r for r in summary if r["condition"] == "memory" and r["graded_total"]]
    tool = [r for r in summary if r["condition"] == "tool" and r["graded_total"]]
    n_mem = len(mem)
    by_name = {display(r["model"]): r for r in mem}
    rows_mem = load_rows("memory")
    data(set(rows_mem) == {r["model"] for r in mem}, "summary.json and the downloaded runs disagree on which memory runs count; re-run analysis/date_the_clock.py")
    text = POST.read_text(encoding="utf-8")

    def row(name: str) -> dict | None:
        r = by_name.get(name)
        if r is None:
            failures.append(f"the post talks about {name} but there is no scored memory run for it")
        return r

    def rows_of(name: str) -> dict[str, dict]:
        r = row(name)
        return rows_mem.get(r["model"], {}) if r else {}

    def card(name: str) -> dict:
        r = row(name)
        return (r or {}).get("card") or {}

    def fam(name: str, family: str) -> tuple[int, int]:
        v = (row(name) or {}).get("per_family", {}).get(family, {})
        return v.get("correct", -1), v.get("total", -1)

    # Lineup.
    expect(r"<N> models, all through Kaggle Benchmarks", n_mem)

    # Title and the Calgary offset question.
    standard = sum(1 for r in mem if r.get("calgary_on_standard_time_nov_15") is True)
    answered = sum(1 for r in mem if r.get("calgary_on_standard_time_nov_15") is not None)
    expect(r"<N> of <N> frontier models still put Calgary on standard time", standard, answered)
    expect(r"All <N> models said -07:00", standard)
    data(standard == answered, "the post says 'All N models said -07:00' but some model that answered did not")

    # The hook: 09:00 Calgary to Toronto on November 15.
    conv = "convert:calgary:toronto:2026-11-15:09:00"
    conv_rows = [rows[conv] for rows in rows_mem.values() if conv in rows]
    conv_1100 = sum(1 for r in conv_rows if (r.get("answer") or {}).get("time") == "11:00")
    expect(r"<N> of the <N> answered that one", len(conv_rows), n_mem)
    expect(r"the other <N> dropped it", n_mem - len(conv_rows))
    expect(r"all <N> said 11:00", conv_1100)
    data(conv_1100 == len(conv_rows), "the post says all of them said 11:00 on Calgary to Toronto, but some answered otherwise")
    expect(r"On the Calgary to Toronto question, <N> models gave the same wrong answer", conv_1100)

    # Controls and awkward offsets.
    n_control = sum(1 for c in CASES if c["graded"] and c["family"] == "control")
    control_perfect = sum(1 for r in mem if r["per_family"].get("control", {}).get("correct") == r["per_family"].get("control", {}).get("total") == n_control)
    full_control = [r["per_family"]["control"]["correct"] for r in mem if r["per_family"].get("control", {}).get("total") == n_control]
    awkward_perfect = sum(1 for r in mem if r["per_family"].get("awkward_offset", {}).get("correct") == r["per_family"].get("awkward_offset", {}).get("total"))
    expect(r"<N> of the <N> answered all <N> control questions correctly", control_perfect, n_mem, n_control)
    expect(r"no complete run scored below <N> of <N>", min(full_control), n_control)
    expect(r"<N> got every awkward-offset question they answered right", awkward_perfect)

    # The 2026 wave.
    changed_ids = [c["id"] for c in CASES if c["family"] == "wave_2026" and c["discriminates"]]
    unchanged_ids = [c["id"] for c in CASES if c["family"] == "wave_2026" and c["graded"] and not c["discriminates"]]

    def n_right(rows: dict[str, dict], ids: list[str]) -> int:
        return sum(1 for i in ids if i in rows and rows[i]["correct"])

    all_unchanged = sum(1 for rows in rows_mem.values() if n_right(rows, unchanged_ids) == len(unchanged_ids))
    zero_changed = sum(1 for rows in rows_mem.values() if n_right(rows, changed_ids) == 0)
    total_changed_right = sum(n_right(rows, changed_ids) for rows in rows_mem.values())
    astra_changed = n_right(rows_of("GPT-6 Astra"), changed_ids)
    gemini = [m for m in rows_mem if "gemini" in m]
    gemini_zero = sum(1 for m in gemini if n_right(rows_mem[m], changed_ids) == 0)
    expect(r"<N> of the <N> got all <N>\b", all_unchanged, n_mem, len(unchanged_ids))
    expect(r"<N> of the <N> got none of the <N> changed answers right", zero_changed, n_mem, len(changed_ids))
    expect(r"<N> of the <N> Geminis", gemini_zero, len(gemini))
    expect(r"there were <N> correct answers", total_changed_right)
    expect(r"GPT-6 Astra produced <N> of them", astra_changed)
    expect(r"The other <N> came with reasons", total_changed_right - astra_changed)
    for name in ("Claude Opus 5", "GPT-5.5", "GPT-5.6 Terra"):
        data(n_right(rows_of(name), changed_ids) == 0, f"{name} got a changed 2026 answer right; the post says it got none")
    astra_bc = [i for i in changed_ids if i in rows_of("GPT-6 Astra") and rows_of("GPT-6 Astra")[i]["correct"]]
    data(astra_bc and all(":vancouver" in i for i in astra_bc), f"GPT-6 Astra's correct 2026 answers are not all about Vancouver: {astra_bc}")

    # The ladder.
    def assert_clock(name: str, earliest: str, latest: str, agreement: int) -> None:
        r = row(name)
        if not r:
            return
        c = r["clock"]
        got = (c["earliest"]["iana"], c["latest"]["iana"], c["best_agreement"])
        data(got == (earliest, latest, agreement), f"{name}: post says clock {earliest}..{latest} at {agreement}, data says {got[0]}..{got[1]} at {got[2]}")

    assert_clock("GPT-6 Astra", "2026b", "2026b", 46)
    for name in ("GPT-5.5", "GPT-5.6 Terra", "Claude Opus 5"):
        assert_clock(name, "2025b", "2026a", 46)
    for name in ("Gemini 2.5 Pro", "Gemini 3.7 Flash", "Gemini 3.8 Flash"):
        assert_clock(name, "2025a", "2025a", 44)
    assert_clock("Gemini 3.1 Pro", "2025a", "2025a", 45)
    assert_clock("Gemini 3.5 Flash-Lite", "2024a", "2024b", 36)
    assert_clock("Claude Sonnet 5", "2022f", "2022f", 39)
    assert_clock("Claude Haiku 4.5", "2022b", "2022d", 37)
    expect(r"agrees with tzdata 2026b on all <N> changed answers", 46)
    expect(r"identical to the answer, <N> of <N> at the peak", 44, 46)
    expect(r"at 2024a to 2024b with a blurry <N> of <N>", 36, 46)

    def curve(name: str) -> str:
        r = row(name)
        return json.dumps(r["clock"]["agreement_by_release"], sort_keys=True) if r else ""

    data(len({curve(n) for n in ("Gemini 2.5 Pro", "Gemini 3.7 Flash", "Gemini 3.8 Flash")}) == 1, "the three Gemini curves the post calls identical are not identical")
    data(len({curve(n) for n in ("GPT-5.5", "GPT-5.6 Terra", "Claude Opus 5")}) == 1, "GPT-5.5, GPT-5.6 Terra and Claude Opus 5 do not share one curve")
    astra = row("GPT-6 Astra")
    if astra:
        a = astra["clock"]["agreement_by_release"]
        by_iana = {k.split("(")[1].rstrip(")"): v for k, v in a.items()}
        data(by_iana["2026c"] < by_iana["2026b"] - 10, "GPT-6 Astra's agreement does not fall off at 2026c the way the post says")
        data(all(by_iana[r] <= by_iana["2026b"] for r in by_iana), "GPT-6 Astra's peak is not 2026b")

    # Stated cutoffs and release dates the prose spells out.
    data(card("GPT-6 Astra").get("stated_cutoff") == "2026-04-30", "GPT-6 Astra's stated cutoff is no longer 2026-04-30 in model_cards.json")
    require_text("OpenAI says the model's cutoff is April 30, 2026")
    data(month(card("GPT-5.5").get("stated_cutoff", "")) == "December 2025" and month(card("GPT-5.6 Terra").get("stated_cutoff", "")) == "February 2026", "GPT-5.5 / GPT-5.6 Terra cutoffs changed in model_cards.json")
    require_text("December 2025 and February 2026, both consistent")
    data(month(card("Claude Opus 5").get("stated_cutoff", "")) == "May 2026", "Claude Opus 5's stated cutoff changed in model_cards.json")
    require_text("trained on data to May 2026")
    data(month(card("Gemini 2.5 Pro").get("released", "")) == "June 2025" and month(card("Gemini 3.7 Flash").get("released", "")) == "August 2026" and month(card("Gemini 3.8 Flash").get("released", "")) == "September 2026", "Gemini release months changed in model_cards.json")
    require_text("Gemini 2.5 Pro from June 2025, Gemini 3.7 Flash from August 2026 and Gemini 3.8 Flash from September 2026")
    data(month(card("Claude Sonnet 5").get("stated_cutoff", "")) == "January 2026" and month(card("Claude Haiku 4.5").get("stated_cutoff", "")) == "February 2025", "Sonnet 5 / Haiku 4.5 cutoffs changed in model_cards.json")
    require_text("stated cutoffs of January 2026 and February 2025")
    sonnet, haiku = row("Claude Sonnet 5"), row("Claude Haiku 4.5")
    if sonnet and haiku:
        data(month(sonnet["clock"]["earliest"]["date"]) == "October 2022", "Sonnet 5's clock is no longer dated October 2022")
        data(month(haiku["clock"]["earliest"]["date"]) == "August 2022" and month(haiku["clock"]["latest"]["date"]) == "September 2022", "Haiku 4.5's clock is no longer dated August to September 2022")
    require_text("Claude Sonnet 5 dates to October 2022 and Claude Haiku 4.5 to August or September 2022")

    # Legislated changes 2022 to 2025.
    s_ok, s_total = fam("Claude Sonnet 5", "legislated_2022_2025")
    expect(r"It scored <N> of <N> on the changes legislated between 2022 and 2025", s_ok, s_total)
    for name in ("GPT-6 Astra", "GPT-5.5", "GPT-5.6 Terra", "Claude Opus 5"):
        ok, total = fam(name, "legislated_2022_2025")
        data(ok == total == s_total, f"{name} did not score {s_total} of {s_total} on the legislated changes; the post says it did")
    expect(r"Opus 5 scored <N> of <N>\.", s_total, s_total)

    # Manitoba.
    mb = "change_day:winnipeg:2026-11-01"
    mb_rows = {m: rows[mb] for m, rows in rows_mem.items() if mb in rows}
    mb_back = sum(1 for r in mb_rows.values() if (r.get("answer") or {}).get("changes") is True and (r.get("answer") or {}).get("direction") == "back")
    expect(r"<N> answered and all <N> said the clocks fall back", len(mb_rows), mb_back)
    data(mb_back == len(mb_rows), "the post says every model that answered the Winnipeg question said the clocks fall back; the data disagrees")

    # Hedging: the post says nobody flagged their training cutoff.
    hedge = re.compile(r"training data|knowledge cutoff|as of my|may have changed|might have changed|cannot know|can't know|subject to change", re.IGNORECASE)
    hedged = [(display(m), r["id"], r["note"]) for m, rows in rows_mem.items() for r in rows.values() if hedge.search(r.get("note") or "")]
    expect(r"Not one of the <N> said", n_mem)
    data(not hedged, "the post says no model hedged about its training cutoff, but these notes do: " + "; ".join(f"{m} on {i}: {n[:90]}" for m, i, n in hedged[:5]))

    # Any 'N of M' beside a model's name must be that model's score.
    for r in summary:
        if not r["graded_total"]:
            continue
        name = re.escape(display(r["model"]))
        # "X went from A to B of N" is the tool sentence, checked separately below.
        expect(rf"{name}(?:(?!went from)[^.\n|]){{0,80}}?\b<N> of {r['graded_total']}\b", r["graded_correct"], required=False)

    # With the tool.
    for t in tool:
        name = display(t["model"])
        m = by_name.get(name)
        if m:
            expect(rf"{re.escape(name)} went from <N> to <N> of <N>", m["graded_correct"], t["graded_correct"], t["graded_total"], required=False)
        tc = t.get("tool_calls") or {}
        if re.search(rf"{re.escape(name)}[^.]*?called the tool on every case", text):
            data(tc.get("cases_with_a_call") == tc.get("cases"), f"{name} did not call the tool on every case ({tc.get('cases_with_a_call')} of {tc.get('cases')})")

    # Tables.
    data(post_table("memory") in text, "POST.md's headline table differs from analysis/render_tables.py post_table(); regenerate it and paste")
    if "| Model | From memory | With the tool |" in text:
        data(tool_vs_memory() in text, "POST.md's tool table differs from analysis/render_tables.py tool_vs_memory(); regenerate it and paste")

    # Quotations.
    notes = set()
    for condition in ("memory", "tool"):
        for rows in load_rows(condition).values():
            for r in rows.values():
                if r.get("note"):
                    notes.add(norm(r["note"]))
    body = text.split("---", 2)[-1]
    for q in re.findall(r'"([^"\n]{40,})"', body):
        nq = norm(q)
        if not any(nq in n for n in notes):
            failures.append(f"quotation is not in any model's recorded note: \"{q[:90]}\"")


def main() -> int:
    check_case_set()
    check_release_dates()
    if SUMMARY_PATH.exists():
        check_results()
    else:
        print("no results/summary.json yet; checked the case set only")

    if failures or missing:
        print("CLAIM CHECK FAILED")
        for f in failures:
            print("  wrong:   " + f)
        for m in missing:
            print("  missing: " + m)
        return 1
    n_cases = len(CASES)
    n_graded = sum(1 for c in CASES if c["graded"])
    n_ladder = sum(1 for c in CASES if c["discriminates"])
    print(f"claims OK: {n_cases} cases, {n_graded} graded, {n_ladder} ladder, {n_cases - n_graded} unresolved")
    return 0


if __name__ == "__main__":
    sys.exit(main())
