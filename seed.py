"""Transcribed public NVIDIA FY2026 results, USD millions. No synthetic facts."""
from pathlib import Path
import sqlite3, json
ROOT=Path(__file__).resolve().parent
SOURCE='https://investor.nvidia.com/news/press-release-details/2026/NVIDIA-Announces-Financial-Results-for-Fourth-Quarter-and-Fiscal-2026/default.aspx'
# code, label, statement, FY2025, FY2026
ROWS=[
('revenue','Revenue','income',130497,215938),('cost','Cost of revenue','income',32639,62475),('gross','Gross profit','income',97858,153463),('rd','Research & development','income',12914,18497),('sga','Selling, general & administrative','income',3491,4579),('opex','Total operating expenses','income',16405,23076),('operating','Operating profit','income',81453,130387),('interest_income','Interest income','income',1786,2300),('interest_expense','Interest expense','income',247,259),('other_income','Other income, net','income',1034,9022),('pretax','Profit before tax','income',84026,141450),('tax','Income tax expense','income',11146,21383),('net','Profit for the year','income',72880,120067),
('cash','Cash & cash equivalents','position',8589,10605),('securities','Current marketable securities','position',34621,51951),('liquidity','Cash + current marketable securities','derived',43210,62556),('ar','Trade receivables, net','position',23065,38466),('inventory','Inventories','position',10080,21403),('prepaid','Prepayments & other current assets','position',3771,3180),('current_assets','Total current assets','position',80126,125605),('ppe','Property & equipment, net','position',6283,10383),('lease_assets','Operating lease assets','position',1793,2867),('goodwill','Goodwill','position',5188,20832),('intangibles','Intangible assets, net','position',807,3306),('deferred_tax','Deferred tax assets','position',10979,13258),('equity_investments','Non-marketable equity securities','position',3387,22251),('other_assets','Other assets','position',3038,8301),('assets','Total assets','position',111601,206803),('ap','Trade payables','position',6310,9812),('accrued','Accrued & other current liabilities','position',11737,21352),('debt_current','Current debt','position',0,999),('current_liabilities','Total current liabilities','position',18047,32163),('debt_long','Non-current debt','position',8463,7469),('lease_liabilities','Non-current operating lease liabilities','position',1519,2572),('other_liabilities','Other non-current liabilities','position',4245,7306),('liabilities','Total liabilities','position',32274,49510),('equity','Total equity','position',79327,157293),
('sbc','Share-based compensation','cashflow',4737,6386),('da','Depreciation & amortisation','cashflow',1864,2843),('gains','Investment gains adjustment','cashflow',-1030,-8918),('cf_tax','Deferred tax adjustment','cashflow',-4477,-1424),('cf_other','Other operating adjustments','cashflow',-502,-287),('cf_ar','Change in receivables','cashflow',-13063,-15399),('cf_inventory','Change in inventories','cashflow',-4781,-11324),('cf_prepaid','Change in prepayments & other assets','cashflow',-395,577),('cf_ap','Change in payables','cashflow',3357,3096),('cf_accrued','Change in accrued liabilities','cashflow',4278,5257),('cf_long','Change in other long-term liabilities','cashflow',1221,1844),('cfo','Net operating cash flow','cashflow',64089,102718),('cfi','Net investing cash flow','cashflow',-20421,-52228),('cff','Net financing cash flow','cashflow',-42359,-48474),('opening_cash','Opening cash & equivalents','cashflow',7280,8589),('cash_change','Net change in cash','cashflow',1309,2016),('capex','Property, equipment & intangible purchases','supplement',3236,6042),('capex_principal','Related principal payments','supplement',129,101),('buybacks','Cash paid for share repurchases','supplement',33706,40086),('dividends','Dividends paid','supplement',834,974)]
def initialize():
    with sqlite3.connect(ROOT/'wallet.db') as c:
        c.executescript((ROOT/'schema.sql').read_text())
        c.executemany('INSERT OR IGNORE INTO periods VALUES (?, ?, ?)', [('FY2025','2025-01-26','US GAAP'),('FY2026','2026-01-25','US GAAP')])
        for code,label,section,a,b in ROWS:
            c.execute('INSERT OR REPLACE INTO metrics(code,label,section) VALUES(?,?,?)',(code,label,section))
            c.executemany('INSERT OR REPLACE INTO facts VALUES(?,?,?,?)',[(p,code,v,SOURCE) for p,v in [('FY2025',a),('FY2026',b)]])
def dataset():
    with sqlite3.connect(ROOT/'wallet.db') as c:
        c.row_factory=sqlite3.Row
        ps=[dict(r) for r in c.execute('SELECT * FROM periods ORDER BY id')]
        ms=[dict(r) for r in c.execute('SELECT * FROM metrics ORDER BY rowid')]
        for p in ps:p['values']={r['metric_code']:r['value'] for r in c.execute('SELECT * FROM facts WHERE period_id=?',(p['id'],))}
    return {'company':'NVIDIA','source':SOURCE,'source_date':'2026-02-25','unit':'USD millions','periods':ps,'metrics':ms}
if __name__=='__main__':
    initialize()
    (ROOT/'dist'/'data.json').write_text(json.dumps(dataset(),indent=2))
    print('SQLite database seeded; browser snapshot exported.')
