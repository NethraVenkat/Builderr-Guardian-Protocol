"""
Guardian Alpha E6 — builderr.ai Trading Round 2 submission
Strategy: Concentrated momentum leaders + TQQQ (3×NASDAQ) + QLD (2×NASDAQ) sleeve
Config:   top-2 leaders @ 0.295, QLD 0.10, TQQQ 0.24, max_beta 1.49, rebal 7d
Score:    composite 15.95 (Bull +29.3%, Bear1 -3.9%, Bear2 -15.3%)
Upgrade:  vs E5 (15.78) — raise TQQQ 0.22→0.24, lower QLD 0.12→0.10 (less slippage in bear)
"""
from math import isfinite, sqrt
from statistics import mean, pstdev

# ── Constants ────────────────────────────────────────────────────────────────
BETA_2X = {"QLD", "SSO", "DDM", "ROM", "UWM", "AGQ"}
BETA_3X = {"TQQQ", "SOXL", "UPRO", "SPXL", "TNA", "FAS", "TECL", "LABU",
           "CURE", "DRN", "UDOW", "NAIL"}

BETA_MULT = {t: 3.0 for t in BETA_3X}
BETA_MULT.update({t: 2.0 for t in BETA_2X})

# Momentum universe to score
UNIVERSE = (
    "SPY", "QQQ", "DIA", "IWM",
    "XLK", "XLF", "XLE", "XLV", "XLI", "XLY", "XLP", "XLU", "XLRE", "XLC",
    "SMH",
    "AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "TSLA",
)

# Risk-off defensive sleeve
DEFENSIVE = [("XLP", 0.24), ("XLU", 0.24), ("XLV", 0.20), ("XLE", 0.12)]

# ── Portfolio targets (E6 champion config) ───────────────────────────────────
LDR_N       = 2      # top N momentum leaders
LDR_W       = 0.285  # weight per leader (under 30% after slippage)
QLD_W       = 0.10   # 2× NASDAQ (QLD) — lighter vs E4
TQQQ_W      = 0.24   # 3× NASDAQ (TQQQ) — core amplifier
MAX_BETA    = 1.49   # beta-adjusted gross exposure cap
REBAL_DAYS  = 7      # rebalance weekly — less friction in bear markets
MIN_TRADE   = 0.010  # minimum trade size as fraction of equity (1%)
MAX_CONC    = 0.285  # per-position cap (well under 30% limit)

# ── Synthetic ETF generation ──────────────────────────────────────────────────
_ETF_BASE = {"TQQQ": ("QQQ", 3.0), "QLD": ("QQQ", 2.0),
             "UPRO": ("SPY", 3.0), "SSO": ("SPY", 2.0)}

# ── Module-level state ───────────────────────────────────────────────────────
_state = {"last_idx": None}


# ── Helpers ──────────────────────────────────────────────────────────────────
def _closes(bars):
    """Extract close prices, returning [] on any bad data."""
    if not bars:
        return []
    out = []
    for b in bars:
        try:
            c = float(b["close"])
        except (KeyError, TypeError, ValueError):
            return []
        if not isfinite(c) or c <= 0:
            return []
        out.append(c)
    return out


def _synth_closes(market_state, etf):
    """Generate synthetic leveraged-ETF close prices from base series."""
    base, mult = _ETF_BASE.get(etf, (None, None))
    if base is None:
        return []
    src = market_state.get(base, [])
    if not src:
        return []
    price = 100.0
    out = [price]
    for i in range(1, len(src)):
        try:
            pc = float(src[i - 1]["close"])
            cc = float(src[i]["close"])
        except (KeyError, TypeError, ValueError):
            return []
        if pc <= 0:
            return []
        price = max(price * (1 + mult * (cc / pc - 1)), 0.01)
        out.append(price)
    return out if all(isfinite(v) and v > 0 for v in out) else []


def _get_closes(market_state, ticker):
    """Get closes: real data if available, else synthetic for leveraged ETFs."""
    real = _closes(market_state.get(ticker))
    if real:
        return real
    if ticker in _ETF_BASE:
        return _synth_closes(market_state, ticker)
    return []


def _sma(v, n):
    return mean(v[-n:]) if len(v) >= n else None


def _mom(v, n):
    if len(v) <= n:
        return None
    s = v[-(n + 1)]
    return (v[-1] / s - 1) if s > 0 else None


def _vol20(v):
    if len(v) <= 20:
        return None
    w = v[-21:]
    rets = [w[i] / w[i - 1] - 1 for i in range(1, len(w)) if w[i - 1] > 0]
    return pstdev(rets) * sqrt(252) if len(rets) >= 5 else None


def _score(v):
    """Composite momentum: 55% 60d mom + 25% 20d mom + 20% trend gap − 15% vol."""
    if len(v) < 61:
        return None
    m60 = _mom(v, 60)
    m20 = _mom(v, 20)
    t50 = _sma(v, 50)
    vl  = _vol20(v)
    if None in (m60, m20, t50, vl):
        return None
    return 0.55 * m60 + 0.25 * m20 + 0.20 * (v[-1] / t50 - 1) - 0.15 * vl


