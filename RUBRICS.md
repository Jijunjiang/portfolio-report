# Rubric lifecycle: building and hill-climbing strategy rubrics

Two skills in this repo convert judgment calls into scored, checkable
criteria — `opportunity-scanner` (turnaround/compounder screening) and
`portfolio-report`'s option-selling suggestions. This doc is the shared
process both follow, so a new rubric doesn't have to reinvent it, and so
"is the strategy actually working" stays answerable from a log instead of
a feeling.

## Stage 1 — Generate the initial rubric

- Start from the informal heuristics already stated and used in a skill's
  playbooks — don't invent criteria from a blank page. The rubric is a
  formalization of judgment already exercised, not a new theory.
- Structure as weighted categories summing to a fixed scale (100 pts so
  far), each criterion tagged mechanical (computed directly from a tool
  call, no judgment) or judgment (needs reading/context). Roughly
  two-thirds mechanical is the working target — enough to run fast and
  often, with judgment criteria reserved for a deeper, occasional pass.
- **Validate before trusting operationally.** Check the rubric against
  real historical cases with known outcomes before using it live — e.g.
  the opportunity-scanner rubric was checked against HOOD/INTC/CVNA
  (recovered) vs. PTON (didn't), see `.claude/skills/opportunity-scanner/validation.md`.
  An unvalidated rubric is a hypothesis, not a tool — say so plainly until
  it's been checked against at least a few known-outcome cases.

### How to research a new or revised criterion

Don't invent a criterion's threshold or weight from intuition when
published research exists on the underlying idea — ground it, but source
honestly:

1. **Rank sources by rigor, not by how confidently they're written.**
   Peer-reviewed academic finance journals (Journal of Finance, Journal of
   Accounting Research, Review of Financial Studies) > practitioner
   research from parties with a data/track-record edge but a commercial
   angle (AQR, exchange-published white papers from CBOE/S&P) > books
   written for a retail audience (useful for the practical heuristic, but
   rarely peer-reviewed or out-of-sample tested) > blog posts (leads to
   primary sources only, never cite directly).
2. **Read for the mechanism, not just the headline result.** A factor
   that "worked" in a 1990s US large-cap sample may not transfer to a
   micro-cap turnaround or a single-name options overlay — check the
   sample the finding came from and how far it is from this account's
   actual use case (a handful of concentrated positions, not a
   diversified long/short factor portfolio) before adopting its threshold
   as-is.
3. **Actively look for the critical/opposing paper, not just the
   confirming one** — e.g. the covered-call literature has both "this
   captures a real, persistent premium" and "here's the uncompensated risk
   baked into the naive version" findings; both inform the rubric, not
   just the flattering one.
4. **Note the citation and what it justifies directly in the rubric file**
   (inline, near the criterion it grounds) so a future reviewer can see
   why a threshold is what it is, not just that it is.

### Literature backing today's rubrics

**Opportunity-scanner (deep-value turnaround / quality compounder), maps to
`rubric.md`:**

- Piotroski, J. (2000), *"Value Investing: The Use of Historical Financial
  Statement Information to Separate Winners from Losers,"* Journal of
  Accounting Research 38 — the F-Score paper; ~7.5%/yr excess return from
  screening cheap stocks on 9 binary financial-strength signals. Directly
  informs Category B (profitability/margin/ROE mechanical checks) — the
  same "cheap alone isn't enough, needs financial strength too" logic.
- Altman, E. (1968), *"Financial Ratios, Discriminant Analysis and the
  Prediction of Corporate Bankruptcy,"* Journal of Finance — the Z-Score;
  informs the instinct behind Category B/E's solvency-adjacent checks
  (avoiding value traps that are cheap because they're actually distressed,
  not because they're merely out of favor).
- Asness, Frazzini & Pedersen (2019), *"Quality Minus Junk,"* Review of
  Accounting Studies 24 — profitability + growth + safety command a
  higher risk-adjusted return with only a modest price premium. Directly
  informs Category D's growth-compounder criteria (PEG < 1.5 and ROE >
  15% together, not either alone).
- De Bondt & Thaler (1985), *"Does the Stock Market Overreact?,"* Journal
  of Finance 40 — prior 3-year losers subsequently outperform prior
  winners; overreaction is asymmetric and larger for losers. This is the
  empirical basis for treating a deep drawdown itself (Category A) as a
  potential signal rather than pure noise — but note the paper's own
  caveat that this is a multi-year, diversified-portfolio effect, not a
  guarantee for any single distressed name, which is exactly why Category
  A alone doesn't discriminate HOOD/INTC/CVNA from PTON in this account's
  own validation test.
- Greenblatt, J., *The Little Book That Beats the Market* (2006) — the
  "Magic Formula" (earnings yield + return on capital); informs the
  "cheap and good, not just cheap" framing across Categories A/B/D, and
  its own stated caveat (underperforms in ~1 of every 4 full years) is
  worth carrying into how confidence bands get framed here.

**Portfolio-report option-selling, maps to
`playbooks/option-suggestion-rubric.md`:**

- Whaley, R. (2002), *"Return and Risk of the CBOE Buy-Write Monthly
  Index,"* Journal of Derivatives — the original BXM (S&P 500 covered-call
  index) study; found a slightly higher annualized return than the index
  itself at roughly two-thirds the volatility. Baseline case for why
  covered-call writing is a defensible income strategy at all.
