"""
Ask 2: replace the theoretical exposure score with REVEALED AI usage (AEI),
then re-run the entry-level panel and the same falsification battery.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from datapaths import dp
import os, re, sys, numpy as np, pandas as pd
from scipy import stats as sp
sys.path.insert(0,'.')
from fastfe import fe_did, _demean

HERE="/Users/maxstober/Developer/Macro-Research"; DATA=HERE+"/FRED-Data/"

# The AEI release ships either as a long metric file or already pivoted by SOC.
# Accept both so this runs against whatever vintage is on disk.
_src = dp("aei_claude_ai_2026-06-26.csv")
_ren = {"pct": "use", "collaboration_bucket_automation_pct": "auto_sh",
        "collaboration_bucket_augmentation_pct": "aug_sh", "ai_autonomy_mean": "autonomy"}
# The AEI release ships either long (one row per metric) or already pivoted by SOC.
# Branch on the columns actually present, not on the filename.
_long = _src if "geo_level" in pd.read_csv(_src, nrows=0).columns else None
if _long:
    A = pd.read_csv(_long)
    A = A[(A.geo_level == "global") & (A.category_name == "soc_occupation")]
    A["soc"] = A.node_external_id.astype(str).str.extract(r"(\d{2}-\d{4})")[0]
    W = A.pivot_table(index="soc", columns="metric_id", values="value", aggfunc="mean")
    S = W[list(_ren)].rename(columns=_ren).reset_index().dropna(subset=["use"])
else:
    S = pd.read_csv(_src)
    S["soc"] = S.soc.astype(str).str.extract(r"(\d{2}-\d{4})")[0]
    S = S.rename(columns=_ren)[["soc"] + list(_ren.values())].dropna(subset=["use"])
S["auto_use"]=S.use*S.auto_sh/100.0
print(f"AEI occupations mapped to SOC6: {len(S)}")

XW=pd.read_csv(DATA+"occ2010_soc_crosswalk.csv")
def lk(soc,cols):
    h=S[S.soc==soc]
    if len(h): return [h[c].iloc[0] for c in cols]
    for n in (5,2):
        h=S[S.soc.str.startswith(soc[:n])]
        if len(h): return [h[c].mean() for c in cols]
    return [np.nan]*len(cols)
COLS=["use","auto_sh","aug_sh","autonomy","auto_use"]
got=np.array([lk(s,COLS) for s in XW.soc])
for i,c in enumerate(COLS): XW[c]=got[:,i]
OCC=XW[["occ","title"]+COLS].dropna(subset=["use"]).drop_duplicates("occ")

P=pd.read_csv(HERE+"/cps_panel.csv")
Wp=P.pivot_table(index=["occ","year"],columns="band",values="emp",aggfunc="sum").fillna(0.).reset_index()
Wp=Wp.merge(OCC,on="occ",how="left")
D=Wp[(Wp.year>=2016)&Wp.use.notna()].copy()
D["tot"]=D[["a20_24","a25_34","a35p"]].sum(axis=1)
D=D[(D.a20_24>0)&(D.tot>0)].copy()
D["share"]=100*D.a20_24/D.tot
D["ly"]=np.log(D.a20_24); D["ltot"]=np.log(D.tot); D["lo"]=np.log(D.a35p.clip(lower=1))
# usage intensity per worker: usage share divided by employment share
emp24=D[D.year==2024].groupby("occ").tot.sum()
D["empsh"]=D.occ.map(emp24/emp24.sum())*100
D["intensity"]=np.log((D.use/D.empsh.clip(lower=1e-6)).clip(lower=1e-6))
for c in ["use","auto_use","auto_sh","autonomy","intensity"]:
    D[c+"_rk"]=D[c].rank(pct=True)
    D.loc[D[c].isna(), c+"_rk"]=np.nan

print(f"panel: {D.occ.nunique()} occupations matched to AEI, {len(D)} cells")
print(f"employment coverage 2024: "
      f"{100*D[D.year==2024].tot.sum()/Wp[Wp.year==2024][['a20_24','a25_34','a35p']].sum().sum():.1f}%")
print("\ntop 8 occupations by AEI usage share:")
for _,x in OCC.nlargest(8,"use").iterrows(): print(f"   {x.use:6.2f}%  {x.title}")

MEAS=[("usage share (rank)","use_rk"),
      ("usage x automation share (rank)","auto_use_rk"),
      ("automation share of usage (rank)","auto_sh_rk"),
      ("AI autonomy mean (rank)","autonomy_rk"),
      ("usage intensity per worker (rank)","intensity_rk")]
OUTS=[("log emp 20-24","ly"),("log emp 35+","lo"),("log TOTAL emp","ltot"),("young SHARE (pp)","share")]

print("\n"+"="*98)
print("[1] ENTRY-LEVEL PANEL WITH REVEALED USAGE. Occupation + year FE, weighted, post=2023.")
print("="*98)
for ml,mc in MEAS:
    Dm=D[D[mc].notna()].copy()
    print(f"\n{ml}   [{Dm.occ.nunique()} occupations]")
    print(f"  {'outcome':<26}{'coef':>10}{'se':>9}{'t':>7}{'p':>9}")
    for ol,oc in OUTS:
        b,se,t,p,G,N=fe_did(Dm,oc,Dm[mc].values)
        st=" ***" if p<0.01 else " **" if p<0.05 else " *" if p<0.10 else ""
        print(f"  {ol:<26}{b:>+10.4f}{se:>9.4f}{t:>+7.2f}{p:>9.4f}{st}")
print(f"\n  clusters {G}, cells {N}")

print("\n"+"="*98)
print("[2] THE SAME FALSIFICATION BATTERY (young share)")
print("="*98)
def seg(dd,knot,xcol,label):
    ww=dd.tot.values/dd.tot.mean()
    zz=((dd[xcol]-dd[xcol].mean())/dd[xcol].std()).values
    t=dd.year.values.astype(float)-knot
    X=np.column_stack([zz*t,zz*np.maximum(t,0)]); y=dd["share"].values.reshape(-1,1)
    o_,ou=pd.factorize(dd.occ.values); y_,yu=pd.factorize(dd.year.values)
    M=_demean(np.hstack([X,y]),o_,y_,ww,len(ou),len(yu))
    Xt,yt=M[:,:-1],M[:,-1]; sw=np.sqrt(ww)
    b,*_=np.linalg.lstsq(Xt*sw[:,None],yt*sw,rcond=None); r=yt-Xt@b
    XtX=np.linalg.pinv((Xt*ww[:,None]).T@Xt); mt=np.zeros((2,2))
    for g in np.unique(o_):
        i=np.where(o_==g)[0]; s=(Xt[i]*ww[i,None]).T@r[i]; mt+=np.outer(s,s)
    G=len(ou); se=np.sqrt(np.maximum(np.diag(XtX@mt@XtX*(G/(G-1))),0))
    tc=b[1]/se[1]
    print(f"  {label:<40} pre-slope {b[0]:>+7.4f} (t {b[0]/se[0]:>+5.2f})  "
          f"slope CHANGE {b[1]:>+7.4f} (t {tc:>+5.2f}, p {2*(1-sp.norm.cdf(abs(tc))):.3f})")

for ml,mc in [("usage share","use_rk"),("usage x automation share","auto_use_rk"),
              ("usage intensity per worker","intensity_rk")]:
    Dm=D[D[mc].notna()].copy()
    print(f"\n  -- {ml} --")
    seg(Dm,2022,mc,"knot 2022")
    seg(Dm[Dm.year<=2025],2022,mc,"knot 2022, excl. partial 2026")
    seg(Dm[Dm.year<=2025],2019,mc,"PLACEBO knot 2019")
    seg(Dm[Dm.year<=2025],2020,mc,"PLACEBO knot 2020")
    pl=Dm[Dm.year<=2019]
    b,se,t,p,G,N=fe_did(pl,"share",pl[mc].values,post_from=2018)
    print(f"  {'PLACEBO window 2016-19, fake post 2018':<40}{b:>+10.4f} (t {t:+.2f}, p {p:.3f})")
    bu,seu,tu,pu,_,_=fe_did(Dm,"share",Dm[mc].values,wcol=None)
    print(f"  {'UNWEIGHTED':<40}{bu:>+10.4f} (t {tu:+.2f}, p {pu:.3f})")
