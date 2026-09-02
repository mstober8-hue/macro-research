import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from datapaths import dp
import re, sys, numpy as np, pandas as pd
sys.path.insert(0,'.')
exec(open('redo_panel.py').read().split('OUTCOMES = [')[0])
from bls_parse import load
from fastfe import fe_did, _demean
from scipy import stats as sp

def norm(t):
    t=str(t).lower(); t=re.sub(r"[^a-z0-9 ]"," ",t)
    t=re.sub(r"\b(occupations?|workers?|and|other|all|misc|miscellaneous|nec|including)\b"," ",t)
    return re.sub(r"\s+"," ",t).strip()
X=OCC[["occ","title","rep_good"]].copy(); X["k"]=X.title.map(norm); X=X.drop_duplicates("k")
bl=[]
for y in range(2011,2023):
    d=load(dp(f"aa{y}.htm"),y); d=d[~d.title.str.lower().str.startswith("total employed")]
    d["k"]=d.title.map(norm)
    bl.append(d.merge(X[["k","occ","rep_good"]],on="k",how="inner").drop_duplicates(["occ","year"]))
B=pd.concat(bl); B=B[(B.tot>0)&B.a20_24.notna()].copy(); B["share"]=100*B.a20_24/B.tot

def step_and_trend(d,yb,with_trend=True):
    w=d.tot.values/d.tot.mean()
    z=((d.rep_good-d.rep_good.mean())/d.rep_good.std()).values
    t=(d.year.values-d.year.values.mean())
    cols=[z*(d.year.values>=yb)]
    if with_trend: cols.append(z*t)
    Xm=np.column_stack(cols); y=d["share"].values.reshape(-1,1)
    o_,ou=pd.factorize(d.occ.values); p_,pu=pd.factorize(d.year.values)
    M=_demean(np.hstack([Xm,y]),o_,p_,w,len(ou),len(pu))
    Xt,yt=M[:,:-1],M[:,-1]; sw=np.sqrt(w)
    b,*_=np.linalg.lstsq(Xt*sw[:,None],yt*sw,rcond=None); r=yt-Xt@b
    XtX=np.linalg.pinv((Xt*w[:,None]).T@Xt); k=Xt.shape[1]; mt=np.zeros((k,k))
    for g in np.unique(o_):
        i=np.where(o_==g)[0]; s=(Xt[i]*w[i,None]).T@r[i]; mt+=np.outer(s,s)
    G=len(ou); se=np.sqrt(np.maximum(np.diag(XtX@mt@XtX*(G/(G-1))),0))
    return b[0],se[0],b[0]/se[0]

print("="*94)
print("BREAK-DATE SEARCH RUN SEPARATELY ON EACH SOURCE (no splice), t-stat on the step")
print("Column 2 adds an exposure-specific LINEAR TREND, so the step must beat a trend.")
print("="*94)
print(f"\n  {'break':<8}{'BLS 2011-2022':>18}{'+trend':>12}   {'CPS 2016-2026':>18}{'+trend':>12}")
for yb in range(2014,2025):
    row=f"  {yb:<8}"
    for src,dd,lo,hi in [("BLS",B,2011,2022),("CPS",D,2016,2026)]:
        if yb<=lo or yb>hi: row+=f"{'-':>18}{'-':>12}"; continue
        s=dd[(dd.year>=lo)&(dd.year<=hi)]
        b0,se0,t0=step_and_trend(s,yb,False)
        b1,se1,t1=step_and_trend(s,yb,True)
        row+=f"{b0:>+11.3f} (t{t0:>+5.2f}){t1:>+12.2f}"
    print(row)

print("\n"+"="*94)
print("WHAT A PURE TREND WOULD LOOK LIKE: simulate a trending series with NO break")
print("and run the same search, to see where max |t| lands by construction.")
print("="*94)
rng=np.random.default_rng(3)
d=D.copy()
z=((d.rep_good-d.rep_good.mean())/d.rep_good.std()).values
occ_fx=pd.Series(rng.normal(0,3,d.occ.nunique()),index=d.occ.unique())
sim=d.copy()
sim["share"]=(d.occ.map(occ_fx).values + (-0.12)*z*(d.year.values-2021)
              + rng.normal(0,2.0,len(d)))
ts=[]
for yb in range(2018,2025):
    b0,se0,t0=step_and_trend(sim,yb,False); ts.append((yb,t0))
print("\n  pure-trend simulation, CPS window:")
print("   "+"  ".join(f"{y}:{t:+.2f}" for y,t in ts))
print(f"   max |t| at {max(ts,key=lambda x:abs(x[1]))[0]}  (sample midpoint is 2021)")

print("\n"+"="*94)
print("SPLICE ARTIFACT CHECK: is there a jump exactly at the 2015/2016 source seam?")
print("="*94)
J=B[["occ","year","share","tot"]].rename(columns={"share":"s_bls"}).merge(
    D[["occ","year","share"]].rename(columns={"share":"s_cps"}),on=["occ","year"])
for y in range(2016,2023):
    o=J[J.year==y]
    if len(o)<50: continue
    print(f"  {y}: BLS {np.average(o.s_bls,weights=o.tot):.2f}%  CPS {np.average(o.s_cps,weights=o.tot):.2f}%  "
          f"ratio {np.average(o.s_cps,weights=o.tot)/np.average(o.s_bls,weights=o.tot):.4f}  (n={len(o)})")
print("\n  A constant ratio across years means the splice rescale is safe.")
print("  A drifting ratio means the two sources diverge and the splice injects a trend.")
