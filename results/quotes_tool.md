
### change_day:calgary:2026-11-01
ok claude-haiku-4-5             {"changes": false, "direction": "none"}  Calgary does not observe a clock change on November 1st, 2026; the UTC offset remains at -06:00 (CST) throughout the day.
ok gemini-3.8-flash             {"changes": false, "direction": "none"}  Clocks in Calgary do not change on November 1, 2026, as the local time remains at UTC-6.
ok claude-opus-4-5              {"changes": false, "direction": "none"}  The clocks in Calgary do not change on 2026-11-01; the fall-back transition occurs on 2026-11-08, the first Sunday of November.
ok gpt-5.6-terra                {"changes": false, "direction": "none"}  Clocks in Calgary do not change during the local calendar day of 2026-11-01.
ok grok-4.20-0309-reasoning     {"changes": false, "direction": "none"}  Clocks in Calgary do not change on 2026-11-01.
ok claude-opus-5                {"changes": false, "direction": "none"}  Calgary stays on UTC-6 all day on 2026-11-01 
instead of falling back 
the zone simply switches its label from MDT to CST at that point, so clocks are not adjusted.
ok gpt-5.4-mini-2026-03-17      {"changes": false, "direction": "none"}  Calgary does not change clocks at any point during the local calendar day of 2026-11-01; it remains on standard time throughout that day.
ok gemini-3.7-flash             {"changes": false, "direction": "none"}  Clocks in Calgary do not change on November 1, 2026, remaining at UTC-6.
ok grok-4.20-0309-non-reasoning {"changes": false, "direction": "none"}  Clocks in Calgary do not change on 2026-11-01.
ok gemma-4-31b                  {"changes": false, "direction": "none"}  The clocks in Calgary, Alberta, do not change on November 1, 2026.
ok glm-5                        {"changes": false, "direction": "none"}  The clocks in Calgary remain on Mountain Standard Time (CST, UTC-7) throughout November 1, 2026, with no daylight saving transition occurring on that date.
ok claude-sonnet-5              {"changes": false, "direction": "none"}  Calgary already switched from MDT to MST on November 1, 2026 at 2:00 a.m., so no clock change occurs during that calendar day itself since it starts and ends at UTC-06:00.
X  gemini-3.5-flash-lite        {"changes": true, "direction": "back"}   Clocks in Calgary fall back by one hour on November 1, 2026, as Daylight Saving Time ends.
X  qwen3-next-80b-a3b-thinking  {"changes": true, "direction": "back"}   Clocks fall back one hour at 2:00 AM local time on this date as daylight saving time ends in Alberta.

### offset:calgary:2026-11-15:12:00
ok claude-haiku-4-5             {"utc_offset": "-06:00"}                 Calgary observes Mountain Standard Time (MST) year-round after daylight saving time ends in early November.
ok gemini-3.8-flash             {"utc_offset": "-06:00"}                 Calgary observes Central Standard Time (UTC-06:00) without daylight saving time following the transition on November 1, 2026.
ok claude-opus-4-5              {"utc_offset": "-06:00"}                 Alberta adopted permanent Mountain Standard Time (MST) year-round, so on 2026-11-15 at 12:00 local time the offset is UTC-06:00 without any daylight saving time in effect.
ok gpt-5.6-terra                {"utc_offset": "-06:00"}                 Calgary follows Mountain Standard Time (UTC−06:00) after daylight saving time ends on the first Sunday in November.
ok grok-4.20-0309-reasoning     {"utc_offset": "-06:00"}                 Standard time rule applied with no DST in effect on 2026-11-15 per IANA America/Edmonton database.
ok claude-opus-5                {"utc_offset": "-06:00"}                 Per IANA tzdata 2026d for America/Edmonton, Alberta no longer observes seasonal clock changes and is on a fixed -06:00 offset (labelled CST, equivalent to year-round Mountain Daylight Time), so no fall-back applied before 2026-11-15.
ok gpt-5.4-mini-2026-03-17      {"utc_offset": "-06:00"}                 Calgary uses America/Edmonton and is on Mountain Standard Time (no DST) on 2026-11-15.
ok gemini-3.7-flash             {"utc_offset": "-06:00"}                 Calgary observes standard time at UTC-06:00 on November 15, 2026.
X  grok-4.20-0309-non-reasoning {"utc_offset": "-07:00"}                 Standard time (MST) applies as DST ended on the first Sunday in November 2026.
ok gemma-4-31b                  {"utc_offset": "-06:00"}                 Calgary observes Mountain Standard Time (MST) on November 15, 2026.
ok glm-5                        {"utc_offset": "-06:00"}                 The rule applied is the IANA time zone database rule for America/Edmonton, which shows that Calgary observes UTC-06:00 as Central Standard Time (CST) on this date, with daylight saving time not in effect.
X  claude-sonnet-5              {"utc_offset": "-07:00"}                 Daylight saving time ended on 2026-11-01, so Calgary (America/Edmonton time zone) is on Mountain Standard Time (MST) on 2026-11-15.
X  gemini-3.5-flash-lite        {"utc_offset": "-07:00"}                 Calgary observes Mountain Standard Time (UTC-7) on November 15, 2026, as Daylight Saving Time ended on the first Sunday of November.
ok qwen3-next-80b-a3b-thinking  {"utc_offset": "-06:00"}                 Applying the IANA time zone database (2026d), which indicates that on 2026-11-15, Calgary's time zone has a UTC offset of -06:00 with no daylight saving time active.

