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
| `tasks/render_task.py` | Renders the self-contained Kaggle task files from the answer key. |
| `tasks/world_clock_memory.py` | Kaggle task `world-clock-from-memory`: the model answers from its own knowledge. |
| `tasks/world_clock_tool.py` | Kaggle task `world-clock-tool-v2`: the model may call `zone_clock()`, which reads tzdata 2026d, and is free not to. (The `-v2` is a scar: Kaggle caps how many tasks an account can create in a short window, and the first slugs died as empty shells.) |
| `tasks/world_clock_smoke.py` | Kaggle task `world-clock-smoke`: a stratified 20-case subset, used once to prove the pipeline. |
| `analysis/date_the_clock.py` | Scores downloaded runs, dates each model's clock against the tzdata ladder, writes `results/summary.json` and `results/summary.md`. |
| `check_claims.py` | Fails if a number in the README or the post disagrees with the data. |
| `tests/` | Tests for the answer normalisers and for the dating ladder on synthetic answer sheets. |
| `SCRIPT.md` | The post outline, written before the first commit. |

## Reproduce the answer key

```
python tzhist/fetch_releases.py
python cases/build_cases.py
python tasks/render_task.py
```

## Run on Kaggle

The account needs Kaggle phone verification first; without it, task creation fails
server-side and the Model Proxy token is refused.

```
kaggle auth login
powershell -File scripts\run_all.ps1        # push both tasks, run every model one at a time, download
python analysis/date_the_clock.py results/raw
python analysis/render_tables.py > results/tables.md
python analysis/plot_ladder.py
python analysis/plot_wave.py
python check_claims.py
```

One model at a time is deliberate. The Model Proxy reserves quota per in-flight request
from the output-token cap, and the account's daily allowance is small enough that nineteen
parallel runs drained it in minutes and every later request was refused. Each run also
caps output at 2,500 tokens (doubling once if a model runs out of room) and retries
transient proxy errors itself, because nested evaluations ignore the SDK's retry setting.

Each run leaves `world_clock_answers.json` in its output folder with every case, the
model's normalised answer, its one-sentence note, whether it called the tool, and token
counts. That file is what the analysis, the tables, the charts and the post are built from.

Models the proxy lists but cannot serve are reported and left out: `claude-opus-4-1`,
`grok-4.6` and `grok-4.5-0708` return 404, and `deepseek-r1-0528` rejects tool calling, so
it appears in the from-memory table only.

## What is not in the answer key

Manitoba. The province announced permanent daylight time on September 17, 2026, the tz
maintainers have modelled it in their working tree, and no release carries it yet. The three
Manitoba cases are asked, recorded, shown beside the official announcement, and never counted.
