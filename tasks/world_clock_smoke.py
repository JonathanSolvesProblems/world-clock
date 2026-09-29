# %% [markdown]
# # World Clock: 20-case smoke test, from memory
#
# Every model is asked the same 125 questions about local time. Each expected answer was
# computed by Python's `zoneinfo` against the IANA time zone database, release 2026d
# (PyPI `tzdata` 2026.4), by `cases/build_cases.py` in the public repository. No answer in
# the key was typed by a person.
#
# **Condition:** A stratified 20-case subset of the from-memory task, graded against tzdata 2026d. Used to check the pipeline before spending quota on the full lineup.
#
# Families: `control` (textbook zones), `awkward_offset` (+05:45, +12:45, 30-minute DST),
# `southern` (southern-hemisphere DST), `legislated_2022_2025` (Iran, Jordan, Mexico,
# Greenland, Egypt, Kazakhstan, Paraguay, Chile), `wave_2026` (British Columbia, Alberta,
# Northwest Territories, Morocco stopped changing their clocks in 2026), and `unresolved`
# (Manitoba announced permanent daylight time on 2026-09-17; no tzdata release has it yet,
# so those three cases are recorded and never counted).
#
# Score = correct answers over the 122 graded cases.

# %%
import json
import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass

import pandas as pd

import kaggle_benchmarks as kbench
from kaggle_benchmarks.tools import base as tool_base
from kaggle_benchmarks.tools import native as tool_native

CONDITION = "memory"
TASK_NAME = "world-clock-smoke"
TZDATA_PYPI = "2026.4"
TZDATA_IANA = "2026d"
# A stratified subset when non-zero; the smoke task bakes in 20, the real tasks 0 (all).
LIMIT = int(os.environ.get("WORLD_CLOCK_LIMIT", "20") or 0)
N_JOBS = int(os.environ.get("WORLD_CLOCK_JOBS", "2") or 2)
# The Model Proxy reserves quota per request from the output-token cap, so an uncapped
# request on a frontier model can reserve several dollars and be refused. 2500 tokens is
# generous for a two-field answer plus a sentence, and leaves room for reasoning tokens.
# A model that still runs out of room gets one more try at double the cap, up to MAX_CAP.
MAX_TOKENS = int(os.environ.get("WORLD_CLOCK_MAX_TOKENS", "2500") or 2500)
MAX_CAP = 10000
# Tool-calling rounds per case. The SDK default of 10 was exhausted by a model that checked
# every zone twice; 30 leaves room for that without letting a loop run forever.
MAX_TOOL_ROUNDS = 30

