"""Stage 3F offline tournament. Only new Stage 3F outputs; no vendor data/network.

Run from repository root with python -B. Commands: prepare, run, summarize.
Frozen strategy bytes are compiled unchanged in independent restricted namespaces.
Scratch adapters compile exact, unchanged definition AST nodes, excluding I/O drivers.
"""
from __future__ import annotations
import argparse, ast, builtins, collections, copy, csv, datetime as dt
import gzip, hashlib, importlib, io, json, math, os, pathlib, platform, random
import statistics, subprocess, sys, time, traceback, types

ROOT = pathlib.Path(__file__).resolve().parents[2]
TAG = 'v30_stage3f_20261025'
OUT = ROOT / 'research/evidence/v30' / (TAG + '_tournament')
START = 100000.0
SEEDS = [310601, 310619]
SCENARIOS = ['bull','bear','sideways','high_volatility','crash','fast_recovery',
 'slow_recovery','technology_drawdown','sector_rotation','volatility_spike',
 'leveraged_decay','missing_bars','opening_gap','corporate_actions','liquidity_shock','long_cycle']
ROOT_STRATEGIES = ['agent.py','baseline.py','ai_momentum.py','drawdown_momentum.py',
 'example_sector_rotation.py','example_vol_target.py','house_barbell_realasset.py',
 'momentum_v1.py','qqq_benchmark.py','seed_dual_momentum.py']
SCRATCH = ['scratch/test_hypotheses.py','scratch/test_hypotheses_part2.py',
 'scratch/counterfactual_rebalancing.py','scratch/test_candidates_a_to_f.py']
DEPS = ['research/engine/cash_affordability_model.py',
 'research/engine/v30_broker_accounting_r.py','research/engine/v30_broker_accounting_final.py']
PROTECTED = {'agent.py':('raw','46e68dc93fdfb10f1eecfa832673ac4626c1b93627272d89b0d06a054cb13ffd'),
 'universe.json':('lf','66563b613c0bd760759afb23ebb95c59385cfbcfb1b05569e392cb4b683cb5dd'),
 'research/strategies/v12_candidate_ae.py':('lf','978edf7aabc5387af5c8b1fa6a59e152cd6b82bf80fdbfa306b8a6202f187793'),
 'research/strategies/v30_candidate_d2_cash_cushion.py':('raw','5a04215a9096646818' )}
# Explicit full value; retain no shortened checksum in the actual certification.
PROTECTED['research/strategies/v30_candidate_d2_cash_cushion.py'] = ('raw','5a04215a909664681a4378ef3d06d7c33f6afc5ed1306bfe42ed37c2518f8215')
B3 = set('TQQQ SOXL UPRO SPXL TNA FAS TECL LABU CURE DRN UDOW NAIL'.split())
B2 = set('QLD SSO DDM ROM UWM AGQ'.split())
def beta(t): return 3 if t in B3 else 2 if t in B2 else 1
def digest(b): return hashlib.sha256(b).hexdigest()
def canon(x): return json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def write(path, x):
    path=pathlib.Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x',encoding='utf-8',newline='\n') as f: json.dump(x,f,indent=2,allow_nan=False)
def git(*args):
    allowed={'log','show','rev-parse','branch','status','ls-tree','diff','for-each-ref'}
    assert args[0] in allowed
    p=subprocess.run(['git','--no-optional-locks',*args],cwd=ROOT,capture_output=True)
    if p.returncode: raise RuntimeError(p.stderr.decode(errors='replace'))
    return p.stdout
def git_status():
    return git('status','--porcelain=v1','--untracked-files=normal','--','.',
     ':!tiingo_cache',':!scratch',':!private_results.json',':!history.json',':!leaderboard.json').decode()
def checkpoint():
    r={'branch':git('branch','--show-current').decode().strip(),
       'head':git('rev-parse','HEAD').decode().strip(),'parent':git('rev-parse','HEAD^').decode().strip(),
       'tracked_status':git('status','--porcelain=v1','--untracked-files=no').decode(),'hashes':{}}
    assert r['branch']=='archive/v30-stage2h-final-evidence-freeze'
    assert r['head']=='4540ee49dac29e4599fbbeb96bbcffd2dafd6705'
    assert r['parent']=='ce6b4c21b832044d0ffb45dce2ba949ab867d520'
    for p,(mode,h) in PROTECTED.items():
        b=(ROOT/p).read_bytes(); actual=digest(b.replace(b'\r\n',b'\n') if mode=='lf' else b)
        r['hashes'][p]={'mode':mode,'expected':h,'actual':actual,'match':actual==h}
        assert actual==h, 'STOP: protected invariant failed: '+p
    r['archive_deltas']={ref:git('show','--format=','--shortstat',ref).decode().strip() for ref in ['HEAD','HEAD^']}
    return r