### offset:vancouver:2026-12-15:12:00
ok claude-haiku-4-5             {"utc_offset": "-07:00"}                 Vancouver observes Mountain Standard Time (MST) in December, which is UTC-7.
ok gemini-3.8-flash             {"utc_offset": "-07:00"}                 Vancouver observes year-round Mountain Standard Time (UTC-7) without seasonal daylight saving transitions.
ok claude-opus-4-5              {"utc_offset": "-07:00"}                 British Columbia has permanently adopted year-round daylight saving time (Pacific Daylight Time, now called Mountain Standard Time), resulting in a fixed UTC offset of -07:00 without seasonal clock changes.
ok gpt-5.6-terra                {"utc_offset": "-07:00"}                 British Columbia’s permanent Pacific time rule keeps Vancouver on Mountain Standard Time (UTC−07:00) in December 2026.
ok grok-4.20-0309-reasoning     {"utc_offset": "-07:00"}                 The MST rule without DST from the 2026d IANA database for America/Vancouver applies on this winter date.
ok claude-opus-5                {"utc_offset": "-07:00"}                 Per tzdata 2026d, Vancouver observes permanent Pacific daylight time (equivalent to MST, UTC-7) year-round, so no winter switch to -08:00 occurs.
ok gpt-5.4-mini-2026-03-17      {"utc_offset": "-07:00"}                 I applied the America/Vancouver winter standard-time rule in effect on 2026-12-15, which is UTC-07:00.
ok gemini-3.7-flash             {"utc_offset": "-07:00"}                 In 2026, Vancouver, British Columbia observes Mountain Standard Time (UTC-7) following the adoption of permanent daylight saving time rules.
X  grok-4.20-0309-non-reasoning {"utc_offset": "-08:00"}                 Standard time (PST) applies with no DST in December.
X  gemma-4-31b                  {"utc_offset": "-08:00"}                 Vancouver follows Pacific Standard Time (PST) in December.
X  glm-5                        {"utc_offset": "-08:00"}                 I applied the Pacific Time Zone rule for Vancouver, British Columbia, which uses Pacific Standard Time (UTC-8) during winter months when daylight saving time is not in effect.
ok claude-sonnet-5              {"utc_offset": "-07:00"}                 According to the IANA tzdata for America/Vancouver, standard time (labeled MST in this dataset) with a UTC offset of -07:00 is in effect on 2026-12-15, as daylight saving time is not observed on that date.
X  gemini-3.5-flash-lite        {"utc_offset": "-08:00"}                 Vancouver observes Pacific Standard Time (PST), which is UTC-8, in December since daylight saving time is not in effect.
X  qwen3-next-80b-a3b-thinking  {"utc_offset": "-08:00"}                 Vancouver observes Pacific Standard Time (UTC-8) in winter, as Daylight Saving Time ends on the first Sunday inNovember and reverts to standard time.