# %%
CASES = json.loads(r"""[{"id":"offset:new_york:2026-07-15:12:00","family":"control","kind":"offset","prompt":"What is the UTC offset in effect in New York City, USA at 12:00 local time on 2026-07-15? Answer with the offset in the form +HH:MM or -HH:MM.","expected":{"utc_offset":"-04:00"},"graded":true},{"id":"offset:new_york:2026-12-15:12:00","family":"control","kind":"offset","prompt":"What is the UTC offset in effect in New York City, USA at 12:00 local time on 2026-12-15? Answer with the offset in the form +HH:MM or -HH:MM.","expected":{"utc_offset":"-05:00"},"graded":true},{"id":"offset:london:2026-07-15:12:00","family":"control","kind":"offset","prompt":"What is the UTC offset in effect in London, United Kingdom at 12:00 local time on 2026-07-15? Answer with the offset in the form +HH:MM or -HH:MM.","expected":{"utc_offset":"+01:00"},"graded":true},{"id":"offset:london:2026-12-15:12:00","family":"control","kind":"offset","prompt":"What is the UTC offset in effect in London, United Kingdom at 12:00 local time on 2026-12-15? Answer with the offset in the form +HH:MM or -HH:MM.","expected":{"utc_offset":"+00:00"},"graded":true},{"id":"offset:tokyo:2026-07-15:12:00","family":"control","kind":"offset","prompt":"What is the UTC offset in effect in Tokyo, Japan at 12:00 local time on 2026-07-15? Answer with the offset in the form +HH:MM or -HH:MM.","expected":{"utc_offset":"+09:00"},"graded":true},{"id":"offset:paris:2026-01-15:12:00","family":"control","kind":"offset","prompt":"What is the UTC offset in effect in Paris, France at 12:00 local time on 2026-01-15? Answer with the offset in the form +HH:MM or -HH:MM.","expected":{"utc_offset":"+01:00"},"graded":true},{"id":"offset:los_angeles:2026-11-15:12:00","family":"control","kind":"offset","prompt":"What is the UTC offset in effect in Los Angeles, USA at 12:00 local time on 2026-11-15? Answer with the offset in the form +HH:MM or -HH:MM.","expected":{"utc_offset":"-08:00"},"graded":true},{"id":"offset:toronto:2026-11-15:12:00","family":"control","kind":"offset","prompt":"What is the UTC offset in effect in Toronto, Ontario, Canada at 12:00 local time on 2026-11-15? Answer with the offset in the form +HH:MM or -HH:MM.","expected":{"utc_offset":"-05:00"},"graded":true},{"id":"offset:sydney:2026-01-15:12:00","family":"control","kind":"offset","prompt":"What is the UTC offset in effect in Sydney, New South Wales, Australia at 12:00 local time on 2026-01-15? Answer with the offset in the form +HH:MM or -HH:MM.","expected":{"utc_offset":"+11:00"},"graded":true},{"id":"offset:sydney:2026-07-15:12:00","family":"control","kind":"offset","prompt":"What is the UTC offset in effect in Sydney, New South Wales, Australia at 12:00 local time on 2026-07-15? Answer with the offset in the form +HH:MM or -HH:MM.","expected":{"utc_offset":"+10:00"},"graded":true},{"id":"offset:mumbai:2026-07-15:12:00","family":"control","kind":"offset","prompt":"What is the UTC offset in effect in Mumbai, India at 12:00 local time on 2026-07-15? Answer with the offset in the form +HH:MM or -HH:MM.","expected":{"utc_offset":"+05:30"},"graded":true},{"id":"offset:dubai:2026-07-15:12:00","family":"control","kind":"offset","prompt":"What is the UTC offset in effect in Dubai, United Arab Emirates at 12:00 local time on 2026-07-15? Answer with the offset in the form +HH:MM or -HH:MM.","expected":{"utc_offset":"+04:00"},"graded":true},{"id":"convert:new_york:london:2026-07-15:09:00","family":"control","kind":"convert","prompt":"It is 09:00 on 2026-07-15 in New York City, USA. What is the local date and time at that same moment in London, United Kingdom? Give the date as YYYY-MM-DD and the time as HH:MM in 24-hour format.","expected":{"date":"2026-07-15","time":"14:00"},"graded":true},{"id":"convert:tokyo:los_angeles:2026-03-10:09:00","family":"control","kind":"convert","prompt":"It is 09:00 on 2026-03-10 in Tokyo, Japan. What is the local date and time at that same moment in Los Angeles, USA? Give the date as YYYY-MM-DD and the time as HH:MM in 24-hour format.","expected":{"date":"2026-03-09","time":"17:00"},"graded":true},{"id":"convert:toronto:paris:2026-11-15:09:00","family":"control","kind":"convert","prompt":"It is 09:00 on 2026-11-15 in Toronto, Ontario, Canada. What is the local date and time at that same moment in Paris, France? Give the date as YYYY-MM-DD and the time as HH:MM in 24-hour format.","expected":{"date":"2026-11-15","time":"15:00"},"graded":true},{"id":"convert:london:sydney:2026-01-15:09:00","family":"control","kind":"convert","prompt":"It is 09:00 on 2026-01-15 in London, United Kingdom. What is the local date and time at that same moment in Sydney, New South Wales, Australia? Give the date as YYYY-MM-DD and the time as HH:MM in 24-hour format.","expected":{"date":"2026-01-15","time":"20:00"},"graded":true},{"id":"convert:chicago:mumbai:2026-07-15:09:00","family":"control","kind":"convert","prompt":"It is 09:00 on 2026-07-15 in Chicago, USA. What is the local date and time at that same moment in Mumbai, India? Give the date as YYYY-MM-DD and the time as HH:MM in 24-hour format.","expected":{"date":"2026-07-15","time":"19:30"},"graded":true},{"id":"convert:berlin:tokyo:2026-12-15:09:00","family":"control","kind":"convert","prompt":"It is 09:00 on 2026-12-15 in Berlin, Germany. What is the local date and time at that same moment in Tokyo, Japan? Give the date as YYYY-MM-DD and the time as HH:MM in 24-hour format.","expected":{"date":"2026-12-15","time":"17:00"},"graded":true},{"id":"change_day:new_york:2026-03-08","family":"control","kind":"change_day","prompt":"Do the clocks in New York City, USA change at any point during the local calendar day of 2026-03-08, either springing forward or falling back? Answer whether they change and, if so, in which direction.","expected":{"changes":true,"direction":"forward"},"graded":true},{"id":"change_day:new_york:2026-11-01","family":"control","kind":"change_day","prompt":"Do the clocks in New York City, USA change at any point during the local calendar day of 2026-11-01, either springing forward or falling back? Answer whether they change and, if so, in which direction.","expected":{"changes":true,"direction":"back"},"graded":true},{"id":"change_day:london:2026-03-29","family":"control","kind":"change_day","prompt":"Do the clocks in London, United Kingdom change at any point during the local calendar day of 2026-03-29, either springing forward or falling back? Answer whether they change and, if so, in which direction.","expected":{"changes":true,"direction":"forward"},"graded":true},{"id":"change_day:london:2026-10-25","family":"control","kind":"change_day","prompt":"Do the clocks in London, United Kingdom change at any point during the local calendar day of 2026-10-25, either springing forward or falling back? Answer whether they change and, if so, in which direction.","expected":{"changes":true,"direction":"back"},"graded":true},{"id":"change_day:toronto:2026-11-01","family":"control","kind":"change_day","prompt":"Do the clocks in Toronto, Ontario, Canada change at any point during the local calendar day of 2026-11-01, either springing forward or falling back? Answer whether they change and, if so, in which direction.","expected":{"changes":true,"direction":"back"},"graded":true},{"id":"change_day:tokyo:2026-03-08","family":"control","kind":"change_day","prompt":"Do the clocks in Tokyo, Japan change at any point during the local calendar day of 2026-03-08, either springing forward or falling back? Answer whether they change and, if so, in which direction.","expected":{"changes":false,"direction":"none"},"graded":true},{"id":"change_day:paris:2026-10-25","family":"control","kind":"change_day","prompt":"Do the clocks in Paris, France change at any point during the local calendar day of 2026-10-25, either springing forward or falling back? Answer whether they change and, if so, in which direction.","expected":{"changes":true,"direction":"back"},"graded":true},{"id":"change_day:phoenix:2026-03-08","family":"control","kind":"change_day","prompt":"Do the clocks in Phoenix, Arizona, USA change at any point during the local calendar day of 2026-03-08, either springing forward or falling back? Answer whether they change and, if so, in which direction.","expected":{"changes":false,"direction":"none"},"graded":true},{"id":"offset:kathmandu:2026-07-15:12:00","family":"awkward_offset","kind":"offset","prompt":"What is the UTC offset in effect in Kathmandu, Nepal at 12:00 local time on 2026-07-15? Answer with the offset in the form +HH:MM or -HH:MM.","expected":{"utc_offset":"+05:45"},"graded":true},{"id":"offset:chatham:2026-01-15:12:00","family":"awkward_offset","kind":"offset","prompt":"What is the UTC offset in effect in Waitangi, Chatham Islands, New Zealand at 12:00 local time on 2026-01-15? Answer with the offset in the form +HH:MM or -HH:MM.","expected":{"utc_offset":"+13:45"},"graded":true},{"id":"offset:chatham:2026-07-15:12:00","family":"awkward_offset","kind":"offset","prompt":"What is the UTC offset in effect in Waitangi, Chatham Islands, New Zealand at 12:00 local time on 2026-07-15? Answer with the offset in the form +HH:MM or -HH:MM.","expected":{"utc_offset":"+12:45"},"graded":true},{"id":"offset:lord_howe:2026-01-15:12:00","family":"awkward_offset","kind":"offset","prompt":"What is the UTC offset in effect in Lord Howe Island, Australia at 12:00 local time on 2026-01-15? Answer with the offset in the form +HH:MM or -HH:MM.","expected":{"utc_offset":"+11:00"},"graded":true},{"id":"offset:lord_howe:2026-07-15:12:00","family":"awkward_offset","kind":"offset","prompt":"What is the UTC offset in effect in Lord Howe Island, Australia at 12:00 local time on 2026-07-15? Answer with the offset in the form +HH:MM or -HH:MM.","expected":{"utc_offset":"+10:30"},"graded":true},{"id":"offset:eucla:2026-07-15:12:00","family":"awkward_offset","kind":"offset","prompt":"What is the UTC offset in effect in Eucla, Western Australia at 12:00 local time on 2026-07-15? Answer with the offset in the form +HH:MM or -HH:MM.","expected":{"utc_offset":"+08:45"},"graded":true},{"id":"offset:st_johns:2026-07-15:12:00","family":"awkward_offset","kind":"offset","prompt":"What is the UTC offset in effect in St. John's, Newfoundland and Labrador, Canada at 12:00 local time on 2026-07-15? Answer with the offset in the form +HH:MM or -HH:MM.","expected":{"utc_offset":"-02:30"},"graded":true},{"id":"offset:st_johns:2026-12-15:12:00","family":"awkward_offset","kind":"offset","prompt":"What is the UTC offset in effect in St. John's, Newfoundland and Labrador, Canada at 12:00 local time on 2026-12-15? Answer with the offset in the form +HH:MM or -HH:MM.","expected":{"utc_offset":"-03:30"},"graded":true},{"id":"offset:kiritimati:2026-07-15:12:00","family":"awkward_offset","kind":"offset","prompt":"What is the UTC offset in effect in Kiritimati, Line Islands, Kiribati at 12:00 local time on 2026-07-15? Answer with the offset in the form +HH:MM or -HH:MM.","expected":{"utc_offset":"+14:00"},"graded":true},{"id":"offset:marquesas:2026-07-15:12:00","family":"awkward_offset","kind":"offset","prompt":"What is the UTC offset in effect in Taiohae, Marquesas Islands, French Polynesia at 12:00 local time on 2026-07-15? Answer with the offset in the form +HH:MM or -HH:MM.","expected":{"utc_offset":"-09:30"},"graded":true},{"id":"offset:kabul:2026-07-15:12:00","family":"awkward_offset","kind":"offset","prompt":"What is the UTC offset in effect in Kabul, Afghanistan at 12:00 local time on 2026-07-15? Answer with the offset in the form +HH:MM or -HH:MM.","expected":{"utc_offset":"+04:30"},"graded":true},{"id":"offset:yangon:2026-07-15:12:00","family":"awkward_offset","kind":"offset","prompt":"What is the UTC offset in effect in Yangon, Myanmar at 12:00 local time on 2026-07-15? Answer with the offset in the form +HH:MM or -HH:MM.","expected":{"utc_offset":"+06:30"},"graded":true},{"id":"offset:adelaide:2026-01-15:12:00","family":"awkward_offset","kind":"offset","prompt":"What is the UTC offset in effect in Adelaide, South Australia at 12:00 local time on 2026-01-15? Answer with the offset in the form +HH:MM or -HH:MM.","expected":{"utc_offset":"+10:30"},"graded":true},{"id":"offset:adelaide:2026-07-15:12:00","family":"awkward_offset","kind":"offset","prompt":"What is the UTC offset in effect in Adelaide, South Australia at 12:00 local time on 2026-07-15? Answer with the offset in the form +HH:MM or -HH:MM.","expected":{"utc_offset":"+09:30"},"graded":true},{"id":"convert:kathmandu:new_york:2026-07-15:09:00","family":"awkward_offset","kind":"convert","prompt":"It is 09:00 on 2026-07-15 in Kathmandu, Nepal. What is the local date and time at that same moment in New York City, USA? Give the date as YYYY-MM-DD and the time as HH:MM in 24-hour format.","expected":{"date":"2026-07-14","time":"23:15"},"graded":true},{"id":"convert:st_johns:toronto:2026-07-15:09:00","family":"awkward_offset","kind":"convert","prompt":"It is 09:00 on 2026-07-15 in St. John's, Newfoundland and Labrador, Canada. What is the local date and time at that same moment in Toronto, Ontario, Canada? Give the date as YYYY-MM-DD and the time as HH:MM in 24-hour format.","expected":{"date":"2026-07-15","time":"07:30"},"graded":true},{"id":"convert:chatham:auckland:2026-01-15:09:00","family":"awkward_offset","kind":"convert","prompt":"It is 09:00 on 2026-01-15 in Waitangi, Chatham Islands, New Zealand. What is the local date and time at that same moment in Auckland, New Zealand? Give the date as YYYY-MM-DD and the time as HH:MM in 24-hour format.","expected":{"date":"2026-01-15","time":"08:15"},"graded":true},{"id":"convert:lord_howe:sydney:2026-07-15:09:00","family":"awkward_offset","kind":"convert","prompt":"It is 09:00 on 2026-07-15 in Lord Howe Island, Australia. What is the local date and time at that same moment in Sydney, New South Wales, Australia? Give the date as YYYY-MM-DD and the time as HH:MM in 24-hour format.","expected":{"date":"2026-07-15","time":"08:30"},"graded":true},{"id":"change_day:lord_howe:2026-10-04","family":"awkward_offset","kind":"change_day","prompt":"Do the clocks in Lord Howe Island, Australia change at any point during the local calendar day of 2026-10-04, either springing forward or falling back? Answer whether they change and, if so, in which direction.","expected":{"changes":true,"direction":"forward"},"graded":true},{"id":"change_day:chatham:2026-09-27","family":"awkward_offset","kind":"change_day","prompt":"Do the clocks in Waitangi, Chatham Islands, New Zealand change at any point during the local calendar day of 2026-09-27, either springing forward or falling back? Answer whether they change and, if so, in which direction.","expected":{"changes":true,"direction":"forward"},"graded":true},{"id":"change_day:st_johns:2026-11-01","family":"awkward_offset","kind":"change_day","prompt":"Do the clocks in St. John's, Newfoundland and Labrador, Canada change at any point during the local calendar day of 2026-11-01, either springing forward or falling back? Answer whether they change and, if so, in which direction.","expected":{"changes":true,"direction":"back"},"graded":true},{"id":"change_day:adelaide:2026-10-04","family":"awkward_offset","kind":"change_day","prompt":"Do the clocks in Adelaide, South Australia change at any point during the local calendar day of 2026-10-04, either springing forward or falling back? Answer whether they change and, if so, in which direction.","expected":{"changes":true,"direction":"forward"},"graded":true},{"id":"offset:santiago:2026-01-15:12:00","family":"southern","kind":"offset","prompt":"What is the UTC offset in effect in Santiago, Chile at 12:00 local time on 2026-01-15? Answer with the offset in the form +HH:MM or -HH:MM.","expected":{"utc_offset":"-03:00"},"graded":true},{"id":"offset:santiago:2026-07-15:12:00","family":"southern","kind":"offset","prompt":"What is the UTC offset in effect in Santiago, Chile at 12:00 local time on 2026-07-15? Answer with the offset in the form +HH:MM or -HH:MM.","expected":{"utc_offset":"-04:00"},"graded":true},{"id":"offset:auckland:2026-01-15:12:00","family":"southern","kind":"offset","prompt":"What is the UTC offset in effect in Auckland, New Zealand at 12:00 local time on 2026-01-15? Answer with the offset in the form +HH:MM or -HH:MM.","expected":{"utc_offset":"+13:00"},"graded":true},{"id":"offset:auckland:2026-07-15:12:00","family":"southern","kind":"offset","prompt":"What is the UTC offset in effect in Auckland, New Zealand at 12:00 local time on 2026-07-15? Answer with the offset in the form +HH:MM or -HH:MM.","expected":{"utc_offset":"+12:00"},"graded":true},{"id":"offset:sao_paulo:2026-01-15:12:00","family":"southern","kind":"offset","prompt":"What is the UTC offset in effect in S\u00e3o Paulo, Brazil at 12:00 local time on 2026-01-15? Answer with the offset in the form +HH:MM or -HH:MM.","expected":{"utc_offset":"-03:00"},"graded":true},{"id":"offset:windhoek:2026-07-15:12:00","family":"southern","kind":"offset","prompt":"What is the UTC offset in effect in Windhoek, Namibia at 12:00 local time on 2026-07-15? Answer with the offset in the form +HH:MM or -HH:MM.","expected":{"utc_offset":"+02:00"},"graded":true},{"id":"offset:johannesburg:2026-01-15:12:00","family":"southern","kind":"offset","prompt":"What is the UTC offset in effect in Johannesburg, South Africa at 12:00 local time on 2026-01-15? Answer with the offset in the form +HH:MM or -HH:MM.","expected":{"utc_offset":"+02:00"},"graded":true},{"id":"offset:melbourne:2026-04-15:12:00","family":"southern","kind":"offset","prompt":"What is the UTC offset in effect in Melbourne, Victoria, Australia at 12:00 local time on 2026-04-15? Answer with the offset in the form +HH:MM or -HH:MM.","expected":{"utc_offset":"+10:00"},"graded":true},{"id":"convert:santiago:new_york:2026-01-15:09:00","family":"southern","kind":"convert","prompt":"It is 09:00 on 2026-01-15 in Santiago, Chile. What is the local date and time at that same moment in New York City, USA? Give the date as YYYY-MM-DD and the time as HH:MM in 24-hour format.","expected":{"date":"2026-01-15","time":"07:00"},"graded":true},{"id":"convert:sydney:london:2026-04-01:09:00","family":"southern","kind":"convert","prompt":"It is 09:00 on 2026-04-01 in Sydney, New South Wales, Australia. What is the local date and time at that same moment in London, United Kingdom? Give the date as YYYY-MM-DD and the time as HH:MM in 24-hour format.","expected":{"date":"2026-03-31","time":"23:00"},"graded":true},{"id":"convert:auckland:los_angeles:2026-11-15:09:00","family":"southern","kind":"convert","prompt":"It is 09:00 on 2026-11-15 in Auckland, New Zealand. What is the local date and time at that same moment in Los Angeles, USA? Give the date as YYYY-MM-DD and the time as HH:MM in 24-hour format.","expected":{"date":"2026-11-14","time":"12:00"},"graded":true},{"id":"convert:sao_paulo:lisbon:2026-01-15:09:00","family":"southern","kind":"convert","prompt":"It is 09:00 on 2026-01-15 in S\u00e3o Paulo, Brazil. What is the local date and time at that same moment in Lisbon, Portugal? Give the date as YYYY-MM-DD and the time as HH:MM in 24-hour format.","expected":{"date":"2026-01-15","time":"12:00"},"graded":true},{"id":"offset:santiago:2026-04-10:12:00","family":"southern","kind":"offset","prompt":"What is the UTC offset in effect in Santiago, Chile at 12:00 local time on 2026-04-10? Answer with the offset in the form +HH:MM or -HH:MM.","expected":{"utc_offset":"-04:00"},"graded":true},{"id":"change_day:santiago:2026-09-06","family":"southern","kind":"change_day","prompt":"Do the clocks in Santiago, Chile change at any point during the local calendar day of 2026-09-06, either springing forward or falling back? Answer whether they change and, if so, in which direction.","expected":{"changes":true,"direction":"forward"},"graded":true},{"id":"change_day:sydney:2026-04-05","family":"southern","kind":"change_day","prompt":"Do the clocks in Sydney, New South Wales, Australia change at any point during the local calendar day of 2026-04-05, either springing forward or falling back? Answer whether they change and, if so, in which direction.","expected":{"changes":true,"direction":"back"},"graded":true},{"id":"change_day:sydney:2026-10-04","family":"southern","kind":"change_day","prompt":"Do the clocks in Sydney, New South Wales, Australia change at any point during the local calendar day of 2026-10-04, either springing forward or falling back? Answer whether they change and, if so, in which direction.","expected":{"changes":true,"direction":"forward"},"graded":true},{"id":"change_day:sao_paulo:2026-11-01","family":"southern","kind":"change_day","prompt":"Do the clocks in S\u00e3o Paulo, Brazil change at any point during the local calendar day of 2026-11-01, either springing forward or falling back? Answer whether they change and, if so, in which direction.","expected":{"changes":false,"direction":"none"},"graded":true},{"id":"change_day:auckland:2026-09-27","family":"southern","kind":"change_day","prompt":"Do the clocks in Auckland, New Zealand change at any point during the local calendar day of 2026-09-27, either springing forward or falling back? Answer whether they change and, if so, in which direction.","expected":{"changes":true,"direction":"forward"},"graded":true},{"id":"offset:tehran:2023-07-15:12:00","family":"legislated_2022_2025","kind":"offset","prompt":"What is the UTC offset in effect in Tehran, Iran at 12:00 local time on 2023-07-15? Answer with the offset in the form +HH:MM or -HH:MM.","expected":{"utc_offset":"+03:30"},"graded":true},{"id":"offset:amman:2023-01-15:12:00","family":"legislated_2022_2025","kind":"offset","prompt":"What is the UTC offset in effect in Amman, Jordan at 12:00 local time on 2023-01-15? Answer with the offset in the form +HH:MM or -HH:MM.","expected":{"utc_offset":"+03:00"},"graded":true},{"id":"offset:damascus:2023-07-15:12:00","family":"legislated_2022_2025","kind":"offset","prompt":"What is the UTC offset in effect in Damascus, Syria at 12:00 local time on 2023-07-15? Answer with the offset in the form +HH:MM or -HH:MM.","expected":{"utc_offset":"+03:00"},"graded":true},{"id":"offset:mexico_city:2023-07-15:12:00","family":"legislated_2022_2025","kind":"offset","prompt":"What is the UTC offset in effect in Mexico City, Mexico at 12:00 local time on 2023-07-15? Answer with the offset in the form +HH:MM or -HH:MM.","expected":{"utc_offset":"-06:00"},"graded":true},{"id":"offset:mexico_city:2024-07-15:12:00","family":"legislated_2022_2025","kind":"offset","prompt":"What is the UTC offset in effect in Mexico City, Mexico at 12:00 local time on 2024-07-15? Answer with the offset in the form +HH:MM or -HH:MM.","expected":{"utc_offset":"-06:00"},"graded":true},{"id":"offset:chihuahua:2023-01-15:12:00","family":"legislated_2022_2025","kind":"offset","prompt":"What is the UTC offset in effect in Chihuahua City, Chihuahua, Mexico at 12:00 local time on 2023-01-15? Answer with the offset in the form +HH:MM or -HH:MM.","expected":{"utc_offset":"-06:00"},"graded":true},{"id":"offset:nuuk:2024-01-15:12:00","family":"legislated_2022_2025","kind":"offset","prompt":"What is the UTC offset in effect in Nuuk, Greenland at 12:00 local time on 2024-01-15? Answer with the offset in the form +HH:MM or -HH:MM.","expected":{"utc_offset":"-02:00"},"graded":true},{"id":"offset:nuuk:2024-07-15:12:00","family":"legislated_2022_2025","kind":"offset","prompt":"What is the UTC offset in effect in Nuuk, Greenland at 12:00 local time on 2024-07-15? Answer with the offset in the form +HH:MM or -HH:MM.","expected":{"utc_offset":"-01:00"},"graded":true},{"id":"offset:ittoqqortoormiit:2024-07-15:12:00","family":"legislated_2022_2025","kind":"offset","prompt":"What is the UTC offset in effect in Ittoqqortoormiit (Scoresbysund), Greenland at 12:00 local time on 2024-07-15? Answer with the offset in the form +HH:MM or -HH:MM.","expected":{"utc_offset":"-01:00"},"graded":true},{"id":"offset:cairo:2023-07-15:12:00","family":"legislated_2022_2025","kind":"offset","prompt":"What is the UTC offset in effect in Cairo, Egypt at 12:00 local time on 2023-07-15? Answer with the offset in the form +HH:MM or -HH:MM.","expected":{"utc_offset":"+03:00"},"graded":true},{"id":"offset:cairo:2024-07-15:12:00","family":"legislated_2022_2025","kind":"offset","prompt":"What is the UTC offset in effect in Cairo, Egypt at 12:00 local time on 2024-07-15? Answer with the offset in the form +HH:MM or -HH:MM.","expected":{"utc_offset":"+03:00"},"graded":true},{"id":"offset:almaty:2024-07-15:12:00","family":"legislated_2022_2025","kind":"offset","prompt":"What is the UTC offset in effect in Almaty, Kazakhstan at 12:00 local time on 2024-07-15? Answer with the offset in the form +HH:MM or -HH:MM.","expected":{"utc_offset":"+05:00"},"graded":true},{"id":"offset:almaty:2025-01-15:12:00","family":"legislated_2022_2025","kind":"offset","prompt":"What is the UTC offset in effect in Almaty, Kazakhstan at 12:00 local time on 2025-01-15? Answer with the offset in the form +HH:MM or -HH:MM.","expected":{"utc_offset":"+05:00"},"graded":true},{"id":"offset:asuncion:2025-06-15:12:00","family":"legislated_2022_2025","kind":"offset","prompt":"What is the UTC offset in effect in Asunci\u00f3n, Paraguay at 12:00 local time on 2025-06-15? Answer with the offset in the form +HH:MM or -HH:MM.","expected":{"utc_offset":"-03:00"},"graded":true},{"id":"offset:asuncion:2025-01-15:12:00","family":"legislated_2022_2025","kind":"offset","prompt":"What is the UTC offset in effect in Asunci\u00f3n, Paraguay at 12:00 local time on 2025-01-15? Answer with the offset in the form +HH:MM or -HH:MM.","expected":{"utc_offset":"-03:00"},"graded":true},{"id":"offset:coyhaique:2025-07-15:12:00","family":"legislated_2022_2025","kind":"offset","prompt":"What is the UTC offset in effect in Coyhaique, Ays\u00e9n Region, Chile at 12:00 local time on 2025-07-15? Answer with the offset in the form +HH:MM or -HH:MM.","expected":{"utc_offset":"-03:00"},"graded":true},{"id":"offset:suva:2023-01-15:12:00","family":"legislated_2022_2025","kind":"offset","prompt":"What is the UTC offset in effect in Suva, Fiji at 12:00 local time on 2023-01-15? Answer with the offset in the form +HH:MM or -HH:MM.","expected":{"utc_offset":"+12:00"},"graded":true},{"id":"convert:mexico_city:chicago:2023-07-15:09:00","family":"legislated_2022_2025","kind":"convert","prompt":"It is 09:00 on 2023-07-15 in Mexico City, Mexico. What is the local date and time at that same moment in Chicago, USA? Give the date as YYYY-MM-DD and the time as HH:MM in 24-hour format.","expected":{"date":"2023-07-15","time":"10:00"},"graded":true},{"id":"convert:almaty:moscow:2024-07-15:09:00","family":"legislated_2022_2025","kind":"convert","prompt":"It is 09:00 on 2024-07-15 in Almaty, Kazakhstan. What is the local date and time at that same moment in Moscow, Russia? Give the date as YYYY-MM-DD and the time as HH:MM in 24-hour format.","expected":{"date":"2024-07-15","time":"07:00"},"graded":true},{"id":"convert:asuncion:buenos_aires:2025-06-15:09:00","family":"legislated_2022_2025","kind":"convert","prompt":"It is 09:00 on 2025-06-15 in Asunci\u00f3n, Paraguay. What is the local date and time at that same moment in Buenos Aires, Argentina? Give the date as YYYY-MM-DD and the time as HH:MM in 24-hour format.","expected":{"date":"2025-06-15","time":"09:00"},"graded":true},{"id":"convert:tehran:dubai:2023-07-15:09:00","family":"legislated_2022_2025","kind":"convert","prompt":"It is 09:00 on 2023-07-15 in Tehran, Iran. What is the local date and time at that same moment in Dubai, United Arab Emirates? Give the date as YYYY-MM-DD and the time as HH:MM in 24-hour format.","expected":{"date":"2023-07-15","time":"09:30"},"graded":true},{"id":"convert:cairo:athens:2023-07-15:09:00","family":"legislated_2022_2025","kind":"convert","prompt":"It is 09:00 on 2023-07-15 in Cairo, Egypt. What is the local date and time at that same moment in Athens, Greece? Give the date as YYYY-MM-DD and the time as HH:MM in 24-hour format.","expected":{"date":"2023-07-15","time":"09:00"},"graded":true},{"id":"convert:amman:jerusalem:2023-01-15:09:00","family":"legislated_2022_2025","kind":"convert","prompt":"It is 09:00 on 2023-01-15 in Amman, Jordan. What is the local date and time at that same moment in Jerusalem? Give the date as YYYY-MM-DD and the time as HH:MM in 24-hour format.","expected":{"date":"2023-01-15","time":"08:00"},"graded":true},{"id":"change_day:mexico_city:2023-04-02","family":"legislated_2022_2025","kind":"change_day","prompt":"Do the clocks in Mexico City, Mexico change at any point during the local calendar day of 2023-04-02, either springing forward or falling back? Answer whether they change and, if so, in which direction.","expected":{"changes":false,"direction":"none"},"graded":true},{"id":"change_day:mexico_city:2022-10-30","family":"legislated_2022_2025","kind":"change_day","prompt":"Do the clocks in Mexico City, Mexico change at any point during the local calendar day of 2022-10-30, either springing forward or falling back? Answer whether they change and, if so, in which direction.","expected":{"changes":true,"direction":"back"},"graded":true},{"id":"change_day:tehran:2023-03-22","family":"legislated_2022_2025","kind":"change_day","prompt":"Do the clocks in Tehran, Iran change at any point during the local calendar day of 2023-03-22, either springing forward or falling back? Answer whether they change and, if so, in which direction.","expected":{"changes":false,"direction":"none"},"graded":true},{"id":"change_day:amman:2022-10-28","family":"legislated_2022_2025","kind":"change_day","prompt":"Do the clocks in Amman, Jordan change at any point during the local calendar day of 2022-10-28, either springing forward or falling back? Answer whether they change and, if so, in which direction.","expected":{"changes":false,"direction":"none"},"graded":true},{"id":"change_day:cairo:2023-04-28","family":"legislated_2022_2025","kind":"change_day","prompt":"Do the clocks in Cairo, Egypt change at any point during the local calendar day of 2023-04-28, either springing forward or falling back? Answer whether they change and, if so, in which direction.","expected":{"changes":true,"direction":"forward"},"graded":true},{"id":"offset:almaty:2024-03-05:12:00","family":"legislated_2022_2025","kind":"offset","prompt":"What is the UTC offset in effect in Almaty, Kazakhstan at 12:00 local time on 2024-03-05? Answer with the offset in the form +HH:MM or -HH:MM.","expected":{"utc_offset":"+05:00"},"graded":true},{"id":"offset:asuncion:2025-03-25:12:00","family":"legislated_2022_2025","kind":"offset","prompt":"What is the UTC offset in effect in Asunci\u00f3n, Paraguay at 12:00 local time on 2025-03-25? Answer with the offset in the form +HH:MM or -HH:MM.","expected":{"utc_offset":"-03:00"},"graded":true},{"id":"change_day:asuncion:2024-10-06","family":"legislated_2022_2025","kind":"change_day","prompt":"Do the clocks in Asunci\u00f3n, Paraguay change at any point during the local calendar day of 2024-10-06, either springing forward or falling back? Answer whether they change and, if so, in which direction.","expected":{"changes":true,"direction":"forward"},"graded":true},{"id":"offset:vancouver:2026-11-15:12:00","family":"wave_2026","kind":"offset","prompt":"What is the UTC offset in effect in Vancouver, British Columbia, Canada at 12:00 local time on 2026-11-15? Answer with the offset in the form +HH:MM or -HH:MM.","expected":{"utc_offset":"-07:00"},"graded":true},{"id":"offset:vancouver:2026-12-15:12:00","family":"wave_2026","kind":"offset","prompt":"What is the UTC offset in effect in Vancouver, British Columbia, Canada at 12:00 local time on 2026-12-15? Answer with the offset in the form +HH:MM or -HH:MM.","expected":{"utc_offset":"-07:00"},"graded":true},{"id":"offset:vancouver:2026-07-15:12:00","family":"wave_2026","kind":"offset","prompt":"What is the UTC offset in effect in Vancouver, British Columbia, Canada at 12:00 local time on 2026-07-15? Answer with the offset in the form +HH:MM or -HH:MM.","expected":{"utc_offset":"-07:00"},"graded":true},{"id":"offset:fort_nelson:2026-11-15:12:00","family":"wave_2026","kind":"offset","prompt":"What is the UTC offset in effect in Fort Nelson, British Columbia, Canada at 12:00 local time on 2026-11-15? Answer with the offset in the form +HH:MM or -HH:MM.","expected":{"utc_offset":"-07:00"},"graded":true},{"id":"offset:calgary:2026-11-15:12:00","family":"wave_2026","kind":"offset","prompt":"What is the UTC offset in effect in Calgary, Alberta, Canada at 12:00 local time on 2026-11-15? Answer with the offset in the form +HH:MM or -HH:MM.","expected":{"utc_offset":"-06:00"},"graded":true},{"id":"offset:edmonton:2026-12-15:12:00","family":"wave_2026","kind":"offset","prompt":"What is the UTC offset in effect in Edmonton, Alberta, Canada at 12:00 local time on 2026-12-15? Answer with the offset in the form +HH:MM or -HH:MM.","expected":{"utc_offset":"-06:00"},"graded":true},{"id":"offset:yellowknife:2026-11-15:12:00","family":"wave_2026","kind":"offset","prompt":"What is the UTC offset in effect in Yellowknife, Northwest Territories, Canada at 12:00 local time on 2026-11-15? Answer with the offset in the form +HH:MM or -HH:MM.","expected":{"utc_offset":"-06:00"},"graded":true},{"id":"offset:inuvik:2026-11-15:12:00","family":"wave_2026","kind":"offset","prompt":"What is the UTC offset in effect in Inuvik, Northwest Territories, Canada at 12:00 local time on 2026-11-15? Answer with the offset in the form +HH:MM or -HH:MM.","expected":{"utc_offset":"-06:00"},"graded":true},{"id":"offset:casablanca:2026-10-15:12:00","family":"wave_2026","kind":"offset","prompt":"What is the UTC offset in effect in Casablanca, Morocco at 12:00 local time on 2026-10-15? Answer with the offset in the form +HH:MM or -HH:MM.","expected":{"utc_offset":"+00:00"},"graded":true},{"id":"offset:casablanca:2026-12-15:12:00","family":"wave_2026","kind":"offset","prompt":"What is the UTC offset in effect in Casablanca, Morocco at 12:00 local time on 2026-12-15? Answer with the offset in the form +HH:MM or -HH:MM.","expected":{"utc_offset":"+00:00"},"graded":true},{"id":"convert:calgary:toronto:2026-11-15:09:00","family":"wave_2026","kind":"convert","prompt":"It is 09:00 on 2026-11-15 in Calgary, Alberta, Canada. What is the local date and time at that same moment in Toronto, Ontario, Canada? Give the date as YYYY-MM-DD and the time as HH:MM in 24-hour format.","expected":{"date":"2026-11-15","time":"10:00"},"graded":true},{"id":"convert:vancouver:seattle:2026-11-15:09:00","family":"wave_2026","kind":"convert","prompt":"It is 09:00 on 2026-11-15 in Vancouver, British Columbia, Canada. What is the local date and time at that same moment in Seattle, Washington, USA? Give the date as YYYY-MM-DD and the time as HH:MM in 24-hour format.","expected":{"date":"2026-11-15","time":"08:00"},"graded":true},{"id":"convert:calgary:denver:2026-11-15:09:00","family":"wave_2026","kind":"convert","prompt":"It is 09:00 on 2026-11-15 in Calgary, Alberta, Canada. What is the local date and time at that same moment in Denver, Colorado, USA? Give the date as YYYY-MM-DD and the time as HH:MM in 24-hour format.","expected":{"date":"2026-11-15","time":"08:00"},"graded":true},{"id":"convert:casablanca:paris:2026-10-15:09:00","family":"wave_2026","kind":"convert","prompt":"It is 09:00 on 2026-10-15 in Casablanca, Morocco. What is the local date and time at that same moment in Paris, France? Give the date as YYYY-MM-DD and the time as HH:MM in 24-hour format.","expected":{"date":"2026-10-15","time":"11:00"},"graded":true},{"id":"convert:casablanca:london:2026-12-15:09:00","family":"wave_2026","kind":"convert","prompt":"It is 09:00 on 2026-12-15 in Casablanca, Morocco. What is the local date and time at that same moment in London, United Kingdom? Give the date as YYYY-MM-DD and the time as HH:MM in 24-hour format.","expected":{"date":"2026-12-15","time":"09:00"},"graded":true},{"id":"convert:inuvik:toronto:2026-11-15:09:00","family":"wave_2026","kind":"convert","prompt":"It is 09:00 on 2026-11-15 in Inuvik, Northwest Territories, Canada. What is the local date and time at that same moment in Toronto, Ontario, Canada? Give the date as YYYY-MM-DD and the time as HH:MM in 24-hour format.","expected":{"date":"2026-11-15","time":"10:00"},"graded":true},{"id":"change_day:vancouver:2026-11-01","family":"wave_2026","kind":"change_day","prompt":"Do the clocks in Vancouver, British Columbia, Canada change at any point during the local calendar day of 2026-11-01, either springing forward or falling back? Answer whether they change and, if so, in which direction.","expected":{"changes":false,"direction":"none"},"graded":true},{"id":"change_day:calgary:2026-11-01","family":"wave_2026","kind":"change_day","prompt":"Do the clocks in Calgary, Alberta, Canada change at any point during the local calendar day of 2026-11-01, either springing forward or falling back? Answer whether they change and, if so, in which direction.","expected":{"changes":false,"direction":"none"},"graded":true},{"id":"change_day:edmonton:2026-11-01","family":"wave_2026","kind":"change_day","prompt":"Do the clocks in Edmonton, Alberta, Canada change at any point during the local calendar day of 2026-11-01, either springing forward or falling back? Answer whether they change and, if so, in which direction.","expected":{"changes":false,"direction":"none"},"graded":true},{"id":"change_day:yellowknife:2026-11-01","family":"wave_2026","kind":"change_day","prompt":"Do the clocks in Yellowknife, Northwest Territories, Canada change at any point during the local calendar day of 2026-11-01, either springing forward or falling back? Answer whether they change and, if so, in which direction.","expected":{"changes":false,"direction":"none"},"graded":true},{"id":"change_day:inuvik:2026-11-01","family":"wave_2026","kind":"change_day","prompt":"Do the clocks in Inuvik, Northwest Territories, Canada change at any point during the local calendar day of 2026-11-01, either springing forward or falling back? Answer whether they change and, if so, in which direction.","expected":{"changes":false,"direction":"none"},"graded":true},{"id":"change_day:casablanca:2026-09-20","family":"wave_2026","kind":"change_day","prompt":"Do the clocks in Casablanca, Morocco change at any point during the local calendar day of 2026-09-20, either springing forward or falling back? Answer whether they change and, if so, in which direction.","expected":{"changes":true,"direction":"back"},"graded":true},{"id":"change_day:vancouver:2026-03-08","family":"wave_2026","kind":"change_day","prompt":"Do the clocks in Vancouver, British Columbia, Canada change at any point during the local calendar day of 2026-03-08, either springing forward or falling back? Answer whether they change and, if so, in which direction.","expected":{"changes":true,"direction":"forward"},"graded":true},{"id":"change_day:fort_nelson:2026-11-01","family":"wave_2026","kind":"change_day","prompt":"Do the clocks in Fort Nelson, British Columbia, Canada change at any point during the local calendar day of 2026-11-01, either springing forward or falling back? Answer whether they change and, if so, in which direction.","expected":{"changes":false,"direction":"none"},"graded":true},{"id":"change_day:seattle:2026-11-01","family":"wave_2026","kind":"change_day","prompt":"Do the clocks in Seattle, Washington, USA change at any point during the local calendar day of 2026-11-01, either springing forward or falling back? Answer whether they change and, if so, in which direction.","expected":{"changes":true,"direction":"back"},"graded":true},{"id":"offset:winnipeg:2026-11-15:12:00","family":"unresolved","kind":"offset","prompt":"What is the UTC offset in effect in Winnipeg, Manitoba, Canada at 12:00 local time on 2026-11-15? Answer with the offset in the form +HH:MM or -HH:MM.","expected":{"utc_offset":"-06:00"},"graded":false},{"id":"change_day:winnipeg:2026-11-01","family":"unresolved","kind":"change_day","prompt":"Do the clocks in Winnipeg, Manitoba, Canada change at any point during the local calendar day of 2026-11-01, either springing forward or falling back? Answer whether they change and, if so, in which direction.","expected":{"changes":true,"direction":"back"},"graded":false},{"id":"convert:winnipeg:toronto:2026-11-15:09:00","family":"unresolved","kind":"convert","prompt":"It is 09:00 on 2026-11-15 in Winnipeg, Manitoba, Canada. What is the local date and time at that same moment in Toronto, Ontario, Canada? Give the date as YYYY-MM-DD and the time as HH:MM in 24-hour format.","expected":{"date":"2026-11-15","time":"10:00"},"graded":false}]""")

