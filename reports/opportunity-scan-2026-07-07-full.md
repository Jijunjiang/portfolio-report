# Opportunity scan — 2026-07-07 (full gated run)

First run under the corrected rubric: domain-leadership and net-profit-margin
are now hard gates (see `.claude/skills/opportunity-scanner/rubric.md`'s
"Gates" section), not scored points, and logging moved to one CSV per run
(`reports/opportunity-scanner-logs/2026-07-07-full-<archetype>.csv`, merged
into `2026-07-07-full.csv` for this report). 235 Stage-0 survivors across 4
archetypes; 171 fully scored, 64 disqualified/gate-failed before scoring.

**This narrows a universe, it does not predict a return.** Multi-bagger
identification is inherently uncertain — treat everything below as a
research shortlist, not a signal to act on directly.

## Turnaround (high risk, 5-10x pattern) — 0 candidates survived

20 Stage-0 matches (oversold + established + profitable). Only **AD**
(Array Digital Infrastructure) cleared the mandatory 40%-off-high drawdown
gate (55.7% off high) — every other match was within 17-38% of its 52-week
high, which per `validation.md`'s CRWD false-positive is exactly the "looks
oversold but isn't actually a HOOD/INTC-depth setup" pattern this gate
exists to catch. AD then failed the domain-leadership gate: a ~$3B regional
prepaid/postpaid wireless reseller competing against AT&T/Verizon/T-Mobile's
hundreds-of-billions scale, no discernible moat, recently shrinking via
divestiture.

**This is a legitimate empty result, not an error** — a stock that's both
severely oversold *and* genuinely 40%+ off its high *and* a real market
leader is rare by construction, and today none existed. 9 borderline
cases (25-40% off high: TU, CRGY, LYB, KLAC, LBRT, NE, TDS, T, HAS) are
logged as minimal rows for future reference, not discarded silently.

## Moonshot growth (high risk, 10x+ pattern) — 35 of 61 scored

26 disqualified at the leadership gate (thin/commoditized: SEZL vs.
Affirm/Klarna, DAVE in a crowded consumer-fintech space, several regional
banks/title insurers below national scale, undifferentiated lead-gen
aggregators). Top 5:

| Ticker | Score | Thesis |
|---|---|---|
| **MGNI** (Magnite) | 28 | Largest independent ad-exchange, cheap PEG+ROE combo, secular ad-tech tailwind |
| **FSS** (Federal Signal) | 27 | Dominant niche leader in municipal safety equipment, infrastructure tailwind |
| **GOLF** (Titleist) | 26 | Dominant global golf-equipment brand |
| **FTDR** (American Home Shield) | 26 | Dominant home-warranty leader, ROE 120%+ |
| **ACAD** (ACADIA Pharma) | 26 | First-in-class CNS drugs, cheap PEG+ROE |

## Compounder / quality inflection (medium risk, 2-5x pattern) — 42 of 70 scored

28 disqualified (single-drug biotechs with no durable franchise, sub-scale
BNPL/fintech vs. established leaders, diversified industrials with no real
moat). Top 5:

| Ticker | Score | Thesis |
|---|---|---|
| **DUOL** (Duolingo) | 27 | Dominant #1 in language-learning, AI-driven product tailwind |
| **CRDO** (Credo Technology) | 27 | AI-datacenter interconnect niche leader, secular buildout tailwind |
| **TMDX** (TransMedics) | 26 | Near-monopoly in organ-transplant preservation technology |
| **VRT** (Vertiv) | 26 | Top-tier data-center power/cooling infrastructure, AI buildout tailwind |
| **MELI** (MercadoLibre) | 26 | Dominant Latin American e-commerce/fintech platform |

**Flag:** BLKB's ROE read as 419% — a leverage/buyback accounting artifact,
not pure operating quality (per `SKILL.md` step 4's own warning). VIK
(312%), ENR (127%), GDDY (398%) are similar cases; scored cautiously, worth
a manual check before treating those specific ROE numbers at face value.

## Steady value (low risk, ~30-50% pattern) — 94 of 94 scored

**Zero disqualified at the leadership gate** — a $10B+/high-quality-
fundamentals prefilter turned out to already select for genuine leaders (34
dominant #1/#2 names, 60 solid niche leaders), so the gate did no filtering
work in this archetype today. Top names (many tied at 27 — see caveat
below): **NVO** (Novo Nordisk), **NOC** (Northrop Grumman), **MPLX**,
**OKE**, **AER** (AerCap), **WES**, **KSPI**, **GIB**, **GEN**.

**Caveat on the ties:** 8 of the top-10 steady_value names share an
identical category breakdown (12/3/6/6 across B/C/D/E). That's plausible
for a tightly-filtered set of similar blue-chip quality names, but it also
suggests the judgment criteria (`[J]` tags) may have been scored somewhat
uniformly across this batch rather than fully differentiated per company —
treat the *ranking* within this tied group as low-confidence; the fact that
all 8 cleared the bar is the real signal, not their exact order.

Two names already held in the account (UBER, SPG) correctly scored `0` on
the concentration criterion rather than a fresh `2`.

## What's still genuinely missing (honest gaps, not fabricated)

- **Category C (momentum)** — MACD, price-vs-EMA (except steady_value,
  which got this one), relative volume, RSI-recross — needs a
  `get_equity_historicals`-based calculation that wasn't run for most of
  today's 171 scored candidates. `c20_aroon` was scored mechanically for
  moonshot_growth since it's implied by that scan's own filter.
- **Category D's earnings-specific criteria** (`d24_epsbeat`,
  `d25_noearnings2wk`) — would need per-ticker `get_earnings_results`/
  `get_earnings_calendar` calls (up to ~171), not run at this scale today.
- **Category E's concentration/liquidity checks** — only checked where a
  fork had time; not universal across all 171.
- **Gross margin** — not probed for compounder or steady_value this run
  (real gap, not a fetch failure where noted).

None of these are silently defaulted — every uncomputed cell in the
underlying log is `N/A`, never a fabricated score.

## Files

- Per-archetype run files: `reports/opportunity-scanner-logs/2026-07-07-full-{turnaround,moonshot_growth,compounder,steady_value}.csv`
- Merged view: `reports/opportunity-scanner-logs/2026-07-07-full.csv` (235 rows, 46 columns)
- Legacy pre-gate snapshot (partial, superseded by this run): `reports/opportunity-scanner-logs/2026-07-07-run1-partial.csv`
