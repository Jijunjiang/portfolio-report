# Playbook: margin risk

Scope: `type: "margin"` accounts only.

There is no tool that returns the broker's actual maintenance margin
requirement or margin-call price. Don't fabricate one. What's available and
honest to report:

- `cash` from `get_portfolio`, when negative, is the margin loan balance.
- Approximate loan-to-value: `abs(cash) / equity_value`. Frame it as "using
  X% of your stock value as collateral for a margin loan," not as a
  precise regulatory ratio.
- `buying_power.buying_power` (margined) vs. `buying_power.unleveraged_buying_power`
  (cash-only) — the gap between them is roughly the remaining margin
  cushion in dollar terms, which is more actionable for the user than a
  ratio.

Worth flagging explicitly:
- A rising loan-to-value trend day over day (compare against the prior
  report in `reports/`) — that's the leading indicator of tightening margin,
  not a single day's snapshot.
- Any single position that's both a large fraction of `equity_value` *and*
  has open short calls against it — a sharp drop concentrates margin risk
  and assignment risk in the same name at the same time.

Always close the margin section by pointing the user to the Robinhood app's
own margin/maintenance figures for the authoritative number — this report's
loan-to-value is a directional signal, not a substitute.

## Margin interest paid

Not available from any tool in this MCP — checked exhaustively (interest,
fee, statement, transaction, document, activity, journal, transfer — no
matching tool exists). No single API call will ever produce this figure
directly, so this account builds it from daily tracking instead of
estimating from a single snapshot.

**Daily balance tracking (`reports/margin-balance-history.csv`,** columns
`date,account_number,margin_used,rate_annual,estimated_daily_interest`)**:**
every run, for every margin account with a loan balance
(`margin_used = abs(cash)` from `get_portfolio` when `cash` is negative),
append one row:
- `rate_annual`: the user's confirmed annual margin rate as a decimal
  (currently `0.045`, i.e. 4.5% — this is a rate the user told us directly,
  not fetched; if they mention a rate change, use the new rate for all
  rows from that date forward, not retroactively).
- `estimated_daily_interest = margin_used * rate_annual / 365`.

Then, every run, report:
- **Estimated margin interest, YTD-tracked**: sum of
  `estimated_daily_interest` for all rows in the current calendar year.
  Label this clearly as an **estimate built from tracked daily balances and
  a user-confirmed rate**, not the broker's actual calculation — Robinhood
  may use a different day-count convention, tiered rates by balance size,
  or compounding, so this will be directionally right but not exact.
- **Tracking start date**: the earliest row's date. Days before that have
  no recorded balance and are NOT backfilled or estimated — say plainly
  that the YTD-tracked figure only covers the period since tracking began,
  not the full year, until enough days have accumulated.

`reports/margin-interest.csv` (columns
`date,account_number,amount_charged,source`) remains available as a
**ground-truth check**: if the user ever pastes in an actual figure from a
Robinhood statement, append it there and compare against the tracked
estimate for that period — call out the gap if it's large, since that
would mean the assumed rate or day-count is off.
