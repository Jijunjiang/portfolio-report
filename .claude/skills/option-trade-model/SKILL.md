---
name: option-trade-model
description: Deep quantitative evaluation of a specific covered-call, cash-secured-put, or buy-write candidate — Black-Scholes-based assignment probability, annualized returns, volatility richness, tax-adjusted expected value, and position sizing. Use for "should I sell a covered call on X", "evaluate this put", "should I buy X and sell calls against it", "is this strike worth it". For the lightweight daily screening pass used in the automated report, see the portfolio-report skill's playbooks instead — this is the on-demand deep-dive version.
---

# Option trade model

This is a deliberately narrower, more rigorous tool than the daily report's
quick screen: one candidate trade (or a small comparison set), evaluated
properly, on request. Read-only analysis — never place an order from this
skill. If the user wants to act after seeing the numbers, that's a
separate explicit step.

## 0. What this model does that generic option-selling guides don't

Two things specific to managing a real account, not a textbook example:
1. **Tax-adjusts the expected value** of writing a call against a position
   with a large embedded gain — most retail "wheel strategy" content
   ignores this entirely, but it's frequently the dominant term for an
   account that's held positions a long time.
2. **Checks portfolio concentration** before recommending size, not just
   contract capacity from shares owned.

Standard industry heuristics (delta 0.20–0.30, 30–45 DTE, sell when IV
rank is elevated) are used as a sanity check, not the primary output — the
primary output is the actual math below, computed from this account's live
data.

**User's stated strategy preference (applies to every evaluation):**
cash-secured puts are the default; covered calls are secondary. The user
considers a covered call riskier here specifically — assignment forces a
sale of an already-owned, often-appreciated position (see step 5's
tax-adjusted EV), while a put's assignment just acquires stock at a fresh
cost basis. When a covered call is evaluated anyway, the user wants strikes
pushed **well past** the standard 0.20–0.30 delta zone, toward "almost
impossible to settle" — low-single-digit-delta, deep OTM, more like the
account's existing TSM $600c than a textbook 30-delta write. Smaller
premium is an accepted tradeoff for that low a probability; don't recommend
moving the strike closer just because the annualized yield looks better —
that's optimizing for the wrong thing given the stated preference.

## 0.5 Ticker quirks worth knowing

`BRK.B`'s option chain symbol is `BRKB` (no period) — `get_option_chains`/
`get_option_instruments` with `chain_symbol: "BRK.B"` silently returns empty,
not an error. If a chain lookup comes back empty for a symbol that
obviously has listed options, retry without punctuation before concluding
there are none.

## 1. Inputs (gather live, never assume)

- `S`: current stock price — `get_equity_quotes`.
- `K`, expiration, type: candidate strike — `get_option_chains` →
  `get_option_instruments`.
- `premium`, `delta`, `implied_volatility`: `get_option_quotes` on the
  specific instrument_id. Use `mark_price` as the premium (not bid or ask
  alone).
- `T`: days to expiration ÷ 365.
- `r`: risk-free rate proxy. No live tool provides this — use 0.045 (4.5%)
  as a stated assumption unless the user gives a different figure. Its
  effect on short-dated (< 90 day) option probabilities is small; don't
  spend effort refining it.
- Embedded gain per share on the underlying, if it's an existing holding
  (from the portfolio-report tax section: `quantity * (S -
  average_buy_price)`).
- Realized volatility comparison: trailing 20-trading-day close-to-close
  log-return volatility, annualized (`get_equity_historicals`, `interval:
  day`, ~30 calendar days back to get 20 sessions). Compute:
  `daily_log_return = ln(close_t / close_t-1)`, `realized_vol =
  stdev(daily_log_returns) * sqrt(252)`.

## 2. Assignment probability — compute it, don't just trust delta

Quoted `delta` approximates `N(d1)`, which is a common industry shortcut
but is **not** the same as the true risk-neutral probability of finishing
ITM, which is `N(d2)`. `d1` and `d2` diverge more at higher IV and longer
DTE. Compute both:

```
d1 = (ln(S/K) + (r + σ²/2)·T) / (σ·√T)
d2 = d1 - σ·√T
```

- Call: `P(assignment) = N(d2)`
- Put: `P(assignment) = N(-d2)`

Report both the quoted delta and the computed `N(d2)`. If they differ by
more than ~5 percentage points, say so explicitly — it means the
delta-as-probability shortcut is meaningfully overstating (delta is always
≥ the true N(d2) for calls when r,σ > 0) the odds of assignment for this
specific contract, which matters most exactly when someone is relying on
"30 delta ≈ 30% assignment risk" folklore for a longer-dated or high-IV
contract.