# %% [markdown]
# ## The answer schemas
#
# Structured output keeps grading deterministic. The `note` field is the model's one
# sentence about which rule it applied; it is recorded, never graded.

# %%
@dataclass
class OffsetAnswer:
    utc_offset: str  # "+HH:MM" or "-HH:MM"
    note: str  # one sentence naming the rule applied


@dataclass
class ConvertAnswer:
    date: str  # YYYY-MM-DD
    time: str  # HH:MM, 24-hour
    note: str  # one sentence naming the offsets used


@dataclass
class ChangeDayAnswer:
    changes: bool
    direction: str  # "forward", "back" or "none"
    note: str  # one sentence


SCHEMAS = {"offset": OffsetAnswer, "convert": ConvertAnswer, "change_day": ChangeDayAnswer}

FIELD_HINTS = {
    "offset": (
        " Return utc_offset as a string in the form +HH:MM or -HH:MM, and note as one "
        "sentence naming the rule you applied."
    ),
    "convert": (
        " Return date as YYYY-MM-DD, time as HH:MM in 24-hour format, and note as one "
        "sentence naming the UTC offsets you used for each place."
    ),
    "change_day": (
        " Return changes as true or false, direction as exactly one of 'forward', 'back' "
        "or 'none', and note as one sentence."
    ),
}

