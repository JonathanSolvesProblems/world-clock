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

On Kaggle: the [World Clock benchmark](https://www.kaggle.com/benchmarks/jonathanandrei/world-clock), made of two tasks,
[from memory](https://www.kaggle.com/benchmarks/tasks/jonathanandrei/world-clock-from-memory) and
[with a tzdata tool](https://www.kaggle.com/benchmarks/tasks/jonathanandrei/world-clock-tool-v2).

## Layout

| Path | What it is |
|---|---|
| `cases/specs.py` | The curated case list: places, dates, question kinds. No answers. |
| `cases/build_cases.py` | Computes every expected answer with `zoneinfo` under every tzdata release in `tzhist/releases/`. Writes `cases.json`, `answer_key.csv`, `ladder.csv`. |
| `tzhist/fetch_releases.py` | Downloads every tzdata wheel from PyPI since 2022 and unpacks its zoneinfo tree. |
| `tasks/render_task.py` | Renders the self-contained Kaggle task files from the answer key. |
| `tasks/world_clock_memory.py` | Kaggle task `world-clock-from-memory`: the model answers from its own knowledge. |
| `tasks/world_clock_tool.py` | Kaggle task `world-clock-tool-v2`: the model may call `zone_clock()`, which reads tzdata 2026d, and is free not to. It asks a subset of the questions (every 2026 one, Manitoba, and eighteen older ones; the list is in `cases/specs.py`) because a tool loop costs several times a plain answer. (The `-v2` is a scar: Kaggle caps how many tasks an account can create in a short window, and the first slugs died as empty shells.) |
| `tasks/world_clock_smoke.py` | Kaggle task `world-clock-smoke`: a stratified 20-case subset, used once to prove the pipeline. |
| `analysis/date_the_clock.py` | Scores downloaded runs, dates each model's clock against the tzdata ladder, writes `results/summary.json` and `results/summary.md`. |
| `analysis/model_cards.json` | Release dates and vendor-stated knowledge cutoffs, with the source of each, to set beside the ladder's date. |
| `analysis/render_tables.py` | Renders every table from `summary.json`, including the post's tables with the display names the post uses. |
| `analysis/paste_tables.py` | Pastes the generated tables into `POST.md` over the ones already there. |
| `analysis/plot_ladder.py`, `analysis/plot_wave.py` | The two charts in the post. |
| `analysis/make_cover.py` | The post's cover image. The count on it is read from the runs, and the script refuses to draw "N of N" if any model answered differently. |
| `analysis/quotes.py`, `analysis/wave_detail.py`, `analysis/inspect_runs.py` | Pull each model's own notes for the cases the post talks about, list which 2026 answers each model got right, and eyeball a downloaded run. |
| `analysis/tool_trace.py` | Reads the tool-run conversations: which zone each model asked about, whether it followed or overrode the tool, and whether its answer changed when the SDK asked it to restate the answer in the schema. Writes `results/tool_trace.json`. |
| `analysis/tool_facts.py` | Computes every number the post's tool section states (who asked, who overrode, the restating counts, Coyhaique) from `summary.json` and `tool_trace.json`. `check_claims.py` holds the prose to it. |
| `analysis/dump_conversation.py` | Prints one case's full conversation from a downloaded run, tool calls included. |
| `analysis/run_costs.py` | Sums what each downloaded run cost from the per-request costs in its `.run.json`, and totals per day. |
| `analysis/quota.py` | Prints the account's model quota (used and allowed, in dollars) through the SDK call the CLI does not expose. Run both before launching a lineup: the quota is $10 a day, and once it is gone every queued run fails all its questions on a 403. |
| `check_claims.py` | Fails if a number in the README or the post disagrees with the data, if the post's tables differ from the generated ones, or if a quotation in the post is not in a model's recorded note. |
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
python analysis/paste_tables.py
python analysis/plot_ladder.py
python analysis/plot_wave.py
python analysis/quotes.py > results/quotes.md
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
