"""Verify generated leaderboards, preservation and checksums after reporting."""
import collections, csv, hashlib, json, math, pathlib, statistics, sys, time
ROOT=pathlib.Path(__file__).resolve().parents[2]
OUT=ROOT/'research/evidence/v30/v30_stage3f_20261025_tournament_v2'
def load(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def rows(p):
    with p.open(newline='',encoding='utf-8') as f: return list(csv.DictReader(f))
def main():
    begin=time.perf_counter(); failures=[]; checks=collections.Counter()
    def check(ok,label,detail=None):
        checks[label]+=1
        if not ok: failures.append({'check':label,'detail':detail})
    def close(x,y): return abs(float(x)-float(y))<=max(1e-9,abs(float(y))*1e-10)
    verification=load(OUT/'independent_verification_attempt_01.json')
    check(verification['status']=='PASS','independent journals verified')
    results=load(OUT/'reproducible_run_manifest.json'); base=[r for r in results if r['mode']=='base']; index={(r['candidate'],r['dataset']):r for r in base}
    registry=load(OUT/'inventory.json'); ids={r['id'] for r in registry}; n=len(ids)
    board=rows(OUT/'competition_return_leaderboard.csv'); check(len(board)==len(base),'full competition board accounting')
    for row in board:
        r=index[(row['candidate'],row['dataset'])]
        check(close(row['return'],r['metrics']['total_return']),'competition return recomputation',row['candidate'])
        check(close(row['max_drawdown'],r['metrics']['max_drawdown']),'competition drawdown recomputation',row['candidate'])
        check(row['source_sha256']==r['source_sha256'],'leaderboard source identity')
        check(row['classification']=='SYNTHETIC' and row['compliance']==r['compliance'],'leaderboard classification')
        check(int(row['sessions'])==r['actual_sessions'],'leaderboard session count')
    for dataset in {r['dataset'] for r in base}:
        group=[r for r in board if r['dataset']==dataset]
        check({r['candidate'] for r in group}==ids,'all candidates in each board',dataset)
        eligible=[r for r in group if r['compliance']=='PASS']
        eligible.sort(key=lambda r:-float(r['return']))
        for row in eligible:
            expected=1+sum(float(z['return'])>float(row['return'])+1e-12 for z in eligible)
            check(int(row['eligible_return_rank'])==expected,'tie-aware compliant rank',row['candidate'])
        for row in group:
            if row['compliance']!='PASS': check(row['eligible_return_rank']=='','noncompliant not ranked')
    for row in rows(OUT/'risk_adjusted_leaderboard.csv'):
        rr=[r for r in base if r['candidate']==row['candidate'] and r['dataset'].startswith('long_cycle')]
        for column,key in [('mean_sharpe','sharpe'),('mean_sortino','sortino'),('mean_cagr','cagr'),('mean_return','total_return')]:
            vals=[r['metrics'][key] for r in rr]
            check(row[column]=='' if any(v is None for v in vals) else close(row[column],statistics.mean(vals)),'risk board '+column,row['candidate'])
        check(close(row['worst_max_drawdown'],max(r['metrics']['max_drawdown'] for r in rr)),'risk board worst drawdown')
        check(int(row['sessions'])==sum(r['actual_sessions'] for r in rr),'risk board sessions')
    for row in rows(OUT/'capital_preservation_leaderboard.csv'):
        rr=[r for r in base if r['candidate']==row['candidate'] and not r['dataset'].startswith('long_cycle')]
        check(close(row['worst_max_drawdown'],max(r['metrics']['max_drawdown'] for r in rr)),'capital board drawdown')
        check(close(row['worst_total_return'],min(r['metrics']['total_return'] for r in rr)),'capital board return')
    for row in load(OUT/'synthetic_stress_robustness_leaderboard.json'):
        rr=[r for r in base if r['candidate']==row['candidate'] and not r['dataset'].startswith('long_cycle')]
        check(row['compliant_runs']==sum(r['compliance']=='PASS' for r in rr),'robustness compliant count')
        check(close(row['worst_total_return'],min(r['metrics']['total_return'] for r in rr)),'robustness worst return')
    manifest=load(OUT/'artifact_checksums.json')
    for entry in manifest['files']:
        p=ROOT/entry['path']; check(p.is_file() and p.stat().st_size==entry['bytes'] and sha(p)==entry['sha256'],'artifact checksum',entry['path'])
    for entry in load(OUT/'preservation_before.json'):
        check(sha(ROOT/entry['path'])==entry['sha256'],'historical preservation',entry['path'])
    summary=load(OUT/'completion_summary.json')
    check(summary['total_scored_sessions']==sum(r['actual_sessions'] for r in results),'reported session total')
    check(summary['total_simulations']==len(results),'reported simulation total')
    check(set((r['candidate'],r['dataset']) for r in base)==set(index),'run-key identity')
    report=ROOT/'GUARDIAN_ALPHA_V30_STAGE3F_ALL_VERSION_PAPER_TRADING_TOURNAMENT.md'
    reporttext=report.read_text(encoding='utf-8')
    for phrase in ['NOT ESTABLISHED AS BEST PROSPECTIVELY','real historical evaluation is BLOCKED','Stage3F stops here']:
        check(phrase in reporttext,'report scientific limitation',phrase)
    receipt={'status':'PASS' if not failures else 'FAILED','checks':dict(checks),'total_checks':sum(checks.values()),'failures':failures,
      'elapsed_seconds':time.perf_counter()-begin,'artifact_manifest_sha256':sha(OUT/'artifact_checksums.json'),'report_sha256':sha(report),
      'script_sha256':sha(pathlib.Path(__file__)),'note':'Receipt intentionally excluded from original manifest; closure manifest covers it without self-reference.'}
    with (OUT/'final_audit_receipt.json').open('x',encoding='utf-8') as f: json.dump(receipt,f,indent=2)
    closure={'self_excluded':True,'base_manifest':{'path':str((OUT/'artifact_checksums.json').relative_to(ROOT)),'sha256':sha(OUT/'artifact_checksums.json')},
      'final_receipt':{'path':str((OUT/'final_audit_receipt.json').relative_to(ROOT)),'sha256':sha(OUT/'final_audit_receipt.json')}}
    with (OUT/'closure_checksums.json').open('x',encoding='utf-8') as f: json.dump(closure,f,indent=2)
    print(json.dumps(receipt,indent=2)); return 0 if not failures else 1
if __name__=='__main__': sys.exit(main())
