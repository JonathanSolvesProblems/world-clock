"""Render the Kaggle task files from the answer key.

Usage:
    python tasks/render_task.py

Reads `cases/cases.json` and writes one self-contained kaggle-benchmarks task file per
condition into `tasks/`:

    world_clock_memory.py   the model answers from its own knowledge
    world_clock_tool.py     the model may call zone_clock(), a one-function tool that
                            reads tzdata 2026d, and is free not to

The task files embed the cases and the expected answers so the Kaggle kernel needs no
dataset attachment and no network access to grade. The per-release answers used for the
dating ladder stay out of the task file; that analysis runs offline on downloaded results.
"""

from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
CASES = json.loads((HERE.parent / "cases" / "cases.json").read_text(encoding="utf-8"))

# The slug Kaggle sees is the slugified main function name, so `task_name` doubles as the
# function name with hyphens turned into underscores. Slugs `world-clock-memory` and
# `wc-push-probe` exist on Kaggle as broken shells from pushes made before the account was
# phone-verified; they cannot be deleted, so the live tasks use different slugs.
CONDITIONS = {
    "memory": {
        "task_name": "world-clock-from-memory",
        "behaviour": "memory",
        "default_limit": 0,
        "title": "from memory",
        "description": (
            "125 time-zone questions graded against the IANA tz database (tzdata 2026d). "
            "The model answers from its own knowledge, with no tools."
        ),
    },
    "tool": {
        "task_name": "world-clock-with-tzdata-tool",
        "behaviour": "tool",
        "default_limit": 0,
        "title": "with a tzdata tool it may ignore",
        "description": (
            "The same 125 time-zone questions graded against the IANA tz database (tzdata 2026d). "
            "The model may call zone_clock(), which reads tzdata 2026d, and is free not to."
        ),
    },
    "smoke": {
        "task_name": "world-clock-smoke",
        "behaviour": "memory",
        "default_limit": 20,
        "title": "20-case smoke test, from memory",
        "description": (
            "A stratified 20-case subset of the from-memory task, graded against tzdata 2026d. "
            "Used to check the pipeline before spending quota on the full lineup."
        ),
    },
}

