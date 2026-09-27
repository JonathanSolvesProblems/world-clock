"""Build the World Clock case set and its answer key from the IANA database.

Usage:
    python cases/build_cases.py

Reads `cases/specs.py`, computes every expected answer with `zoneinfo` under each tzdata
release unpacked in `tzhist/releases/`, and writes:

    cases/cases.json      one record per case: prompt, family, kind, expected answer under
                          the grading release, and the answer under every release since 2022
    cases/answer_key.csv  the same, flat, for eyeballing
    cases/ladder.csv      only the cases whose answer differs between releases, which are the
                          rungs of the dating ladder

No answer in these files is typed by a person. If a spec asks about a place on a date,
the database says what the clock did.
"""

from __future__ import annotations

import csv
import json
import sys
import zoneinfo
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from specs import OFFICIAL_ANSWERS, PLACES, SPECS  # noqa: E402

RELEASES_DIR = HERE.parent / "tzhist" / "releases"
GRADING_RELEASE = "2026.4"  # PyPI tzdata version; IANA 2026d


def release_dirs() -> list[tuple[str, Path]]:
    index = json.loads((RELEASES_DIR / "index.json").read_text())
    out = []
    for version in sorted(index, key=lambda v: tuple(int(x) for x in v.split("."))):
        out.append((version, RELEASES_DIR / version / "zoneinfo"))
    return out


def iana_name(version: str) -> str:
    index = json.loads((RELEASES_DIR / "index.json").read_text())
    return index[version]["iana"]


class ReleaseClock:
    """Answers questions about one tzdata release, and only that release.

    zoneinfo falls back to the installed tzdata package when a key is missing from
    TZPATH, which would quietly leak the current database into an old release's answers.
    So every key is checked on disk first, and a missing key uses the place's declared
    fallback zone, which is where that place actually lived before it got its own zone.
    """

    def __init__(self, version: str, path: Path):
        self.version = version
        self.path = path
        zoneinfo.reset_tzpath(to=[str(path)])
        zoneinfo.ZoneInfo.clear_cache()

    def zone(self, place: str) -> zoneinfo.ZoneInfo:
        _, key, fallback = PLACES[place]
        if (self.path / key).exists():
            return zoneinfo.ZoneInfo(key)
        if fallback and (self.path / fallback).exists():
            return zoneinfo.ZoneInfo(fallback)
        raise KeyError(f"{key} missing from tzdata {self.version} and no fallback")

    @staticmethod
    def fmt_offset(td: timedelta) -> str:
        total = int(td.total_seconds())
        sign = "+" if total >= 0 else "-"
        total = abs(total)
        return f"{sign}{total // 3600:02d}:{(total % 3600) // 60:02d}"

    def offset(self, place: str, date: str, time: str) -> dict:
        tz = self.zone(place)
        local = datetime.fromisoformat(f"{date}T{time}").replace(tzinfo=tz)
        return {"utc_offset": self.fmt_offset(local.utcoffset())}

    def convert(self, src: str, dst: str, date: str, time: str) -> dict:
        local = datetime.fromisoformat(f"{date}T{time}").replace(tzinfo=self.zone(src))
        target = local.astimezone(self.zone(dst))
        return {"date": target.strftime("%Y-%m-%d"), "time": target.strftime("%H:%M")}

    def _end_of_day_offset(self, tz: zoneinfo.ZoneInfo, day) -> timedelta:
        """UTC offset in force at the last second of a local calendar day.

        fold=1 picks the later of two ambiguous wall times, which is the offset that
        is actually in force when the day ends.
        """
        end = datetime(day.year, day.month, day.day, 23, 59, 59, tzinfo=tz, fold=1)
        return end.utcoffset()

    def change_day(self, place: str, date: str) -> dict:
        """Do the clocks change during this local calendar day?

        Defined as: the offset in force at the end of the day differs from the offset in
        force at the end of the previous day. Specs avoid transitions that sit exactly on
        a midnight fall-back, where people disagree about which day the change belongs to.
        """
        tz = self.zone(place)
        day = datetime.fromisoformat(date).date()
        before = self._end_of_day_offset(tz, day - timedelta(days=1))
        after = self._end_of_day_offset(tz, day)
        if before == after:
            return {"changes": False, "direction": "none"}
        direction = "forward" if after > before else "back"
        return {"changes": True, "direction": direction}