SYSTEM = (
    "You answer questions about local time, UTC offsets and clock changes. Use your best "
    "knowledge of the rules actually in force on the date asked, including any recent "
    "changes to daylight saving time or time zones. Do not refuse and do not say you "
    "cannot know: give your single best answer and fill every field."
)
if CONDITION == "tool":
    SYSTEM += (
        " A function tool called zone_clock is available. It reads the IANA time zone "
        "database. You may call it if you want to, or answer without it."
    )

# %% [markdown]
# ## The tool (only offered in the `tool` condition)
#
# `zone_clock` reads tzdata 2026d, pinned inside the kernel so the answer does not depend
# on whatever tz database the Kaggle image happens to ship.

# %%
def _pin_tzdata() -> str:
    """Install the exact tzdata release and point zoneinfo at it. Returns the IANA version."""
    import importlib
    import zoneinfo

    try:
        import tzdata

        if getattr(tzdata, "__version__", "") != TZDATA_PYPI:
            raise ImportError("wrong tzdata version")
    except ImportError:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-q", f"tzdata=={TZDATA_PYPI}"],
            check=False,
        )
        import tzdata

        importlib.reload(tzdata)
    root = os.path.join(os.path.dirname(tzdata.__file__), "zoneinfo")
    zoneinfo.reset_tzpath(to=[root])
    zoneinfo.ZoneInfo.clear_cache()
    return tzdata.IANA_VERSION


