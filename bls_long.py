import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from datapaths import dp
import re, sys, numpy as np, pandas as pd
sys.path.insert(0,'.')
exec(open('redo_panel.py').read().split('OUTCOMES = [')[0])
from bls_parse import load
from fastfe import fe_did

def norm(t):
    t=str(t).lower()
    t=re.sub(r"[^a-z0-9 ]"," ",t)
    t=re.sub(r"\b(occupations?|workers?|and|other|all|misc|miscellaneous|nec|including)\b"," ",t)
    return re.sub(r"\s+"," ",t).strip()

X=OCC[["occ","title","rep_good"]].copy(); X["k"]=X.title.map(norm)
X=X.drop_duplicates("k")

frames=[]
for y in range(2011,2023):
    d=load(dp(f"aa{y}.htm"),y)
    d=d[~d.title.str.lower().str.startswith("total employed")]
    d["k"]=d.title.map(norm)
    m=d.merge(X[["k","occ","rep_good"]],on="k",how="inner").drop_duplicates(["occ","year"])
    frames.append(m)
    if y in (2011,2015,2019,2022):
        print(f"  {y}: {len(d)} leaf rows -> {len(m)} matched, "
              f"{100*m.tot.sum()/d.tot.sum():.1f}% of employment")
B=pd.concat(frames)
B=B[(B.tot>0)&B.a20_24.notna()].copy()
B["share"]=100*B.a20_24/B.tot
print(f"\nBLS panel: {B.occ.nunique()} occupations x {B.year.nunique()} years, {len(B)} cells")

cut=X.rep_good.quantile([1/3,2/3]).values
B["terc"]=np.where(B.rep_good>=cut[1],"high",np.where(B.rep_good<=cut[0],"low","mid"))
T=(B[B.terc!="mid"].groupby(["year","terc"])
   .apply(lambda g: np.average(g.share,weights=g.tot),include_groups=False).unstack())
T["gap"]=T["high"]-T["low"]
print("\n"+"="*78)
print("ASK 3 (partial): PUBLISHED BLS TABLES 2011-2022, young 20-24 share by tercile")
print("Independent of the IPUMS microdata. 2016-2019 overlaps and can be compared.")
print("="*78)
print(T.round(2).to_string())

for a,b in [(2011,2015),(2011,2019),(2015,2019),(2019,2022)]:
    sl=np.polyfit(T.loc[a:b].index,T.loc[a:b,"gap"],1)[0]
    print(f"  gap trend {a}-{b}: {sl:+.3f} pp/yr")

print("\n" + "="*78)
print("The same two-way FE test, run on the pre-2016 BLS years only")
print("="*78)
B["tot_w"]=B.tot
for lo,hi,post,lab in [(2011,2019,2016,"2011-2019, fake post 2016"),
                       (2011,2015,2013,"2011-2015, fake post 2013"),
                       (2011,2022,2020,"2011-2022, fake post 2020"),
                       (2016,2022,2020,"2016-2022, fake post 2020")]:
    d=B[(B.year>=lo)&(B.year<=hi)].rename(columns={"tot_w":"tot2"}).copy()
    d["tot"]=d["tot2"]
    r=fe_did(d,"share",d.rep_good.values,wcol="tot",post_from=post)
    print(f"  {lab:<34}{r[0]:>+9.4f}  t {r[2]:>+5.2f}  p {r[3]:.4f}   (occ {r[4]}, N {r[5]})")
B.to_csv("bls_occ_age_2011_2022.csv",index=False)
print("\n  written: bls_occ_age_2011_2022.csv")
