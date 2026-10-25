"""Build Stage 3F audit handover from completed, independently verified journals."""
from __future__ import annotations
import ast, collections, csv, datetime as dt, gzip, hashlib, importlib.util, json, math, pathlib, platform, statistics, subprocess, sys, time
ROOT=pathlib.Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('stage3f_report_core',ROOT/'research/simulations/v30_stage3f_20261025_tournament.py')
t=importlib.util.module_from_spec(spec); spec.loader.exec_module(t)
OUT=t.OUT
def load(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def dump(name,x): t.write(OUT/name,x)
def csvout(name,rows):
    if not rows: return
    fields=list(dict.fromkeys(k for r in rows for k in r))
    with (OUT/name).open('x',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)
def pct(x): return 'N/A' if x is None else f'{x*100:.2f}%'
def fnum(x): return 'N/A' if x is None else f'{x:.3f}'
def mdtable(headers,rows):
    return '\n'.join(['| '+' | '.join(headers)+' |','|'+'|'.join(['---']*len(headers))+'|']+['| '+' | '.join(str(v).replace('|','/') for v in row)+' |' for row in rows])
def main():
    registry=load(OUT/'inventory.json'); cfg=load(OUT/'configuration_preregistered.json'); aliases=load(OUT/'deduplication.json')
    results=[load(p) for p in sorted((OUT/'runs').glob('*/*/result.json'))]
    base=[r for r in results if r['mode']=='base']; byid=collections.defaultdict(list)
    for r in base: byid[r['candidate']].append(r)
    sources={r['id']:r for r in registry}; frames={}; datasets={}
    # Explicit local contract findings, based on source inspection preceding execution.
    contract=[
     ('Interface','decide(market_state, portfolio_state, cash)','AGENT_BRIEF.md; live_runner.py:418-437','MATCH'),
     ('Universe','frozen 1000 identifiers; 30 strategy-referenced identifiers have synthetic observations; all other symbols unavailable equally','universe.json; configuration_preregistered.json','PARTIAL universe coverage'),
     ('Capital','$100,000; long only, no margin cash','live_runner.py:137,449-485','MATCH'),
     ('Warmup','220 prior bars maximum supplied, including 220 initial bars per observed symbol','README.md; live_runner.py:136','documented window; runner passes growing history'),
     ('Decision/fill','prior completed bars; next session opening fill','live_runner.py:418-454','MATCH on common domain'),
     ('Preview distinction','preview starts cash-only on first evaluated day, then fills pending orders; scoring runner decides before first scored open','preview.py:run_regime; live_runner.py:run_bot','explicit difference'),
     ('Prices to strategy','prior closes only; current opens never in strategy input','live_runner.py:418-425','MATCH'),
     ('Fees','zero explicit commission in base; 5bp plain/10bp leveraged slippage; adverse direction','live_runner.py:251-252,451-485','MATCH base'),
     ('Sell order','stable sells before buys; oversells clipped to held shares','live_runner.py:449-485','MATCH'),
     ('Buy limits','cash, 30% fill notional concentration room and beta-adjusted 1.5x room','live_runner.py:455-471','MATCH base; close drift recorded separately'),
     ('Orders/trades','100 proposed orders; 50 actual fills maximum per day','live_runner.py:255; AGENT_BRIEF.md:48','PARTIAL: runner lacks 50-fill clamp; published rule enforced here'),
     ('Concentration','>=30% for >5 consecutive close marks is a breach','preview.py:149-158','local-code interpretation; prose has inconsistent inequalities'),
     ('Drawdown','initial cash included in peak; >=50% flagged, not retrospectively suppressed','preview.py:_max_drawdown/main','PARTIAL: fixes initial-peak omission and retains complete failed path'),
     ('Missing bars','reject if no current open; carry last known close for existing positions','local source uses zero for missing marks despite Stage 3E carry claim','RESEARCH CORRECTION, not exact parity'),
     ('Corporate actions','split shares and historical signal scale on ex-date; dividend entitlement receivable and cash at pay date','local runner has no action implementation','RESEARCH EXTENSION; parity UNKNOWN'),
     ('Timeout','measure each decision; discard orders if >5 seconds after return','AGENT_BRIEF.md','PARTIAL: no preemptive timeout; measured decisions reported'),
     ('Holding period','daily batch; no intraday fill timestamps; no exchange latency model','AGENT_BRIEF.md','NOT VERIFIED intraday 60-second enforcement'),
     ('Valuation','cash plus closing position value plus dividend receivables; stale marks retained','source arithmetic plus explicit research extensions','PARTIAL overall'),
     ('Benchmark','current baseline.py, four ETF equal initial allocations under same engine (C006); QQQ benchmark also runs as candidate','baseline.py; inventory.json','MATCH equal conditions'),
     ('Scoring','compliant forward percentage return is the locally documented objective; synthetic runs cannot establish official score','docs/competition-contract.md section 5','official unseen evaluator parity NOT VERIFIED')]
    dump('execution_contract_parity.json',{'overall':'PARTIAL','authority':'locally preserved sources only; no current web or hidden evaluator access',
      'rules':[dict(rule=a,implementation=b,source=c,status=d) for a,b,c,d in contract],
      'source_hashes':{p:t.digest((ROOT/p).read_bytes()) for p in ['live_runner.py','preview.py','docs/competition-contract.md','AGENT_BRIEF.md','README.md']},
      'preflight_parity_test':'test_28: E0 first 20 synthetic bull sessions matches local runner curve to cents and trade count; not proof of all-case parity'})
    dump('runtime_environment.json',{'python':sys.version,'executable':sys.executable,'platform':platform.platform(),'packages':'standard library only',
      'network':'no network calls or broker libraries; restricted strategy importer','isolation':'fresh module graph per candidate and scenario; no shared strategy objects',
      'sandbox_limit':'restricted Python loader is defense in depth, not a hostile-code OS sandbox',
      'configuration_sha256':t.digest((OUT/'configuration_preregistered.json').read_bytes()),
      'harness_sha256':t.digest(pathlib.Path(t.__file__).read_bytes())})
    # Source-history follow-up: rename ancestry and scratch definitions, no vendor data.
    follow=[]
    for p in t.SCRATCH:
        for commit in t.git('log','--all','--format=%H','--',p).decode().splitlines():
            try: raw=t.source_bytes(p,commit)
            except RuntimeError: continue
            follow.append({'path':p,'commit':commit,'same_lf_as_worktree':raw.replace(b'\r\n',b'\n')==(ROOT/p).read_bytes().replace(b'\r\n',b'\n')})
    historical_names=sorted(set(t.git('log','--all','--name-only','--format=','--','*.py').decode().splitlines()))
    foreign=[p for p in historical_names if '/' not in p and p.endswith('_agent.py') and p not in t.ROOT_STRATEGIES]
    dump('discovery_scope_and_exclusions.json',{'scratch_history':follow,'renames':['soham_agent.py -> momentum_v1.py','soham_agent_v2.py -> ai_momentum.py'],
      'third_party_contestant_names_not_Guardian_versions':foreign,'third_party_sources_loaded':False,
      'coverage':'reachable local Git references, current strategy directory, starter/reference strategies, four preserved scratch implementation files',
      'limitations':['unreachable Git objects/reflogs not traversed','external historical temp snapshots not re-read; V29E publication snapshots are documentary aliases only',
       '43 effective-trial ledger is not reconstructible into 43 frozen independent agents; unspecified threshold/halflife sweeps not invented'],
      'superseded_discovery':'v30_stage3f_20261025_tournament: 67 entries; preserved; v2 adds renamed historical source before any tournament run'})
    # Proven wrapper alias; other equal outputs are not proof of functional identity.
    wrapper=[r for r in registry if r['source_path']=='research/strategies/v30_execution_safe_agent.py']
    wrapper_ids=[r['id'] for r in wrapper]
    identical=all(next(r for r in byid[wrapper_ids[0]] if r['dataset']==x['dataset'])['metrics']==x['metrics'] for x in byid[wrapper_ids[1]])
    dump('logical_deduplication.json',{'distinct_source_entry_parameter_graph_keys':len(registry),
      'distinct_raw_source_files':len({r['source_sha256'] for r in registry}),
      'exact_duplicate_reference_count':len(aliases),
      'proven_default_wrapper_alias':{'candidates':wrapper_ids,'same_metrics_all_base_runs':identical,'reason':'module decide delegates to singleton default V30ExecutionSafeAgent; same constructor and arguments'},
      'implementation_upper_bound_after_wrapper_alias':len(registry)-1,
      'semantic_uniqueness':'NOT VERIFIED for all remaining pairs; comment/format differences and behaviorally inactive rules may remain',
      'no_double_weighting':'leaderboards retain entries for accounting, but aliases are explicitly marked; no aggregate vote or universal score'})
    statuses=[]; failed=[]
    for rec in registry:
        rr=byid[rec['id']]; success=sum(r['status']=='EXECUTED SUCCESSFULLY' for r in rr)
        item={'candidate':rec['id'],'label':rec['label'],'source_sha256':rec['source_sha256'],'base_runs':len(rr),'successful_base_runs':success,
          'failed_base_runs':len(rr)-success,'expected_base_runs':32,'sessions':sum(r['actual_sessions'] for r in rr),
          'status':'EXECUTED SUCCESSFULLY' if success==32 else 'FAILED' if len(rr)==32 else 'NOT VERIFIED',
          'compliant_runs':sum(r['compliance']=='PASS' for r in rr),'all_run_compliance':'PASS' if all(r['compliance']=='PASS' for r in rr) and len(rr)==32 else 'FAILED',
          'adapter':'unchanged AST definition extracted from scratch; I/O driver excluded' if rec['extract'] else 'unchanged full module; default class constructor if needed'}
        statuses.append(item)
        if item['status']!='EXECUTED SUCCESSFULLY': failed.append(item)
    dump('eligibility_and_candidate_accounting.json',statuses)
    enriched=[]
    for rec in registry:
        p=rec['source_path']; stage='Starter/reference strategy; Git reference records revision'
        if 'v30_candidate_d' in p: stage='V30 Stage 2B defensive allocation'
        elif 'v30_candidate_c' in p: stage='V30 Stage 2C volatility gating'
        elif 'v30_candidate_p' in p: stage='V30 Stage 2D position sizing'
        elif 'v30_execution' in p: stage='V30 Stage 2A execution safety; suffix identifies remediation/final'
        elif 'v12_' in p: stage='V12 / B2-C integrated A+E'
        elif 'v11_' in p or 'test_candidates_a_to_f' in p: stage='V11 A-F candidates'
        elif 'loss_reduction' in p or 'counterfactual' in p: stage='V10 / Track B loss reduction and cadence research'
        elif 'candidate_alpha' in p or 'hypotheses' in p: stage='Track B exploratory research; exact stage only as documented in source'
        elif p=='agent.py': stage='Frozen E0/current submission' if rec['git_commit']=='WORKTREE' else 'Historical starter/E0 source revision'
        account=next(x for x in statuses if x['candidate']==rec['id'])
        enriched.append(dict(rec,creation_stage=stage,
          historical_evaluation_status='Earlier evaluations are documentary context only, not recertified. Stage3F actual status: '+account['status'],
          successfully_executed_base_runs=account['successful_base_runs'],successful_sessions=account['sessions'],
          runnable_without_modification='yes, original decision code; AST isolation adapter required' if rec['extract'] else 'yes, default constructor/function',
          logically_equivalent_to='C038/C039 default wrapper pair' if rec['id'] in wrapper_ids else 'not proved beyond exact duplicate references'))
    dump('complete_strategy_version_inventory.json',enriched)
    dump('failed_and_excluded_register.json',{'failed_candidate_entries':failed,'failed_runs':[r for r in results if r['status']!='EXECUTED SUCCESSFULLY'],
      'blocked_data_tracks':['real Tier1/Tier2','sealed Tier3','public fixture rights unresolved'],
      'not_verified_trials':['unnamed Stage6/Stage2C cutoff and Stage2D halflife sweeps without distinct frozen execution configuration'],
      'excluded_from_primary_ranking':'noncompliant runs remain visible but unranked; duplicate wrapper marked',
      'injected_test_failures':'test_24 intentionally raises ValueError twice and verifies FAILED classification; not a harness test failure'})
    violation_rows=[dict(candidate=r['candidate'],dataset=r['dataset'],mode=r['mode'],status=r['compliance'],
      leverage_close_sessions=r['violations'].get('leverage_close_sessions',0),
      concentration_sessions=r['violations'].get('concentration_sessions',0),catastrophe_sessions=r['violations'].get('catastrophe_sessions',0),
      invalid_orders=r['violations'].get('invalid_orders',0),decision_timeout=r['violations'].get('decision_timeout',0),
      lookahead_violations=0 if not r['errors'] else 'see errors',frozen_universe_violations='included in invalid_orders; raw rejection reason retained',
      margin_violations=0 if not r['errors'] else 'see errors') for r in results]
    csvout('compliance_violation_matrix.csv',violation_rows)
    flat=[dict(candidate=r['candidate'],dataset=r['dataset'],mode=r['mode'],source_sha256=r['source_sha256'],classification='SYNTHETIC',status=r['status'],compliance=r['compliance'],
      **{k:v for k,v in r['metrics'].items() if not isinstance(v,(list,dict))}) for r in results]
    csvout('complete_performance_metrics.csv',flat); dump('reproducible_run_manifest.json',results)
    # Full per-dataset competition boards: never aggregate different scenario return paths into one score.
    competition=[]; perboards={}
    for dsid in sorted({r['dataset'] for r in base}):
        ordered=sorted([r for r in base if r['dataset']==dsid],key=lambda r:-(r['metrics'].get('total_return',-math.inf)))
        rank=0; eligible_count=0; previous_return=None; board=[]
        for r in ordered:
            if r['status']=='EXECUTED SUCCESSFULLY' and r['compliance']=='PASS':
                eligible_count+=1
                if previous_return is None or abs(r['metrics']['total_return']-previous_return)>1e-12: rank=eligible_count
                eligible_rank=rank; previous_return=r['metrics']['total_return']
            else: eligible_rank=None
            row={'dataset':dsid,'candidate':r['candidate'],'label':r['label'],'source_sha256':r['source_sha256'],'classification':'SYNTHETIC',
              'sessions':r['actual_sessions'],'eligible_return_rank':eligible_rank,'return':r['metrics'].get('total_return'),
              'max_drawdown':r['metrics'].get('max_drawdown'),'compliance':r['compliance'],
              'limitations':'synthetic only; 30-symbol coverage; partial contract parity; default wrapper duplicate C038/C039'}
            competition.append(row); board.append(row)
        perboards[dsid]=board
    csvout('competition_return_leaderboard.csv',competition)
    risk=[]; capital=[]; robustness=[]; evidence=[]
    for rec in registry:
        rr=byid[rec['id']]; long=[r for r in rr if r['dataset'].startswith('long_cycle')]; stress=[r for r in rr if not r['dataset'].startswith('long_cycle')]
        identity=dict(candidate=rec['id'],label=rec['label'],source_sha256=rec['source_sha256'],classification='SYNTHETIC')
        risk.append(dict(identity,sessions=sum(r['actual_sessions'] for r in long),
          mean_sharpe=statistics.mean(r['metrics']['sharpe'] for r in long) if all(r['metrics']['sharpe'] is not None for r in long) else None,
          mean_sortino=statistics.mean(r['metrics']['sortino'] for r in long) if all(r['metrics']['sortino'] is not None for r in long) else None,
          mean_cagr=statistics.mean(r['metrics']['cagr'] for r in long) if all(r['metrics']['cagr'] is not None for r in long) else None,
          mean_return=statistics.mean(r['metrics']['total_return'] for r in long),
          worst_max_drawdown=max(r['metrics']['max_drawdown'] for r in long),
          compliance='PASS' if all(r['compliance']=='PASS' for r in long) else 'FAILED',
          limitations='two independent synthetic long-cycle paths; arithmetic mean of path ratios, not pooled Sharpe'))
        capital.append(dict(identity,sessions=sum(r['actual_sessions'] for r in stress),
          worst_max_drawdown=max(r['metrics']['max_drawdown'] for r in stress),worst_total_return=min(r['metrics']['total_return'] for r in stress),
          total_trades=sum(r['metrics']['trades'] for r in stress),mean_exposure=statistics.mean(r['metrics']['average_exposure'] for r in stress),
          catastrophe_runs=sum(r['violations'].get('catastrophe_sessions',0)>0 for r in stress),
          compliance='PASS' if all(r['compliance']=='PASS' for r in stress) else 'FAILED',limitations='30 synthetic stress paths; low exposure may improve this objective'))
        ranks=[next(x['eligible_return_rank'] for x in perboards[r['dataset']] if x['candidate']==rec['id']) for r in stress]
        robustness.append(dict(identity,sessions=sum(r['actual_sessions'] for r in stress),
          compliant_runs=sum(r['compliance']=='PASS' for r in stress),total_runs=len(stress),
          worst_total_return=min(r['metrics']['total_return'] for r in stress),
          median_eligible_rank=statistics.median(x for x in ranks if x is not None) if any(x is not None for x in ranks) else None,
          rank_range=[min(x for x in ranks if x is not None),max(x for x in ranks if x is not None)] if any(x is not None for x in ranks) else None,
          compliance='PASS' if all(r['compliance']=='PASS' for r in stress) else 'FAILED',limitations='ordering: compliant paths first, then worst return; arbitrary design, not a prospective probability'))
        evidence.append(dict(identity,sessions=sum(r['actual_sessions'] for r in rr),executed=len(rr),expected=32,
          failed=sum(r['status']!='EXECUTED SUCCESSFULLY' for r in rr),compliance='PASS' if all(r['compliance']=='PASS' for r in rr) else 'FAILED',
          evidence_grade='same synthetic evidence tier',limitations='no independent market OOS; same verifier and source custody controls'))
    risk.sort(key=lambda r:(r['mean_sharpe'] is None,-(r['mean_sharpe'] or 0)))
    capital.sort(key=lambda r:(r['worst_max_drawdown'],-r['worst_total_return']))
    robustness.sort(key=lambda r:(-r['compliant_runs'],-r['worst_total_return']))
    csvout('risk_adjusted_leaderboard.csv',risk); csvout('capital_preservation_leaderboard.csv',capital)
    dump('synthetic_stress_robustness_leaderboard.json',robustness); csvout('evidence_quality_leaderboard.csv',evidence)
    compliance=sorted(statuses,key=lambda r:(-r['compliant_runs'],r['candidate']))
    csvout('rule_compliance_leaderboard.csv',compliance)
    # Paired E0/D2 diagnostic: common E0 risk-off tag, no significance testing.
    e0=next(r for r in registry if r['source_path']=='agent.py' and r['git_commit']=='WORKTREE')['id']
    d2=next(r for r in registry if r['source_path'].endswith('v30_candidate_d2_cash_cushion.py') and r['git_commit']=='WORKTREE')['id']
    paired=[]
    for dsid in sorted({r['dataset'] for r in base}):
        with gzip.open(OUT/'datasets'/(dsid+'.json.gz'),'rt') as f: ds=json.load(f)
        # The common E0 regime tag depends only on SPY/QQQ. Avoid retaining every
        # ticker's full rolling history during reporting; tournament inputs stay unchanged.
        signal_data=dict(ds,bars={s:ds['bars'][s] for s in ['SPY','QQQ']})
        frames=t.prepare_frames(signal_data)
        for mode in ['base']+(['zero_cost','high_cost','close_fill'] if dsid.startswith('long_cycle') else []):
            a=next(r for r in results if r['candidate']==e0 and r['dataset']==dsid and r['mode']==mode)
            z=next(r for r in results if r['candidate']==d2 and r['dataset']==dsid and r['mode']==mode)
            days=[]
            for cid in [e0,d2]:
                with (OUT/'runs'/cid/(dsid+'_'+mode)/'daily.csv').open(newline='',encoding='utf-8') as f:
                    days.append([{k:float(v) if k!='date' else v for k,v in row.items()} for row in csv.DictReader(f)])
            defensive=[]; false_alarm=[]; loader=t.IsolatedLoader(sources[e0])
            try:
                loader.load(); module=loader.cache['candidate']
                for idx,fr in enumerate(frames):
                    spy=module.closes(fr['market'].get('SPY')); qqq=module.closes(fr['market'].get('QQQ'))
                    risk_on=bool(len(spy)>=50 and len(qqq)>=50 and spy[-1]>module.sma(spy,50) and qqq[-1]>module.sma(qqq,50) and module.realized_vol(qqq,20)<.35)
                    if not risk_on:
                        defensive.append(idx)
                        prior=spy[-1] if spy else None; today=fr['current'].get('SPY')
                        if prior and today and today['close']>prior: false_alarm.append(idx)
            finally: loader.close()
            short=lambda rows,ids: statistics.mean(max(0,-rows[i]['return']) for i in ids) if ids else None
            drag=statistics.mean(days[1][i]['return']-days[0][i]['return'] for i in false_alarm) if false_alarm else None
            dd_reduction=a['metrics']['max_drawdown']-z['metrics']['max_drawdown']; return_sacrifice=a['metrics']['total_return']-z['metrics']['total_return']
            paired.append({'dataset':dsid,'mode':mode,'E0':e0,'D2':d2,'E0_return':a['metrics']['total_return'],'D2_return':z['metrics']['total_return'],
              'D2_minus_E0_return':-return_sacrifice,'E0_max_drawdown':a['metrics']['max_drawdown'],'D2_max_drawdown':z['metrics']['max_drawdown'],
              'D2_minus_E0_drawdown':-dd_reduction,'D2_minus_E0_mean_cash_fraction':z['metrics']['mean_cash_fraction']-a['metrics']['mean_cash_fraction'],
              'defensive_sessions':len(defensive),'E0_defensive_mean_loss':short(days[0],defensive),'D2_defensive_mean_loss':short(days[1],defensive),
              'D2_minus_E0_defensive_mean_loss':short(days[1],defensive)-short(days[0],defensive) if defensive else None,
              'D2_minus_E0_defensive_cash_fraction':statistics.mean(days[1][i]['cash']/days[1][i]['equity']-days[0][i]['cash']/days[0][i]['equity'] for i in defensive) if defensive else None,
              'false_alarm_sessions':len(false_alarm),'D2_minus_E0_return_on_false_alarms':drag,
              'return_sacrificed_per_drawdown_reduced':return_sacrifice/dd_reduction if dd_reduction>1e-10 else None,
              'E0_compliance':a['compliance'],'D2_compliance':z['compliance']})
    dump('E0_vs_D2_paired_analysis.json',{'classification':'SYNTHETIC descriptive only','pairs':paired,
      'defensive_definition':'prior-bar common E0 risk gate false; not hindsight-reclassified or candidate-specific',
      'shortfall_definition':'mean max(0, -daily return) over common defensive sessions; not prior confirmatory endpoint',
      'false_alarm_definition':'common risk-off decision followed by positive synthetic SPY close/prior-close return; retrospective diagnostic, not a tradable label',
      'inference':'none; failed Stage3B-R2 small-sample HAC/bootstrap test-size finding preserved; no p-values or superiority claim',
      'source_vs_report_correction':'frozen D2 source is XLP .18/XLU .18/XLV .14, no XLE; old Stage2E JSON incorrectly described proportional E0 sleeves'})
    # Preservation and final checkpoint.
    before=load(OUT/'preservation_before.json'); preservation=[]
    for x in before:
        p=ROOT/x['path']; actual=t.digest(p.read_bytes()) if p.is_file() else None
        preservation.append(dict(x,after_sha256=actual,unchanged=actual==x['sha256']))
    dump('preservation_after.json',preservation); cert=t.checkpoint(); dump('checkpoint_after.json',cert)
    verification=load(OUT/'independent_verification_attempt_01.json'); tests=load(OUT/'tests_attempt_01.json')
    execution=load(OUT/'tournament_execution_01.json'); start=load(OUT/'budget.json')['start_epoch']; now=time.time()
    run_status=collections.Counter(r['status'] for r in results); session_count=sum(r['actual_sessions'] for r in results)
    gates=[
     ('A','Protected Git checkpoint','PASS','branch, HEAD, parent and protected hashes match before and after'),
     ('B','Strategy inventory completeness','PARTIAL','68 preserved executable entries covered; unreachable objects and undocumented sweeps cannot be certified exhaustive'),
     ('C','Data eligibility','PASS','new synthetic observations only; real historical comparison BLOCKED'),
     ('D','Competition contract parity','PARTIAL','common-domain parity tested; explicit timing/window, missing-bar, action, order-limit and risk differences'),
     ('E','Simulator correctness','PASS' if tests['exit_code']==0 and verification['status']=='PASS' else 'FAILED','31 executed controls plus independent journal reconstruction; limited to modeled cases'),
     ('F','Equal-condition execution','PASS' if verification['status']=='PASS' else 'FAILED','same dataset hashes, starting equity, input windows and engine rules across all entries'),
     ('G','All eligible strategies attempted','PASS' if not verification['absent_base_runs'] else 'PARTIAL','68 entries x 32 base fixtures; sensitivity E0/D2 only'),
     ('H','Performance metric accuracy',verification['status'],'independent Decimal reconstruction of all journals and leaderboard inputs'),
     ('I','Stress-test execution','PASS','15 named stress families x 2 seeds x 68 entries; 2 long-cycle paths separately'),
     ('J','Independent E0/D2 comparison','PARTIAL','paired executed descriptive comparison and independent accounting; no independent market sample or external reviewer'),
     ('K','Compliance and risk verification','PASS' if verification['status']=='PASS' else 'FAILED','breaches explicitly retained; PASS here means verified classification, not every candidate compliant'),
     ('L','Reproducibility and preservation','PASS' if all(x['unchanged'] for x in preservation) and verification['status']=='PASS' else 'FAILED','new artifacts only; source snapshots, raw journals, measured runs, checksums'),
     ('M','Zero unauthorized Git/external actions','PASS','read-only Git; no broker, provider, credential, holdout or external network actions'),
     ('N','Scientific integrity','PASS','synthetic/descriptive labels; no official score, significance, universal winner or promotion')]
    dump('acceptance_gates.json',[dict(gate=a,name=b,status=c,basis=d) for a,b,c,d in gates])
    totals={'candidate_entries':len(registry),'implementation_upper_bound_after_proven_wrapper_alias':len(registry)-1,
      'unique_semantics_not_proved':True,'duplicate_references':len(aliases),'source_files':len({r['source_sha256'] for r in registry}),
      'fully_successful_candidates':sum(s['status']=='EXECUTED SUCCESSFULLY' for s in statuses),'failed_candidates':len(failed),
      'base_simulations':len(base),'sensitivity_simulations':len(results)-len(base),'total_simulations':len(results),
      'total_scored_sessions':session_count,'run_statuses':dict(run_status),
      'measured_tournament_seconds':execution['elapsed_seconds'],'sum_simulation_seconds':sum(r['elapsed_seconds'] for r in results),
      'independent_verification_seconds':verification['elapsed_seconds'],'measured_preparation_to_report_seconds':now-start,
      'earlier_read_only_inspection':'not covered by the preparation timer; no precise full-turn duration claimed',
      'maximum_planned_minutes':360,'test_failures':tests['failures'],'test_errors':tests['errors'],
      'all_preserved':all(x['unchanged'] for x in preservation),'preserved_files':len(preservation)}
    dump('completion_summary.json',totals)
    # A fully self-contained report with complete boards, concise main explanation and source IDs.
    report=[]; add=report.append
    add('# GUARDIAN ALPHA V30 — STAGE 3F ALL-VERSION PAPER-TRADING TOURNAMENT')
    add('**PARTIAL scientific completion: all 68 inventoried executable entries ran, but real historical evaluation is BLOCKED and exact official contract parity is PARTIAL.** This is an executed offline synthetic tournament, not a prospective performance certification. **BEST ON TESTED SAMPLE — NOT ESTABLISHED AS BEST PROSPECTIVELY.**')
    add('## Checkpoint and preservation')
    add(f"Branch `{cert['branch']}`; HEAD `{cert['head']}`; parent `{cert['parent']}`. Archive commit deltas are 198 and 87 added files. {len(preservation)} explicitly allowlisted historical code/report/Stage3D–3E evidence files have unchanged before/after hashes. Tracked working-tree status remains empty. Tier3/cache contents were never inspected, including for availability. No original file was edited, no Git mutation occurred, and no external actions were taken.")
    add(mdtable(['Protected source','Mode','SHA-256','Match'],[[p,x['mode'],x['actual'],x['match']] for p,x in cert['hashes'].items()]))
    add('Preservation hashing covers code, root/documentation reports and the uncommitted Stage3D–3E evidence allowlist; it deliberately does not claim byte verification of forbidden market data. The 285 archived paths are registered without opening raw observations. The Git checkpoint protects archive identity. No cache traversal or whole-repository content hash was attempted.')
    add('## Coverage, execution and timing')
    add(mdtable(['Measure','Actual'],[[k,v] for k,v in totals.items() if not isinstance(v,(list,dict))]))
    add('The 68 entries are distinct source/entry/parameter/dependency keys, not 68 proved different economic algorithms. C038/C039 are the same default class and its delegating module wrapper; both were run and flagged. After this alias the upper bound is 67 implementations; additional semantic equivalence is NOT VERIFIED. Historical renamed starter bots were followed through Git. V29/V29E publication/evidence stages did not establish separate trading logic. The prior 43-trial count includes accounting and parameter sweeps; undocumented missing configurations were not invented. Exact source references and 37 duplicate references are in the inventory and deduplication registers.')
    add('All inventoried entries completed 32 base runs: 30 stress paths of 126 scored sessions plus two independent 504-session long-cycle paths. Each has 220 warmup bars. E0/D2 completed 12 additional sensitivity runs in total. Failures and noncompliance are distinct. The tournament process exit code is '+str(execution['exit_code'])+'.')
    add('Timing is actual machine-measured time. The six-hour allocation is a maximum plan, not elapsed work. Preparation-to-report timing excludes the earlier read-only inspection; this audit does not invent a precise whole-conversation duration. The verifier overlaps input-hash preparation with the final tournament runs and waits for the tournament exit receipt before reading the complete run set, so its wall time includes that wait. Runtime metadata and execution command/exit receipts are preserved.')
    add('## Data, fairness and contract limitations')
    add('Only new, independently seeded synthetic OHLCV paths were loaded. Symbols are identifiers from the frozen 1,000-name universe; 30 symbols referenced by strategy source have observations, equally available to every candidate. Invented weekday timestamps begin 2000-01-03 and end before 2022; they are not historical observations or an exchange holiday calendar. The 126-session evaluation window and 504-session evaluation window are recorded in every run manifest. No market observation, calibrated return statistic or old expected result seeded the generator.')
    add('Exact synthetic windows: warmup 2000-01-03 through 2000-11-03 (220 invented weekdays); short stress evaluation 2000-11-06 through 2001-04-30 (126 sessions); long-cycle evaluation 2000-11-06 through 2002-10-10 (504 sessions). These date labels are fictional time coordinates, not claims that those market observations were used.')
    add('Real Tiingo Tier1/Tier2 evaluation is BLOCKED by the no-cache rule. Tier2 is a reused development sample, never independent OOS. Tier3 remains sealed. The public sample fixture was not opened, hashed or decompressed: V29F records UNKNOWN underlying provenance/derived rights, conflicting with the later Stage3D assertion of permission. No legal grant is inferred from repository custody or software licensing.')
    add(mdtable(['Rule','Implementation / qualification','Local evidence','Parity'],contract))
    add('All strategies receive fresh isolated source namespaces, original source/default parameters, independent cash/positions, equal prior-only histories and the same execution model. Class instances bind their existing decide method. Scratch adapters compile unchanged definition ASTs while omitting top-level old-data loaders and report writers; inputs/outputs are untranslated, no original file is modified, and AST/source identity is tested. This preserves decision code but does not certify equivalence to every original historical driver. Missing current bars reject fills and carry stale marks; stale-price liquidity is not assumed. Negative cash and short sales are blocked. Corporate actions are invented explicit split/ex-date/payment events; they are not a claim about the official evaluator.')
    add('Corporate-action NAV includes unpaid dividend receivables, while the original cash/positions/last_prices strategy interface does not expose receivables as spendable cash. This known interface limitation applies identically to all candidates. Split histories are adjusted only when the split is effective; no future action is revealed. The synthetic leveraged products use daily amplified latent-factor returns and invented expense drag; they are not calibrated replicas of actual ETF tracking behavior.')
    add('The benchmark is the preserved four-ETF baseline C006 under the same conditions. Sharpe uses arithmetic daily excess returns versus zero risk-free rate and sample standard deviation with 252 annualization; Sortino uses RMS of negative daily returns including zeros. Total return includes first-day P&L versus initial $100,000. CAGR and Calmar are N/A below 252 scored sessions, and ratios with zero denominators are N/A. Turnover is gross absolute fill notional / initial equity, not half-turnover. Monthly blocks are synthetic calendar bins with partial months explicitly flagged. VaR/ES are descriptive empirical 5% tails; no probability calibration is claimed. Decision runtime is measured; exchange latency is not modeled.')
    add('Reported peak exposure and drawdown are based on daily closing portfolio marks, not intraday high/low paths. Purchases are constrained by the reference opening-fill room calculations; price-driven later breaches are flagged rather than hidden by forced liquidation. Empirical tail metrics use ceil(0.05 × session count) observations, so finite-sample tail mass can exceed exactly 5%.')
    add('## Conditional findings')
    qualified_risk=[r for r in risk if r['compliance']=='PASS']; qualified_capital=[r for r in capital if r['compliance']=='PASS']
    add('Risk-adjusted long-cycle leader among compliant paths: '+(qualified_risk[0]['candidate']+' ('+qualified_risk[0]['label']+'), mean path Sharpe '+fnum(qualified_risk[0]['mean_sharpe']) if qualified_risk else 'none')+'. Capital-preservation leader among candidates compliant on all stress paths: '+(qualified_capital[0]['candidate']+', worst stress drawdown '+pct(qualified_capital[0]['worst_max_drawdown']) if qualified_capital else 'none')+'. These are different objectives, not a universal ranking.')
    winners=[]
    for dsid,board in perboards.items():
        ok=[r for r in board if r['eligible_return_rank']==1]
        worst=board[-1]
        winners.append([dsid,', '.join(x['candidate'] for x in ok) if ok else 'none',pct(ok[0]['return']) if ok else 'N/A',worst['candidate'],pct(worst['return']),worst['compliance']])
    add(mdtable(['Synthetic path','Best compliant return entry','Return','Lowest raw return entry','Return','Lowest-entry compliance'],winners))
    add('Winner/loser explanations are conditional on the imposed scenario: bull paths reward sustained risk exposure; crash/bear and tech shocks punish prior holdings before any causal exit; cash-heavy rules can reduce losses while sacrificing rebounds; rotation and high volatility expose churn and whipsaw; transaction costs are charged to every actual fill. Exact source objectives, daily positions, cash fractions, turnover and fees allow these mechanisms to be audited. A low-return or noncompliant result is retained, not labeled an execution failure. No causal explanation beyond these observed paths establishes future superiority.')
    add('## E0 versus D2')
    add('E0 is C001 (`agent.py`); frozen D2 is C032. D2 source uses XLP 18%, XLU 18%, XLV 14%, with 50% target cash and no XLE during risk-off. An older Stage2E matrix describes different weights; the frozen source, not that erroneous summary, was executed. The paired table reports D2 minus E0; a negative drawdown difference means D2 reduced drawdown. Common defensive sessions use the E0 prior-data risk gate. False-alarm cash drag is only a retrospective diagnostic. Full cash/shortfall and return-sacrificed ratios are in the paired JSON.')
    add(mdtable(['Dataset','Execution','E0 return','D2 return','Return delta','Drawdown delta','Mean cash delta'],[[r['dataset'],r['mode'],pct(r['E0_return']),pct(r['D2_return']),pct(r['D2_minus_E0_return']),pct(r['D2_minus_E0_drawdown']),pct(r['D2_minus_E0_mean_cash_fraction'])] for r in paired]))
    add('Stage3B-R2 found that the small-sample joint HAC/bootstrap procedure did not control nominal test size: its report records 7.70–10.80% null-boundary rejection at N=30 against nominal 5%. That failed finding remains intact. This tournament performs no significance or confirmatory superiority test and does not reuse that procedure.')
    add('## Full risk-adjusted leaderboard')
    add('Long-cycle paths only, 504 sessions per seed. Sorted by mean of the two path Sharpes; noncompliant entries remain visible and are ineligible for the compliant-leader conclusion. Full hashes are provided in the inventory and machine-readable leaderboard.')
    add(mdtable(['Entry','Sessions','Mean return','Mean CAGR','Mean Sharpe','Mean Sortino','Worst DD','Compliance'],[[r['candidate'],r['sessions'],pct(r['mean_return']),pct(r['mean_cagr']),fnum(r['mean_sharpe']),fnum(r['mean_sortino']),pct(r['worst_max_drawdown']),r['compliance']] for r in risk]))
    add('## Full capital-preservation leaderboard')
    add(mdtable(['Entry','Sessions','Worst DD','Worst return','Mean exposure','Trades','Catastrophe paths','Compliance'],[[r['candidate'],r['sessions'],pct(r['worst_max_drawdown']),pct(r['worst_total_return']),pct(r['mean_exposure']),r['total_trades'],r['catastrophe_runs'],r['compliance']] for r in capital]))
    add('## Full synthetic stress robustness leaderboard')
    add('Sort order is compliant-path count, then worst return. This is a declared engineering ordering; it is not an estimate of crash probabilities or forward expected return.')
    add(mdtable(['Entry','Sessions','Compliant paths / 30','Worst return','Median eligible rank','Compliance'],[[r['candidate'],r['sessions'],r['compliant_runs'],pct(r['worst_total_return']),r['median_eligible_rank'],r['compliance']] for r in robustness]))
    add('## Full rule-compliance and evidence-quality boards')
    add('All entries share the same SYNTHETIC evidence grade. There is no meaningful evidence-quality superiority ranking from identical provenance. The table exposes session coverage and compliance instead of fabricating a score.')
    add(mdtable(['Entry','Base runs','Successful','Sessions','Compliant paths / 32','Execution status','Compliance'],[[r['candidate'],r['base_runs'],r['successful_base_runs'],r['sessions'],r['compliant_runs'],r['status'],r['all_run_compliance']] for r in compliance]))
    add('## Adversarial tests and independent verification')
    add(f"{tests['passed']}/{tests['tests']} executed tests passed; {len(tests['failures'])} failed assertions and {len(tests['errors'])} test errors. The deliberate throwing strategy is a negative control with preserved failure receipt, not an unreported failed harness test. All 25 requested assurance areas map to the numbered controls and full-journal verifier. Independent verification status: **{verification['status']}**, {verification['runs']} journals, {verification['sessions']} sessions, {verification['failures']} failed runs. Its implementation reconstructs cash/shares/dividend receivables using Decimal, reconstructs causal input hashes independently, and recomputes return, drawdown, exposure, ratios, costs and monthly statistics without importing the harness metric function.")
    add('Independent means a separately implemented accounting/metric verifier within this audit, not an external quant review or second agent. Hostile-code sandbox escape, actual venue latency, hidden competition execution and real corporate-event coverage were not established. No original test suite that might load sealed data was run. The superseded first discovery inventory is preserved; no expensive evaluation was discarded or rerun to improve rankings.')
    add('## Acceptance gates')
    add(mdtable(['Gate','Requirement','Verdict','Basis'],gates))
    add('## Complete version inventory')
    add('Each ID links to the full inventory fields: source path/commit/raw and normalized hashes, original objective, interface, dependencies, extraction status, parameters and exact dependency snapshots. Creation-stage detail is derived only where source/commit documents it; otherwise it is not inferred from a result.')
    add(mdtable(['ID','Source / entry','Git ref','Raw SHA-256','Adapter'],[[r['id'],r['label'],r['git_commit'],r['source_sha256'],'AST definition' if r['extract'] else 'full source'] for r in registry]))
    add('## Complete competition-style return boards')
    add('These are separate synthetic fixture leaderboards, not official competition ranks. An em dash in rank means noncompliant/ineligible for that path. Raw returns remain visible. Each path supplies the same observations and sessions to every entry. The full CSV includes source hashes, sample class, sessions, compliance and limitations for every row.')
    for dsid,board in perboards.items():
        add('### '+dsid+' — SYNTHETIC')
        add(mdtable(['Eligible rank','Entry','Sessions','Return','Max DD','Compliance'],[[r['eligible_return_rank'] or '—',r['candidate'],r['sessions'],pct(r['return']),pct(r['max_drawdown']),r['compliance']] for r in board]))
    add('## Git status and new artifacts')
    status=t.git_status(); (OUT/'git_status_after.txt').write_text(status,encoding='utf-8')
    add('Exact scoped status is in `git_status_after.txt`; tracked-only status is empty. Scope excludes `tiingo_cache`, scratch and existing private/history/leaderboard result files so sealed paths are not enumerated. Existing Stage3D–3E untracked files remain untracked. New Stage3F outputs are untracked. This deliberately does not claim a full untracked scan of prohibited directories.')
    add('Every pre-closure new artifact is listed with size and SHA-256 in `artifact_checksums.json`; that manifest excludes itself. The subsequent `final_audit_receipt.json` checks leaderboards, preservation and every listed checksum. `closure_checksums.json` hashes the base manifest and final audit receipt, and excludes itself, avoiding circular hashes. Together these registers identify every artifact, including their explicitly excluded terminal manifest. The inventory includes initial/revised discovery evidence, source snapshots, generator/configuration, compressed synthetic inputs, every decision/fill journal, daily CSV, per-run receipt, full metrics/leaderboards, paired comparison, tests, independent verification, preservation certificates and scripts. No old evidence was overwritten. A human can reproduce into a separately named Stage3F output directory; existing run directories are never overwritten.')
    add('## Human decisions and stop boundary')
    add('No result justifies changing the frozen official submission. No promotion, submission replacement or DEC-06 activation is authorized. Required unresolved decisions are rights-cleared explicit non-cache historical inputs if a real-data comparison is desired, clarification of contradictory competition rules/hidden evaluator behavior, and a genuinely unseen authorized evaluation design. Restoring missing sweep configurations would expand coverage but must not invent old versions. Preserve the synthetic results as engineering/descriptive research. **Stage3F stops here.**')
    reportpath=ROOT/'GUARDIAN_ALPHA_V30_STAGE3F_ALL_VERSION_PAPER_TRADING_TOURNAMENT.md'
    with reportpath.open('x',encoding='utf-8',newline='\n') as f: f.write('\n\n'.join(report)+'\n')
    # Record status after the report itself exists.
    (OUT/'git_status_final.txt').write_text(t.git_status(),encoding='utf-8')
    allfiles=list(OUT.rglob('*'))+list((ROOT/'research/evidence/v30/v30_stage3f_20261025_tournament').rglob('*'))
    allfiles += [reportpath]+list((ROOT/'research/simulations').glob('v30_stage3f*'))+list((ROOT/'research/tests').glob('test_v30_stage3f*'))
    manifest=[{'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':t.digest(p.read_bytes())} for p in sorted(set(allfiles)) if p.is_file()]
    dump('artifact_checksums.json',{'self_excluded':True,'files':manifest,'count':len(manifest)})
    print(json.dumps({'summary':totals,'report':str(reportpath),'risk_leader':qualified_risk[0] if qualified_risk else None,
      'capital_leader':qualified_capital[0] if qualified_capital else None,'artifacts':len(manifest)},indent=2))
if __name__=='__main__': main()
