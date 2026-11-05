# What the wrong answers say

From `analysis/error_kinds.py`, a test suggested by Arhan Canli on the DEV post. Every wrong answer on the 2022 to 2025 changes was read by hand; the labels are in the script.

- 26 of 153 wrong answers on the 2022 to 2025 changes name the real change.
- 46 ladder questions come from 16 places and 12 legal changes.
- Counted by legal change, 19 of 19 models land on the same releases.
- 19 of 19 peaks are won by one change or less, 10 by half a change or less.
- Wrong from memory and asked with the tool: 8 of 10 fixed where the note named the change, 23 of 35 where it did not. All 8 fixed had called the tool; the 2 missed had not.

| Model | Stated cutoff | Named, wrong date | Named, right date | Ladder | Without those questions | Without those jurisdictions | By legal change | Margin |
|---|---|---|---|---|---|---|---|---|
| GPT-6 Astra | 2026-04-30 | 0 | 0 | 2026b | 2026b | 2026b | 2026b | 1.0 |
| Claude Opus 5 | 2026-05 | 0 | 0 | 2025b to 2026a | 2025b to 2026a | 2025b to 2026a | 2025b to 2026a | 1.0 |
| GPT-5.5 | 2025-12-01 | 0 | 0 | 2025b to 2026a | 2025b to 2026a | 2025b to 2026a | 2025b to 2026a | 1.0 |
| GPT-5.6 Terra | 2026-02-16 | 0 | 0 | 2025b to 2026a | 2025b to 2026a | 2025b to 2026a | 2025b to 2026a | 1.0 |
| Gemini 2.5 Pro | 2025-01 | 0 | 1 | 2025a | 2025a | 2025a | 2025a | 0.33 |
| Gemini 3.7 Flash | 2026-03 | 0 | 2 | 2025a | 2025a | 2025a | 2025a | 1.0 |
| Gemini 3.8 Flash | 2026-03 | 0 | 0 | 2025a | 2025a | 2025a | 2025a | 1.0 |
| Gemini 3.1 Pro | 2025-01 | 0 | 2 | 2025a | 2025a | 2025a | 2025a | 0.33 |
| GLM-5 | not published | 2 | 1 | 2024a to 2024b | 2024a to 2024b | 2024a to 2025a | 2024a to 2024b | 0.67 |
| Gemini 3.5 Flash-Lite | not published | 1 | 1 | 2024a to 2024b | 2024a to 2024b | 2024a to 2024b | 2024a to 2024b | 1.0 |
| Gemma 4 31B | 2025-01 | 0 | 1 | 2024a to 2024b | 2024a to 2024b | 2024a to 2024b | 2024a to 2024b | 0.67 |
| Grok 4.20 Reasoning | 2025-09-01 | 0 | 1 | 2023a to 2023c | 2023a to 2023c | 2023a to 2023c | 2023a to 2023c | 0.33 |
| GPT-5.4 mini | 2025-08-31 | 0 | 0 | 2024a to 2024b | 2024a to 2024b | 2024a to 2024b | 2024a to 2024b | 0.33 |
| Claude Opus 4.5 | not published | 0 | 2 | 2022g | 2022g | 2022a to 2024b | 2022g | 0.33 |
| Claude Sonnet 5 | 2026-01 | 1 | 3 | 2022f | 2022f to 2023d | 2022f | 2022f | 0.33 |
| Qwen3-Next 80B Thinking | 2025-09-30 | 2 | 3 | 2022f | 2022f to 2022g | 2022e to 2022g | 2022f | 0.33 |
| DeepSeek-R1 | 2025-03-31 | 0 | 1 | 2022a | 2022a | 2022a | 2022a | 0.33 |
| Grok 4.20 | 2025-09-01 | 0 | 1 | 2022e | 2022e to 2024b | 2023a to 2024b | 2022e | 0.2 |
| Claude Haiku 4.5 | 2025-02 | 1 | 0 | 2022a to 2022d | 2022a to 2022d | 2022a to 2022d | 2022a to 2022d | 0.33 |

## The notes