def source_bytes(path,commit=None): return git('show',commit+':'+path) if commit else (ROOT/path).read_bytes()
def tree_entries(b):
    tree=ast.parse(b.decode('utf-8-sig'))
    entries=[]
    for n in tree.body:
        if isinstance(n,ast.FunctionDef) and n.name=='decide': entries.append(('decide','function',n))
        if isinstance(n,ast.ClassDef) and any(isinstance(v,ast.FunctionDef) and v.name=='decide' for v in n.body): entries.append((n.name,'class',n))
    return tree,entries
def dependencies(tree):
    return sorted({n.module for n in ast.walk(tree) if isinstance(n,ast.ImportFrom) and n.module}|
                  {a.name for n in ast.walk(tree) if isinstance(n,ast.Import) for a in n.names})
def snapshot(b):
    h=digest(b); p=OUT/'sources'/(h+'.py')
    if not p.exists(): p.parent.mkdir(parents=True,exist_ok=True); p.write_bytes(b)
    return h
def prepare():
    start=time.time(); cert=checkpoint(); OUT.mkdir(parents=True,exist_ok=False)
    write(OUT/'checkpoint_before.json',cert)
    write(OUT/'budget.json',{'start_epoch':start,'start_utc':dt.datetime.now(dt.timezone.utc).isoformat(),
      'maximum_minutes':360,'allocation_minutes':dict(discovery=45,contract_data=40,harness=75,tournament=70,stress=50,verification=40,reporting=40),
      'note':'Budget begins at machine-recorded preparation; earlier read-only inspection time is separately disclosed.'})
    (OUT/'git_status_before.txt').write_text(git_status(),encoding='utf-8')
    # Explicit code/report directories only. Never descend into cache, hidden dirs or vendor data.
    preserve=set(ROOT.glob('*.md'))|set(ROOT.glob('*.py'))|{ROOT/'universe.json'}
    for directory in ['docs','research/strategies','research/engine','research/scripts','research/tests','research/simulations','scratch']:
        preserve.update((ROOT/directory).glob('*.py')); preserve.update((ROOT/directory).glob('*.md'))
    for pattern in ['v30_stage3d*','v30_stage3e*']:
        preserve.update((ROOT/'research/evidence/v30').glob(pattern))
    # Archive file metadata, not raw market observations. Source/report files are hashed above.
    write(OUT/'preservation_before.json',[{'path':p.relative_to(ROOT).as_posix(),'sha256':digest(p.read_bytes()),'bytes':p.stat().st_size}
      for p in sorted(preserve) if p.is_file() and TAG not in p.name])
    archive=[]
    for ref in ['HEAD^','HEAD']:
        for row in git('diff','--name-status',ref+'^',ref).decode().splitlines(): archive.append({'commit':ref,'entry':row})
    write(OUT/'archive_285_file_register.json',archive)
    paths=set(ROOT_STRATEGIES)|{p.relative_to(ROOT).as_posix() for p in (ROOT/'research/strategies').glob('*.py') if p.name!='__init__.py'}
    historical=git('log','--all','--name-only','--format=','--','research/strategies',*ROOT_STRATEGIES).decode().splitlines()
    paths.update(p for p in historical if p.endswith('.py') and not p.endswith('__init__.py'))
    registry=[]; keys={}; aliases=[]; sources=[]
    def register(path,b,commit,entry,kind,node,kwargs=None,args=None,extract=False,label=None):
        sh=snapshot(b); lf=digest(b.replace(b'\r\n',b'\n')); tr=ast.parse(b.decode('utf-8-sig'))
        agent_b=source_bytes('agent.py',commit) if commit and path!='agent.py' else (ROOT/'agent.py').read_bytes()
        agent_h=snapshot(agent_b)
        depmap={'agent':agent_h}
        for dep in DEPS:
            if dep.replace('/','.').removesuffix('.py') in dependencies(tr):
                depmap[dep.replace('/','.').removesuffix('.py')]=snapshot(source_bytes(dep,commit))
        # A dependency context is part of implementation identity; source alone is insufficient.
        key=(lf,entry,json.dumps(kwargs or {},sort_keys=True),json.dumps(args or []),tuple(sorted(depmap.items())) if 'agent' in dependencies(tr) else ())
        alias={'source_path':path,'git_commit':commit or 'WORKTREE','source_sha256':sh,'entry':entry,'kwargs':kwargs or {},'args':args or []}
        if key in keys:
            alias['duplicate_of']=keys[key]; aliases.append(alias); return
        cid=f'C{len(registry)+1:03d}'; keys[key]=cid
        doc=ast.get_docstring(node) or ast.get_docstring(tr) or 'Objective not documented'
        record=dict(id=cid,label=label or (path+':'+entry+(' @'+commit[:8] if commit else '')),family=path.split('/')[-1].removesuffix('.py'),
          source_path=path,git_commit=commit or 'WORKTREE',source_sha256=sh,lf_sha256=lf,entry=entry,kind=kind,
          kwargs=kwargs or {},args=args or [],extract=extract,dependency_sources=depmap,
          creation_stage='from filename/source docstring; commit supplies historical context',objective=doc,
          execution_interface='decide(market_state, portfolio_state, cash); class/factory bound without parameter changes',
          dependencies=dependencies(tr),historical_evaluation_status='preserved source; historical PASS not inherited',genuine_source=True,
          runnable_without_source_modification=True,eligibility='ELIGIBLE_PENDING_EXECUTION',logical_equivalence='not proved; see exact duplicate register')
        registry.append(record)
    for path in sorted(paths,key=lambda p:(p!='agent.py',p)):
        versions=[]
        if (ROOT/path).is_file(): versions.append((None,(ROOT/path).read_bytes()))
        for commit in git('log','--all','--format=%H','--',path).decode().splitlines():
            try: versions.append((commit,source_bytes(path,commit)))
            except RuntimeError: continue # deleted source has no blob at deletion commit
        for commit,b in versions:
            tree,entries=tree_entries(b); sources.append({'path':path,'commit':commit or 'WORKTREE','sha256':digest(b),'entries':[e[0] for e in entries]})
            for entry,kind,node in entries: register(path,b,commit,entry,kind,node)
    # Exact scratch definitions are preserved; only top-level data loading/drivers are omitted.
    for path in SCRATCH:
        b=(ROOT/path).read_bytes(); tree,entries=tree_entries(b)
        for entry,kind,node in entries:
            if entry=='ParameterizedCadenceAgent':
                policies=next(n.value for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='POLICIES' for t in n.targets))
                for label,call in zip(policies.keys,policies.values):
                    register(path,b,None,entry,kind,node,kwargs={k.arg:ast.literal_eval(k.value) for k in call.keywords},extract=True,label=ast.literal_eval(label))
            else: register(path,b,None,entry,kind,node,extract=True)
        for node in tree.body:
            if isinstance(node,ast.FunctionDef) and node.name.startswith('make_h'):
                argsets=[[.020],[.025],[.030]] if node.name=='make_h1_decide' else [['no_xle'],['conservative']] if node.name=='make_h5_decide' else [[]]
                for args in argsets: register(path,b,None,node.name,'factory',node,args=args,extract=True,label=node.name+str(args))
    universe=json.loads((ROOT/'universe.json').read_text())['tickers']
    # Coverage derives from strategy identifiers, never from historical observations or performance.
    symbols={'SPY','QQQ','XLK','XLV','XLP','XLU','XLE','QLD','SSO'}
    for p in (OUT/'sources').glob('*.py'):
        tr=ast.parse(p.read_text(encoding='utf-8-sig'))
        symbols|={n.value for n in ast.walk(tr) if isinstance(n,ast.Constant) and isinstance(n.value,str) and n.value in universe}
    config={'classification':'SYNTHETIC','initial_cash':START,'warmup':220,'seeds':SEEDS,'scenarios':SCENARIOS,
      'sessions':126,'long_cycle_sessions':504,'annualization':252,'risk_free_rate':0,
      'universe_hash':digest((ROOT/'universe.json').read_bytes()),'universe':universe,'observed_symbols':sorted(symbols),
      'calendar':'invented weekdays from 2000-01-03; not an exchange calendar; every date before 2022',
      'scenario_parameters':{'warmup_drift':.0007,'warmup_sigma':.006,'bull_drift':.0015,'bear_drift':-.0025,
       'base_sigma':.008,'high_vol_sigma':.035,'crash_index':35,'crash_return':-.35,'gap_index':45,'gap_return':-.30,
       'tech_shock_index':40,'tech_shock':-.25,'vol_spike_range':[35,55],'spike_sigma':.06,'rotation_block':21,
       'split_index':40,'split_ratio':2,'dividend_ex_index':70,'dividend_pay_index':75,'dividend_fraction':.01,
       'missing_range':[40,46],'liquidity_slip_multiplier':20,'long_cycle_block':126},
      'rules':{'commission_bps':0,'slippage_bps_equity':5,'slippage_bps_leveraged':10,'beta_cap':1.5,'name_cap':.30,
       'concentration_violation':'fraction >= .30 for >5 consecutive sessions','catastrophe_drawdown':.5,
       'max_proposed_orders':100,'max_fills_daily':50,'timing':'prior-close information, same-session open fill',
       'missing':'no current open => reject; close marks carry last known price','corporate_actions':'split shares and backward signal prices on ex-date; dividend receivable then cash at payment',
       'settlement':'immediate sell proceeds; no margin','decision_seconds':5},
      'sensitivity':{'candidates':['agent.py','research/strategies/v30_candidate_d2_cash_cushion.py'],
       'scenario':'long_cycle','modes':['zero_cost','high_cost','close_fill']},
      'ranking':'separate per-scenario return tables; long_cycle Track B Sharpe; stress worst return and drawdown, no universal score',
      'frozen_before_first_run':True}
    write(OUT/'inventory.json',registry); write(OUT/'deduplication.json',aliases); write(OUT/'source_references.json',sources)
    write(OUT/'configuration_preregistered.json',config)
    write(OUT/'data_provenance.json',{'used':'new Stage 3F generator only','classification':'SYNTHETIC',
     'authorization':'explicit Stage 3F user request for synthetic scenarios','prior_optimization':'none of these observations existed before preparation; scenarios are engineering designs, not holdout market validation',
     'market_data_loaded':False,'licensing':'no vendor observations or estimated vendor statistics used; no claim to grant a distribution license',
     'blocked':[{'data':'Tier 1/Tier 2 Tiingo','reason':'all tiingo_cache contents prohibited; Tier 2 additionally reused development sample'},
      {'data':'Tier 3','reason':'sealed; no availability inspection'},
      {'data':'sample_regimes.json.gz','reason':'V29F UNKNOWN source/derived rights conflicts with Stage 3D assertion; not opened, hashed or decompressed'}],
     'evidence':['GUARDIAN_ALPHA_V29F_RIGHTS_RESOLUTION.md','research/evidence/v30/v30_stage3d_data_rights_and_provenance_matrix.json',
      'GUARDIAN_ALPHA_V30_STAGE2E_CROSS_STAGE_EVIDENCE_AND_RISK_BUDGET.md section 8.1'],
     '43_trials':'includes accounting, raw/adjusted, cutoff and halflife sweeps; not a source count',
     'V29_V29E':'archive/publication snapshots, not new decision implementations unless source hash differs',
     'missing_parameter_trials':'unrecoverable exact sweep factories are NOT VERIFIED; no reconstructed equivalent created'})
    print(json.dumps({'candidates':len(registry),'duplicate_references':len(aliases),'symbols':len(symbols),'out':str(OUT)}))