TZDATA_LOADED = _pin_tzdata() if CONDITION == "tool" else None


def zone_clock(iana_zone: str, local_datetime: str) -> dict:
    """Read the IANA time zone database (tzdata 2026d, released September 2026) for one zone at one local wall-clock time.

    Args:
        iana_zone: An IANA zone key such as 'America/Edmonton', 'Europe/London' or 'Africa/Casablanca'.
        local_datetime: A local wall-clock date and time in ISO 8601 format such as '2026-11-15T09:00'.

    Returns the UTC offset in force at that local time, the zone abbreviation, whether
    daylight saving time is in effect, and the UTC offsets in force at the end of the
    previous day and at the end of that day, which show whether the clocks change during
    that day.
    """
    import zoneinfo
    from datetime import datetime, timedelta

    try:
        tz = zoneinfo.ZoneInfo(iana_zone)
    except Exception:
        return {
            "isError": True,
            "errorCategory": "validation",
            "isRetryable": False,
            "message": f"{iana_zone!r} is not an IANA zone key in tzdata {TZDATA_LOADED}. Use a key such as 'America/Edmonton'.",
        }
    try:
        local = datetime.fromisoformat(local_datetime)
    except ValueError:
        return {
            "isError": True,
            "errorCategory": "validation",
            "isRetryable": False,
            "message": f"could not parse local_datetime {local_datetime!r}; use ISO 8601 such as '2026-11-15T09:00'.",
        }
    local = local.replace(tzinfo=tz)

    def fmt(td: timedelta) -> str:
        total = int(td.total_seconds())
        sign = "+" if total >= 0 else "-"
        total = abs(total)
        return f"{sign}{total // 3600:02d}:{(total % 3600) // 60:02d}"

    day = local.date()
    end_today = datetime(day.year, day.month, day.day, 23, 59, 59, tzinfo=tz, fold=1)
    yday = day - timedelta(days=1)
    end_yesterday = datetime(yday.year, yday.month, yday.day, 23, 59, 59, tzinfo=tz, fold=1)
    return {
        "tzdata_release": TZDATA_LOADED,
        "iana_zone": iana_zone,
        "local_datetime": local.strftime("%Y-%m-%dT%H:%M"),
        "utc_offset": fmt(local.utcoffset()),
        "abbreviation": local.tzname(),
        "is_dst": bool(local.dst()),
        "utc_offset_end_of_previous_day": fmt(end_yesterday.utcoffset()),
        "utc_offset_end_of_this_day": fmt(end_today.utcoffset()),
        "clocks_change_during_this_day": end_yesterday.utcoffset() != end_today.utcoffset(),
    }


