#!/usr/bin/env python3
"""
Test the rubric's JUDGMENT criteria (a8_cyclical_judgment,
b33_domainleadership_judgment) against the same known-outcome cases as
backtest.py — the gap that script explicitly can't cover (see its
docstring and README.md). Calls the real Claude API so the judgment is
an actual model call, not this script's own logic — same "data vs.
judgment" split as compute_rubric.py / a real rubric-scoring session.

HONEST LIMITATION, read before trusting any result from this script:
HOOD/INTC/CVNA/PTON are all well-known, heavily-written-about situations.
Any model (including the one asked here) likely has training-data
knowledge of how each story actually ended, which is a real hindsight-
contamination risk this script cannot fully eliminate just by phrasing
the prompt carefully. Treat results as a plausibility check on whether an
LLM *can produce the right kind of reasoning* for this judgment call, not
as proof the judgment layer would have worked blind, in real time, in
2022/2024. The rubric's actual validation for the judgment layer is the
live pipeline (today's real candidates, scored now, outcomes checked
quarterly by rubric-engine) — this experiment is a supplement to that,
not a replacement.

Usage:
    export ANTHROPIC_API_KEY=sk-...
    python3 judgment_experiment.py --all
    python3 judgment_experiment.py HOOD

Requires: pip install requests (or run with a Python that already has it)
"""

import json
import os
import sys
import requests

API_URL = "https://api.anthropic.com/v1/messages"
MODEL = "claude-sonnet-5"

# Point-in-time facts only — deliberately excludes anything about what
# happened AFTER the date given (that's the whole test). Written from
# what was publicly known/reported at the time, not with the benefit of
# hindsight about the eventual outcome.
CASE_FACTS = {
    "HOOD": {
        "as_of": "2022-06-16",
        "outcome": "recovered",
        "company_label": "Robinhood Markets (HOOD)",
        "brief": (
            "Robinhood Markets (HOOD), retail brokerage app, IPO'd July 2021 near $38, "
            "now down ~92% from its August 2021 high of $85 to about $7. Trading volumes "
            "and new-account growth have collapsed sharply as 2021's meme-stock and crypto "
            "retail-trading boom normalized. Crypto trading revenue (a growing part of the "
            "business) is hit hard by the 2022 crypto market decline. Facing regulatory "
            "scrutiny over its payment-for-order-flow revenue model. Still holds significant "
            "cash reserves from its IPO. Expanding into new products (retirement accounts, "
            "a credit card). Sector: financial technology / online brokerage."
        ),
    },
    "INTC": {
        "as_of": "2024-08-07",
        "outcome": "recovered",
        "company_label": "Intel Corp (INTC)",
        "brief": (
            "Intel Corp (INTC), longtime dominant x86 CPU maker, down ~72% from its "
            "2020-era high near $68 to about $19. Losing market share to AMD in consumer "
            "and server CPUs, and falling behind TSMC/Samsung on advanced chip "
            "manufacturing process nodes. Announced major layoffs and suspended its "
            "dividend in 2024. Pursuing an expensive multi-year 'IDM 2.0' strategy to "
            "regain manufacturing leadership and become a contract chip foundry. Missing "
            "earnings estimates. Losing ground in the AI-chip boom to Nvidia. Receiving "
            "large US CHIPS Act subsidies to build domestic fabs. Sector: semiconductors, "
            "integrated device manufacturer."
        ),
    },
    "CVNA": {
        "as_of": "2022-12-07",
        "outcome": "recovered",
        "company_label": "Carvana (CVNA)",
        "brief": (
            "Carvana (CVNA), online used-car retailer known for its 'car vending "
            "machines,' down ~99% from its 2021 high near $85 to under $1. Heavily "
            "leveraged balance sheet from aggressive growth, including a large 2022 "
            "debt-funded acquisition of ADESA's US physical auto-auction business. "
            "Rising interest rates crushing used-car demand and financing economics. "
            "Some analysts raising going-concern doubts; company bonds trading at "
            "distressed-debt levels. Management pursuing cost cuts and consolidating "
            "physical locations. Sector: online used-vehicle retail / e-commerce."
        ),
    },
    "PTON": {
        "as_of": "2024-04-24",
        "outcome": "did_not_recover",
        "company_label": "Peloton Interactive (PTON)",
        "brief": (
            "Peloton Interactive (PTON), connected fitness hardware (bikes/treadmills) "
            "plus subscription app, down ~98% from its January 2021 high of $171 to "
            "about $3. Pandemic-era at-home fitness demand has collapsed as gyms and "
            "in-person life reopened. Prior equipment recalls (treadmill safety issues) "
            "damaged the brand. Multiple rounds of layoffs and several CEO changes since "
            "2022. Subscriber growth stalled. High debt load. Management repeatedly "
            "cutting costs and reportedly exploring strategic alternatives including a "
            "possible sale of the company. Facing competition from cheaper connected-"
            "fitness alternatives and free fitness content. Sector: connected fitness "
            "hardware and subscription."
        ),
    },
}

