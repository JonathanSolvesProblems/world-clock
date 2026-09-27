"""Download every tzdata wheel from PyPI since 2022 and unpack its zoneinfo tree.

Each release becomes a directory `tzhist/releases/<version>/zoneinfo/...` that
`zoneinfo.ZoneInfo` can be pointed at with `zoneinfo.reset_tzpath`. This is the
answer key for the dating metric: a model that agrees with tzdata 2024.1 more than
with 2026.4 has a world clock from early 2024.

The PyPI version maps to an IANA release: 2026.4 is tzdata 2026d, 2024.1 is 2024a,
and so on. The mapping is recorded in `releases/index.json` from the wheel metadata.
"""

from __future__ import annotations

import json
import subprocess
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
WHEELS = HERE / "wheels"
RELEASES = HERE / "releases"

VERSIONS = [
    "2022.1", "2022.2", "2022.3", "2022.4", "2022.5", "2022.6", "2022.7",
    "2023.1", "2023.2", "2023.3", "2023.4",
    "2024.1", "2024.2",
    "2025.1", "2025.2", "2025.3",
    "2026.1", "2026.2", "2026.3", "2026.4",
]


def download(version: str) -> Path:
    target = WHEELS / version
    target.mkdir(parents=True, exist_ok=True)
    existing = list(target.glob("tzdata-*.whl"))
    if existing:
        return existing[0]
    subprocess.run(
        [sys.executable, "-m", "pip", "download", f"tzdata=={version}",
         "--no-deps", "--only-binary=:all:", "-d", str(target), "--quiet"],
        check=True,
    )
    return next(target.glob("tzdata-*.whl"))


def unpack(version: str, wheel: Path) -> str:
    dest = RELEASES / version
    iana = None
    with zipfile.ZipFile(wheel) as zf:
        for member in zf.namelist():
            if member.startswith("tzdata/zoneinfo/"):
                rel = member[len("tzdata/"):]
                out = dest / rel
                if member.endswith("/"):
                    out.mkdir(parents=True, exist_ok=True)
                    continue
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_bytes(zf.read(member))
        # tzdata.IANA_VERSION lives in tzdata/__init__.py
        init = [m for m in zf.namelist() if m.endswith("tzdata/__init__.py")]
        if init:
            text = zf.read(init[0]).decode()
            for line in text.splitlines():
                if line.startswith("IANA_VERSION"):
                    iana = line.split("=", 1)[1].strip().strip("'\"")
    return iana or "unknown"


def main() -> None:
    index = {}
    for version in VERSIONS:
        wheel = download(version)
        iana = unpack(version, wheel)
        index[version] = {"iana": iana, "wheel": wheel.name}
        print(f"{version:8s} -> IANA {iana}")
    (RELEASES / "index.json").write_text(json.dumps(index, indent=2))


if __name__ == "__main__":
    main()
