"""Write the demo video's edit plan from the narration transcript.

Usage:
    python scripts/make_edit_plan.py

Beats are pinned to word timings in broll/_transcript.json (Whisper small on
broll/narration.wav). Two Whisper errors are corrected against the script.
Writes demo.edit-plan.json for `vidkit assemble --edit-plan`.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
tr = json.loads((ROOT / "broll" / "_transcript.json").read_text(encoding="utf-8"))

FIXES = {"handled": "handed", "Opis": "Opus", "All of 19": "All 19"}
for seg in tr["segments"]:
    for w in seg["words"]:
        bare = w["word"].strip()
        if bare in FIXES:
            w["word"] = w["word"].replace(bare, FIXES[bare])
        if bare == "-5":
            w["word"] = " 5"
    seg["text"] = "".join(w["word"] for w in seg["words"]).strip()

SEG = [
    ("b01_alberta", 0.0, 8.6, "Source: Government of Alberta, 2026"),
    ("b02_question", 8.6, 14.1, ""),
    ("b03_answer", 14.1, 17.8, "Graded by tzdata 2026d"),
    ("b04_kaggle", 17.8, 21.4, "World Clock on Kaggle Benchmarks"),
    ("b05_tzdb", 21.4, 26.4, "The IANA time zone database"),
    ("b06_script", 26.4, 31.7, "cases/build_cases.py"),
    ("b07_controls", 31.7, 37.1, ""),
    ("b08_wave", 37.1, 44.8, ""),
    ("b09_ladder", 44.8, 56.4, ""),
    ("b10_astra", 56.4, 65.5, "Source: OpenAI, 2026"),
    ("b11_gemini", 65.5, 71.4, "Source: Google DeepMind model card, 2026"),
    ("b12_tool", 71.4, 76.9, ""),
    ("b13_half", 76.9, 80.2, ""),
    ("b14_opus", 80.2, 84.2, ""),
    ("b15_close", 84.2, 89.6, "github.com/JonathanSolvesProblems/world-clock"),
    ("s99-end", 89.6, 93.3, ""),
]

plan = {
    "project_name": "World Clock",
    "add_intro_card": True,
    "intro_clip": "s00-title",
    "intro_duration": 3.5,
    "intro_effect": "none",
    "add_outro_card": False,
    "theme": {
        "palette": {"bg": "#fcfcfb", "accent": "#2a78d6", "text": "#0b0b0b", "text2": "#52514e"},
        "captions": {"margin_v": 70},
    },
    "segments": [
        {"clip_id": c, "start_time": s, "end_time": e, "lower_third": lt, "effect": "none"}
        for c, s, e, lt in SEG
    ],
    "_transcript": tr,
}
(ROOT / "demo.edit-plan.json").write_text(json.dumps(plan, indent=1), encoding="utf-8")
print("wrote demo.edit-plan.json:", len(SEG), "segments")
print(" ".join(w["word"] for s in tr["segments"] for w in s["words"] if w["word"].strip() in ("handed", "Opus", "5", "All", "19")))
