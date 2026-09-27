"""The dating ladder must recover a known clock.

A synthetic model that answers every case exactly as tzdata 2024a would must be dated to
2024a (tied with any later release that gives the same answers on the ladder cases, which
here is none, because 2025a changed Paraguay). A model that answers as 2026d must read as
current. A model that answers as 2022a must be dated to 2022a.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "analysis"))

import date_the_clock as dtc  # noqa: E402

CASES = json.loads((ROOT / "cases" / "cases.json").read_text(encoding="utf-8"))


def synthetic_answers(release: str, tmp_path: Path, condition: str = "memory") -> Path:
    rows = []
    for c in CASES:
        ans = c["by_release"][release]
        rows.append(
            {
                "id": c["id"],
                "family": c["family"],
                "kind": c["kind"],
                "graded": c["graded"],
                "expected": c["expected"],
                "answer": ans,
                "correct": ans == c["expected"],
                "note": "",
                "tool_calls": 0,
            }
        )
    out = tmp_path / f"model-{release}" / "world_clock_answers.json"
    out.parent.mkdir(parents=True)
    out.write_text(json.dumps({"model": f"synthetic-{release}", "condition": condition, "rows": rows}))
    return out


def test_2024a_clock_is_dated_2024a(tmp_path):
    result = dtc.score_file(synthetic_answers("2024.1", tmp_path))
    clock = result["clock"]
    assert clock["earliest"]["iana"] == "2024a"
    # 2024b changed no future timestamps in our cases, so it ties.
    assert clock["latest"]["iana"] in ("2024a", "2024b")
    assert clock["current"] is False
    assert result["graded_total"] == 122


def test_2026d_clock_is_current(tmp_path):
    result = dtc.score_file(synthetic_answers("2026.4", tmp_path))
    clock = result["clock"]
    assert clock["current"] is True
    assert clock["earliest"]["iana"] == "2026d"
    assert result["graded_correct"] == result["graded_total"]


def test_2022a_clock_is_dated_2022a(tmp_path):
    result = dtc.score_file(synthetic_answers("2022.1", tmp_path))
    clock = result["clock"]
    assert clock["earliest"]["iana"] == "2022a"
    assert clock["latest"]["iana"] == "2022a"
    # A 2022a clock gets every 2026 case wrong.
    fam = result["per_family"]["wave_2026"]
    assert fam["correct"] < fam["total"]


def test_unresolved_cases_are_reported_not_graded(tmp_path):
    result = dtc.score_file(synthetic_answers("2026.4", tmp_path))
    ids = {u["id"] for u in result["unresolved"]}
    assert ids == {
        "offset:winnipeg:2026-11-15:12:00",
        "change_day:winnipeg:2026-11-01",
        "convert:winnipeg:toronto:2026-11-15:09:00",
    }
    for u in result["unresolved"]:
        assert u["official"] is not None
