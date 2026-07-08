#!/usr/bin/env python3
"""
Collect the raw data every opportunity-scanner rubric criterion needs, from
already-fetched raw data — one JSON key per criterion.

This script does NOT call any Robinhood/MCP tool itself — it has no API
credentials and shouldn't. The calling Claude Code session fetches the raw
data (get_equity_historicals, get_equity_fundamentals, a scan's own result
columns, get_earnings_results, get_equity_positions) and passes it in as
JSON; this script maps that raw data onto each of the 33 rubric criteria's
actual named data requirements — a **data-collection** pass, not a scoring
pass. Scoring (applying rubric.md's point thresholds to this data) is a
separate, later step.

Exists because of a concrete failure mode (2026-07-07): several criteria
were marked "computable from historicals" in reports/rubric-data-sources.csv
based on confirming the raw data existed for one ticker, but the actual
calculation code was never written — so those cells sat N/A for every
candidate, every run. This script makes the calculation real, testable,
and reusable instead of re-derived ad hoc each time.

Usage:
    python3 compute_rubric.py input.json                  # data-collection
                                                            # mode (default):
                                                            # JSON to stdout
    python3 compute_rubric.py --pass-fail input.json       # pass/fail mode:
                                                            # PASS/FAIL/N/A
                                                            # per criterion
                                                            # instead of raw
                                                            # data fields
    python3 compute_rubric.py input.json out.json          # write to a file
                                                            # instead of stdout
    python3 compute_rubric.py --self-test                  # sanity-checks
                                                            # both modes on
                                                            # synthetic data,
                                                            # no real API
                                                            # data needed

Input JSON schema (all top-level keys optional — only what's present gets
collected; everything else is honestly "N/A"):
{
  "ticker": "NVDA",
  "archetype": "turnaround" | "moonshot_growth" | "compounder" | "steady_value",
  "current_price": 196.43,
  "scan_columns": {
    "RSI": 22.4, "Williams Percent Range (14)": -93.3, "PEG": 0.42,
    "Gross margin": 0.61, "Operating margin": 0.42, "Net profit margin": 0.36,
    "Return on equity": 0.95, "Return on assets": 0.29,
    "Aroon Oscillator (14)": 92, "Average directional index (14)": 34.5,
    "EMA": 190.1, "Market cap": 3.05e11, "Historical volatility (30, 1D)": 0.35,
    "Relative volume": 0.55
  },
  "fundamentals": {
    "high_52_weeks": 250.0, "low_52_weeks": 80.0, "market_cap": 3.05e11,
    "dividend_yield": null, "average_volume": 5.6e7, "float": 2.4e10,
    "sector": "Technology", "description": "..."
  },
  "historicals": [
    {"begins_at": "2026-06-01", "open": 190.0, "high": 195.0, "low": 188.0,
     "close": 193.0, "volume": 4.5e7},
    ...  // oldest first, at least 60 daily bars recommended
  ],
  "earnings": [
    {"quarter_end": "2026-04-30", "eps_estimate": 1.20, "eps_actual": 1.35},
    ...  // oldest first, most recent last
  ],
  "next_earnings_date": "2026-07-20",
  "today": "2026-07-07",
  "held_tickers": ["UBER", "SPG"]
}

Output JSON schema: one entry per criterion id — the key IS the criterion,
the value is either the dict of named raw-data fields it needs (each
individually "N/A" if unavailable), or the literal string "N/A" for a
criterion with no external data requirement at all, e.g.:
  "a1_pctoffhigh": {"high_52_weeks": 236.54, "current_price": 196.93}
  "a4_stochastic": {"stochastic_k_14": 52.83}
  "b12_netmargin": "N/A"          // retired criterion, no data needed
  "e32_fitstyle_judgment": "N/A"  // pure synthesis judgment, no data needed
Applying rubric.md's point thresholds to this data is a separate step, not
this script's job — see rubric.md for the exact scoring rule per criterion.
"""

import json
import sys
from datetime import datetime, timedelta


# ---------------------------------------------------------------------------
# Technical indicator primitives (stdlib only, no numpy/pandas dependency)
# ---------------------------------------------------------------------------

def _closes(bars):
    return [b["close"] for b in bars]


def sma(values, period):
    if len(values) < period:
        return None
    return sum(values[-period:]) / period


