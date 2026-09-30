"""Draw the post's cover image: the one question, the answer every model gave, the right one.

Usage:
    python analysis/make_cover.py [--out results/cover.png]

1000 x 420 (DEV's cover ratio), rendered at 2x. The count on the card is read from the
downloaded runs, not typed: how many models answered the Calgary to Toronto question, and
how many of them said 11:00. If the two differ the script refuses to draw a card that
says "N of N".
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from date_the_clock import find_answer_files  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
CASE = "convert:calgary:toronto:2026-11-15:09:00"

SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK2 = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
BLUE = "#2a78d6"
ORANGE = "#eb6834"


def counts() -> tuple[int, int]:
    answered = said_eleven = 0
    for p in find_answer_files(ROOT / "results" / "raw"):
        d = json.loads(p.read_text(encoding="utf-8"))
        if d.get("condition") != "memory" or "smoke" in d.get("task", "") or not d.get("graded_total"):
            continue
        row = next((r for r in d["rows"] if r["id"] == CASE), None)
        if row is None:
            continue
        answered += 1
        said_eleven += int((row.get("answer") or {}).get("time") == "11:00")
    return answered, said_eleven


def main() -> int:
    out = ROOT / "results" / "cover.png"
    if "--out" in sys.argv:
        out = Path(sys.argv[sys.argv.index("--out") + 1])
    answered, said_eleven = counts()
    if not answered or answered != said_eleven:
        print(f"not drawing: {said_eleven} of {answered} models said 11:00, the card needs all of them")
        return 1

    plt.rcParams["font.family"] = ["Segoe UI", "DejaVu Sans", "sans-serif"]
    fig = plt.figure(figsize=(10, 4.2), dpi=200)
    fig.patch.set_facecolor(SURFACE)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor(SURFACE)
    ax.set_xlim(0, 1000)
    ax.set_ylim(0, 420)
    ax.axis("off")

    ax.text(60, 362, "It is 09:00 in Calgary on November 15, 2026.", fontsize=17, color=INK, va="center")
    ax.text(60, 326, "What time is it in Toronto?", fontsize=17, color=INK, va="center")

    # Left: what the models said, struck through.
    ax.text(60, 205, "11:00", fontsize=78, color=MUTED, va="center", fontweight="bold")
    ax.plot([52, 372], [203, 203], color=ORANGE, linewidth=5, solid_capstyle="round")
    ax.text(62, 118, f"{said_eleven} of {answered} models", fontsize=15, color=INK, va="center", fontweight="bold")
    ax.text(62, 90, "asked from memory on Kaggle Benchmarks", fontsize=11.5, color=INK2, va="center")

    # Divider.
    ax.plot([500, 500], [80, 270], color=GRID, linewidth=1.5)

    # Right: what the database says.
    ax.text(560, 205, "10:00", fontsize=78, color=INK, va="center", fontweight="bold")
    ax.plot([562, 872], [142, 142], color=BLUE, linewidth=5, solid_capstyle="round")
    ax.text(562, 118, "the IANA tz database, release 2026d", fontsize=15, color=INK, va="center", fontweight="bold")
    ax.text(562, 90, "Alberta stopped changing its clocks on June 18", fontsize=11.5, color=INK2, va="center")

    ax.text(60, 34, "World Clock: a benchmark that dates each model's knowledge of the world's clocks", fontsize=10.5, color=MUTED, va="center")

    out.parent.mkdir(exist_ok=True)
    fig.savefig(out, facecolor=SURFACE)
    print(f"wrote {out} ({said_eleven} of {answered})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
