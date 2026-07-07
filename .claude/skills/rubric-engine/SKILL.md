---
name: rubric-engine
description: Quarterly hill-climb review for a rubric-based strategy — resolves outcomes on logged candidates, checks which rubric categories actually discriminate good calls from bad ones, and drafts an evidence-cited rubric change for human approval. Use for "run the quarterly rubric review", "check if the opportunity-scanner rubric needs adjusting", "is the option-suggestion strategy actually working", "hill-climb the rubric". Never auto-applies a change — always proposes, human decides. See RUBRIC-ENGINE.md and RUBRICS.md for the system design and lifecycle this implements.
---

# Rubric engine

Implements Stages 3–4 of `../../../RUBRICS.md` (resolve outcomes,
hill-climb) for whichever rubric is being reviewed. Read-only against
trading tools — this skill never places an order and never edits a
rubric file without an explicit user approval step. Works against any
rubric registered in `RUBRICS.md`'s "Today's instances" table; as of
writing that's two:

| Target | Rubric | Log | Resolution horizon |
|---|---|---|---|
| `opportunity-scanner` | `.claude/skills/opportunity-scanner/rubric.md` | `reports/opportunity-scanner-log.csv` | 1 quarter (`outcome_1q`), 1 year (`outcome_1y`) |
| `option-suggestion` | `.claude/skills/portfolio-report/playbooks/option-suggestion-rubric.md` | `reports/option-suggestion-log.csv` | option's own expiration date |

If the user names a target ambiguously ("check the rubric"), ask which
one rather than guessing — the two have different resolution horizons and
different log schemas.

## Step 1 — Resolve outcomes

Read the target's log CSV. For every row whose resolution horizon has
passed and whose outcome columns are still blank:

- **opportunity-scanner rows**: pull the current price
  (`get_equity_quotes`) and compute return since `price_at_scan`. Fill
  `outcome_1q` if ≥1 quarter has passed since `date_scanned`, `outcome_1y`
  if ≥1 year has passed. Don't overwrite an already-filled outcome column
  — a row can pick up `outcome_1q` this quarter and `outcome_1y` a year
  from now, both are kept.
- **option-suggestion rows**: for rows where `expiration` has passed (or
  `executed` shows a real fill), check `get_option_positions` /
  `get_option_orders` to determine `outcome` (`expired_worthless`,
  `assigned`, `rolled`, `closed_early`, or `not_executed` for skips) and
  compute `realized_pnl` per `tax-basics.md`'s roll-netting method where
  relevant.

Write the filled-in rows back to the CSV. This step is purely factual — no
judgment calls yet, that's step 3.

## Step 2 — Correlation analysis

For the opportunity-scanner log, the per-criterion columns
(`a1_pctoffhigh` through `e32_fitstyle_judgment`) let this run at the
individual-criterion level, not just the category subtotal — do it at
**both** levels:

- **Per-criterion**: for each of the 32 columns, split resolved rows into
  those where the criterion scored well vs. poorly (skip any row where
  that cell is `N/A` — it wasn't computed, it's not evidence either way)
  and compare `outcome_1q`/`outcome_1y`. This is what actually answers
  "does this specific criterion predict anything," not just "does
  Category A as a whole."
- **Per-category**: bucket resolved rows by category subscore
  (high/medium/low) and compare outcomes, same as before — useful for
  spotting a category-level pattern even when no single criterion inside
  it is individually decisive.