def stdev(values, period):
    if len(values) < period:
        return None
    window = values[-period:]
    mean = sum(window) / period
    variance = sum((x - mean) ** 2 for x in window) / period
    return variance ** 0.5


def ema_series(values, period):
    """Full EMA series (same length as values, first `period-1` entries are None)."""
    if len(values) < period:
        return [None] * len(values)
    k = 2 / (period + 1)
    out = [None] * (period - 1)
    seed = sum(values[:period]) / period
    out.append(seed)
    prev = seed
    for v in values[period:]:
        cur = v * k + prev * (1 - k)
        out.append(cur)
        prev = cur
    return out


def rsi_series(closes, period=14):
    """Wilder's RSI, full series (same length as closes, leading Nones)."""
    if len(closes) < period + 1:
        return [None] * len(closes)
    deltas = [closes[i] - closes[i - 1] for i in range(1, len(closes))]
    gains = [max(d, 0) for d in deltas]
    losses = [max(-d, 0) for d in deltas]

    out = [None] * period  # aligns with closes: out[i] is RSI as of closes[i]
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period
    rs = avg_gain / avg_loss if avg_loss != 0 else float("inf")
    out.append(100 - (100 / (1 + rs)) if avg_loss != 0 else 100.0)

    for i in range(period, len(deltas)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period
        rs = avg_gain / avg_loss if avg_loss != 0 else float("inf")
        out.append(100 - (100 / (1 + rs)) if avg_loss != 0 else 100.0)
    return out


def macd_histogram_series(closes, fast=12, slow=26, signal=9):
    """Standard MACD histogram (macd_line - signal_line), full series."""
    if len(closes) < slow + signal:
        return None
    ema_fast = ema_series(closes, fast)
    ema_slow = ema_series(closes, slow)
    macd_line = [
        (f - s) if (f is not None and s is not None) else None
        for f, s in zip(ema_fast, ema_slow)
    ]
    valid = [v for v in macd_line if v is not None]
    if len(valid) < signal:
        return None
    signal_line_valid = ema_series(valid, signal)
    # re-align signal line to the full-length macd_line index space
    offset = len(macd_line) - len(valid)
    histogram = [None] * offset
    for m, s in zip(valid, signal_line_valid):
        histogram.append(None if s is None else m - s)
    return histogram


def bollinger_lower_band(closes, period=20, num_std=2):
    m = sma(closes, period)
    sd = stdev(closes, period)
    if m is None or sd is None:
        return None
    return m - num_std * sd


def stochastic_k(bars, period=14):
    if len(bars) < period:
        return None
    window = bars[-period:]
    highest_high = max(b["high"] for b in window)
    lowest_low = min(b["low"] for b in window)
    close = bars[-1]["close"]
    if highest_high == lowest_low:
        return None
    return (close - lowest_low) / (highest_high - lowest_low) * 100


def williams_percent_range(bars, period=14):
    """Williams %R(N): (Highest High(N) - Close) / (Highest High(N) - Lowest
    Low(N)) * -100. Not used in the live daily pipeline (Williams %R comes
    from the scanner's own filter there, confirmed reliable) — this exists
    for experiments/backtest.py, which has no scan to pull a point-in-time
    value from and has to compute everything from raw historicals."""
    if len(bars) < period:
        return None
    window = bars[-period:]
    highest_high = max(b["high"] for b in window)
    lowest_low = min(b["low"] for b in window)
    close = bars[-1]["close"]
    if highest_high == lowest_low:
        return None
    return (highest_high - close) / (highest_high - lowest_low) * -100


def support_level(bars, lookback=60):
    """Simple heuristic: lowest low over the trailing `lookback` days.
    Documented approximation, not a formal swing-low/pivot algorithm — see
    rubric.md's a6_support note. Uses whatever history is available if
    fewer than `lookback` bars are present."""
    if not bars:
        return None
    window = bars[-lookback:]
    return min(b["low"] for b in window)


def relative_volume(bars, period=30):
    """today's volume / trailing-N-day average volume (excluding today)."""
    if len(bars) < period + 1:
        return None
    today = bars[-1]
    window = bars[-(period + 1):-1]
    avg_vol = sum(b["volume"] for b in window) / period
    if avg_vol == 0:
        return None
    return today["volume"] / avg_vol


def aroon_oscillator(bars, period=14):
    if len(bars) < period:
        return None
    window = bars[-period:]
    highs = [b["high"] for b in window]
    lows = [b["low"] for b in window]
    days_since_high = period - 1 - highs.index(max(highs))
    days_since_low = period - 1 - lows.index(min(lows))
    aroon_up = (period - days_since_high) / period * 100
    aroon_down = (period - days_since_low) / period * 100
    return aroon_up - aroon_down


def true_range(bars, i):
    high, low = bars[i]["high"], bars[i]["low"]
    prev_close = bars[i - 1]["close"]
    return max(high - low, abs(high - prev_close), abs(low - prev_close))


def adx_series(bars, period=14):
    """Standard Wilder ADX. Returns full series aligned to bars (leading Nones)."""
    n = len(bars)
    if n < period * 2:
        return [None] * n
    plus_dm = [0.0]
    minus_dm = [0.0]
    tr = [0.0]
    for i in range(1, n):
        up_move = bars[i]["high"] - bars[i - 1]["high"]
        down_move = bars[i - 1]["low"] - bars[i]["low"]
        plus_dm.append(up_move if (up_move > down_move and up_move > 0) else 0.0)
        minus_dm.append(down_move if (down_move > up_move and down_move > 0) else 0.0)
        tr.append(true_range(bars, i))

    def wilder_smooth(series, period):
        out = [None] * period
        seed = sum(series[1:period + 1])
        out.append(seed)
        prev = seed
        for i in range(period + 1, len(series)):
            cur = prev - (prev / period) + series[i]
            out.append(cur)
            prev = cur
        return out

    smoothed_tr = wilder_smooth(tr, period)
    smoothed_plus_dm = wilder_smooth(plus_dm, period)
    smoothed_minus_dm = wilder_smooth(minus_dm, period)

    dx = [None] * n
    for i in range(n):
        if smoothed_tr[i] in (None, 0) or smoothed_plus_dm[i] is None:
            continue
        plus_di = 100 * smoothed_plus_dm[i] / smoothed_tr[i]
        minus_di = 100 * smoothed_minus_dm[i] / smoothed_tr[i]
        denom = plus_di + minus_di
        dx[i] = 100 * abs(plus_di - minus_di) / denom if denom else 0.0

    valid_dx = [v for v in dx if v is not None]
    if len(valid_dx) < period:
        return [None] * n
    adx = [None] * n
    first_adx_idx = n - len(valid_dx) + period - 1
    adx[first_adx_idx] = sum(valid_dx[:period]) / period
    prev = adx[first_adx_idx]
    vi = period
    for i in range(first_adx_idx + 1, n):
        if dx[i] is None:
            continue
        cur = (prev * (period - 1) + dx[i]) / period
        adx[i] = cur
        prev = cur
    return adx


# ---------------------------------------------------------------------------
# Rubric criterion scoring — thresholds match rubric.md exactly.
# NOTE: e29_liquidity and e31_iv_extreme are tagged [M] in rubric.md but the
# doc does not give crisp numeric cutoffs — the thresholds below are a
# documented, reasonable approximation, not a verified-precise rule. Flagged
# in each result's "note" field; don't present them with false confidence.
# ---------------------------------------------------------------------------

def _d(**fields):
    """Return the named raw-data fields a criterion needs, as fetched —
    each individual field that's missing shows 'N/A' (not Python None,
    so it's unambiguous in the JSON output), not a fabricated value."""
    return {k: ("N/A" if v is None or v == "" else v) for k, v in fields.items()}


NO_DATA_NEEDED = "N/A"  # for criteria with zero data requirement at all (pure synthesis judgment)


def collect_rubric_data(data):
    """For each of the 33 opportunity-scanner rubric criteria, return the
    named raw data it needs, with real values where fetchable. This does
    NOT compute a score — it's a data-collection pass only (see module
    docstring). A criterion needing no external data at all maps to the
    literal string "N/A"; a criterion needing data that's individually
    missing shows "N/A" for that specific field."""
    out = {}
    archetype = data.get("archetype")
    price = data.get("current_price")
    scan = data.get("scan_columns") or {}
    fund = data.get("fundamentals") or {}
    bars = data.get("historicals") or []
    earnings = data.get("earnings") or []
    held = set(data.get("held_tickers") or [])
    ticker = data.get("ticker")
    today = data.get("today")

    closes = _closes(bars) if bars else []

    # --- Category A (turnaround archetype only) ---
    out["a1_pctoffhigh"] = _d(high_52_weeks=fund.get("high_52_weeks"), current_price=price)

    rsi_val = scan.get("RSI")
    if rsi_val is None and closes:
        series = rsi_series(closes)
        rsi_val = series[-1] if series and series[-1] is not None else None
        if rsi_val is not None:
            rsi_val = round(rsi_val, 2)
    out["a2_rsi"] = _d(rsi_14=rsi_val)

    out["a3_williams"] = _d(williams_pct_range_14=scan.get("Williams Percent Range (14)"))

    stoch = stochastic_k(bars, 14) if bars else None
    out["a4_stochastic"] = _d(stochastic_k_14=round(stoch, 2) if stoch is not None else None)

    lower_band = bollinger_lower_band(closes, 20, 2) if closes else None
    out["a5_bollinger"] = _d(
        bollinger_lower_band_20_2sd=round(lower_band, 2) if lower_band is not None else None,
        current_price=price)

    support = support_level(bars, 20) if bars else None
    out["a6_support"] = _d(
        support_level_trailing20d_low=round(support, 2) if support is not None else None,
        current_price=price)

    out["a7_peg_lt1"] = _d(peg=scan.get("PEG"))

    out["a8_cyclical_judgment"] = _d(sector=fund.get("sector"))

    # --- Category B ---
    out["b9_mktcap"] = _d(market_cap=scan.get("Market cap") or fund.get("market_cap"))
    out["b10_grossmargin"] = _d(gross_margin=scan.get("Gross margin"))
    out["b11_opmargin"] = _d(operating_margin=scan.get("Operating margin"))
    out["b12_netmargin"] = NO_DATA_NEEDED  # RETIRED 2026-07-07 — Stage-0 gate now, never scored (see rubric.md Gates)
    out["b13_roe"] = _d(return_on_equity=scan.get("Return on equity"))
    out["b14_roa"] = _d(return_on_assets=scan.get("Return on assets"))
    out["b15_dividend"] = _d(dividend_yield=fund.get("dividend_yield")) if "dividend_yield" in fund else NO_DATA_NEEDED

    if earnings:
        recent = [e["eps_actual"] for e in earnings[-4:] if e.get("eps_actual") is not None]
        out["b16_epstrend"] = _d(trailing_eps_actuals=recent if recent else None)
    else:
        out["b16_epstrend"] = _d(trailing_eps_actuals=None)

    out["b17_leverage_judgment"] = NO_DATA_NEEDED  # no direct debt/leverage filter exists — judgment-only by design

    # --- Category C ---
    hist = macd_histogram_series(closes) if closes else None
    recent_hist = [h for h in hist[-10:] if h is not None] if hist else None
    out["c18_macd"] = _d(macd_histogram_latest=hist[-1] if hist and hist[-1] is not None else None,
                          macd_histogram_trailing10=recent_hist)

    ema50 = scan.get("EMA")
    if ema50 is None and len(closes) >= 50:
        series = ema_series(closes, 50)
        ema50 = round(series[-1], 2) if series[-1] is not None else None
    out["c19_ema"] = _d(ema_50=ema50, current_price=price)

    aroon = scan.get("Aroon Oscillator (14)")
    if aroon is None and bars:
        aroon = aroon_oscillator(bars, 14)
    out["c20_aroon"] = _d(aroon_oscillator_14=aroon)

    adx = scan.get("Average directional index (14)")
    if adx is None and len(bars) >= 28:
        series = adx_series(bars, 14)
        adx = series[-1]
    out["c21_adx"] = _d(adx_14=adx)

    rv = relative_volume(bars, 30) if bars else None
    up_day = (bars[-1]["close"] > bars[-1]["open"]) if bars else None
    out["c22_relvol"] = _d(relative_volume_30d=round(rv, 2) if rv is not None else None, is_up_day=up_day)

    rsi_series_full = rsi_series(closes) if closes else None
    recent_rsi = [v for v in rsi_series_full[-15:] if v is not None] if rsi_series_full else None
    out["c23_rsirecross"] = _d(
        rsi_14_latest=rsi_series_full[-1] if rsi_series_full and rsi_series_full[-1] is not None else None,
        rsi_14_trailing15=recent_rsi)

    # --- Category D ---
    if earnings:
        last = earnings[-1]
        out["d24_epsbeat"] = _d(eps_estimate=last.get("eps_estimate"), eps_actual=last.get("eps_actual"))
    else:
        out["d24_epsbeat"] = _d(eps_estimate=None, eps_actual=None)

    out["d25_noearnings2wk"] = _d(next_earnings_date=data.get("next_earnings_date"), today=today)

    out["d26_tailwind_judgment"] = _d(sector=fund.get("sector"))
    out["d27_catalyst_judgment"] = _d(description=fund.get("description"))

    if archetype == "compounder":
        out["d28_pegroe_combo"] = _d(peg=scan.get("PEG"), return_on_equity=scan.get("Return on equity"))
    else:
        out["d28_pegroe_combo"] = NO_DATA_NEEDED  # compounder-archetype-only criterion

    # --- Category E ---
    out["e29_liquidity"] = _d(average_volume=fund.get("average_volume"), float_shares=fund.get("float"))
    out["e30_not_concentrated"] = _d(ticker=ticker, held_tickers=sorted(held) if held else None)
    out["e31_iv_extreme"] = _d(historical_volatility_30d=scan.get("Historical volatility (30, 1D)"))
    out["e32_fitstyle_judgment"] = NO_DATA_NEEDED  # holistic synthesis judgment by design — not a fetch

    # --- Gate: criterion 33 ---
    out["b33_domainleadership_judgment"] = _d(sector=fund.get("sector"), description=fund.get("description"))

    return out


# Backward-compatible alias — earlier drafts of this script called it score_criteria.
score_criteria = collect_rubric_data


def evaluate_pass_fail(data):
    """For each of the 33 rubric criteria, return "PASS" (scores >0 points
    under rubric.md's exact thresholds), "FAIL" (scores exactly 0), or
    "N/A" (data unavailable, judgment-only by design, retired, or
    archetype-conditional and not applicable to this candidate's archetype).

    PASS/FAIL is a *binary* simplification of rubric.md's point tiers —
    for a graduated criterion (e.g. a1_pctoffhigh: 8/6/4/2/0), PASS means
    "cleared some tier above zero," not "hit the top tier." This matches
    the account's existing 40%-off-high gate semantics (SKILL.md step 2)
    and is meant for "which stocks clear this bar at all," not a
    replacement for the full point score in reports/opportunity-scanner-
    logs/*.csv.
    """
    archetype = data.get("archetype")
    price = data.get("current_price")
    scan = data.get("scan_columns") or {}
    fund = data.get("fundamentals") or {}
    bars = data.get("historicals") or []
    earnings = data.get("earnings") or []
    held = set(data.get("held_tickers") or [])
    ticker = data.get("ticker")
    today = data.get("today")
    closes = _closes(bars) if bars else []

    def pf(cond):
        return "PASS" if cond else "FAIL"

    out = {}

    high_52w = fund.get("high_52_weeks")
    out["a1_pctoffhigh"] = pf((high_52w - price) / high_52w * 100 >= 40) if (high_52w and price) else "N/A"

    rsi_val = scan.get("RSI")
    if rsi_val is None and closes:
        series = rsi_series(closes)
        rsi_val = series[-1] if series and series[-1] is not None else None
    out["a2_rsi"] = pf(rsi_val < 30) if rsi_val is not None else "N/A"

    williams = scan.get("Williams Percent Range (14)")
    out["a3_williams"] = pf(williams < -80) if williams is not None else "N/A"

    stoch = stochastic_k(bars, 14) if bars else None
    out["a4_stochastic"] = pf(stoch < 20) if stoch is not None else "N/A"

    lower_band = bollinger_lower_band(closes, 20, 2) if closes else None
    out["a5_bollinger"] = pf(price < lower_band) if (lower_band is not None and price is not None) else "N/A"

    support = support_level(bars, 20) if bars else None
    out["a6_support"] = pf(price <= support) if (support is not None and price is not None) else "N/A"

    peg = scan.get("PEG")
    out["a7_peg_lt1"] = pf(peg < 1) if (peg is not None and peg != "") else "N/A"

    out["a8_cyclical_judgment"] = "N/A"  # judgment call, not fetchable as pass/fail

    mktcap = scan.get("Market cap") or fund.get("market_cap")
    out["b9_mktcap"] = pf(mktcap > 2e9) if mktcap is not None else "N/A"

    gm = scan.get("Gross margin")
    out["b10_grossmargin"] = pf(gm > 0.30) if (gm is not None and gm != "") else "N/A"

    om = scan.get("Operating margin")
    out["b11_opmargin"] = pf(om > 0) if (om is not None and om != "") else "N/A"

    out["b12_netmargin"] = "N/A"  # retired 2026-07-07 — Stage-0 gate now, never scored

    roe = scan.get("Return on equity")
    out["b13_roe"] = pf(roe > 0) if (roe is not None and roe != "") else "N/A"

    roa = scan.get("Return on assets")
    out["b14_roa"] = pf(roa > 0) if (roa is not None and roa != "") else "N/A"

    out["b15_dividend"] = pf(bool(fund.get("dividend_yield"))) if "dividend_yield" in fund else "N/A"

    if earnings and len(earnings) >= 2:
        recent = [e["eps_actual"] for e in earnings[-4:] if e.get("eps_actual") is not None]
        out["b16_epstrend"] = pf(recent[-1] - recent[0] >= 0) if len(recent) >= 2 else "N/A"
    else:
        out["b16_epstrend"] = "N/A"

    out["b17_leverage_judgment"] = "N/A"  # no direct data source, judgment-only by design

    hist = macd_histogram_series(closes) if closes else None
    if hist:
        recent_hist = [h for h in hist[-10:] if h is not None]
        turned_positive = len(recent_hist) >= 2 and recent_hist[-1] > 0 and any(h <= 0 for h in recent_hist[:-1])
        out["c18_macd"] = pf(turned_positive)
    else:
        out["c18_macd"] = "N/A"

    ema50 = scan.get("EMA")
    if ema50 is None and len(closes) >= 50:
        series = ema_series(closes, 50)
        ema50 = series[-1]
    out["c19_ema"] = pf(price > ema50) if (ema50 is not None and price is not None) else "N/A"

    aroon = scan.get("Aroon Oscillator (14)")
    if aroon is None and bars:
        aroon = aroon_oscillator(bars, 14)
    out["c20_aroon"] = pf(aroon > 0) if aroon is not None else "N/A"

    adx = scan.get("Average directional index (14)")
    if adx is None and len(bars) >= 28:
        series = adx_series(bars, 14)
        adx = series[-1]
    out["c21_adx"] = pf(adx > 25) if adx is not None else "N/A"

    rv = relative_volume(bars, 30) if bars else None
    if rv is not None:
        up_day = bars[-1]["close"] > bars[-1]["open"]
        out["c22_relvol"] = pf(rv > 1.3 and up_day)
    else:
        out["c22_relvol"] = "N/A"

    if closes:
        series = rsi_series(closes)
        recent = [v for v in series[-15:] if v is not None]
        crossed = any(recent[i - 1] < 30 <= recent[i] for i in range(1, len(recent)))
        out["c23_rsirecross"] = pf(crossed)
    else:
        out["c23_rsirecross"] = "N/A"

    if earnings:
        last = earnings[-1]
        est, act = last.get("eps_estimate"), last.get("eps_actual")
        out["d24_epsbeat"] = pf(act >= est) if (est is not None and act is not None) else "N/A"
    else:
        out["d24_epsbeat"] = "N/A"

    next_earn = data.get("next_earnings_date")
    if next_earn and today:
        days_out = (datetime.fromisoformat(next_earn) - datetime.fromisoformat(today)).days
        out["d25_noearnings2wk"] = pf(days_out > 14 or days_out < 0)
    else:
        out["d25_noearnings2wk"] = "N/A"

    out["d26_tailwind_judgment"] = "N/A"
    out["d27_catalyst_judgment"] = "N/A"

    if archetype == "compounder":
        peg, roe_v = scan.get("PEG"), scan.get("Return on equity")
        out["d28_pegroe_combo"] = pf(peg < 1.5 or roe_v > 0.15) if (peg is not None and roe_v is not None) else "N/A"
    else:
        out["d28_pegroe_combo"] = "N/A"  # compounder-archetype-only criterion

    avg_vol, float_shares = fund.get("average_volume"), fund.get("float")
    if avg_vol and float_shares:
        out["e29_liquidity"] = pf((avg_vol / float_shares) > 0.001)
    else:
        out["e29_liquidity"] = "N/A"

    out["e30_not_concentrated"] = pf(ticker not in held) if ticker is not None else "N/A"

    hv = scan.get("Historical volatility (30, 1D)")
    out["e31_iv_extreme"] = pf(0.25 < hv < 1.5) if hv is not None else "N/A"

    out["e32_fitstyle_judgment"] = "N/A"

    out["b33_domainleadership_judgment"] = "N/A"  # gate — genuine judgment, not evaluable as pass/fail here

    return out


def _self_test():
    """Synthetic 90-bar uptrend-then-dip series, no real API data needed."""
    import random
    random.seed(42)
    bars = []
    price = 100.0
    for i in range(90):
        drift = 0.3 if i < 60 else -0.4
        price = max(1.0, price + drift + random.uniform(-1.5, 1.5))
        high = price + random.uniform(0, 1.5)
        low = price - random.uniform(0, 1.5)
        vol = random.uniform(1e6, 3e6) * (2.0 if i == 89 else 1.0)
        bars.append({"begins_at": f"day{i}", "open": price - 0.2, "high": high,
                      "low": low, "close": price, "volume": vol})

    data = {
        "ticker": "TESTCO",
        "archetype": "turnaround",
        "current_price": bars[-1]["close"],
        "scan_columns": {"RSI": 25.0, "Williams Percent Range (14)": -85.0, "PEG": 0.8,
                          "Gross margin": 0.35, "Operating margin": 0.1,
                          "Return on equity": 0.12, "Return on assets": 0.06,
                          "Market cap": 3e9, "Historical volatility (30, 1D)": 0.4},
        "fundamentals": {"high_52_weeks": 150.0, "low_52_weeks": 60.0,
                          "dividend_yield": 0.02, "average_volume": 2e6,
                          "float": 5e8, "sector": "Technology", "description": "test co"},
        "historicals": bars,
        "earnings": [{"quarter_end": "2026-01-01", "eps_estimate": 1.0, "eps_actual": 0.9},
                     {"quarter_end": "2026-04-01", "eps_estimate": 1.1, "eps_actual": 1.2}],
        "next_earnings_date": "2026-08-01",
        "today": "2026-07-07",
        "held_tickers": [],
    }
    result = collect_rubric_data(data)
    print(json.dumps(result, indent=2, default=str))

    def has_real_data(v):
        if v == "N/A":
            return False
        return any(x != "N/A" for x in v.values())

    with_data = sum(1 for v in result.values() if has_real_data(v))
    print(f"\n{with_data}/{len(result)} criteria have at least one real (non-N/A) data value on synthetic data",
          file=sys.stderr)
    assert with_data >= 25, "self-test regression: fewer criteria have real data than expected"

    pf_result = evaluate_pass_fail(data)
    passed = sum(1 for v in pf_result.values() if v == "PASS")
    failed = sum(1 for v in pf_result.values() if v == "FAIL")
    na = sum(1 for v in pf_result.values() if v == "N/A")
    print(f"pass/fail: {passed} PASS, {failed} FAIL, {na} N/A (of {len(pf_result)})", file=sys.stderr)
    assert passed + failed >= 20, "self-test regression: fewer criteria evaluable as pass/fail than expected"
    print("Self-test passed.", file=sys.stderr)


def main():
    if len(sys.argv) >= 2 and sys.argv[1] == "--self-test":
        _self_test()
        return

    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    mode = "data"
    args = sys.argv[1:]
    if args and args[0] in ("--data", "--pass-fail"):
        mode = "data" if args[0] == "--data" else "pass-fail"
        args = args[1:]

    if not args:
        print(__doc__)
        sys.exit(1)

    with open(args[0]) as f:
        data = json.load(f)

    result = evaluate_pass_fail(data) if mode == "pass-fail" else collect_rubric_data(data)
    args = args[1:]

    if args:
        with open(args[0], "w") as f:
            json.dump(result, f, indent=2, default=str)
    else:
        print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
