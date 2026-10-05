"""Build the demo video's b-roll from the project's own results.

Usage:
    python scripts/make_broll.py [only_id ...]

Writes 1920x1080 clips into broll/ (gitignored). Charts and cards are animated with
Pillow from results/summary.json and results/tool_trace.json, so every number on screen
comes from the same data as the post. Web pages are recorded with Playwright while they
scroll. Each clip runs longer than its beat so the edit never loops.
"""

from __future__ import annotations

import json
import math
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "broll"
sys.path.insert(0, str(ROOT / "analysis"))

W, H, FPS = 1920, 1080, 30
BG = (252, 252, 251)
INK = (11, 11, 11)
INK2 = (82, 81, 78)
MUTED = (137, 135, 129)
GRID = (225, 224, 217)
BLUE = (42, 120, 214)
ORANGE = (235, 104, 52)
AQUA = (27, 175, 122)
YELLOW = (237, 161, 0)

FONT_DIR = Path("C:/Windows/Fonts")


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    name = "segoeuib.ttf" if bold else "segoeui.ttf"
    return ImageFont.truetype(str(FONT_DIR / name), size)


def ease(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


class Writer:
    """Pipe RGB frames into ffmpeg."""

    def __init__(self, name: str):
        self.path = OUT / f"{name}.mp4"
        self.proc = subprocess.Popen(
            ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
             "-i", "-", "-c:v", "libx264", "-crf", "18", "-preset", "fast", "-pix_fmt", "yuv420p", str(self.path)],
            stdin=subprocess.PIPE,
        )

    def add(self, img: Image.Image) -> None:
        self.proc.stdin.write(img.convert("RGB").tobytes())

    def close(self) -> None:
        self.proc.stdin.close()
        self.proc.wait()
        print(f"wrote {self.path.name}")


def canvas() -> tuple[Image.Image, ImageDraw.ImageDraw]:
    img = Image.new("RGB", (W, H), BG)
    return img, ImageDraw.Draw(img)


def text_center(d: ImageDraw.ImageDraw, y: int, s: str, f, fill=INK, x: int | None = None) -> None:
    w = d.textlength(s, font=f)
    d.text(((W - w) / 2 if x is None else x - w / 2, y), s, font=f, fill=fill)


# ---------------------------------------------------------------- data

def _changed_right() -> dict:
    from date_the_clock import find_answer_files
    cases = {c["id"]: c for c in json.loads((ROOT / "cases" / "cases.json").read_text(encoding="utf-8"))}
    ids = {cid for cid, c in cases.items() if c["family"] == "wave_2026" and c["discriminates"]}
    out = {}
    for p in find_answer_files(ROOT / "results" / "raw"):
        dd = json.loads(p.read_text(encoding="utf-8"))
        if dd.get("condition") == "memory" and dd.get("graded_total"):
            out[display(dd["model"])] = sum(1 for x in dd["rows"] if x["id"] in ids and x["correct"])
    return out


class _Lazy(dict):
    def __missing__(self, k):
        self.update(_changed_right())
        return dict.__getitem__(self, k)


CHANGED_RIGHT = _Lazy()

def summary() -> list[dict]:
    return json.loads((ROOT / "results" / "summary.json").read_text(encoding="utf-8"))


def display(model: str) -> str:
    from render_tables import display as d
    return d(model)


# ---------------------------------------------------------------- cards

def question(seconds: float = 8.0) -> None:
    w = Writer("b02_question")
    lines = ["It's 9:00 a.m. in Calgary", "on November 15, 2026.", "What time is it in Toronto?"]
    f = font(84, True)
    starts = [0.2, 1.6, 3.3]
    for i in range(int(seconds * FPS)):
        t = i / FPS
        img, d = canvas()
        for k, (line, s0) in enumerate(zip(lines, starts)):
            n = int(max(0, (t - s0)) * 34)
            if n <= 0:
                continue
            part = line[:n]
            fill = BLUE if k == 2 else INK
            d.text((220, 300 + k * 140), part, font=f, fill=fill)
        # a small clock face that ticks, top right
        cx, cy, r = 1640, 230, 110
        d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=INK2, width=6)
        for h in range(12):
            a = h / 12 * 2 * math.pi
            d.line((cx + math.sin(a) * (r - 18), cy - math.cos(a) * (r - 18), cx + math.sin(a) * (r - 6), cy - math.cos(a) * (r - 6)), fill=MUTED, width=4)
        hour = 9 / 12 * 2 * math.pi
        minute = (t * 6 % 60) / 60 * 2 * math.pi
        d.line((cx, cy, cx + math.sin(hour) * 55, cy - math.cos(hour) * 55), fill=INK, width=9)
        d.line((cx, cy, cx + math.sin(minute) * 85, cy - math.cos(minute) * 85), fill=ORANGE, width=5)
        w.add(img)
    w.close()


