---
name: portfolio-report
description: Generate the daily Robinhood portfolio report — consolidated holdings, margin usage, tax exposure, and option-selling suggestions across all accounts. Use for "daily report", "portfolio report", "how are my holdings doing", "run today's report", "should I sell any options".
---

# Portfolio daily report

Read-only analysis and suggestions only. Never call `place_equity_order` or
`place_option_order` from this skill. If the user wants to act on a
suggestion, that's a separate, explicit conversation — don't chain into it
automatically.

## 1. Gather accounts

Call `get_accounts`. For each active account, call `get_portfolio`. Skip
deep analysis (positions, options, PnL) for accounts with `total_value` under
~$100 — just list them with their balance. For every other account, run the
full pipeline below.

Mask account numbers in any output: show only `••••<last 4>`. Use the
account `nickname` when set, otherwise `brokerage_account_type`, to refer to
an account in prose (e.g. "your Roth IRA").

Note each account's tax wrapper up front, since it changes everything
downstream:
- `ira_roth` / other IRA types → gains are not currently taxable; skip the
  tax section for this account entirely.
- `individual`, `joint_tenancy_with_ros`, etc. → taxable brokerage; run the
  full tax section.

## 2. Positions and live prices

For each taxable/margin account with meaningful holdings:
- `get_equity_positions` — quantity, average_buy_price per symbol.
- `get_option_positions` (`nonzero=true`) — open option positions. This
  response does NOT include strike or option_type. Resolve those with
  `get_option_instruments` (batch by `ids`, comma-separated) before doing
  anything else with the position.
- `get_equity_quotes` for every held symbol, batched in one call, to get
  current price (see that tool's own guide for which price field is
  "current").

### Option position premium math (verified against `get_option_orders`)

`get_option_positions.average_price` is the **per-contract** premium
already scaled by the 100x multiplier (i.e. it equals `price_per_share *
100`, not price-per-share and not the position total). It is negative for
short (credit received) positions.

Total premium collected/paid for a position = `average_price * quantity`.
Do not multiply by the multiplier again — that double-counts.

Cross-check: `get_option_orders` (filtered narrowly — by `symbol` or
`created_at_gte` — the unfiltered list is huge and will blow the context
budget) has `premium` (per-contract) and `processed_premium` (per-contract *
filled quantity) on each order, confirming the above scaling.

## 3. Margin section (margin accounts only)

There is no dedicated maintenance-margin tool. Approximate from
`get_portfolio`:
- Leverage = `cash` (negative = margin loan balance) against `equity_value`.
- Loan-to-value ≈ `abs(cash) / equity_value` when cash is negative.
- Quote `buying_power.buying_power` and `buying_power.unleveraged_buying_power`
  as the actual spendable/cushion figures — they're broker-computed and more
  authoritative than a hand-rolled maintenance estimate.

State explicitly that this is an approximation, not the broker's real-time
maintenance requirement, and that a fast drop in the stock positions
collateralizing the loan is the actual risk (margin call), not a fixed
percentage. See `playbooks/margin-risk.md` for how to phrase this and what
thresholds are worth flagging.

**Every run, also append today's margin balance** to
`reports/margin-balance-history.csv` and report the estimated YTD margin
interest computed from it — see `playbooks/margin-risk.md` for the exact
method (this is how margin interest, otherwise unavailable from any tool
here, gets tracked over time).

## 4. Tax section (taxable accounts only)

Per position: `unrealized_gain = quantity * (current_price -
average_buy_price)`.

Known limitation: these tools don't expose per-lot purchase dates, so
short-term vs. long-term holding period **cannot be determined precisely**.
Say so in the report rather than guessing a holding period. Flag the
positions with the largest embedded gains regardless of term, since those
are the ones where an option assignment or a sale has the biggest tax
consequence.

For realized P&L: `get_realized_pnl` (span `year` or `ytd` isn't valid — use
`day`/`week`/`month`/`3month`/`year`/`all`, or `start_date`/`end_date` for a
custom window). Always pass `asset_classes` or it errors with
"un-specified asset class". This is realized-only and excludes open
positions; label it that way. For the underlying trade list use
`get_pnl_trade_history` only if the user wants line-by-line detail — the
bucketed `get_realized_pnl` is enough for the daily report.

**YTD realized P&L (every run):** call `get_realized_pnl` with
`start_date=<Jan 1 of current year>`, `end_date=<today>`, once per asset
class present on the account (`asset_classes: ["equity"]`,
`["option"]`, and `["crypto"]` if the account holds crypto per
`get_portfolio.crypto_value`) — separate calls, since a single call with
multiple classes returns one combined total, not a breakdown. Report each
class's YTD total plus the combined sum.

