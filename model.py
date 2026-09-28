"""Deterministic one-year sensitivity model. Not NVIDIA guidance."""
import math
LIMITS={'growth':(-30,50),'margin':(-15,10),'days':(0,90),'capex':(0,30),'borrowing':(0,30)}
def project(v, assumptions):
    a={k:float(assumptions.get(k,0)) for k in LIMITS}
    for k,(lo,hi) in LIMITS.items():
        if not math.isfinite(a[k]) or not lo<=a[k]<=hi: raise ValueError(f'{k} must be between {lo} and {hi}')
    revenue=v['revenue']*(1+a['growth']/100)
    margin=v['gross']/v['revenue']+a['margin']/100
    operating=revenue*margin-v['opex']
    pretax=operating+v['interest_income']-v['interest_expense']+v['other_income']
    tax=max(0,pretax)*v['tax']/v['pretax']
    net=pretax-tax
    receivables=revenue/365*a['days']
    cfo=v['cfo']+net-v['net']-receivables
    capex=a['capex']*1000
    debt=a['borrowing']*1000
    cfi=v['cfi']-capex
    cff=v['cff']+debt
    ending=v['cash']+cfo+cfi+cff
    return dict(revenue=revenue,operating=operating,net=net,cfo=cfo,cfi=cfi,cff=cff,ending_cash=ending,receivables=receivables,free_cash_flow=cfo-v['capex']-v['capex_principal']-capex,debt=v['debt_current']+v['debt_long']+debt)
