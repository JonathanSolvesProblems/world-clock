# World Clock

A Kaggle benchmark that asks frontier models what time it is, and grades every answer against
the IANA time zone database.

Alberta stopped changing its clocks on June 18, 2026. British Columbia had done it in March,
the Northwest Territories followed in August, Morocco returned to plain UTC on September 20,
and Manitoba announced on September 17 that it will not fall back on November 1. Every one
of those changes is in a public record and in the tz database that runs the clock on your
phone. None of them is in a model trained before mid-2026.

This benchmark measures that gap, and then dates it: the same answer sheet is scored against
every tzdata release since 2022, and the release a model agrees with most is the month its
world clock stopped.

Entry for the DEV x Kaggle Benchmarking Challenge (September 23 to October 11, 2026).

## Layout

| Path | What it is |
|---|---|
| `cases/specs.py` | The curated case list: places, dates, question kinds. No answers. |
| `cases/build_cases.py` | Computes every expected answer with `zoneinfo` under every tzdata release in `tzhist/releases/`. Writes `cases.json`, `answer_key.csv`, `ladder.csv`. |
| `tzhist/fetch_releases.py` | Downloads every tzdata wheel from PyPI since 2022 and unpacks its zoneinfo tree. |
| `tasks/render_task.py` | Renders the two self-contained Kaggle task files from the answer key. |
| `tasks/world_clock_memory.py` | Task: the model answers from its own knowledge. |
| `tasks/world_clock_tool.py` | Task: the model may call `zone_clock()`, which reads tzdata 2026d, and is free not to. |
| `tests/test_grading.py` | Tests for the answer normalisers, run against the rendered task file. |
| `SCRIPT.md` | The post outline, written before the first commit. |

## Reproduce the answer key

```
python tzhist/fetch_releases.py
python cases/build_cases.py
python tasks/render_task.py
```

## Run on Kaggle

```
kaggle b init -y
WORLD_CLOCK_LIMIT=20 python tasks/world_clock_memory.py    # smoke test against the default model
kaggle b t push world-clock-memory -f tasks/world_clock_memory.py --wait
kaggle b t run world-clock-memory -m <model> --wait
kaggle b t download world-clock-memory -o results/raw
```

## What is not in the answer key

Manitoba. The province announced permanent daylight time on September 17, 2026, the tz
maintainers have modelled it in their working tree, and no release carries it yet. The three
Manitoba cases are asked, recorded, shown beside the official announcement, and never counted.
