
### change_day:calgary:2026-11-01
ok claude-haiku-4-5             {"changes": false, "direction": "none"}  Calgary observes daylight saving time, but the clock change in 2026 occurs on October 25th, not November 1st.
ok claude-opus-4-5              {"changes": false, "direction": "none"}  The clocks in Calgary do not change on 2026-11-01; the fall-back transition occurs on 2026-11-08, the first Sunday of November.
ok gpt-5.6-terra                {"changes": false, "direction": "none"}  Clocks in Calgary do not change during the local calendar day of 2026-11-01.
ok gemini-3.8-flash             {"changes": false, "direction": "none"}  Clocks in Calgary do not change on November 1, 2026, as the local offset remains at UTC-6.
ok gpt-5.4-mini-2026-03-17      {"changes": false, "direction": "none"}  Calgary does not change clocks during the local calendar day of 2026-11-01; it remains on standard time all day.
ok grok-4.20-0309-reasoning     {"changes": false, "direction": "none"}  The clocks in Calgary do not change on 2026-11-01.
ok claude-opus-5                {"changes": false, "direction": "none"}  Calgary stays on UTC-6 all day on 2026-11-01 
instead of falling back 
the zone simply switches its label from MDT to CST at that point, so clocks are not adjusted.
X  gpt-5.5-2026-04-23           {"changes": true, "direction": "back"}   Calgary is scheduled to end daylight saving time on 2026-11-01, with clocks falling back one hour at 02:00 local time.
ok gemini-3.7-flash             {"changes": false, "direction": "none"}  Clocks in Calgary do not change on November 1, 2026, as the local time remains at UTC-6 throughout the day.
ok grok-4.20-0309-non-reasoning {"changes": false, "direction": "none"}  Clocks in Calgary do not change on 2026-11-01.
ok glm-5                        {"changes": false, "direction": "none"}  The clocks in Calgary remain on Mountain Standard Time (CST, UTC-7) throughout November 1, 2026, with no daylight saving transition occurring on that date.
ok gemma-4-31b                  {"changes": false, "direction": "none"}  The clocks in Calgary, Alberta, do not change on November 1, 2026.
ok gemini-3.1-pro-preview       {"changes": false, "direction": "none"}  Although the time zone abbreviation changes from MDT to CST during the day, the UTC offset remains -06:00 and the clocks do not change.
ok claude-sonnet-5              {"changes": false, "direction": "none"}  Calgary already switched from MDT to MST on November 1, 2026 at 2:00 a.m., so no clock change occurs during that calendar day itself since it starts and ends at UTC-06:00.
X  gemini-3.5-flash-lite        {"changes": true, "direction": "back"}   Clocks in Calgary fall back by one hour on November 1, 2026, at 2:00 AM local time, marking the end of Daylight Saving Time.
X  qwen3-next-80b-a3b-thinking  {"changes": true, "direction": "back"}   Clocks fall back one hour at 2:00 AM local time on this date as daylight saving time ends in Alberta.

