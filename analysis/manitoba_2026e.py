"""Grade the three Manitoba questions against tzdata 2026e.

Usage:
    python analysis/manitoba_2026e.py

The benchmark's answer key is tzdata 2026d, the release Kaggle graded against. Manitoba
announced permanent daylight time on 2026-09-17, after 2026d, so its three questions were
asked and recorded but never counted. tzdata 2026e (released 2026-09-30, PyPI tzdata
2026.5) added Manitoba: "Manitoba moves to permanent -05 on 2026-10-31". This script
downloads 2026e into tzhist/after/ (outside the dating ladder, which stays at the twenty
releases 2022a to 2026d), computes the three answers with the same code the answer key
uses, and scores every model's recorded answers against them. Writes results/manitoba_2026e.json.
"""

from __future__ import annotations

import json
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "analysis"))
from cases.build_cases import ReleaseClock  # noqa: E402
from date_the_clock import canon, find_answer_files  # noqa: E402
from render_tables import display  # noqa: E402

AFTER = ROOT / "tzhist" / "after"
VERSION = "2026.5"
CASE_ARGS = {
    "offset:winnipeg:2026-11-15:12:00": ("offset", ("winnipeg", "2026-11-15", "12:00")),
    "change_day:winnipeg:2026-11-01": ("change_day", ("winnipeg", "2026-11-01")),
    "convert:winnipeg:toronto:2026-11-15:09:00": ("convert", ("winnipeg", "toronto", "2026-11-15", "09:00")),
}


def release_dir() -> Path:
    dest = AFTER / VERSION
    if (dest / "zoneinfo" / "America" / "Winnipeg").exists():
        return dest
    wheels = AFTER / "wheels"
    wheels.mkdir(parents=True, exist_ok=True)
    if not list(wheels.glob(f"tzdata-{VERSION}-*.whl")):
        # The project venv has no pip; run this download with the system Python if it fails.
        subprocess.run([sys.executable, "-m", "pip", "download", f"tzdata=={VERSION}", "--no-deps", "--only-binary=:all:", "-d", str(wheels), "--quiet"], check=True)  # noqa: E501
    wheel = next(wheels.glob(f"tzdata-{VERSION}-*.whl"))
    with zipfile.ZipFile(wheel) as zf:
        init = [m for m in zf.namelist() if m.endswith("tzdata/__init__.py")][0]
        assert "2026e" in zf.read(init).decode(), "PyPI tzdata 2026.5 is not IANA 2026e"
        for m in zf.namelist():
            if m.startswith("tzdata/zoneinfo/") and not m.endswith("/"):
                out = dest / m[len("tzdata/"):]
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_bytes(zf.read(m))
    return dest


def main() -> dict:
    clock = ReleaseClock("2026e", release_dir() / "zoneinfo")
    truth = {}
    for cid, (kind, args) in CASE_ARGS.items():
        truth[cid] = getattr(clock, kind)(*args)
    models = {}
    for p in find_answer_files(ROOT / "results" / "raw"):
        d = json.loads(p.read_text(encoding="utf-8"))
        if d.get("condition") != "memory" or not d.get("graded_total"):
            continue
        rows = {r["id"]: r for r in d["rows"]}
        models[display(d["model"])] = {
            cid: {"answer": rows[cid]["answer"], "right_under_2026e": canon(rows[cid]["answer"]) == canon(truth[cid])}
            for cid in CASE_ARGS if cid in rows
        }
    out = {
        "tzdata": "2026e",
        "released": "2026-09-30",
        "truth": truth,
        "models": models,
        "n_models": len(models),
        "right_count": {cid: sum(1 for m in models.values() if m.get(cid, {}).get("right_under_2026e")) for cid in CASE_ARGS},
    }
    (ROOT / "results" / "manitoba_2026e.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    return out


if __name__ == "__main__":
    r = main()
    print("tzdata 2026e says:", json.dumps(r["truth"]))
    for cid, n in r["right_count"].items():
        print(f"  {cid}: {n} of {r['n_models']} right under 2026e")
    for name, m in r["models"].items():
        ok = [cid.split(":")[0] for cid, v in m.items() if v["right_under_2026e"]]
        if ok:
            print(f"  {name} right on: {ok}")
