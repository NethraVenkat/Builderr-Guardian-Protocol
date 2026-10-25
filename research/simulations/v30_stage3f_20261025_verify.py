"""Independent Stage 3F Decimal journal reconstruction. Reads only Stage 3F artifacts."""
import collections, csv, decimal, gzip, hashlib, json, math, pathlib, statistics, sys, time
ROOT=pathlib.Path(__file__).resolve().parents[2]
OUT=ROOT/'research/evidence/v30/v30_stage3f_20261025_tournament_v2'
D=decimal.Decimal
decimal.getcontext().prec=40
def num(x): return D(str(x))
def load(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def digest(b): return hashlib.sha256(b).hexdigest()
def canon(x): return json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def b(t): return 3 if t in set('TQQQ SOXL UPRO SPXL TNA FAS TECL LABU CURE DRN UDOW NAIL'.split()) else 2 if t in set('QLD SSO DDM ROM UWM AGQ'.split()) else 1
def write(path,x):
    with path.open('x',encoding='utf-8') as f: json.dump(x,f,indent=2,allow_nan=False)
def verify():
    started=time.perf_counter(); registry=load(OUT/'inventory.json'); cfg=load(OUT/'configuration_preregistered.json')
    datasets={}; audits=[]; failures=[]; input_hashes={}; actual_pairs=[]; market_bydate={}
    for p in sorted((OUT/'datasets').glob('*.json.gz')):
        with gzip.open(p,'rt') as f: ds=json.load(f)
        h=ds.pop('sha256'); assert digest(canon(ds))==h, 'dataset hash'; ds['sha256']=h
        assert all(r['ts']<'2022-01-01' for rows in ds['bars'].values() for r in rows)
        datasets[ds['id']]=ds
        market_bydate[ds['id']]={date:{} for date in ds['eval_dates']}
        for ticker,rows in ds['bars'].items():
            for row in rows:
                if row['ts'] in market_bydate[ds['id']]: market_bydate[ds['id']][row['ts']][ticker]=row
        hashes={}
        # Independent rolling construction, using incremental histories instead of harness slices.
        streams={t:iter(rows) for t,rows in ds['bars'].items()}; nxt={t:next(it,None) for t,it in streams.items()}; history={t:[] for t in streams}
        for date in ds['eval_dates']:
            for ticker,it in streams.items():
                while nxt[ticker] and nxt[ticker]['ts']<date:
                    history[ticker].append(nxt[ticker]); nxt[ticker]=next(it,None)
            market={}
            for ticker,hist in history.items():
                market[ticker]=[]
                for row in hist[-220:]:
                    ratio=math.prod(a['ratio'] for a in ds['actions'] if a['type']=='split' and a['ticker']==ticker and row['ts']<a['date']<=date)
                    adj=dict(row)
                    for key in ['open','high','low','close']: adj[key]/=ratio
                    adj['volume']*=ratio; market[ticker].append(adj)
            hashes[date]=digest(canon(market))
        input_hashes[ds['id']]=hashes
    # Input reconstruction may overlap the final tournament runs; never snapshot
    # the run inventory until the tournament process has recorded its exit receipt.
    wait_start=time.perf_counter()
    while not (OUT/'tournament_execution_01.json').exists():
        if time.perf_counter()-wait_start>1200: raise TimeoutError('Tournament exit receipt absent after 20 minutes; no partial PASS produced')
        time.sleep(10)
    for path in sorted((OUT/'runs').glob('*/*/result.json')):
        r=load(path); ds=datasets[r['dataset']]; rec=next(x for x in registry if x['id']==r['candidate'])
        errors=[]; cash=D(100000); shares={}; marks={t:num(rows[-1]['close']) for t,rows in
          {t:[x for x in rows if x['ts']<ds['eval_dates'][0]] for t,rows in ds['bars'].items()}.items() if rows}
        current=market_bydate[r['dataset']]
        receiv=[]; equity=[D(100000)]; fees=D(0); slip=D(0); turn=D(0); fills=0; maxdiff=D(0); peakgross=0.; peakbeta=0.
        journal_count=0; rejected=0; invalid=0; missing=0; monthly={}; cashfrac=[]; exposures=[]; daily=[]
        rule_counts=collections.Counter(); name_streak={}; running_peak=D(100000)
        with (path.parent/'daily.csv').open(newline='',encoding='utf-8') as f: daily=list(csv.DictReader(f))
        def check(a,z,label,tol=1e-6):
            nonlocal maxdiff
            difference=abs(num(a)-num(z)); maxdiff=max(maxdiff,difference)
            if difference>num(tol): errors.append({'check':label,'actual':str(a),'expected':str(z),'absolute_difference':str(difference)})
        with gzip.open(path.parent/'journal.jsonl.gz','rt',encoding='utf-8') as f:
            for line in f:
                j=json.loads(line); date=j['date']; journal_count+=1
                if j['input_sha256']!=input_hashes[r['dataset']][date]: errors.append({'check':'identical causal input hash','date':date})
                if not j['prior_max_date']<date: errors.append({'check':'future information','date':date})
                for a in ds['actions']:
                    if a['date']!=date: continue
                    t=a['ticker']
                    if a['type']=='split':
                        shares[t]=shares.get(t,D(0))*num(a['ratio'])
                        if t in marks: marks[t]/=num(a['ratio'])
                    else: receiv.append({'pay_date':a['pay_date'],'amount':shares.get(t,D(0))*num(a['amount'])})
                cash+=sum((a['amount'] for a in receiv if a['pay_date']<=date),D(0))
                receiv=[a for a in receiv if a['pay_date']>date]
                check(j['cash_before_orders'],cash,'cash before orders')
                daily_fills=0
                for event in j['events']:
                    if event['status']=='REJECTED':
                        rejected+=1; bad=event.get('reason') in ['invalid','malformed','not_list','universe']; invalid+=bad; rule_counts['invalid_orders']+=bad; continue
                    t=event['ticker']; q=num(event['quantity']); price=num(event['fill_price']); fee=num(event['fee']); raw=num(event['raw_price'])
                    if t not in cfg['universe']: errors.append({'check':'frozen universe'})
                    field='close' if r['mode']=='close_fill' else 'open'; check(raw,current[date][t][field],'execution time/price')
                    mult=0 if r['mode']=='zero_cost' else 5 if r['mode']=='high_cost' else 20 if ds['scenario']=='liquidity_shock' else 1
                    sl=num(.001 if b(t)>1 else .0005)*mult
                    check(price,raw*(1+sl if event['side']=='buy' else 1-sl),'slippage model')
                    check(fee,price*q*(num(.001) if r['mode']=='high_cost' else D(0)),'commission model')
                    check(event['cash_before'],cash,'fill cash before')
                    if event['side']=='buy': cash-=q*price+fee; shares[t]=shares.get(t,D(0))+q
                    else: cash+=q*price-fee; shares[t]=shares.get(t,D(0))-q
                    check(event['cash_after'],cash,'fill cash after'); check(event['position_after'],shares[t],'position after fill')
                    if cash<num(-1e-7) or shares[t]<num(-1e-7): errors.append({'check':'negative cash/position'})
                    fees+=fee; slip+=abs(price-raw)*q; turn+=price*q; fills+=1
                    daily_fills+=1
                if daily_fills>50: errors.append({'check':'daily 50-fill cap'})
                for t,row in current[date].items(): marks[t]=num(row['close'])
                for t,q in shares.items(): check(j['positions'].get(t,0),q,'shares reconciliation')
                for t,px in marks.items(): check(j['marks'][t],px,'causal closing mark')
                nav=cash+sum((q*marks[t] for t,q in shares.items()),D(0))+sum((a['amount'] for a in receiv),D(0))
                check(j['equity'],nav,'NAV identity'); check(j['cash'],cash,'session cash')
                dr=daily[journal_count-1]; check(dr['equity'],nav,'daily CSV equity')
                check(dr['return'],nav/equity[-1]-1,'daily CSV return',1e-10)
                month=date[:7]
                if month not in monthly: monthly[month]=[equity[-1],nav,0]
                monthly[month][1]=nav; monthly[month][2]+=1
                equity.append(nav); gross=float(sum((abs(q*marks[t]) for t,q in shares.items()),D(0))/nav)
                bgross=float(sum((abs(q*marks[t])*b(t) for t,q in shares.items()),D(0))/nav)
                peakgross=max(peakgross,gross); peakbeta=max(peakbeta,bgross); exposures.append(gross); cashfrac.append(float(cash/nav))
                missing+=len(ds['bars'])-len(current[date])
                if bgross>1.5+1e-6: rule_counts['leverage_close_sessions']+=1
                for ticker,q in shares.items():
                    # Compare using the same float threshold; Decimal at exactly 30% may differ by one ulp.
                    fraction=float(q*marks[ticker]/nav)
                    name_streak[ticker]=name_streak.get(ticker,0)+1 if fraction>=.30 else 0
                if max(name_streak.values(),default=0)>5: rule_counts['concentration_sessions']+=1
                running_peak=max(running_peak,nav)
                if float(1-nav/running_peak)>=.5: rule_counts['catastrophe_sessions']+=1
                if float(dr['decision_seconds'])>5: rule_counts['decision_timeout']+=1
        m=r['metrics']; rr=[float(y/x-1) for x,y in zip(equity,equity[1:])]; n=len(rr)
        if n:
            peak=D(100000); dd=D(0); underwater=0; longest=0
            for e in equity[1:]:
                peak=max(peak,e); dd=max(dd,1-e/peak)
                underwater=underwater+1 if e<peak-num(1e-8) else 0; longest=max(longest,underwater)
            mean=statistics.mean(rr); sd=statistics.stdev(rr) if n>1 else 0; downside=math.sqrt(statistics.mean(min(v,0)**2 for v in rr))
            ret=float(equity[-1]/100000-1); cagr=float((equity[-1]/100000)**(D(252)/n)-1) if n>=252 else None
            sortedrr=sorted(rr); tail=sortedrr[:math.ceil(n*.05)]
            computed=dict(final_equity=float(equity[-1]),total_return=ret,cagr=cagr,average_daily_return=mean,
              max_drawdown=float(dd),peak_gross_exposure=peakgross,peak_beta_exposure=peakbeta,worst_day=min(rr),
              realized_volatility=sd*math.sqrt(252),var95_loss=-sortedrr[math.ceil(n*.05)-1],expected_shortfall95_loss=-statistics.mean(tail),
              max_underwater_sessions=longest,sharpe=mean/sd*math.sqrt(252) if sd>1e-12 else None,
              sortino=mean/downside*math.sqrt(252) if downside>1e-12 else None,
              calmar=cagr/float(dd) if cagr is not None and dd>num(1e-12) else None,
              exposure_adjusted_total_return=ret/statistics.mean(exposures) if statistics.mean(exposures)>1e-12 else None,
              average_exposure=statistics.mean(exposures),trades=fills,turnover=float(turn/100000),fees=float(fees),slippage=float(slip),
              rejected_orders=rejected,invalid_signals=invalid,missing_observations=missing,mean_cash_fraction=statistics.mean(cashfrac),sessions=n)
            for key,value in computed.items():
                if value is None:
                    if m[key] is not None: errors.append({'check':key+' must be N/A'})
                else: check(m[key],value,'metric '+key,max(1e-8,abs(value)*1e-10))
            for key,(first,last,count) in monthly.items(): check(m['monthly_returns'][key]['return_'],last/first-1,'monthly return',1e-10)
        if n!=r['actual_sessions']: errors.append({'check':'session count'})
        if r['source_sha256']!=rec['source_sha256']: errors.append({'check':'source hash'})
        if r['dataset_sha256']!=ds['sha256']: errors.append({'check':'dataset identity'})
        for key in set(rule_counts)|set(r['violations']):
            if rule_counts[key]!=r['violations'].get(key,0): errors.append({'check':'compliance counter '+key,'actual':r['violations'].get(key,0),'expected':rule_counts[key]})
        expected_compliance='FAILED' if any(rule_counts.values()) or r['errors'] else 'PASS'
        if expected_compliance!=r['compliance']: errors.append({'check':'compliance verdict','expected':expected_compliance})
        audit={'run':str(path.parent.relative_to(OUT)),'sessions':n,'status':'PASS' if not errors else 'FAILED','checks_failed':len(errors),
         'max_absolute_numeric_difference':str(maxdiff),'errors':errors[:10]}
        audits.append(audit); actual_pairs.append((r['candidate'],r['dataset'],r['mode']))
        if errors: failures.append(audit)
        if len(audits)%100==0: print(json.dumps({'verified_runs':len(audits),'failed':len(failures)}),flush=True)
    expected={(r['id'],s+'_'+str(seed),'base') for r in registry for s in cfg['scenarios'] for seed in cfg['seeds']}
    absent=sorted(expected-set(actual_pairs)); duplicates=len(actual_pairs)-len(set(actual_pairs))
    summary={'status':'PASS' if not failures and not absent and not duplicates else 'FAILED',
      'method':'Independent Decimal cash/share/receivable ledger, independent causal input reconstruction and metric formulas; no engine metric functions imported',
      'runs':len(audits),'sessions':sum(a['sessions'] for a in audits),'failures':len(failures),'absent_base_runs':absent,'duplicate_run_keys':duplicates,
      'elapsed_seconds':time.perf_counter()-started,'script_sha256':digest(pathlib.Path(__file__).read_bytes()),'details':audits,
      'limitation':'Independent implementation in the same audit session, not an external human or second-agent review; exclusion/failure rank semantics reviewed separately'}
    write(OUT/'independent_verification_attempt_01.json',summary)
    print(json.dumps({k:v for k,v in summary.items() if k!='details'},indent=2))
    return 0 if summary['status']=='PASS' else 1
if __name__=='__main__': sys.exit(verify())
