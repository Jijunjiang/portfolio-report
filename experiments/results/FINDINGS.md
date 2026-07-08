# Backtest findings — 2026-07-07 (updated with the low-risk/high-reward bar)

Full data in `summary.md` / `*-backtest.json`. This is the interpretation.
Read `../README.md` and `../DESIGN.md` first for the honest scope
(technical criteria only, 4 cases, not a statistically meaningful sample).

**Update**: the metric below (never >30% drawdown within 6 months, and
eventually reaches 5x) replaced a looser "raw forward return" check per
direct feedback — it's a much better test of what actually matters for a
real, low-frequency account: could you have *held* the position without
being shaken out, not just "was the return positive at some arbitrary
horizon."

## Headline result: this stricter bar discriminates cleanly — much better than raw forward returns did

| Case | Screen fired | Passes low-risk/high-reward | Actual outcome |
|---|---:|---:|---|
| HOOD | 1 | **1/1 (100%)** | Recovered, 11x off the low |
| INTC | 9 | **9/9 (100%)** | Recovered, 5.7x off the low |
| CVNA | 9 | **1/9 (11%)** | Recovered, 96.6x off the low |
| **PTON** | 11 | **0/11 (0%)** | **Did not recover** |

This is a real improvement over the earlier (raw-forward-return) version
of this experiment, which made PTON look deceptively competitive with the
winners on some individual dates. Under this stricter bar, **PTON fails
outright, on every single one of its 11 firing dates** — it never reaches
5x from any entry point in the available data, full stop. HOOD and INTC
pass on *every* firing date. This is the cleanest, most decision-relevant
signal this backtest has produced so far.

## CVNA is the genuinely interesting case, not a clean pass or fail

CVNA only passes on its very last firing date (2022-12-07, $0.77 —
practically at the actual $0.71 bottom). Every earlier firing date
(2022-10-19 through 2022-11-09) **fails the bar specifically because of
the 6-month drawdown constraint**, not because it never recovered:

| Entry date | Max drawdown within 6mo | Eventually hit 5x? | Passes? |
|---|---:|---|:---:|
| 2022-10-19 | **-75.2%** | Yes, in 496 days (~16mo) | ❌ no — drawdown breach |
| 2022-11-04 | -57.5% | Yes, in 257 days | ❌ no — drawdown breach |
| 2022-11-08 | -49.5% | Yes, in 246 days | ❌ no — drawdown breach |
| **2022-12-07** | **-2.9%** | **Yes, in 183 days** | **✅ yes** |

Every one of these entries *eventually* multiplied — the difference is
purely how much pain came first. An account that bought CVNA on the first
signal (Oct 19) and had a real 30% stop-loss discipline would have been
stopped out around -30% (roughly early November) and never seen the
6,459% two-year return that materialized from the December entry. This is
the same "being early to oversold isn't the same as being at the bottom"
finding as before, now precisely quantified: **CVNA's screen re-fired 9
times over ~7 weeks as the stock kept falling, and only the last of those
9 signals was actually tradeable under a real risk constraint.**

## What this suggests, concretely

1. **A single technical fire is not enough — the *pattern* of repeated
   fires and how the drawdown behaves after each one carries real
   information.** CVNA's later, calmer fires (smaller subsequent
   drawdown, faster time-to-5x) were the tradeable ones; the early,
   still-falling fires weren't. A rule like "wait for the screen to fire
   without a new closing low for N sessions" might separate these
   better than firing on RSI/Williams alone — worth a follow-up
   experiment, not implemented here.
2. **HOOD and INTC's 100% pass rates are the real prize finding** — every
   single day the mechanical screen fired for these two names would have
   been both survivable (never >30% further down within 6 months) and
   eventually hugely profitable (5x). That's a much stronger result than
   "the screen sometimes works."
3. **PTON's 0/11 is exactly the false-positive case this bar is meant to
   catch**, and it does — cleanly, unlike the raw-forward-return version
   of this experiment which made a couple of PTON's entries look
   superficially competitive with real winners.

## Honest gaps, unchanged from before

- Only 4 cases (3 winners, 1 non-winner) — not a statistically meaningful
  sample; see `RUBRICS.md`'s own 5-case minimum. More non-recovery cases
  in particular would meaningfully strengthen this.
- Only tests 2 of Category A's 7 mechanical criteria (RSI, Williams %R).
  Stochastic/Bollinger/Support/PEG and Category C's momentum criteria are
  all computable with the same functions but not wired in yet.
- Fundamentals and judgment criteria still can't be backtested this way —
  see `../DESIGN.md`. `judgment_experiment.py` (built, calls the real
  Claude API, needs `ANTHROPIC_API_KEY`) is the intended supplement for
  the judgment half, with an explicit date-anchored anti-hindsight prompt
  design — still not run in this sandbox.