### offset:calgary:2026-11-15:12:00
ok claude-haiku-4-5             {"utc_offset": "-06:00"}                 Calgary observes Mountain Standard Time (MST) during November, which is UTC-6, as daylight saving time ends in early November.
ok claude-opus-4-5              {"utc_offset": "-06:00"}                 Alberta adopted permanent Mountain Standard Time (MST) year-round, so on 2026-11-15 at 12:00 local time the offset is UTC-06:00 without any daylight saving time in effect.
ok gpt-5.6-terra                {"utc_offset": "-06:00"}                 Calgary follows Mountain Standard Time (UTC−06:00) after daylight saving time ends on the first Sunday in November.
ok gemini-3.8-flash             {"utc_offset": "-06:00"}                 Calgary observes year-round UTC-6 (Central Standard Time) according to the America/Edmonton time zone rules.
ok gpt-5.4-mini-2026-03-17      {"utc_offset": "-06:00"}                 Calgary uses America/Edmonton and on 2026-11-15 standard time (CST, no DST) applies.
ok grok-4.20-0309-reasoning     {"utc_offset": "-06:00"}                 The IANA time zone America/Edmonton rule in 2026d specifies CST without DST on 2026-11-15.
ok claude-opus-5                {"utc_offset": "-06:00"}                 Per IANA tzdata 2026d for America/Edmonton, Alberta no longer observes seasonal clock changes and is on a fixed -06:00 offset (labelled CST, equivalent to year-round Mountain Daylight Time), so no fall-back applied before 2026-11-15.
ok gpt-5.5-2026-04-23           {"utc_offset": "-06:00"}                 I applied the IANA America/Edmonton rule in effect on 2026-11-15, when Calgary is on standard time with abbreviation CST and no daylight saving transition that day.
ok gemini-3.7-flash             {"utc_offset": "-06:00"}                 Calgary observes standard time at UTC-06:00 (CST) under the America/Edmonton time zone rules on November 15, 2026.
X  grok-4.20-0309-non-reasoning {"utc_offset": "-07:00"}                 Standard time (MST) is in effect on 2026-11-15 with no DST or clock change that day.
ok glm-5                        {"utc_offset": "-06:00"}                 The rule applied is the IANA time zone database rule for America/Edmonton, which shows that Calgary observes UTC-06:00 as Central Standard Time (CST) on this date, with daylight saving time not in effect.
X  gemma-4-31b                  {"utc_offset": "-07:00"}                 Calgary observes Mountain Standard Time (MST) on November 15, 2026.
X  gemini-3.1-pro-preview       {"utc_offset": "-07:00"}                 Calgary is in the Mountain Time Zone and observes Mountain Standard Time (UTC-7) in November, as daylight saving time ends on the first Sunday of November.
X  claude-sonnet-5              {"utc_offset": "-07:00"}                 Daylight saving time ended on 2026-11-01, so Calgary (America/Edmonton time zone) is on Mountain Standard Time (MST) on 2026-11-15.
X  gemini-3.5-flash-lite        {"utc_offset": "-07:00"}                 Calgary observes Mountain Standard Time (UTC-7) on November 15, 2026, as Daylight Saving Time ended on the first Sunday of November.
ok qwen3-next-80b-a3b-thinking  {"utc_offset": "-06:00"}                 Applying the IANA time zone database (2026d), which indicates that on 2026-11-15, Calgary's time zone has a UTC offset of -06:00 with no daylight saving time active.

### offset:vancouver:2026-12-15:12:00
ok claude-haiku-4-5             {"utc_offset": "-07:00"}                 Vancouver observes Mountain Standard Time (MST) in mid-December, which is UTC-7:00.
ok claude-opus-4-5              {"utc_offset": "-07:00"}                 British Columbia has permanently adopted year-round daylight saving time (Pacific Daylight Time, now called Mountain Standard Time), resulting in a fixed UTC offset of -07:00 without seasonal clock changes.
ok gpt-5.6-terra                {"utc_offset": "-07:00"}                 British Columbia’s permanent Pacific time rule keeps Vancouver on Mountain Standard Time (UTC−07:00) in December 2026.
ok gemini-3.8-flash             {"utc_offset": "-07:00"}                 Vancouver observes year-round Mountain Standard Time (UTC-7) under the updated time zone rules.
ok gpt-5.4-mini-2026-03-17      {"utc_offset": "-07:00"}                 Applied the America/Vancouver time zone rule in effect on 2026-12-15, which is standard time (MST) with no clock change that day.
ok grok-4.20-0309-reasoning     {"utc_offset": "-07:00"}                 The MST standard time rule from the 2026d tzdata is in effect for America/Vancouver on this date.
ok claude-opus-5                {"utc_offset": "-07:00"}                 Per tzdata 2026d, Vancouver observes permanent Pacific daylight time (equivalent to MST, UTC-7) year-round, so no winter switch to -08:00 occurs.
X  gpt-5.5-2026-04-23           {"utc_offset": "-08:00"}                 Vancouver observes Pacific Standard Time in mid-December, after daylight saving time has ended, so the applicable offset is UTC−08:00.
ok gemini-3.7-flash             {"utc_offset": "-07:00"}                 Vancouver observes Mountain Standard Time (UTC-07:00) following the adoption of year-round standard time.
X  grok-4.20-0309-non-reasoning {"utc_offset": "-08:00"}                 Standard time (PST) is in effect on 2026-12-15 in Vancouver with no DST or clock change.
X  glm-5                        {"utc_offset": "-08:00"}                 I applied the Pacific Time Zone rule for Vancouver, British Columbia, which uses Pacific Standard Time (UTC-8) during winter months when daylight saving time is not in effect.
ok gemma-4-31b                  {"utc_offset": "-07:00"}                 Pacific Standard Time is in effect in Vancouver on December 15, 2026.
ok gemini-3.1-pro-preview       {"utc_offset": "-07:00"}                 The offset is based on the provided 2026d IANA time zone database release, which indicates Vancouver has switched to permanent UTC-07:00.
ok claude-sonnet-5              {"utc_offset": "-07:00"}                 According to the IANA tzdata for America/Vancouver, standard time (labeled MST in this dataset) with a UTC offset of -07:00 is in effect on 2026-12-15, as daylight saving time is not observed on that date.
X  gemini-3.5-flash-lite        {"utc_offset": "-08:00"}                 Vancouver observes Pacific Standard Time (PST), which is UTC-8, during the month of December as daylight saving time is not in effect.
X  qwen3-next-80b-a3b-thinking  {"utc_offset": "-08:00"}                 Vancouver observes Pacific Standard Time (UTC-8) in winter, as Daylight Saving Time ends on the first Sunday inNovember and reverts to standard time.

