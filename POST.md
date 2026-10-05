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

Six families of places and dates. Textbook controls (New York, London, Tokyo). Awkward offsets (Kathmandu at +05:45, the Chatham Islands at +12:45, Lord Howe Island's 30-minute daylight saving). Southern-hemisphere daylight saving. Changes legislated between 2022 and 2025 (Iran, Jordan, Syria, Mexico, Greenland, Egypt, Kazakhstan, Paraguay, Chile's Aysén region). The 2026 wave (British Columbia, Alberta, Northwest Territories, Morocco). And Manitoba, which announced its change on September 17, after the release I graded against, so its three questions are asked, recorded, and not counted in the score. That leaves 122 graded questions.

The part I care about most is the dating trick. Of the 122, 46 have an answer that changed between one tzdata release and another. I keep every release since 2022a unpacked, twenty of them, score each model's answer sheet against all twenty, and the release a model agrees with most is the month its world clock stopped. A model that still puts Almaty at +06:00 has a clock from before February 2024. One that puts Vancouver at -08:00 in December 2026 has a clock from before April 2026.

Answers are structured output, so grading is a string comparison after normalising `UTC-6`, `-6:00` and `−06:00` to the same thing. A wrong hour is a wrong hour. There is no judge model anywhere in the loop, and the task records the model's one-sentence reason for each answer without grading it, which is where the quotes below come from.

## Which models I ran it against

19 models, all through Kaggle Benchmarks, same prompt, temperature 0, no tools. I included 2025 models on purpose (Gemini 2.5 Pro from June, DeepSeek-R1 from May, Claude Haiku 4.5 from October) because a dating method that cannot date a 2025 model to 2025 is not worth reading. Then I asked 46 of the questions a second time with a one-function tool the model was free to ignore: `zone_clock(iana_zone, local_datetime)`, which reads tzdata 2026d. Not "use this tool." Just "it is there."

| Model | Released | Score (of 122) | 2026 questions right (of 25) | Clock dated by the ladder | Vendor's stated cutoff |
|---|---|---|---|---|---|
| GPT-6 Astra | 2026-09-03 | 107 | 10 | 2026b (April 2026), agrees on 45 of 46 | 2026-04-30 |
| Claude Opus 5 | 2026-07-24 | 102 | 5 | 2025b to 2026a (March 2025 to March 2026), agrees on 46 of 46 | 2026-05 |
| GPT-5.5 | 2026-04-23 | 102 | 5 | 2025b to 2026a (March 2025 to March 2026), agrees on 46 of 46 | 2025-12-01 |
| GPT-5.6 Terra | 2026-07-09 | 102 | 5 | 2025b to 2026a (March 2025 to March 2026), agrees on 46 of 46 | 2026-02-16 |
| Gemini 2.5 Pro | 2025-06 | 99 | 6 | 2025a (January 2025), agrees on 42 of 46 | 2025-01 |
| Gemini 3.7 Flash | 2026-08 | 99 | 5 | 2025a (January 2025), agrees on 44 of 46 | 2026-03 |
| Gemini 3.8 Flash | 2026-09-02 | 99 | 5 | 2025a (January 2025), agrees on 44 of 46 | 2026-03 |
| Gemini 3.1 Pro | 2026-02-19 | 98 | 5 | 2025a (January 2025), agrees on 43 of 46 | 2025-01 |
| GLM-5 | 2026-02-11 | 93 of 121 | 4 of 24 | 2024a to 2024b (February 2024 to September 2024), agrees on 42 of 46 | not published |
| Gemini 3.5 Flash-Lite | 2026 | 91 | 7 | 2024a to 2024b (February 2024 to September 2024), agrees on 39 of 46 | not published |
| Gemma 4 31B | 2026-04-02 | 90 | 3 | 2024a to 2024b (February 2024 to September 2024), agrees on 41 of 46 | 2025-01 |
| Grok 4.20 Reasoning | 2026-03 | 89 | 4 | 2023a to 2023c (March 2023), agrees on 40 of 46 | 2025-09-01 |
| GPT-5.4 mini | 2026-03-17 | 88 | 4 | 2024a to 2024b (February 2024 to September 2024), agrees on 39 of 46 | 2025-08-31 |
| Claude Opus 4.5 | 2025-11 | 87 | 5 | 2022g (November 2022), agrees on 37 of 46 | not published |
| Claude Sonnet 5 | 2026-06-30 | 87 | 5 | 2022f (October 2022), agrees on 39 of 46 | 2026-01 |
| Qwen3-Next 80B Thinking | 2025-09-11 | 85 | 9 | 2022f (October 2022), agrees on 37 of 46 | 2025-09-30 |
| DeepSeek-R1 | 2025-05-28 | 82 of 121 | 7 | 2022a (March 2022), agrees on 36 of 46 | 2025-03-31 |
| Grok 4.20 | 2026-03 | 77 | 7 | 2022e (October 2022), agrees on 34 of 46 | 2025-09-01 |
| Claude Haiku 4.5 | 2025-10-15 | 59 | 3 | 2022a to 2022d (March 2022 to September 2022), agrees on 39 of 46 | 2025-02 |

