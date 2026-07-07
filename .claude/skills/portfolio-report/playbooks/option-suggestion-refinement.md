# Refining the option-selling strategy over time

Same philosophy as the opportunity-scanner's `refinement.md`: evidence-based
manual tuning at this account's cadence, not automated optimization. Log
every suggestion, check back on what actually happened, adjust the
playbooks when the evidence supports it — not before.

## The log

`reports/option-suggestion-log.csv` — one row per suggestion, every run,
**including skipped candidates**, not just the ones sold. A skip that
would have expired worthless and profitably is exactly as informative as a
sell that went badly; without logging skips there's no way to tell if the
skip logic is any good.

Columns: `date_suggested, symbol, type, strike, expiration,
contracts_suggested, total_premium_suggested, price_at_suggestion,
recommendation, thesis, executed, execution_details, date_resolved,
outcome, realized_pnl, verdict, score_total, score_a..score_f` (the
score_* columns are the `option-suggestion-rubric.md` breakdown — leave
blank for rows predating 2026-07-06, since assignment-probability data
wasn't captured in the lightweight daily screen before then; score
everything from here forward).

`executed` is `yes` / `no` / `variant` (user acted on the idea but at a
different strike/size/expiration than suggested — log what actually
happened in `execution_details`, since the variant itself is a data point
about whether the suggestion's strike selection was too conservative or
too aggressive relative to what the user was actually comfortable with).

## The quarterly review

For every row whose option has reached its expiration date (or was closed
early):
1. Determine `outcome`: `expired_worthless`, `assigned`, `rolled`, or
   `closed_early`. Pull `get_option_orders`/`get_option_positions` to
   confirm rather than assuming.
2. Fill in `realized_pnl` for that row (premium collected minus any
   buy-back cost, per the roll-netting method in `tax-basics.md` if it was
   rolled).
3. Set `verdict` — and note the CSP/covered-call asymmetry from
   `cash-secured-puts.md`: **assignment is not automatically a bad
   verdict.** For a CSP, `verdict = good_call` if either (a) it expired
   worthless, or (b) it was assigned and the effective cost still reads as
   a reasonable entry looking at the price a quarter later (i.e. the
   52-week-low thesis held up). `verdict = bad_call` if assigned into a
   continued slide well past the effective cost, or if a **skip** would
   have expired worthless and profitably. For a covered call,
   `verdict = bad_call` specifically when assignment forced a sale that
   then kept running well above the strike (the actual failure mode this
   account cares about, per `covered-calls.md`) — being assigned near a
   plateau is fine.
4. Look for patterns: which rubric categories (A–F) actually predicted
   `good_call` vs `bad_call`? Which skips, if any, turned out to be
   missed income?

## What "refining" means concretely

- **Reweight a rubric category** only if it fails to discriminate
  good/bad verdicts across enough resolved rows — same discipline as the
  opportunity-scanner rubric, cite the specific rows.
- **Adjust a threshold** (e.g. the 25%/35% assignment-probability bands,
  or the "6% N(d2)" covered-call reference point) if the logged outcomes
  show it's too loose or too tight.
- **Never refine on fewer than ~5 resolved cases** for a given
  category/name combination — this account trades a few times a quarter,
  so that bar will take a while to clear for any single category. Say so
  explicitly if ever tempted to act on 2–3 data points.

## Cadence

Update the log every run (new suggestions logged, `executed` field updated
if something was acted on). Do the outcome/verdict review pass once a
quarter, paired with the opportunity-scanner's own quarterly review —
they're on the same cadence for the same reason: not enough new resolved
evidence week to week to justify more often.
