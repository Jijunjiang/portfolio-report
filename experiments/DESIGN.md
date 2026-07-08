# Experiment design — does the opportunity-scanner strategy actually work?

**Question:** if this rubric had been running in the past, would it have
picked out the stocks that went on to multiply (the HOOD/INTC pattern this
whole system was built around) before they skyrocketed, without also
flagging things that stayed broken? Answered with real historical data
and a real model call, not opinion — extending
`.claude/skills/opportunity-scanner/validation.md`'s informal check into a
scripted, repeatable experiment.

## Two-part design, because the rubric has two kinds of criteria

The rubric (`rubric.md`) is explicitly split into **[M] mechanical**
criteria (computed from data) and **[J] judgment** criteria (need real
reasoning). Those need two different kinds of experiment — you can't
backtest a judgment call with a price chart, and you can't ask an LLM to
"reason about" what RSI was.

### Part 1 — `backtest.py`: mechanical criteria, tested against real price history

Uses `compute_rubric.py`'s indicator functions (already built and verified
against live data earlier this session — see that script's own docstring)
against full historical OHLCV bars. For each known case, scans a window
around the actual trough date and checks, **using only data available up
to that day** (no lookahead), whether the live turnaround screen's actual
thresholds (RSI(14)<30 AND Williams%R(14)<-80) would have fired — then
reports the real forward return at 3mo/6mo/1yr/2yr from each firing date.

No LLM involved in this half — it's pure historical math, which is why it
can be fully automated and re-run any time new cases are added.

### Part 2 — `judgment_experiment.py`: judgment criteria, tested against a real Claude API call

The mechanical backtest structurally cannot evaluate `a8_cyclical_judgment`
or `b33_domainleadership_judgment` — those need to read a company's
situation and reason about it, which is exactly what an LLM call is for.
This script sends each case's **point-in-time-only** facts (what was
publicly known as of the trough date, deliberately excluding anything
about what happened after) to the real Claude API using the same scoring
rubric a live opportunity-scan session would use, and records what score
it produces versus the actual known outcome.

This is the direct answer to "can you just run the rubric" for the
judgment criteria — yes, and this script is that call made programmatic
and repeatable instead of asked once in a chat.

## Case registry

`cases.py` (used by both scripts): HOOD, INTC, CVNA (all recovered after
70-99% drawdowns) and PTON (did not recover despite a 98% drawdown) — the
same four cases `validation.md` already established, now with exact
trough-window dates and outcome facts machine-readable instead of prose.

## Honest limitations (read before trusting any result)

- **Mechanical backtest**: only tests 2 of Category A's 7 mechanical
  criteria so far (RSI, Williams %R — the two used in the live turnaround
  scan's own Stage-0 filter). Stochastic/Bollinger/Support/PEG and all of
  Category C are computable with the same functions but not wired into
  `backtest.py` yet — a real next step, not a fundamental blocker.
- **Judgment experiment**: HOOD/INTC/CVNA/PTON are all well-known,
  heavily-covered situations. Any model asked about them — including the
  one this script calls — very likely has training-data knowledge of how
  each story actually ended, which no amount of careful prompt-phrasing
  can fully eliminate. This is a plausibility check on whether an LLM
  *can produce the right kind of reasoning*, not proof the judgment layer
  would have worked blind, in real time, historically. The real validation
  of the judgment layer is the live pipeline already running (today's
  actual candidates, scored now with no outcome yet known, resolved
  quarterly by `rubric-engine`) — this experiment supplements that, it
  doesn't replace it.
- **Fundamentals** (margins, ROE, PEG, dividend yield) can't be backtested
  at all — `get_equity_fundamentals` only returns a current snapshot, no
  point-in-time historical fundamentals API exists here. Same gap
  `validation.md` already flagged.
- **4 cases is not a statistically meaningful sample** — `RUBRICS.md`'s
  own rule is never refine on fewer than ~5 resolved cases per category;
  this is well under that. Every result here is a sanity check /
  existence-proof, not a backtested hit rate.

## Results so far (2026-07-07 run, updated with the low-risk/high-reward bar)

Full data: `results/summary.md`, `results/*-backtest.json`. Full writeup:
`results/FINDINGS.md`. `backtest.py` now scores each firing date against a
precise, decision-relevant bar instead of a raw forward-return percentage:
**never more than 30% down within 6 months of entry, and eventually
reaches 5x**. Under that bar the screen discriminates cleanly: **HOOD
1/1 and INTC 9/9 firing dates pass (100% each); PTON 0/11 (0%) — it never
reaches 5x from any entry point in the available data.** CVNA is the
nuanced case: only its very last firing date (right at the actual bottom)
passes — every earlier fire breached the 30% drawdown constraint even
though all of them eventually multiplied, showing precisely that being
early to "oversold" during a real capitulation is not the same as being
at the bottom. See `FINDINGS.md` for the full breakdown.

The judgment experiment (`judgment_experiment.py`) is built and ready to
run but needs `ANTHROPIC_API_KEY` set, which isn't available in this
sandboxed environment — run it separately with real API credentials to
get that half of the picture.

## Related: the 98-criterion candidate pool

Separate from the backtest above, `experiments/prompts/full-rubric-100.csv`
holds a much larger candidate criteria pool (33 live-scored + 65
researched-but-not-yet-live) — see `RESEARCH-PLAN.md` for the category
breakdown and citations, and `RUBRIC-ENGINE.md` for how a pool criterion
is meant to get promoted (evidence + approval, same as any other change).

## Extending this

- Add more cases, especially more `did_not_recover` ones (only 1 of 4
  today) — the false-positive side is the more decision-relevant half and
  the most underrepresented in this sample.
- Wire in the remaining Category A/C criteria to `backtest.py`.
- Run `judgment_experiment.py` with a real API key and fold the result
  into `FINDINGS.md`.
- Consider a genuinely blind version of the judgment experiment using a
  *recent, less-famous* candidate (something from today's actual
  `reports/opportunity-scanner-logs/*.csv` whose outcome isn't resolved
  yet) instead of a historical case an LLM may already know the ending
  to — the cleanest way to actually eliminate the hindsight-contamination
  risk flagged above.
