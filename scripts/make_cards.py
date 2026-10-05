"""Title and end cards for the demo video: headshot, product name, site.

Usage:
    python scripts/make_cards.py
"""

from __future__ import annotations

import io
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "broll"
W, H = 1920, 1080
BG = (252, 252, 251)
INK = (11, 11, 11)
INK2 = (82, 81, 78)
ACCENT = (42, 120, 214)
HEADSHOT = "https://jonathansolvesproblems.com/about/jonathan-headshot.jpg"


def font(size: int, bold: bool = False):
    return ImageFont.truetype("C:/Windows/Fonts/" + ("segoeuib.ttf" if bold else "segoeui.ttf"), size)


def headshot(diam: int) -> Image.Image:
    cache = OUT / "_headshot.jpg"
    if not cache.exists():
        req = urllib.request.Request(HEADSHOT, headers={"User-Agent": "Mozilla/5.0"})
        cache.write_bytes(urllib.request.urlopen(req, timeout=30).read())
    src = Image.open(cache).convert("RGB")
    side = src.width  # square crop from the top keeps the hair (it starts at y=27 of 1500)
    sq = src.crop((0, 0, side, side))
    big = diam * 4
    sq = sq.resize((big, big), Image.LANCZOS)
    mask = Image.new("L", (big, big), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, big - 1, big - 1), fill=255)
    ring = Image.new("RGBA", (big + 48, big + 48), (0, 0, 0, 0))
    ImageDraw.Draw(ring).ellipse((0, 0, big + 47, big + 47), fill=ACCENT + (255,))
    ring.paste(sq, (24, 24), mask)
    return ring.resize((diam + 12, diam + 12), Image.LANCZOS)


def card(name: str, lines: list[tuple[str, int, bool, tuple]]) -> None:
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    face = headshot(300)
    img.paste(face, ((W - face.width) // 2, 170), face)
    y = 170 + face.height + 50
    for text, size, bold, col in lines:
        if text == "--rule--":
            y += 18
            d.line(((W - 120) / 2, y + 6, (W + 120) / 2, y + 6), fill=ACCENT, width=6)
            y += 44
            continue
        f = font(size, bold)
        d.text(((W - d.textlength(text, font=f)) / 2, y), text, font=f, fill=col)
        y += int(size * 1.35)
    img.save(OUT / f"{name}.png")
    print(f"wrote {name}.png")


if __name__ == "__main__":
    card("s00-title", [("World Clock", 96, True, INK), ("Dating every model's knowledge of the world's clocks", 40, False, INK2), ("--rule--", 0, False, INK), ("jonathansolvesproblems.com", 34, False, INK2)])
    card("s99-end", [("World Clock", 96, True, INK), ("The benchmark, the code and every result are linked below.", 38, False, INK2), ("--rule--", 0, False, INK), ("jonathansolvesproblems.com", 34, False, INK2)])
