# Playbook: tax exposure basics

Scope: taxable accounts only (skip Roth/other tax-advantaged wrappers
entirely — see SKILL.md step 1).

## What we can and can't compute

Can compute per position: `unrealized_gain = quantity * (current_price -
average_buy_price)`. This is exact for the aggregate position.

Cannot compute: short-term vs. long-term split, for either unrealized or
realized gains. Checked directly against `get_pnl_trade_history` — its
per-trade records have `timestamp` (of the *closing* trade), `symbol`,
`side`, `quantity`, `price`, and `realized_gain`, but no lot acquisition
date and no `term` field. `get_equity_positions` likewise gives one
blended `average_buy_price` per symbol, not per-lot dates. There is no
tool in this MCP that returns holding period. Don't approximate or guess
one — say plainly in the report that ST/LT is not available from this
data source, and point to the source that actually has it: Robinhood's
1099-B / tax documents (issued after year-end) or the per-position "tax
lots" view in the app, both of which track this internally for you
already, just not through this API.

## Margin interest / fees

Not computable at all — there is no tool in this MCP (checked the full
tool list) that returns margin interest charged, account fees, or any
statement/transaction-level data. Don't infer a fee from the loan balance
or estimate a rate. State this as a hard gap in the report and point to
Robinhood's monthly account statement (Statements & History in the app) or
the year-end tax documents for the actual figure.

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

Report YTD every run (see SKILL.md step 4 for the exact calls), broken out
by asset class (equity / option / crypto) rather than one blended number —
on an account running a heavy options-selling strategy, the option-class
total is usually where most of the realized activity actually is, and
blending it with equity hides that.

## Rolled options are not realized losses — net them, don't report the close leg alone

A "roll" (buy-to-close an existing short option, sell-to-open a new one on
the same underlying to extend and/or adjust the strike) shows up in
`get_pnl_trade_history` as a lone closing trade with a `realized_gain` that
compares the *original* opening credit against *today's* buy-back cost. On
a stock that's rallied hard since the original contract was opened, this
can print a large negative number that reads like a loss — it isn't one in
any actionable sense, because the position wasn't closed out, it was
extended. Reporting that number alone, without the new contract's credit
next to it, is the single easiest way for this report to be misleading
about an active covered-call/wheel strategy.

**Detecting a roll**, verified against `get_option_orders` on this account:
- **Atomic roll** (one order, both legs): `opening_strategy` and
  `closing_strategy` are both non-null on the same order. Its own `premium`
  /`processed_premium`/`direction` already give the net credit or debit of
  the whole roll directly — use those, don't decompose further.
- **Manual roll** (two orders): a `closing_strategy`-only order and a
  separate `opening_strategy`-only order on the *same* `chain_id`, same
  `option_type`, close together in time (same day, in practice within
  seconds-to-minutes on this account). Net economics = the new order's
  `processed_premium` (credit) minus the closing order's `processed_premium`
  (debit) — compute and report that net figure, not either leg alone.

**What to report:** for any short option whose close is part of a detected
roll, replace "realized a loss of $X" with something like: "rolled
[old strike/exp] → [new strike/exp]; the close alone shows as a $X
realized loss because the original credit was small relative to today's
buy-back cost, but the new contract collected $Y, for a net
[credit/debit] of $Z on the roll itself." When summarizing YTD option P&L,
call out the portion attributable to roll closes separately from
everything else, since roll-close "losses" are usually the majority of
any large negative option total on an actively-managed covered-call
account and materially change how the headline number should be read.
Genuinely closed-out positions (bought back or expired with **no** new
same-underlying position opened nearby) are real realized gains/losses —
report those at face value.

## Wash sales

Not computable from these tools (would need a full transaction ledger with
lot matching). If the report shows a position with a realized loss this
year and the same symbol was bought back within 30 days, flag it as a
*possible* wash sale worth checking manually — don't assert it as certain.
