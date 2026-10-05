"""Portrait (1080x1920) frames for the World Clock Short.

Usage:
    python scripts/make_short_broll.py [--safe-zone]

Every number is computed from the same data as the post and the long video. Content stays
in the top ~1350px; the bottom 570px is the caption band. Web pages are recorded at a
phone viewport. Writes broll/vertical/*.png and *.mp4.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "broll" / "vertical"
sys.path.insert(0, str(ROOT / "analysis"))
sys.path.insert(0, str(ROOT / "scripts"))

W, H = 1080, 1920
BG = (10, 10, 15)
INK = (236, 236, 238)
INK2 = (160, 160, 172)
YELLOW = (255, 229, 0)
ORANGE = (245, 120, 64)
GREEN = (82, 222, 140)
BLUE = (96, 160, 240)
TOP = 250
SAFE = 1350
SAFE_ZONE = "--safe-zone" in sys.argv


def font(size: int, bold: bool = True):
    return ImageFont.truetype("C:/Windows/Fonts/" + ("seguibl.ttf" if bold else "segoeui.ttf"), size)


def canvas():
    img = Image.new("RGB", (W, H), BG)
    return img, ImageDraw.Draw(img)


def center(d, y, text, f, fill):
    d.text(((W - d.textlength(text, font=f)) / 2, y), text, font=f, fill=fill)


def save(img, name):
    if SAFE_ZONE:
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(ov).rectangle((0, SAFE, W, H), fill=(255, 0, 0, 70))
        img = Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")
    img.save(OUT / f"{name}.png")
    print("wrote", name)


def data():
    from render_tables import SUMMARY, display
    from tool_facts import facts
    import make_broll as mb

    mem = [r for r in SUMMARY if r["condition"] == "memory" and r["graded_total"]]
    perfect_controls = sum(1 for r in mem if r["per_family"]["control"]["correct"] == r["per_family"]["control"]["total"])
    changed = mb._changed_right()
    f = facts()
    return {
        "n": len(mem),
        "perfect_controls": perfect_controls,
        "zero": sum(1 for v in changed.values() if v == 0),
        "changed": changed,
        "n_tool": f["n_full"],
        "asked40": sum(1 for v in f["asked"].values() if v >= 40),
        "said11": sorted(f["hook_said_11"]),
        "tool_models": sorted(f["models"]),
        "display": display,
    }


def question():
    img, d = canvas()
    y = TOP + 160
    for line, col in (("It's 9:00 a.m.", INK), ("in Calgary.", INK), ("Nov 15, 2026.", INK2), ("", INK), ("What time is it", YELLOW), ("in Toronto?", YELLOW)):
        if line:
            center(d, y, line, font(96), col)
        y += 128
    save(img, "v02_question")


def answer(D):
    img, d = canvas()
    center(d, TOP + 40, "AI said", font(56, False), INK2)
    center(d, TOP + 110, "11:00", font(220), (120, 120, 130))
    d.line((170, TOP + 250, W - 170, TOP + 250), fill=ORANGE, width=22)
    center(d, TOP + 380, f"{D['n']} of {D['n']} models", font(64), ORANGE)
    center(d, TOP + 560, "Real answer", font(56, False), INK2)
    center(d, TOP + 630, "10:00", font(220), GREEN)
    center(d, TOP + 900, "Alberta stopped changing", font(50, False), INK2)
    center(d, TOP + 960, "its clocks on June 18", font(50, False), INK2)
    save(img, "v03_answer")


def answer_key():
    img, d = canvas()
    center(d, TOP + 80, "The answer key", font(80), INK)
    center(d, TOP + 240, "125", font(220), YELLOW)
    center(d, TOP + 500, "questions", font(64), INK)
    center(d, TOP + 640, "computed from the IANA", font(52, False), INK2)
    center(d, TOP + 705, "time zone database", font(52, False), INK2)
    center(d, TOP + 860, "typed by hand: 0", font(64), GREEN)
    save(img, "v06_key")


def know(D):
    img, d = canvas()
    center(d, TOP + 40, "Textbook time zones", font(66), INK)
    center(d, TOP + 140, f"{D['perfect_controls']} of {D['n']}", font(180), GREEN)
    center(d, TOP + 370, "models perfect", font(56, False), INK2)
    d.line((140, TOP + 500, W - 140, TOP + 500), fill=(40, 40, 50), width=4)
    center(d, TOP + 560, "The 2026 changes", font(66), INK)
    center(d, TOP + 660, "?", font(220), ORANGE)
    save(img, "v07_know")


def none(D):
    img, d = canvas()
    center(d, TOP + 20, f"{D['zero']} of {D['n']}", font(200), ORANGE)
    center(d, TOP + 250, "got none of the 2026", font(58), INK)
    center(d, TOP + 320, "changes right", font(58), INK)
    names = sorted(D["changed"], key=lambda n: (D["changed"][n], n))
    cols, cw, ch, x0, y0 = 4, 245, 118, 50, TOP + 450
    for k, n in enumerate(names):
        x, y = x0 + (k % cols) * cw, y0 + (k // cols) * ch
        v = D["changed"][n]
        col = ORANGE if v == 0 else BLUE
        d.rounded_rectangle((x, y, x + cw - 20, y + ch - 16), radius=12, outline=col, width=3)
        short = n.replace(" Thinking", "").replace(" Reasoning", " R")
        d.text((x + 12, y + 10), short, font=font(21, False), fill=INK2)
        d.text((x + 12, y + 40), str(v), font=font(44), fill=col)
    save(img, "v08_none")


def tool(D):
    img, d = canvas()
    center(d, TOP + 60, "Then I gave them", font(70), INK)
    center(d, TOP + 150, "the database", font(70), INK)
    center(d, TOP + 360, f"{D['asked40']} of {D['n_tool']}", font(200), GREEN)
    center(d, TOP + 600, "checked it on nearly", font(56, False), INK2)
    center(d, TOP + 665, "every question", font(56, False), INK2)
    save(img, "v12_tool")


def half(D):
    img, d = canvas()
    center(d, TOP + 20, "...and still said", font(66), INK)
    center(d, TOP + 110, "11:00", font(150), ORANGE)
    names = D["tool_models"]
    cols, cw, ch, x0, y0 = 4, 245, 120, 50, TOP + 330
    for k, n in enumerate(names):
        x, y = x0 + (k % cols) * cw, y0 + (k // cols) * ch
        bad = n in D["said11"]
        col = ORANGE if bad else GREEN
        d.rounded_rectangle((x, y, x + cw - 16, y + ch - 14), radius=12, outline=col, width=3)
        short = n.replace(" Thinking", "").replace("Qwen3-Next 80B", "Qwen3-Next").replace(" Reasoning", " R").replace("Gemini ", "Gem ")
        d.text((x + 12, y + 8), short, font=font(21, False), fill=INK2)
        d.text((x + 12, y + 40), "11:00" if bad else "10:00", font=font(44), fill=col)
    center(d, TOP + 870, f"{len(D['said11'])} of {D['n_tool']}", font(110), ORANGE)
    save(img, "v13_half")


def opus():
    img, d = canvas()
    d.text((80, TOP + 60), "Claude Opus 5,", font=font(58), fill=INK2)
    d.text((80, TOP + 130), "after checking:", font=font(58, False), fill=INK2)
    d.line((70, TOP + 260, 70, TOP + 900), fill=ORANGE, width=10)
    y = TOP + 270
    for line in ('"... the tool reports', "-06:00 with", "abbreviation CST,", "which does not", "match Alberta's", 'actual rules ..."'):
        d.text((110, y), line, font=font(72), fill=INK)
        y += 105
    save(img, "v14_opus")


def end():
    img, d = canvas()
    center(d, TOP + 220, "Checking", font(120), INK)
    center(d, TOP + 370, "isn't believing.", font(120), YELLOW)
    center(d, TOP + 640, "World Clock", font(64), INK2)
    center(d, TOP + 720, "on Kaggle Benchmarks", font(52, False), INK2)
    save(img, "v15_end")


def screencast(name: str, url: str, seconds: float, scroll: int, wait: float = 6.0):
    from playwright.sync_api import sync_playwright

    rec = OUT / "_rec"
    rec.mkdir(exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx = b.new_context(viewport={"width": 540, "height": 960}, device_scale_factor=2, record_video_dir=str(rec), record_video_size={"width": 540, "height": 960}, is_mobile=True, has_touch=True)
        page = ctx.new_page()
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(int(wait * 1000))
        for label in ("OK, Got it.", "OK, Got it"):
            try:
                page.get_by_text(label, exact=True).first.click(timeout=1500)
                break
            except Exception:  # noqa: BLE001
                pass
        path = page.video.path()
        n = int(seconds * 30)
        for k in range(n):
            page.evaluate(f"window.scrollTo(0, {scroll * (1 - (1 - k / n) ** 3)})")
            page.wait_for_timeout(33)
        ctx.close()
        b.close()
    dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path]).decode())
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{max(0, dur - seconds - 0.2):.2f}", "-i", path, "-r", "30", "-vf", f"scale={W}:{H}", "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", str(OUT / f"{name}.mp4")], check=True)
    print("wrote", name, "from", url)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    D = data()
    if "--web-only" not in sys.argv:
        question(); answer(D); answer_key(); know(D); none(D); tool(D); half(D); opus(); end()
    if not SAFE_ZONE and "--no-web" not in sys.argv:
        screencast("v04_kaggle", "https://www.kaggle.com/benchmarks/tasks/jonathanandrei/world-clock-from-memory", 5.5, 250, wait=8)
        screencast("v05_tzdb", "https://www.iana.org/time-zones", 7, 200)
