# World Clock results

| Model | Condition | Graded | Accuracy | Clock dated to | Ladder agreement | Vendor says cutoff | Calgary falls back Nov 1? |
|---|---|---|---|---|---|---|---|
| google/gemini-3.1-pro-preview | memory | 100/122 | 82.0% | 2025a (2025-01-15) to 2025a (2025-01-15) | 45/46 | 2025-01 | yes (wrong) |
| google/gemini-3.7-flash | memory | 99/122 | 81.1% | 2025a (2025-01-15) to 2025a (2025-01-15) | 44/46 | 2026-03 | yes (wrong) |
| google/gemini-3.8-flash | memory | 99/122 | 81.1% | 2025a (2025-01-15) to 2025a (2025-01-15) | 44/46 | 2026-03 | yes (wrong) |
| google/gemini-2.5-pro | memory | 98/122 | 80.3% | 2025a (2025-01-15) to 2025a (2025-01-15) | 44/46 | 2025-01 | yes (wrong) |
| google/gemini-3.7-flash | tool | 118/120 | 98.3% | current (2026d) | 42/44 | 2026-03 | n/a |

## Accuracy by family

| Model | Condition | awkward_offset | control | legislated_2022_2025 | southern | wave_2026 |
|---|---|---|---|---|---|---|
| google/gemini-3.1-pro-preview | memory | 22/22 | 26/26 | 29/31 | 18/18 | 5/25 |
| google/gemini-3.7-flash | memory | 22/22 | 26/26 | 28/31 | 18/18 | 5/25 |
| google/gemini-3.8-flash | memory | 22/22 | 26/26 | 28/31 | 18/18 | 5/25 |
| google/gemini-2.5-pro | memory | 22/22 | 26/26 | 27/31 | 18/18 | 5/25 |
| google/gemini-3.7-flash | tool | 22/22 | 26/26 | 30/31 | 18/18 | 22/23 |

## Manitoba (announced, not yet in tzdata)

- google/gemini-3.1-pro-preview [memory] offset:winnipeg:2026-11-15:12:00: model {"utc_offset": "-06:00"}; tzdata 2026d {"utc_offset": "-06:00"}; official {"utc_offset": "-05:00"}. Note: Winnipeg observes Central Standard Time (UTC-06:00) after Daylight Saving Time ends on the first Sunday in November.
- google/gemini-3.1-pro-preview [memory] change_day:winnipeg:2026-11-01: model {"changes": true, "direction": "back"}; tzdata 2026d {"changes": true, "direction": "back"}; official {"changes": false, "direction": "none"}. Note: On November 1, 2026, clocks in Winnipeg fall back one hour as Daylight Saving Time ends.
- google/gemini-3.1-pro-preview [memory] convert:winnipeg:toronto:2026-11-15:09:00: model {"date": "2026-11-15", "time": "10:00"}; tzdata 2026d {"date": "2026-11-15", "time": "10:00"}; official {"date": "2026-11-15", "time": "09:00"}. Note: Winnipeg used UTC-6 and Toronto used UTC-5.
- google/gemini-3.7-flash [memory] offset:winnipeg:2026-11-15:12:00: model {"utc_offset": "-06:00"}; tzdata 2026d {"utc_offset": "-06:00"}; official {"utc_offset": "-05:00"}. Note: Winnipeg observes Central Standard Time (UTC-6) in mid-November following the end of Daylight Saving Time on the first Sunday of the month.
- google/gemini-3.7-flash [memory] change_day:winnipeg:2026-11-01: model {"changes": true, "direction": "back"}; tzdata 2026d {"changes": true, "direction": "back"}; official {"changes": false, "direction": "none"}. Note: On November 1, 2026, clocks in Winnipeg turn back one hour at 2:00 AM as Daylight Saving Time ends.
- google/gemini-3.7-flash [memory] convert:winnipeg:toronto:2026-11-15:09:00: model {"date": "2026-11-15", "time": "10:00"}; tzdata 2026d {"date": "2026-11-15", "time": "10:00"}; official {"date": "2026-11-15", "time": "09:00"}. Note: Winnipeg is in Central Standard Time (UTC-6) and Toronto is in Eastern Standard Time (UTC-5).
- google/gemini-3.8-flash [memory] offset:winnipeg:2026-11-15:12:00: model {"utc_offset": "-06:00"}; tzdata 2026d {"utc_offset": "-06:00"}; official {"utc_offset": "-05:00"}. Note: Central Standard Time is in effect in Winnipeg on November 15, 2026, following the end of daylight saving time on the first Sunday of November.
- google/gemini-3.8-flash [memory] change_day:winnipeg:2026-11-01: model {"changes": true, "direction": "back"}; tzdata 2026d {"changes": true, "direction": "back"}; official {"changes": false, "direction": "none"}. Note: Clocks in Winnipeg fall back by one hour at 2:00 AM on November 1, 2026, marking the end of daylight saving time.
- google/gemini-3.8-flash [memory] convert:winnipeg:toronto:2026-11-15:09:00: model {"date": "2026-11-15", "time": "10:00"}; tzdata 2026d {"date": "2026-11-15", "time": "10:00"}; official {"date": "2026-11-15", "time": "09:00"}. Note: Winnipeg is at UTC-6 (Central Standard Time) and Toronto is at UTC-5 (Eastern Standard Time).
- google/gemini-2.5-pro [memory] offset:winnipeg:2026-11-15:12:00: model {"utc_offset": "-06:00"}; tzdata 2026d {"utc_offset": "-06:00"}; official {"utc_offset": "-05:00"}. Note: On this date, Daylight Saving Time is not in effect in Manitoba, which reverts to Central Standard Time (UTC-6) on the first Sunday in November.
- google/gemini-2.5-pro [memory] change_day:winnipeg:2026-11-01: model {"changes": true, "direction": "back"}; tzdata 2026d {"changes": true, "direction": "back"}; official {"changes": false, "direction": "none"}. Note: On November 1, 2026, clocks in Winnipeg fall back one hour from 2:00 AM CDT to 1:00 AM CST as daylight saving time ends.
- google/gemini-2.5-pro [memory] convert:winnipeg:toronto:2026-11-15:09:00: model {"date": "2026-11-15", "time": "10:00"}; tzdata 2026d {"date": "2026-11-15", "time": "10:00"}; official {"date": "2026-11-15", "time": "09:00"}. Note: The calculation is based on Winnipeg using UTC-6 and Toronto using UTC-5 at that time.
- google/gemini-3.7-flash [tool] offset:winnipeg:2026-11-15:12:00: model {"utc_offset": "-06:00"}; tzdata 2026d {"utc_offset": "-06:00"}; official {"utc_offset": "-05:00"}. Note: Winnipeg observes Central Standard Time (UTC-6) as standard time following the end of daylight saving time on the first Sunday of November.
- google/gemini-3.7-flash [tool] change_day:winnipeg:2026-11-01: model {"changes": true, "direction": "back"}; tzdata 2026d {"changes": true, "direction": "back"}; official {"changes": false, "direction": "none"}. Note: Clocks in Winnipeg fall back by one hour on November 1, 2026, marking the end of Daylight Saving Time.
- google/gemini-3.7-flash [tool] convert:winnipeg:toronto:2026-11-15:09:00: model {"date": "2026-11-15", "time": "10:00"}; tzdata 2026d {"date": "2026-11-15", "time": "10:00"}; official {"date": "2026-11-15", "time": "09:00"}. Note: Winnipeg is observed at UTC-6 (CST) and Toronto is observed at UTC-5 (EST).
