# Experiments — does this strategy actually work?

`.claude/skills/opportunity-scanner/validation.md` already ran an informal
version of this check (HOOD/INTC/CVNA recovered vs. PTON didn't, same
drawdown depth) but only tested the drawdown-percentage criterion by hand.
This directory formalizes and extends that into a real, scripted backtest
using the full technical-indicator engine built in `compute_rubric.py` —
answering the actual question: **if the mechanical Stage-0 screen had been
running on a given date in the past, would it have flagged the stock
before it went on to multiply, and how often would it have also flagged
something that didn't?**

## What this can and can't test

**Can test rigorously — the mechanical/technical criteria**: RSI, Williams
%R, Stochastic, Bollinger Bands, support level, MACD, EMA reclaim, Aroon,
ADX, relative volume. All of these are computable purely from historical
OHLCV bars (`get_equity_historicals`), which *is* available point-in-time
with no lookahead — `backtest.py` only ever looks at bars up to and
including the date being tested, never later ones.

**Cannot test rigorously — the fundamental/quality criteria** (margins,
ROE, ROA, PEG, dividend yield): `get_equity_fundamentals` only returns a
**current** snapshot, there is no point-in-time historical fundamentals
API available here. This is the same honest limitation `validation.md`
already flagged. Any experiment result below is therefore a test of "would
the technical screen alone have caught this," not the full rubric —
say so explicitly in every result, don't let a good technical hit rate
imply the whole rubric is validated.

**Cannot test at all — the judgment criteria** (cyclical-vs-structural,
domain leadership, catalyst, tailwind): these need real reasoning about
what was actually happening at the company at the time, which isn't
reconstructable from price data. `validation.md`'s narrative read (HOOD/
INTC/CVNA = cyclical/fixable, PTON = structural demand destruction) is the
only kind of evidence possible here, and it already exists — not
re-litigated in this directory.

## Method

1. **Case registry** (`cases.py`): known outcomes — some that multiplied
   after a deep drawdown (HOOD, INTC, CVNA), one that didn't (PTON), plus
   room to add more as they come up. Each case has a ticker and the
   approximate trough window to scan around.
2. **`backtest.py`**: for each case, pulls full daily OHLCV history
   (`get_equity_historicals` output, fetched separately and saved to
   `data/<ticker>.json` — see "Fetching data" below, since this script
   itself has no MCP access), then for every trading day in the trough
   window, computes what `compute_rubric.py`'s technical criteria would
   have shown using only bars up to that day, and checks whether the
   turnaround Stage-0 screen's actual live thresholds (RSI(14)<30 AND
   Williams%R(14)<-80) would have fired. For every date that fires, reports
   the forward return at fixed horizons (3mo/6mo/1yr/2yr) from that date's
   close to today (or as far as the data allows).
3. **Results** land in `results/<ticker>-backtest.json` and get summarized
   in `results/summary.md`.

## Fetching data

This directory's scripts are plain Python with no MCP/API access (same
design principle as `compute_rubric.py` — no credentials belong in a
script file). A Claude Code session fetches each ticker's full daily
history via `get_equity_historicals` and saves it to
`experiments/data/<ticker>.json` in this shape:

```json
{"ticker": "HOOD", "bars": [{"begins_at": "...", "open": ..., "high": ...,
"low": ..., "close": ..., "volume": ...}, ...]}
```

then `backtest.py data/<ticker>.json` runs the analysis against it.

## Honest framing for results

A hit (the screen fired before a real multi-bagger) is evidence the
technical criteria are pointed in a useful direction, not proof the
strategy "works" — 4-6 known-outcome cases is nowhere near enough to
establish a real hit rate or false-positive rate (see `RUBRICS.md`'s own
"never refine on fewer than ~5 resolved cases" rule, which applies here
too). Treat every number here as a existence-proof / sanity-check, not a
backtested Sharpe ratio. The far more meaningful validation is the live
one already running: `reports/opportunity-scanner-logs/*.csv` resolving
real `outcome_1q`/`outcome_1y` on real, forward-looking picks, reviewed
quarterly by the `rubric-engine` skill.
