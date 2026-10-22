import os
import sys
sys.path.insert(0, os.path.abspath("."))

from research.engine.provider import StaticRegimeProvider
from research.engine.replay import ReplayEngine
from research.strategies.v12_candidate_ae import CandidateAE_Combined

prov = StaticRegimeProvider('sample_regimes.json.gz', 'calm_uptrend')

res_e0 = ReplayEngine('agent.py', prov).run_replay()
cand_ae = CandidateAE_Combined()
res_ae = ReplayEngine(cand_ae.decide, prov).run_replay()

print("=== BASELINE E0 ===")
buys_0 = sum(f.notional for f in res_e0['fill_log'] if f.side == 'buy')
sells_0 = sum(f.notional for f in res_e0['fill_log'] if f.side == 'sell')
print(f"Total buys:                  ${buys_0:,.2f}")
print(f"Total sells:                 ${sells_0:,.2f}")
print(f"Two-sided Turnover (B+S):    ${buys_0 + sells_0:,.2f}")
print(f"One-sided Turnover min(B,S): ${min(buys_0, sells_0):,.2f}")
print(f"Real Slippage Cost:          ${sum(f.notional * f.slippage for f in res_e0['fill_log']):,.2f}")
print(f"Flawed V12 Slippage Metric:  ${sum(f.filled_qty * f.slippage for f in res_e0['fill_log']):,.4f}")

print("\n=== CANDIDATE A+E ===")
buys_ae = sum(f.notional for f in res_ae['fill_log'] if f.side == 'buy')
sells_ae = sum(f.notional for f in res_ae['fill_log'] if f.side == 'sell')
print(f"Total buys:                  ${buys_ae:,.2f}")
print(f"Total sells:                 ${sells_ae:,.2f}")
print(f"Two-sided Turnover (B+S):    ${buys_ae + sells_ae:,.2f}")
print(f"One-sided Turnover min(B,S): ${min(buys_ae, sells_ae):,.2f}")
print(f"Real Slippage Cost:          ${sum(f.notional * f.slippage for f in res_ae['fill_log']):,.2f}")
print(f"Flawed V12 Slippage Metric:  ${sum(f.filled_qty * f.slippage for f in res_ae['fill_log']):,.4f}")