# %% [markdown]
# ## Grading
#
# Answers are normalised before comparison so that `UTC-6`, `-6:00` and `−06:00` all read
# as `-06:00`. Nothing else is forgiven: a wrong hour is a wrong hour.

# %%
_OFFSET_RE = re.compile(r"([+\-−–])?\s*(\d{1,2})(?::?(\d{2}))?")


def norm_offset(text) -> str:
    s = str(text).strip().upper().replace("UTC", "").replace("GMT", "").replace("Z", "")
    s = s.replace("−", "-").replace("–", "-").strip()
    m = _OFFSET_RE.search(s)
    if not m:
        return f"unparsed:{text!r}"
    sign = "-" if m.group(1) == "-" else "+"
    hours = int(m.group(2))
    minutes = int(m.group(3) or 0)
    if hours > 14 or minutes > 59:
        return f"unparsed:{text!r}"
    return f"{sign}{hours:02d}:{minutes:02d}"


_TIME_RE = re.compile(r"(\d{1,2}):(\d{2})\s*(AM|PM|A\.M\.|P\.M\.)?", re.IGNORECASE)
_DATE_RE = re.compile(r"(\d{4})-(\d{1,2})-(\d{1,2})")


def norm_time(text) -> str:
    m = _TIME_RE.search(str(text))
    if not m:
        return f"unparsed:{text!r}"
    h, mi = int(m.group(1)), int(m.group(2))
    ampm = (m.group(3) or "").replace(".", "").upper()
    if ampm == "PM" and h < 12:
        h += 12
    if ampm == "AM" and h == 12:
        h = 0
    if h > 23 or mi > 59:
        return f"unparsed:{text!r}"
    return f"{h:02d}:{mi:02d}"