TEMPLATE = r'''# %% [markdown]
# # World Clock: __TITLE__
#
# Every model is asked the same 125 questions about local time. Each expected answer was
# computed by Python's `zoneinfo` against the IANA time zone database, release 2026d
# (PyPI `tzdata` 2026.4), by `cases/build_cases.py` in the public repository. No answer in
# the key was typed by a person.
#
# **Condition:** __DESCRIPTION__
#
# Families: `control` (textbook zones), `awkward_offset` (+05:45, +12:45, 30-minute DST),
# `southern` (southern-hemisphere DST), `legislated_2022_2025` (Iran, Jordan, Mexico,
# Greenland, Egypt, Kazakhstan, Paraguay, Chile), `wave_2026` (British Columbia, Alberta,
# Northwest Territories, Morocco stopped changing their clocks in 2026), and `unresolved`
# (Manitoba announced permanent daylight time on 2026-09-17; no tzdata release has it yet,
# so those three cases are recorded and never counted).
#
# Score = correct answers over the 122 graded cases.

# %%
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass

import pandas as pd

import kaggle_benchmarks as kbench
from kaggle_benchmarks.tools import base as tool_base

CONDITION = "__BEHAVIOUR__"
TASK_NAME = "__TASK_NAME__"
TZDATA_PYPI = "2026.4"
TZDATA_IANA = "2026d"
# A stratified subset when non-zero; the smoke task bakes in 20, the real tasks 0 (all).
LIMIT = int(os.environ.get("WORLD_CLOCK_LIMIT", "__DEFAULT_LIMIT__") or 0)
N_JOBS = int(os.environ.get("WORLD_CLOCK_JOBS", "4") or 4)

# %%
CASES = json.loads(r"""__CASES_JSON__""")

# %% [markdown]
# ## The answer schemas
#
# Structured output keeps grading deterministic. The `note` field is the model's one
# sentence about which rule it applied; it is recorded, never graded.

# %%
@dataclass
class OffsetAnswer:
    utc_offset: str  # "+HH:MM" or "-HH:MM"
    note: str  # one sentence naming the rule applied


@dataclass
class ConvertAnswer:
    date: str  # YYYY-MM-DD
    time: str  # HH:MM, 24-hour
    note: str  # one sentence naming the offsets used


@dataclass
class ChangeDayAnswer:
    changes: bool
    direction: str  # "forward", "back" or "none"
    note: str  # one sentence


SCHEMAS = {"offset": OffsetAnswer, "convert": ConvertAnswer, "change_day": ChangeDayAnswer}

FIELD_HINTS = {
    "offset": (
        " Return utc_offset as a string in the form +HH:MM or -HH:MM, and note as one "
        "sentence naming the rule you applied."
    ),
    "convert": (
        " Return date as YYYY-MM-DD, time as HH:MM in 24-hour format, and note as one "
        "sentence naming the UTC offsets you used for each place."
    ),
    "change_day": (
        " Return changes as true or false, direction as exactly one of 'forward', 'back' "
        "or 'none', and note as one sentence."
    ),
}

SYSTEM = (
    "You answer questions about local time, UTC offsets and clock changes. Use your best "
    "knowledge of the rules actually in force on the date asked, including any recent "
    "changes to daylight saving time or time zones. Do not refuse and do not say you "
    "cannot know: give your single best answer and fill every field."
)
if CONDITION == "tool":
    SYSTEM += (
        " A function tool called zone_clock is available. It reads the IANA time zone "
        "database. You may call it if you want to, or answer without it."
    )

# %% [markdown]
# ## The tool (only offered in the `tool` condition)
#
# `zone_clock` reads tzdata 2026d, pinned inside the kernel so the answer does not depend
# on whatever tz database the Kaggle image happens to ship.

# %%
def _pin_tzdata() -> str:
    """Install the exact tzdata release and point zoneinfo at it. Returns the IANA version."""
    import importlib
    import zoneinfo

    try:
        import tzdata

        if getattr(tzdata, "__version__", "") != TZDATA_PYPI:
            raise ImportError("wrong tzdata version")
    except ImportError:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-q", f"tzdata=={TZDATA_PYPI}"],
            check=False,
        )
        import tzdata

        importlib.reload(tzdata)
    root = os.path.join(os.path.dirname(tzdata.__file__), "zoneinfo")
    zoneinfo.reset_tzpath(to=[root])
    zoneinfo.ZoneInfo.clear_cache()
    return tzdata.IANA_VERSION


TZDATA_LOADED = _pin_tzdata() if CONDITION == "tool" else None


def zone_clock(iana_zone: str, local_datetime: str) -> dict:
    """Read the IANA time zone database (tzdata 2026d, released September 2026) for one zone at one local wall-clock time.

    Args:
        iana_zone: An IANA zone key such as 'America/Edmonton', 'Europe/London' or 'Africa/Casablanca'.
        local_datetime: A local wall-clock date and time in ISO 8601 format such as '2026-11-15T09:00'.

    Returns the UTC offset in force at that local time, the zone abbreviation, whether
    daylight saving time is in effect, and the UTC offsets in force at the end of the
    previous day and at the end of that day, which show whether the clocks change during
    that day.
    """
    import zoneinfo
    from datetime import datetime, timedelta

    try:
        tz = zoneinfo.ZoneInfo(iana_zone)
    except Exception:
        return {"error": f"unknown IANA zone key: {iana_zone!r}"}
    try:
        local = datetime.fromisoformat(local_datetime)
    except ValueError:
        return {"error": f"could not parse local_datetime: {local_datetime!r}; use ISO 8601 like 2026-11-15T09:00"}
    local = local.replace(tzinfo=tz)

    def fmt(td: timedelta) -> str:
        total = int(td.total_seconds())
        sign = "+" if total >= 0 else "-"
        total = abs(total)
        return f"{sign}{total // 3600:02d}:{(total % 3600) // 60:02d}"

    day = local.date()
    end_today = datetime(day.year, day.month, day.day, 23, 59, 59, tzinfo=tz, fold=1)
    yday = day - timedelta(days=1)
    end_yesterday = datetime(yday.year, yday.month, yday.day, 23, 59, 59, tzinfo=tz, fold=1)
    return {
        "tzdata_release": TZDATA_LOADED,
        "iana_zone": iana_zone,
        "local_datetime": local.strftime("%Y-%m-%dT%H:%M"),
        "utc_offset": fmt(local.utcoffset()),
        "abbreviation": local.tzname(),
        "is_dst": bool(local.dst()),
        "utc_offset_end_of_previous_day": fmt(end_yesterday.utcoffset()),
        "utc_offset_end_of_this_day": fmt(end_today.utcoffset()),
        "clocks_change_during_this_day": end_yesterday.utcoffset() != end_today.utcoffset(),
    }


# %% [markdown]
# ## Grading
#
# Answers are normalised before comparison so that `UTC-6`, `-6:00` and `−06:00` all read
# as `-06:00`. Nothing else is forgiven: a wrong hour is a wrong hour.

# %%
_OFFSET_RE = re.compile(r"([+\-−–])?\s*(\d{1,2})(?::?(\d{2}))?")


def norm_offset(text) -> str:
    s = str(text).strip().upper().replace("UTC", "").replace("GMT", "").replace("Z", "")
    s = s.replace("−", "-").replace("–", "-").strip()
    m = _OFFSET_RE.search(s)
    if not m:
        return f"unparsed:{text!r}"
    sign = "-" if m.group(1) == "-" else "+"
    hours = int(m.group(2))
    minutes = int(m.group(3) or 0)
    if hours > 14 or minutes > 59:
        return f"unparsed:{text!r}"
    return f"{sign}{hours:02d}:{minutes:02d}"


_TIME_RE = re.compile(r"(\d{1,2}):(\d{2})\s*(AM|PM|A\.M\.|P\.M\.)?", re.IGNORECASE)
_DATE_RE = re.compile(r"(\d{4})-(\d{1,2})-(\d{1,2})")


def norm_time(text) -> str:
    m = _TIME_RE.search(str(text))
    if not m:
        return f"unparsed:{text!r}"
    h, mi = int(m.group(1)), int(m.group(2))
    ampm = (m.group(3) or "").replace(".", "").upper()
    if ampm == "PM" and h < 12:
        h += 12
    if ampm == "AM" and h == 12:
        h = 0
    if h > 23 or mi > 59:
        return f"unparsed:{text!r}"
    return f"{h:02d}:{mi:02d}"


def norm_date(text) -> str:
    m = _DATE_RE.search(str(text))
    if not m:
        return f"unparsed:{text!r}"
    return f"{int(m.group(1)):04d}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"


def norm_direction(text) -> str:
    s = str(text).strip().lower()
    if s.startswith("forw") or "ahead" in s or "spring" in s:
        return "forward"
    if s.startswith("back") or "behind" in s or "fall" in s:
        return "back"
    return "none"


def normalise(kind: str, answer) -> dict:
    if kind == "offset":
        return {"utc_offset": norm_offset(getattr(answer, "utc_offset", answer))}
    if kind == "convert":
        return {"date": norm_date(getattr(answer, "date", "")), "time": norm_time(getattr(answer, "time", ""))}
    changes = bool(getattr(answer, "changes", False))
    direction = norm_direction(getattr(answer, "direction", "none")) if changes else "none"
    return {"changes": changes, "direction": direction}


def count_tool_calls(chat) -> int:
    n = 0
    for item in chat.history:
        if isinstance(item, kbench.chats.Chat):
            n += count_tool_calls(item)
        elif isinstance(getattr(item, "content", None), tool_base.ToolInvocationResult):
            n += 1
    return n


# %% [markdown]
# ## One case

# %%
@kbench.task(name="world_clock_case", store_task=False)
def world_clock_case(llm, id, family, kind, prompt, expected_json, graded) -> dict:
    expected = json.loads(expected_json)
    schema = SCHEMAS[kind]
    full_prompt = prompt + FIELD_HINTS[kind]
    tool_calls = 0
    with kbench.chats.new(f"case {id}", system_instructions=SYSTEM) as chat:
        if CONDITION == "tool":
            answer = llm.prompt(full_prompt, schema=schema, tools=[zone_clock])
            tool_calls = count_tool_calls(chat)
        else:
            answer = llm.prompt(full_prompt, schema=schema)
        usage = getattr(chat, "usage", None)
    got = normalise(kind, answer)
    correct = got == expected
    note = str(getattr(answer, "note", ""))[:400]
    if graded:
        kbench.assertions.assert_true(
            correct,
            expectation=(
                f"[{family}] {prompt} Expected {json.dumps(expected)} per tzdata {TZDATA_IANA}; "
                f"model answered {json.dumps(got)}."
            ),
        )
    return {
        "id": id,
        "family": family,
        "kind": kind,
        "graded": bool(graded),
        "expected": expected,
        "answer": got,
        "correct": bool(correct),
        "note": note,
        "tool_calls": tool_calls,
        "input_tokens": getattr(usage, "input_tokens", None),
        "output_tokens": getattr(usage, "output_tokens", None),
        "latency_ms": getattr(usage, "total_backend_latency_ms", None),
    }


# %% [markdown]
# ## The benchmark

# %%
def select_cases(cases: list[dict], limit: int) -> list[dict]:
    """Stratified round-robin over families so a smoke test touches every bucket."""
    if not limit or limit >= len(cases):
        return cases
    by_family: dict[str, list[dict]] = {}
    for c in cases:
        by_family.setdefault(c["family"], []).append(c)
    picked: list[dict] = []
    while len(picked) < limit:
        progressed = False
        for fam in by_family:
            if by_family[fam] and len(picked) < limit:
                picked.append(by_family[fam].pop(0))
                progressed = True
        if not progressed:
            break
    return picked


def cases_frame() -> pd.DataFrame:
    rows = []
    for c in select_cases(CASES, LIMIT):
        rows.append(
            {
                "id": c["id"],
                "family": c["family"],
                "kind": c["kind"],
                "prompt": c["prompt"],
                "expected_json": json.dumps(c["expected"], sort_keys=True),
                "graded": bool(c["graded"]),
            }
        )
    return pd.DataFrame(rows)


@kbench.task(
    name=TASK_NAME,
    description="__DESCRIPTION__",
)
def __FUNC_NAME__(llm) -> tuple[int, int]:
    df = cases_frame()
    with kbench.client.enable_cache():
        results = world_clock_case.evaluate(
            llm=[llm],
            evaluation_data=df,
            n_jobs=N_JOBS,
            timeout=240,
            on_failure="continue",
            max_attempts=2,
            retry_delay=10,
            remove_run_files=True,
        )
    completed = results.completed_runs
    rows = [r.result for r in completed]
    errored = [{"params": {k: v for k, v in r.params.items() if k != "llm"}, "error": str(getattr(r, "error_message", ""))[:300]} for r in results.errored_runs]

    graded_rows = [r for r in rows if r["graded"]]
    correct = sum(1 for r in graded_rows if r["correct"])
    total = len(graded_rows)

    by_family: dict[str, list[int]] = {}
    for r in graded_rows:
        by_family.setdefault(r["family"], []).append(int(r["correct"]))
    summary = {fam: {"correct": sum(v), "total": len(v)} for fam, v in by_family.items()}

    out = {
        "task": TASK_NAME,
        "condition": CONDITION,
        "tzdata_release": TZDATA_IANA,
        "model": getattr(llm, "model", None) or getattr(llm, "name", str(llm)),
        "graded_correct": correct,
        "graded_total": total,
        "errored": errored,
        "by_family": summary,
        "rows": rows,
    }
    with open("world_clock_answers.json", "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    print(f"{TASK_NAME}: {correct}/{total} graded cases correct; {len(errored)} errored")
    for fam, s in summary.items():
        print(f"  {fam:22s} {s['correct']:3d}/{s['total']}")
    print("WORLD_CLOCK_ANSWERS_JSON " + json.dumps(out, ensure_ascii=True))
    return correct, total


# %%
run = __FUNC_NAME__.run(kbench.llm)
run
'''


