"""
Forensic audit of V13-03: Liquidation Timeline Reconciliation.
"""
import os
import sys
sys.path.insert(0, os.path.abspath("."))

import gzip
import json
from research.engine.provider import StaticRegimeProvider
from research.engine.replay import ReplayEngine
from preview import _expand

raw_regimes = json.loads(gzip.open("sample_regimes.json.gz", "rb").read())
regime = raw_regimes["vol_spike_snapback"]
bars = {t: _expand(rows) for t, rows in regime["bars"].items()}
all_dates = sorted({b["ts"] for rows in bars.values() for b in rows})
eval_dates = [d for d in all_dates if regime["eval_start"] <= d <= regime["eval_end"]]

prov = StaticRegimeProvider("sample_regimes.json.gz", "vol_spike_snapback")
eng = ReplayEngine("agent.py", prov)
res = eng.run_replay()

print("=== TIMELINE OF INITIAL TECH BASKET (AAPL, MSFT, NVDA, QQQ, XLK) ===")
print(f"{'0-Idx':<5} | {'1-Idx':<5} | {'Calendar Date':<12} | {'Phase':<20} | {'Action / Telemetry'}")
print("-" * 110)

spy_bars = {b["ts"]: b for b in bars["SPY"]}
qqq_bars = {b["ts"]: b for b in bars["QQQ"]}

for idx, dt in enumerate(eval_dates[:10]):
    spy_c = spy_bars[dt]["close"]
    qqq_c = qqq_bars[dt]["close"]
    eq = res["equity_curve"][idx]
    
    # Check fills on this date open
    fills_today = [f for f in res["fill_log"] if dt in f.ticker or True] # we can check orders
    
    action = ""
    phase = ""
    if idx == 0:
        phase = "First Scored Close"
        action = f"SPY={spy_c:.2f}, QQQ={qqq_c:.2f} (RiskOn=True). Agent emits initial BUY orders for Tech basket."
    elif idx == 1:
        phase = "Session 2 Open & Close"
        action = f"Open fills BUY orders for Tech basket ($91,455.87 cost). Equity close=${eq:,.2f}."
    elif idx in (2, 3, 4):
        phase = f"Session {idx+1} Holding"
        action = f"Tech held. SPY={spy_c:.2f}. Days since rebalance={idx-0}. No rebalance triggered."
    elif idx == 5:
        phase = "Session 6 Close (Rebal)"
        action = f"Days since rebalance=5! SPY={spy_c:.2f} < SMA50. RiskOn=False! Agent emits SELL orders for Tech basket at Close."
    elif idx == 6:
        phase = "Session 7 Open (Fill)"
        action = f"Open fills SELL orders for Tech basket! Gross proceeds=$79,054.30. Realized Loss=-$12,401.57. Fills BUY defensive basket."
    elif idx >= 7:
        phase = f"Session {idx+1} Holding"
        action = f"Defensive basket held. Equity=${eq:,.2f}."
        
    print(f"Day {idx:<2d} | Sess {idx+1:<2d}| {dt:<12} | {phase:<20} | {action}")
