import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from datapaths import dp
import numpy as np, pandas as pd
from scipy import stats as sp
from btos_parse import build
from btos_panel import demean, fe

def fe_trend(df, ycol, xcol, unit, trend=True):
    """Unit + period FE, optionally plus unit-specific linear time trends."""
    d=df[[unit,"t",ycol,xcol]].dropna().copy()
    if len(d)<40: return None
    u,uu=pd.factorize(d[unit].values); p,pu=pd.factorize(d["t"].values)
    tt=(d.t.values-d.t.values.mean())/d.t.values.std()
    X=[d[xcol].values]
    if trend:
        for k in range(len(uu)): X.append((u==k)*tt)
    X=np.column_stack(X); y=d[ycol].values
    M=demean(np.column_stack([X,y]),u,p,len(uu),len(pu))
    Xd,yd=M[:,:-1],M[:,-1]
    b,*_=np.linalg.lstsq(Xd,yd,rcond=None); r=yd-Xd@b
    XtX=np.linalg.pinv(Xd.T@Xd)
    meat=np.zeros((Xd.shape[1],)*2)
    for k in range(len(uu)):
        i=np.where(u==k)[0]
        if not len(i): continue
        s=Xd[i].T@r[i]; meat+=np.outer(s,s)
    G=len(uu); V=XtX@meat@XtX*(G/(G-1))
    se=float(np.sqrt(max(V[0,0],0))); t=b[0]/se
    return dict(b=b[0],se=se,t=t,p=2*(1-sp.norm.cdf(abs(t))),G=G,N=len(d))

def diffs(df, unit, cols, k=1):
    d=df.sort_values([unit,"t"]).copy()
    for c in cols:
        d["d_"+c]=d.groupby(unit)[c].diff(k)
    return d

PANELS=[("SECTOR old",dp("old_Sector.xlsx"),"Sector"),
        ("SECTOR new",dp("btos_Sector.xlsx"),"Sector"),
        ("STATE  old",dp("old_State.xlsx"),"State"),
        ("STATE  new",dp("btos_State.xlsx"),"State")]
OUT=[("employment","emp_net"),("revenue","rev_net"),("demand","dem_net"),("prices [placebo]","price_net")]

if __name__ == '__main__':
    print("="*100)
    print("DIAGNOSTIC 1: add UNIT-SPECIFIC LINEAR TRENDS")
    print("Unit FE do not absorb unit-specific trends. AI adoption is a smooth upward trend in")
    print("every unit, so anything else trending within a unit will correlate with it.")
    print("="*100)
    for lab,path,unit in PANELS:
        B=build(path,unit)
        print(f"\n{lab}    {'outcome':<20}{'no trends':>22}{'with unit trends':>26}")
        for ol,oc in OUT:
            a=fe(B,oc,"ai",unit); b=fe_trend(B,oc,"ai",unit)
            if not a or not b: continue
            print(f"{'':12}{ol:<20}{a['b']:>+9.4f} (p {a['p']:.3f}){b['b']:>+13.4f} (p {b['p']:.3f})")
    
    print("\n"+"="*100)
    print("DIAGNOSTIC 2: FIRST DIFFERENCES. Does a CHANGE in adoption predict a CHANGE in")
    print("employment? This removes every unit-specific trend by construction.")
    print("="*100)
    for lab,path,unit in PANELS:
        B=build(path,unit)
        D=diffs(B,unit,["ai","emp_net","rev_net","dem_net","price_net"])
        print(f"\n{lab}")
        print(f"  {'outcome':<22}{'coef':>10}{'se':>9}{'t':>7}{'p':>9}")
        for ol,oc in OUT:
            r=fe(D,"d_"+oc,"d_ai",unit)
            if not r: continue
            star=" **" if r["p"]<0.05 else " *" if r["p"]<0.10 else ""
            print(f"  {ol:<22}{r['b']:>+10.4f}{r['se']:>9.4f}{r['t']:>+7.2f}{r['p']:>9.4f}{star}")
        print(f"  units {r['G']}, cells {r['N']}")
    
    print("\n"+"="*100)
    print("DIAGNOSTIC 3: LONGER DIFFERENCES (6 fortnights, about 3 months)")
    print("="*100)
    for lab,path,unit in PANELS:
        B=build(path,unit)
        D=diffs(B,unit,["ai","emp_net","rev_net","dem_net","price_net"],k=6)
        print(f"\n{lab}")
        for ol,oc in OUT:
            r=fe(D,"d_"+oc,"d_ai",unit)
            if not r: continue
            star=" **" if r["p"]<0.05 else " *" if r["p"]<0.10 else ""
            print(f"  {ol:<22}{r['b']:>+10.4f}{r['se']:>9.4f}{r['t']:>+7.2f}{r['p']:>9.4f}{star}")
    