def build_system_prompt(company_label, as_of):
    """Embeds the as-of date directly into each criterion's question text
    (not just the surrounding framing) — per direct feedback that the
    question itself needs to be date-anchored ("at 2025-10-10, is HOOD a
    leadership stock in brokerage") rather than relying on a generic
    "answer as of X" instruction alone. This does not fully eliminate
    hindsight-contamination risk for famous cases (see README.md/
    DESIGN.md's honest limitation on that) but it's the strongest
    practical mitigation available: an explicit, repeated, date-anchored
    framing plus an instruction to consciously discard anything the model
    knows about what happened after that date."""
    return f"""You are scoring one criterion of a stock-picking rubric for a personal, \
low-frequency, high-conviction investment account.

STRICT TIME BOUNDARY: today, for the purpose of this task, is {as_of}. You are simulating \
the judgment call as it would have been made on that exact date, using only information \
that was knowable then. You may recognize this company and may know things that happened \
to it AFTER {as_of} — if so, you must deliberately set that knowledge aside and answer as \
if {as_of} were the present moment with an unknown future. Do not let post-{as_of} outcomes \
(recovery, continued decline, acquisition, bankruptcy, anything) leak into either score or \
its reasoning. If your reasoning references anything dated after {as_of}, that's a failure \
of this task.

Score two criteria, exactly matching this rubric. Both questions are phrased with the date \
built in — answer them as asked, not as of today's real date:

a8_cyclical_judgment: As of {as_of}, does {company_label}'s drawdown look cyclical/ \
sentiment-driven (a temporary, external, or fixable problem — a demand cycle, a regulatory \
overhang, a leverage problem fixable by refinancing/cost cuts, a manufacturing execution \
problem in an otherwise-viable business) rather than a structural business breakdown \
(permanent demand destruction, the core product/service becoming obsolete, an unfixable \
competitive position)? Score 4 (clearly cyclical/fixable), 2 (unclear/mixed), or 0 (looks \
structural) — based only on what was true and knowable as of {as_of}.

b33_domainleadership_judgment: As of {as_of}, is {company_label} a top-tier/dominant leader \
in its specific market domain (clear #1 or #2, durable moat) or at least a solid niche \
leader (#3-4, real but not airtight moat) — durable enough to be worth holding through a \
full 10-year cycle regardless of near-term volatility? Or is it sub-scale/commoditized/ \
easily disrupted? Score 5 (dominant leader), 2 (solid niche leader), or 0 (sub-scale/ \
commoditized/disrupted) — based on {company_label}'s actual market position as of {as_of}, \
not on anything that happened to its competitive standing afterward.

Respond with ONLY a JSON object, no other text: \
{{"a8_cyclical_judgment": {{"score": 0|2|4, "reasoning": "..."}}, \
"b33_domainleadership_judgment": {{"score": 0|2|5, "reasoning": "..."}}}}"""


def call_claude(api_key, company_label, brief, as_of):
    system_prompt = build_system_prompt(company_label, as_of)
    payload = {
        "model": MODEL,
        "max_tokens": 600,
        "system": system_prompt,
        "messages": [{
            "role": "user",
            "content": (
                f"It is {as_of}. Here is {company_label}'s situation as of today "
                f"({as_of}) — nothing below or in your own knowledge from after this "
                f"date should factor into your answer:\n\n{brief}"
            ),
        }],
    }
    resp = requests.post(
        API_URL,
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json=payload,
        timeout=60,
    )
    resp.raise_for_status()
    text = resp.json()["content"][0]["text"]
    return json.loads(text)


def run_case(ticker, api_key):
    case = CASE_FACTS[ticker]
    judgment = call_claude(api_key, case["company_label"], case["brief"], case["as_of"])
    result = {
        "ticker": ticker,
        "as_of": case["as_of"],
        "actual_outcome": case["outcome"],
        "judgment": judgment,
    }
    return result


def main():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Set ANTHROPIC_API_KEY first — see this script's docstring.", file=sys.stderr)
        sys.exit(1)

    args = sys.argv[1:]
    tickers = list(CASE_FACTS.keys()) if (args and args[0] == "--all") else args
    if not tickers:
        print(__doc__)
        sys.exit(1)

    results_dir = os.path.join(os.path.dirname(__file__), "results")
    os.makedirs(results_dir, exist_ok=True)
    all_results = []
    for ticker in tickers:
        if ticker not in CASE_FACTS:
            print(f"No case facts for {ticker}", file=sys.stderr)
            continue
        result = run_case(ticker, api_key)
        all_results.append(result)
        a8 = result["judgment"]["a8_cyclical_judgment"]["score"]
        b33 = result["judgment"]["b33_domainleadership_judgment"]["score"]
        print(f"{ticker}: a8={a8} b33={b33} actual={result['actual_outcome']}", file=sys.stderr)

    out_path = os.path.join(results_dir, "judgment-experiment.json")
    with open(out_path, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"\nWrote {out_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
