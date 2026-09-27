"""The curated case list for the World Clock benchmark.

Nothing here is an answer. A spec names a place, a moment, and a question type, and
`build_cases.py` computes the answer from the IANA database under every tzdata release
since 2022. The families below are the analysis buckets used in the post.

Place names are written the way a person would type them into a chat window, with
enough context to be unambiguous, and never with an IANA zone key, which would be a hint.
"""

from __future__ import annotations

# place key -> (display name for prompts, IANA zone, fallback zone if the key does not
# exist in an older tzdata release). A fallback is what that place actually used before
# it got its own zone, so the answer key stays honest for old releases.
PLACES: dict[str, tuple[str, str, str | None]] = {
    # controls
    "new_york": ("New York City, USA", "America/New_York", None),
    "london": ("London, United Kingdom", "Europe/London", None),
    "paris": ("Paris, France", "Europe/Paris", None),
    "berlin": ("Berlin, Germany", "Europe/Berlin", None),
    "tokyo": ("Tokyo, Japan", "Asia/Tokyo", None),
    "los_angeles": ("Los Angeles, USA", "America/Los_Angeles", None),
    "seattle": ("Seattle, Washington, USA", "America/Los_Angeles", None),
    "chicago": ("Chicago, USA", "America/Chicago", None),
    "denver": ("Denver, Colorado, USA", "America/Denver", None),
    "phoenix": ("Phoenix, Arizona, USA", "America/Phoenix", None),
    "toronto": ("Toronto, Ontario, Canada", "America/Toronto", None),
    "mumbai": ("Mumbai, India", "Asia/Kolkata", None),
    "dubai": ("Dubai, United Arab Emirates", "Asia/Dubai", None),
    "moscow": ("Moscow, Russia", "Europe/Moscow", None),
    "athens": ("Athens, Greece", "Europe/Athens", None),
    "lisbon": ("Lisbon, Portugal", "Europe/Lisbon", None),
    "jerusalem": ("Jerusalem", "Asia/Jerusalem", None),
    "buenos_aires": ("Buenos Aires, Argentina", "America/Argentina/Buenos_Aires", None),
    # awkward offsets
    "kathmandu": ("Kathmandu, Nepal", "Asia/Kathmandu", None),
    "chatham": ("Waitangi, Chatham Islands, New Zealand", "Pacific/Chatham", None),
    "lord_howe": ("Lord Howe Island, Australia", "Australia/Lord_Howe", None),
    "eucla": ("Eucla, Western Australia", "Australia/Eucla", None),
    "st_johns": ("St. John's, Newfoundland and Labrador, Canada", "America/St_Johns", None),
    "kiritimati": ("Kiritimati, Line Islands, Kiribati", "Pacific/Kiritimati", None),
    "marquesas": ("Taiohae, Marquesas Islands, French Polynesia", "Pacific/Marquesas", None),
    "kabul": ("Kabul, Afghanistan", "Asia/Kabul", None),
    "yangon": ("Yangon, Myanmar", "Asia/Yangon", None),
    "adelaide": ("Adelaide, South Australia", "Australia/Adelaide", None),
    "auckland": ("Auckland, New Zealand", "Pacific/Auckland", None),
    "sydney": ("Sydney, New South Wales, Australia", "Australia/Sydney", None),
    "melbourne": ("Melbourne, Victoria, Australia", "Australia/Melbourne", None),
    # southern hemisphere
    "santiago": ("Santiago, Chile", "America/Santiago", None),
    "sao_paulo": ("São Paulo, Brazil", "America/Sao_Paulo", None),
    "windhoek": ("Windhoek, Namibia", "Africa/Windhoek", None),
    "johannesburg": ("Johannesburg, South Africa", "Africa/Johannesburg", None),
    # legislated changes 2022 to 2025
    "tehran": ("Tehran, Iran", "Asia/Tehran", None),
    "amman": ("Amman, Jordan", "Asia/Amman", None),
    "damascus": ("Damascus, Syria", "Asia/Damascus", None),
    "mexico_city": ("Mexico City, Mexico", "America/Mexico_City", None),
    "chihuahua": ("Chihuahua City, Chihuahua, Mexico", "America/Chihuahua", None),
    "nuuk": ("Nuuk, Greenland", "America/Nuuk", "America/Godthab"),
    "ittoqqortoormiit": ("Ittoqqortoormiit (Scoresbysund), Greenland", "America/Scoresbysund", None),
    "cairo": ("Cairo, Egypt", "Africa/Cairo", None),
    "almaty": ("Almaty, Kazakhstan", "Asia/Almaty", None),
    "asuncion": ("Asunción, Paraguay", "America/Asuncion", None),
    "coyhaique": ("Coyhaique, Aysén Region, Chile", "America/Coyhaique", "America/Santiago"),
    "suva": ("Suva, Fiji", "Pacific/Fiji", None),
    # the 2026 wave
    "vancouver": ("Vancouver, British Columbia, Canada", "America/Vancouver", None),
    "fort_nelson": ("Fort Nelson, British Columbia, Canada", "America/Fort_Nelson", None),
    "calgary": ("Calgary, Alberta, Canada", "America/Edmonton", None),
    "edmonton": ("Edmonton, Alberta, Canada", "America/Edmonton", None),
    "yellowknife": ("Yellowknife, Northwest Territories, Canada", "America/Yellowknife", None),
    "inuvik": ("Inuvik, Northwest Territories, Canada", "America/Inuvik", None),
    "casablanca": ("Casablanca, Morocco", "Africa/Casablanca", None),
    # unresolved
    "winnipeg": ("Winnipeg, Manitoba, Canada", "America/Winnipeg", None),
}

