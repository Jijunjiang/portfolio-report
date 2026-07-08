# Research plan — expanding to a 98-criterion candidate pool

This documents the plan behind `experiments/prompts/full-rubric-100.csv`
(65 new candidate criteria + the original 33). It didn't exist as a
written document when the work happened — the plan only lived in the
instructions given to four parallel research passes, which isn't part of
the repo and isn't reproducible from memory alone. Writing it up after
the fact so the reasoning and citations are actually preserved.

## Goal

Go from 33 scored criteria to roughly 100, per direct instruction: "need
100 individual rubrics, we can reduce later or give score 0 later" — i.e.
bias toward a broad, well-researched candidate pool now, prune later with
evidence (the normal `rubric-engine` hill-climb process), not toward
getting the count exactly right up front.

## Category breakdown

The existing 33 already covered five categories (A: value/drawdown,
B: financial quality, C: momentum, D: catalyst/story, E: risk/portfolio
fit) plus a standalone gate (criterion 33: domain leadership). Eight new
categories were chosen to cover the major areas of real equity-analysis
practice not yet represented:

| New category | Criteria | What it covers | Why it was missing |
|---|---:|---|---|
| F — Valuation depth | 10 | EV/EBITDA, FCF yield, Graham Number, P/S, P/B, forward P/E, shareholder yield, Price/FCF | The existing rubric has PEG (criterion 7) but no broader valuation toolkit — a stock can be cheap on PEG and expensive on every other multiple |
| G — Growth quality | 8 | Revenue/EPS CAGR, revenue acceleration, estimate revisions, Rule of 40, margin expansion | EPS trend (criterion 16) is the only existing growth signal, and it's binary improving/flat/worsening, not a real growth-quality read |
| H — Balance sheet / financial health | 8 | Altman Z-score, Piotroski F-score components, current ratio, interest coverage, debt/EBITDA | Criterion 17 (leverage) is pure judgment with "no direct debt filter exists" — this category asks whether that's actually true or just under-researched |
| I — Ownership & sentiment | 8 | Insider-buying clusters, short interest/days-to-cover, institutional ownership trend, analyst target gap | Nothing in the original 33 looks at who else is buying/selling — a real signal class in practice |
| J — Additional technical/momentum | 10 | Relative strength, golden/death cross, ATR volatility regime, OBV trend, 52wk breakout, Ichimoku, 12-1 momentum | Existing Category C covers MACD/EMA/Aroon/ADX/relative-volume/RSI-recross; this extends technical coverage without duplicating those |
| K — Additional catalyst/event | 8 | Buyback, index-inclusion mechanics, 13D activist filings, insider buying, analyst actions, guidance raise, regulatory approval, M&A rumor | Existing Category D covers earnings beat/window and sector tailwind/catalyst judgment; this adds specific, named event types |
| L — Business quality / moat | 8 | Moat *type* (network/brand/switching-cost/scale/regulatory), moat durability trend, insider alignment, recurring revenue %, customer concentration, TAM momentum, pricing power, capital intensity | Criterion 33 asks *whether* a company is a leader (a rank question); this asks *what kind* of moat and how durable (a mechanism question) — deliberately not a duplicate |
| M — Macro/sector positioning | 5 | Sector relative strength, rate sensitivity, business-cycle positioning, commodity/FX exposure | Nothing in the original 33 places a candidate in its macro/sector context at all |

## Research requirement given to each pass

Each of the four research passes (paired two categories each: F+G, H+I,
J+K, L+M) was required to:

1. **Use real, citable frameworks, not invented thresholds.** What came
   back: Graham's Graham Number formula (*The Intelligent Investor*),
   Altman's 1968 Z-score, Piotroski's 2000 F-score components, Lakonishok
   & Lee's 2001 (*Review of Financial Studies*) insider-cluster-buying
   finding, Jegadeesh & Titman's 1993 (*Journal of Finance*) momentum
   factor, Wilder's 1978 ATR formula, Granville's 1963 On-Balance Volume,
   Morningstar's five-source economic moat framework, S&P Dow Jones
   Indices' actual index-inclusion mechanics, and academic 13D
   activist-filing research (Brav/Klein/Zur; Greenwood & Schor).
2. **Phrase every criterion as a plain-English question**, matching the
   existing `question` column style in `reports/rubric-questions.csv`.
3. **Tag each [M] mechanical or [J] judgment**, and for [J] criteria write
   a persona-tailored system instruction (senior equity analyst / credit
   analyst / technical chartist / merger-arb analyst, matched to the
   specific criterion) using the same STRICT TIME BOUNDARY anti-hindsight
   framing already established in `judgment_experiment.py`.
4. **Say explicitly when a needed data source doesn't exist in this
   project's toolset**, rather than assuming one — this is what surfaced
   the "HONEST GAP" rows in Category H and several of I/K (no Form 4
   insider data, no 13F ownership data, no SEC 13D filings, no raw
   balance-sheet line items available from any connected tool today).
5. **Avoid ID collisions and duplicate questions** against the existing 33
   and against each other's assigned categories.

## What happened after

All four passes' output got merged into `experiments/prompts/
full-rubric-100.csv` (98 rows total, validated for schema consistency and
zero ID collisions) and wired into `RUBRIC-ENGINE.md` / the
`rubric-engine` skill as a candidate pool — see that skill's Step 3 and
`RUBRIC-ENGINE.md`'s "Research can move fast; promotion to the live
rubric still can't" section for how a pool criterion is meant to actually
get used (evidence + human approval, same as any other rubric change,
never just because the research behind it is good).

## What this plan doesn't cover

- No formal criteria for *why* these 8 categories specifically, versus
  some other split — they were chosen to cover the major areas of
  real-world equity analysis not yet represented, not derived from a
  more rigorous prioritization method.
- No cross-checking yet for how much the new criteria correlate with
  each other or with the existing 33 (e.g. Category H's Altman Z-score
  and the existing criterion 17's leverage judgment are answering
  related questions from different angles — deliberately, but untested
  for redundancy).
- No priority ordering among the 65 for which should be promoted first
  if/when evidence supports doing so — that's `rubric-engine`'s job when
  it actually happens, not pre-decided here.