def answer(seconds: float = 6.0) -> None:
    from render_tables import SUMMARY
    mem = [r for r in SUMMARY if r["condition"] == "memory" and r["graded_total"]]
    n = len(mem)
    w = Writer("b03_answer")
    big = font(230, True)
    small = font(44, True)
    sub = font(34)
    for i in range(int(seconds * FPS)):
        t = i / FPS
        img, d = canvas()
        a = ease(t / 0.5)
        col = tuple(int(BG[c] + (MUTED[c] - BG[c]) * a) for c in range(3))
        d.text((170, 330), "11:00", font=big, fill=col)
        d.text((180, 640), f"{n} of {n} models", font=small, fill=INK)
        d.text((180, 700), "asked from memory on Kaggle Benchmarks", font=sub, fill=INK2)
        s = ease((t - 0.9) / 0.6)
        if s > 0:
            x1 = 150 + s * (790 - 150)
            d.line((150, 470, x1, 470), fill=ORANGE, width=16)
        d.line((990, 330, 990, 760), fill=GRID, width=3)
        r = ease((t - 2.0) / 0.5)
        if r > 0:
            col = tuple(int(BG[c] + (INK[c] - BG[c]) * r) for c in range(3))
            d.text((1060, 330), "10:00", font=big, fill=col)
            d.line((1070, 615, 1070 + 640 * r, 615), fill=BLUE, width=12)
            d.text((1070, 640), "the IANA tz database, 2026d", font=small, fill=col)
            d.text((1070, 700), "Alberta stopped changing its clocks on June 18", font=sub, fill=col)
        w.add(img)
    w.close()


def controls_vs_wave(seconds: float = 7.5) -> None:
    """Every model knows how clocks work; almost none know about this year."""
    rows = [r for r in summary() if r["condition"] == "memory" and r["graded_total"]]
    rows.sort(key=lambda r: -r["per_family"]["control"]["correct"] / r["per_family"]["control"]["total"])
    w = Writer("b07_controls")
    f_lab = font(22)
    f_h = font(40, True)
    f_s = font(26)
    left, top, rowh = 380, 190, 34
    barw = 560
    for i in range(int(seconds * FPS)):
        t = i / FPS
        img, d = canvas()
        d.text((120, 80), "Textbook questions", font=f_h, fill=INK)
        d.text((1080, 80), "Questions about 2026", font=f_h, fill=INK)
        d.text((120, 132), "share right, from memory", font=f_s, fill=INK2)
        d.text((1080, 132), "changed answers right, of 20", font=f_s, fill=INK2)
        g1 = ease(t / 1.6)
        g2 = ease((t - 2.4) / 1.6)
        for k, r in enumerate(rows):
            y = top + k * rowh
            d.text((left - 20 - d.textlength(display(r["model"]), font=f_lab), y + 6), display(r["model"]), font=f_lab, fill=INK2)
            c = r["per_family"]["control"]
            frac = c["correct"] / c["total"]
            d.rectangle((left, y + 8, left + barw * frac * g1, y + 30), fill=BLUE)
            # 2026 changed answers: wave correct minus the five unchanged controls inside the family
            changed = CHANGED_RIGHT[display(r["model"])]
            x0 = 1300
            if g2 > 0:
                d.rectangle((x0, y + 8, x0 + 28 * changed * g2, y + 30), fill=ORANGE)
                d.text((x0 + 28 * changed * g2 + 12, y + 4), str(changed) if g2 > 0.95 else "", font=f_lab, fill=INK2)
        w.add(img)
    w.close()