- Israelov & Nielsen (2015), *"Covered Calls Uncovered,"* Financial
  Analysts Journal 71(6) (AQR) — decomposes covered-call returns into
  equity exposure, a genuinely compensated short-volatility premium
  (Sharpe ≈1.0), and an *uncompensated* embedded equity-reversal bet. This
  is the load-bearing counterpoint behind Category A's "push deeper OTM
  than the standard 20–35 delta screen": pushing further out reduces the
  uncompensated reversal exposure the AQR paper flags, at the direct cost
  of collecting less of the volatility premium the Whaley paper documents
  — that trade-off is real, not free, and this rubric's "almost impossible
  to settle" bar is a deliberate (user-preference-driven) choice to sit
  further toward the safe/low-premium end of it than a naive yield-max
  approach would.
- Bondarenko, O. (2019), *"Historical Performance of Put-Writing
  Strategies,"* CBOE research — the PUT index study; cash-secured
  at-the-money put writing on the S&P 500 produced better Sharpe/Sortino
  than the index itself with materially lower drawdown, attributed to the
  volatility risk premium (average implied vol exceeding realized vol by
  ~4.2 pts, 1990–2018). Baseline case for why CSPs are a sound default
  strategy — informs Category B's assignment-probability banding (this
  account's puts are sold well OTM, not ATM like the benchmark index, so
  collect less premium than the benchmark in exchange for a wider margin
  of safety on Category A's effective-cost check).

**General methodology:**

- Tetlock & Gardner, *Superforecasting* (2015) — evidence-based,
  continuously-revised, probabilistic judgment outperforms
  intuition/expertise alone. The direct inspiration for this whole
  lifecycle's emphasis on logging every candidate (including skips),
  resolving outcomes, and only reweighting on accumulated evidence rather
  than conviction.

None of this literature was built for a concentrated, few-trades-per-
quarter retail account — it mostly comes from diversified, systematically
rebalanced factor portfolios or benchmark index studies. Treat every
number above as directional grounding for *why* a criterion exists, not as
a threshold to copy verbatim; the account's own logged outcomes (Stages 2–4
below) are what actually calibrate the thresholds for this portfolio.
- When a skill has both a fast recurring pass and an occasional deep pass,
  split the rubric into a mechanical subscore (used every run) and a full
  score (used on shortlisted candidates only) — mirrors the
  opportunity-scanner's category A+C mechanical subscore vs. full B/D/E
  workup.

## Stage 2 — Log every scored candidate, not just the interesting ones

- Every application of the rubric — whether it led to acting on the
  candidate or skipping it — gets a row in that rubric's CSV log, score
  included. Skips matter as much as picks: without logging them, there's
  no way to tell later whether the skip logic was actually right.
- The log is append-only. Never delete or rewrite historical rows, even
  after the rubric itself changes — a score under an old rubric version is
  still a valid data point about that version.

## Stage 3 — Resolve outcomes

- On a fixed cadence matched to how often this account actually decides
  things (quarterly — there isn't enough new resolved evidence week to
  week to justify reviewing more often), go back through rows old enough
  to have resolved and fill in what actually happened.
- Judge the outcome against the strategy's real goal, not a naive
  win/loss. A cash-secured put getting assigned isn't automatically bad
  (assignment at a genuine discount is the strategy working as intended);
  a covered call getting assigned right before the stock kept running is
  bad even though the option "worked" mechanically. See each rubric's own
  refinement doc for the specific verdict criteria.

## Stage 4 — Hill-climb: add, reweight, or retire criteria based on evidence

- **Add** a criterion when the resolved log shows a pattern that shows up
  repeatedly across outcomes but nothing current captures.
- **Reweight** up if a criterion discriminates well (present in good
  outcomes, absent in bad ones); down or to zero if it doesn't
  discriminate at all (fires roughly equally on both). Cite the specific
  logged rows driving the change — never reweight from a vague impression.
- **Retire** a criterion once enough data shows it's actively
  counter-predictive or fully redundant with another one.
- **Never touch weights on fewer than ~5 resolved cases** for the
  category being adjusted. This is hill-climbing at the account's real
  decision cadence, not continuous optimization — small-sample changes
  risk fitting noise. Say so explicitly if ever tempted to act on 2–3 data
  points.
- Record every change in that rubric file's own `## Changelog` section:
  date, what changed, why, and which rows justified it — so a future
  review can audit whether the change actually panned out too.

## Stage 5 — Repeat

Back to Stage 2 with the updated rubric. Old rows keep their original
scores; don't retroactively rescore history under a new rubric version —
that would corrupt the very evidence used to justify changing it.

## Today's instances

| Rubric | Skill | Log | Refinement doc |
|---|---|---|---|
| `.claude/skills/opportunity-scanner/rubric.md` | opportunity-scanner | `reports/opportunity-scanner-log.csv` | `.claude/skills/opportunity-scanner/refinement.md` |
| `.claude/skills/portfolio-report/playbooks/option-suggestion-rubric.md` | portfolio-report | `reports/option-suggestion-log.csv` | `.claude/skills/portfolio-report/playbooks/option-suggestion-refinement.md` |

When a new strategy needs a rubric, follow the five stages above and add a
row to this table.
