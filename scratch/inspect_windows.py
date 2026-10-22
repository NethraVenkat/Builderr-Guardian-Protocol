import gzip, json

data = json.loads(gzip.open("sample_regimes.json.gz", "rb").read())
for k, v in data.items():
    bars = v["bars"]
    all_d = sorted({r[0] for rows in bars.values() for r in rows})
    eval_d = [d for d in all_d if v["eval_start"] <= d <= v["eval_end"]]
    warmup_d = [d for d in all_d if d < v["eval_start"]]
    print(f"Regime: {k}")
    print(f"  eval_start: {v['eval_start']}, eval_end: {v['eval_end']}")
    print(f"  Total bar dates: {len(all_d)} ({all_d[0]} to {all_d[-1]})")
    print(f"  Warm-up dates: {len(warmup_d)} ({warmup_d[0]} to {warmup_d[-1]})")
    print(f"  Scored eval dates: {len(eval_d)} ({eval_d[0]} to {eval_d[-1]})")