def prompt_for(kind: str, payload: tuple) -> str:
    if kind == "offset":
        place, date, time = payload
        name = PLACES[place][0]
        return (
            f"What is the UTC offset in effect in {name} at {time} local time on {date}? "
            "Answer with the offset in the form +HH:MM or -HH:MM."
        )
    if kind == "convert":
        src, dst, date, time = payload
        return (
            f"It is {time} on {date} in {PLACES[src][0]}. "
            f"What is the local date and time at that same moment in {PLACES[dst][0]}? "
            "Give the date as YYYY-MM-DD and the time as HH:MM in 24-hour format."
        )
    if kind == "change_day":
        place, date = payload
        return (
            f"Do the clocks in {PLACES[place][0]} change at any point during the local "
            f"calendar day of {date}, either springing forward or falling back? "
            "Answer whether they change and, if so, in which direction."
        )
    raise ValueError(kind)


def compute(clock: ReleaseClock, kind: str, payload: tuple) -> dict:
    if kind == "offset":
        return clock.offset(*payload)
    if kind == "convert":
        return clock.convert(*payload)
    if kind == "change_day":
        return clock.change_day(*payload)
    raise ValueError(kind)


def case_id(kind: str, payload: tuple) -> str:
    return f"{kind}:" + ":".join(str(p) for p in payload)


def main() -> None:
    releases = release_dirs()
    versions = [v for v, _ in releases]
    if GRADING_RELEASE not in versions:
        raise SystemExit(f"grading release {GRADING_RELEASE} not unpacked; run tzhist/fetch_releases.py")

    # answers[case_id][version] = dict
    answers: dict[str, dict[str, dict]] = {case_id(k, p): {} for _, k, p in SPECS}
    for version, path in releases:
        clock = ReleaseClock(version, path)
        for family, kind, payload in SPECS:
            answers[case_id(kind, payload)][version] = compute(clock, kind, payload)

    cases = []
    for family, kind, payload in SPECS:
        cid = case_id(kind, payload)
        by_release = answers[cid]
        expected = by_release[GRADING_RELEASE]
        distinct = {json.dumps(v, sort_keys=True) for v in by_release.values()}
        record = {
            "id": cid,
            "family": family,
            "kind": kind,
            "places": [PLACES[p][0] for p in payload if isinstance(p, str) and p in PLACES],
            "zones": [PLACES[p][1] for p in payload if isinstance(p, str) and p in PLACES],
            "prompt": prompt_for(kind, payload),
            "expected": expected,
            "graded": family != "unresolved",
            "discriminates": len(distinct) > 1,
            "by_release": by_release,
            "grading_release": {"pypi": GRADING_RELEASE, "iana": iana_name(GRADING_RELEASE)},
        }
        official = OFFICIAL_ANSWERS.get((kind, payload))
        if official is not None:
            record["official_answer"] = official
        cases.append(record)

    (HERE / "cases.json").write_text(json.dumps(cases, indent=2, ensure_ascii=False), encoding="utf-8")

    with (HERE / "answer_key.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["id", "family", "kind", "graded", "discriminates", "expected"] + [f"tz{v}" for v in versions])
        for c in cases:
            w.writerow(
                [c["id"], c["family"], c["kind"], c["graded"], c["discriminates"], json.dumps(c["expected"])]
                + [json.dumps(c["by_release"][v]) for v in versions]
            )

    with (HERE / "ladder.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["id", "family", "first_release_with_current_answer", "expected", "earliest_answer"])
        for c in cases:
            if not c["discriminates"]:
                continue
            current = json.dumps(c["expected"], sort_keys=True)
            first = next(v for v in versions if json.dumps(c["by_release"][v], sort_keys=True) == current
                         and all(json.dumps(c["by_release"][u], sort_keys=True) == current
                                 for u in versions[versions.index(v):]))
            w.writerow([c["id"], c["family"], f"{first} ({iana_name(first)})",
                        json.dumps(c["expected"]), json.dumps(c["by_release"][versions[0]])])

    n = len(cases)
    graded = sum(c["graded"] for c in cases)
    disc = sum(c["discriminates"] for c in cases)
    print(f"{n} cases, {graded} graded, {disc} discriminate between releases")
    by_family: dict[str, int] = {}
    for c in cases:
        by_family[c["family"]] = by_family.get(c["family"], 0) + 1
    for fam, count in by_family.items():
        print(f"  {fam:22s} {count}")


if __name__ == "__main__":
    main()
