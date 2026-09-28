import unittest, json, sqlite3, threading, urllib.request, urllib.error, subprocess, re
from http.server import ThreadingHTTPServer
from seed import initialize, dataset, ROOT
from model import project
from app import Handler
class FinancialTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  initialize();cls.data=dataset()
 def test_statements_reconcile(self):
  for p in self.data['periods']:
   v=p['values']
   with self.subTest(period=p['id']):
    self.assertEqual(v['assets'],v['liabilities']+v['equity'])
    self.assertEqual(v['revenue']-v['cost'],v['gross'])
    self.assertEqual(v['gross']-v['opex'],v['operating'])
    self.assertEqual(v['operating']+v['interest_income']-v['interest_expense']+v['other_income'],v['pretax'])
    self.assertEqual(v['pretax']-v['tax'],v['net'])
    self.assertEqual(v['opening_cash']+v['cfo']+v['cfi']+v['cff'],v['cash'])
    self.assertEqual(sum(v[k] for k in ['net','sbc','da','gains','cf_tax','cf_other','cf_ar','cf_inventory','cf_prepaid','cf_ap','cf_accrued','cf_long']),v['cfo'])
    self.assertEqual(sum(v[k] for k in ['cash','securities','ar','inventory','prepaid']),v['current_assets'])
    self.assertEqual(sum(v[k] for k in ['current_assets','ppe','lease_assets','goodwill','intangibles','deferred_tax','equity_investments','other_assets']),v['assets'])
    self.assertEqual(sum(v[k] for k in ['current_liabilities','debt_long','lease_liabilities','other_liabilities']),v['liabilities'])
    self.assertEqual(sum(v[k] for k in ['ap','accrued','debt_current']),v['current_liabilities'])
 def test_disclosed_free_cash_flow(self):
  for p,expected in zip(self.data['periods'],[60724,96575]):
   v=p['values'];self.assertEqual(v['cfo']-v['capex']-v['capex_principal'],expected)
 def test_model_sensitivities(self):
  for p in self.data['periods']:
   v=p['values'];base=project(v,{})
   self.assertAlmostEqual(base['ending_cash'],v['cash']+v['cash_change'])
   delay=project(v,{'days':15})
   self.assertAlmostEqual(base['ending_cash']-delay['ending_cash'],v['revenue']/365*15)
   self.assertAlmostEqual(project(v,{'capex':5})['ending_cash'],base['ending_cash']-5000)
   self.assertAlmostEqual(project(v,{'borrowing':5})['ending_cash'],base['ending_cash']+5000)
   self.assertLess(project(v,{'growth':-20,'margin':-5,'days':60,'capex':10})['ending_cash'],0)
 def test_bounds(self):
  for a in [{'days':-1},{'growth':51},{'margin':float('nan')},{'capex':float('inf')}]:
   with self.assertRaises(ValueError):project(self.data['periods'][0]['values'],a)
 def test_js_python_parity(self):
  text=(ROOT/'dist/app.js').read_text();fn=text[text.index('function calculate('):text.index('\nlet result;')]
  cases=[{}, {'growth':20,'capex':5},{'growth':-20,'margin':-5,'days':60,'capex':10},{'growth':50,'margin':10,'days':90,'capex':30,'borrowing':30}]
  for p in self.data['periods']:
   for case in cases:
    a=dict(growth=0,margin=0,days=0,capex=0,borrowing=0);a.update(case)
    code=fn+'\nconsole.log(JSON.stringify(calculate('+json.dumps(p['values'])+','+json.dumps(a)+')))'
    js=json.loads(subprocess.check_output(['node','-e',code]))
    for k,val in project(p['values'],a).items():self.assertAlmostEqual(js[k],val,places=7)
 def test_api(self):
  server=ThreadingHTTPServer(('127.0.0.1',0),Handler);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();base=f'http://127.0.0.1:{server.server_port}'
  try:
   with urllib.request.urlopen(base+'/api/data') as r:self.assertEqual(len(json.load(r)['periods']),2)
   with urllib.request.urlopen(base+'/') as r:self.assertIn(b'Company Wallet',r.read())
   body=json.dumps({'period':'FY2026','assumptions':{'days':15}}).encode()
   with urllib.request.urlopen(urllib.request.Request(base+'/api/project',body,{'Content-Type':'application/json'})) as r:self.assertIn('ending_cash',json.load(r))
   with self.assertRaises(urllib.error.HTTPError) as cm:urllib.request.urlopen(base+'/wallet.db')
   self.assertEqual(cm.exception.code,404)
  finally:server.shutdown();server.server_close()
if __name__=='__main__':unittest.main()
