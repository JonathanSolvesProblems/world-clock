"""Trace what each model did with the zone_clock tool, case by case.

Usage:
    python analysis/tool_trace.py [results/raw] [--show MODEL_SUBSTRING]

For every scored tool run (the same run analysis/date_the_clock.py picks), reads the
.run.json conversation beside its answers file and records, per case: the tool calls the
model made (zone, date, what the tool said), whether any call was about the case's own
place on the case's own date, the model's last answer in its own words before the SDK
asked it to restate the answer in the schema, and the structured answer that was graded.

Writes results/tool_trace.json and prints a summary table. The counts that matter:

- followed: asked the tool about the right place and date, and the graded answer agrees
  with what the tool said
- overrode: asked the tool about the right place and date, and the graded answer does not
- other zone only: every call was about some other place or date
- no call: answered from memory
- changed when restated: the model's own words before "Now format your previous answer"
  carried a different value from the JSON it then produced
- right before restating: the graded answer is wrong and the model's own words had it right
"""

from __future__ import annotations

import glob
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from date_the_clock import find_answer_files  # noqa: E402
from render_tables import display  # noqa: E402
from cases.specs import PLACES  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
CASES = {c["id"]: c for c in json.loads((ROOT / "cases" / "cases.json").read_text(encoding="utf-8"))}
FORMAT_PROMPT = "Now format your previous answer using the requested schema."


def zones_for(place_key: str) -> set[str]:
    """The case's own IANA zone. The fallback zone (America/Santiago for Coyhaique) does not
    count: the tool reads tzdata 2026d, which has the real zone, so asking about the
    fallback is asking about a different place."""
    spec = PLACES[place_key]
    zone = spec.get("zone") if isinstance(spec, dict) else spec[1]
    return {zone} if isinstance(zone, str) else set()


def case_places(case_id: str) -> tuple[list[str], str]:
    parts = case_id.split(":")
    if parts[0] == "convert":
        return [parts[1], parts[2]], parts[3]
    return [parts[1]], parts[2]


def norm_offset(s: str) -> str:
    s = s.replace("−", "-").replace("–", "-")
    m = re.match(r"^([+-])(\d{1,2}):(\d{2})$", s.strip())
    if not m:
        return s.strip()
    return f"{m.group(1)}{int(m.group(2)):02d}:{m.group(3)}"


def free_text_value(kind: str, text: str, case_id: str) -> str | bool | None:
    """Pull the answer out of the model's own words, or None if it is not clear."""
    text = text.replace("−", "-")
    # Many models write the JSON themselves before being asked to; read it if it is there.
    m = re.search(r"\{.*\}", text, re.S)
    if m:
        try:
            obj = json.loads(m.group(0))
            if isinstance(obj, dict):
                field = {"offset": "utc_offset", "convert": "time", "change_day": "changes"}[kind]
                if field in obj:
                    return structured_value(kind, obj)
        except Exception:
            pass
    if kind == "offset":
        toks = re.findall(r"(?<![\w:])[+-]\d{1,2}:\d{2}\b", text)
        return norm_offset(toks[-1]) if toks else None
    if kind == "convert":
        m = re.search(r"[Tt]ime\**:?\**\s*\**\s*(\d{1,2}:\d{2})", text)
        if m:
            h, mm = m.group(1).split(":")
            return f"{int(h):02d}:{mm}"
        input_time = case_id.split(":")[-2] + ":" + case_id.split(":")[-1]
        toks = [t for t in re.findall(r"\b(\d{1,2}:\d{2})\b", text) if t != input_time]
        if toks:
            h, mm = toks[-1].split(":")
            return f"{int(h):02d}:{mm}"
        return None
    if kind == "change_day":
        if re.search(r"\b(do|does|did) not (change|fall|spring|turn|move)|no (clock )?changes?\b|remains? (on|at)\b|unchanged", text, re.I):
            return False
        if re.search(r"fall(s|ing)? back|spring(s|ing)? forward|turn(s|ed)? (the clocks? )?(back|forward)|set (the clocks? )?(back|forward)|clocks? change", text, re.I):
            return True
        return None
    return None


