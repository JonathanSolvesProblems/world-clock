"""Gallery preview images: eight 3:2 stills in the demo video's order, with captions.

Usage:
    python scripts/preview.py

Writes preview/1-*.png ... 8-*.png (1500x1000) and preview/captions.md. Seven come from the
last settled frame of the raw b-roll clips (never the rendered video, which has captions
burned in), letterboxed to 3:2 in the clip's own background colour. The eighth is the live
Kaggle benchmark page. Each caption is asserted to be 140 characters or fewer; the count is
printed here and nowhere else.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "preview"
W, H = 1500, 1000

SHOTS = [
    ("1-the-question", "clip", "b03_answer", 5.8),
    ("2-what-they-know", "clip", "b07_controls", 7.2),
    ("3-nobody-knows-2026", "clip", "b08_wave", 9.2),
    ("4-dating-astra", "clip", "b10_astra", 10.7),
    ("5-gemini-one-clock", "clip", "b11_gemini", 7.7),
    ("6-with-the-tool", "clip", "b13_half", 5.8),
    ("7-opus-argues", "clip", "b14_opus", 5.8),
    ("8-kaggle-task", "page", "https://www.kaggle.com/benchmarks/tasks/jonathanandrei/world-clock-from-memory", 0),
]

CAPTIONS = {
    "1-the-question": "9 a.m. in Calgary on November 15 is 10 a.m. in Toronto. All 19 models asked from memory said 11.",
    "2-what-they-know": "Models know textbook time zones. On the answers that changed in 2026, most get nothing right.",
    "3-nobody-knows-2026": "13 of 19 models got none of the 20 changed 2026 answers right.",
    "4-dating-astra": "Scored against every tzdata release, GPT-6 Astra's clock stops at 2026b. OpenAI states an April 30, 2026 cutoff.",
    "5-gemini-one-clock": "Three Gemini models peak at the same release, tzdata 2025a. Their world clock stops in January 2025.",
    "6-with-the-tool": "With a tzdata lookup tool one call away, 8 of 16 models still said 9 a.m. Calgary is 11:00 in Toronto.",
    "7-opus-argues": "Claude Opus 5 called the tool, got Calgary's real offset, and wrote that it does not match Alberta's actual rules.",
    "8-kaggle-task": "The from-memory task on Kaggle Benchmarks: 125 questions graded against the IANA time zone database, tzdata 2026d.",
}


def letterbox(img: Image.Image) -> Image.Image:
    bg = img.getpixel((5, 5))
    scale = W / img.width
    img = img.resize((W, round(img.height * scale)), Image.LANCZOS)
    canvas = Image.new("RGB", (W, H), bg)
    canvas.paste(img, (0, (H - img.height) // 2))
    return canvas


def clip_frame(clip: str, t: float) -> Image.Image:
    tmp = OUT / "_frame.png"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(t), "-i", str(ROOT / "broll" / f"{clip}.mp4"), "-frames:v", "1", str(tmp)], check=True)
    img = Image.open(tmp).convert("RGB")
    img.load()
    tmp.unlink()
    return img


def page_shot(url: str) -> Image.Image:
    from playwright.sync_api import sync_playwright

    tmp = OUT / "_page.png"
    with sync_playwright() as p:
        b = p.chromium.launch()
        page = b.new_page(viewport={"width": W, "height": H})
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(8000)
        for label in ("OK, Got it.", "OK, Got it"):
            try:
                page.get_by_text(label, exact=True).first.click(timeout=1500)
                break
            except Exception:  # noqa: BLE001
                pass
        page.wait_for_timeout(800)
        page.evaluate("window.scrollTo(0, 60)")
        page.wait_for_timeout(1200)
        page.screenshot(path=str(tmp))
        b.close()
    img = Image.open(tmp).convert("RGB")
    img.load()
    tmp.unlink()
    return img


def main() -> None:
    OUT.mkdir(exist_ok=True)
    lines = ["# Gallery captions", ""]
    for name, kind, src, t in SHOTS:
        img = letterbox(clip_frame(src, t)) if kind == "clip" else page_shot(src)
        path = OUT / f"{name}.png"
        img.save(path)
        cap = CAPTIONS[name]
        assert len(cap) <= 140, f"{name}: caption is {len(cap)} characters"
        assert "—" not in cap and "–" not in cap
        size = path.stat().st_size
        ok = img.size == (W, H) and size < 5_000_000
        print(f"{'ok ' if ok else 'BAD'} {path.name} {img.size} {size // 1024} KB, caption {len(cap)} chars")
        lines += [f"## {name}.png", "", cap, ""]
    (OUT / "captions.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