## 3. Volatility richness — IV vs. realized, not true IV Rank

True IV Rank/Percentile needs a historical *implied* volatility time
series, which no tool here provides (checked — `get_option_historicals`
is contract price bars, not IV history). Substitute a directly computable
metric instead: **IV/HV ratio** = current `implied_volatility` ÷ trailing
20-day realized volatility (from step 1). Above ~1.2 → premium is rich
relative to how the stock has actually been moving (favorable to sell);
below ~0.8 → premium is cheap (the option isn't compensating you much for
the actual recent movement; less favorable). State this is a substitute
for IV Rank, not IV Rank itself, since it compares to realized rather than
the stock's own historical IV range.

## 4. Standard return metrics

- Annualized static return: `(premium / basis) × (365 / DTE)`, where
  `basis` = `S` for a covered call, `K` for a cash-secured put.
- Covered call, return-if-called: `((premium + max(K − S, 0)) / S) × (365
  / DTE)` — only add the `max(K−S,0)` term for an OTM strike.
- Covered call, downside cushion: `premium / S` — how far the stock can
  fall before the covered position is worse off than today's entry.
- CSP, effective cost basis if assigned: `K − premium`; express the
  discount to current price as `(S − (K − premium)) / S`.

## 5. Tax-adjusted expected value (the part generic guides skip)

For a covered call on an **existing holding** with embedded gain
`G_per_share`:

```
expected_forced_gain = N(d2) × G_per_share × quantity_covered
```

This is not "expected tax owed" (no marginal rate is assumed unless the
user supplies one) — it's the **probability-weighted dollar amount of gain
that assignment would force you to realize this year**. Present it next
to the premium being collected: a trade collecting $355/contract while
carrying a 15% chance of forcing $174,600 of recognized gain is a
different decision than the same premium on a position with no embedded
gain, even though the raw premium and delta look identical. If the user
gives a marginal rate, multiply through for an expected tax dollar figure;
otherwise leave it as the expected gain amount and let them apply their
own rate.

For a cash-secured put, the analogous check is smaller (assignment sets a
*new* cost basis, not a forced sale) — mention only if relevant.

## 6. Position sizing — concentration, not just share coverage

Contract capacity from `shares_available_for_sells / 100` (or, for a CSP,
`buying_power.unleveraged_buying_power / (K × 100)`) is a **ceiling**, not
a recommendation. Before suggesting a size:
- Compute this underlying's resulting share of total portfolio value
  (stock value, or stock + cash-secured collateral) if the full suggested
  size were used.
- Flag if that pushes the position above roughly 15–20% of total account
  value, using this account's own GOOG+INTC concentration (~46% combined)
  as the cautionary reference point already established in the daily
  report — don't recommend compounding concentration that's already been
  flagged as a risk.
- When sizing is capacity-constrained rather than concentration-constrained,
  say so, and suggest starting below max capacity for a first tranche on
  any name not already established in the option book.

## 7. New-buy candidates: three ways in, compared side by side

When the candidate is a stock **not currently held**, evaluate all three
entry approaches together rather than picking one by default:

| Approach | Effective entry | Upside | Use when |
|---|---|---|---|
| Buy stock outright | `S` | Uncapped | Strongly bullish, don't want upside capped |
| Buy-write (buy + sell call same day) | `S − premium` | Capped at `K` | Want reduced cost basis, fine capping upside for income |
| Cash-secured put | N/A until assigned; effective cost `K − premium` if assigned | Full upside only after assignment | Willing to wait for a pullback, want to be paid to wait |

Compute the standard return metrics (step 4) and assignment probability
(step 2) for whichever strikes are realistic for the buy-write and CSP
columns, and present the comparison table rather than just answering with
one recommendation — this is a decision with a real behavioral tradeoff
(patience vs. immediacy vs. uncapped upside), not a single right answer.
That said, given the user's stated preference for puts over covered calls,
lead with the cash-secured put column's numbers in the interpretation
text even though all three are shown.

## 8. Output format

For a single-candidate evaluation: one table (assignment probability
[quoted delta vs. computed N(d2)], IV/HV ratio, annualized return(s),
downside cushion or effective cost basis, expected forced-gain if
applicable) plus 2-3 sentences of plain-language interpretation — lead
with whatever number is most decision-relevant (usually the tax-adjusted
figure if the position has a large embedded gain, otherwise the annualized
return and assignment probability).

For a new-buy comparison: the three-approach table from step 7 plus the
same metrics per approach.

Always state the `r` assumption and the IV/HV-as-IV-Rank-substitute
caveat once, briefly — don't repeat the full disclaimer paragraph every
time if evaluating multiple candidates in one response.