SAFE_IMPORTS={'__future__','math','statistics','typing','copy','dataclasses','datetime','enum','collections','functools','itertools'}
class IsolatedLoader:
    """Fresh source graph per run; controlled imports and no filesystem/network builtins."""
    def __init__(self,record): self.record=record; self.cache={}; self.names=[]
    def importer(self,name,globals=None,locals=None,fromlist=(),level=0):
        if level: raise ImportError('relative imports blocked')
        if name in self.record['dependency_sources']: return self.module(name,self.record['dependency_sources'][name])
        if name in SAFE_IMPORTS: return importlib.import_module(name)
        raise ImportError('Stage3F forbidden import: '+name)
    def module(self,name,sh,extract=False):
        if name in self.cache: return self.cache[name]
        raw=(OUT/'sources'/(sh+'.py')).read_bytes(); assert digest(raw)==sh
        tree=ast.parse(raw.decode('utf-8-sig')); code=raw
        if extract:
            body=[]
            for n in tree.body:
                if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and (isinstance(n,ast.ClassDef) or n.name.startswith('make_h')): body.append(n)
                elif isinstance(n,ast.ImportFrom) and n.module in SAFE_IMPORTS|{'agent'}: body.append(n)
                elif isinstance(n,ast.Import) and all(a.name in SAFE_IMPORTS|{'agent'} for a in n.names): body.append(n)
            tree=ast.Module(body=body,type_ignores=[]); code=compile(tree,self.record['source_path'],'exec')
        name_unique=TAG+'_'+name.replace('.','_')+'_'+str(id(self))
        mod=types.ModuleType(name_unique); mod.__file__=self.record['source_path']; self.cache[name]=mod
        sys.modules[name_unique]=mod; self.names.append(name_unique)
        safe=dict(vars(builtins)); safe['__import__']=self.importer
        def denied(*a,**k): raise PermissionError('Stage3F file/dynamic execution forbidden')
        for n in ['open','input','exec','eval','compile','breakpoint']: safe[n]=denied
        mod.__dict__['__builtins__']=safe
        exec(code,mod.__dict__)
        return mod
    def load(self):
        r=self.record; mod=self.module('candidate',r['source_sha256'],r['extract']); obj=getattr(mod,r['entry'])
        if r['kind']=='class': obj=obj(*r['args'],**r['kwargs']).decide
        elif r['kind']=='factory': obj=obj(*r['args'],**r['kwargs'])
        return obj
    def close(self):
        for n in self.names: sys.modules.pop(n,None)