def structured_value(kind: str, answer: dict | None) -> str | bool | None:
    if not answer:
        return None
    if kind == "offset":
        return norm_offset(str(answer.get("utc_offset", "")))
    if kind == "convert":
        return answer.get("time")
    if kind == "change_day":
        return answer.get("changes")
    return None


def expected_value(kind: str, case: dict) -> str | bool | None:
    return structured_value(kind, case["expected"])


def parse_tool_part(text: str) -> dict | None:
    try:
        inner = json.loads(text)
        if isinstance(inner, str):
            inner = json.loads(inner)
        if isinstance(inner, dict) and inner.get("name") == "zone_clock":
            return inner
    except Exception:
        return None
    return None


def walk_cases(run: dict) -> dict[str, dict]:
    """conversation id -> conversation, for every case conversation in the run file."""
    out: dict[str, dict] = {}

    def walk(node) -> None:
        if isinstance(node, dict):
            cid = str(node.get("id", ""))
            if "requests" in node and cid.startswith("case "):
                out[cid] = node
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)

    walk(run)
    return out


def trace_case(conv: dict) -> dict:
    calls: list[dict] = []
    free_texts: list[str] = []
    after_format: list[str] = []
    formatting = False
    for req in conv.get("requests", []):
        for part in req.get("contents", []):
            role = part.get("role", "").replace("CONTENT_ROLE_", "")
            for p in part.get("parts", []):
                text = p.get("text")
                if text is None:
                    continue
                if role == "CONTEXT":
                    call = parse_tool_part(text)
                    if call:
                        args = call.get("arguments") or {}
                        out = call.get("output") or {}
                        calls.append({
                            "zone": args.get("iana_zone"),
                            "local_datetime": args.get("local_datetime"),
                            "utc_offset": out.get("utc_offset"),
                            "changes": out.get("clocks_change_during_this_day"),
                            "error": (call.get("error") or {}).get("message") if isinstance(call.get("error"), dict) else call.get("error"),
                        })
                elif role == "USER" and text.strip() == FORMAT_PROMPT:
                    formatting = True
                elif role == "ASSISTANT" and text.strip():
                    (after_format if formatting else free_texts).append(text)
    return {"calls": calls, "free_text": free_texts[-1] if free_texts else None, "restated": bool(after_format)}


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else ROOT / "results" / "raw"
    show = sys.argv[sys.argv.index("--show") + 1] if "--show" in sys.argv else None

    report: dict[str, dict] = {}
    for answers_path in find_answer_files(root):
        d = json.loads(answers_path.read_text(encoding="utf-8"))
        if d.get("condition") != "tool" or "smoke" in d.get("task", "") or not d.get("graded_total"):
            continue
        runs = glob.glob(str(answers_path.parent / "*.run.json"))
        if not runs:
            print(f"no .run.json beside {answers_path}")
            continue
        run = json.loads(Path(runs[0]).read_text(encoding="utf-8"))
        convs = walk_cases(run)
        by_case: dict[str, dict] = {}
        for cid, conv in convs.items():
            case_id = cid[len("case "):].rsplit("-", 1)[0]
            by_case[case_id] = trace_case(conv)

        rows = {r["id"]: r for r in d["rows"]}
        records = []
        for case_id, row in rows.items():
            case = CASES[case_id]
            kind = case["kind"]
            places, date = case_places(case_id)
            own_zones = set().union(*(zones_for(p) for p in places))
            t = by_case.get(case_id, {"calls": [], "free_text": None, "restated": False})
            own = [c for c in t["calls"] if c["zone"] in own_zones and str(c["local_datetime"] or "").startswith(date)]
            errors = [c for c in t["calls"] if c["error"]]
            ft = free_text_value(kind, t["free_text"], case_id) if t["free_text"] else None
            sv = structured_value(kind, row.get("answer"))
            ev = expected_value(kind, case)
            rec = {
                "id": case_id,
                "kind": kind,
                "graded": row["graded"],
                "correct": row["correct"],
                "n_calls": len(t["calls"]),
                "own_place_calls": len(own),
                "other_zones": sorted({c["zone"] for c in t["calls"] if c["zone"] not in own_zones and c["zone"]}),
                "tool_errors": len(errors),
                "restated": t["restated"],
                "free_text_value": ft,
                "structured_value": sv,
                "expected_value": ev,
                "changed_when_restated": (ft is not None and sv is not None and ft != sv),
                "right_before_restating": (row["graded"] and not row["correct"] and ft is not None and ft == ev),
                "note": row.get("note", ""),
                "free_text": (t["free_text"] or "")[:400],
            }
            records.append(rec)

        graded = [r for r in records if r["graded"]]
        summary = {
            "cases": len(graded),
            "correct": sum(1 for r in graded if r["correct"]),
            "with_call": sum(1 for r in graded if r["n_calls"]),
            "own_place": sum(1 for r in graded if r["own_place_calls"]),
            "followed": sum(1 for r in graded if r["own_place_calls"] and r["correct"]),
            "overrode": sum(1 for r in graded if r["own_place_calls"] and not r["correct"]),
            "other_zone_only": sum(1 for r in graded if r["n_calls"] and not r["own_place_calls"]),
            "no_call": sum(1 for r in graded if not r["n_calls"]),
            "no_call_correct": sum(1 for r in graded if not r["n_calls"] and r["correct"]),
            "tool_errors": sum(r["tool_errors"] for r in graded),
            "restated": sum(1 for r in graded if r["restated"]),
            "changed_when_restated": sum(1 for r in graded if r["changed_when_restated"]),
            "right_before_restating": sum(1 for r in graded if r["right_before_restating"]),
            "wrong": [r["id"] for r in graded if not r["correct"]],
        }
        report[d["model"]] = {"task": d["task"], "summary": summary, "cases": records}

    out = ROOT / "results" / "tool_trace.json"
    out.write_text(json.dumps(report, indent=1, ensure_ascii=False), encoding="utf-8")

    print("| Model | Score | Asked the tool | About the right place and date | Followed it | Overrode it | Other zone only | No call | Changed when restated | Right before restating |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    for model, rep in sorted(report.items(), key=lambda kv: -kv[1]["summary"]["correct"]):
        s = rep["summary"]
        print(
            f"| {display(model)} | {s['correct']} of {s['cases']} | {s['with_call']} | {s['own_place']} | {s['followed']} | {s['overrode']} | "
            f"{s['other_zone_only']} | {s['no_call']} | {s['changed_when_restated']} | {s['right_before_restating']} |"
        )
    for model, rep in report.items():
        if show and show not in model:
            continue
        s = rep["summary"]
        if not show and not (s["overrode"] or s["other_zone_only"] or s["right_before_restating"]):
            continue
        print(f"\n### {display(model)}")
        for r in rep["cases"]:
            if not r["graded"]:
                continue
            flag = []
            if r["own_place_calls"] and not r["correct"]:
                flag.append("OVERRODE")
            if r["n_calls"] and not r["own_place_calls"]:
                flag.append(f"OTHER ZONE {r['other_zones']}")
            if r["right_before_restating"]:
                flag.append("RIGHT BEFORE RESTATING")
            if r["changed_when_restated"] and not r["right_before_restating"]:
                flag.append(f"CHANGED WHEN RESTATED ({r['free_text_value']} -> {r['structured_value']})")
            if flag or show:
                if not flag and not (show and not r["correct"]):
                    continue
                print(f"  {'ok' if r['correct'] else 'X '} {r['id']:45s} calls={r['n_calls']} {' | '.join(flag)}")
                if flag:
                    print(f"       words: {r['free_text'][:220]!r}")
                    print(f"       json:  {r['structured_value']!r}  expected {r['expected_value']!r}  note: {r['note'][:160]}")
    print(f"\nwrote {out} ({len(report)} tool runs)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
