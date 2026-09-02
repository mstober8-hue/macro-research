"""
BTOS panel: measured AI adoption against measured employment change,
same firms, same survey, same fortnight. Unit and period fixed effects.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from datapaths import dp
import numpy as np, pandas as pd
from scipy import stats as sp
from btos_parse import build

def demean(M, u, p, n_u, n_p, iters=80, tol=1e-12):
    M=M.astype(float).copy()
    cu=np.bincount(u,minlength=n_u); cp=np.bincount(p,minlength=n_p)
    for _ in range(iters):
        prev=M.copy()
        for j in range(M.shape[1]):
            M[:,j]-=(np.bincount(u,weights=M[:,j],minlength=n_u)/cu)[u]
        for j in range(M.shape[1]):
            M[:,j]-=(np.bincount(p,weights=M[:,j],minlength=n_p)/cp)[p]
        if np.max(np.abs(M-prev))<tol: break
    return M

def fe(df, ycol, xcol, unit):
    d=df[[unit,"t",ycol,xcol]].dropna()
    if d[unit].nunique()<3 or len(d)<30: return None
    u,uu=pd.factorize(d[unit].values); p,pu=pd.factorize(d["t"].values)
    M=demean(np.column_stack([d[xcol].values,d[ycol].values]),u,p,len(uu),len(pu))
    x,y=M[:,0],M[:,1]
    sxx=(x*x).sum()
    if sxx<=0: return None
    b=(x*y).sum()/sxx; r=y-b*x
    s=np.bincount(u,weights=x*r,minlength=len(uu))
    G=len(uu); V=(s**2).sum()/sxx**2*(G/(G-1))
    se=float(np.sqrt(max(V,0))); t=b/se
    return dict(b=b,se=se,t=t,p=2*(1-sp.norm.cdf(abs(t))),G=G,N=len(d))

def circ_shift_p(df, ycol, xcol, unit, nboot=2000, seed=7):
    """Circular-shift the X series within each unit. Preserves each series'
    own autocorrelation, destroys the cross relationship. The project's
    stats_inference.py logic, applied within panel units."""
    obs=fe(df,ycol,xcol,unit)
    if obs is None: return None
    rng=np.random.default_rng(seed)
    d=df[[unit,"t",ycol,xcol]].dropna().sort_values([unit,"t"]).reset_index(drop=True)
    idx={k:v.values for k,v in d.groupby(unit).groups.items()}
    null=np.empty(nboot)
    for i in range(nboot):
        dd=d.copy()
        for k,ii in idx.items():
            v=d.loc[ii,xcol].values
            dd.loc[ii,xcol]=np.roll(v,rng.integers(1,len(v)) if len(v)>1 else 0)
        r=fe(dd,ycol,xcol,unit)
        null[i]=r["b"] if r else np.nan
    null=null[~np.isnan(null)]
    return obs, (np.abs(null)>=abs(obs["b"])).mean(), null.std()

def lead(df, unit, h, col="emp_net"):
    d=df.copy().sort_values([unit,"t"])
    d["y_lead"]=d.groupby(unit)[col].shift(-h)
    return d

PANELS=[("SECTOR, old AI question (2023-09 to 2025-09)",dp("old_Sector.xlsx"),"Sector"),
        ("SECTOR, new AI question (2025-11 to 2026-08)",dp("btos_Sector.xlsx"),"Sector"),
        ("STATE,  old AI question (2023-09 to 2025-09)",dp("old_State.xlsx"),"State"),
        ("STATE,  new AI question (2025-11 to 2026-08)",dp("btos_State.xlsx"),"State")]

if __name__ == '__main__':
    print("="*104)
    print("BTOS PANEL: does MEASURED AI adoption predict employment change in the same units?")
    print("Unit and period fixed effects. No 2022 step dummy, no theoretical exposure score.")
    print("Outcome: net employment diffusion (% firms increasing minus % decreasing), in pp.")
    print("Regressor: % of firms using AI. Coefficient is pp of net employment per 1pp of AI use.")
    print("="*104)
    
    store={}
    for lab,path,unit in PANELS:
        B=build(path,unit); store[lab]=(B,unit)
        print(f"\n{lab}")
        print(f"  {'outcome':<34}{'coef':>10}{'se':>9}{'t':>7}{'p(clust)':>10}{'p(shift)':>10}")
        for ylab,ycol in [("employment, contemporaneous","emp_net"),
                          ("revenue/sales","rev_net"),
                          ("demand","dem_net"),
                          ("own prices [placebo]","price_net")]:
            r=circ_shift_p(B,ycol,"ai",unit,nboot=600)
            if r is None: print(f"  {ylab:<34}{'insufficient data':>46}"); continue
            o,ps,nsd=r
            print(f"  {ylab:<34}{o['b']:>+10.4f}{o['se']:>9.4f}{o['t']:>+7.2f}{o['p']:>10.4f}{ps:>10.4f}")
        print(f"  units {o['G']}, cells {o['N']}")
    
    print("\n"+"="*104)
    print("DOES AI ADOPTION LEAD EMPLOYMENT? Outcome is employment h fortnights ahead.")
    print("="*104)
    for lab,path,unit in PANELS:
        B,_=store[lab]
        print(f"\n{lab}")
        print(f"  {'horizon':<20}{'coef':>10}{'se':>9}{'t':>7}{'p':>9}")
        for h in [0,1,2,3,4,6,8]:
            d=lead(B,unit,h)
            r=fe(d,"y_lead","ai",unit)
            if r is None: continue
            star=" **" if r["p"]<0.05 else " *" if r["p"]<0.10 else ""
            print(f"  h = {h:<2} ({h*2:>2} weeks)   {r['b']:>+10.4f}{r['se']:>9.4f}{r['t']:>+7.2f}{r['p']:>9.4f}{star}")
    
    print("\n"+"="*104)
    print("FORWARD-LOOKING: expected AI use in 6 months vs expected employment in 6 months")
    print("="*104)
    for lab,path,unit in PANELS:
        B,_=store[lab]
        r=fe(B,"emp_exp_net","ai_exp",unit)
        if r is None: print(f"  {lab:<48} unavailable"); continue
        print(f"  {lab:<48}{r['b']:>+10.4f}{r['se']:>9.4f}{r['t']:>+7.2f}{r['p']:>9.4f}   units {r['G']}, cells {r['N']}")
    