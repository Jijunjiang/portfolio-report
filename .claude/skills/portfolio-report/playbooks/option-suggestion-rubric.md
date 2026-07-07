# Rubric: scoring option-selling suggestions

Codifies the heuristics already in `cash-secured-puts.md` and
`covered-calls.md` into a checkable score, so suggestions can be compared
against each other consistently and, later, against what actually happened
(see `option-suggestion-refinement.md`). Compute this alongside every
suggestion and log the total in `reports/option-suggestion-log.csv` — it
isn't a gate that blocks a suggestion from appearing, just a consistency
score to correlate against outcomes over time.

## Cash-secured puts (100 pts)

- **A. Effective-cost position vs. 52-week range (25 pts).** `effective_cost
  = strike - premium`; `position_pct = (effective_cost - low_52w) /
  (high_52w - low_52w)`. Below 0% (under the low): 25. 0–10% above the low:
  15. 10–50%: 5. Above 50%: 0.
- **B. Assignment probability band (20 pts).** Prefer the lower end per
  user preference (confirmed on SOFI $16→$15). ≤25%: 20. 26–35%: 12. >35%:
  5.
- **C. Fundamental floor (20 pts).** Positive P/E *and* dividend yield
  >2%: 20. Positive P/E, no/low dividend: 10. Negative P/E (loss-making,
  no floor): 0.
- **D. Earnings-window handling (15 pts).** No earnings before expiration:
  15. Earnings before expiration but clearly flagged with date: 8.
  Unflagged overlap: 0 (this should never happen — treat as a process bug
  if it does).
- **E. Sizing discipline (10 pts).** Within `unleveraged_buying_power`, no
  stacking within ~$5 of an existing put on the same name: 10. Either
  violated: 0.
- **F. Annualized yield sanity (10 pts).** Yield roughly proportionate to
  assignment risk (a very high yield at a "safe" score above should read as
  suspicious, not free money) — judgment call, not formula: 0–10.

## Covered calls (100 pts)

- **A. OTM distance (35 pts).** Reference point: the account's own TSM
  $600c (~35–40% OTM, low-single-digit N(d2)). N(d2) ≤6%: 35. 6–15%: 20.
  15–25%: 8. >25% (standard 20–35 delta screen): 0 — this account's stated
  preference explicitly rejects the standard screen for covered calls.
- **B. Respects embedded gain as a floor (20 pts).** Strike clears the
  tax-flagged embedded-gain distance *and* goes further per (A): 20.
  Clears embedded gain only, doesn't push further OTM: 5. Doesn't clear
  it: 0.
- **C. Capacity check (15 pts).** No naked exposure (contracts ≤ spare
  `shares_available_for_sells / 100` after existing short calls): 15.
  Any naked exposure: 0 (should never happen — process bug if it does).
- **D. Earnings-window handling (15 pts).** Same as CSP criterion D.
- **E. Tax-adjusted EV sanity (15 pts).** Tax-adjusted expected forced
  gain (N(d2) × embedded gain) is small relative to premium collected: 15.
  Tax-adjusted EV is large relative to premium (TSM $590c-style case,
  worth flagging even if still recommended): 5.

## Using the score

Log the total (and category subtotals, same spirit as the
opportunity-scanner rubric) in `reports/option-suggestion-log.csv` at
suggestion time. The score is descriptive, not predictive yet — there
isn't enough resolved history to know which categories actually correlate
with good outcomes. That correlation is exactly what
`option-suggestion-refinement.md`'s quarterly review is for.

## Changelog

Every reweight/add/retire gets one line here: date, what changed, why, and
which logged rows in `reports/option-suggestion-log.csv` justified it. See
`../../../../RUBRICS.md` for the full lifecycle this follows. Empty so far
— scoring only started 2026-07-06, no resolved cases yet.
