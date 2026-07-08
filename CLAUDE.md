# Project instructions

Personal, read-only Robinhood portfolio-analysis system. These rules apply
across every skill in this repo. Skill-specific detail (exact filters,
thresholds, scan IDs, point values) lives in `.claude/skills/*/SKILL.md`,
`.claude/skills/opportunity-scanner/rubric.md`, and `RUBRICS.md` — this
file is for behavior that should hold regardless of which skill is
running, not a place to duplicate that detail.

## Never place an order

Every skill here is read-only analysis/suggestions. Never call
`place_equity_order` or `place_option_order` from any skill's own logic.
If the user wants to act on a suggestion, that's a separate, explicit
conversation they initiate — don't chain into it automatically.

## Never fabricate a score, default, or placeholder value

If a value wasn't actually computed, the field is `N/A` — never a flat
default (`0`, `1`, a copied neighbor value) that looks like a real result.
`N/A` (not computed) and `0` (computed and scored zero) mean different
things and must never be conflated. This was violated once early in this
project (several judgment criteria were silently defaulted to `+1` and
looked like real scores) and had to be found and fixed — don't
reintroduce it in any log, rubric, or report.

## Verify against the live API before trusting docs or training knowledge

Scanner filter behavior, MCP tool availability, and data completeness have
each diverged from what documentation or intuition suggested at least once
in this project (three scanner filter types are permanently broken
server-side regardless of parameters; `get_equity_fundamentals` never
returns margin/ROE/ROA no matter what the schema implies; a whole new data
connector was being evaluated before discovering `get_equity_historicals`/
`get_option_historicals` already covered the gap). When a tool's behavior
matters for a scoring or filtering decision, test it live rather than
assuming.

## Verify fetchability on a real test ticker before adding or keeping a rubric criterion

"The data exists somewhere" is not the same as "this criterion is
fetchable in the actual daily workflow." Category C of the
opportunity-scanner rubric had 6 criteria marked "computable from
historicals" in `reports/rubric-data-sources.csv` for weeks — true for one
ticker in isolation, but the calculation code to actually produce a score
was never written, so those cells sat `N/A` for every candidate, every
run. That's the failure mode to prevent: a criterion that's theoretically
possible but never actually verified against a live tool call becomes
permanent dead weight in the rubric.

Before adding a new criterion (or when auditing why a rubric has too many
`N/A`s), pick one real test ticker and actually run the exact fetch/
calculation the criterion needs, live — not "the docs say this field
exists," an actual returned value. Log the attempt (method tried, result,
sample value) to a verification CSV (see `reports/rubric-fetch-
verification-*.csv` for the format). If the first approach fails, try a
genuinely different one (different params, different tool, a client-side
calculation from raw historicals instead of a broken scanner filter)
before concluding a criterion isn't fetchable. Only keep a criterion in
the *scored* rubric once it's actually been produced a real value on the
test ticker — a criterion that's still "not yet implemented" after that
check belongs in a follow-up task, not silently in the live rubric
generating N/A rows.

## Disqualifying criteria are gates, not scores

A criterion that's already enforced identically for every candidate that
reaches a rubric (e.g. a Stage-0 scan-level filter) must never *also* be a
scored point criterion downstream — it can't discriminate anything if it's
guaranteed true for 100% of rows, and double-representing it just inflates
the total misleadingly. More generally: when the user's intent for a
criterion is "skip stocks that fail this" rather than "average this into
the score," implement it as a hard gate — stop scoring immediately on
failure, log a minimal disqualified row, don't carry the candidate through
the rest of the rubric with wasted effort. Don't default a new criterion
to "scored" just because most existing ones are; ask which behavior is
intended if it's not obvious from how the user described it.

## Never mutate a live saved scan without reverting immediately

Adding filters to `update_scan_filters` to surface a column's data can
silently drop instruments that lack a computable value for *any* active
filter — not just leave that column blank for them. If probing a scan for
extra data, capture the result and revert the scan's filters back to its
documented baseline in the very next call, and verify `total_items`
matches the baseline after reverting before trusting anything else.

## Backward-compatible logging

Never rename, remove, or renumber an existing log column or rubric
criterion once rows have been logged against it — always append new ones
at the end, even when that breaks "logical" ordering. Exception: a
same-day, same-run correction (e.g. retiring a criterion minutes after it
was scored, before any outcome-resolution time has passed) can be backed
out of that day's own rows. That's different from retroactively rescoring
a locked historical dataset from a prior day, which is never allowed
(`RUBRICS.md` Stage 5).

## Log every candidate, not just the winners

Every survivor of a Stage-0 prefilter gets a row — including ones a later
gate disqualifies or that score low. A minimal "disqualified, here's why"
row is still a data point worth having for future correlation analysis;
silently dropping it isn't.

## Rubric/strategy changes go through the changelog

Any change to a scan filter, a rubric weight/threshold, or a criterion's
existence gets logged to `reports/rubric-changelog.csv` (id, timestamp,
rubric, category, change, status) alongside making the change — whether
it's evidence-driven (a `rubric-engine` hill-climb proposal) or
user-directed (a stated preference, logged as such, not dressed up as
evidence it isn't). See `RUBRICS.md` for the full lifecycle.

## Opportunity-scanner logs are one file per run, not appended

`reports/opportunity-scanner-logs/` holds one CSV per run, not a single
ever-growing appended file (changed 2026-07-07 — the old
`reports/opportunity-scanner-log.csv` is kept only as a historical
snapshot, don't append to it going forward). Anything that reads
historical rows across multiple runs (e.g. `rubric-engine`) globs across
the directory rather than assuming one fixed path.

## Trading preferences (see skill docs for full detail/rationale)

- `GOOG`: never suggest an option trade on this name, in either direction.
- Cash-secured puts are the default; covered calls are secondary, and when
  used, strikes go well past the standard delta screen toward "almost
  impossible to settle."
- Low-frequency, high-conviction account — a few trades per quarter, not
  active/daily trading. Don't design any workflow here around a faster
  cadence than that.
- Risk-averse opportunity screening: positive-profit-only prefilter across
  every archetype, and a domain-leadership gate (top-tier or solid niche
  leader, 10-year-hold durability) that disqualifies sub-scale/
  commoditized/easily-disrupted candidates outright.