def wave_zero(seconds: float = 9.5) -> None:
    """13 of the 19 got none of the changed answers right."""
    from render_tables import SUMMARY
    import date_the_clock  # noqa: F401
    rows = [r for r in SUMMARY if r["condition"] == "memory" and r["graded_total"]]
    cases = {c["id"]: c for c in json.loads((ROOT / "cases" / "cases.json").read_text(encoding="utf-8"))}
    changed_ids = {cid for cid, c in cases.items() if c["family"] == "wave_2026" and c["discriminates"]}
    from date_the_clock import find_answer_files
    right = {}
    for p in find_answer_files(ROOT / "results" / "raw"):
        dd = json.loads(p.read_text(encoding="utf-8"))
        if dd.get("condition") != "memory" or not dd.get("graded_total"):
            continue
        right[display(dd["model"])] = sum(1 for x in dd["rows"] if x["id"] in changed_ids and x["correct"])
    names = sorted(right, key=lambda n: (right[n], n))
    zero = sum(1 for n in names if right[n] == 0)
    w = Writer("b08_wave")
    f_name = font(25, True)
    f_num = font(58, True)
    f_h = font(46, True)
    cols, cw, ch = 5, 345, 140
    for i in range(int(seconds * FPS)):
        t = i / FPS
        img, d = canvas()
        d.text((140, 70), "Changed 2026 answers each model got right, of 20", font=f_h, fill=INK)
        for k, n in enumerate(names):
            appear = ease((t - k * 0.12) / 0.4)
            if appear <= 0:
                continue
            x = 140 + (k % cols) * cw
            y = 200 + (k // cols) * ch
            box = BLUE if right[n] else ORANGE
            fill = tuple(int(BG[c] + (box[c] - BG[c]) * 0.12 * appear) for c in range(3))
            d.rounded_rectangle((x, y, x + cw - 30, y + ch - 24), radius=14, fill=fill, outline=tuple(int(BG[c] + (box[c] - BG[c]) * appear) for c in range(3)), width=3)
            d.text((x + 20, y + 14), n, font=f_name, fill=INK2)
            d.text((x + 20, y + 52), str(right[n]), font=f_num, fill=box)
        c = ease((t - 4.0) / 0.6)
        if c > 0:
            col = tuple(int(BG[k] + (ORANGE[k] - BG[k]) * c) for k in range(3))
            d.text((1500 - d.textlength(f"{zero} of {len(names)} got none of them", font=f_h) + 330, 70), f"{zero} of {len(names)} got none of them", font=f_h, fill=col) if False else d.text((140, 790), f"{zero} of {len(names)} got none of them", font=f_h, fill=col)
        w.add(img)
    w.close()


def ladder(name: str, seconds: float, highlight: list[str], note: list[tuple[float, str, tuple]] | None = None, mark: str | None = None) -> None:
    """Agreement with each tzdata release; lines draw left to right."""
    index = json.loads((ROOT / "tzhist" / "releases" / "index.json").read_text(encoding="utf-8"))
    rel = sorted(index, key=lambda v: tuple(int(x) for x in v.split(".")))
    iana = [index[v]["iana"] for v in rel]
    rows = [r for r in summary() if r["condition"] == "memory" and r.get("clock")]
    x0, x1, y0, y1 = 200, 1720, 780, 250
    n = len(rel)

    def px(k: float) -> float:
        return x0 + (x1 - x0) * k / (n - 1)

    def py(v: float) -> float:
        return y0 - (y0 - y1) * v / 46

    w = Writer(name)
    f_t = font(24)
    f_h = font(44, True)
    f_l = font(30, True)
    hl_cols = [BLUE, ORANGE, AQUA, YELLOW]
    for i in range(int(seconds * FPS)):
        t = i / FPS
        img, d = canvas()
        d.text((200, 70), "Answers that match each tzdata release, of the 46 that changed", font=f_h, fill=INK)
        for v in (0, 10, 20, 30, 40, 46):
            d.line((x0, py(v), x1, py(v)), fill=GRID, width=2)
            d.text((x0 - 50, py(v) - 15), str(v), font=f_t, fill=MUTED)
        for k, lab in enumerate(iana):
            if lab.endswith("a") or lab == "2026d":
                d.text((px(k) - 28, y0 + 18), lab, font=f_t, fill=MUTED)
        for lab in ("2026b", "2026c"):
            k = iana.index(lab)
            d.line((px(k), y1, px(k), y0), fill=GRID, width=2)
        reveal = ease(t / 2.8) * (n - 1)
        hl_rows = [r for r in rows if display(r["model"]) in highlight]
        others = [r for r in rows if display(r["model"]) not in highlight]
        for group, is_hl in ((others, False), (hl_rows, True)):
            for j, r in enumerate(group):
                a = r["clock"]["agreement_by_release"]
                ys = [a[f"{v} ({index[v]['iana']})"] for v in rel]
                pts = []
                for k in range(n):
                    if k <= reveal:
                        pts.append((px(k), py(ys[k])))
                    elif k - 1 < reveal:
                        f = reveal - (k - 1)
                        pts.append((px(k - 1 + f), py(ys[k - 1] + (ys[k] - ys[k - 1]) * f)))
                if len(pts) > 1:
                    col = hl_cols[highlight.index(display(r["model"])) % 4] if is_hl else ((200, 199, 192) if highlight else BLUE)
                    d.line(pts, fill=col, width=7 if is_hl else (3 if highlight else 3), joint="curve")
                if is_hl and reveal >= n - 1:
                    best = max(ys)
                    k = max(idx for idx, v in enumerate(ys) if v == best)
                    d.ellipse((px(k) - 13, py(best) - 13, px(k) + 13, py(best) + 13), fill=hl_cols[highlight.index(display(r["model"])) % 4], outline=BG, width=4)
        if hl_rows and reveal >= n - 1:
            for j, r in enumerate(hl_rows):
                col = hl_cols[highlight.index(display(r["model"])) % 4]
                d.text((x1 - d.textlength(display(r["model"]), font=f_l), 132 + j * 40), display(r["model"]), font=f_l, fill=col)
        if note:
            for (t0, s, col) in note:
                a = ease((t - t0) / 0.5)
                if a > 0:
                    c = tuple(int(BG[k] + (col[k] - BG[k]) * a) for k in range(3))
                    d.text((1000, 960 - 0), s, font=f_l, fill=c) if False else None
            shown = [s for s in note if t >= s[0]]
            for j, (t0, s, col) in enumerate(shown):
                a = ease((t - t0) / 0.5)
                c = tuple(int(BG[k] + (col[k] - BG[k]) * a) for k in range(3))
                d.text((x0, 140 + j * 44), s, font=f_l, fill=c)
        w.add(img)
    w.close()


def tool_asked(seconds: float = 7.5) -> None:
    trace = json.loads((ROOT / "results" / "tool_trace.json").read_text(encoding="utf-8"))
    from tool_facts import facts
    f = facts()
    names = sorted(f["asked"], key=lambda n: -f["asked"][n])
    w = Writer("b12_tool")
    f_lab = font(26)
    f_h = font(44, True)
    f_s = font(28)
    left, top, rowh, barw = 470, 180, 40, 1100
    for i in range(int(seconds * FPS)):
        t = i / FPS
        img, d = canvas()
        d.text((140, 60), "With the tool on the table: questions where the model asked it, of 43", font=f_h, fill=INK)
        d.text((140, 118), "zone_clock() reads tzdata 2026d. The model may ignore it.", font=f_s, fill=INK2)
        g = ease((t - 0.3) / 2.0)
        for k, n in enumerate(names):
            y = top + k * rowh
            d.text((left - 20 - d.textlength(n, font=f_lab), y + 8), n, font=f_lab, fill=INK2)
            v = f["asked"][n]
            d.rectangle((left, y + 10, left + barw * v / 43 * g, y + 40), fill=AQUA if v >= 40 else MUTED)
            if g > 0.95:
                d.text((left + barw * v / 43 + 14, y + 6), str(v), font=f_lab, fill=INK2)
        w.add(img)
    w.close()


def half(seconds: float = 6.0) -> None:
    from tool_facts import facts
    f = facts()
    names = sorted(f["models"])
    said = set(f["hook_said_11"])
    w = Writer("b13_half")
    f_n = font(26, True)
    f_t = font(60, True)
    f_h = font(46, True)
    cols, cw, ch = 4, 420, 160
    for i in range(int(seconds * FPS)):
        t = i / FPS
        img, d = canvas()
        d.text((140, 60), "09:00 in Calgary is ... in Toronto?", font=f_h, fill=INK)
        for k, n in enumerate(names):
            x = 140 + (k % cols) * cw
            y = 170 + (k // cols) * ch
            flip = ease((t - 0.6 - k * 0.08) / 0.3)
            ans = "11:00" if n in said else "10:00"
            col = ORANGE if n in said else AQUA
            c = tuple(int(BG[j] + (col[j] - BG[j]) * flip) for j in range(3))
            d.rounded_rectangle((x, y, x + cw - 30, y + ch - 30), radius=14, outline=c if flip > 0 else GRID, width=3)
            d.text((x + 20, y + 14), n, font=f_n, fill=INK2)
            if flip > 0:
                d.text((x + 20, y + 58), ans, font=f_t, fill=c)
        a = ease((t - 2.6) / 0.5)
        if a > 0:
            c = tuple(int(BG[j] + (ORANGE[j] - BG[j]) * a) for j in range(3))
            d.text((1260, 60), f"{len(said)} of {len(names)} still said 11:00", font=f_h, fill=c)
        w.add(img)
    w.close()


def opus(seconds: float = 6.0) -> None:
    w = Writer("b14_opus")
    quote = '"... the tool reports -06:00 with abbreviation CST, which does not match Alberta\'s actual rules ..."'
    f_q = font(62, True)
    f_s = font(34)
    words = quote.split(" ")
    lines, cur = [], ""
    dd = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    for wd in words:
        trial = (cur + " " + wd).strip()
        if dd.textlength(trial, font=f_q) > 1500:
            lines.append(cur)
            cur = wd
        else:
            cur = trial
    lines.append(cur)
    total = sum(len(l) for l in lines)
    for i in range(int(seconds * FPS)):
        t = i / FPS
        img, d = canvas()
        d.text((210, 220), "Claude Opus 5, after calling the tool about Calgary", font=f_s, fill=INK2)
        d.line((180, 290, 180, 300 + 90 * len(lines)), fill=ORANGE, width=8)
        n = int(max(0, t - 0.3) * 48)
        left = n
        for k, l in enumerate(lines):
            part = l[:max(0, left)]
            left -= len(l)
            d.text((210, 300 + k * 90), part, font=f_q, fill=INK)
        w.add(img)
    w.close()


# ---------------------------------------------------------------- web screencasts

def screencast(name: str, url: str, seconds: float, scroll_px: int, wait: float = 3.0, selector_hide: list[str] | None = None) -> None:
    from playwright.sync_api import sync_playwright

    vid_dir = OUT / "_rec"
    vid_dir.mkdir(exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx = b.new_context(viewport={"width": W, "height": H}, record_video_dir=str(vid_dir), record_video_size={"width": W, "height": H}, device_scale_factor=1)
        page = ctx.new_page()
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(int(wait * 1000))
        for label in ("OK, Got it.", "OK, Got it", "Accept", "Got it"):
            try:
                page.get_by_text(label, exact=True).first.click(timeout=1500)
                page.wait_for_timeout(600)
                break
            except Exception:  # noqa: BLE001
                pass
        for sel in selector_hide or []:
            try:
                page.add_style_tag(content=f"{sel}{{display:none !important}}")
            except Exception:  # noqa: BLE001
                pass
        start = page.video.path()
        steps = int(seconds * FPS)
        for k in range(steps):
            y = scroll_px * ease(k / steps) if scroll_px else 0
            page.evaluate(f"window.scrollTo(0, {y})")
            page.wait_for_timeout(int(1000 / FPS))
        ctx.close()
        b.close()
    src = Path(start)
    # Drop the loading seconds from the head: keep the last `seconds`.
    dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(src)]).decode().strip())
    ss = max(0.0, dur - seconds - 0.2)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{ss:.2f}", "-i", str(src), "-r", str(FPS), "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", str(OUT / f"{name}.mp4")], check=True)
    print(f"wrote {name}.mp4 from {url}")


