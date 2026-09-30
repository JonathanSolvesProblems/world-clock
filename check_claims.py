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
    expect(r"I asked <N> models what time it is", n_mem)
    gemma = row("Gemma 4 31B")
    if gemma:
        unparsed = gemma.get("unparsed_answers")
        unparsed = len(unparsed) if isinstance(unparsed, list) else int(unparsed or 0)
        expect(r"Gemma 4 left the answer field empty on <N> of them", unparsed)

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
    expect(r"All <N> said 11:00", conv_1100)
    data(conv_1100 == len(conv_rows) == n_mem, f"the post says all {n_mem} said 11:00 on Calgary to Toronto; {len(conv_rows)} answered and {conv_1100} said 11:00")
    expect(r"On the Calgary to Toronto question, all <N> models gave the same wrong answer", conv_1100)

    # Controls and awkward offsets.
    n_control = sum(1 for c in CASES if c["graded"] and c["family"] == "control")
    control_perfect = sum(1 for r in mem if r["per_family"].get("control", {}).get("correct") == r["per_family"].get("control", {}).get("total") == n_control)
    full_control = [r["per_family"]["control"]["correct"] for r in mem if r["per_family"].get("control", {}).get("total") == n_control]
    awkward_perfect = sum(1 for r in mem if r["per_family"].get("awkward_offset", {}).get("correct") == r["per_family"].get("awkward_offset", {}).get("total"))
    expect(r"<N> of the <N> answered all <N> control questions correctly", control_perfect, n_mem, n_control)
    expect(r"nobody scored below <N> of <N>", min(full_control), n_control)
    data(len(full_control) == n_mem, f"the post says nobody scored below {min(full_control)} of {n_control} on the controls, but {n_mem - len(full_control)} runs did not answer every control")
    expect(r"<N> got every awkward-offset question right", awkward_perfect)

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
    expect(r"not one of those <N> notes says that anything changed in 2026", total_changed_right - astra_changed)
    expect(r"I read every one of the <N>\.", total_changed_right - astra_changed)
    astra_model = (row("GPT-6 Astra") or {}).get("model")
    mentions_change = re.compile(r"(permanent|abolish|adopt|no longer|scrapp|ended|stopped).{0,80}2026|2026.{0,80}(permanent|abolish|adopt|no longer|scrapp|ended|stopped)", re.IGNORECASE | re.DOTALL)
    for m, rows in rows_mem.items():
        if m == astra_model:
            continue
        for i in changed_ids:
            r = rows.get(i)
            if r and r["correct"] and mentions_change.search(r.get("note") or ""):
                failures.append(f"{display(m)}'s note on {i} does describe a 2026 change; the post says none of the non-Astra correct notes do: {r['note'][:120]}")
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
    expect(r"identical, point for point, <N> of <N> at the peak", 44, 46)
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
    expect(r"<N> said the clocks fall back, which is also what tzdata 2026d says", mb_back)
    data(len(mb_rows) == n_mem, f"the post says every model answered the Winnipeg question; {len(mb_rows)} of {n_mem} did")
    not_back = [display(m) for m, r in mb_rows.items() if not ((r.get("answer") or {}).get("changes") is True and (r.get("answer") or {}).get("direction") == "back")]
    data(not_back == ["Qwen3-Next 80B Thinking"], f"the post says only Qwen denied the Winnipeg fall-back; the data says {not_back}")

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

    # With the tool. Everything here is scored on the tool task's subset of questions.
    from render_tables import N_SUBSET, N_SUBSET_GRADED, tool_rows
    from run_costs import walk_requests
    from tool_trace import FORMAT_PROMPT

    trace_path = ROOT / "results" / "tool_trace.json"
    trace = json.loads(trace_path.read_text(encoding="utf-8")) if trace_path.exists() else {}
    tool_by_name = {display(t["model"]): t for t in tool_rows()}

    def trace_summary(name: str) -> dict:
        t = tool_by_name.get(name)
        return ((trace.get(t["model"]) if t else None) or {}).get("summary") or {}

    expect(r"asks <N> of the <N> questions: every question about 2026", N_SUBSET, len(CASES))
    expect(r"Then I asked <N> of the questions a second time", N_SUBSET)
    expect(r"<N> of the <N> are graded", N_SUBSET_GRADED, N_SUBSET)

    # The tool section's numbers all come from analysis/tool_facts.py.
    from tool_facts import facts as tool_facts

    f = tool_facts()
    n_full = f["n_full"]
    qwen = "Qwen3-Next 80B Thinking"
    expect(r"<N> models finished it", n_full)
    expect(r"<N> of the <N> asked the tool on every one of the <N> questions", len(f["asked_every_question"]), n_full, N_SUBSET_GRADED)
    expect(r"GPT-5\.6 Terra on <N> and Claude Sonnet 5 on <N>", f["asked"].get("GPT-5.6 Terra", -1), f["asked"].get("Claude Sonnet 5", -1))
    expect(
        r"Qwen asked on <N>, answered the rest from memory, and scored <N>, which is lower than the <N> it got without the tool",
        f["asked"].get(qwen, -1), f["tool_score"].get(qwen, -1), f["memory_score"].get(qwen, -1),
    )
    not_all = sorted(set(f["models"]) - set(f["asked_every_question"]))
    data(not_all == sorted(["GPT-5.6 Terra", "Claude Sonnet 5", qwen]), f"the post names Terra, Sonnet 5 and Qwen as the ones that did not ask on every question; the data says {not_all}")
    expect(r"<N> of the <N> got at least 34 of 43 with the tool", len(f["at_least_34"]), n_full)
    expect(r"nobody got more than <N> from memory", f["max_memory"])
    data(f["perfect"] == ["Claude Haiku 4.5"], f"the post says Claude Haiku 4.5 is the only model with all {N_SUBSET_GRADED}; the data says {f['perfect']}")
    data(f["overrode"].get("Claude Haiku 4.5") == 0, "the post says Haiku 4.5 never answered against the database; the trace says it did")

    expect(r"<N> of the <N> still said 11:00", len(f["hook_said_11"]), n_full)
    expect(r"<N> of those <N> wrote the correct offsets in the same sentence", len(f["hook_said_11_with_right_offsets"]), len(f["hook_said_11"]))
    data("GPT-5.6 Terra" in f["hook_said_11_with_right_offsets"], "GPT-5.6 Terra is quoted as writing the right offsets and answering 11:00; the data disagrees")
    expect(r"Across the <N> models there were <N> answers like that", n_full, f["overrode_total"])
    expect(r"In <N> cases the model's own words had the right answer and the restated one did not", f["right_before_restating"])
    expect(r"<N> answers went the other way", f["fixed_by_restating"])
    if len(f["gemini_3_7_flash_three_runs"]) == 3:
        expect(r"scored <N>, <N> and <N>\.", *f["gemini_3_7_flash_three_runs"])
    expect(
        r"<N> of the <N> missed the question, and only <N> asked about America/Coyhaique at all",
        len(f["coyhaique_missed"]), n_full, n_full - len(f["coyhaique_never_asked_the_zone"]),
    )
    asked_40 = sum(1 for v in f["asked"].values() if v >= 40)
    expect(r"<N> of the <N> models that had the database asked it on at least 40 of the 43 questions", asked_40, n_full)
    expect(r"<N> of the <N> still told Calgary it was 11:00 in Toronto", len(f["hook_said_11"]), n_full)
    if f["reasoning_off"] is not None:
        data(f["reasoning_off"] == ["GPT-5.6 Terra"], f"the post says only GPT-5.6 Terra ran the tool half with reasoning off; the runs say {f['reasoning_off']}")
    data("GPT-6 Astra" not in f["models"], "the post says GPT-6 Astra is missing from the tool half, but it has a scored tool run")

    def tcase(name: str, case_id: str) -> dict:
        t = tool_by_name.get(name)
        cases = {c["id"]: c for c in ((trace.get(t["model"]) if t else None) or {}).get("cases", [])}
        return cases.get(case_id, {})

    opus_calgary, opus_morocco = tcase("Claude Opus 5", "offset:calgary:2026-11-15:12:00"), tcase("Claude Opus 5", "offset:casablanca:2026-12-15:12:00")
    data(opus_calgary.get("correct") is True, "the post says Claude Opus 5 came round to the tool's answer on Calgary's offset; it is graded wrong")
    data(opus_morocco.get("correct") is False and opus_morocco.get("structured_value") == "+01:00", "the post says Claude Opus 5 answered +01:00 on Casablanca in December; the data disagrees")
    lite = tcase("Gemini 3.5 Flash-Lite", "change_day:calgary:2026-11-01")
    expect(r"called the tool <N> times about Calgary's clocks on November 1", lite.get("n_calls", -1))
    data(lite.get("own_place_calls", 0) >= 1 and lite.get("structured_value") is True, "the post says Flash-Lite asked about Calgary on November 1 and still answered that the clocks change; the data disagrees")
    sonnet_van = tcase("Claude Sonnet 5", "offset:vancouver:2026-11-15:12:00")
    data(sonnet_van.get("free_text_value") == "-07:00" and sonnet_van.get("structured_value") == "-08:00", f"the post says Claude Sonnet 5 wrote -07:00 for Vancouver and restated it as -08:00; the trace says {sonnet_van.get('free_text_value')} then {sonnet_van.get('structured_value')}")

    # What the two conditions cost, from the per-request costs in the downloaded runs.
    def run_cost(folder: Path) -> float | None:
        """Cost of the run whose files are in `folder`, provided it answered all 125 questions."""
        runs = list(folder.glob("*.run.json"))
        answers = folder / "world_clock_answers.json"
        if not runs or not answers.exists() or len(json.loads(answers.read_text(encoding="utf-8"))["rows"]) != len(CASES):
            return None
        reqs: list = []
        walk_requests(json.loads(runs[0].read_text(encoding="utf-8")), reqs)
        return sum(int(m.get("inputTokensCostNanodollars", 0) or 0) + int(m.get("outputTokensCostNanodollars", 0) or 0) for m in reqs) / 1e9

    # Gemini 3.8 Flash on all 125 questions: its scored memory run, and its version 4 tool
    # run (the last tool version that asked all 125).
    flash38 = by_name.get("Gemini 3.8 Flash")
    mem_cost = run_cost((ROOT / flash38["source"]).parent) if flash38 else None
    v4_dirs = [p for p in (ROOT / "results" / "raw" / "world-clock-tool-v2" / "4" / "gemini-3.8-flash").glob("*") if p.is_dir()]
    tool_cost = run_cost(v4_dirs[0]) if v4_dirs else None
    if mem_cost is not None and tool_cost is not None:
        require_text(f"Gemini 3.8 Flash cost ${mem_cost:.2f} for the 125 questions from memory and ${tool_cost:.2f} for the same 125 with the tool")
    else:
        print("note: results/raw is not present, so the two cost figures in the post were not re-checked")
    # The daily quota the post names is what analysis/quota.py read from Kaggle's API on
    # 2026-09-30 ($9.9939 used of $10.00). It cannot be re-read offline; the sentence is pinned.
    require_text("a model quota of $10 a day")

    # Tables.
    data(post_table("memory") in text, "POST.md's headline table differs from analysis/render_tables.py post_table(); regenerate it and paste")
    data("| Model | From memory (of" in text and tool_vs_memory() in text, "POST.md's tool table differs from analysis/render_tables.py tool_vs_memory(); run analysis/paste_tables.py")

    # Quotations.
    notes = set()
    for condition in ("memory", "tool"):
        for rows in load_rows(condition).values():
            for r in rows.values():
                if r.get("note"):
                    notes.add(norm(r["note"]))
    # In the tool condition a model also answers in its own words before the SDK asks it to
    # restate the answer in the schema. Those words are in results/tool_trace.json.
    for rep in trace.values():
        for c in rep.get("cases", []):
            if c.get("free_text"):
                notes.add(norm(c["free_text"]))
            if c.get("note"):
                notes.add(norm(c["note"]))
    body = text.split("---", 2)[-1]
    for q in re.findall(r'"([^"\n]{40,})"', body):
        if q == FORMAT_PROMPT:
            continue  # the SDK's own message, quoted from analysis/tool_trace.py, not a model's words
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
