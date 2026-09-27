# World Clock results

| Model | Condition | Graded | Accuracy | Clock dated to | Ladder agreement | Vendor says cutoff | Calgary falls back Nov 1? |
|---|---|---|---|---|---|---|---|
| google/gemini-3.1-pro-preview | memory | 8/8 | 100.0% | 2022b to current | 1/1 | 2025-01 | n/a |
| openai/gpt-oss-120b | memory | 1/1 | 100.0% | n/a | n/a | 2024-06-30 | n/a |
| qwen/qwen3-next-80b-a3b-thinking | memory | 1/1 | 100.0% | n/a | n/a | 2025-09-30 | n/a |
| openai/gpt-5.4-mini-2026-03-17 | memory | 21/23 | 91.3% | 2024a (2024-02-01) to 2026a (2026-03-01) | 4/4 | 2025-08-31 | n/a |
| openai/gpt-5.6-terra | memory | 13/16 | 81.2% | 2025b (2025-03-22) to 2026b (2026-04-22) | 7/7 | 2026-02-16 | n/a |
| google/gemini-3.7-flash | memory | 99/122 | 81.1% | 2025a (2025-01-15) to 2025a (2025-01-15) | 44/46 | 2026-03 | yes (wrong) |
| anthropic/claude-sonnet-5@default | memory | 14/18 | 77.8% | 2023d (2023-12-21) to 2023d (2023-12-21) | 6/6 | 2026-01 | n/a |
| google/gemini-3.8-flash | memory | 60/83 | 72.3% | 2025a (2025-01-15) to 2025a (2025-01-15) | 40/42 | 2026-03 | yes (wrong) |
| google/gemini-3.5-flash-lite | memory | 40/59 | 67.8% | 2024a (2024-02-01) to 2024b (2024-09-04) | 24/31 | not published | n/a |
| anthropic/claude-haiku-4-5@20251001 | memory | 10/24 | 41.7% | 2022e (2022-10-11) to 2022e (2022-10-11) | 15/18 | 2025-02 | yes (wrong) |
| deepseek-ai/deepseek-r1-0528 | memory | 1/3 | 33.3% | 2022a (2022-03-15) to 2022d (2022-09-23) | 2/2 | 2025-03-31 | n/a |
| anthropic/claude-opus-4-1@20250805 | memory | 0/0 | None% | n/a | n/a | 2025-03 | n/a |
| anthropic/claude-opus-5@default | memory | 0/0 | None% | n/a | n/a | 2026-05 | n/a |
| openai/gpt-5.5-2026-04-23 | memory | 0/0 | None% | n/a | n/a | 2025-12-01 | n/a |
| openai/gpt-6-astra | memory | 0/0 | None% | n/a | n/a | 2026-04-30 | n/a |
| xai/grok-4.6 | memory | 0/0 | None% | n/a | n/a | 2026-02-01 | n/a |

## Accuracy by family

| Model | Condition | awkward_offset | control | legislated_2022_2025 | southern | wave_2026 |
|---|---|---|---|---|---|---|
| google/gemini-3.1-pro-preview | memory | 1/1 | 6/6 | 1/1 |  |  |
| openai/gpt-oss-120b | memory |  | 1/1 |  |  |  |
| qwen/qwen3-next-80b-a3b-thinking | memory |  | 1/1 |  |  |  |
| openai/gpt-5.4-mini-2026-03-17 | memory | 1/1 | 16/16 | 2/2 | 2/2 | 0/2 |
| openai/gpt-5.6-terra | memory | 4/4 | 2/2 | 4/4 | 2/2 | 1/4 |
| google/gemini-3.7-flash | memory | 22/22 | 26/26 | 28/31 | 18/18 | 5/25 |
| anthropic/claude-sonnet-5@default | memory | 2/2 | 8/8 | 3/5 |  | 1/3 |
| google/gemini-3.8-flash | memory | 2/2 | 18/18 | 23/26 | 12/12 | 5/25 |
| google/gemini-3.5-flash-lite | memory | 9/9 | 5/6 | 15/21 | 5/5 | 6/18 |
| anthropic/claude-haiku-4-5@20251001 | memory | 2/2 |  | 5/10 |  | 3/12 |
| deepseek-ai/deepseek-r1-0528 | memory |  | 1/1 | 0/1 |  | 0/1 |
| anthropic/claude-opus-4-1@20250805 | memory |  |  |  |  |  |
| anthropic/claude-opus-5@default | memory |  |  |  |  |  |
| openai/gpt-5.5-2026-04-23 | memory |  |  |  |  |  |
| openai/gpt-6-astra | memory |  |  |  |  |  |
| xai/grok-4.6 | memory |  |  |  |  |  |

