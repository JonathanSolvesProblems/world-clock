"""The answer schemas accept what the model actually sends.

Qwen3-Next returned `{" time": "11:00", ...}` with a stray space in the key, the SDK called
`ConvertAnswer(**value)` with it, and three cases died on a TypeError instead of being
graded. The schemas now clean their keys and fill missing fields, so the SDK's own parser
returns an answer for anything that is valid JSON. These tests drive the SDK's dataclass
handler exactly as the benchmark does.
"""

from __future__ import annotations

import json
from pathlib import Path

TASK_FILE = Path(__file__).resolve().parent.parent / "tasks" / "world_clock_memory.py"


def load_schema_namespace() -> dict:
    text = TASK_FILE.read_text(encoding="utf-8")
    start = text.index("# ## The answer schemas")
    end = text.index("\nSCHEMAS = ", start)
    end = text.index("\n", end + 1)  # keep the SCHEMAS line itself
    cell = text[start:end]
    code = "\n".join(line for line in cell.splitlines() if not line.startswith("# "))
    code = code.replace("# %%", "")
    ns: dict = {}
    exec("from dataclasses import dataclass\n" + code, ns)
    return ns


NS = load_schema_namespace()


def parse_with_sdk(cls, response: str):
    """Run the SDK's dataclass handler: it yields the schema prompt, then parses a response."""
    from kaggle_benchmarks.prompting import root_model_handler

    gen = root_model_handler(cls)
    next(gen)
    try:
        gen.send(response)
    except StopIteration as stop:
        return stop.value
    raise AssertionError("handler did not return a value")


def test_stray_space_in_key_is_accepted():
    answer = parse_with_sdk(NS["ConvertAnswer"], json.dumps({"date": "2026-11-15", " time": "11:00", "note": "x"}))
    assert answer.date == "2026-11-15"
    assert answer.time == "11:00"
    assert answer.note == "x"


def test_missing_field_becomes_empty_and_grades_wrong():
    answer = parse_with_sdk(NS["OffsetAnswer"], json.dumps({"note": "no offset given"}))
    assert answer.utc_offset == ""
    answer = parse_with_sdk(NS["ChangeDayAnswer"], json.dumps({"direction": "back", "note": "x"}))
    assert answer.changes is False
    assert answer.direction == "back"


def test_unknown_keys_are_dropped_and_case_is_ignored():
    answer = parse_with_sdk(NS["OffsetAnswer"], json.dumps({"UTC_Offset": "-06:00", "Note": "x", "extra": 1}))
    assert answer.utc_offset == "-06:00"
    assert answer.note == "x"
    assert not hasattr(answer, "extra")


def test_sdk_schema_still_lists_every_field():
    from kaggle_benchmarks.prompting import root_model_handler

    gen = root_model_handler(NS["ConvertAnswer"])
    prompt, model_cls = next(gen)
    for name in ("date", "time", "note"):
        assert name in prompt
        assert name in model_cls.model_fields