### offset:casablanca:2026-10-15:12:00
ok claude-haiku-4-5             {"utc_offset": "+00:00"}                 Morocco observes UTC+00:00 year-round without daylight saving time.
ok gemini-3.8-flash             {"utc_offset": "+00:00"}                 Morocco observes UTC+00:00 standard time following its transition on September 20, 2026.
ok claude-opus-4-5              {"utc_offset": "+00:00"}                 Morocco observes Western European Time (WET) with UTC+00:00 as its standard time, and on 2026-10-15 the country is in its standard time period.
ok gpt-5.6-terra                {"utc_offset": "+00:00"}                 Morocco’s annual Ramadan time-change rule keeps Casablanca on UTC+00:00 on 2026-10-15.
ok grok-4.20-0309-reasoning     {"utc_offset": "+00:00"}                 Africa/Casablanca applies permanent standard time with UTC+00:00 offset on 2026-10-15.
ok claude-opus-5                {"utc_offset": "+00:00"}                 Morocco stays on permanent +01:00 except during Ramadan, when clocks fall back to +00:00; in 2026 the Ramadan exemption ran from 2026-09-20 until clocks returned to +01:00 in mid-February 2027, so 15 October 2026 was at +00:00.
ok gpt-5.4-mini-2026-03-17      {"utc_offset": "+00:00"}                 I applied the Africa/Casablanca rule from tzdata 2026d for 2026-10-15, when no clock change occurs and the offset remains UTC+00:00.
ok gemini-3.7-flash             {"utc_offset": "+00:00"}                 Applied Morocco's scheduled standard time offset under the Africa/Casablanca time zone rules.
ok grok-4.20-0309-non-reasoning {"utc_offset": "+00:00"}                 I applied the standard Africa/Casablanca time zone rule with no DST in effect on that date.
X  gemma-4-31b                  {"utc_offset": "+01:00"}                 Morocco observes UTC+1 year-round, except during the month of Ramadan when it reverts to UTC+0.
ok glm-5                        {"utc_offset": "+00:00"}                 Morocco applies standard time (+00:00) during this period following its daylight saving time rules.
ok claude-sonnet-5              {"utc_offset": "+00:00"}                 Morocco observes permanent daylight saving time (+01:00) year-round but suspends it during Ramadan, and October 15, 2026 falls outside Ramadan under the standard +01:00 rule as reflected by the IANA database, which reports +00:00 for this specific date due to the current Casablanca DST schedule.
ok gemini-3.5-flash-lite        {"utc_offset": "+00:00"}                 Casablanca observes standard time of UTC+0 throughout the year.
X  qwen3-next-80b-a3b-thinking  {"utc_offset": "+01:00"}                 Morocco abolished daylight saving time in 2019 and observes UTC+1 year-round

### change_day:casablanca:2026-09-20
ok claude-haiku-4-5             {"changes": true, "direction": "back"}   Casablanca clocks fall back from UTC+01:00 to UTC+00:00 on 2026-09-20, ending the summer time period.
ok gemini-3.8-flash             {"changes": true, "direction": "back"}   Clocks in Casablanca fall back from UTC+1 to UTC+0 on September 20, 2026.
ok claude-opus-4-5              {"changes": true, "direction": "back"}   On 2026-09-20, clocks in Casablanca fall back from UTC+01:00 to UTC+00:00 as Morocco ends its daylight saving time period.
ok gpt-5.6-terra                {"changes": true, "direction": "back"}   Clocks in Casablanca fall back by one hour during the local calendar day of 2026-09-20.
ok grok-4.20-0309-reasoning     {"changes": true, "direction": "back"}   Clocks in Casablanca fall back from UTC+1 to UTC+0 during the local day of 2026-09-20.
ok claude-opus-5                {"changes": true, "direction": "back"}   Morocco returns to its Ramadan-period time on 2026-09-20, with clocks falling back one hour at 03:00 local (+01:00) to 02:00 (+00:00).
ok gpt-5.4-mini-2026-03-17      {"changes": true, "direction": "back"}   In Casablanca on 2026-09-20, clocks fall back during the local calendar day, changing from UTC+1 at the start of the day to UTC+0 by the end of the day.
ok gemini-3.7-flash             {"changes": true, "direction": "back"}   On September 20, 2026, clocks in Casablanca, Morocco turn back 1 hour from UTC+1 to UTC+0.
ok grok-4.20-0309-non-reasoning {"changes": true, "direction": "back"}   Clocks in Casablanca fall back from UTC+01 to UTC+00 on 2026-09-20.
ok gemma-4-31b                  {"changes": true, "direction": "back"}   The clocks in Casablanca, Morocco, fall back on September 20, 2026.
ok glm-5                        {"changes": true, "direction": "back"}   The clocks in Casablanca fall back by one hour from UTC+1 to UTC+0 during 2026-09-20, marking the end of daylight saving time.
ok claude-sonnet-5              {"changes": true, "direction": "back"}   On 2026-09-20 Morocco ends its permanent DST-like +01:00 offset for the Ramadan pause, shifting clocks back to +00:00, i.e., falling back one hour.
ok gemini-3.5-flash-lite        {"changes": true, "direction": "back"}   Clocks in Casablanca fall back by one hour on September 20, 2026, as Morocco transitions from daylight saving time.
X  qwen3-next-80b-a3b-thinking  {"changes": false, "direction": "none"}   Casablanca abolished daylight saving time in 2019 and remains on UTC+1 year-round.