## Manitoba (announced, not yet in tzdata)

- google/gemini-3.7-flash [memory] offset:winnipeg:2026-11-15:12:00: model {"utc_offset": "-06:00"}; tzdata 2026d {"utc_offset": "-06:00"}; official {"utc_offset": "-05:00"}. Note: Winnipeg observes Central Standard Time (UTC-06:00) during standard time, which began on the first Sunday of November.
- google/gemini-3.7-flash [memory] change_day:winnipeg:2026-11-01: model {"changes": true, "direction": "back"}; tzdata 2026d {"changes": true, "direction": "back"}; official {"changes": false, "direction": "none"}. Note: Clocks in Winnipeg fall back by one hour at 2:00 AM on November 1, 2026, ending daylight saving time.
- google/gemini-3.7-flash [memory] convert:winnipeg:toronto:2026-11-15:09:00: model {"date": "2026-11-15", "time": "10:00"}; tzdata 2026d {"date": "2026-11-15", "time": "10:00"}; official {"date": "2026-11-15", "time": "09:00"}. Note: Winnipeg is on Central Standard Time (UTC-6) and Toronto is on Eastern Standard Time (UTC-5).
- google/gemini-3.8-flash [memory] offset:winnipeg:2026-11-15:12:00: model {"utc_offset": "-06:00"}; tzdata 2026d {"utc_offset": "-06:00"}; official {"utc_offset": "-05:00"}. Note: Winnipeg observes Central Standard Time (UTC-6) after daylight saving time ends on the first Sunday of November.
- google/gemini-3.8-flash [memory] change_day:winnipeg:2026-11-01: model {"changes": true, "direction": "back"}; tzdata 2026d {"changes": true, "direction": "back"}; official {"changes": false, "direction": "none"}. Note: Clocks in Winnipeg fall back by one hour at 2:00 a.m. on November 1, 2026, marking the end of daylight saving time.
- google/gemini-3.8-flash [memory] convert:winnipeg:toronto:2026-11-15:09:00: model {"date": "2026-11-15", "time": "10:00"}; tzdata 2026d {"date": "2026-11-15", "time": "10:00"}; official {"date": "2026-11-15", "time": "09:00"}. Note: Winnipeg is on Central Standard Time (UTC-6) and Toronto is on Eastern Standard Time (UTC-5).
- google/gemini-3.5-flash-lite [memory] offset:winnipeg:2026-11-15:12:00: model {"utc_offset": "-06:00"}; tzdata 2026d {"utc_offset": "-06:00"}; official {"utc_offset": "-05:00"}. Note: Central Standard Time is in effect in Winnipeg on November 15, 2026, as daylight saving time ended on the first Sunday of the month.
- google/gemini-3.5-flash-lite [memory] change_day:winnipeg:2026-11-01: model {"changes": true, "direction": "back"}; tzdata 2026d {"changes": true, "direction": "back"}; official {"changes": false, "direction": "none"}. Note: Clocks in Winnipeg, Manitoba, are set backward one hour from 02:00 to 01:00 local standard time on November 1, 2026, as Daylight Saving Time ends.
- google/gemini-3.5-flash-lite [memory] convert:winnipeg:toronto:2026-11-15:09:00: model {"date": "2026-11-15", "time": "10:00"}; tzdata 2026d {"date": "2026-11-15", "time": "10:00"}; official {"date": "2026-11-15", "time": "09:00"}. Note: Winnipeg uses Central Standard Time with a UTC offset of -6 hours, while Toronto uses Eastern Standard Time with a UTC offset of -5 hours.
- anthropic/claude-haiku-4-5@20251001 [memory] convert:winnipeg:toronto:2026-11-15:09:00: model {"date": "2026-11-15", "time": "10:00"}; tzdata 2026d {"date": "2026-11-15", "time": "10:00"}; official {"date": "2026-11-15", "time": "09:00"}. Note: Winnipeg is UTC-6 (CST) and Toronto is UTC-5 (EST) on this date, so Toronto is 1 hour ahead.
