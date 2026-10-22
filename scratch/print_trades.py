import sys, os
sys.path.insert(0, os.getcwd())
from scratch.reproduce_p0_accounting import trade_log

for t in trade_log:
    r_pnl = t.get('realized_pnl', 0.0)
    print(f"Day {t['day_idx']:2d} ({t['date']}) | {t['side'].upper():<4} {t['ticker']:<5} | Qty: {t['qty']:8.2f} | Px: ${t['price']:7.2f} | Fill: ${t['fill']:7.2f} | Realized: ${r_pnl:9.2f}")