GLM-5 and DeepSeek-R1 each lost one call to their backends, so each is scored on 121 questions; every other model answered all 122, though Gemma 4 left the answer field empty on six of them, and an empty answer counts as wrong. The vendor cutoffs are what each company publishes where it publishes one, and third-party trackers where it does not. Claude Opus 4.1 and Grok 4.6 are on Kaggle's list but return 404 from the proxy, so they are not here.

## What I found

### Everyone knows how clocks work

Fifteen of the 19 answered all 26 control questions correctly, and nobody scored below 23 of 26. Twelve got every awkward-offset question right, including Lord Howe Island's half-hour spring forward and the Chatham Islands at +13:45 in January. The southern hemisphere was nearly as clean. This is the part where the [Test of Time paper](https://arxiv.org/abs/2406.09170) found models scoring 74 to 90 percent on time-zone questions back in 2024 and attributed it to the amount of time-zone text on the internet. That reading holds. Time zones as a topic are learned.

Time zones as of a date are a different thing.

### Nobody knows about Alberta

Twenty of the 25 questions about the 2026 wave have an answer that changed this year. The other five are controls inside the family, Vancouver in July or Fort Nelson in November, where nothing changed. Twelve of the 19 got all five. Thirteen of the 19 got none of the 20 changed answers right, including Claude Opus 5, GPT-5.5, GPT-5.6 Terra and three of the five Geminis.

On the 20 changed questions, across 19 models, there were 18 correct answers. GPT-6 Astra produced 5 of them. Four are about British Columbia, with the right reason: "British Columbia adopted permanent UTC−07:00 time in March 2026, so Vancouver does not turn clocks back in autumn." The fifth is an Inuvik conversion with no reason given. The other 13 came from models that did not know, and not one of those 13 notes says that anything changed in 2026. Qwen said "Clocks do not change on 2026-11-01 as the fall back occurs on 2026-11-02." November 1 is the Sunday. Gemini 2.5 Pro said Inuvik's clocks do not change because "the Northwest Territories permanently observes Mountain Daylight Time (UTC-6) year-round", then put Inuvik on UTC-7 in the next question. I read every one of the thirteen. Not one model knew that Alberta, the Northwest Territories or Morocco had changed anything.

The Calgary offset question is the one I would put in front of a judge, because it cannot be right by accident. Calgary at noon on November 15, 2026 is -06:00. All 19 models said -07:00.

