"""Print one case's conversation from a downloaded Kaggle run file, tool calls included.

Usage:
    python analysis/dump_conversation.py <path/to/*.run.json> <case id or prefix> [--raw]

Walks the run's conversations, finds the ones whose id starts with "case <prefix>", and
prints each request's parts in order: system, user, tool outputs (the zone_clock JSON with
the call_id shortened) and the model's text. --raw prints the JSON of the first match
instead, for when the shape is not what this script expects.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


def shorten(text: str) -> str:
    return re.sub(r'call_id\\*": \\*"[^"\\]{0,20}[^,]*', 'call_id": "..."', text)


def main() -> int:
    path = Path(sys.argv[1])
    prefix = sys.argv[2]
    raw = "--raw" in sys.argv
    run = json.loads(path.read_text(encoding="utf-8"))

    # Case conversations are nested inside the subtask records; walk everything.
    convs: list[dict] = []

    def walk(node) -> None:
        if isinstance(node, dict):
            if "requests" in node and str(node.get("id", "")).startswith("case "):
                convs.append(node)
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)

    walk(run)
    hits = [c for c in convs if str(c.get("id", "")).startswith(f"case {prefix}")]
    if not hits:
        print(f"no conversation id starts with 'case {prefix}' among {len(convs)} conversations")
        return 1
    if raw:
        print(json.dumps(hits[0], indent=1)[:20000])
        return 0
    for c in hits:
        print(f"=== {c['id']}")
        for req in c.get("requests", []):
            for part in req.get("contents", []):
                role = part.get("role", "?").replace("CONTENT_ROLE_", "")
                sender = part.get("senderName", "")
                for p in part.get("parts", []):
                    text = p.get("text")
                    if text is None:
                        text = json.dumps({k: v for k, v in p.items()})
                    text = shorten(text)
                    if role == "CONTEXT":
                        # Tool output: decode the JSON-in-a-string so the arguments and output read.
                        try:
                            inner = json.loads(text)
                            if isinstance(inner, str):
                                inner = json.loads(inner)
                            args = inner.get("arguments")
                            out = inner.get("output")
                            err = inner.get("error")
                            print(f"  [{sender}] args={json.dumps(args)} -> offset={ (out or {}).get('utc_offset') } change={(out or {}).get('clocks_change_during_this_day')} error={err}")
                            continue
                        except Exception:
                            pass
                    if role == "SYSTEM":
                        continue
                    print(f"  [{role} {sender}] {text[:600]}")
            metrics = req.get("metrics", {})
            print(f"  -- request {req.get('id', '')[-6:]}: in={metrics.get('inputTokens')} out={metrics.get('outputTokens')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