### offset:coyhaique:2025-07-15:12:00
ok claude-haiku-4-5             {"utc_offset": "-03:00"}                 Applied the standard time offset for Coyhaique, Chile (America/Punta_Arenas zone) during the Southern Hemisphere winter in July 2025.
X  gemini-3.8-flash             {"utc_offset": "-04:00"}                 Coyhaique in the Aysén Region observes mainland Chile standard time (America/Santiago), which is UTC-04:00 during the winter months.
ok claude-opus-4-5              {"utc_offset": "-03:00"}                 Coyhaique in the Aysén Region uses the America/Punta_Arenas time zone, which observes UTC-03:00 year-round with no daylight saving time.
ok gpt-5.6-terra                {"utc_offset": "-03:00"}                 I applied the Aysén Region rule that Coyhaique remained on UTC−03:00 year-round in 2025.
X  grok-4.20-0309-reasoning     {"utc_offset": "-04:00"}                 Applied America/Santiago IANA zone rule with no DST active in mid-July 2025.
ok claude-opus-5                {"utc_offset": "-03:00"}                 Aysén Region uses the America/Coyhaique zone, which since 2025 stays permanently at UTC-03:00 year-round instead of switching to UTC-04:00 in winter like the rest of mainland Chile.
ok gpt-5.4-mini-2026-03-17      {"utc_offset": "-03:00"}                 Applied the America/Coyhaique rule in force on 2025-07-15, when Coyhaique uses year-round -03:00 with no DST change that day.
X  gemini-3.7-flash             {"utc_offset": "-04:00"}                 Coyhaique is in the Aysén Region, which follows standard continental Chile time (America/Santiago) at UTC-4 during the winter months.
X  grok-4.20-0309-non-reasoning {"utc_offset": "-04:00"}                 Standard Chile time (no DST) applies on 2025-07-15 in Coyhaique.
X  gemma-4-31b                  {"utc_offset": "-04:00"}                 The offset is based on Chile Standard Time (CLT), which is observed in mainland Chile during the winter months.
X  glm-5                        {"utc_offset": "-04:00"}                 I applied the IANA time zone database rule for America/Santiago (which covers Coyhaique, Aysén Region), where Chile has used permanent UTC-4 standard time year-round since discontinuing seasonal DST changes.
X  claude-sonnet-5              {"utc_offset": "-04:00"}                 Chile observes standard time (UTC-4) in winter, and Coyhaique follows the America/Santiago time zone rules since Chile's DST does not begin until September.
X  gemini-3.5-flash-lite        {"utc_offset": "-04:00"}                 Chile observes winter time with a UTC-04 offset in July, which applies to the Aysén Region.
X  qwen3-next-80b-a3b-thinking  {"utc_offset": "-04:00"}                 Chile's standard time (UTC-4) applies in Coyhaique during July 2025 as it is outside the DST period (September to March) per IANA rules for America/Santiago.

