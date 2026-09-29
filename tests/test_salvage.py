"""The parse-failure salvage must recover a DeepSeek-style answer and refuse a truncated one."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

TASK_FILE = Path(__file__).resolve().parent.parent / "tasks" / "world_clock_memory.py"


def load_salvage():
    text = TASK_FILE.read_text(encoding="utf-8")
    start = text.index("def salvage(")
    end = text.index("def ask(")
    ns: dict = {"json": json, "re": re}
    exec(text[start:end], ns)
    return ns["salvage"]


salvage = load_salvage()


@dataclass
class ConvertAnswer:
    date: str
    time: str
    note: str


@dataclass
class OffsetAnswer:
    utc_offset: str
    note: str


DEEPSEEK_MESSAGE = """Response parsing failed.
Input Value:
---
<think>
 Let me check the rules. The answer is {"date": "wrong"} no wait.
 Let's output that.
</think>
{
  "date": "2026-07-15",
  "time": "14:00",
  "note": "New York observes UTC-4 (EDT) and London observes UTC+1 (BST) during this period."
}
---
Target Schema:
---
{"properties": {"date": {"type": "string"}}}
---
Parsing Error:
---
Invalid JSON Expecting value: line 1 column 1 (char 0)
---
"""

TRUNCATED_MESSAGE = """Response parsing failed.
Input Value:
---


{"utc_offset": "+12:45", "note": "Chatham Islands observe standard time (UTC+12:45) from the first Sunday in April to the last Sunday inSeptember, and
---
Target Schema:
---
{"properties": {}}
---
Parsing Error:
---
Invalid JSON Unterminated string starting at: line 3 column 34 (char 35)
---
"""


def test_salvages_json_after_think_block():
    got = salvage(ConvertAnswer, DEEPSEEK_MESSAGE)
    assert got is not None
    assert got.date == "2026-07-15"
    assert got.time == "14:00"
    assert got.note.startswith("New York observes")


def test_ignores_json_inside_the_think_block_when_a_real_answer_follows():
    got = salvage(ConvertAnswer, DEEPSEEK_MESSAGE)
    assert got.date != "wrong"


def test_refuses_truncated_json():
    assert salvage(OffsetAnswer, TRUNCATED_MESSAGE) is None


def test_drops_unknown_fields():
    msg = 'Response parsing failed.\nInput Value:\n---\n{"utc_offset": "-06:00", "note": "x", "extra": 1}\n---\nTarget Schema:\n---\n{}\n---'
    got = salvage(OffsetAnswer, msg)
    assert got is not None and got.utc_offset == "-06:00"