def norm_date(text) -> str:
    m = _DATE_RE.search(str(text))
    if not m:
        return f"unparsed:{text!r}"
    return f"{int(m.group(1)):04d}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"


def norm_direction(text) -> str:
    s = str(text).strip().lower()
    if s.startswith("forw") or "ahead" in s or "spring" in s:
        return "forward"
    if s.startswith("back") or "behind" in s or "fall" in s:
        return "back"
    return "none"


def normalise(kind: str, answer) -> dict:
    if kind == "offset":
        return {"utc_offset": norm_offset(getattr(answer, "utc_offset", answer))}
    if kind == "convert":
        return {"date": norm_date(getattr(answer, "date", "")), "time": norm_time(getattr(answer, "time", ""))}
    changes = bool(getattr(answer, "changes", False))
    direction = norm_direction(getattr(answer, "direction", "none")) if changes else "none"
    return {"changes": changes, "direction": direction}


def count_tool_calls(chat) -> int:
    n = 0
    for item in chat.history:
        if isinstance(item, kbench.chats.Chat):
            n += count_tool_calls(item)
        elif isinstance(getattr(item, "content", None), tool_base.ToolInvocationResult):
            n += 1
    return n


TRANSIENT = ("429", "rate_limit", "heavy load", "exceeds your available quota", "502", "503", "overloaded", "timeout")
CAP_NAMES = ("max_tokens", "max_completion_tokens")


def _call(llm, prompt: str, schema, tools, extra: dict | None):
    """One attempt. Without tools this is llm.prompt. With tools it is the SDK's own tool
    loop, called directly so the round limit can be raised above prompt()'s fixed 10."""
    if not tools:
        return llm.prompt(prompt, schema=schema, extra_api_params=extra)
    kbench.user.send(prompt)
    kwargs = {
        "seed": 0,
        "temperature": 0 if getattr(llm, "support_temperature", False) else None,
        "reasoning": None,
    }
    if extra:
        kwargs.update(extra)
    message = tool_native.native_tool_agent(
        llm, tools, schema=schema, max_tool_rounds=MAX_TOOL_ROUNDS, **kwargs
    )
    return message.content


