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

## 0. Four archetypes across the risk/return spectrum

Two archetypes (Turnaround, Quality Inflection) existed originally; two
more (Moonshot Growth, Steady Value) were added 2026-07-07 because they
are structurally different opportunities that the original two scans
conflated. Each has its own Stage 0 prefilter scan and gets scored/logged
with `archetype` set to the tag below and logged to
`reports/opportunity-scanner-logs/` (one CSV per run — see step 6).

| Archetype | Risk / Reward | Pattern | Scan ID | ~Daily matches |
|---|---|---|---|---|
| `turnaround` | High risk, 5-10x | Distressed, established company recovers (HOOD, INTC) | `38edc26c-8b66-4235-9f3b-40275bb6cb7f` | 20 raw (was 32 pre-profitability filter), ~3 pass the 40%-off-high gate |
| `moonshot_growth` | High risk, 10x+ | Small/mid-cap, no distress — explosive momentum/growth, not mean-reversion | `fd3c2707-3c1c-4283-9223-d5e447ae8425` | 61 (was 76) |
| `compounder` (Quality Inflection) | Medium risk, 2-5x | Quality business, secular tailwind, "buy NVDA/TSM early" | `2a31c406-2b3f-4552-bcb4-6e78ceaba979` | 71 (already required positive profit) |
| `steady_value` | Low risk, ~30-50% | Traditional blue-chip, undervalued not distressed | `95b3655e-8750-46ec-b835-c933ae316999` | ~94 (was ~91; op-margin>10% already implied positive profit for most) |

**All four archetypes now require `Net profit margin > 0` (added
2026-07-07)** — a deliberate, user-directed narrowing to currently-
profitable companies only. Worth naming the tradeoff explicitly for
`turnaround` specifically: HOOD and INTC were not reliably profitable at
their actual beaten-down entry points (per `validation.md`), so this
filter could exclude a real future HOOD/INTC-style setup in exchange for
screening out the higher-risk still-unprofitable distressed names. That's
the deliberate choice made here, not an oversight — revisit via
`rubric-engine` once enough turnaround rows resolve to show whether this
filter is costing good picks or correctly avoiding bad ones.

`moonshot_growth` and `steady_value` are read-only-scoring at this point
(no dedicated playbook subsections yet) — they reuse `rubric.md`'s
Category B/D/E and skip Category A the same way `compounder` does; see
each scan's filter set below for what's mechanically enforced at Stage 0
versus what step 6 scores afterward.

## 1. The saved scans — this is the Stage 0 prefilter

Each scan *is* a rubric itself — a hard-cutoff, binary pass/fail prefilter
that runs before `rubric.md`'s weighted ~98-point scoring ever starts (see
`../../../RUBRICS.md`'s lifecycle: this is Stage 0, not a separate ad hoc
thing). Tuned so each archetype's daily universe is small enough to fully
score and log every survivor (see step 6), loose enough not to miss real
candidates. Changes to any of these filters get logged to
`reports/rubric-changelog.csv` (`rubric=opportunity-scanner,
category=prefilter-<archetype>`) exactly like a weighted-criterion change
would.

- **`38edc26c-8b66-4235-9f3b-40275bb6cb7f`** — "Deep Value Turnaround
  Candidates": `Market cap > $2B`, `RSI(14) < 30`, `Williams %R(14) < -80`,
  `Net profit margin > 0` — the RSI+Williams combination requires two
  independent oversold signals to agree, sorted by RSI ascending. **20
  matches as of 2026-07-07** (32 before the profitability filter was
  added). Note: this combination still does *not* filter out a
  short-term dip inside an uptrend (CRWD clears both RSI<30 and
  Williams<-80 while being only 2.5% off its 52-week high) — that's a
  structural limit of technical oscillators, not something more scan
  filters fix. Step 2 below (the 52-week-high distance check) remains
  mandatory for exactly this reason. A `FILTER_TYPE_STOCHASTIC_OSCILLATOR`
  filter was tried and rejected — the scanner backend has a template bug
  on that specific filter type (`%!s(MISSING)Stochastic(...)`) regardless
  of parameters; don't retry it until Robinhood fixes it server-side.