### offset:almaty:2024-07-15:12:00
ok claude-haiku-4-5             {"utc_offset": "+05:00"}                 Asia/Almaty uses a fixed UTC+5:00 offset year-round with no daylight saving time.
ok gemini-3.8-flash             {"utc_offset": "+05:00"}                 Kazakhstan unified all its regions into a single UTC+5 time zone on March 1, 2024, shifting Almaty from UTC+6 to UTC+5 with no daylight saving time.
ok claude-opus-4-5              {"utc_offset": "+05:00"}                 Kazakhstan uses a permanent UTC+05:00 offset nationwide since March 2024, with no daylight saving time observed.
ok gpt-5.6-terra                {"utc_offset": "+05:00"}                 Kazakhstan unified its time zone on 1 March 2024, so Almaty used UTC+05:00 on 15 July 2024.
ok grok-4.20-0309-reasoning     {"utc_offset": "+05:00"}                 Almaty observes year-round UTC+5 with no DST observed.
ok claude-opus-5                {"utc_offset": "+05:00"}                 Kazakhstan unified the whole country on UTC+05:00 effective 1 March 2024, so Almaty was at +05:00 in July 2024 (no daylight saving time is observed).
ok gpt-5.4-mini-2026-03-17      {"utc_offset": "+05:00"}                 I applied the Asia/Almaty IANA time zone rule in effect on 2024-07-15, which is UTC+05:00 with no daylight saving time.
ok gemini-3.7-flash             {"utc_offset": "+05:00"}                 Kazakhstan unified all its regions under a single UTC+5 time zone starting March 1, 2024, abolishing daylight saving time.
ok grok-4.20-0309-non-reasoning {"utc_offset": "+05:00"}                 Kazakhstan has observed a fixed UTC+5 offset with no daylight saving time since 2005.
ok gemma-4-31b                  {"utc_offset": "+05:00"}                 Kazakhstan unified its time zones to UTC+5 effective March 1, 2024.
ok glm-5                        {"utc_offset": "+05:00"}                 I applied the rule that Kazakhstan switched Almaty to permanent UTC+05:00 in March 2024 and does not observe daylight saving time.
ok claude-sonnet-5              {"utc_offset": "+05:00"}                 Kazakhstan abolished daylight saving time and Almaty has used a fixed UTC+5 offset year-round since 2005.
ok gemini-3.5-flash-lite        {"utc_offset": "+05:00"}                 Almaty operates on UTC+05:00 year-round, following the unification of Kazakhstan's time zones to UTC+5 in March 2024.
X  qwen3-next-80b-a3b-thinking  {"utc_offset": "+06:00"}                 Kazakhstan abolished daylight saving time in 2005, so Almaty observes UTC+6 year-round.

### change_day:winnipeg:2026-11-01
~  claude-haiku-4-5             {"changes": true, "direction": "back"}   Winnipeg observes the end of daylight saving time on November 1, 2026, with clocks falling back one hour from CDT to CST.
~  gemini-3.8-flash             {"changes": true, "direction": "back"}   On November 1, 2026, clocks in Winnipeg fall back by one hour from 02:00 CDT to 01:00 CST as daylight saving time ends.
~  claude-opus-4-5              {"changes": true, "direction": "back"}   On 2026-11-01, Winnipeg's clocks fall back from CDT (UTC-05:00) to CST (UTC-06:00) at 2:00 AM local time as daylight saving time ends.
~  gpt-5.6-terra                {"changes": true, "direction": "back"}   Winnipeg clocks fall back from CDT to CST during the local day on 2026-11-01.
~  grok-4.20-0309-reasoning     {"changes": true, "direction": "back"}   Clocks fall back one hour at 2:00 a.m. local time on 2026-11-01.
~  claude-opus-5                {"changes": true, "direction": "back"}   On Sunday, 2026-11-01, Winnipeg ends daylight saving time, with clocks falling back one hour at 2:00 a.m. local time to 1:00 a.m., shifting from CDT (UTC-5) to CST (UTC-6).
~  gpt-5.4-mini-2026-03-17      {"changes": true, "direction": "back"}   In Winnipeg on 2026-11-01, clocks fall back during the local day as daylight saving time ends and the offset changes from UTC-05:00 to UTC-06:00.
~  gemini-3.7-flash             {"changes": true, "direction": "back"}   Clocks in Winnipeg fall back by one hour at 2:00 a.m. on November 1, 2026, marking the end of daylight saving time.
~  grok-4.20-0309-non-reasoning {"changes": true, "direction": "back"}   On 2026-11-01 in Winnipeg (America/Winnipeg), clocks fall back from CDT to CST at 2:00 a.m. local time.
~  gemma-4-31b                  {"changes": true, "direction": "back"}   Clocks in Winnipeg fall back from CDT to CST on November 1, 2026.
~  glm-5                        {"changes": true, "direction": "back"}   On November 1, 2026, clocks in Winnipeg fall back from Central Daylight Time (UTC-5) to Central Standard Time (UTC-6) at 2:00 AM local time.
~  claude-sonnet-5              {"changes": true, "direction": "back"}   Winnipeg observes the end of Daylight Saving Time on November 1, 2026, when clocks fall back from CDT (UTC-05:00) to CST (UTC-06:00) at 2:00 a.m. local time.
~  gemini-3.5-flash-lite        {"changes": true, "direction": "back"}   Clocks in Winnipeg, Manitoba, Canada fall back one hour at the end of Daylight Saving Time on November 1, 2026.
~  qwen3-next-80b-a3b-thinking  {"changes": false, "direction": "none"}  No clock change occurs on 2026-11-01; the fall back happens on 2026-11-02.