def salvage(schema, error_text: str):
    """Recover a structured answer from a parse failure the SDK gave up on.

    Some models return visible reasoning before the JSON (DeepSeek-R1 wraps it in think
    tags), which the SDK's parser rejects as "Expecting value: line 1 column 1". The
    failure message carries the raw response, so the last complete JSON object in it is
    parsed here and handed to the schema. Returns None when nothing usable is there,
    which is what a response truncated mid-string looks like.
    """
    marker = "Input Value:"
    body = error_text.split(marker, 1)[1] if marker in error_text else error_text
    body = body.split("Target Schema:", 1)[0]
    if "</think>" in body:
        body = body.split("</think>")[-1]
    end = body.rfind("}")
    while end != -1:
        depth = 0
        start = None
        for i in range(end, -1, -1):
            if body[i] == "}":
                depth += 1
            elif body[i] == "{":
                depth -= 1
                if depth == 0:
                    start = i
                    break
        if start is None:
            return None
        try:
            data = json.loads(body[start : end + 1])
        except ValueError:
            end = body.rfind("}", 0, end)
            continue
        if isinstance(data, dict):
            fields = {f for f in getattr(schema, "__dataclass_fields__", {})}
            try:
                return schema(**{k: v for k, v in data.items() if k in fields})
            except TypeError:
                return None
        return None
    return None


def ask(llm, prompt: str, schema, tools=None):
    """A model call with an output-token cap and retries.

    Nested evaluations run with max_attempts=1 whatever the caller asks, so transient
    proxy errors (429 under load, quota reservation refused) have to be retried here.
    Some backends reject `max_tokens` and want `max_completion_tokens`; the cap name
    falls through on that error. A response cut off by the cap gets another try at
    double the cap. A response the SDK could not parse is salvaged from its raw text
    when a complete JSON object is in there. Anything else is raised as is.
    """
    cap_index = 0
    cap = MAX_TOKENS
    delay = 5
    last: Exception | None = None
    for _ in range(10):
        extra = {CAP_NAMES[cap_index]: cap} if cap_index < len(CAP_NAMES) else None
        try:
            return _call(llm, prompt, schema, tools, extra)
        except Exception as exc:  # noqa: BLE001
            last = exc
            msg = str(exc)
            low = msg.lower()
            if "unsupported" in low and any(name in low for name in CAP_NAMES):
                cap_index += 1
                continue
            if "response parsing failed" in low:
                recovered = salvage(schema, msg)
                if recovered is not None:
                    return recovered
                if cap >= MAX_CAP:
                    raise
                cap = min(cap * 2, MAX_CAP)
                continue
            if "length limit was reached" in low or "lengthfinishreason" in low:
                if cap >= MAX_CAP:
                    raise
                cap = min(cap * 2, MAX_CAP)
                continue
            if any(t in low for t in TRANSIENT):
                time.sleep(delay)
                delay = min(delay * 2, 60)
                continue
            raise
    assert last is not None
    raise last


# %% [markdown]
# ## One case

# %%
@kbench.task(name="world_clock_case", store_task=False)
def world_clock_case(llm, id, family, kind, prompt, expected_json, graded) -> dict:
    expected = json.loads(expected_json)
    schema = SCHEMAS[kind]
    full_prompt = prompt + FIELD_HINTS[kind]
    tool_calls = 0
    with kbench.chats.new(f"case {id}", system_instructions=SYSTEM) as chat:
        if CONDITION == "tool":
            answer = ask(llm, full_prompt, schema, tools=[zone_clock])
            tool_calls = count_tool_calls(chat)
        else:
            answer = ask(llm, full_prompt, schema)
        usage = getattr(chat, "usage", None)
    got = normalise(kind, answer)
    correct = got == expected
    note = str(getattr(answer, "note", ""))[:400]
    if graded:
        kbench.assertions.assert_true(
            correct,
            expectation=(
                f"[{family}] {prompt} Expected {json.dumps(expected)} per tzdata {TZDATA_IANA}; "
                f"model answered {json.dumps(got)}."
            ),
        )
    return {
        "id": id,
        "family": family,
        "kind": kind,
        "graded": bool(graded),
        "expected": expected,
        "answer": got,
        "correct": bool(correct),
        "note": note,
        "tool_calls": tool_calls,
        "input_tokens": getattr(usage, "input_tokens", None),
        "output_tokens": getattr(usage, "output_tokens", None),
        "latency_ms": getattr(usage, "total_backend_latency_ms", None),
    }


# %% [markdown]
# ## The benchmark

# %%
def select_cases(cases: list[dict], limit: int) -> list[dict]:
    """Stratified round-robin over families so a smoke test touches every bucket."""
    if not limit or limit >= len(cases):
        return cases
    by_family: dict[str, list[dict]] = {}
    for c in cases:
        by_family.setdefault(c["family"], []).append(c)
    picked: list[dict] = []
    while len(picked) < limit:
        progressed = False
        for fam in by_family:
            if by_family[fam] and len(picked) < limit:
                picked.append(by_family[fam].pop(0))
                progressed = True
        if not progressed:
            break
    return picked


def cases_frame() -> pd.DataFrame:
    rows = []
    for c in select_cases(CASES, LIMIT):
        rows.append(
            {
                "id": c["id"],
                "family": c["family"],
                "kind": c["kind"],
                "prompt": c["prompt"],
                "expected_json": json.dumps(c["expected"], sort_keys=True),
                "graded": bool(c["graded"]),
            }
        )
    return pd.DataFrame(rows)


@kbench.task(
    name=TASK_NAME,
    description="A stratified 20-case subset of the from-memory task, graded against tzdata 2026d. Used to check the pipeline before spending quota on the full lineup.",
)
def world_clock_smoke(llm) -> tuple[int, int]:
    df = cases_frame()
    with kbench.client.enable_cache():
        # No per-job timeout: joblib's TimeoutError escapes on_failure="continue" and
        # kills the whole run, which is how eleven models were lost on 2026-09-27.
        results = world_clock_case.evaluate(
            llm=[llm],
            evaluation_data=df,
            n_jobs=N_JOBS,
            timeout=None,
            on_failure="continue",
            max_attempts=1,
            remove_run_files=True,
        )
    completed = results.completed_runs
    rows = [r.result for r in completed]
    def _tail(msg) -> str:
        lines = [ln for ln in str(msg or "").strip().splitlines() if ln.strip()]
        return lines[-1][:400] if lines else ""

    errored = [
        {"params": {k: v for k, v in r.params.items() if k != "llm"}, "error": _tail(getattr(r, "error_message", ""))}
        for r in results.errored_runs
    ]

    graded_rows = [r for r in rows if r["graded"]]
    correct = sum(1 for r in graded_rows if r["correct"])
    total = len(graded_rows)

    by_family: dict[str, list[int]] = {}
    for r in graded_rows:
        by_family.setdefault(r["family"], []).append(int(r["correct"]))
    summary = {fam: {"correct": sum(v), "total": len(v)} for fam, v in by_family.items()}

    out = {
        "task": TASK_NAME,
        "condition": CONDITION,
        "tzdata_release": TZDATA_IANA,
        "model": getattr(llm, "model", None) or getattr(llm, "name", str(llm)),
        "graded_correct": correct,
        "graded_total": total,
        "errored": errored,
        "by_family": summary,
        "rows": rows,
    }
    with open("world_clock_answers.json", "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    print(f"{TASK_NAME}: {correct}/{total} graded cases correct; {len(errored)} errored")
    for fam, s in summary.items():
        print(f"  {fam:22s} {s['correct']:3d}/{s['total']}")
    print("WORLD_CLOCK_ANSWERS_JSON " + json.dumps(out, ensure_ascii=True))
    return correct, total


# %%
run = world_clock_smoke.run(kbench.llm)
run