def render(condition: str) -> Path:
    meta = CONDITIONS[condition]
    slim = [
        {
            "id": c["id"],
            "family": c["family"],
            "kind": c["kind"],
            "prompt": c["prompt"],
            "expected": c["expected"],
            "graded": c["graded"],
        }
        for c in CASES
    ]
    cases_json = json.dumps(slim, ensure_ascii=True, separators=(",", ":"))
    assert '"""' not in cases_json
    text = (
        TEMPLATE.replace("__CASES_JSON__", cases_json)
        .replace("__BEHAVIOUR__", meta["behaviour"])
        .replace("__DEFAULT_LIMIT__", str(meta["default_limit"]))
        .replace("__TASK_NAME__", meta["task_name"])
        # The CLI matches the push slug against the slugified function name.
        .replace("__FUNC_NAME__", meta["task_name"].replace("-", "_"))
        .replace("__TITLE__", meta["title"])
        .replace("__DESCRIPTION__", meta["description"])
    )
    out = HERE / f"world_clock_{condition}.py"
    out.write_text(text, encoding="utf-8", newline="\n")
    return out


if __name__ == "__main__":
    for cond in CONDITIONS:
        path = render(cond)
        print(f"wrote {path.relative_to(HERE.parent)} ({path.stat().st_size} bytes)")