### offset:casablanca:2026-10-15:12:00
ok claude-haiku-4-5             {"utc_offset": "+00:00"}                 Morocco observes UTC+0 year-round without daylight saving time.
ok claude-opus-4-5              {"utc_offset": "+00:00"}                 Morocco observes Western European Time (WET) with UTC+00:00 as its standard time, and on 2026-10-15 the country is in its standard time period.
ok gpt-5.6-terra                {"utc_offset": "+00:00"}                 Morocco’s annual Ramadan time-change rule keeps Casablanca on UTC+00:00 on 2026-10-15.
ok gemini-3.8-flash             {"utc_offset": "+00:00"}                 According to the IANA time zone database (tzdata 2026d), Casablanca observes UTC+00:00 standard time following the transition on September 20, 2026.
ok gpt-5.4-mini-2026-03-17      {"utc_offset": "+00:00"}                 I applied the Africa/Casablanca rule from tzdata 2026d, which shows no clock change on 2026-10-15 and an offset of UTC+00:00 at 12:00 local time.
ok grok-4.20-0309-reasoning     {"utc_offset": "+00:00"}                 Standard time rule for Africa/Casablanca with no DST in effect.
ok claude-opus-5                {"utc_offset": "+00:00"}                 Morocco stays on permanent +01:00 except during Ramadan, when clocks fall back to +00:00; in 2026 the Ramadan exemption ran from 2026-09-20 until clocks returned to +01:00 in mid-February 2027, so 15 October 2026 was at +00:00.
ok gpt-5.5-2026-04-23           {"utc_offset": "+00:00"}                 I applied the Africa/Casablanca rule in effect on 2026-10-15, which has Morocco on UTC+00:00 at that local time.
ok gemini-3.7-flash             {"utc_offset": "+00:00"}                 In 2026, Casablanca observes UTC+00:00 during the winter/Ramadan-related adjustment schedule as defined in standard time database rules for Morocco.
ok grok-4.20-0309-non-reasoning {"utc_offset": "+00:00"}                 Applied the Africa/Casablanca IANA zone rule showing standard time (no DST) with zero offset on 2026-10-15.
ok glm-5                        {"utc_offset": "+00:00"}                 Morocco applies standard time (+00:00) during this period following its daylight saving time rules.
ok gemma-4-31b                  {"utc_offset": "+00:00"}                 Morocco typically observes UTC+1, but reverts to UTC+0 during the month of Ramadan.
X  gemini-3.1-pro-preview       {"utc_offset": "+01:00"}                 Morocco observes UTC+01:00 year-round except for a temporary suspension during the month of Ramadan, which does not fall in October.
ok claude-sonnet-5              {"utc_offset": "+00:00"}                 Morocco observes permanent daylight saving time (+01:00) year-round but suspends it during Ramadan, and October 15, 2026 falls outside Ramadan under the standard +01:00 rule as reflected by the IANA database, which reports +00:00 for this specific date due to the current Casablanca DST schedule.
ok gemini-3.5-flash-lite        {"utc_offset": "+00:00"}                 Morocco observes Western European Time (UTC+0) during standard time and typically suspends daylight saving time during the holy month of Ramadan, but on October 15, 2026, the standard offset of +00:00 is in effect.
X  qwen3-next-80b-a3b-thinking  {"utc_offset": "+01:00"}                 Morocco abolished daylight saving time in 2019 and observes UTC+1 year-round

