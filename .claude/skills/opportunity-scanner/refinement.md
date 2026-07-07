# Refining the rubric over time

This is one instance of the shared lifecycle in `../../../RUBRICS.md`
(generate → log → resolve → hill-climb → repeat) — this doc covers the
specifics for this rubric; see that doc for the general process and for
how the option-suggestion rubric follows the same pattern.

There's no automated gradient descent here — not enough data volume for
that, and no formal loss function to optimize. What's actually practical
at this account's cadence (a few decisions a quarter) is **evidence-based
manual tuning**: log every scored candidate, check back on what actually
happened, and adjust weights/thresholds when the evidence supports it.
Call it hill-climbing in spirit, not in algorithm — a human-and-agent
review loop, run quarterly, not a continuously-optimizing system.

## The log

`reports/opportunity-scanner-log.csv` — one row per candidate scored,
ever. Columns: `date_scanned, ticker, archetype, total_score,
category_a..category_e` (subtotals), `price_at_scan,
pct_off_high_at_scan`, then **one column per individual rubric
criterion** — `a1_pctoffhigh` through `e32_fitstyle_judgment`, matching
`rubric.md`'s 32 numbered criteria exactly — followed by `outcome_1q,
outcome_1y`.

**Every criterion cell is either a real score or the literal string
`N/A`** — never a silent 0. `N/A` means the criterion genuinely wasn't
computed this run (missing data, a tool gap, or a `[J]` judgment call that
wasn't actually made); a `0` means it was computed and failed. Conflating
the two would misrepresent gaps as failures and corrupt the very evidence
`rubric-engine` reads later — see the 2026-07-07 rebuild for why this
matters: several criteria previously carried a flat placeholder value
(e.g. leverage/catalyst/fit-style judgment defaulted to a fixed +1 for
every row) that looked like real per-candidate assessment but wasn't;
those are now honestly `N/A`.

Append a row every time step 6 of `SKILL.md` produces a scored candidate
— including ones that don't make the shortlist, not just the winners,
otherwise there's no way to tell whether low scores were actually avoided
for good reason later.

## The quarterly review

Each time this skill runs (or at minimum once a quarter even if not run
for new candidates), for every row logged ≥1 quarter ago:
1. Pull the current price (`get_equity_quotes`) and compute the actual
   return since `price_at_scan`.
2. Add `outcome_1q`, `outcome_1y` columns to that row as they become
   available (don't overwrite — a candidate might look bad at 1 quarter
   and good at 1 year, both data points matter).
3. Look for patterns across the accumulated rows: which category
   subtotals actually correlate with good outcomes so far? Which
   criteria fired on both winners and losers (i.e., aren't
   discriminating, like category A alone in the HOOD/CVNA/PTON test)?

## What "refining" means concretely

- **Reweight**, don't just re-thumbs-up: if a criterion never
  distinguishes winners from losers across enough logged cases, lower
  its point value in `rubric.md` and say why, citing the specific rows.
  If one keeps showing up disproportionately in the good outcomes,
  raise it.
- **Adjust thresholds**, not just weights: e.g. if ≥40% off high turns
  out too loose (lets through too many that don't pay off) or too tight
  (excludes cases that later worked), move the threshold and note the
  evidence.
- **Add criteria the log reveals are missing**: if a pattern shows up
  repeatedly in the outcomes that nothing in the current 32 criteria
  captures, that's a real signal to add one — grounded in logged
  evidence, not a guess.
- **Never refine on fewer than ~5 resolved cases per category** — the
  validation experiment (see `validation.md`) used 4 cases and that was
  enough to prove category A alone doesn't discriminate, but that's a
  qualitative existence-proof, not a sample size to reweight numeric
  point values from. Small-sample tuning risks fitting noise; say so if
  ever tempted to reweight off 2–3 data points.

## Cadence

Update the log every time the scanner runs. Do the "what actually
happened" review pass once a quarter, paired with the scan cadence in
`SKILL.md` — not more often; there isn't enough new resolved evidence
week to week to justify it.
