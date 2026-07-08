"""
Known-outcome test cases for the backtest — see README.md for the honest
framing (existence-proof / sanity-check, not a statistically meaningful
sample; don't over-claim from 4-6 cases).

`trough_window` is an approximate (start, end) date range to scan for the
Stage-0 screen firing — wide enough to catch the actual low without
requiring it be known to the day beforehand (which would be lookahead
bias in choosing the window itself, even though the indicator math inside
it is point-in-time correct).
"""

CASES = [
    {
        "ticker": "HOOD",
        "outcome": "recovered",
        "high": {"price": 85.00, "date": "2021-08-01"},
        "low": {"price": 6.81, "date": "2022-06-13"},
        "trough_window": ("2022-04-01", "2022-08-31"),
        "note": "92% drawdown, 11x off the low as of 2026-07 (validation.md)",
    },
    {
        "ticker": "INTC",
        "outcome": "recovered",
        "high": {"price": 68.00, "date": "2020-01-01"},
        "low": {"price": 18.89, "date": "2024-09-01"},
        "trough_window": ("2024-07-01", "2024-11-30"),
        "note": "72% drawdown, 5.7x off the low as of 2026-07 (validation.md)",
    },
    {
        "ticker": "CVNA",
        "outcome": "recovered",
        "high": {"price": 85.00, "date": "2021-08-01"},
        "low": {"price": 0.71, "date": "2022-12-01"},
        "trough_window": ("2022-10-01", "2023-02-28"),
        "note": "99.2% drawdown, 96.6x off the low as of 2026-07 (validation.md, most extreme case)",
    },
    {
        "ticker": "PTON",
        "outcome": "did_not_recover",
        "high": {"price": 171.00, "date": "2021-01-01"},
        "low": {"price": 2.70, "date": "2024-04-01"},
        "trough_window": ("2024-02-01", "2024-06-30"),
        "note": "98.4% drawdown, only 2.1x off the low as of 2026-07, still 96.6% below high — a technical false-positive test case",
    },
]
