# Validation experiment

**Question:** does severe price drawdown in an established company actually
predict a multi-bagger recovery (the HOOD/INTC pattern), or does it also
flag stocks that stay broken? Tested with real historical price data
(`get_equity_historicals`), not opinion.

## Cases tested

| Ticker | High → low | Drawdown | Outcome since low | Verdict |
|---|---|---:|---|---|
| **HOOD** | $85 (Aug 2021) → $6.81 (Jun 2022) | 92% | Now $112.73 — **11x** off the low | Recovered |
| **INTC** | ~$68 (2020) → $18.89 (Sep 2024) | 72% | Now $120.41 — **5.7x** off the low | Recovered |
| **CVNA** | ~$85 (2021) → $0.71 (Dec 2022) | 99.2% | Now $68.60 — **96.6x** off the low | Recovered (most extreme case tested) |
| **PTON** | $171 (Jan 2021) → $2.70 (Apr 2024) | 98.4% | Now $5.75 — only 2.1x off the low, **still 96.6% below its high** | **Did not recover** |

## The finding that matters

**Drawdown depth alone does not discriminate.** PTON's drawdown (98.4%) is
essentially identical to CVNA's (99.2%) and worse than HOOD's (92%) or
INTC's (72%) — a pure Category A (price/technical) score would have rated
PTON as *at least as attractive* as the three winners. It wasn't. Category
A gets a candidate onto the list; it cannot be the reason to act on one.

**What actually differed (qualitative, category B/D territory):** HOOD,
INTC, and CVNA all had drawdowns rooted in *cyclical or operationally
fixable* problems — trading-volume cyclicality and a regulatory overhang
(HOOD), a fixable-but-painful manufacturing/execution problem in a
cyclical industry (INTC), an over-levered balance sheet in a cyclical
industry fixed by refinancing and operational cuts (CVNA). PTON's
drawdown reflects *structural* demand destruction — a pandemic-era demand
spike unwinding permanently as people returned to gyms and in-person
life, not a cyclical trough waiting to mean-revert. Same price chart
shape, different underlying reality.

## Honest limitation

`get_equity_fundamentals` only returns a **current** snapshot — there is
no way to pull point-in-time historical fundamentals for these tickers as
they looked at the actual trough date. So category B/D (quality,
catalyst) could only be validated **narratively** here (the cyclical-vs-
structural read above), not mechanically backtested the way category A
was. This is a real gap: the rubric's price-based criteria are backtestable
today; its business-quality criteria currently rely on judgment applied
at scan time, checked against outcomes only after the fact (see
`refinement.md`). Don't overstate the rigor of category B/D scores as a
result — they're informed judgment, not verified history.

## Conclusion

The two-gate design (mechanical drawdown/technical screen, then
mandatory qualitative quality/catalyst read before shortlisting) is
validated by this test, not just theorized: a mechanical-only version of
this screen would have put PTON and CVNA side by side as equally
attractive, and only one of them paid off. The rubric's insistence on
category B/D as *mandatory*, not optional polish, is doing real work.