def weekdays(n):
    days=[]; d=dt.date(2000,1,3)
    while len(days)<n:
        if d.weekday()<5: days.append(d.isoformat())
        d+=dt.timedelta(days=1)
    return days
def generate(scenario,seed,config):
    n=config['long_cycle_sessions'] if scenario=='long_cycle' else config['sessions']; warm=config['warmup']
    dates=weekdays(n+warm); syms=config['observed_symbols']; p=config['scenario_parameters']
    seedkey=int(digest(f'{scenario}|{seed}|stage3f-v1'.encode())[:16],16); rng=random.Random(seedkey)
    bars={t:[] for t in syms}; last={t:80+i*2 for i,t in enumerate(syms)}; actions=[]
    tech=set('QQQ XLK SMH AAPL MSFT GOOGL AMZN META NVDA TSLA TQQQ QLD SOXL TECL ROM'.split())
    defensive=set('XLP XLU XLV SHY TLT IEF GLD IAU'.split())
    for i,date in enumerate(dates):
        j=i-warm; regime=scenario
        if scenario=='long_cycle' and j>=0: regime=['bull','bear','sideways','fast_recovery'][min(j//126,3)]
        mu=.0007 if j<0 else .0015 if regime=='bull' else -.0025 if regime=='bear' else 0.0 if regime in ['sideways','leveraged_decay'] else .0005
        sigma=.006 if j<0 else .035 if regime=='high_volatility' else .008
        if j>=0 and regime=='leveraged_decay': sigma=.025
        if 35<=j<55 and regime=='volatility_spike': sigma=.06
        if regime in ['crash','fast_recovery','slow_recovery'] and j>35:
            mu=.006 if regime=='fast_recovery' else .001 if regime=='slow_recovery' else -.001
        common=rng.gauss(mu,sigma)
        if j==35 and regime in ['crash','fast_recovery','slow_recovery']: common=-.35
        if regime=='leveraged_decay' and j>=0: common=(.04 if j%2==0 else -.04)
        for k,t in enumerate(syms):
            b=beta(t); loading=.35 if t in defensive else 1.2 if t in tech else .8
            r=loading*common+rng.gauss(0,sigma*.28)+(k%7-3)*.00004
            if regime=='technology_drawdown' and j==40 and t in tech: r-=.25
            if regime=='sector_rotation' and j>=0: r+=(.003 if (k%4)==((j//21)%4) else -.001)
            r=b*r-(b-1)*.00015 # daily-reset leveraged product, explicit invented expense drag
            gap=rng.gauss(0,.001)
            if regime=='opening_gap' and j==45: gap=-.30 if t not in defensive else -.08
            prev=last[t]
            if scenario=='corporate_actions' and j==40 and t in ['SPY','QQQ','XLK','XLP','XLU','XLV','XLE']:
                prev/=2; actions.append({'date':date,'ticker':t,'type':'split','ratio':2})
            div=0
            if scenario=='corporate_actions' and j==70 and t in ['SPY','QQQ','XLK','XLP','XLU','XLV','XLE']:
                div=prev*.01; actions.append({'date':date,'pay_date':dates[i+5],'ticker':t,'type':'dividend','amount':div})
            op=max(.01,prev*(1+gap)-div); cl=max(.01,op*(1+max(-.90,r)))
            row={'ts':date,'open':op,'high':max(op,cl)*1.003,'low':min(op,cl)*.997,'close':cl,'volume':1000000+1000*k}
            last[t]=cl
            if scenario=='missing_bars' and 40<=j<=46 and t in ['SPY','QQQ','XLP','XLU','XLV','XLE','QLD']: continue
            bars[t].append(row)
    data={'id':scenario+'_'+str(seed),'scenario':scenario,'seed':seed,'classification':'SYNTHETIC',
      'eval_dates':dates[warm:],'warmup_dates':dates[:warm],'bars':bars,'actions':actions}
    assert max(dates)<'2022-01-01'
    data['sha256']=digest(canon(data)); return data

class FrozenBar(dict):
    def _deny(self,*a,**k): raise TypeError('immutable market observation')
    __setitem__=__delitem__=clear=pop=popitem=setdefault=update=_deny
def prepare_frames(data,warm=220):
    bydate={t:{b['ts']:b for b in rows} for t,rows in data['bars'].items()}
    actions=collections.defaultdict(list)
    for a in data['actions']: actions[a['date']].append(a)
    frames=[]
    for date in data['eval_dates']:
        splits={t:math.prod(a['ratio'] for a in data['actions'] if a['type']=='split' and a['ticker']==t and a['date']<=date) for t in bydate}
        market={}
        for t,rows in data['bars'].items():
            history=[]
            for row in [r for r in rows if r['ts']<date][-warm:]:
                adjust=math.prod(a['ratio'] for a in data['actions'] if a['type']=='split' and a['ticker']==t and row['ts']<a['date']<=date)
                history.append(FrozenBar({key:(v/adjust if key in ['open','high','low','close'] else v*adjust if key=='volume' else v) for key,v in row.items()}))
            market[t]=history
        current={t:rows[date] for t,rows in bydate.items() if date in rows}
        frames.append({'date':date,'market':market,'current':current,'actions':actions[date],
          'input_sha256':digest(canon(market))})
    return frames

def execute_orders(orders,cash,positions,avg,opens,marks,universe,mode='base',slip_mult=1.,commission_bps=0.,limits=True):
    journal=[]; normalized=[]
    if not isinstance(orders,list): return cash,[{'status':'REJECTED','reason':'not_list','raw':repr(orders)}]
    for index,o in enumerate(orders):
        reason=None
        try:
            t=str(o['ticker']).strip().upper(); side=o['side']; q=float(o['quantity'])
            if index>=100: reason='order_limit'
            elif t not in universe: reason='universe'
            elif side not in ['buy','sell'] or not math.isfinite(q) or q<=0: reason='invalid'
            elif t not in opens or not math.isfinite(opens[t]) or opens[t]<=0: reason='missing_open'
        except (KeyError,ValueError,TypeError,OverflowError): reason='malformed'
        if reason: journal.append({'status':'REJECTED','reason':reason,'index':index,'raw':repr(o)})
        else: normalized.append((index,t,side,q))
    fills=0
    for index,t,side,requested in sorted(normalized,key=lambda x:x[2]!='sell'):
        q=requested; raw=opens[t]; slip=(.001 if beta(t)>1 else .0005)*slip_mult; fee_rate=commission_bps/10000
        fill=raw*(1+slip if side=='buy' else 1-slip); held=positions.get(t,0); reason=None
        eq=cash+sum(v*marks.get(k,0) for k,v in positions.items())
        if fills>=50: reason='fill_limit'
        if side=='buy':
            room=max(0,.30*eq-held*fill); used=sum(v*marks.get(k,0)*beta(k) for k,v in positions.items())
            allowed=min(cash/(1+fee_rate),room,max(0,1.5*eq-used)/beta(t)) if limits else cash/(1+fee_rate)
            q=min(q,max(0,allowed)/fill)
        else: q=min(q,held)
        if q<=1e-12: reason=reason or ('no_holdings' if side=='sell' else 'cash_or_risk_limit')
        if reason: journal.append({'status':'REJECTED','reason':reason,'index':index,'ticker':t,'side':side,'requested':requested}); continue
        fee=fill*q*fee_rate; before=cash
        if side=='buy':
            avg[t]=(avg.get(t,0)*held+fill*q+fee)/(held+q); positions[t]=held+q; cash-=fill*q+fee
        else: positions[t]=held-q; cash+=fill*q-fee
        if abs(cash)<1e-9: cash=0.
        assert cash>=-1e-7 and positions[t]>=-1e-9
        fills+=1; journal.append({'status':'FILLED' if q>=requested-1e-10 else 'PARTIAL',
         'index':index,'ticker':t,'side':side,'requested':requested,'quantity':q,'raw_price':raw,'fill_price':fill,
         'fee':fee,'slippage':abs(fill-raw)*q,'cash_before':before,'cash_after':cash,'position_after':positions[t]})
    return cash,journal

def metrics(rows):
    if not rows: return {}
    eq=[START]+[r['equity'] for r in rows]; rets=[eq[i]/eq[i-1]-1 for i in range(1,len(eq))]
    n=len(rets); mean=statistics.mean(rets); sd=statistics.stdev(rets) if n>1 else 0
    downside=math.sqrt(sum(min(r,0)**2 for r in rets)/n); peak=START; mdd=0; under=0; longest=0; recoveries=[]
    for e in eq[1:]:
        peak=max(peak,e); mdd=max(mdd,1-e/peak)
        if e<peak-1e-8: under+=1; longest=max(longest,under)
        else:
            if under: recoveries.append(under)
            under=0
    ret=eq[-1]/START-1; cagr=(eq[-1]/START)**(252/n)-1 if n>=252 and eq[-1]>0 else None
    exposure=statistics.mean(r['gross_exposure'] for r in rows); low=sorted(rets); tail=low[:max(1,math.ceil(.05*n))]
    monthly={}; last=START
    for r in rows:
        month=r['date'][:7]
        if month not in monthly: monthly[month]={'start_equity':last,'end_equity':r['equity'],'sessions':0}
        monthly[month]['end_equity']=r['equity']; monthly[month]['sessions']+=1; last=r['equity']
    return dict(final_equity=eq[-1],total_return=ret,cagr=cagr,average_daily_return=mean,
      monthly_returns={k:dict(return_=v['end_equity']/v['start_equity']-1,sessions=v['sessions'],partial_calendar_month=True) for k,v in monthly.items()},
      max_drawdown=mdd,peak_gross_exposure=max(r['gross_exposure'] for r in rows),
      peak_beta_exposure=max(r['beta_exposure'] for r in rows),worst_day=min(rets),realized_volatility=sd*math.sqrt(252),
      var95_loss=-low[max(0,math.ceil(.05*n)-1)],expected_shortfall95_loss=-statistics.mean(tail),
      max_underwater_sessions=longest,completed_recovery_durations=recoveries,unrecovered_at_end=under>0,
      sharpe=mean/sd*math.sqrt(252) if sd>1e-12 else None,
      sortino=mean/downside*math.sqrt(252) if downside>1e-12 else None,
      calmar=cagr/mdd if cagr is not None and mdd>1e-12 else None,
      exposure_adjusted_total_return=ret/exposure if exposure>1e-12 else None,average_exposure=exposure,
      trades=sum(r['trades'] for r in rows),turnover=sum(r['turnover'] for r in rows)/START,
      fees=sum(r['fees'] for r in rows),slippage=sum(r['slippage'] for r in rows),
      rejected_orders=sum(r['rejected'] for r in rows),invalid_signals=sum(r['invalid'] for r in rows),
      missing_observations=sum(r['missing'] for r in rows),execution_latency=None,
      mean_cash_fraction=statistics.mean(r['cash']/r['equity'] for r in rows),sessions=n)

def run_one(record,data,frames,config,mode='base',retain=True):
    started=time.perf_counter(); loader=IsolatedLoader(record); cash=START; pos={}; avg={}; receivables=[]
    rows=[]; journal=[]; errors=[]; streak={}; peak=START; violations=collections.Counter()
    last_marks={t:bs[-1]['close'] for t,bs in frames[0]['market'].items() if bs}
    try:
        decide=loader.load()
        for frame in frames:
            date=frame['date']; action_j=[]
            for a in frame['actions']:
                t=a['ticker']
                if a['type']=='split':
                    old=pos.get(t,0); pos[t]=old*a['ratio']; avg[t]=avg.get(t,0)/a['ratio']
                    if t in last_marks: last_marks[t]/=a['ratio']
                    action_j.append(dict(a,old_quantity=old,new_quantity=pos[t]))
                else:
                    amount=pos.get(t,0)*a['amount']; receivables.append({'pay_date':a['pay_date'],'amount':amount,'ticker':t})
                    action_j.append(dict(a,entitlement=amount))
            paid=[a for a in receivables if a['pay_date']<=date]; cash+=sum(a['amount'] for a in paid)
            receivables=[a for a in receivables if a['pay_date']>date]
            # Signals get only prior bars. Split adjustment is known pre-open, no current prices are supplied.
            ms={t:list(bs) for t,bs in frame['market'].items()}
            prior={t:bs[-1]['close'] for t,bs in ms.items() if bs}
            portfolio={'cash':cash,'positions':[{'ticker':t,'quantity':q,'avg_cost':avg.get(t,0)} for t,q in pos.items() if q>0], 'last_prices':prior}
            assert all(b['ts']<date for bs in ms.values() for b in bs)
            decision_start=time.perf_counter(); err=None
            try: orders=decide(ms,copy.deepcopy(portfolio),cash)
            except Exception as exc: orders=[]; err=repr(exc); errors.append({'date':date,'error':err})
            elapsed=time.perf_counter()-decision_start
            if elapsed>5: violations['decision_timeout']+=1; orders=[]
            current=frame['current']; opens={t:b['close' if mode=='close_fill' else 'open'] for t,b in current.items()}
            marks=dict(last_marks); marks.update(opens)
            mult=0 if mode=='zero_cost' else 5 if mode=='high_cost' else 20 if data['scenario']=='liquidity_shock' else 1
            commission=10 if mode=='high_cost' else 0
            cash_before=cash
            cash,events=execute_orders(orders,cash,pos,avg,opens,marks,set(config['universe']),mode,mult,commission)
            last_marks.update({t:b['close'] for t,b in current.items()})
            eq=cash+sum(q*last_marks.get(t,0) for t,q in pos.items())+sum(a['amount'] for a in receivables)
            assert math.isfinite(eq) and eq>0
            gross=sum(abs(q*last_marks.get(t,0)) for t,q in pos.items())/eq
            bgross=sum(abs(q*last_marks.get(t,0))*beta(t) for t,q in pos.items())/eq
            if bgross>1.5+1e-6: violations['leverage_close_sessions']+=1
            conc=max([q*last_marks.get(t,0)/eq for t,q in pos.items()]+[0])
            for t,q in pos.items():
                streak[t]=streak.get(t,0)+1 if q*last_marks.get(t,0)/eq>=.30 else 0
            if max(streak.values(),default=0)>5: violations['concentration_sessions']+=1
            peak=max(peak,eq); dd=1-eq/peak
            if dd>=.5: violations['catastrophe_sessions']+=1
            fills=[e for e in events if e['status'] in ['FILLED','PARTIAL']]
            invalid=sum(e.get('reason') in ['invalid','malformed','not_list','universe'] for e in events)
            violations['invalid_orders']+=invalid
            row={'date':date,'cash':cash,'receivables':sum(a['amount'] for a in receivables),'equity':eq,
              'return':eq/(rows[-1]['equity'] if rows else START)-1,'drawdown':dd,'gross_exposure':gross,'beta_exposure':bgross,
              'concentration':conc,'trades':len(fills),'turnover':sum(e['fill_price']*e['quantity'] for e in fills),
              'fees':sum(e['fee'] for e in fills),'slippage':sum(e['slippage'] for e in fills),
              'rejected':sum(e['status']=='REJECTED' for e in events),'invalid':invalid,
              'missing':len(data['bars'])-len(current),'decision_seconds':elapsed}
            rows.append(row)
            journal.append({'date':date,'input_sha256':frame['input_sha256'],'prior_max_date':max((b['ts'] for bs in ms.values() for b in bs),default=None),
             'cash_before_orders':cash_before,'orders':orders,'error':err,'events':events,'actions':action_j,'dividends_paid':paid,
             'positions':dict(pos),'marks':dict(last_marks),'cash':cash,'receivables':list(receivables),'equity':eq})
    except Exception:
        errors.append({'date':rows[-1]['date'] if rows else None,'error':traceback.format_exc()})
    finally: loader.close()
    result={'candidate':record['id'],'label':record['label'],'source_sha256':record['source_sha256'],'dataset':data['id'],
      'dataset_sha256':data['sha256'],'classification':'SYNTHETIC','mode':mode,'seed':data['seed'],
      'start_session':data['eval_dates'][0],'end_session':data['eval_dates'][-1],'actual_sessions':len(rows),
      'status':'EXECUTED SUCCESSFULLY' if not errors and len(rows)==len(frames) else 'FAILED','errors':errors,
      'elapsed_seconds':time.perf_counter()-started,'exit_code':0 if not errors else 1,
      'metrics':metrics(rows),'violations':dict(violations),'compliance':'PASS' if not errors and not any(violations.values()) else 'FAILED',
      'maximum_decision_seconds':max([r['decision_seconds'] for r in rows]+[0]),
      'command':f'python -B research/simulations/{TAG}_tournament.py run --candidate {record["id"]}',
      'complete':len(rows)==len(frames),'latency':'decision wall time measured; exchange latency not modeled'}
    if retain:
        dest=OUT/'runs'/record['id']/(data['id']+'_'+mode); dest.mkdir(parents=True,exist_ok=False)
        write(dest/'result.json',result)
        with (dest/'daily.csv').open('x',newline='',encoding='utf-8') as f:
            if rows: w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
        with (dest/'journal.jsonl.gz').open('xb') as raw:
            with gzip.GzipFile(fileobj=raw,mode='wb',mtime=0,filename='') as f:
                for j in journal: f.write(canon(j)+b'\n')
    return result,rows,journal

def run(candidate=None):
    checkpoint(); config=json.loads((OUT/'configuration_preregistered.json').read_text()); registry=json.loads((OUT/'inventory.json').read_text())
    if candidate: registry=[r for r in registry if r['id']==candidate]
    for scenario in SCENARIOS:
        for seed in SEEDS:
            data=generate(scenario,seed,config); frames=prepare_frames(data); p=OUT/'datasets'/(data['id']+'.json.gz')
            if not p.exists():
                p.parent.mkdir(exist_ok=True)
                with p.open('xb') as raw:
                    with gzip.GzipFile(fileobj=raw,mode='wb',mtime=0,filename='') as f: f.write(canon(data))
            for record in registry:
                dest=OUT/'runs'/record['id']/(data['id']+'_base')
                if dest.exists(): continue # preserve, never overwrite previous attempts
                r,_,_=run_one(record,data,frames,config)
                print(json.dumps({k:r[k] for k in ['candidate','dataset','mode','status','elapsed_seconds']},separators=(',',':')),flush=True)
            if scenario=='long_cycle':
                for record in registry:
                    if record['git_commit']!='WORKTREE' or record['source_path'] not in config['sensitivity']['candidates']: continue
                    for mode in config['sensitivity']['modes']:
                        if (OUT/'runs'/record['id']/(data['id']+'_'+mode)).exists(): continue
                        r,_,_=run_one(record,data,frames,config,mode)
                        print(json.dumps({k:r[k] for k in ['candidate','dataset','mode','status','elapsed_seconds']}),flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('command',choices=['prepare','run']); parser.add_argument('--candidate')
    a=parser.parse_args()
    if a.command=='prepare': prepare()
    elif a.command=='run': run(a.candidate)
