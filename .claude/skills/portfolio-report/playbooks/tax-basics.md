# Playbook: tax exposure basics

Scope: taxable accounts only (skip Roth/other tax-advantaged wrappers
entirely — see SKILL.md step 1).

## What we can and can't compute

Can compute per position: `unrealized_gain = quantity * (current_price -
average_buy_price)`. This is exact for the aggregate position.

Cannot compute: short-term vs. long-term split. The available tools return
an average cost basis across all lots, not individual lot purchase dates.
Say this plainly in the report rather than assuming long-term (the safer
assumption for a rough estimate, if one is needed for illustration, but
always labeled as an assumption, never presented as fact).

## The highest-value check: assignment risk on embedded gains

For every open short option, look up its underlying's unrealized gain. If a
short **call** is within ~10% of the money (or already ITM) *and* the
underlying carries a large embedded gain, that's the standout finding for
the report — assignment would force a sale and realize that gain in one
shot, at whatever the current mix of short/long-term rates works out to.
Lead the tax section with this, don't bury it under routine per-position
gain/loss listings.

For short **puts**, the analogous risk is assignment creating a *new* cost
basis at the strike — not usually a tax problem today, but worth a one-line
mention if the put is deep ITM and assignment looks likely soon.

## Realized P&L framing

`get_realized_pnl` gives bucketed realized gains — present the requested
window's total plus a one-line trend (improving/worsening vs. the prior
comparable window if you have it), not the full bucket dump unless asked.
Always label it "realized only, excludes open positions" and "informational,
not tax advice" per that tool's own guide.

## Wash sales

Not computable from these tools (would need a full transaction ledger with
lot matching). If the report shows a position with a realized loss this
year and the same symbol was bought back within 30 days, flag it as a
*possible* wash sale worth checking manually — don't assert it as certain.