- option-suggestion: rate of `verdict = good_call` per bucket (apply the
  CSP/covered-call asymmetric verdict logic from
  `option-suggestion-refinement.md` — assignment isn't automatically bad).

Report the bucket/criterion comparison **and the N in each bucket,
excluding `N/A` rows from that N** — a criterion that "looks"
discriminating on 3 non-`N/A` resolved rows is not evidence, it's noise;
say so plainly rather than presenting it as a finding. A criterion that's
`N/A` on most rows (e.g. Category C right now, or `a4_stochastic` given
the broken scanner filter) isn't ready for correlation analysis at all —
report it as "insufficient real data," not as a weak finding.

## Step 2b — Literature refresh

Before drafting proposals from internal evidence alone, spend one pass
checking whether new academic or practitioner research has come out since
the last review that bears on a category under consideration (per
`RUBRICS.md`'s "research is ongoing, not a one-time pass"). Use `WebSearch`
for this — don't rely on memory for anything published after the last
review. This is a second, independent input into Step 3's proposals, not
a replacement for the logged-outcome evidence: a criterion can get
proposed for revision because the internal log shows it isn't
discriminating, because new external research undercuts its premise, or
both — cite whichever actually applies, and don't manufacture a citation
to justify a change the log evidence alone already supports.

## Step 3 — Draft a proposal (only where evidence supports it)

For any category with **≥5 resolved cases** where the bucket comparison
shows a real gap (not just directionally different by a row or two):

- Draft a specific, numeric change — a new weight, a new threshold, a new
  criterion to add, or a criterion to retire — not a vague "seems like
  this matters more."
- Cite the exact rows (dates/tickers or dates/symbols) that justify it.
- For every category with **<5 resolved cases**, explicitly report "not
  enough evidence yet" rather than staying silent — the absence of a
  proposal should be visible, not just implied.

Never propose changing more than one category at a time from a single
review unless the evidence independently supports each — bundling changes
makes it impossible to tell later which change actually helped.

**Immediately log every drafted proposal** to
`reports/rubric-changelog.csv` — columns: `id, timestamp, rubric,
category, change, status`. One row per proposal:
- `id`: next sequential integer (check the last row in the file).
- `timestamp`: full ISO 8601 date+time (a review can draft several
  proposals in one sitting, date-only would collide).
- `rubric`: which rubric this is (`opportunity-scanner` or
  `option-suggestion`).
- `category`: the category tag it touches (e.g. `A`, `D`) — just the tag,
  not a paragraph.
- `change`: one free-text field covering what's changing and why,
  including the cited evidence rows (e.g. `"Category A weight 8pt->5pt —
  didn't discriminate across HOOD/CVNA/PTON (opportunity-scanner-log rows
  12,15,19)"`). Everything that used to be separate change_type/old_value/
  new_value/reason/evidence_rows columns lives in this one field now —
  keep it terse but self-contained.
- `status`: `proposed`.

Log it before presenting to the user, not after — the proposal itself is
a data point worth keeping even if it's later rejected.

## Step 4 — Human approval gate

Present the proposal(s) from Step 3 to the user with the supporting
evidence. Do not edit the rubric file yet. Wait for explicit approval,
rejection, or a request for more evidence before proceeding.

Update that proposal's row in `reports/rubric-changelog.csv` in place —
find it by `id` — setting `status` to `approved` or `rejected` (never
delete the row either way; a rejected proposal with its reasoning is
still useful history). If the user asks for more evidence instead of a
yes/no, leave `status = proposed` and revisit next cycle rather than
guessing.

## Step 5 — Apply (only after approval)

On approval, edit the rubric file directly (the weight/threshold/criterion
change) and append one line to its `## Changelog` section:

```
- YYYY-MM-DD: <what changed> — <why, citing the specific resolved rows>
  (full record: reports/rubric-changelog.csv)
```

The prose changelog entry and the CSV row are deliberately redundant —
the prose is for a human reading the rubric file inline, the CSV is the
structured, queryable, timestamped record of the same fact (see
`SYSTEM-DESIGN.md` for why both forms are kept). Then stop — don't
retroactively rescore historical log rows under the changed rubric
(`RUBRICS.md` Stage 5: old rows keep their original scores).

## Cadence

Run once a quarter, same cadence as both source skills' own review
cadence — there isn't enough new resolved evidence week to week to justify
running this more often. Running it more frequently than quarterly and
finding "no new proposals" every time is expected, not a sign something's
broken.