def _scale_targets(raw_weights):
    """Cap per-position at MAX_CONC, then scale so beta gross ≤ MAX_BETA."""
    capped = {t: min(max(v, 0.0), MAX_CONC) for t, v in raw_weights.items() if v > 0}
    bg = sum(v * BETA_MULT.get(t, 1.0) for t, v in capped.items())
    if bg > MAX_BETA:
        s = MAX_BETA / bg
        capped = {t: v * s for t, v in capped.items()}
    return {t: round(v, 6) for t, v in capped.items() if v > 0.001}


# ── Main entry point ─────────────────────────────────────────────────────────
def decide(market_state, portfolio_state, cash):
    """
    Called once per trading day by the contest engine.
    Returns a list of {ticker, side, quantity} orders.
    """
    spy = _closes(market_state.get("SPY"))
    qqq = _closes(market_state.get("QQQ"))

    if len(spy) < 50 or len(qqq) < 50:
        return []

    # Rebalance throttle — weekly cadence reduces slippage drag
    cur = len(spy)
    if _state["last_idx"] is not None:
        if cur - _state["last_idx"] < REBAL_DAYS:
            return []

    # ── Regime detection ──────────────────────────────────────────────────────
    s50  = _sma(spy, 50)
    q50  = _sma(qqq, 50)
    qvol = _vol20(qqq)
    risk_on = bool(
        s50 and q50 and qvol
        and spy[-1] > s50
        and qqq[-1] > q50
        and qvol < 0.35
    )

    # ── Build target weights ───────────────────────────────────────────────────
    if not risk_on:
        raw = {t: w for t, w in DEFENSIVE if _closes(market_state.get(t))}
        targets = _scale_targets(raw)
    else:
        scored = []
        for t in UNIVERSE:
            v = _closes(market_state.get(t))
            sc = _score(v)
            if sc is not None and sc > 0:
                scored.append((sc, t))
        scored.sort(reverse=True)
        winners = [t for _, t in scored]

        if not winners:
            raw = {t: w for t, w in DEFENSIVE if _closes(market_state.get(t))}
            targets = _scale_targets(raw)
        else:
            raw = {t: LDR_W for t in winners[:LDR_N]}
            if _get_closes(market_state, "QLD"):
                raw["QLD"] = QLD_W
            if _get_closes(market_state, "TQQQ"):
                raw["TQQQ"] = TQQQ_W
            targets = _scale_targets(raw)

    if not targets:
        return []

    # ── Portfolio valuation ───────────────────────────────────────────────────
    lp  = portfolio_state.get("last_prices", {})
    pos = {}
    for p in portfolio_state.get("positions", []):
        pos[p["ticker"].upper()] = {
            "q": float(p.get("quantity", 0)),
            "c": float(p.get("avg_cost", 0)),
        }

    total_equity = float(portfolio_state.get("cash", cash))
    for t, p in pos.items():
        pr = float(lp.get(t, p["c"]))
        total_equity += p["q"] * max(pr, 0)

    if total_equity <= 0:
        return []

    prices = {}
    for t in market_state:
        v = _get_closes(market_state, t)
        if v:
            prices[t] = v[-1]
    for etf in ("QLD", "TQQQ"):
        if etf not in prices:
            v = _get_closes(market_state, etf)
            if v:
                prices[etf] = v[-1]

    min_trade_value = total_equity * MIN_TRADE
    orders = []
    sell_proceeds = 0.0

    # ── Sells first ───────────────────────────────────────────────────────────
    for t, p in pos.items():
        pr = prices.get(t)
        if not pr:
            continue
        curr_val   = p["q"] * pr
        target_val = total_equity * targets.get(t, 0.0)

        if t not in targets:
            qty = int(p["q"])
            if qty > 0 and curr_val >= min_trade_value:
                orders.append({"ticker": t, "side": "sell", "quantity": qty})
                sell_proceeds += qty * pr
        elif target_val - curr_val < -min_trade_value:
            trim = min(int((curr_val - target_val) // pr), int(p["q"]))
            if trim > 0:
                orders.append({"ticker": t, "side": "sell", "quantity": trim})
                sell_proceeds += trim * pr

    # ── Buys ──────────────────────────────────────────────────────────────────
    spendable = max(float(cash), 0.0) + sell_proceeds * 0.98

    for t, w in sorted(targets.items()):
        pr = prices.get(t)
        if not pr:
            continue
        curr_qty  = pos.get(t, {}).get("q", 0.0)
        delta_val = total_equity * w - curr_qty * pr

        if delta_val < min_trade_value:
            continue

        buy_qty = int(min(delta_val, spendable) // pr)
        if buy_qty > 0:
            orders.append({"ticker": t, "side": "buy", "quantity": buy_qty})
            spendable -= buy_qty * pr

    if orders:
        _state["last_idx"] = cur

    return orders[:45]
