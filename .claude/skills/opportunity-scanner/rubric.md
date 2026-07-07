# Opportunity scoring rubric

A composite score built from 33 individual criteria across 5 categories
(32 original + criterion 33, added 2026-07-07 — see below). Each criterion
is tagged **[M]** mechanical (computed directly from a tool) or **[J]**
judgment (requires reading/context, not a pure number) — roughly
two-thirds mechanical, one-third judgment. Don't present a [J] criterion's
score as more precise than it is.

**Before scoring a criterion, check `reports/rubric-data-sources.csv`** —
the verified fetch method for each of the 32 criteria, including which
scanner filters are confirmed working, which are server-side broken
(Stochastic, Bollinger, Support — don't retry these), which are unreliable
(Relative Volume returns a constant 1.0 in some scan combinations), and
which have no direct fetch at all (`b17_leverage_judgment`,
`e32_fitstyle_judgment` are judgment-only by design; `c23_rsirecross`
needs a manual historicals-based calc that isn't implemented yet). Don't
re-derive this from scratch each run — it was researched and tested live
against the API on 2026-07-07.

**Guide score, not a verdict:** ≥70 = strong candidate worth deep research.
50–69 = watchlist, revisit next quarter. <50 = discard for now. These
bands are a starting point, not calibrated against a large sample —
HOOD's setup would have scored high on category A alone; treat the bands
as directional.

Run this on candidates that already passed the two saved scans — see
SKILL.md step 1, which is Stage 0 of this rubric (a hard-cutoff prefilter,
tuned to ~100 combined daily matches so every survivor can get the full
score below, not just a subset). This 100-point rubric is Stage 1 of the
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

## Category B — Financial quality / not a value trap (25 pts)

9. **[M]** Market cap > $2B → 3 (established company, matches both HOOD and INTC's scale at entry).
10. **[M]** Gross margin > 30% → 2, else 0.
11. **[M]** Operating margin > 0% → 2, else 0 (don't require high — turnarounds are often thin here).
12. **[M]** Net profit margin > 0% → 2; negative but improving vs. prior period → 1; negative and worsening → 0.
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

## Criterion 33 — Domain leadership (added 2026-07-07)

User-directed addition: "I hate risk — judge whether this is a company I
could buy and hold for 10 years, top-tier in its domain." Logically part
of Category B (financial quality / not a value trap) but numbered 33
rather than inserted as B's own #10 — inserting mid-sequence would have
renumbered every criterion after it and broken the column mapping in the
251 rows already logged before this date. Applies to **all archetypes**,
not just turnaround — a risk-averse durability filter belongs everywhere
this account puts money, not only in the distressed-value screen.

33. **[J]** Company is a top-tier / dominant leader in its specific market
    domain — clear #1 or #2 position, with a durable moat (scale, brand,
    network effects, switching costs, regulatory barrier, or a
    technological lead a competitor can't quickly close) that would make
    it reasonable to hold through a full 10-year cycle regardless of
    near-term volatility → **5**. Solid leader in a narrower niche, or a
    clear #3–4 in a larger domain, real but not airtight moat → **2**.
    Sub-scale, commoditized, easily disrupted, or not a business worth
    holding through a decade → **0**.

    This is a judgment call about the *business*, not the *stock price* —
    don't conflate it with Category A's drawdown-depth criteria (a cheap,
    deeply-oversold stock can still fail this if it's a weak player in its
    domain) or Category D's tailwind criterion (a strong sector tailwind
    can lift a mediocre #4 player too, which is exactly the distinction
    this criterion is for). Ground the call in the company description,
    market cap relative to known competitors, and — when genuinely
    uncertain — a `WebSearch` for the company's actual competitive
    position, rather than guessing from the sector label alone.

## Presenting a scored candidate

Show the category subtotals (A–E out of their max), not just the final
number — a candidate scoring 60 from strong value + weak momentum reads
differently than 60 from strong momentum + no real discount, and the user
should see which. List which specific criteria drove the score down, not
just the criteria that drove it up — the discarded points are often the
most decision-relevant part.

## Changelog

Every reweight/add/retire gets one line here: date, what changed, why, and
which logged rows in `reports/opportunity-scanner-log.csv` justified it.
See `../../../RUBRICS.md` for the full lifecycle this follows.

- **2026-07-07**: Added criterion 33 (domain leadership / 10-year-hold
  quality), 5 pts, applies to all archetypes. User-directed, not
  evidence-driven (no resolved rows exist yet to justify it either way —
  this is a Stage 1 addition from stated risk preference, not a Stage
  4 hill-climb). Numbered 33 rather than inserted into Category B's
  sequence to avoid breaking the column mapping already logged for 251
  prior rows.