JOBS = {
    "b01_alberta": lambda: screencast("b01_alberta", "https://www.alberta.ca/albertas-new-time-system-abt", 11, 900, selector_hide=["#onetrust-banner-sdk", ".goa-cookie-banner"]),
    "b02_question": lambda: question(8.0),
    "b03_answer": lambda: answer(6.0),
    "b04_kaggle": lambda: screencast("b04_kaggle", "https://www.kaggle.com/benchmarks/tasks/jonathanandrei/world-clock-from-memory", 6, 300, wait=8),
    "b05_tzdb": lambda: screencast("b05_tzdb", "https://www.iana.org/time-zones", 7, 120),
    "b06_script": lambda: screencast("b06_script", "https://github.com/JonathanSolvesProblems/world-clock/blob/main/cases/build_cases.py", 7.5, 1400, wait=4),
    "b07_controls": lambda: controls_vs_wave(7.5),
    "b08_wave": lambda: wave_zero(9.5),
    "b09_ladder": lambda: ladder("b09_ladder", 13.5, []),
    "b10_astra": lambda: ladder("b10_astra", 11.0, ["GPT-6 Astra"], note=[(0.5, "Clock dated to tzdata 2026b, released April 22, 2026", BLUE), (5.0, "OpenAI's stated cutoff: April 30, 2026", INK)]),
    "b11_gemini": lambda: ladder("b11_gemini", 8.0, ["Gemini 3.8 Flash", "Gemini 3.7 Flash", "Gemini 2.5 Pro"], note=[(0.5, "All three peak at tzdata 2025a, January 2025", INK)]),
    "b12_tool": lambda: tool_asked(7.5),
    "b13_half": lambda: half(6.0),
    "b14_opus": lambda: opus(6.0),
    "b15_close": lambda: screencast("b15_close", "https://github.com/JonathanSolvesProblems/world-clock", 8.5, 900, wait=4),
}

if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    only = sys.argv[1:] or list(JOBS)
    for job in only:
        JOBS[job]()