- **Gemini 2.5 Pro**, `offset:nuuk:2024-07-15:12:00`, right date: "Greenland adopted UTC-02:00 year-round for Nuuk starting in March 2023, abolishing seasonal clock changes."
- **Gemini 3.7 Flash**, `offset:nuuk:2024-07-15:12:00`, right date: "Nuuk observes standard time UTC-2 year-round following Greenland's 2023 time zone reform." With the tool: right, 1 call(s).
- **Gemini 3.7 Flash**, `offset:ittoqqortoormiit:2024-07-15:12:00`, right date: "Ittoqqortoormiit changed its time zone to UTC-2 year-round on March 31, 2024, aligning with western Greenland."
- **Gemini 3.1 Pro**, `offset:chihuahua:2023-01-15:12:00`, right date: "Chihuahua City observed UTC-7 standard time on this date following the November 2022 amendment to Mexico's time zone law which reverted most of the state to the Pacific Time Zone."
- **Gemini 3.1 Pro**, `offset:ittoqqortoormiit:2024-07-15:12:00`, right date: "On March 31, 2024, Ittoqqortoormiit permanently changed its time zone to UTC-2 to align with the rest of Greenland."
- **GLM-5**, `offset:chihuahua:2023-01-15:12:00`, right date: "Chihuahua City is located in the Mexican Pacific Zone (Zona Pacífico), which observes Mountain Standard Time (UTC-7) year-round following the elimination of Daylight Saving Time in most of Mexico by decree in late 2022."
- **GLM-5**, `offset:cairo:2024-07-15:12:00`, wrong date: "Egypt cancelled daylight saving time for 2024, remaining on Eastern European Standard Time year-round."
- **GLM-5**, `offset:asuncion:2025-06-15:12:00`, wrong date: "Paraguay abolished Daylight Saving Time in March 2024, establishing permanent standard time." With the tool: right, 1 call(s).
- **Gemini 3.5 Flash-Lite**, `offset:chihuahua:2023-01-15:12:00`, right date: "On January 15, 2023, Chihuahua observed standard time at UTC-07:00, following the federal time zone changes enacted in late 2022 that abolished daylight saving time for most of the state."
- **Gemini 3.5 Flash-Lite**, `offset:nuuk:2024-07-15:12:00`, wrong date: "Nuuk, Greenland adopted UTC-2 year-round starting in November 2023, so standard daylight saving rules no longer apply." With the tool: right, 1 call(s).
- **Gemma 4 31B**, `offset:chihuahua:2023-01-15:12:00`, right date: "Chihuahua follows Mountain Standard Time (MST) and abolished daylight saving time in 2022."
- **Grok 4.20 Reasoning**, `offset:chihuahua:2023-01-15:12:00`, right date: "Chihuahua City follows Mexico's 2022 DST elimination rule for non-border areas, remaining on fixed Mountain Standard Time all year."
- **Claude Opus 4.5**, `offset:chihuahua:2023-01-15:12:00`, right date: "Chihuahua, Mexico observes Mountain Standard Time (UTC-07:00) during winter months, as Mexico ended daylight saving time in most of the country in 2022 but Chihuahua being a northern border state near the US continued observing standard time in January."
- **Claude Opus 4.5**, `offset:nuuk:2024-07-15:12:00`, right date: "Greenland abolished daylight saving time in 2023 and moved permanently to UTC-2, so Nuuk observes year-round Western Greenland Time at UTC-2." With the tool: right, 1 call(s).
- **Claude Sonnet 5**, `offset:tehran:2023-07-15:12:00`, wrong date: "Iran observed daylight saving time (UTC+4:30) during summer 2023 before abolishing DST later that year." With the tool: right, 1 call(s).
- **Claude Sonnet 5**, `offset:cairo:2023-07-15:12:00`, right date: "Egypt abolished DST and has remained on Eastern European Time (UTC+2) year-round since 2014 (with a brief 2023 reinstatement of DST starting in late April, but offset remains +02:00 as Egypt does not observe DST in July 2023 per standard time)." With the tool: right, 1 call(s).
- **Claude Sonnet 5**, `offset:almaty:2024-07-15:12:00`, right date: "Kazakhstan does not observe daylight saving time, and Almaty has used the UTC+6 time zone year-round since 2024-03-01." With the tool: right, 1 call(s).
- **Claude Sonnet 5**, `offset:almaty:2024-03-05:12:00`, right date: "Kazakhstan does not observe daylight saving time, and Almaty has used UTC+6 since 2024, as the country shifted to a two-zone system (UTC+5 and UTC+6) in March 2024."
- **Qwen3-Next 80B Thinking**, `offset:tehran:2023-07-15:12:00`, right date: "Iran permanently observes daylight saving time (UTC+4:30) since 2022, with no seasonal changes." With the tool: wrong, 0 call(s).
- **Qwen3-Next 80B Thinking**, `offset:chihuahua:2023-01-15:12:00`, right date: "Mexico eliminated daylight saving time nationwide effective October 30, 2022, so Chihuahua City remains on UTC-7 year-round."
- **Qwen3-Next 80B Thinking**, `offset:nuuk:2024-01-15:12:00`, right date: "Greenland abolished daylight saving time in 2023, so Nuuk observes UTC-3 year-round"
- **Qwen3-Next 80B Thinking**, `offset:asuncion:2025-06-15:12:00`, wrong date: "Paraguay abolished daylight saving time in 2022, remaining on UTC-4 year-round" With the tool: wrong, 0 call(s).
- **Qwen3-Next 80B Thinking**, `offset:asuncion:2025-03-25:12:00`, wrong date: "Paraguay abolished daylight saving time in 2023, so it consistently observes UTC−4 year-round."
- **DeepSeek-R1**, `offset:chihuahua:2023-01-15:12:00`, right date: "Applied Mexico's 2022 time zone reform: Chihuahua City (non-border) uses Mountain Standard Time (UTC-7) year-round without daylight saving."
- **Grok 4.20**, `offset:nuuk:2024-07-15:12:00`, right date: "Greenland observes daylight saving time in summer, so on 2024-07-15 Nuuk was using UTC-02:00 under the post-2023 rules that keep it on DST from March to November." With the tool: right, 1 call(s).
- **Claude Haiku 4.5**, `offset:nuuk:2024-01-15:12:00`, wrong date: "Greenland observes West Greenland Time (WGT), which is UTC-3, year-round as daylight saving time was abolished in Greenland."
