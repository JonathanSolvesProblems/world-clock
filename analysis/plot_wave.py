"""Draw the 2026-wave scores: from memory beside with-the-tool, one row per model.

Usage:
    python analysis/plot_wave.py [--out results/wave.png]

Reads results/summary.json. The 2026 wave is the 25 graded questions about British
Columbia, Alberta, the Northwest Territories and Morocco after their 2026 changes. Two bars
per model: answers from memory (slot 1) and answers with the tzdata tool available (slot
2). Models sorted by their from-memory score. Text stays in ink tokens; colour is on the
bars only; a legend is present because there are two series.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SUMMARY = json.loads((ROOT / "results" / "summary.json").read_text(encoding="utf-8"))

SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK2 = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
AXIS = "#c3c2b7"
MEMORY = "#2a78d6"
TOOL = "#eb6834"


def short(model: str) -> str:
    return model.split("/")[-1].split("@")[0]


def main() -> None:
    out = ROOT / "results" / "wave.png"
    if "--out" in sys.argv:
        out = Path(sys.argv[sys.argv.index("--out") + 1])

    mem = {short(r["model"]): r for r in SUMMARY if r["condition"] == "memory" and r["graded_total"]}
    tool = {short(r["model"]): r for r in SUMMARY if r["condition"] == "tool" and r["graded_total"]}
    names = sorted(mem, key=lambda n: (mem[n]["per_family"].get("wave_2026", {}).get("correct", 0), n))
    if not names:
        raise SystemExit("nothing to plot")
    total = max(r["per_family"].get("wave_2026", {}).get("total", 25) for r in mem.values())

    plt.rcParams["font.family"] = ["Segoe UI", "DejaVu Sans", "sans-serif"]
    height = 0.9 + 0.42 * len(names)
    fig, ax = plt.subplots(figsize=(8.4, height), dpi=200)
    fig.patch.set_facecolor(SURFACE)
    ax.set_facecolor(SURFACE)

    bar_h = 0.34
    gap = 0.04  # surface gap between the two bars of one model
    for i, name in enumerate(names):
        m = mem[name]["per_family"].get("wave_2026", {}).get("correct", 0)
        ax.barh(i + (bar_h + gap) / 2, m, height=bar_h, color=MEMORY, zorder=3)
        ax.text(m + 0.3, i + (bar_h + gap) / 2, str(m), va="center", ha="left", fontsize=7.5, color=INK2)
        if name in tool:
            t = tool[name]["per_family"].get("wave_2026", {}).get("correct", 0)
            ax.barh(i - (bar_h + gap) / 2, t, height=bar_h, color=TOOL, zorder=3)
            ax.text(t + 0.3, i - (bar_h + gap) / 2, str(t), va="center", ha="left", fontsize=7.5, color=INK2)

    ax.set_yticks(range(len(names)))
    ax.set_yticklabels(names, fontsize=8, color=INK)
    ax.set_xlim(0, total + 2)
    ax.set_xticks([0, 5, 10, 15, 20, total])
    ax.set_xticklabels([str(t) for t in [0, 5, 10, 15, 20, total]], fontsize=7.5, color=MUTED)
    ax.grid(axis="x", color=GRID, linewidth=1, zorder=0)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    for spine in ("left", "bottom"):
        ax.spines[spine].set_color(AXIS)
    ax.tick_params(length=0)
    ax.set_title(
        f"Questions about the 2026 clock changes answered correctly, out of {total}",
        loc="left", fontsize=10.5, color=INK, pad=10,
    )
    ax.legend(
        handles=[Patch(color=MEMORY, label="from memory"), Patch(color=TOOL, label="with zone_clock() available")],
        loc="lower right", frameon=False, fontsize=8, labelcolor=INK2,
    )
    fig.text(
        0.01, 0.005,
        "British Columbia, Alberta, Northwest Territories and Morocco all stopped changing their clocks in 2026. "
        "Grader: tzdata 2026d.",
        fontsize=7.5, color=INK2, va="bottom",
    )
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    out.parent.mkdir(exist_ok=True)
    fig.savefig(out, facecolor=SURFACE)
    print(f"wrote {out} ({len(names)} models)")


if __name__ == "__main__":
    main()