![How many of the 25 questions about the 2026 changes each model got right, from memory and with the tool](https://raw.githubusercontent.com/JonathanSolvesProblems/world-clock/main/results/wave.png)

### Dating the clocks

This is the chart the whole benchmark was built for. Each line is one model's agreement with each tzdata release since 2022, on the 46 answers that changed. The peak is the release the model's clock is dated to. Identical curves are drawn once and labelled with every model on them.

![Answers matching each tzdata release, per vendor](https://raw.githubusercontent.com/JonathanSolvesProblems/world-clock/main/results/ladder.png)

GPT-6 Astra is the cleanest result in the set. Its curve rises through every release since 2022, agrees with tzdata 2026b on 45 of the 46 changed answers, and falls off a cliff at 2026c. The one it disagrees on is that Inuvik conversion. tzdata 2026b was released on April 22, 2026, and carries British Columbia; the next release, 2026c, came on July 8. So the ladder says this clock stopped somewhere between those two dates. OpenAI says the model's cutoff is April 30, 2026. Those agree, and the ladder got there from nothing but clock questions.

GPT-5.5, GPT-5.6 Terra and Claude Opus 5 share one curve, and it is also a perfect 46 of 46, at 2026a. That is the last release before British Columbia. OpenAI's stated cutoffs for its two are December 2025 and February 2026, both consistent. Anthropic says Opus 5 was trained on data to May 2026, which should include a change that took effect on March 9. Its own note on Vancouver in December says why it does not: "On 2026-12-15 Vancouver is on Pacific Standard Time (UTC-8), since daylight saving ended on the first Sunday of November 2026 and British Columbia's permanent-DST legislation has not been brought into force." It knows the law. Its clock stopped before the law started.

Gemini 2.5 Pro, 3.1 Pro, 3.7 Flash and 3.8 Flash all date to tzdata 2025a, released January 15, 2025. Gemini 2.5 Pro from June 2025, Gemini 3.7 Flash from August 2026 and Gemini 3.8 Flash from September 2026 all peak there, and the two Flash curves never differ by more than one answer anywhere on the ladder. Only Flash-Lite sits elsewhere, at 2024a to 2024b with a blurry 39 of 46. Google's model card for 3.8 Flash gives a cutoff of March 2026 "for some domains" and January 2025 for the rest. The clock is one of the rest, and it has not moved in fifteen months of releases.

Claude Sonnet 5 dates to October 2022 and Claude Haiku 4.5 to somewhere between March and September 2022, against stated cutoffs of January 2026 and February 2025. These are not parsing accidents, I read the answers. Sonnet 5 says "Iran observed daylight saving time (UTC+4:30) during summer 2023 before abolishing DST later that year" (Iran abolished it in 2022), puts Cairo on +02:00 in July 2023 in a sentence that mentions Egypt's 2023 reintroduction of daylight saving and then ignores it, and says "Almaty has used the UTC+6 time zone year-round since 2024-03-01", which is the day Kazakhstan moved Almaty to +05:00. It scored 16 of 31 on the changes legislated between 2022 and 2025. GPT-6 Astra, GPT-5.5, GPT-5.6 Terra and Opus 5 scored 31 of 31.

The peak height matters as much as its position. A model at 46 of 46 has a sharp clock: everything before the peak right, everything after it wrong. A model at 34 of 46 has a blurry one, and the dating is a best fit rather than a fact. The table gives both numbers for every model.

How much of this is noise? I fixed the harness several times along the way, so 15 models ran the from-memory questions at least twice, 42 runs in all. The median model's score moved by 2 questions between runs, and the largest swing was 10 questions, Claude Haiku 4.5. The release its clock dates to stayed the same in 10 of the 15, and moved by one or two releases in the rest. Every run of every model put Calgary on -07:00.

### With the tool

Then I asked again with a tool on the table. `zone_clock(iana_zone, local_datetime)` reads tzdata 2026d and returns the offset in force. The system prompt says the tool exists and that the model may call it or answer without it. Nothing tells the model its knowledge might be out of date.

This half asks 46 of the 125 questions: every question about 2026, the three about Manitoba, and eighteen older ones as a control group. 43 of the 46 are graded. The reason it is a subset is money, which I get to below. 16 models finished it.

| Model | From memory (of 43) | With the tool (of 43) | Asked the tool | Overrode it | Asked about another zone only | Answer changed when restated |
|---|---|---|---|---|---|---|
| Claude Haiku 4.5 | 14 | 43 | 43 of 43 | 0 | 2 | 2 |
| Claude Opus 4.5 | 18 | 42 | 43 of 43 | 1 | 1 | 2 |
| Gemini 3.8 Flash | 21 | 42 | 43 of 43 | 0 | 1 | 0 |
| GPT-5.4 mini | 20 | 42 | 43 of 43 | 1 | 1 | 3 |
| GPT-5.6 Terra | 23 | 42 | 42 of 43 | 1 | 0 | 0 |
| Grok 4.20 Reasoning | 18 | 42 | 43 of 43 | 1 | 0 | 1 |
| Claude Opus 5 | 23 | 41 | 43 of 43 | 2 | 0 | 3 |
| Gemini 3.7 Flash | 21 | 39 | 43 of 43 | 3 | 1 | 2 |
| GPT-5.5 | 23 | 39 | 33 of 43 | 1 | 0 | 1 |
| Grok 4.20 | 21 | 38 | 43 of 43 | 4 | 1 | 4 |
| Gemma 4 31B | 18 | 36 | 43 of 43 | 5 | 4 | 4 |
| GLM-5 | 20 of 42 | 36 | 43 of 43 | 6 | 1 | 4 |
| Gemini 3.1 Pro | 22 | 35 | 41 of 43 | 7 | 1 | 7 |
| Claude Sonnet 5 | 17 | 34 | 40 of 43 | 6 | 2 | 6 |
| Gemini 3.5 Flash-Lite | 22 | 33 | 43 of 43 | 9 | 3 | 2 |
| Qwen3-Next 80B Thinking | 21 | 19 | 2 of 43 | 0 | 1 | 0 |

**Almost everyone checks.** Eleven of the 16 asked the tool on every one of the 43 questions. GPT-5.6 Terra asked on 42, Gemini 3.1 Pro on 41, Claude Sonnet 5 on 40 and GPT-5.5 on 33. Qwen asked on 2, answered the rest from memory, and scored 19, which is lower than the 21 it got without the tool.

**Checking mostly works.** Fourteen of the 16 got at least 34 of 43 with the tool, and nobody got more than 23 from memory. Claude Haiku 4.5, whose clock dated to 2022 in the memory half, is the only model that got all 43. It never once answered against the database.

**Checking is not believing.** Take the question this post opened with. With the database one call away, 8 of the 16 still said 11:00. Two of those eight wrote the correct offsets in the same sentence. GPT-5.6 Terra's note reads "Calgary used UTC−06:00 and Toronto used UTC−05:00." Its answer was 11:00.

Claude Opus 5 argued with the tool in so many words. On Calgary's offset it wrote "the tool reports -06:00 with abbreviation CST, which does not match Alberta's actual rules" before coming round to the tool's answer. On Casablanca in December it did not come round. It answered +01:00 and left this note: "the zone_clock lookup returned +00:00, which conflicts with this known rule". Gemini 3.5 Flash-Lite called the tool 3 times about Calgary's clocks on November 1, was told they do not change, and answered that they fall back. Across the 16 models there were 47 answers like that, where the model asked about the right place on the right date and then answered something else.

**Some of it is a second chance to be wrong.** Kaggle's SDK runs the tool loop, then sends a final message, "Now format your previous answer using the requested schema.", and the benchmark grades that restated answer. `analysis/tool_trace.py` compares the two, and the last column of the table counts the cases where they differ. In 28 cases the model's own words had the right answer and the restated one did not. Claude Sonnet 5 wrote "Per IANA tzdata 2026d, Vancouver is on permanent standard time (abbreviated MST, no DST) at -07:00 for this date", then restated the offset as -08:00. 13 answers went the other way and were fixed at that step. Gemini 3.7 Flash ran this task three times while I was fixing the harness and scored 42, 40 and 39.

**The failure I like best is Coyhaique.** Chile's Aysén region got its own zone, America/Coyhaique, in tzdata 2025b. A model whose clock stopped before that does not know the zone exists, so it asks the database about America/Santiago, gets a true answer about the wrong place, and reports it. 9 of the 16 missed the question, and only five asked about America/Coyhaique at all. Gemini 3.8 Flash: "Coyhaique in the Aysén Region follows official mainland Chile standard time (America/Santiago), which observes UTC-04:00 during the winter months." A lookup tool fixes what the model knows to look up.

**Why a subset, and who is missing.** Kaggle gives each account a model quota of $10 a day, and a tool loop is expensive because every round sends the whole conversation again. Gemini 3.8 Flash cost $0.16 for the 125 questions from memory and $0.99 for the same 125 with the tool. My first full tool lineup ran out of quota partway through, and the runs queued behind it failed on a 403 from the proxy. So the tool half is 46 questions. GPT-6 Astra is missing for a different reason: the API refuses function tools for that model unless reasoning is off, and refuses to switch its reasoning off, so Kaggle's SDK has no way to hand it a tool. GPT-5.6 Terra has the same rule and does allow reasoning off, so it ran this half that way. DeepSeek-R1 does not support tool calling at all.

### Manitoba, which the database caught up with

Manitoba announced on September 17 that it will not fall back on November 1. When I built the answer key no release had it, so its three questions were asked, recorded, and left out of the score. Then, on September 30, the tz maintainers shipped tzdata 2026e: "Manitoba moves to permanent -05 on 2026-10-31".

So I graded those three answers against 2026e. Winnipeg at noon on November 15 is -05:00, and 9 a.m. in Winnipeg is 9 a.m. in Toronto. All 19 models said -06:00, and all 19 said 10:00. Asked whether Winnipeg's clocks change on November 1, 18 said they fall back. Qwen said they do not, and it only got that right because it believes the fall-back is on November 2.

The benchmark ran before the database knew, and the database caught up a week later. The models will take a training run.

## What surprised me

Release date is not the clock. Gemini 3.8 Flash shipped on September 2, 2026 with its world clock on the same release as Gemini 2.5 Pro from June 2025: tzdata 2025a. Fifteen months of model releases, one clock.

Knowing about a law is not knowing its date. Opus 5 can tell you British Columbia passed a permanent daylight time law and still puts Vancouver on the wrong offset, because the fact it learned was "passed" and the fact that matters is "in force since March 9."

The models agree with each other more than with the world. On the Calgary to Toronto question, all 19 models gave the same wrong answer, with the same confidence, and most of them cited the same rule: daylight saving ends on the first Sunday in November. That rule was true in Alberta for 55 years. It stopped being true on June 18.

Checking is not believing. Fourteen of the 16 models that had the database asked it on at least 40 of the 43 questions, and eight of the 16 still told Calgary it was 11:00 in Toronto. Claude Opus 5 told the database it was wrong about Alberta.

## What I would measure next

Run the same 125 questions again after tzdata 2027a, without changing a line, and see which vendors' clocks moved. The answer key updates itself; the benchmark is designed to be re-run.

Tell the model the current date in the prompt and see whether any of them hedge. Not one of the 19 said "as of my training data" on a question about November 2026.

Add a web-search condition beside the tzdata tool. With a database one call away, nearly every model looked. The open question is whether a model goes looking when nothing on the table suggests it should.

Grade the model's own words as well as the restated answer, as two scores. The gap between them is a measurement of the harness, and I only found it by reading transcripts.

## Where to see it

- The benchmark on Kaggle: https://www.kaggle.com/benchmarks/jonathanandrei/world-clock
- Its two tasks: [from memory](https://www.kaggle.com/benchmarks/tasks/jonathanandrei/world-clock-from-memory) and [with the tzdata tool](https://www.kaggle.com/benchmarks/tasks/jonathanandrei/world-clock-tool-v2)
- Code, answer key, every result and both charts: https://github.com/JonathanSolvesProblems/world-clock

The repo has a script called `check_claims.py`. It reads the results and fails if any number in this post disagrees with them. It ran before this was published.
