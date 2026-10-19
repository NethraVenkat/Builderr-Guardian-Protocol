import sys, types, json, math, time
# Create a minimal dummy yfinance module to satisfy live_runner import
dummy_yf = types.SimpleNamespace()

def dummy_download(*args, **kwargs):
    # Return None to simulate failure; live_runner will skip fetching bars
    return None

dummy_yf.download = dummy_download
# Insert dummy module into sys.modules under name 'yfinance'
sys.modules['yfinance'] = dummy_yf

# Now import live_runner without pulling real yfinance
import importlib.util
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location('live_runner', ROOT / 'live_runner.py')
live = importlib.util.module_from_spec(spec)
spec.loader.exec_module(live)

# Helper to create simple market_state with constant price bars
def make_market_state(tickers, price=100.0):
    from datetime import datetime, timedelta
    total_days = live.WARMUP_DAYS + live.EVAL_DAYS
    bars = []
    for i in range(total_days):
        ts = (datetime.utcnow() - timedelta(days=total_days - i)).strftime('%Y-%m-%d')
        bars.append({"ts": ts, "open": price, "high": price, "low": price, "close": price, "volume": 0})
    return {t: list(bars) for t in tickers}

# Dummy decide that proposes large buys for each ticker (to test limits)
def dummy_decide(market_state, portfolio_state, cash):
    orders = []
    for t in market_state.keys():
        orders.append({"ticker": t, "side": "buy", "quantity": 1_000_000})
    return orders

# Test Gross Exposure Limit Enforcement
ms = make_market_state(['TQQQ', 'SPY', 'AAPL'])
res = live.run_bot(dummy_decide, ms, entry_date=live.SCORE_START, enforce_limits=True)
print('Gross Exposure Test -> trades:', res['trades'], 'equity:', res['equity'])

# Test Concentration Limit (30% per ticker) – single ticker large order
ms2 = make_market_state(['AAPL'])
def decide_conc(market_state, portfolio_state, cash):
    return [{"ticker": "AAPL", "side": "buy", "quantity": 1_000_000}]
res2 = live.run_bot(decide_conc, ms2, entry_date=live.SCORE_START, enforce_limits=True)
print('Concentration Test -> trades:', res2['trades'], 'equity:', res2['equity'])

# Test Trade Rate Limit (50 trades per day) – many orders

def many_orders(market_state, portfolio_state, cash):
    return [{"ticker": "SPY", "side": "buy", "quantity": 1} for _ in range(120)]
ms3 = make_market_state(['SPY'])
res3 = live.run_bot(many_orders, ms3, entry_date=live.SCORE_START, enforce_limits=True)
print('Trade Rate Test -> trades executed:', res3['trades'])

# Hold duration cannot be simulated in daily runner – note
print('Hold duration enforcement cannot be verified in daily runner (LOCAL_ENFORCEMENT_NOT_VERIFIED)')

# Measure decision runtime (excluding import)
start = time.time()
live.run_bot(dummy_decide, ms, entry_date=live.SCORE_START, enforce_limits=False)
print('Decision runtime (seconds):', time.time() - start)

