# World Clock results

| Model | Condition | Graded | Accuracy | Clock dated to | Ladder agreement |
|---|---|---|---|---|---|
| google/gemini-3.7-flash | memory | 15/17 | 88.2% | 2022e (2022-10-11) to 2026a (2026-03-01) | 4/4 |

## Accuracy by family

| Model | Condition | awkward_offset | control | legislated_2022_2025 | southern | wave_2026 |
|---|---|---|---|---|---|---|
| google/gemini-3.7-flash | memory | 4/4 | 4/4 | 3/3 | 3/3 | 1/3 |

## Manitoba (announced, not yet in tzdata)

- google/gemini-3.7-flash [memory] offset:winnipeg:2026-11-15:12:00: model {"utc_offset": "-06:00"}; tzdata 2026d {"utc_offset": "-06:00"}; official {"utc_offset": "-05:00"}. Note: Winnipeg observes Central Standard Time (UTC-06:00) after Daylight Saving Time ends on the first Sunday in November.
- google/gemini-3.7-flash [memory] change_day:winnipeg:2026-11-01: model {"changes": true, "direction": "back"}; tzdata 2026d {"changes": true, "direction": "back"}; official {"changes": false, "direction": "none"}. Note: On November 1, 2026, clocks in Winnipeg fall back by one hour at 2:00 AM local time to return to Central Standard Time.
- google/gemini-3.7-flash [memory] convert:winnipeg:toronto:2026-11-15:09:00: model {"date": "2026-11-15", "time": "10:00"}; tzdata 2026d {"date": "2026-11-15", "time": "10:00"}; official {"date": "2026-11-15", "time": "09:00"}. Note: Winnipeg was on Central Standard Time (UTC-6) and Toronto was on Eastern Standard Time (UTC-5).
