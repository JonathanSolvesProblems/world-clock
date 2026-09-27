# The post, written before the first commit

Working title (N and M filled from `results/summary.json` after the run, never by hand):

> Alberta stopped changing its clocks in June. N of M frontier models still turn them back on November 1.

Domain-free tagline, for the first line under the title:

> Every model's world clock is frozen at its training cutoff. I dated each one to the month.

## The 90-second version (this is also the outline of the DEV post)

1. **The hook, one paragraph.** On June 18, 2026 Alberta passed the Official Time Act and stopped
   changing its clocks. British Columbia had done it in March, the Northwest Territories followed in
   August, Morocco went back to plain UTC on September 20, and Manitoba announced on September 17
   that it will not fall back on November 1. CBC is reporting calendar chaos in Calgary. Microsoft
   published interim Windows guidance. So I asked the question a developer in Calgary asks: if I
   have a 9 a.m. call with Toronto on November 15, what time is it there? Then I asked every model
   on Kaggle Benchmarks.

2. **The grader.** Every answer is checked against the IANA time zone database, release 2026d, the
   same file that runs the clock on the reader's phone. I did not write the answer key. Four releases
   a year rewrite it, so the benchmark never goes stale.

3. **The test.** Six families of cases, all generated from public records:
   - controls: stable zones and textbook conversions (this is where Test of Time 2024 reported
     74 to 90 percent, so the models should be near perfect here)
   - awkward offsets: Kathmandu +05:45, Chatham +12:45, Lord Howe's 30-minute DST, Eucla +08:45
   - southern hemisphere DST: Santiago, Sydney, Auckland, Asunción before and after 2024
   - legislated changes 2022 to 2025: Iran, Jordan, Syria, Mexico, Greenland, Egypt, Kazakhstan,
     Paraguay, Chile's Aysén
   - the 2026 wave: BC, Alberta, NWT, Morocco
   - the unknowable case: Manitoba on November 1, announced but in no tzdata release

4. **The number.** For each model: wrong answers per hundred, by family. Then the dating trick: run
   the same answer sheet against every tzdata release since 2022a and report the release each model
   agrees with most. That puts a month on the model's world clock.

5. **The ablation.** Same cases, three ways: from memory; with a one-line `utc_offset()` tool backed
   by tzdata 2026d; with the SDK's web search tool. The question is not only whether the tool fixes
   it, but whether the model calls the tool when it already believes it knows.

6. **The live case.** Manitoba has said it will not fall back on November 1. No tzdata release has
   it yet. Every model was asked what Winnipeg does on that morning. The right answer, today, is
   "it depends on a release that has not shipped", and I record who hedged and who asserted. Winners
   are announced November 5. The reader will know the answer before the judges do.

7. **What surprised me, what I would measure next.** Filled from the data, not from this script.

8. **Where to see it.** Kaggle benchmark link, public repo, `check_claims.py` that fails the build if
   a number in this post disagrees with `results/summary.json`.

## What is deliberately not in the post

- No architecture section. The SDK, the DataFrame evaluate, the structured output schema are one
  sentence each inside the method.
- No self-graded number. Every score is agreement with IANA.
- The tool-use result is a section, not the thesis. The thesis is the frozen clock.

## Human at the centre

The developer in Calgary who missed a call is the subject of sentence one. If a real person from the
CBC or Microsoft coverage can be named and quoted, they lead. If not, the sentence stays first person.
