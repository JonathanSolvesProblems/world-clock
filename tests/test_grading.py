"""Unit tests for the grading normalisers inside the rendered task file.

The task file is a notebook-style script that runs on import, so the grading cell is
extracted by its markdown headers and executed on its own. This keeps the template as the
single source of truth for how an answer is read.
"""

from __future__ import annotations

import re
from pathlib import Path
from types import SimpleNamespace

TASK_FILE = Path(__file__).resolve().parent.parent / "tasks" / "world_clock_memory.py"


def load_grading_namespace() -> dict:
    text = TASK_FILE.read_text(encoding="utf-8")
    start = text.index("# ## Grading")
    end = text.index("# ## One case")
    cell = text[start:end]
    # drop the markdown comment lines and the cell marker
    code = "\n".join(line for line in cell.splitlines() if not line.startswith("# "))
    code = code.replace("# %%", "")
    ns: dict = {"re": re}
    exec("import re\nimport kaggle_benchmarks as kbench\nfrom kaggle_benchmarks.tools import base as tool_base\n" + code, ns)
    return ns


NS = load_grading_namespace()


def test_offset_forms_collapse():
    f = NS["norm_offset"]
    for raw in ["-06:00", "-6:00", "UTC-6", "GMT-06", "−06:00", " -06 ", "-0600"]:
        assert f(raw) == "-06:00", raw
    assert f("+05:45") == "+05:45"
    assert f("UTC+5:45") == "+05:45"
    assert f("+00:00") == "+00:00"
    assert f("UTC") .startswith("unparsed") or f("UTC") == "+00:00"


def test_offset_rejects_garbage():
    f = NS["norm_offset"]
    assert f("noon").startswith("unparsed")
    assert f("+25:00").startswith("unparsed")


def test_time_and_date():
    assert NS["norm_time"]("9:00") == "09:00"
    assert NS["norm_time"]("09:00") == "09:00"
    assert NS["norm_time"]("9:00 PM") == "21:00"
    assert NS["norm_time"]("12:15 AM") == "00:15"
    assert NS["norm_time"]("late") .startswith("unparsed")
    assert NS["norm_date"]("2026-11-15") == "2026-11-15"
    assert NS["norm_date"]("2026-1-5") == "2026-01-05"


def test_direction():
    f = NS["norm_direction"]
    assert f("forward") == "forward"
    assert f("Forwards (spring forward)") == "forward"
    assert f("back") == "back"
    assert f("backward") == "back"
    assert f("fall back") == "back"
    assert f("none") == "none"
    assert f("") == "none"


def test_normalise_change_day_forces_none_when_no_change():
    norm = NS["normalise"]
    got = norm("change_day", SimpleNamespace(changes=False, direction="back", note=""))
    assert got == {"changes": False, "direction": "none"}
    got = norm("change_day", SimpleNamespace(changes=True, direction="Backward", note=""))
    assert got == {"changes": True, "direction": "back"}


def test_normalise_convert_and_offset():
    norm = NS["normalise"]
    assert norm("convert", SimpleNamespace(date="2026-11-15", time="10:00", note="")) == {
        "date": "2026-11-15",
        "time": "10:00",
    }
    assert norm("offset", SimpleNamespace(utc_offset="UTC-7", note="")) == {"utc_offset": "-07:00"}
