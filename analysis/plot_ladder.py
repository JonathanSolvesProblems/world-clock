"""Draw the dating ladder: agreement with each tzdata release, one panel per vendor.

Usage:
    python analysis/plot_ladder.py [--condition memory] [--out results/ladder.png]

Reads results/summary.json. Each line is one model's agreement with each tzdata release on
the 46 ladder cases; the marker sits on the release the clock is dated to. Small multiples
by vendor keep every panel under five lines so the end labels stay attached to their lines.
Colours follow a fixed categorical order within a panel (blue, orange, aqua, yellow) and
never encode rank. Text uses ink tokens, never a series colour.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SUMMARY = json.loads((ROOT / "results" / "summary.json").read_text(encoding="utf-8"))
INDEX = json.loads((ROOT / "tzhist" / "releases" / "index.json").read_text())
RELEASES = sorted(INDEX, key=lambda v: tuple(int(x) for x in v.split(".")))
IANA = [INDEX[v]["iana"] for v in RELEASES]

SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK2 = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
AXIS = "#c3c2b7"
SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4"]

VENDOR_OF = {
    "google": "Google",
    "anthropic": "Anthropic",
    "openai": "OpenAI",
    "xai": "xAI",
}


def vendor(model: str) -> str:
    prefix = model.split("/")[0].lower()
    return VENDOR_OF.get(prefix, "Open weights and others")


def short(model: str) -> str:
    return model.split("/")[-1].split("@")[0]


def main() -> None:
    condition = "memory"
    out = ROOT / "results" / "ladder.png"
    if "--condition" in sys.argv:
        condition = sys.argv[sys.argv.index("--condition") + 1]
    if "--out" in sys.argv:
        out = Path(sys.argv[sys.argv.index("--out") + 1])

    rows = [r for r in SUMMARY if r["condition"] == condition and r.get("clock")]
    panels: dict[str, list[dict]] = {}
    for r in rows:
        panels.setdefault(vendor(r["model"]), []).append(r)
    order = [v for v in ["Google", "Anthropic", "OpenAI", "xAI", "Open weights and others"] if v in panels]
    if not order:
        raise SystemExit("nothing to plot")

    n = len(order)
    cols = 2 if n > 1 else 1
    nrows = (n + cols - 1) // cols
    fig, axes = plt.subplots(nrows, cols, figsize=(6.4 * cols, 3.6 * nrows), dpi=200, squeeze=False)
    fig.patch.set_facecolor(SURFACE)
    plt.rcParams["font.family"] = ["Segoe UI", "DejaVu Sans", "sans-serif"]

    x = list(range(len(RELEASES)))
    ladder_total = rows[0]["clock"]["ladder_cases"]

    for ax, name in zip(axes.flat, order):
        ax.set_facecolor(SURFACE)
        series = sorted(panels[name], key=lambda r: short(r["model"]))
        # Models with identical curves share one line and one label: an identical
        # ladder row means an identical clock, which is worth seeing as one line.
        curves: dict[tuple, list[dict]] = {}
        for r in series:
            agree = r["clock"]["agreement_by_release"]
            y = tuple(agree[f"{v} ({INDEX[v]['iana']})"] for v in RELEASES)
            curves.setdefault(y, []).append(r)
        distinct = sorted(curves.items(), key=lambda kv: -kv[0][-1])  # by end value, high to low

        # End-label positions: keep labels at least `gap` apart, top down.
        gap = 3.2
        label_y: list[float] = []
        for y, _ in distinct:
            want = float(y[-1])
            if label_y and want > label_y[-1] - gap:
                want = label_y[-1] - gap
            label_y.append(want)

        for i, ((y, members), ly) in enumerate(zip(distinct, label_y)):
            colour = SERIES[i % len(SERIES)]
            ax.plot(x, y, color=colour, linewidth=2, solid_joinstyle="round", solid_capstyle="round", zorder=3)
            best = max(y)
            k = max(idx for idx, val in enumerate(y) if val == best)  # latest release tied at the peak
            ax.scatter([k], [y[k]], s=64, color=colour, edgecolors=SURFACE, linewidths=2, zorder=4)
            names = ", ".join(short(m["model"]) for m in members)
            label = f"{names}: {IANA[k]}"
            xe = x[-1]
            if abs(ly - y[-1]) > 0.1:
                ax.plot([xe + 0.15, xe + 0.9], [y[-1], ly], color=AXIS, linewidth=0.8, zorder=2)
            ax.text(xe + 1.05, ly, label, va="center", ha="left", fontsize=7, color=INK2)

        ax.set_title(f"{name} ({len(series)} model{'s' if len(series) != 1 else ''})", loc="left", fontsize=10, color=INK, pad=6)
        ax.set_ylim(0, ladder_total + 2)
        ax.set_xlim(-0.5, len(RELEASES) - 0.5 + 11)  # room for end labels
        ax.set_xticks(x)
        shown = {"2022a", "2023a", "2024a", "2025a", "2026a", "2026d"}
        ax.set_xticklabels([lab if lab in shown else "" for lab in IANA], fontsize=7, color=MUTED)
        ax.set_yticks([0, 10, 20, 30, 40, ladder_total])
        ax.set_yticklabels([str(t) for t in [0, 10, 20, 30, 40, ladder_total]], fontsize=7, color=MUTED)
        ax.grid(axis="y", color=GRID, linewidth=1)
        for spine in ("top", "right"):
            ax.spines[spine].set_visible(False)
        for spine in ("left", "bottom"):
            ax.spines[spine].set_color(AXIS)
        ax.tick_params(length=0)
        for iana_name in ("2026b", "2026c", "2026d"):
            ax.axvline(IANA.index(iana_name), color=GRID, linewidth=1, zorder=1)

    for ax in list(axes.flat)[len(order):]:
        ax.set_visible(False)

    fig.suptitle(
        f"Answers matching each tzdata release, out of the {ladder_total} that changed since 2022",
        x=0.02, ha="left", fontsize=11, color=INK,
    )
    fig.text(
        0.02, 0.005,
        "The peak marks the release the model's clock is dated to. Vertical lines are the 2026 releases: 2026b (British Columbia),\n"
        "2026c (Alberta and Morocco), 2026d (Northwest Territories). Answers from memory, no tools. Grader: tzdata 2026d.",
        fontsize=7.5, color=INK2, va="bottom",
    )
    fig.tight_layout(rect=(0, 0.05, 1, 0.95))
    out.parent.mkdir(exist_ok=True)
    fig.savefig(out, facecolor=SURFACE)
    print(f"wrote {out} ({len(rows)} models, {n} panels)")


if __name__ == "__main__":
    main()
