import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from datapaths import dp
import re, sys, numpy as np, pandas as pd
sys.path.insert(0,'.')
exec(open('redo_panel.py').read().split('OUTCOMES = [')[0])   # OCC, D (microdata 2016-2026)
from bls_parse import load
from fastfe import fe_did
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
B=pd.concat(bl); B=B[(B.tot>0)&B.a20_24.notna()].copy()
B["share"]=100*B.a20_24/B.tot

print("="*88)
print("VALIDATION: do the two independent sources agree where they overlap (2016-2019)?")
print("="*88)
M=D[["occ","year","share","tot"]].rename(columns={"share":"share_cps","tot":"tot_cps"})
J=B[["occ","year","share","tot"]].rename(columns={"share":"share_bls","tot":"tot_bls"}).merge(M,on=["occ","year"])
ov=J[(J.year>=2016)&(J.year<=2019)]
print(f"  {len(ov)} overlapping occupation-years")
print(f"  correlation of young share, BLS vs CPS microdata: r = {ov.share_bls.corr(ov.share_cps):+.3f}")
print(f"  mean absolute difference: {(ov.share_bls-ov.share_cps).abs().mean():.2f}pp")
print(f"  employment-weighted mean young share  BLS {np.average(ov.share_bls,weights=ov.tot_bls):.2f}%"
      f"   CPS {np.average(ov.share_cps,weights=ov.tot_cps):.2f}%")

# splice: BLS for 2011-2015, microdata for 2016-2026
b1=B[B.year<=2015][["occ","year","share","tot","rep_good"]].copy(); b1["src"]="BLS"
m1=D[["occ","year","share","tot","rep_good"]].copy(); m1["src"]="CPS"
# put BLS on the CPS scale using the overlap ratio, per tercile-free global factor
ratio=np.average(ov.share_cps,weights=ov.tot_cps)/np.average(ov.share_bls,weights=ov.tot_bls)
b1["share"]=b1.share*ratio
C=pd.concat([b1,m1]).sort_values(["occ","year"])
C=C[C.occ.isin(set(b1.occ)&set(m1.occ))]
print(f"\n  spliced panel: {C.occ.nunique()} occupations, {C.year.min()}-{C.year.max()}, "
      f"{len(C)} cells (BLS rescaled by {ratio:.4f})")

print("\n"+"="*88)
print("BREAK-DATE SEARCH: which year does the young-share divergence actually start?")
print("Two-way FE, employment weighted, one step dummy at a time. Best = largest |t|.")
print("="*88)
print(f"\n  {'break year':<14}{'coef':>10}{'se':>9}{'t':>8}{'p':>10}")
best=None
for yb in range(2013,2025):
    r=fe_did(C,"share",C.rep_good.values,post_from=yb)
    mark=""
    if best is None or abs(r[2])>abs(best[1]): best=(yb,r[2]); 
    print(f"  {yb:<14}{r[0]:>+10.4f}{r[1]:>9.4f}{r[2]:>+8.2f}{r[3]:>10.4f}")
print(f"\n  strongest break: {best[0]}  (t = {best[1]:+.2f})")

print("\n"+"="*88)
print("HORSE RACE: 2020 break and 2022 break in the SAME regression")
print("="*88)
from fastfe import _demean
d=C.copy(); w=d.tot.values/d.tot.mean()
z=((d.rep_good-d.rep_good.mean())/d.rep_good.std()).values
for combo in [((2020,2023),"2020 (COVID) vs 2023 (ChatGPT)"),((2019,2023),"2019 vs 2023"),
              ((2020,2022),"2020 vs 2022")]:
    (y1,y2),lab=combo
    X=np.column_stack([z*(d.year.values>=y1), z*(d.year.values>=y2)])
    y=d["share"].values.reshape(-1,1)
    o_,ou=pd.factorize(d.occ.values); p_,pu=pd.factorize(d.year.values)
    M2=_demean(np.hstack([X,y]),o_,p_,w,len(ou),len(pu))
    Xt,yt=M2[:,:-1],M2[:,-1]; sw=np.sqrt(w)
    b,*_=np.linalg.lstsq(Xt*sw[:,None],yt*sw,rcond=None); r=yt-Xt@b
    XtX=np.linalg.pinv((Xt*w[:,None]).T@Xt); mt=np.zeros((2,2))
    for g in np.unique(o_):
        i=np.where(o_==g)[0]; s=(Xt[i]*w[i,None]).T@r[i]; mt+=np.outer(s,s)
    G=len(ou); se=np.sqrt(np.maximum(np.diag(XtX@mt@XtX*(G/(G-1))),0))
    print(f"\n  {lab}")
    for k,yy in enumerate([y1,y2]):
        t=b[k]/se[k]
        print(f"    step at {yy}: {b[k]:>+9.4f}  se {se[k]:.4f}  t {t:>+5.2f}  p {2*(1-sp.norm.cdf(abs(t))):.4f}")