# Each spec: (family, kind, payload)
#   kind "offset":     payload = (place, "YYYY-MM-DD", "HH:MM")
#   kind "convert":    payload = (from_place, to_place, "YYYY-MM-DD", "HH:MM")
#   kind "change_day": payload = (place, "YYYY-MM-DD")
SPECS: list[tuple[str, str, tuple]] = [
    # ---------------------------------------------------------------- controls
    ("control", "offset", ("new_york", "2026-07-15", "12:00")),
    ("control", "offset", ("new_york", "2026-12-15", "12:00")),
    ("control", "offset", ("london", "2026-07-15", "12:00")),
    ("control", "offset", ("london", "2026-12-15", "12:00")),
    ("control", "offset", ("tokyo", "2026-07-15", "12:00")),
    ("control", "offset", ("paris", "2026-01-15", "12:00")),
    ("control", "offset", ("los_angeles", "2026-11-15", "12:00")),
    ("control", "offset", ("toronto", "2026-11-15", "12:00")),
    ("control", "offset", ("sydney", "2026-01-15", "12:00")),
    ("control", "offset", ("sydney", "2026-07-15", "12:00")),
    ("control", "offset", ("mumbai", "2026-07-15", "12:00")),
    ("control", "offset", ("dubai", "2026-07-15", "12:00")),
    ("control", "convert", ("new_york", "london", "2026-07-15", "09:00")),
    ("control", "convert", ("tokyo", "los_angeles", "2026-03-10", "09:00")),
    ("control", "convert", ("toronto", "paris", "2026-11-15", "09:00")),
    ("control", "convert", ("london", "sydney", "2026-01-15", "09:00")),
    ("control", "convert", ("chicago", "mumbai", "2026-07-15", "09:00")),
    ("control", "convert", ("berlin", "tokyo", "2026-12-15", "09:00")),
    ("control", "change_day", ("new_york", "2026-03-08")),
    ("control", "change_day", ("new_york", "2026-11-01")),
    ("control", "change_day", ("london", "2026-03-29")),
    ("control", "change_day", ("london", "2026-10-25")),
    ("control", "change_day", ("toronto", "2026-11-01")),
    ("control", "change_day", ("tokyo", "2026-03-08")),
    ("control", "change_day", ("paris", "2026-10-25")),
    ("control", "change_day", ("phoenix", "2026-03-08")),
    # --------------------------------------------------------- awkward offsets
    ("awkward_offset", "offset", ("kathmandu", "2026-07-15", "12:00")),
    ("awkward_offset", "offset", ("chatham", "2026-01-15", "12:00")),
    ("awkward_offset", "offset", ("chatham", "2026-07-15", "12:00")),
    ("awkward_offset", "offset", ("lord_howe", "2026-01-15", "12:00")),
    ("awkward_offset", "offset", ("lord_howe", "2026-07-15", "12:00")),
    ("awkward_offset", "offset", ("eucla", "2026-07-15", "12:00")),
    ("awkward_offset", "offset", ("st_johns", "2026-07-15", "12:00")),
    ("awkward_offset", "offset", ("st_johns", "2026-12-15", "12:00")),
    ("awkward_offset", "offset", ("kiritimati", "2026-07-15", "12:00")),
    ("awkward_offset", "offset", ("marquesas", "2026-07-15", "12:00")),
    ("awkward_offset", "offset", ("kabul", "2026-07-15", "12:00")),
    ("awkward_offset", "offset", ("yangon", "2026-07-15", "12:00")),
    ("awkward_offset", "offset", ("adelaide", "2026-01-15", "12:00")),
    ("awkward_offset", "offset", ("adelaide", "2026-07-15", "12:00")),
    ("awkward_offset", "convert", ("kathmandu", "new_york", "2026-07-15", "09:00")),
    ("awkward_offset", "convert", ("st_johns", "toronto", "2026-07-15", "09:00")),
    ("awkward_offset", "convert", ("chatham", "auckland", "2026-01-15", "09:00")),
    ("awkward_offset", "convert", ("lord_howe", "sydney", "2026-07-15", "09:00")),
    ("awkward_offset", "change_day", ("lord_howe", "2026-10-04")),
    ("awkward_offset", "change_day", ("chatham", "2026-09-27")),
    ("awkward_offset", "change_day", ("st_johns", "2026-11-01")),
    ("awkward_offset", "change_day", ("adelaide", "2026-10-04")),
    # ------------------------------------------------------ southern hemisphere
    ("southern", "offset", ("santiago", "2026-01-15", "12:00")),
    ("southern", "offset", ("santiago", "2026-07-15", "12:00")),
    ("southern", "offset", ("auckland", "2026-01-15", "12:00")),
    ("southern", "offset", ("auckland", "2026-07-15", "12:00")),
    ("southern", "offset", ("sao_paulo", "2026-01-15", "12:00")),
    ("southern", "offset", ("windhoek", "2026-07-15", "12:00")),
    ("southern", "offset", ("johannesburg", "2026-01-15", "12:00")),
    ("southern", "offset", ("melbourne", "2026-04-15", "12:00")),
    ("southern", "convert", ("santiago", "new_york", "2026-01-15", "09:00")),
    ("southern", "convert", ("sydney", "london", "2026-04-01", "09:00")),
    ("southern", "convert", ("auckland", "los_angeles", "2026-11-15", "09:00")),
    ("southern", "convert", ("sao_paulo", "lisbon", "2026-01-15", "09:00")),
    # Chile falls back at 24:00 Saturday, which lands on a day boundary, so the April
    # change is probed as an offset a few days later instead of as a change-day question.
    ("southern", "offset", ("santiago", "2026-04-10", "12:00")),
    ("southern", "change_day", ("santiago", "2026-09-06")),
    ("southern", "change_day", ("sydney", "2026-04-05")),
    ("southern", "change_day", ("sydney", "2026-10-04")),
    ("southern", "change_day", ("sao_paulo", "2026-11-01")),
    ("southern", "change_day", ("auckland", "2026-09-27")),
    # ------------------------------------------- legislated changes 2022 to 2025
    ("legislated_2022_2025", "offset", ("tehran", "2023-07-15", "12:00")),
    ("legislated_2022_2025", "offset", ("amman", "2023-01-15", "12:00")),
    ("legislated_2022_2025", "offset", ("damascus", "2023-07-15", "12:00")),
    ("legislated_2022_2025", "offset", ("mexico_city", "2023-07-15", "12:00")),
    ("legislated_2022_2025", "offset", ("mexico_city", "2024-07-15", "12:00")),
    ("legislated_2022_2025", "offset", ("chihuahua", "2023-01-15", "12:00")),
    ("legislated_2022_2025", "offset", ("nuuk", "2024-01-15", "12:00")),
    ("legislated_2022_2025", "offset", ("nuuk", "2024-07-15", "12:00")),
    ("legislated_2022_2025", "offset", ("ittoqqortoormiit", "2024-07-15", "12:00")),
    ("legislated_2022_2025", "offset", ("cairo", "2023-07-15", "12:00")),
    ("legislated_2022_2025", "offset", ("cairo", "2024-07-15", "12:00")),
    ("legislated_2022_2025", "offset", ("almaty", "2024-07-15", "12:00")),
    ("legislated_2022_2025", "offset", ("almaty", "2025-01-15", "12:00")),
    ("legislated_2022_2025", "offset", ("asuncion", "2025-06-15", "12:00")),
    ("legislated_2022_2025", "offset", ("asuncion", "2025-01-15", "12:00")),
    ("legislated_2022_2025", "offset", ("coyhaique", "2025-07-15", "12:00")),
    ("legislated_2022_2025", "offset", ("suva", "2023-01-15", "12:00")),
    ("legislated_2022_2025", "convert", ("mexico_city", "chicago", "2023-07-15", "09:00")),
    ("legislated_2022_2025", "convert", ("almaty", "moscow", "2024-07-15", "09:00")),
    ("legislated_2022_2025", "convert", ("asuncion", "buenos_aires", "2025-06-15", "09:00")),
    ("legislated_2022_2025", "convert", ("tehran", "dubai", "2023-07-15", "09:00")),
    ("legislated_2022_2025", "convert", ("cairo", "athens", "2023-07-15", "09:00")),
    ("legislated_2022_2025", "convert", ("amman", "jerusalem", "2023-01-15", "09:00")),
    ("legislated_2022_2025", "change_day", ("mexico_city", "2023-04-02")),
    ("legislated_2022_2025", "change_day", ("mexico_city", "2022-10-30")),
    ("legislated_2022_2025", "change_day", ("tehran", "2023-03-22")),
    ("legislated_2022_2025", "change_day", ("amman", "2022-10-28")),
    ("legislated_2022_2025", "change_day", ("cairo", "2023-04-28")),
    # Kazakhstan's unification and Paraguay's old fall-back both happened at 00:00, on a
    # day boundary, so they are probed as offsets shortly after instead.
    ("legislated_2022_2025", "offset", ("almaty", "2024-03-05", "12:00")),
    ("legislated_2022_2025", "offset", ("asuncion", "2025-03-25", "12:00")),
    ("legislated_2022_2025", "change_day", ("asuncion", "2024-10-06")),
    # -------------------------------------------------------------- 2026 wave
    ("wave_2026", "offset", ("vancouver", "2026-11-15", "12:00")),
    ("wave_2026", "offset", ("vancouver", "2026-12-15", "12:00")),
    ("wave_2026", "offset", ("vancouver", "2026-07-15", "12:00")),
    ("wave_2026", "offset", ("fort_nelson", "2026-11-15", "12:00")),
    ("wave_2026", "offset", ("calgary", "2026-11-15", "12:00")),
    ("wave_2026", "offset", ("edmonton", "2026-12-15", "12:00")),
    ("wave_2026", "offset", ("yellowknife", "2026-11-15", "12:00")),
    ("wave_2026", "offset", ("inuvik", "2026-11-15", "12:00")),
    ("wave_2026", "offset", ("casablanca", "2026-10-15", "12:00")),
    ("wave_2026", "offset", ("casablanca", "2026-12-15", "12:00")),
    ("wave_2026", "convert", ("calgary", "toronto", "2026-11-15", "09:00")),
    ("wave_2026", "convert", ("vancouver", "seattle", "2026-11-15", "09:00")),
    ("wave_2026", "convert", ("calgary", "denver", "2026-11-15", "09:00")),
    ("wave_2026", "convert", ("casablanca", "paris", "2026-10-15", "09:00")),
    ("wave_2026", "convert", ("casablanca", "london", "2026-12-15", "09:00")),
    ("wave_2026", "convert", ("inuvik", "toronto", "2026-11-15", "09:00")),
    ("wave_2026", "change_day", ("vancouver", "2026-11-01")),
    ("wave_2026", "change_day", ("calgary", "2026-11-01")),
    ("wave_2026", "change_day", ("edmonton", "2026-11-01")),
    ("wave_2026", "change_day", ("yellowknife", "2026-11-01")),
    ("wave_2026", "change_day", ("inuvik", "2026-11-01")),
    ("wave_2026", "change_day", ("casablanca", "2026-09-20")),
    ("wave_2026", "change_day", ("vancouver", "2026-03-08")),
    ("wave_2026", "change_day", ("fort_nelson", "2026-11-01")),
    ("wave_2026", "change_day", ("seattle", "2026-11-01")),
    # -------------------------------------------------------------- unresolved
    # Manitoba announced permanent daylight time on 2026-09-17. No tzdata release has
    # it yet, so these are recorded, reported separately, and never counted in accuracy.
    ("unresolved", "offset", ("winnipeg", "2026-11-15", "12:00")),
    ("unresolved", "change_day", ("winnipeg", "2026-11-01")),
    ("unresolved", "convert", ("winnipeg", "toronto", "2026-11-15", "09:00")),
]

# What the government has announced for the unresolved cases, so the post can show the
# official answer beside the tzdata answer. Source: Manitoba news release 75397 (Sept 17,
# 2026) and the tz mailing list's unreleased entry modelling permanent -05 as EST.
OFFICIAL_ANSWERS: dict[tuple[str, tuple], dict] = {
    ("offset", ("winnipeg", "2026-11-15", "12:00")): {"utc_offset": "-05:00"},
    ("change_day", ("winnipeg", "2026-11-01")): {"changes": False, "direction": "none"},
    ("convert", ("winnipeg", "toronto", "2026-11-15", "09:00")): {"date": "2026-11-15", "time": "09:00"},
}