### change_day:casablanca:2026-09-20
ok claude-haiku-4-5             {"changes": true, "direction": "back"}   Clocks in Casablanca fall back from UTC+01:00 to UTC+00:00 on 2026-09-20.
ok claude-opus-4-5              {"changes": true, "direction": "back"}   On 2026-09-20, clocks in Casablanca fall back from UTC+01:00 to UTC+00:00 as Morocco ends its daylight saving time period.
ok gpt-5.6-terra                {"changes": true, "direction": "back"}   Clocks in Casablanca fall back by one hour during the local calendar day of 2026-09-20.
ok gemini-3.8-flash             {"changes": true, "direction": "back"}   Clocks in Casablanca turn back by one hour on September 20, 2026, shifting from UTC+1 to UTC+0.
ok gpt-5.4-mini-2026-03-17      {"changes": true, "direction": "back"}   Casablanca changes clocks during the local day of 2026-09-20, moving back from UTC+01:00 to UTC+00:00.
ok grok-4.20-0309-reasoning     {"changes": true, "direction": "back"}   Clocks in Casablanca change from UTC+01:00 to UTC+00:00 during 2026-09-20.
ok claude-opus-5                {"changes": true, "direction": "back"}   Morocco returns to its Ramadan-period time on 2026-09-20, with clocks falling back one hour at 03:00 local (+01:00) to 02:00 (+00:00).
ok gpt-5.5-2026-04-23           {"changes": true, "direction": "back"}   On 2026-09-20 in Casablanca, Morocco, clocks change during the local day by falling back from UTC+01:00 to UTC+00:00.
ok gemini-3.7-flash             {"changes": true, "direction": "back"}   Clocks in Casablanca fall back by one hour from UTC+1 to UTC+0 on September 20, 2026.
ok grok-4.20-0309-non-reasoning {"changes": true, "direction": "back"}   Clocks in Casablanca fall back from +01:00 to +00:00 at 03:00 on 2026-09-20.
ok glm-5                        {"changes": true, "direction": "back"}   The clocks in Casablanca fall back by one hour from UTC+1 to UTC+0 during 2026-09-20, marking the end of daylight saving time.
ok gemma-4-31b                  {"changes": true, "direction": "back"}   The clocks in Casablanca move back one hour on September 20, 2026.
ok gemini-3.1-pro-preview       {"changes": true, "direction": "back"}   The clocks in Casablanca fall back from UTC+1 to UTC+0 on this day.
ok claude-sonnet-5              {"changes": true, "direction": "back"}   On 2026-09-20 Morocco ends its permanent DST-like +01:00 offset for the Ramadan pause, shifting clocks back to +00:00, i.e., falling back one hour.
ok gemini-3.5-flash-lite        {"changes": true, "direction": "back"}   Clocks in Casablanca change by falling back on September 20, 2026, as Morocco ends daylight saving time / summer time.
X  qwen3-next-80b-a3b-thinking  {"changes": false, "direction": "none"}   Casablanca abolished daylight saving time in 2019 and remains on UTC+1 year-round.

