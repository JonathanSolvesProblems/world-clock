---
title: Alberta stopped changing its clocks in June. 19 of 19 frontier models still put Calgary on standard time in November.
published: false
description: I asked 19 models what time it is. The IANA tz database graded them and dated each one's world clock to the month.
tags: devchallenge, kagglechallenge, ai, machinelearning
cover_image: https://raw.githubusercontent.com/JonathanSolvesProblems/world-clock/main/results/cover.png
---

*This is a submission for the [Kaggle Benchmarking Challenge](https://dev.to/challenges/kaggle-2026-09-23)*

On June 18, Alberta's [Official Time Act](https://www.alberta.ca/albertas-new-time-system-abt) came into force and the province stopped changing its clocks. British Columbia had done it in March. The [Northwest Territories followed in August](https://www.gov.nt.ca/en/newsroom/northwest-territories-ends-seasonal-time-change), [Morocco went back to plain UTC on September 20](https://www.timeanddate.com/news/time/morocco-abolish-dst.html), and on September 17 [Manitoba announced](https://news.gov.mb.ca/news/index.html?item=75397) it will not fall back on November 1 either. [CBC is running stories](https://www.cbc.ca/news/canada/calgary/alberta-permanent-daylight-savings-businesses-calendars-9.7331872) about a Calgary hairstylist whose winter bookings all moved an hour. [Microsoft published interim guidance](https://techcommunity.microsoft.com/blog/dstblog/interim-guidance-for-alberta-time-zone-changes-2026/4545015) for Windows.

So I asked the question someone in Calgary is asking right now. It is 9 a.m. here on November 15. What time is that in Toronto?

Then I put it to 19 models on Kaggle Benchmarks. All 19 said 11:00. The answer is 10:00.

## What I benchmarked and why

Every model's knowledge stops at its training cutoff, and most of the time you cannot see the edge. Time zones are different. Governments change them by statute, on a date, and the IANA time zone database records every change within days. That gives a benchmark two things most benchmarks never get: an answer key nobody has to write, and a calendar to hold the model's knowledge against.

The answer key is tzdata 2026d, the September release of the same database that runs the clock on your phone. I did not type a single expected answer. A script asks Python's `zoneinfo` what the clock did in a given place on a given date, and that is the truth. The maintainers ship a few releases a year, so the key rewrites itself and the benchmark does not go stale.

125 questions, three kinds:

- What is the UTC offset in Calgary at noon on November 15, 2026? Answer as +HH:MM or -HH:MM.
- It is 09:00 on November 15 in Calgary. What is the local date and time in Toronto?
- Do the clocks in Calgary change at any point during November 1, 2026, and in which direction?

Six families of places and dates. Textbook controls (New York, London, Tokyo). Awkward offsets (Kathmandu at +05:45, the Chatham Islands at +12:45, Lord Howe Island's 30-minute daylight saving). Southern-hemisphere daylight saving. Changes legislated between 2022 and 2025 (Iran, Jordan, Syria, Mexico, Greenland, Egypt, Kazakhstan, Paraguay, Chile's Aysén region). The 2026 wave (British Columbia, Alberta, Northwest Territories, Morocco). And Manitoba, which is announced but in no tzdata release yet, so its three questions are asked, recorded, and never counted. That leaves 122 graded questions.

The part I care about most is the dating trick. Of the 122, 46 have an answer that changed between one tzdata release and another. I keep every release since 2022a unpacked, twenty of them, score each model's answer sheet against all twenty, and the release a model agrees with most is the month its world clock stopped. A model that still puts Almaty at +06:00 has a clock from before February 2024. One that puts Vancouver at -08:00 in December 2026 has a clock from before April 2026.

Answers are structured output, so grading is a string comparison after normalising `UTC-6`, `-6:00` and `−06:00` to the same thing. A wrong hour is a wrong hour. There is no judge model anywhere in the loop, and the task records the model's one-sentence reason for each answer without grading it, which is where the quotes below come from.

## Which models I ran it against

19 models, all through Kaggle Benchmarks, same prompt, temperature 0, no tools. I included 2025 models on purpose (Gemini 2.5 Pro from June, DeepSeek-R1 from May, Claude Haiku 4.5 from October) because a dating method that cannot date a 2025 model to 2025 is not worth reading. Then I asked 46 of the questions a second time with a one-function tool the model was free to ignore: `zone_clock(iana_zone, local_datetime)`, which reads tzdata 2026d. Not "use this tool." Just "it is there."

| Model | Released | Score (of 122) | 2026 questions right (of 25) | Clock dated by the ladder | Vendor's stated cutoff |
|---|---|---|---|---|---|
| GPT-6 Astra | 2026-09-03 | 106 | 9 | 2026b (April 2026), agrees on 46 of 46 | 2026-04-30 |
| GPT-5.5 | 2026-04-23 | 102 | 5 | 2025b to 2026a (March 2025 to March 2026), agrees on 46 of 46 | 2025-12-01 |
| GPT-5.6 Terra | 2026-07-09 | 102 | 5 | 2025b to 2026a (March 2025 to March 2026), agrees on 46 of 46 | 2026-02-16 |
| Claude Opus 5 | 2026-07-24 | 101 of 121 | 5 | 2025b to 2026a (March 2025 to March 2026), agrees on 46 of 46 | 2026-05 |
| Gemini 3.1 Pro | 2026-02-19 | 100 | 5 | 2025a (January 2025), agrees on 45 of 46 | 2025-01 |
| Gemini 3.7 Flash | 2026-08 | 99 | 5 | 2025a (January 2025), agrees on 44 of 46 | 2026-03 |
| Gemini 3.8 Flash | 2026-09-02 | 99 | 5 | 2025a (January 2025), agrees on 44 of 46 | 2026-03 |
| Gemini 2.5 Pro | 2025-06 | 98 | 5 | 2025a (January 2025), agrees on 44 of 46 | 2025-01 |
| Gemini 3.5 Flash-Lite | 2026 | 91 | 7 | 2024a to 2024b (February 2024 to September 2024), agrees on 36 of 46 | not published |
| GLM-5 | 2026-02-11 | 90 | 5 | 2024a to 2024b (February 2024 to September 2024), agrees on 40 of 46 | not published |
| GPT-5.4 mini | 2026-03-17 | 90 | 6 | 2024a to 2026a (February 2024 to March 2026), agrees on 37 of 46 | 2025-08-31 |
| Grok 4.20 Reasoning | 2026-03 | 89 | 4 | 2023d to 2024b (December 2023 to September 2024), agrees on 38 of 46 | 2025-09-01 |
| Gemma 4 31B | 2026-04-02 | 87 | 3 | 2024a to 2024b (February 2024 to September 2024), agrees on 40 of 46 | 2025-01 |
| Claude Sonnet 5 | 2026-06-30 | 86 | 5 | 2022f (October 2022), agrees on 39 of 46 | 2026-01 |
| DeepSeek-R1 | 2025-05-28 | 86 | 5 | 2022f to 2024b (October 2022 to September 2024), agrees on 34 of 46 | 2025-03-31 |
| Claude Opus 4.5 | 2025-11 | 85 | 5 | 2022g to 2024b (November 2022 to September 2024), agrees on 35 of 46 | not published |
| Qwen3-Next 80B Thinking | 2025-09-11 | 85 | 9 | 2022f (October 2022), agrees on 37 of 46 | 2025-09-30 |
| Grok 4.20 | 2026-03 | 79 | 7 | 2022b to 2022d (August 2022 to September 2022), agrees on 33 of 46 | 2025-09-01 |
| Claude Haiku 4.5 | 2025-10-15 | 69 | 6 | 2022b to 2022d (August 2022 to September 2022), agrees on 37 of 46 | 2025-02 |

Claude Opus 5 scored 101 of 121 because one call died on its backend; every other model answered all 122, though Gemma 4 left the answer field empty on five of them, and an empty answer counts as wrong. The vendor cutoffs are what each company publishes where it publishes one, and third-party trackers where it does not. Claude Opus 4.1 and Grok 4.6 are on Kaggle's list but return 404 from the proxy, so they are not here.

## What I found

### Everyone knows how clocks work

Fourteen of the 19 answered all 26 control questions correctly, and nobody scored below 24 of 26. Fourteen got every awkward-offset question right, including Lord Howe Island's half-hour spring forward and the Chatham Islands at +13:45 in January. The southern hemisphere was nearly as clean. This is the part where the [Test of Time paper](https://arxiv.org/abs/2406.09170) found models scoring 74 to 90 percent on time-zone questions back in 2024 and attributed it to the amount of time-zone text on the internet. That reading holds. Time zones as a topic are learned.

Time zones as of a date are a different thing.

### Nobody knows about Alberta

Twenty of the 25 questions about the 2026 wave have an answer that changed this year. The other five are controls inside the family, Vancouver in July or Fort Nelson in November, where nothing changed. Fourteen of the 19 got all five. Thirteen of the 19 got none of the 20 changed answers right, including Claude Opus 5, GPT-5.5, GPT-5.6 Terra and four of the five Geminis.

On the 20 changed questions, across 19 models, there were 17 correct answers. GPT-6 Astra produced 4 of them, all about British Columbia, and gave the right reason: "British Columbia adopted permanent UTC−07:00 in March 2026, so Vancouver does not turn its clocks back in November." The other 13 came with reasons that were wrong, and not one of those 13 notes says that anything changed in 2026. Claude Haiku 4.5 put Casablanca on +00:00 in October because it believes Morocco never adopted +01:00 in the first place. Qwen said Calgary's clocks do not change on November 1 because "the fall back occurs on 2026-11-02". November 1 is the Sunday. I read every one of the thirteen. Not one model knew that Alberta, the Northwest Territories or Morocco had changed anything.

The Calgary offset question is the one I would put in front of a judge, because it cannot be right by accident. Calgary at noon on November 15, 2026 is -06:00. All 19 models said -07:00.

![How many of the 25 questions about the 2026 changes each model got right, from memory and with the tool](https://raw.githubusercontent.com/JonathanSolvesProblems/world-clock/main/results/wave.png)

### Dating the clocks

This is the chart the whole benchmark was built for. Each line is one model's agreement with each tzdata release since 2022, on the 46 answers that changed. The peak is the release the model's clock is dated to. Identical curves are drawn once and labelled with every model on them.

![Answers matching each tzdata release, per vendor](https://raw.githubusercontent.com/JonathanSolvesProblems/world-clock/main/results/ladder.png)

GPT-6 Astra is the cleanest result in the set. Its curve rises through every release since 2022, agrees with tzdata 2026b on all 46 changed answers, and falls off a cliff at 2026c. tzdata 2026b was released on April 22, 2026, and carries British Columbia; the next release, 2026c, came on July 8. So the ladder says this clock stopped somewhere between those two dates. OpenAI says the model's cutoff is April 30, 2026. Those agree, and the ladder got there from nothing but clock questions.

GPT-5.5, GPT-5.6 Terra and Claude Opus 5 share one curve, and it is also a perfect 46 of 46, at 2026a. That is the last release before British Columbia. OpenAI's stated cutoffs for its two are December 2025 and February 2026, both consistent. Anthropic says Opus 5 was trained on data to May 2026, which should include a change that took effect on March 9. Its own note on Vancouver in December says why it does not: "Vancouver observes Pacific Standard Time (UTC-8) in mid-December, since daylight saving time runs only from the second Sunday in March to the first Sunday in November and British Columbia's permanent-DST law is not yet in force." It knows the law. Its clock stopped before the law started.

Gemini 2.5 Pro, 3.1 Pro, 3.7 Flash and 3.8 Flash all date to tzdata 2025a, released January 15, 2025. Gemini 2.5 Pro from June 2025, Gemini 3.7 Flash from August 2026 and Gemini 3.8 Flash from September 2026 have curves that are identical, point for point, 44 of 46 at the peak. Only Flash-Lite sits elsewhere, at 2024a to 2024b with a blurry 36 of 46. Google's model card for 3.8 Flash gives a cutoff of March 2026 "for some domains" and January 2025 for the rest. The clock is one of the rest, and it has not moved in fifteen months of releases.

Claude Sonnet 5 dates to October 2022 and Claude Haiku 4.5 to August or September 2022, against stated cutoffs of January 2026 and February 2025. These are not parsing accidents, I read the answers. Sonnet 5 says "Iran observed daylight saving time (UTC+4:30) in July 2023, before abolishing DST later that year" (Iran abolished it in 2022), puts Cairo on +02:00 in July 2023 in a sentence that mentions Egypt's 2023 reintroduction of daylight saving and then ignores it, and says "Almaty has used a fixed UTC+6 offset since 2024" (Kazakhstan unified on +05:00 in March 2024). It scored 15 of 31 on the changes legislated between 2022 and 2025. GPT-6 Astra, GPT-5.5, GPT-5.6 Terra and Opus 5 scored 31 of 31.

The peak height matters as much as its position. A model at 46 of 46 has a sharp clock: everything before the peak right, everything after it wrong. A model at 33 of 46 has a blurry one, and the dating is a best fit rather than a fact. The table gives both numbers for every model.

### With the tool

Then I asked again with a tool on the table. `zone_clock(iana_zone, local_datetime)` reads tzdata 2026d and returns the offset in force. The system prompt says the tool exists and that the model may call it or answer without it. Nothing tells the model its knowledge might be out of date.

This half asks 46 of the 125 questions: every question about 2026, the three about Manitoba, and eighteen older ones as a control group. 43 of the 46 are graded. The reason it is a subset is money, which I get to below.

| Model | From memory (of 43) | With the tool (of 43) | Asked the tool | Overrode it | Asked about another zone only | Answer changed when restated |
|---|---|---|---|---|---|---|
| Gemini 3.7 Flash | 21 | 42 | 43 of 43 | 0 | 1 | 0 |
| Gemini 3.8 Flash | 21 | 42 | 43 of 43 | 0 | 1 | 0 |
| Gemini 3.1 Pro | 22 | 15 of 15 | 12 of 15 | 0 | 0 | 0 |

Gemini 3.7 Flash and 3.8 Flash asked the tool on every question and went from 21 right to 42. The ladder now dates both clocks as current. Their one miss is the same question, and it is my favourite failure in the benchmark. Chile's Aysén region got its own zone, America/Coyhaique, in tzdata 2025b, which is after Gemini's clock stopped. So the model asks the database about America/Santiago, gets a true answer about the wrong place, and reports it: "Coyhaique and the Aysén Region follow continental Chile standard time (America/Santiago), observing UTC-4 during southern hemisphere winter." A lookup tool fixes what the model knows to look up.

Gemini 3.1 Pro got through 15 of the 43 before the quota ran out. It answered all 15 correctly and asked the tool on 12 of them.

The transcripts show one more thing. Kaggle's SDK runs the tool loop, then sends a final message, "Now format your previous answer using the requested schema.", and the benchmark grades that restated answer. In an earlier run of this task, Gemini 3.7 Flash asked the tool about Calgary and Toronto, wrote 10:00 in its own words with Calgary at UTC-6, and then restated it as 11:00 with Calgary at UTC-7. In the run scored here it did not. `analysis/tool_trace.py` counts every case where the model's own words and its restated answer differ, and the last column of the table is that count.

Why a subset. Kaggle gives each account a model quota of $10 a day, and a tool loop is expensive because every round sends the whole conversation again. Gemini 3.8 Flash cost $0.15 for the 125 questions from memory and $0.99 for the same 125 with the tool. My first full tool lineup ran out of quota partway through Gemini 3.1 Pro, and the runs queued behind it failed on a 403 from the proxy. The models from OpenAI, Anthropic, xAI and the open-weight group are not in this table yet for that reason.

### Manitoba, which nobody can know yet

Manitoba announced on September 17 that it will not fall back on November 1. The tz maintainers have modelled it in their working tree, and no release carries it yet. Every model was asked what Winnipeg does on that morning. Eighteen said the clocks fall back, which is also what tzdata 2026d says today. Qwen said they do not, because it believes the fall-back is on November 2. The province says they will not. Winners of this challenge are announced November 5, four days after the answer becomes a fact, so whoever reads this after November 1 knows something neither the models nor the database did when I ran it.

## What surprised me

Release date is not the clock. Gemini 3.8 Flash shipped on September 2, 2026 with the same world clock as Gemini 2.5 Pro from June 2025, down to the identical 46-number curve. Fifteen months of model releases, one clock.

Knowing about a law is not knowing its date. Opus 5 can tell you British Columbia passed a permanent daylight time law and still puts Vancouver on the wrong offset, because the fact it learned was "passed" and the fact that matters is "in force since March 9."

The models agree with each other more than with the world. On the Calgary to Toronto question, all 19 models gave the same wrong answer, with the same confidence, and most of them cited the same rule: daylight saving ends on the first Sunday in November. That rule was true in Alberta for 55 years. It stopped being true on June 18.

## What I would measure next

Run the same 125 questions again after tzdata 2027a, without changing a line, and see which vendors' clocks moved. The answer key updates itself; the benchmark is designed to be re-run.

Tell the model the current date in the prompt and see whether any of them hedge. Not one of the 19 said "as of my training data" on a question about November 2026.

Add a web-search condition beside the tzdata tool, because the interesting question is not whether a tool fixes it. It is whether a model that believes it knows the answer bothers to check.

## Where to see it

- Benchmark on Kaggle, from memory: https://www.kaggle.com/benchmarks/tasks/jonathanandrei/world-clock-from-memory
- Benchmark on Kaggle, with the tzdata tool: https://www.kaggle.com/benchmarks/tasks/jonathanandrei/world-clock-tool-v2
- Code, answer key, every result and both charts: https://github.com/JonathanSolvesProblems/world-clock

The repo has a script called `check_claims.py`. It reads the results and fails if any number in this post disagrees with them. It ran before this was published.
