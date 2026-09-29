---
title: Alberta stopped changing its clocks in June. [N] of [M] frontier models still turn them back on November 1.
published: false
tags: devchallenge, kagglechallenge, ai, machinelearning
---

*This is a submission for the [Kaggle Benchmarking Challenge](https://dev.to/challenges/kaggle-2026-09-23)*

On June 18, Alberta passed the Official Time Act and stopped changing its clocks. British Columbia had done it in March. The Northwest Territories followed in August, Morocco went back to plain UTC on September 20, and on September 17 Manitoba announced it will not fall back on November 1 either. CBC is running stories about calendar chaos in Calgary. Microsoft published interim guidance for Windows.

So I asked the question someone in Calgary is asking right now. I have a 9 a.m. call with Toronto on November 15. What time is that for them?

Then I asked every model on Kaggle Benchmarks.

## What I benchmarked and why

Every model's knowledge of the world stops at its training cutoff. Most of the time you cannot see the edge. Time zones are different: governments change them by statute, on a date, and the IANA time zone database records every change within days. That gives a benchmark two things most benchmarks never get. An answer key nobody has to write, and a calendar to hold the model's knowledge against.

The answer key is tzdata 2026d, the September release of the same database that runs the clock on your phone. I did not type a single expected answer. A script asks `zoneinfo` what the clock did in a given place on a given date, and that is the truth. The IANA maintainers ship about four releases a year, so the key rewrites itself and the benchmark does not go stale.

125 questions, three kinds:

- What is the UTC offset in Calgary at noon on November 15, 2026? Answer as +HH:MM or -HH:MM.
- It is 09:00 on November 15 in Calgary. What is the local date and time in Toronto?
- Do the clocks in Calgary change at any point during November 1, 2026, and in which direction?

Six families of places and dates. Textbook controls (New York, London, Tokyo). Awkward offsets (Kathmandu at +05:45, the Chatham Islands at +12:45, Lord Howe Island's 30-minute daylight saving). Southern-hemisphere daylight saving. Changes legislated between 2022 and 2025 (Iran, Jordan, Syria, Mexico, Greenland, Egypt, Kazakhstan, Paraguay, Chile's Aysén region). The 2026 wave (British Columbia, Alberta, Northwest Territories, Morocco). And Manitoba, which is announced but in no tzdata release yet, so its three questions are asked, recorded, and never counted.

The part I care about most is the dating trick. Of the 125 questions, 46 have an answer that changed between one tzdata release and another. I keep every release since 2022a unpacked, score each model's answer sheet against all twenty of them, and the release a model agrees with most is the month its world clock stopped. A model that still puts Almaty at +06:00 has a clock from before February 2024. A model that puts Vancouver at -08:00 in December 2026 has a clock from before April 2026.

The answers are structured output, so grading is a string comparison after normalising `UTC-6`, `-6:00` and `−06:00` to the same thing. A wrong hour is a wrong hour. There is no judge model anywhere in the loop.

## Which models I ran it against

[M] models, all through Kaggle Benchmarks, all with the same prompt, temperature 0, no tools:

[table: model, vendor, release month]

Two choices in that lineup were deliberate. I included models from mid-2025 on purpose (Claude Opus 4.1, Gemini 2.5 Pro, DeepSeek-R1 from May 2025), because a dating method that cannot date a 2025 model to 2025 is not worth reading. And I ran the same questions a second time with a one-function tool the model was free to ignore: `zone_clock(iana_zone, local_datetime)`, which reads tzdata 2026d. Not "use this tool." Just "it is there." The question was whether a model checks when it already believes it knows.

## What I found

[Headline table: model, graded score out of 122, accuracy by family, clock dated to.]

[Paragraph: the controls. Expected near-perfect; report the actual.]

[Paragraph: the 2026 wave. How many models put Vancouver on -08:00 in December, Calgary on -07:00 in November, Casablanca on +01:00 in October. The exact count of models that still fall back Calgary on November 1.]

[Quote one or two model notes verbatim. From the smoke run, Gemini 3.7 Flash on Vancouver in November: "Pacific Standard Time is observed following the end of daylight saving time on the first Sunday in November." Re-verify against the full run before quoting.]

[Paragraph: the dating table. Which release each model's clock agrees with, and how that lines up with the vendor's published cutoff. Where they disagree, say so.]

[Paragraph: what the 2022 to 2025 family showed. Which changes every model knew (Iran, Jordan) and which some missed (Kazakhstan, Paraguay, Aysén).]

[Paragraph: the tool run. Accuracy with the tool available. How many cases each model actually called it on. Whether the models that were wrong from memory called it more or less than the ones that were right.]

[Paragraph: Manitoba. Every model was asked what Winnipeg does on the morning of November 1. tzdata 2026d says the clocks fall back, because no release carries the announcement yet. The province says they will not. Report who asserted, who hedged, and note that winners of this challenge are announced November 5, four days after the answer becomes a fact.]

## What surprised me

[Filled from the data, not from the plan. Candidates so far: the same model that knew Iran ended daylight saving in 2022 put Vancouver on standard time in December 2026. Nothing is wrong with its reasoning about clocks; the rule it applied was true for 118 years.]

## What I would measure next

[Filled from the data. Candidates: the same benchmark re-run on the December tzdata release, to see which vendors' clocks moved; a web-search condition; whether telling the model the current date changes anything.]

## Where to see it

- Benchmark on Kaggle, from memory: https://www.kaggle.com/benchmarks/tasks/jonathanandrei/world-clock-from-memory
- Benchmark on Kaggle, with the tzdata tool: https://www.kaggle.com/benchmarks/tasks/jonathanandrei/world-clock-tool-v2
- Code, answer key, and every result: https://github.com/JonathanSolvesProblems/world-clock

The repo has a script called `check_claims.py`. It reads the results and fails if any number in this post disagrees with them. It ran before this was published.