Cross-reference open short options against their underlying's embedded gain
using `playbooks/tax-basics.md` — specifically the "assignment risk on a
big embedded gain" check, which is the single highest-value insight this
report can surface. See that playbook also for what's and isn't possible on
short-term vs. long-term gain detail, and for margin interest/fees.

**Before presenting the option-class YTD total, check it for rolls.** A
large negative option realized total on this account is usually not a real
loss — it's typically the close leg of a covered call being rolled forward
to a higher strike/later expiration as the underlying rallies. Apply
`playbooks/tax-basics.md`'s roll-detection method (via `get_option_orders`,
matching `opening_strategy`/`closing_strategy` or paired close+open orders
on the same `chain_id`) before writing up the tax section, and report the
net roll economics alongside the raw realized-loss figure — never present
a roll's close leg as a standalone loss without it.

## 5. Dividend income

Every run, compute both figures in `playbooks/dividends.md`: YTD dividends
received (via `get_equity_orders` with `placed_agent: "drip"`, summed by
symbol) and a forward-looking annualized estimate from current holdings ×
`get_equity_fundamentals` rates. Report them side by side, clearly labeled
as different things (trailing actual vs. forward estimate), with the
DRIP-only caveat from that playbook.

## 6. Option-selling suggestions

**Excluded symbols — never suggest an option trade on these, in either
direction, regardless of embedded gain, capacity, or how attractive the
premium looks:**
- `GOOG` (user preference — no options activity on this name at all)

Check this list before generating any suggestion, not after — don't compute
a candidate strike for an excluded symbol and then discard it.

**Cash-secured puts are the default; covered calls are secondary** (user
preference — a covered call's assignment forces a sale of an already-owned,
often-appreciated position, while a put's assignment just acquires stock at
a fresh cost basis). For each candidate underlying, check CSP eligibility
first (idle `buying_power.unleveraged_buying_power`, per
`playbooks/cash-secured-puts.md`) before considering a covered call on it.
Only suggest against symbols already held (covered calls, using
`shares_available_for_sells` / 100 for contract capacity) or against cash
available (`buying_power.unleveraged_buying_power`, cash-secured puts on
watchlist/held names — don't invent new tickers the user hasn't shown
interest in). When a covered call is still worth mentioning alongside a
put, push the strike well past the standard 0.20–0.30 delta screen toward
"almost impossible to settle," per `playbooks/covered-calls.md` — don't
default to the textbook delta range.

Use `get_option_chains` for the underlying's expirations, then
`get_option_instruments` filtered by `expiration_dates` and `type` to pull
strike candidates. Apply `playbooks/covered-calls.md` and
`playbooks/cash-secured-puts.md` for the quick heuristic screen (delta
range, DTE window) that keeps the daily run fast.

Before suggesting a **new** covered call against a position that already
has open short calls, or against a position flagged in the tax section for
large embedded gain, apply the assignment-risk check first — don't suggest
a strike that would tip an already-close-to-the-money position further ITM.

Check `get_earnings_calendar` for the underlying over the suggestion's
expiration window; flag any suggestion that spans an earnings date.

Every suggestion table gets a **Suggested operation** column — concrete
contract count, capital required, and premium collected at that size (e.g.
"Sell 2 contracts ($26,000, collects $1,456)"), not just metrics; "Skip"
plus a one-line reason for names that don't clear the bar. Close a
multi-candidate table with the aggregate: total capital committed and
total premium if every "Sell" row were taken, and that capital's share of
total buying power.

For a full quantitative workup of any single candidate that survives this
screen (Black-Scholes assignment probability rather than raw delta,
tax-adjusted expected value, concentration-checked sizing) — or when the
user directly asks to evaluate a specific trade or a new stock they're
considering buying — use the `option-trade-model` skill instead of
re-deriving that math here. The daily report's screen stays lightweight on
purpose; that skill is the deep-dive version.

## 7. Output

Write two artifacts each run:

1. `reports/YYYY-MM-DD.md` in this repo — the full report, in this order:
   consolidated net worth across accounts, per-account breakdown, margin
   section, tax section (including the roll-netting analysis), dividend
   income, option suggestions, and a "changes since yesterday" diff against
   the most recent prior file in `reports/` (compare total_value and flag
   any option position that appeared/disappeared/moved materially ITM).
2. Refresh the Artifact dashboard (same underlying numbers, dashboard
   layout) by calling Artifact on the same file path/URL used previously —
   check `reports/.artifact-url` for the URL from the last run, or create a
   fresh one if this is the first run and save the returned URL there.

## Playbooks

New analysis techniques (from books, YouTube, etc.) get added as new files
in `playbooks/` and referenced from the relevant section above — don't grow
this file itself, keep it as the orchestrator.
