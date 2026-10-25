"""Executed Stage 3F harness controls; standard library; no old tests or data loaded."""
import ast, copy, importlib.util, json, math, pathlib, statistics, sys, time, unittest
ROOT=pathlib.Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('stage3f',ROOT/'research/simulations/v30_stage3f_20261025_tournament.py')
t=importlib.util.module_from_spec(spec); spec.loader.exec_module(t)
C=json.loads((t.OUT/'configuration_preregistered.json').read_text())
R=json.loads((t.OUT/'inventory.json').read_text())

def fixture(prices,actions=None):
    dates=t.weekdays(len(prices)); bars={'SPY':[dict(ts=d,open=p,high=p,low=p,close=p,volume=1000) for d,p in zip(dates,prices)]}
    d=dict(id='micro_fixture',scenario='micro',seed=0,classification='SYNTHETIC',bars=bars,actions=actions or [],eval_dates=dates[1:],warmup_dates=dates[:1])
    d['sha256']=t.digest(t.canon(d)); return d
def record(code):
    sh=t.snapshot(code.encode()); return dict(id='UNIT_CONTROL',label='unit control only',source_path='Stage3F unit fixture',source_sha256=sh,
      entry='decide',kind='function',extract=False,args=[],kwargs={},dependency_sources={})
BUY=record("done=False\ndef decide(m,p,c):\n global done\n if done: return []\n done=True\n return [{'ticker':'SPY','side':'buy','quantity':1000}]\n")
def micro(data,r=BUY,mode='zero_cost'):
    return t.run_one(r,data,t.prepare_frames(data),C,mode,retain=False)

