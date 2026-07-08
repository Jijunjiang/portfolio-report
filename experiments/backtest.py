#!/usr/bin/env python3
"""
Backtest the opportunity-scanner's turnaround Stage-0 technical screen
against known-outcome historical cases (see cases.py, README.md for
methodology and honest limitations — this tests the technical criteria
only, not fundamentals or judgment).

Usage:
    python3 backtest.py data/HOOD.json          # one ticker, prints JSON
    python3 backtest.py --all                    # every case in cases.py
                                                   # with data/<ticker>.json
                                                   # present, writes
                                                   # results/<ticker>-
                                                   # backtest.json + prints
                                                   # results/summary.md

Input data file schema (see README.md "Fetching data"):
    {"ticker": "HOOD", "bars": [{"begins_at": "...", "open": ..., "high":
    ..., "low": ..., "close": ..., "volume": ...}, ...]}   // oldest first

No lookahead bias: at each candidate date, only bars with begins_at <=
that date are used to compute indicators. Forward returns look ahead
deliberately (that's the whole point — did the screen firing predict
anything) but are clearly labeled as such, never fed back into the
screening decision itself.
"""

import json
import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..",
                                 ".claude", "skills", "opportunity-scanner", "scripts"))
from compute_rubric import rsi_series, williams_percent_range  # noqa: E402

sys.path.insert(0, os.path.dirname(__file__))
from cases import CASES  # noqa: E402


def _parse_date(s):
    return datetime.fromisoformat(s[:10])


def load_bars(path):
    with open(path) as f:
        data = json.load(f)
    bars = data["bars"]
    for b in bars:
        b["_date"] = _parse_date(b["begins_at"])
    bars.sort(key=lambda b: b["_date"])
    return data["ticker"], bars


def forward_return(bars, from_idx, days_ahead):
    """Nearest bar at/after from_idx's date + days_ahead calendar days."""
    target = bars[from_idx]["_date"] + timedelta(days=days_ahead)
    for i in range(from_idx, len(bars)):
        if bars[i]["_date"] >= target:
            start_price = bars[from_idx]["close"]
            end_price = bars[i]["close"]
            return round((end_price / start_price - 1) * 100, 1)
    return None  # not enough forward data


def scan_window(ticker, bars, window_start, window_end):
    """For every trading day in [window_start, window_end], compute RSI(14)
    and Williams %R(14) using only bars up to that day, and check whether
    the live turnaround screen's actual thresholds (RSI<30 AND
    Williams%R<-80) would have fired. Returns the list of firing dates
    with forward returns."""
    ws, we = _parse_date(window_start), _parse_date(window_end)
    hits = []
    for i, bar in enumerate(bars):
        if not (ws <= bar["_date"] <= we):
            continue
        history = bars[: i + 1]  # point-in-time: nothing after today
        closes = [b["close"] for b in history]
        rsi_vals = rsi_series(closes)
        rsi = rsi_vals[-1] if rsi_vals and rsi_vals[-1] is not None else None
        williams = williams_percent_range(history, 14)
        if rsi is None or williams is None:
            continue
        fired = rsi < 30 and williams < -80
        if fired:
            hits.append({
                "date": bar["begins_at"][:10],
                "close": bar["close"],
                "rsi_14": round(rsi, 2),
                "williams_pct_range_14": round(williams, 2),
                "forward_return_3mo_pct": forward_return(bars, i, 91),
                "forward_return_6mo_pct": forward_return(bars, i, 182),
                "forward_return_1yr_pct": forward_return(bars, i, 365),
                "forward_return_2yr_pct": forward_return(bars, i, 730),
            })
    return hits


def run_case(ticker, bars, case):
    hits = scan_window(ticker, bars, *case["trough_window"])
    first_close = bars[0]["close"]
    last_close = bars[-1]["close"]
    return {
        "ticker": ticker,
        "outcome_label": case["outcome"],
        "note": case["note"],
        "trough_window": list(case["trough_window"]),
        "screen_fired_on_n_days": len(hits),
        "hits": hits,
        "data_range": [bars[0]["begins_at"][:10], bars[-1]["begins_at"][:10]],
    }


def main():
    args = sys.argv[1:]
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    results_dir = os.path.join(os.path.dirname(__file__), "results")
    os.makedirs(results_dir, exist_ok=True)

    if args and args[0] == "--all":
        summary_lines = ["# Backtest summary\n"]
        for case in CASES:
            path = os.path.join(data_dir, f"{case['ticker']}.json")
            if not os.path.exists(path):
                print(f"SKIP {case['ticker']}: no data file at {path}", file=sys.stderr)
                continue
            ticker, bars = load_bars(path)
            result = run_case(ticker, bars, case)
            out_path = os.path.join(results_dir, f"{ticker}-backtest.json")
            with open(out_path, "w") as f:
                json.dump(result, f, indent=2, default=str)
            print(f"{ticker}: screen fired on {result['screen_fired_on_n_days']} day(s) "
                  f"in {case['trough_window']} ({case['outcome']})", file=sys.stderr)
            summary_lines.append(f"## {ticker} ({case['outcome']})\n")
            summary_lines.append(f"{case['note']}\n")
            summary_lines.append(f"Screen fired on **{result['screen_fired_on_n_days']}** day(s) in the trough window.\n")
            if result["hits"]:
                summary_lines.append("| Date | Close | RSI(14) | Williams%R(14) | +3mo | +6mo | +1yr | +2yr |")
                summary_lines.append("|---|---:|---:|---:|---:|---:|---:|---:|")
                for h in result["hits"]:
                    summary_lines.append(
                        f"| {h['date']} | ${h['close']:.2f} | {h['rsi_14']} | "
                        f"{h['williams_pct_range_14']} | "
                        f"{h['forward_return_3mo_pct']}% | {h['forward_return_6mo_pct']}% | "
                        f"{h['forward_return_1yr_pct']}% | {h['forward_return_2yr_pct']}% |"
                    )
            summary_lines.append("")
        summary_path = os.path.join(results_dir, "summary.md")
        with open(summary_path, "w") as f:
            f.write("\n".join(summary_lines))
        print(f"\nWrote {summary_path}", file=sys.stderr)
        return

    if not args:
        print(__doc__)
        sys.exit(1)

    ticker, bars = load_bars(args[0])
    case = next((c for c in CASES if c["ticker"] == ticker), None)
    if case is None:
        print(f"No case registered for {ticker} in cases.py", file=sys.stderr)
        sys.exit(1)
    result = run_case(ticker, bars, case)
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