### offset:coyhaique:2025-07-15:12:00
ok claude-haiku-4-5             {"utc_offset": "-03:00"}                 Standard time in Chile (Zona Sur), which observes -03:00 year-round as of 2025.
ok claude-opus-4-5              {"utc_offset": "-03:00"}                 Coyhaique in the Aysén Region uses the America/Punta_Arenas time zone, which observes UTC-03:00 year-round with no daylight saving time.
ok gpt-5.6-terra                {"utc_offset": "-03:00"}                 I applied the Aysén Region rule that Coyhaique remained on UTC−03:00 year-round in 2025.
X  gemini-3.8-flash             {"utc_offset": "-04:00"}                 Coyhaique in the Aysén Region follows official mainland Chile standard time (America/Santiago), which observes UTC-04:00 during the winter months.
ok gpt-5.4-mini-2026-03-17      {"utc_offset": "-03:00"}                 Applied the America/Coyhaique time zone rule from tzdata for 2025-07-15, when standard time offset -03:00 is in effect and no clock change occurs that day.
ok grok-4.20-0309-reasoning     {"utc_offset": "-03:00"}                 Standard time rule for America/Coyhaique (UTC-3, no DST) applies on 2025-07-15.
ok claude-opus-5                {"utc_offset": "-03:00"}                 Aysén Region uses the America/Coyhaique zone, which since 2025 stays permanently at UTC-03:00 year-round instead of switching to UTC-04:00 in winter like the rest of mainland Chile.
ok gpt-5.5-2026-04-23           {"utc_offset": "-03:00"}                 Applied the America/Coyhaique rule in force for Aysén Region, which remains on UTC-03:00 with no clock change on 2025-07-15.
X  gemini-3.7-flash             {"utc_offset": "-04:00"}                 Coyhaique observes standard mainland Chile time (America/Santiago), which is UTC-04:00 during winter standard time in July.
X  grok-4.20-0309-non-reasoning {"utc_offset": "-04:00"}                 Chile Standard Time (no DST in winter) is in effect on 2025-07-15 in Coyhaique.
X  glm-5                        {"utc_offset": "-04:00"}                 I applied the IANA time zone database rule for America/Santiago (which covers Coyhaique, Aysén Region), where Chile has used permanent UTC-4 standard time year-round since discontinuing seasonal DST changes.
X  gemma-4-31b                  {"utc_offset": "-04:00"}                 Coyhaique follows the continental Chile time zone (America/Santiago), which is in standard time during July.
X  gemini-3.1-pro-preview       {"utc_offset": "-04:00"}                 Coyhaique, in the Aysén Region, observes standard Chile time, which is UTC-04:00 during the winter months.
X  claude-sonnet-5              {"utc_offset": "-04:00"}                 Chile observes standard time (UTC-4) in winter, and Coyhaique follows the America/Santiago time zone rules since Chile's DST does not begin until September.
X  gemini-3.5-flash-lite        {"utc_offset": "-04:00"}                 Chile is on standard time (-04:00) during the Southern Hemisphere winter on July 15, 2025.
X  qwen3-next-80b-a3b-thinking  {"utc_offset": "-04:00"}                 Chile's standard time (UTC-4) applies in Coyhaique during July 2025 as it is outside the DST period (September to March) per IANA rules for America/Santiago.

### offset:almaty:2024-07-15:12:00
ok claude-haiku-4-5             {"utc_offset": "+05:00"}                 Kazakhstan observes a fixed UTC+5 offset year-round with no daylight saving time.
ok claude-opus-4-5              {"utc_offset": "+05:00"}                 Kazakhstan uses a permanent UTC+05:00 offset nationwide since March 2024, with no daylight saving time observed.
ok gpt-5.6-terra                {"utc_offset": "+05:00"}                 Kazakhstan unified its time zone on 1 March 2024, so Almaty used UTC+05:00 on 15 July 2024.
ok gemini-3.8-flash             {"utc_offset": "+05:00"}                 Kazakhstan unified all regions into a single UTC+5 time zone starting March 1, 2024, abolishing UTC+6 in Almaty.
ok gpt-5.4-mini-2026-03-17      {"utc_offset": "+05:00"}                 Applied the Asia/Almaty time zone rule in effect on 2024-07-15, with no daylight saving time change that day.
ok grok-4.20-0309-reasoning     {"utc_offset": "+05:00"}                 Almaty observes a constant UTC+5 offset year-round with no daylight saving time.
ok claude-opus-5                {"utc_offset": "+05:00"}                 Kazakhstan unified the whole country on UTC+05:00 effective 1 March 2024, so Almaty was at +05:00 in July 2024 (no daylight saving time is observed).
ok gpt-5.5-2026-04-23           {"utc_offset": "+05:00"}                 Kazakhstan unified most regions including Almaty on UTC+05:00 from March 1, 2024, with no daylight saving time in effect on July 15, 2024.
ok gemini-3.7-flash             {"utc_offset": "+05:00"}                 Kazakhstan abolished daylight saving time and moved Almaty to a unified standard time zone of UTC+5 starting March 1, 2024.
ok grok-4.20-0309-non-reasoning {"utc_offset": "+05:00"}                 Kazakhstan has observed a fixed UTC+05:00 offset with no DST since 2005.
ok glm-5                        {"utc_offset": "+05:00"}                 I applied the rule that Kazakhstan switched Almaty to permanent UTC+05:00 in March 2024 and does not observe daylight saving time.
ok gemma-4-31b                  {"utc_offset": "+05:00"}                 Kazakhstan transitioned to a single unified time zone of UTC+5 on March 1, 2024.
ok gemini-3.1-pro-preview       {"utc_offset": "+05:00"}                 Almaty observes standard time at UTC+5 year-round following Kazakhstan's unification of all its time zones on March 1, 2024.
ok claude-sonnet-5              {"utc_offset": "+05:00"}                 Kazakhstan abolished daylight saving time and Almaty has used a fixed UTC+5 offset year-round since 2005.
ok gemini-3.5-flash-lite        {"utc_offset": "+05:00"}                 Kazakhstan unified its time zone to UTC+5 across the entire country in March 2024, so Almaty observed UTC+5 on July 15, 2024.
X  qwen3-next-80b-a3b-thinking  {"utc_offset": "+06:00"}                 Kazakhstan abolished daylight saving time in 2005, so Almaty observes UTC+6 year-round.

