# Playbook: dividend income

There is no dedicated dividend/cash-transaction tool in this MCP (checked
the full tool list — no statement, transaction, or dividend-history
endpoint exists). Two different, complementary figures are still
computable from what's available. Report both, labeled clearly as
different things — don't blend them into one number.

## 1. YTD dividends actually received (proxy via DRIP)

`get_equity_orders` with `placed_agent: "drip"` returns every dividend
reinvestment purchase — each order's `dollar_based_amount.amount` is the
dollar amount of that reinvestment, which equals the dividend paid on that
date for that symbol (assuming the position is enrolled in dividend
reinvestment, which is the common case). Filter to `state: "filled"` and
`created_at >= <Jan 1 of current year>`, sum `dollar_based_amount.amount`
per symbol and combined.

**Caveat to always state:** this only captures dividends that were
reinvested through DRIP. Any dividend paid out in cash instead of
reinvested would not appear in this data at all — if the actual cash
dividend total matters precisely (e.g. for a tax return), the year-end
1099-DIV is the authoritative source, not this report.

## 2. Forward-looking annualized dividend income (current holdings, current rate)

`get_equity_fundamentals` returns `dividend_per_share`,
`distribution_frequency` ("Quarterly", "Monthly", etc.), and
`dividend_yield` per symbol. For each currently-held dividend-paying
position: `annual_income = quantity_held * dividend_per_share *
payments_per_year` (4 for Quarterly, 12 for Monthly, etc.). Sum across
positions for a portfolio-level run-rate estimate.

Treat `dividend_yield` / `dividend_per_share` as **possibly stale** before
using them — checked this directly: a name whose dividend was cut or
suspended can still show an old `dividend_per_share` value with `payable_date`
and `ex_dividend_date` from a prior year (e.g. dates over a year old) while
`dividend_yield` is `null`. The `null` yield is the tell; when you see it,
treat the position as currently paying $0 regardless of what
`dividend_per_share` says, and don't include it in the forward estimate.

Label this figure explicitly as an estimate based on today's holdings and
today's declared rate — it is not a guarantee, ignores dividend
growth/cuts, and will differ from the trailing DRIP-based YTD figure above
if holdings changed size during the year (a position that was smaller
earlier in the year collected less then than the current run-rate
implies).
