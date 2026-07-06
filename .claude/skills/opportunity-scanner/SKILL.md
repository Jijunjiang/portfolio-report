---
name: opportunity-scanner
description: Screen for asymmetric, multi-year opportunity candidates (deep-value turnarounds and quality growth compounders) matching the user's own track record (HOOD bought ~$10, INTC bought ~$21, both up 5-11x since). Use for "find opportunities", "any turnaround candidates", "run the quarterly scan", "is there a 5x/10x setup out there". Not for daily trading — this account trades a few times per quarter, high-conviction only.
---

# Opportunity scanner

Read-only screening and research. Never place an order from this skill.
This narrows a huge universe down to a short list worth the user's own
research — it does not predict returns, and nothing here is a buy signal
on its own.

## 0. Validated against the user's own track record

Before designing the rubric, I backtested it against the two trades the
user named, using this account's own historical-data tools — not just
theory:

- **HOOD**, bought ~$10: actual weekly low was **$6.81** (week of
  2022-06-13), down **92% from its Aug-2021 high of $85**. It then spent
  ~18 months basing in the $7–13 range before recovering to $112.73 today
  — an 11x from a $10 entry.
- **INTC**, bought ~$21: actual low was **$18.89** (Sept 2024), down
  **72% from its 2020-era high near $68**. Now $120.41 — a 5.7x.

Both are large, widely-known companies (not obscure microcaps) that fell
70–90%+ from a multi-year high before recovering. That's the pattern this
screen is built to find — severe, sustained drawdown in an established
name, not a short-term technical dip.

**Concrete false-positive caught during validation:** a plain "RSI < 30 +
market cap > $2B" screen also returned CRWD — but CRWD's 52-week high was
hit *the same week* it showed up (down only 2.5% from that high). Its
"oversold" reading was a one-week dip inside a strong uptrend, nothing
like HOOD or INTC's setup. This is why step 2 below is mandatory, not
optional — RSI alone produces false positives that look nothing like the
user's actual winners.

## 1. Two saved scans (already created on the account)

- **`38edc26c-8b66-4235-9f3b-40275bb6cb7f`** — "Deep Value Turnaround
  Candidates": `Market cap > $2B`, `RSI(14) < 30`, sorted by RSI ascending.
  This is the mechanical first pass for the HOOD/INTC archetype.
- **`2a31c406-2b3f-4552-bcb4-6e78ceaba979`** — Growth Compounder screen:
  `Market cap > $1B`, `PEG < 1.5`, `Return on equity > 15%`, sorted by PEG
  ascending. First pass for quality-growth-at-reasonable-price names (the
  TSM archetype — TSM itself clears these filters today).

Re-run either with `run_scan` any time; both are visible in the Robinhood
app's screener section too, not just here. `update_scan_filters` /
`update_scan_config` can retune them (full reference:
`trading://scanner-filter-specs` resource lists every available filter —
fundamental, price/volume, technical, and options).

## 2. Mandatory secondary filter: distance from the high (the scanner can't do this natively)

There's no built-in "% off 52-week high" filter. For every candidate that
survives the Deep Value Turnaround scan, pull `get_equity_fundamentals`
and compute:

```
pct_off_high = (high_52_weeks - current_price) / high_52_weeks
```

**Require ≥40% off the 52-week high to keep a candidate** — this is the
threshold that separates HOOD/INTC-like setups (72–92% off) from
short-term dips like CRWD (2.5% off) that pass RSI alone. If a 52-week
high understates the real drawdown (the stock has been down for longer
than a year), that's even more supportive of the thesis, not less — say so
when it's known, but 52-week is what's mechanically available.

Below ~25% off high: discard, regardless of RSI. 25–40%: borderline,
mention only if nothing better clears the bar. ≥40%: passes the gate —
score it with the full rubric next.

## 3. Score every candidate that passes the gate with `rubric.md`

`rubric.md` has the full 32-criterion, 100-point scoring rubric across
five categories (value/drawdown depth, financial quality, momentum
confirmation, catalyst/story, risk & portfolio fit) — this is what turns
"passed the mechanical filters" into a ranked, explainable score rather
than a pass/fail list. Score every candidate that cleared step 2 against
it; don't shortlist on the 52-week-high filter alone. ≥70 = strong
candidate, 50–69 = watchlist, <50 = discard — see that file for the exact
per-criterion scoring and the mechanical-vs-judgment split.

## 4. Growth compounder screen — quality at a reasonable growth price

No drawdown requirement here; the thesis is different (own a good business
compounding, not a beaten-down one recovering). After the PEG/ROE screen:
- Sort by PEG ascending — cheapest growth-adjusted valuation first.
- Note market cap explicitly; don't assume small-cap is required — TSM
  itself is a multi-trillion-dollar compounder today and still clears
  PEG < 1.5. Larger names offer less 5–10x room but more durability;
  smaller ones offer more room but more risk. Say which end of that
  tradeoff each candidate sits on.
- Flag extreme ROE (>100%) as worth double-checking manually — it's
  sometimes a leverage/buyback accounting artifact rather than pure
  operating quality.
- Score these against `rubric.md` too — skip category A (drawdown-specific),
  use categories B, C, D, E as-is; category D24 already maps directly to
  this screen's own PEG/ROE filter.

## 5. Output format

One shortlist per archetype (typically 3–8 names, not the full scan
dump), each with: ticker, current price, the rubric score with category
subtotals (per `rubric.md`'s presentation guidance — show which
categories drove the score, not just the total), and one sentence on what
would need to be true for this to work out — not a prediction, a
statement of the thesis being bet on. Explicitly list names that were
screened out and why (like CRWD above) when they're a recognizable/
"famous" name the user would expect to see — silence reads as an
oversight, not a considered exclusion.

Always close with: **this narrows a universe, it does not predict a
return. Multi-bagger identification is inherently uncertain — HOOD and
INTC worked out, but the same setup (severe drawdown, established
company) doesn't always resolve upward. Treat this as a research
shortlist for the user's own few-times-a-quarter, high-conviction
decisions, not a signal to act on directly.**

## 6. Cadence

This account trades a handful of times per quarter by design — don't run
this daily. Quarterly is the natural default; the user can ask for it
sooner if something notable is happening. Not currently wired into the
daily `portfolio-report` automation — run on request, or ask the user if
they want a standalone scheduled cloud routine for it.

## 7. Files in this skill

- `rubric.md` — the 32-criterion scoring rubric (step 3).
- `validation.md` — the backtest that shaped the rubric: HOOD/INTC/CVNA
  (recovered) vs. PTON (didn't, despite a near-identical drawdown) —
  read this before trusting category A alone on a new candidate.
- `refinement.md` — how the rubric gets tuned over time using
  `reports/opportunity-scanner-log.csv`: log every scored candidate,
  review outcomes quarterly, reweight/re-threshold on accumulated
  evidence. Not automated — a human-and-agent review loop matched to
  this account's quarterly cadence.