class Controls(unittest.TestCase):
    def test_01_equal_initial_cash(self):
        for r in [BUY,R[0],R[31]]:
            result,rows,j=micro(fixture([100,100]),r)
            self.assertEqual(j[0]['cash_before_orders'],100000)
    def test_02_identical_input_data(self):
        d=t.generate('bull',t.SEEDS[0],C); f=t.prepare_frames(d)[:2]
        outputs=[t.run_one(r,d,f,C,retain=False)[2] for r in [R[0],R[31]]]
        self.assertEqual([x['input_sha256'] for x in outputs[0]],[x['input_sha256'] for x in outputs[1]])
    def test_03_equal_timing(self):
        d=fixture([100,110]); a=micro(d); b=micro(d)
        self.assertEqual(a[2],b[2]); self.assertEqual(a[2][0]['events'][0]['raw_price'],110)
        self.assertLess(a[2][0]['prior_max_date'],a[2][0]['date'])
    def test_04_no_future_information(self):
        d=fixture([100,100,1,10000]); f=t.prepare_frames(d)
        for x in f:
            self.assertTrue(all(b['ts']<x['date'] for bs in x['market'].values() for b in bs))
        d2=copy.deepcopy(d); d2['bars']['SPY'][-1]['close']=999999
        self.assertEqual(f[0]['input_sha256'],t.prepare_frames(d2)[0]['input_sha256'])
    def test_05_identical_fees(self):
        args=([dict(ticker='SPY',side='buy',quantity=10)],100000,{}, {}, {'SPY':100},{'SPY':100},{'SPY'})
        a=t.execute_orders(*copy.deepcopy(args),commission_bps=10)[1][0]
        self.assertAlmostEqual(a['fee'],a['fill_price']*a['quantity']*.001)
    def test_06_identical_slippage(self):
        for sym,slip in [('SPY',.0005),('QLD',.001)]:
            ev=t.execute_orders([dict(ticker=sym,side='buy',quantity=10)],100000,{}, {},{sym:100},{sym:100},{sym})[1][0]
            self.assertAlmostEqual(ev['fill_price'],100*(1+slip))
    def test_07_corporate_action_conservation(self):
        dates=t.weekdays(5)
        actions=[dict(date=dates[2],ticker='SPY',type='split',ratio=2),
         dict(date=dates[3],ticker='SPY',type='dividend',amount=1,pay_date=dates[4])]
        result,rows,j=micro(fixture([100,100,50,49,49],actions))
        self.assertEqual(result['status'],'EXECUTED SUCCESSFULLY')
        for row in rows: self.assertAlmostEqual(row['equity'],100000)
        self.assertEqual(j[1]['positions']['SPY'],600)
        self.assertEqual(j[2]['receivables'][0]['amount'],600)
        self.assertEqual(j[3]['cash'],70600)
    def test_08_cash_conservation(self):
        cash,ev=t.execute_orders([dict(ticker='SPY',side='sell',quantity=5),dict(ticker='SPY',side='buy',quantity=1)],1000,{'SPY':10},{'SPY':100},{'SPY':100},{'SPY':100},{'SPY'},limits=False)
        self.assertAlmostEqual(cash,1000+5*99.95-100.05)
    def test_09_independent_state(self):
        a=t.IsolatedLoader(BUY); b=t.IsolatedLoader(BUY)
        try:
            f=a.load(); g=b.load(); self.assertTrue(f({}, {},100000)); self.assertFalse(f({}, {},100000)); self.assertTrue(g({}, {},100000))
        finally: a.close(); b.close()
    def test_10_deterministic_replay(self):
        a=micro(fixture([100,101,99,102])); b=micro(fixture([100,101,99,102]))
        self.assertEqual(a[2],b[2]); self.assertEqual(a[0]['metrics'],b[0]['metrics'])
    def test_11_missing_bar(self):
        d=fixture([100,100,100,100]); d['bars']['SPY'].pop(2)
        result,rows,j=micro(d); self.assertEqual(rows[1]['equity'],rows[0]['equity'])
        self.assertEqual(rows[1]['missing'],1)
        _,ev=t.execute_orders([dict(ticker='SPY',side='buy',quantity=1)],100000,{}, {},{}, {'SPY':100},{'SPY'})
        self.assertEqual(ev[0]['reason'],'missing_open')
    def test_12_invalid_orders(self):
        orders=[None,{},dict(ticker='SPY',side='buy',quantity=float('nan')),dict(ticker='SPY',side='sell',quantity=-1),dict(ticker='XYZ',side='buy',quantity=1)]
        cash,ev=t.execute_orders(orders,100000,{}, {},{'SPY':100},{'SPY':100},{'SPY'})
        self.assertEqual(cash,100000); self.assertEqual(len(ev),5); self.assertTrue(all(e['status']=='REJECTED' for e in ev))
    def test_13_concentration_limit(self):
        pos={}; cash,ev=t.execute_orders([dict(ticker='SPY',side='buy',quantity=100000)],100000,pos,{}, {'SPY':100},{'SPY':100},{'SPY'})
        self.assertLessEqual(pos['SPY']*ev[0]['fill_price'],30000+1e-8)
    def test_14_leverage_limit(self):
        pos={}; names=['TQQQ','SOXL','UPRO']; px={n:100 for n in names}
        cash,ev=t.execute_orders([dict(ticker=n,side='buy',quantity=10000) for n in names],100000,pos,{},px,px,set(names))
        equity=cash+sum(q*100 for q in pos.values())
        self.assertLessEqual(sum(q*300 for q in pos.values())/equity,1.5+1e-6)
    def test_15_drawdown_initial_equity(self):
        result,rows,j=micro(fixture([100,100,50]))
        self.assertAlmostEqual(result['metrics']['max_drawdown'],.15)
        self.assertAlmostEqual(result['metrics']['total_return'],-.15)
    def test_16_journal_reconciliation(self):
        result,rows,j=micro(fixture([100,101,99,103]))
        for x in j:
            total=x['cash']+sum(q*x['marks'][s] for s,q in x['positions'].items())+sum(a['amount'] for a in x['receivables'])
            self.assertAlmostEqual(total,x['equity'])
    def test_17_source_consistency(self):
        for r in R:
            self.assertEqual(t.digest((t.OUT/'sources'/(r['source_sha256']+'.py')).read_bytes()),r['source_sha256'])
    def test_18_tier3_boundary(self):
        for s in t.SCENARIOS:
            d=t.generate(s,t.SEEDS[0],C); self.assertLess(max(d['eval_dates']),'2022-01-01')
        self.assertFalse(json.loads((t.OUT/'data_provenance.json').read_text())['market_data_loaded'])
    def test_19_credential_io_denied(self):
        loader=t.IsolatedLoader(record("def decide(m,p,c):\n return open('never_open_this_credential_path')\n"))
        try:
            f=loader.load()
            with self.assertRaises(PermissionError): f({}, {},0)
        finally: loader.close()
    def test_20_broker_network_denied(self):
        loader=t.IsolatedLoader(record('import socket\ndef decide(m,p,c): return []\n'))
        try:
            with self.assertRaises(ImportError): loader.load()
        finally: loader.close()
    def test_21_frozen_integrity(self): self.assertTrue(all(v['match'] for v in t.checkpoint()['hashes'].values()))
    def test_22_no_git_mutations(self):
        before=json.loads((t.OUT/'checkpoint_before.json').read_text()); after=t.checkpoint()
        self.assertEqual(before,after)
    def test_23_complete_source_loading(self):
        for r in R:
            loader=t.IsolatedLoader(r)
            try: self.assertTrue(callable(loader.load()),r['id'])
            finally: loader.close()
    def test_24_failure_capture(self):
        bad=record("def decide(m,p,c):\n raise ValueError('injected failure')\n")
        result,rows,j=micro(fixture([100,100,100]),bad)
        self.assertEqual(result['status'],'FAILED'); self.assertEqual(len(result['errors']),2)
        self.assertEqual(len(j),2); self.assertTrue(all(x['error'] for x in j))
    def test_25_metric_recomputation(self):
        result,rows,j=micro(fixture([100,100,80,110]))
        eq=[100000]+[x['equity'] for x in j]; rr=[b/a-1 for a,b in zip(eq,eq[1:])]
        self.assertAlmostEqual(result['metrics']['sharpe'],statistics.mean(rr)/statistics.stdev(rr)*math.sqrt(252))
        self.assertAlmostEqual(math.prod(1+x for x in rr)-1,result['metrics']['total_return'])
    def test_26_zero_variance_na(self):
        result,_,_=micro(fixture([100,100,100]))
        for k in ['sharpe','sortino','calmar','cagr']: self.assertIsNone(result['metrics'][k])
    def test_27_sell_before_buy_and_limit(self):
        pos={'SPY':10}; px={'SPY':100,'QQQ':100}
        cash,ev=t.execute_orders([dict(ticker='QQQ',side='buy',quantity=5),dict(ticker='SPY',side='sell',quantity=10)],0,pos,{},px,px,set(px))
        self.assertEqual(ev[0]['side'],'sell'); self.assertTrue(pos.get('QQQ',0)>0)
        _,ev=t.execute_orders([dict(ticker='SPY',side='buy',quantity=1)]*101,100000,{}, {},px,px,set(px))
        self.assertEqual(sum(e['status'] in ['FILLED','PARTIAL'] for e in ev),50)
        self.assertTrue(any(e.get('reason')=='order_limit' for e in ev))
    def test_28_local_runner_parity_on_common_domain(self):
        # Compile only pure run_bot and beta AST from the local authority; no live_runner imports/top-level execution.
        source=(ROOT/'live_runner.py').read_text(encoding='utf-8'); tree=ast.parse(source)
        nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['run_bot','beta']]
        ns=dict(math=math,SCORE_START='2000-01-03',START_CASH=100000.,SLIP_EQUITY=.0005,SLIP_LEVERAGED=.001,
         MAX_NAME_WEIGHT=.3,MAX_BETA_GROSS=1.5,MAX_ORDERS_PER_DECISION=100,BETA_3X=t.B3,BETA_2X=t.B2)
        exec(compile(ast.Module(body=nodes,type_ignores=[]),'local_authority_extract','exec'),ns)
        d=t.generate('bull',t.SEEDS[0],C); d['eval_dates']=d['eval_dates'][:20]
        bars={s:[r for r in rs if r['ts']<=d['eval_dates'][-1]] for s,rs in d['bars'].items()}
        loader=t.IsolatedLoader(R[0])
        try: reference=ns['run_bot'](loader.load(),bars,d['eval_dates'][0])
        finally: loader.close()
        result,rows,j=t.run_one(R[0],d,t.prepare_frames(d),C,retain=False)
        self.assertEqual([round(x['equity'],2) for x in rows],reference['curve'])
        self.assertEqual(result['metrics']['trades'],reference['trades'])
    def test_29_synthetic_reproduction(self):
        self.assertEqual(t.generate('crash',310601,C),t.generate('crash',310601,C))
        self.assertNotEqual(t.generate('crash',310601,C)['sha256'],t.generate('crash',310619,C)['sha256'])
    def test_30_market_input_immutable(self):
        b=t.FrozenBar(close=1)
        with self.assertRaises(TypeError): b['close']=3
    def test_31_scratch_ast_exact(self):
        for r in R:
            if r['extract']:
                raw=(t.OUT/'sources'/(r['source_sha256']+'.py')).read_bytes()
                self.assertEqual(raw,(ROOT/r['source_path']).read_bytes())
                self.assertTrue(any(n.name==r['entry'] for n in ast.parse(raw).body if isinstance(n,(ast.FunctionDef,ast.ClassDef))))

if __name__=='__main__':
    attempt=sys.argv[1] if len(sys.argv)>1 else '01'
    log=t.OUT/('tests_attempt_'+attempt+'.txt')
    started=time.perf_counter()
    with log.open('x',encoding='utf-8') as f:
        result=unittest.TextTestRunner(stream=f,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Controls))
    ledger={'attempt':attempt,'command':'python -B research/tests/test_v30_stage3f_20261025_tournament.py '+attempt,
      'tests':result.testsRun,'failures':[(str(x),s) for x,s in result.failures],
      'errors':[(str(x),s) for x,s in result.errors], 'elapsed_seconds':time.perf_counter()-started,
      'exit_code':0 if result.wasSuccessful() else 1,'passed':result.testsRun-len(result.errors)-len(result.failures),
      'harness_sha256':t.digest(pathlib.Path(t.__file__).read_bytes()),'test_sha256':t.digest(pathlib.Path(__file__).read_bytes())}
    t.write(t.OUT/('tests_attempt_'+attempt+'.json'),ledger)
    print(log.read_text()); sys.exit(ledger['exit_code'])