### change_day:winnipeg:2026-11-01
~  claude-haiku-4-5             {"changes": true, "direction": "back"}   Winnipeg observes the end of daylight saving time on November 1, 2026, with clocks falling back one hour from CDT to CST.
~  claude-opus-4-5              {"changes": true, "direction": "back"}   On 2026-11-01, Winnipeg's clocks fall back from CDT (UTC-05:00) to CST (UTC-06:00) at 2:00 AM local time as daylight saving time ends.
~  gpt-5.6-terra                {"changes": true, "direction": "back"}   Winnipeg clocks fall back from CDT to CST during the local day on 2026-11-01.
~  gemini-3.8-flash             {"changes": true, "direction": "back"}   Clocks in Winnipeg fall back by one hour on November 1, 2026, marking the end of daylight saving time.
~  gpt-5.4-mini-2026-03-17      {"changes": true, "direction": "back"}   Winnipeg clocks fall back during the local calendar day of 2026-11-01, changing from UTC-05:00 to UTC-06:00.
~  grok-4.20-0309-reasoning     {"changes": true, "direction": "back"}   Clocks in Winnipeg fall back one hour from CDT to CST during the local day of 2026-11-01.
~  claude-opus-5                {"changes": true, "direction": "back"}   On Sunday, 2026-11-01, Winnipeg ends daylight saving time, with clocks falling back one hour at 2:00 a.m. local time to 1:00 a.m., shifting from CDT (UTC-5) to CST (UTC-6).
~  gpt-5.5-2026-04-23           {"changes": true, "direction": "back"}   In Winnipeg on 2026-11-01, clocks fall back from CDT (UTC-05:00) to CST (UTC-06:00).
~  gemini-3.7-flash             {"changes": true, "direction": "back"}   Clocks in Winnipeg fall back by one hour on November 1, 2026, marking the end of Daylight Saving Time.
~  grok-4.20-0309-non-reasoning {"changes": true, "direction": "back"}   Clocks in Winnipeg fall back from CDT to CST on 2026-11-01.
~  glm-5                        {"changes": true, "direction": "back"}   On November 1, 2026, clocks in Winnipeg fall back from Central Daylight Time (UTC-5) to Central Standard Time (UTC-6) at 2:00 AM local time.
~  gemma-4-31b                  {"changes": true, "direction": "back"}   Clocks in Winnipeg fall back from CDT to CST on November 1, 2026.
~  gemini-3.1-pro-preview       {"changes": true, "direction": "back"}   On November 1, 2026, the clocks in Winnipeg fall back by one hour as Daylight Saving Time ends.
~  claude-sonnet-5              {"changes": true, "direction": "back"}   Winnipeg observes the end of Daylight Saving Time on November 1, 2026, when clocks fall back from CDT (UTC-05:00) to CST (UTC-06:00) at 2:00 a.m. local time.
~  gemini-3.5-flash-lite        {"changes": true, "direction": "back"}   Clocks in Winnipeg fall back by one hour on November 1, 2026, marking the end of daylight saving time.
~  qwen3-next-80b-a3b-thinking  {"changes": false, "direction": "none"}  No clock change occurs on 2026-11-01; the fall back happens on 2026-11-02.
