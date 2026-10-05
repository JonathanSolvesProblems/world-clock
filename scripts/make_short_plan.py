"""Edit plan for the World Clock Short (1080x1920), pinned to short/_transcript.json.

Usage:
    python scripts/make_short_plan.py
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
tr = json.loads((ROOT / "short" / "_transcript.json").read_text(encoding="utf-8"))

for seg in tr["segments"]:
    words = []
    for k, w in enumerate(seg["words"]):
        bare = w["word"].strip()
        prev = seg["words"][k - 1]["word"].strip() if k else ""
        nxt = seg["words"][k + 1]["word"].strip() if k + 1 < len(seg["words"]) else ""
        if bare == "of" and prev == "All" and nxt == "19":
            continue  # Whisper heard "All of 19"; the take says "All 19"
        if bare == "handled":
            w["word"] = w["word"].replace("handled", "handed")
        words.append(w)
    seg["words"] = words
    seg["text"] = "".join(w["word"] for w in words).strip()

# Keep the first caption off the thumbnail frame (0 to 0.5 s); the voice still starts at 0.
for seg in tr["segments"]:
    for w in seg["words"]:
        if w["start"] < 0.5:
            w["start"] = 0.5
            w["end"] = max(w["end"], 0.6)

shutil.copy(ROOT / "short" / "thumbnail-short.jpg", ROOT / "broll" / "vertical" / "s00.jpg")

import wave as _wave

with _wave.open(str(ROOT / "short" / "narration.short.wav")) as _w:
    END = round(_w.getnframes() / _w.getframerate(), 2)  # the narration ends on 1.6 s of tail after the last word

SEG = [
    ("s00", 0.0, 0.5), ("v02_question", 0.5, 5.5), ("v03_answer", 5.5, 9.25), ("v04_kaggle", 9.25, 12.85),
    ("v05_tzdb", 12.85, 18.0), ("v06_key", 18.0, 23.1), ("v07_know", 23.1, 28.15), ("v08_none", 28.15, 36.6),
    ("v12_tool", 36.6, 42.45), ("v13_half", 42.45, 45.4), ("v14_opus", 45.4, 49.45), ("v15_end", 49.45, END),
]
plan = {
    "project_name": "World Clock",
    "add_intro_card": False,
    "add_outro_card": False,
    "width": 1080,
    "height": 1920,
    "theme": {
        "palette": {"bg": "#0a0a0f", "accent": "#52de8c", "text": "#ececee", "text2": "#a0a0ac"},
        "captions": {"active": "FFE500", "word_pop": False, "margin_v": 430, "words_per_line": 4, "size": 64},
    },
    "segments": [{"clip_id": c, "start_time": s, "end_time": e, "lower_third": "", "effect": "none"} for c, s, e in SEG],
    "_transcript": tr,
}
(ROOT / "short" / "short.edit-plan.json").write_text(json.dumps(plan, indent=1), encoding="utf-8")
print("wrote short/short.edit-plan.json:", len(SEG), "segments")
