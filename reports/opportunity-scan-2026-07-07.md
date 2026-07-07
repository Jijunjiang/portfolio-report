# Opportunity scan — 2026-07-07

Full run across all 4 archetypes: Stage 0 prefilter (saved scans) → partial
rubric scoring (Category A/B/D/E where data allows; Category C flagged as
a gap this run, see caveats) → every survivor logged to
`reports/opportunity-scanner-log.csv`. See
`.claude/skills/opportunity-scanner/SKILL.md` for archetype definitions
and exact scan filters, `RUBRICS.md` for the scoring lifecycle this
implements.

**251 candidates scored and logged this run** across 4 archetypes — every
one of them, sells and non-sells alike, not just the names below.

## Moonshot Turnaround — high risk, 5-10x (HOOD/INTC pattern)

32 raw scan matches, **only 3 survive the mandatory ≥40%-off-52-week-high
gate** — this archetype is quiet today.

| Ticker | Score | Read |
|---|---:|---|
| RGC | 27 | Regencell Bioscience, 91.7% off high — but a 10-employee, pre-revenue TCM biotech (PB ratio 2,579x). Speculative blowup, not a HOOD/INTC-style established-company turnaround. |
| AD | 19 | Array Digital (small wireless reseller), 55.8% off high. Thin story. |
| LUMN | 17 | Legacy telecom, 46.1% off high — decline reads structural, not cyclical (the rubric's own penalty case). |

**No real candidate today.** The other 29 gate-failures (CRWD, KLAC, HAL,
etc.) are short/medium-term dips on oscillator screens, not genuine
multi-year drawdowns — confirms the RSI+Williams%R prefilter alone can't
replace the 52-week-high check.

## Quality Inflection — medium risk, 2-5x ("buy NVDA/TSM early")

71 candidates scored (Category A skipped, this archetype has no drawdown
requirement).

| Ticker | Score | Read |
|---|---:|---|
| **NVDA** | 26 | PEG 0.31, ROE >100% — priced like value, growing like growth. The clearest fit for this archetype's actual thesis. |
| NXPI | 26 | PEG 0.31, ROE 26%, semis. |
| VRT | 26 | PEG 0.15, ROE 45%, data-center infrastructure — AI-buildout adjacent. |
| PEGA | 25 | Enterprise software, PEG 0.07. |
| MRX / ADEA | 25 | Financial services brokerage / IP licensing. |
| BYD / ANF / GEV / ATAT | 24 | Gaming, apparel retail, power infrastructure, hospitality (China). |

## Moonshot Growth — high risk, 10x+ (new archetype, not turnaround-based)

75 candidates scored, tied heavily at the top (14) — this is a **known
limitation**: this scan has no fundamental filters, so Category B
(margin/ROE) isn't computable for this archetype, compressing scores.
Judgment matters more here than the numeric tie suggests:

| Ticker | Score | Read |
|---|---:|---|
| **CORT** | 14 | Corcept Therapeutics — ADX 62 (strongest *confirmed* trend, not a spike), and unlike most names on this list, has an **approved, currently-commercial drug franchise** — real business momentum, not binary trial risk. |
| **PGNY** | 14 | Progyny — ADX 59, profitable fertility-benefits platform, same "real business, not lottery ticket" case as CORT. |
| TECH, VOYA, THG, LOAR, RLI, CDP, WSBC, HIW | 14 | Tied on partial score; mostly insurance/financials/REITs with strong short-term technicals — momentum-only case, no fundamental confirmation available. |
| APGE, XERS, RARE, SLDB, RGNX (not in top 10) | lower | Pre-revenue/early-commercial biotechs — the "growth" here is clinical-trial binary risk, not business momentum. Treat separately from CORT/PGNY. |

## Steady Value — low risk, ~30-50% (traditional blue-chip)

91 candidates scored.

| Ticker | Score | Read |
|---|---:|---|
| NOC, ERIC, FSLR | 17 | Defense, telecom equipment, solar — all P/E <18 with real profitability. |
| **NVO** | not in top 10 by raw score, but standout on quality/valuation mismatch | P/E 12.1 vs. ROE 71.4%, op margin 45.3% — GLP-1 category leader at a value multiple after its pullback. The strongest "cheap quality" mismatch in the whole list. |
| ADBE, ACN, NTES, INTU, INFY, ZM, FIS | 16 | Broad, liquid, profitable large-caps at single-digit-teens P/E. |

## Honest caveats — read before acting on any of this

- **Category C (momentum: MACD, EMA, Aroon, ADX, relative volume,
  RSI-recross) was not computed for any candidate this run** — it needs
  per-symbol historicals I didn't fetch (250+ more calls). Every logged
  row is missing up to 20 of 100 possible points for this reason alone.
- **Category B is incomplete for `turnaround` and `moonshot_growth`**
  specifically — `get_equity_fundamentals` doesn't return margin/ROE/ROA
  fields at all; those only came through for `compounder`/`steady_value`
  because *those scans'* own columns happened to include them.
- **No earnings-date check** (criteria 24/25) on any candidate — a name
  reporting in the next two weeks changes the risk materially and isn't
  reflected in any score here.
- **No concentration check** against current portfolio holdings was run
  for the two new archetypes (SPG appeared in the Steady Value scan and
  is already held — excluded from the table above but not formally
  screened out in the log).
- Scores across archetypes are **not comparable to each other** — each
  has a different available-points ceiling this run depending on data
  gaps above. A 17 in Steady Value and a 26 in Quality Inflection aren't
  on the same scale.

**Where I'd actually look next, in order:** NVDA (Quality Inflection) and
NVO (Steady Value) have the most complete data and clearest theses. CORT
and PGNY (Moonshot Growth) are the two names worth a closer look before
dismissing the rest of that archetype's list as noise. Turnaround has
nothing today.
