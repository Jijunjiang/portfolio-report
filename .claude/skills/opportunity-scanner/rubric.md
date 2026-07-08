# Opportunity scoring rubric

A composite score built from 31 *scored* criteria across 5 categories,
plus 2 hard gates that run before scoring and can disqualify a candidate
outright rather than just docking points (see "Gates" below). Each scored
criterion is tagged **[M]** mechanical (computed directly from a tool) or
**[J]** judgment (requires reading/context, not a pure number) — roughly
two-thirds mechanical, one-third judgment. Don't present a [J] criterion's
score as more precise than it is.

## Gates (not scored — pass/fail, applied before the rest of the rubric)

Two criteria are disqualifying gates, not point contributions. A candidate
that fails a gate does not get the rest of the rubric scored — log it as
disqualified (ticker, date, archetype, the gate that failed) rather than a
full scored row padded with N/A.

- **Net profit margin > 0** — enforced at Stage 0, the scan level, for
  *every* archetype (see SKILL.md step 1's saved-scan filters). Every
  candidate that reaches this rubric has already passed it, which means
  scoring it again as a point criterion can never discriminate anything —
  it would score the same for 100% of rows. Retired as a scored criterion
  2026-07-07 (was `b12_netmargin`, 2 pts in Category B). If Category B's
  own margin criteria (10, 11) later need a finer profitability read than
  the Stage 0 gate provides, add a *new* criterion rather than reviving
  this one — see the changelog.
- **Domain leadership** — see criterion 33 below. Converted from a scored
  [J] criterion to a gate 2026-07-07, per user direction ("I hate risk —
  should be top-tier in its domain, not just a nice-to-have I average
  into a score").

**Before scoring a criterion, check `reports/rubric-data-sources.csv`** —
the verified fetch method for each criterion, including which
scanner filters are confirmed working, which are server-side broken
(Stochastic, Bollinger, Support — the *scanner filters* for these are
broken, don't retry them), which are unreliable (Relative Volume's own
scanner filter returns a constant 1.0 in some scan combinations — use the
historicals-based calc below instead), and which have no direct fetch at
all by design (`b17_leverage_judgment`, `e32_fitstyle_judgment` are
judgment-only, not a data gap). Don't re-derive this from scratch each
run — it was researched and tested live against the API on 2026-07-07,
then **actually verified on a real test ticker (NVDA) on 2026-07-07** —
see `reports/rubric-fetch-verification-2026-07-07.csv`. Every one of the
33 criteria produced a real value on that ticker; nothing in this rubric
is theoretical-only anymore.

**Historicals-based calculations (criteria 4, 5, 6, 18, 22, 23) — now
implemented, not just theoretically possible.** These six needed
`get_equity_historicals` (daily bars, ~44 trailing sessions covers all six)
plus a client-side calculation instead of a scanner filter:
- **Stochastic %K(14)** (criterion 4): `(Close − Lowest Low(14)) /
  (Highest High(14) − Lowest Low(14)) × 100`.
- **Bollinger Bands** (criterion 5): 20-day SMA of Close ± 2×stdev;
  "below lower band" = Close < SMA − 2×stdev.
- **Support** (criterion 6): trailing 20-day low of the Low series — a
  chosen heuristic, not a universal formula, but now the documented
  standard for this criterion.
- **MACD histogram trend** (criterion 18): EMA(12) − EMA(26) = MACD line,
  EMA(MACD, 9) = signal line, histogram = MACD − signal; "turned positive"
  = a sign flip from ≤0 to >0 in the trailing ~10 sessions. **Don't use the
  scanner's own `FILTER_TYPE_MACD` filter for this** — it takes a single
  `length` param (not the standard 12/26/9), measures something different,
  and gave a materially different number than the real MACD on a live
  side-by-side test.
- **Relative volume on up days** (criterion 22): today's volume ÷
  trailing-30-day average volume, paired with a Close > Open check for the
  "up day" qualifier. Use this instead of `FILTER_TYPE_RELATIVE_VOLUME`
  (confirmed unreliable — see above).
- **RSI crossback** (criterion 23): standard Wilder's-smoothing RSI(14)
  computed across the full bar series; scan for any point where RSI drops
  below 30 then a later point where it's back ≥30. If RSI never dipped
  below 30 in the window, that's a real, correctly-computed `0` (no
  signal) — not a reason to leave the cell `N/A`.

One `get_equity_historicals` call per candidate (44 daily bars) covers all
six of these — reuse the same pull rather than fetching separately per
criterion.

**Guide score, not a verdict:** ≥70 = strong candidate worth deep research.
50–69 = watchlist, revisit next quarter. <50 = discard for now. These
bands are a starting point, not calibrated against a large sample —
HOOD's setup would have scored high on category A alone; treat the bands
as directional.

Run this on candidates that already passed the two saved scans — see
SKILL.md step 1, which is Stage 0 of this rubric (a hard-cutoff prefilter,
tuned to ~100 combined daily matches so every survivor can get the full
score below, not just a subset). This ~98-point rubric (31 scored criteria
plus 2 hard gates — see "Gates" above) is Stage 1 of the
same lifecycle (`../../../RUBRICS.md`) — for scoring/ranking the
prefiltered set, not for scanning the whole market from scratch.

## Category A — Value / drawdown depth (30 pts)

Only relevant for the deep-value-turnaround archetype; skip for growth
compounders (go to Category D instead for their equivalent).

1. **[M]** % off 52-week high: ≥85%→8, ≥70%→6, ≥55%→4, ≥40%→2, <40%→0.
   (Calibration: HOOD's real entry was 92% off high, INTC's 72%.)
2. **[M]** RSI(14): <20→3, <30→2, else 0.
3. **[M]** Williams %R < -80 → 2, else 0 (confirms oversold, independent of RSI).
4. **[M]** Stochastic oscillator < 20 → 2, else 0.
5. **[M]** Price below lower Bollinger Band → 3, else 0 (statistical extreme, not just RSI).
6. **[M]** Price at/below computed Support level (`FILTER_TYPE_SUPPORT`) → 3, else 0.
7. **[M]** PEG < 1 despite the drawdown (cheap even adjusted for whatever growth remains) → 2, else 0.
8. **[J]** Drawdown looks cyclical/sentiment-driven rather than a structural business breakdown → 4, unclear → 2, looks structural → 0.

## Category B — Financial quality / not a value trap (23 pts)

9. **[M]** Market cap > $2B → 3 (established company, matches both HOOD and INTC's scale at entry).
10. **[M]** Gross margin > 30% → 2, else 0.
11. **[M]** Operating margin > 0% → 2, else 0 (don't require high — turnarounds are often thin here).
12. **Retired 2026-07-07** — was net profit margin, now a Stage 0 gate (see "Gates" above). Column `b12_netmargin` stays in the log schema for backward compatibility but is no longer written to (leave `N/A`) and no longer contributes to `category_b`/`total_score`.
13. **[M]** ROE > 10% → 3; > 0% → 1; negative → 0.
14. **[M]** ROA > 5% → 2; > 0% → 1; negative → 0.
15. **[M]** Dividend still being paid (`dividend_yield` non-null) through the drawdown → 2 (cash flow survived), else 0.
16. **[M]** EPS trend improving over the last 2–4 reported quarters (`get_earnings_results`) → 3, flat → 1, worsening → 0.
17. **[J]** Balance sheet / leverage doesn't look stretched relative to the sector norm → 2, uncertain → 1, looks stretched → 0.
   (No direct debt filter is available — infer from P/B, sector, and the company description; say this is an approximation.)

## Category C — Momentum: is the turn actually happening? (20 pts)

18. **[M]** MACD histogram has turned positive in the last ~2 weeks → 4, else 0.
19. **[M]** Price has reclaimed a key EMA (e.g. 50-day) → 3, else 0.
20. **[M]** Aroon Oscillator has turned positive → 3, else 0.
21. **[M]** ADX shows a strengthening trend (rising, not just high) → 2, else 0.
22. **[M]** Relative volume > 1.3 on up days specifically (accumulation, not just noise) → 4, else 0.
23. **[M]** RSI has crossed back above 30 after being below it (recovering from oversold, not still falling) → 4, else 0.

## Category D — Catalyst / story (15 pts) — also used for growth compounders

24. **[M]** Most recent reported quarter beat EPS estimate (`get_earnings_results`) → 3, missed → 0, in-line → 1.
25. **[M]** No earnings report inside the next 2 weeks (avoids scoring a candidate that's about to have its thesis re-priced overnight) → 2, else 0 — informational, not disqualifying.
26. **[J]** Sector/theme has a genuine multi-year tailwind (not just a bounce) → 4, neutral → 2, headwind → 0.
27. **[J]** Company description or recent history suggests a real inflection point (new leadership, restructuring, product cycle) rather than "waiting for the same thing to work eventually" → 3, unclear → 1, no visible catalyst → 0.
28. **[J]** For growth compounders specifically: PEG < 1.5 and ROE > 15% together (already the scan's own filter — treat clearing both as the full 3, one only as 1).

## Category E — Risk & portfolio fit (10 pts)

29. **[M]** Average volume / float supports easily entering and exiting a position of the size this account would actually take → 2, marginal → 1, illiquid → 0.
30. **[M]** Not already a large position in this name or its sector in the account (checked against current holdings) → 2, else 0 — avoid compounding existing concentration.
31. **[M]** Historical/implied volatility elevated but not at "distressed debt" extremes (i.e. the market is pricing real risk, not a going-concern doubt) → 2, else 0.
32. **[J]** Position would fit the account's stated few-trades-per-quarter, high-conviction style rather than needing active monitoring → 2, else 0.

## Criterion 33 — Domain leadership gate (added 2026-07-07, converted to a gate 2026-07-07)

User-directed: "I hate risk — judge whether this is a company I could buy
and hold for 10 years, top-tier in its domain." Originally added as a
scored [J] criterion (5/2/0 pts); converted to a hard gate the same day
once the user clarified this should disqualify, not just dock points —
"those are not scores, should be prefilter, skip stocks not qualified."
Numbered 33 rather than inserted into Category B's own sequence — inserting
mid-sequence would have renumbered every criterion after it and broken the
column mapping in the 251 rows already logged before this date. Applies to
**all archetypes**, not just turnaround — a risk-averse durability filter
belongs everywhere this account puts money, not only in the distressed-
value screen.

Make the same judgment call as before, but the outcome is now qualify/
disqualify rather than a point value:

33. **[J]** Company is a top-tier / dominant leader in its specific market
    domain — clear #1 or #2 position, with a durable moat (scale, brand,
    network effects, switching costs, regulatory barrier, or a
    technological lead a competitor can't quickly close) → **qualifies**,
    logged as `5`. Solid leader in a narrower niche, or a clear #3–4 in a
    larger domain, real but not airtight moat → **also qualifies**, logged
    as `2` (both tiers proceed to the rest of the rubric — user confirmed
    2026-07-07 that a real niche-leadership position is good enough, only
    the bottom tier below should be screened out). Sub-scale, commoditized,
    easily disrupted, or not a business worth holding through a decade →
    **disqualified**, logged as `0` — stop here, do not score the rest of
    the rubric for this candidate, log it as a disqualified row (ticker,
    date, archetype, `b33_domainleadership_judgment=0`, everything else
    `N/A`) rather than a fully scored one.

    The `5`/`2` values are still recorded in the log for future
    correlation analysis (does niche-leader vs. dominant-leader actually
    predict different outcomes?) but neither contributes to
    `total_score`/`category_b` anymore — this is a gate, not a weight.

    This is a judgment call about the *business*, not the *stock price* —
    don't conflate it with Category A's drawdown-depth criteria (a cheap,
    deeply-oversold stock can still fail this if it's a weak player in its
    domain) or Category D's tailwind criterion (a strong sector tailwind
    can lift a mediocre #4 player too, which is exactly the distinction
    this criterion is for). Ground the call in the company description,
    market cap relative to known competitors, and — when genuinely
    uncertain — a `WebSearch` for the company's actual competitive
    position, rather than guessing from the sector label alone.

**Retroactive note:** none of the 251 rows logged 2026-07-07 have this
criterion actually scored yet (it was appended as a new column, all `N/A`
— genuine "not yet assessed," not "assessed and passed"). Converting it to
a gate here doesn't retroactively disqualify any existing row; it changes
how this criterion gets applied going forward, the next time each
archetype's daily scan is scored end-to-end.

## Presenting a scored candidate

Show the category subtotals (A–E out of their max), not just the final
number — a candidate scoring 60 from strong value + weak momentum reads
differently than 60 from strong momentum + no real discount, and the user
should see which. List which specific criteria drove the score down, not
just the criteria that drove it up — the discarded points are often the
most decision-relevant part.

## Changelog

Every reweight/add/retire gets one line here: date, what changed, why, and
which logged rows (across `reports/opportunity-scanner-logs/*.csv`, one
file per run) justified it. See `../../../RUBRICS.md` for the full
lifecycle this follows.

- **2026-07-07**: Added criterion 33 (domain leadership / 10-year-hold
  quality), 5 pts, applies to all archetypes. User-directed, not
  evidence-driven (no resolved rows exist yet to justify it either way —
  this is a Stage 1 addition from stated risk preference, not a Stage
  4 hill-climb). Numbered 33 rather than inserted into Category B's
  sequence to avoid breaking the column mapping already logged for 251
  prior rows.
- **2026-07-07** (same day, follow-up correction): Converted criterion 33
  from a scored [J] criterion to a hard gate — user clarified it should
  disqualify sub-scale/commoditized candidates outright, not just cost
  them points in a weighted average. Both the dominant-leader (`5`) and
  niche-leader (`2`) tiers still pass through to full scoring; only the
  bottom tier (`0`) is disqualified. User-directed, not evidence-driven.
  Also retired criterion 12 (net profit margin, was 2 pts in Category B)
  as a scored criterion in the same pass — user pointed out it's already
  a hard Stage 0 scan-level filter on every archetype, so scoring it again
  can never discriminate (100% of rows reaching this rubric already pass
  it). Category B max reduced 25→23 pts. Full record:
  `reports/rubric-changelog.csv` ids 7-8.
- **2026-07-07** (research pass, not applied here): designed 65 additional
  candidate criteria across 8 new categories (valuation, growth,
  balance-sheet health, ownership/sentiment, additional technical/
  momentum, catalyst/event, business-quality/moat, macro/sector) —
  `experiments/prompts/full-rubric-100.csv`, methodology in
  `experiments/DESIGN.md`. **None of these 65 are scored by this file** —
  this is the candidate pool `rubric-engine`'s Step 3 checks before
  drafting a new-criterion proposal, not a live change. The 33 criteria
  above remain the only ones actually applied to real candidates until a
  specific pool criterion clears the same evidence + approval gate as any
  other rubric change.
