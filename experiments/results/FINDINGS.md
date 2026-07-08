# Backtest findings — 2026-07-07

Full data in `summary.md` / `*-backtest.json`. This is the interpretation.
Read `../README.md` first for the honest scope (technical criteria only,
4 cases, not a statistically meaningful sample).

## Headline result: the pure technical screen does NOT reliably discriminate winners from PTON

This is the single most important finding, and it's a real quantitative
confirmation of what `validation.md` already argued qualitatively:

| Case | Times screen fired | Best 1yr forward return seen | Best 2yr forward return seen | Actual outcome |
|---|---:|---:|---:|---|
| HOOD | 1 | +45.6% | +222.9% | Recovered, 11x off the low |
| INTC | 9 | +19.8% | (insufficient data yet) | Recovered, 5.7x off the low |
| CVNA | 9 | +889.6% | +6459.0% | Recovered, 96.6x off the low |
| **PTON** | **11** | **+107.6%** | **+75.2%** | **Did not recover — still 96.6% below its all-time high** |

**PTON fired the screen more often than any winner except INTC/CVNA, and
some of its individual forward returns look competitive with the real
winners on paper** (+107.6% at 1yr from the 2024-04-24 entry is a better
1yr number than INTC ever produced). If you only looked at "did the
technical screen fire, and was the forward return positive," PTON would
have looked like a hit. It wasn't — the stock never recovered anywhere
near its highs; these are dead-cat bounces inside a structurally broken
business, not the start of a real recovery, and only look decent because
PTON's baseline was already so destroyed that even normal volatility
produces large percentage swings.

**This is exactly why the rubric's mandatory Category B/D judgment gate
exists and isn't optional polish** — the mechanical criteria alone
cannot tell HOOD from PTON. `validation.md`'s qualitative read (cyclical/
fixable vs. structural demand destruction) is doing real, necessary work
that no amount of RSI/Williams%R tuning would replace.

## Second finding: being early to "oversold" is not the same as being at the bottom

CVNA's own data shows this starkly within a single case: the screen fired
on 2022-10-19 (stock at $3.00) with **negative** 3mo/6mo forward returns
(-53%/-42%) — the stock kept falling for another six weeks to its actual
$0.71 low in December. An entry on the *first* fire date would have
meant enduring a further ~74% drawdown before the eventual 3,000%+
recovery. The screen re-fired multiple times on the way down (Oct 19-24,
Nov 4, Nov 7-9, Dec 7) — oversold conditions are not a single event during
a real capitulation, they recur. A mechanical "buy the first RSI<30
signal" rule would have been early and painful even in the case that
ultimately worked out best.

INTC shows a milder version of the same pattern: fired 9 times in early
August 2024, but the real low wasn't until September — several of the
August entries show negative 6mo returns before recovering by 1yr.

## Third finding: HOOD's single, precise fire is the outlier, not the norm

HOOD only fired the screen once, three days after the actual bottom
(2022-06-16 vs. the true low of 2022-06-13) — about as clean a signal as
this kind of screen could produce. But this is the exception across the
4 cases, not what to expect by default; INTC/CVNA/PTON all fired 9-11
times each across weeks or months, several while the stock kept falling.
Don't calibrate expectations of "how precise this screen is" off the HOOD
case alone.

## What this does and doesn't change

**Doesn't change**: the rubric's own design already treats Category A
(technical/drawdown) as a necessary-but-not-sufficient gate, never a
standalone buy signal, and already requires the Category A8/B/D judgment
read before anything reaches a shortlist. This backtest is a confirmation
of that design choice, not a discovery that something's broken.

**Does suggest** two concrete, evidence-backed follow-ups worth
considering (not implemented here — this is a finding to act on via the
normal `rubric-engine` process, with proper approval, not a silent
change):
1. A single-fire-date entry rule may be systematically premature (CVNA,
   INTC both show early fires losing money for months). Worth testing
   whether requiring the screen to fire on **multiple separate days**
   (not just once) before treating it as a real signal would have avoided
   the worst of the early-entry pain, without missing HOOD's single clean
   fire.
2. The forward-return magnitude alone is a bad tie-breaker between
   real winners and PTON-style fakes — some kind of "did the price
   actually reclaim a meaningful fraction of its former high" check
   (which Category C's EMA-reclaim criterion gestures at, but this
   backtest didn't test Category C at all yet) might discriminate better
   than raw technical oversold signals. Worth a follow-up experiment.

## Honest gaps in this experiment itself

- Only tested Category A's two turnaround gate criteria (RSI, Williams
  %R) — not the other 4 Category A criteria (Stochastic, Bollinger,
  Support, PEG) or any of Category C's momentum criteria, all of which
  `compute_rubric.py` can compute and a follow-up run should include.
- 4 cases (3 winners, 1 non-winner) is far too small to compute a real
  hit rate or false-positive rate — see `RUBRICS.md`'s own 5-case minimum
  for exactly this reason. This is a sanity check, not a statistically
  powered backtest. More cases (especially more non-recovery cases, which
  are underrepresented here at just 1 of 4) would meaningfully improve
  this.
