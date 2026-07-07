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
