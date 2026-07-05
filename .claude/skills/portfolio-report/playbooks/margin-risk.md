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

Not available from any tool in this MCP — there's no statement,
transaction, or interest-charge endpoint. Don't estimate a dollar figure
from the loan balance and a guessed rate; that would look precise while
being fabricated. State plainly that this report can't show margin
interest paid, and point to Robinhood's monthly account statement
(Statements & History in the app) for the real number.