- **`2a31c406-2b3f-4552-bcb4-6e78ceaba979`** — Growth Compounder screen
  (feeds `compounder`/Quality Inflection): `Market cap > $1B`,
  `PEG < 0.35`, `Return on equity > 25%`, `Operating margin > 0`,
  `Net profit margin > 0`, sorted by PEG ascending. Tightened from the
  original `PEG < 1.5, ROE > 15%` (394 matches — far too broad for a daily
  full-evaluation pass) by both raising the valuation/quality bar and
  adding explicit profitability filters (the "not a value trap"
  quality-factor logic from `RUBRICS.md`'s Quality Minus Junk citation,
  now enforced at the scan level instead of only in step 4's manual read).
  **~71 matches as of 2026-07-07.** Includes margin/ROE as visible
  columns, so those criteria are computable from the scan result alone —
  no extra fundamentals fetch needed for Category B.
- **`fd3c2707-3c1c-4283-9223-d5e447ae8425`** — "Moonshot Growth
  Candidates": `Market cap BETWEEN $300M-$15B`, `RSI(14) > 75`,
  `Aroon Oscillator > 70`, `ADX > 25`, `Net profit margin > 0` — confirmed
  strong uptrend (not a one-day spike) in small/mid-cap names, the inverse
  screen of the turnaround archetype. **61 matches as of 2026-07-07** (76
  before the profitability filter; that scan's own Net profit margin
  column is now usable directly for Category B, unlike before when it had
  no fundamental columns at all). A `FILTER_TYPE_RELATIVE_VOLUME` filter
  was tried first and returned 0 matches when combined with RSI — dropped
  in favor of Aroon+ADX for trend confirmation instead.
- **`95b3655e-8750-46ec-b835-c933ae316999`** — "Steady Value Compounders"
  (feeds `steady_value`): `Market cap > $10B`, `P/E BETWEEN 0-18`,
  `Return on equity > 15%`, `Operating margin > 10%`,
  `Net profit margin > 0`. **~94 matches as of 2026-07-07** — the added
  profitability filter barely moved the count since `Operating margin >
  10%` already implied positive profit for nearly every match; also now
  gives a real Net profit margin column for Category B instead of relying
  on Operating margin as a proxy. No dividend-yield filter exists in the
  scanner's filter spec at all (checked `trading://scanner-filter-specs`
  directly) — can't prefilter on it, only check individually.

**Data-availability note, found while scoring 2026-07-07:**
`get_equity_fundamentals` does **not** return margin/ROE/ROA fields under
any circumstance — those only appear when a *scan's own columns* include
them (because that scan applied a matching filter). This means Category B
scoring is only as complete as each archetype's scan filters make it:
`compounder` and `steady_value` get real margin/ROE from their scan
columns; `turnaround` and `moonshot_growth` don't have those filters, so
Category B is scored on market cap/dividend/liquidity alone for those two
archetypes unless a future run adds a separate fundamentals-based lookup.

**Category C is not a hard gap — see `reports/rubric-data-sources.csv`.**
Three of its six criteria's scanner filters are permanently broken
server-side (Stochastic, Bollinger, Support all share the same backend
bug), but `get_equity_historicals`/`get_option_historicals` are confirmed
working with real daily OHLCV data for both equities and options — every
Category C criterion (and the trend-vs-snapshot gap on MACD/Aroon/ADX) is
computable client-side from that data. No external connector needed. The
calculation code (RSI, MACD, Bollinger, Stochastic, a support-level
heuristic) just hasn't been written yet — that's the next real piece of
engineering here, not a data-availability wall.

Re-run any scan with `run_scan` any time; all are visible in the
Robinhood app's screener section too, not just here. `update_scan_filters`
/ `update_scan_config` can retune them (full reference:
`trading://scanner-filter-specs` resource lists every available filter —
fundamental, price/volume, technical, and options). Re-check each
archetype's match count after any retune — if it drifts materially
outside ~50–100, that's the signal to tune again, logging the change
either way.

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

## 3. Domain-leadership gate, then score survivors with `rubric.md`

`rubric.md` has 31 scored criteria across five categories (value/drawdown
depth, financial quality, momentum confirmation, catalyst/story, risk &
portfolio fit) plus 2 hard gates that run *before* scoring and can
disqualify a candidate outright — see that file's "Gates" section. One gate
(net profit margin > 0) is already enforced at Stage 0 by the saved scans
themselves (step 1); the other (criterion 33, domain leadership) is a
judgment call that has to be made per candidate, so it runs here, first,
before the rest of the rubric:

1. For every candidate that cleared step 2 (or, for non-turnaround
   archetypes, every Stage 0 survivor), make the domain-leadership call —
   dominant #1/#2, solid niche leader/#3-4, or sub-scale/commoditized/
   disruptable. This is the slowest call to make honestly: budget a
   `WebSearch` per candidate when the company description alone doesn't
   make the competitive position obvious.
2. **Dominant or niche leader → proceed** to score the full rubric (all
   31 remaining criteria) normally.
