import os
import sys
sys.path.insert(0, os.path.abspath("."))

import gzip
import json
from pathlib import Path
from preview import _expand
from statistics import mean, pstdev
from math import sqrt

raw_regimes = json.loads(gzip.open("sample_regimes.json.gz", "rb").read())
regime = raw_regimes["vol_spike_snapback"]
bars = {t: _expand(rows) for t, rows in regime["bars"].items()}
all_dates = sorted({b["ts"] for rows in bars.values() for b in rows})
eval_dates = [d for d in all_dates if regime["eval_start"] <= d <= regime["eval_end"]]

print(f"Total eval dates: {len(eval_dates)}")

spy_bars = bars.get("SPY", [])
qqq_bars = bars.get("QQQ", [])

def get_closes_up_to(bar_list, date):
    return [b["close"] for b in bar_list if b["ts"] <= date]

for i, date_str in enumerate(eval_dates):
    s_closes = get_closes_up_to(spy_bars, date_str)
    q_closes = get_closes_up_to(qqq_bars, date_str)
    
    spy_c = s_closes[-1]
    qqq_c = q_closes[-1]
    
    spy_sma50 = mean(s_closes[-50:]) if len(s_closes) >= 50 else None
    qqq_sma50 = mean(q_closes[-50:]) if len(q_closes) >= 50 else None
    qqq_sma20 = mean(q_closes[-20:]) if len(q_closes) >= 20 else None
    
    if len(q_closes) > 20:
        window = q_closes[-21:]
        rets = [window[k] / window[k-1] - 1.0 for k in range(1, len(window))]
        vol20 = pstdev(rets) * sqrt(252.0)
    else:
        vol20 = None
        
    spy_above_50 = (spy_c > spy_sma50) if spy_sma50 else None
    qqq_above_50 = (qqq_c > qqq_sma50) if qqq_sma50 else None
    qqq_above_20 = (qqq_c > qqq_sma20) if qqq_sma20 else None
    vol_sub_35 = (vol20 < 0.35) if vol20 is not None else None
    
    risk_on_e0 = bool(spy_above_50 and qqq_above_50 and vol_sub_35)
    
    v_str = f"{vol20:.3f}" if vol20 is not None else "N/A"
    s50_str = f"{spy_sma50:.2f}" if spy_sma50 else "N/A"
    q50_str = f"{qqq_sma50:.2f}" if qqq_sma50 else "N/A"
    q20_str = f"{qqq_sma20:.2f}" if qqq_sma20 else "N/A"
    
    if i in [0, 1, 4, 5, 6, 7, 10, 15, 20, 23, 24, 25, 30, 35, 40, 45, 48, 49] or risk_on_e0:
        print(f"Day {i:2d} ({date_str}) | SPY:{spy_c:6.2f}(>{s50_str}:{str(spy_above_50):5s}) | QQQ:{qqq_c:6.2f}(>{q50_str}:{str(qqq_above_50):5s}, >{q20_str}:{str(qqq_above_20):5s}) | Vol20:{v_str}(<0.35:{str(vol_sub_35):5s}) | RiskOn:{risk_on_e0}")