3. **Sub-scale/commoditized/disruptable → stop.** Log a disqualified row
   (ticker, date, archetype, `b33_domainleadership_judgment=0`, everything
   else `N/A`) and move to the next candidate — don't spend further tool
   calls scoring the rest of the rubric for a candidate that's already
   disqualified.

≥70 = strong candidate, 50–69 = watchlist, <50 = discard, for whatever
passes the gate — see `rubric.md` for the exact per-criterion scoring and
the mechanical-vs-judgment split.

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

## 6. Cadence — daily full evaluation of the prefiltered set, quarterly outcome review

The Stage 0 prefilter (step 1) is what makes this affordable: at ~100
combined matches/day, the full 31-criterion rubric (plus the domain-leadership gate) can run on **every**
survivor, every day, not just a cheap mechanical subscore on a few
hundred. This replaced an earlier "mechanical-only daily, full rubric
only for high scorers" design once the prefilter itself was tightened
enough to make full daily evaluation practical — see
`reports/rubric-changelog.csv` for that change.

**Every day, as part of `portfolio-report`:**
1. Run both saved scans (step 1) — ~100 combined matches.
2. Batch-pull `get_equity_fundamentals` (10 symbols per call, ~10-11
   calls total) for every match. This one batched pull covers most of
   what the rubric needs directly: `high_52_weeks`/`low_52_weeks` (step
   2's gate), margins/ROE/market cap (Category B), and — usefully — each
   company's `description`/`sector`/`industry`, which is enough raw
   material to make Category B/D's judgment calls (cyclical vs.
   structural, sector tailwind, catalyst) without a separate research
   pass per stock.
3. **Score one candidate at a time, not all ~100 in a single pass.** Loop:
   pick the next match → apply the full `rubric.md` to it (all 5
   categories) using the scan's own columns plus the batched fundamentals
   pull → apply step 2's ≥40%-off-high gate if it's a turnaround candidate
   → append its row to the log → move to the next match. Scoring is
   inherently a per-candidate judgment call (especially the [J] criteria);
   cramming all ~100 into one combined reasoning pass risks shallow,
   rushed scoring on the later names in the batch. One call's worth of
   fetched data (the batched fundamentals) can feed many sequential
   per-candidate scoring steps — it's the *scoring*, not the *data
   fetch*, that stays one-at-a-time.
4. **Log every single one** — full category breakdown, not just a
   subtotal, sell-worthy or not, gate-disqualified or fully scored. This
   is the "log everything" the account holder wants: every survivor of
   the prefilter gets a complete, resolvable data point, every day.
   **Logging convention (changed 2026-07-07): one CSV per run, never
   appended.** Write to `reports/opportunity-scanner-logs/YYYY-MM-DD-full-
   <archetype>.csv` (one file per archetype per run is fine — a later step
   or a human can merge them into `YYYY-MM-DD-full.csv` if a single
   combined view is wanted for that day). Never write into a prior run's
   file. The old single ever-growing `reports/opportunity-scanner-log.csv`
   is kept only as a historical snapshot from before this change — don't
   append to it.
5. Surface in that day's report only what's actually report-worthy
   (≥70 = full callout, 50–69 = one-line mention, <50 = not listed
   individually, gate-disqualified = one line in the caveats, not a full
   entry) — the log has everything regardless of what's shown.

**Quarterly outcome review:** unchanged in spirit — the `rubric-engine`
skill globs across every file in `reports/opportunity-scanner-logs/`
(not a single fixed path, since each run is now its own file), resolves
`outcome_1q`/`outcome_1y`, and proposes evidence-cited changes to either
the weighted rubric or this Stage 0 prefilter.

## 7. Files in this skill

- `rubric.md` — the 31-criterion scoring rubric plus 2 hard gates (step 3).
- `validation.md` — the backtest that shaped the rubric: HOOD/INTC/CVNA
  (recovered) vs. PTON (didn't, despite a near-identical drawdown) —
  read this before trusting category A alone on a new candidate.
- `refinement.md` — how the rubric gets tuned over time using
  `reports/opportunity-scanner-logs/` (one CSV per run): log every scored
  candidate, review outcomes quarterly, reweight/re-threshold on
  accumulated evidence. Not automated — a human-and-agent review loop
  matched to this account's quarterly cadence.

## 8. Rubric/validation page (separate from the daily portfolio dashboard)

`reports/opportunity-scanner.html` presents the rubric, the validation
backtest, and a preview of the daily mechanical signal — for a human to
read, not regenerated as often as the daily report. Redeploy it (Artifact
on the same file path, URL saved in
`reports/.opportunity-scanner-artifact-url`) when the rubric, validation
findings, or cadence logic materially change — not every daily run.
