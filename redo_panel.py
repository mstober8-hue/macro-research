"""
Re-run cps_panel_did.py's age-band panel with a DEFENSIBLE exposure measure.

cps_panel_did.py built rep = en * (1 - comp) where comp averaged EVERY row of the
O*NET work-context file across four incompatible scales (CX 1-5, CXP 0-100
category percentages that are 81% of the file, CT 1-3, CTP 0-100). The resulting
comp term correlates with a correctly-built complementarity term at r = +0.045.
exposure_measure_audit.py caught that the measure was broken and retracted the
POSITIVE result it produced (total employment, p=0.004) but never re-ran the age
bands, so the NULL on the age gradient still rests on the broken regressor.

This re-runs all six outcomes with:
  A. the repo's own correct construction (ai_replaceability_score.py: Scale ID CX,
     five named complementarity elements, min-max normalised)
  B. that score rank-transformed
  C. raw Eloundou GPT exposure
  D. raw exposure rank-transformed
  E. the broken composite, for reference
"""
import os, re, glob, numpy as np, pandas as pd
from scipy import stats as sp

HERE = "/Users/maxstober/Developer/Macro-Research"
DATA = os.path.join(HERE, "FRED-Data") + os.sep

COMP_VARS = ["Physical Proximity",
             "Face-to-Face Discussions with Individuals and Within Teams",
             "Deal With External Customers or the Public in General",
             "Health and Safety of Other Workers",
             "Consequence of Error"]

def soc6(c):
    m = re.match(r"(\d{2}-\d{4})", str(c)); return m.group(1) if m else None

el = pd.read_csv(DATA + "eloundou_gpt_occupational_exposure_scores.csv")
el.columns = [c.strip() for c in el.columns]
el["soc"] = el["O*NET-SOC Code"].map(soc6)
el["en_raw"] = el[["human_rating_beta", "dv_rating_beta"]].mean(axis=1)
el["en_dv"]  = pd.to_numeric(el["dv_rating_beta"], errors="coerce")
EL = el.dropna(subset=["soc"]).groupby("soc", as_index=False)[["en_raw","en_dv"]].mean()

wc = pd.read_csv(DATA + "onet_work_context_ratings.csv")
wc.columns = [c.strip() for c in wc.columns]
wc["cv"] = pd.to_numeric(wc["Data Value"], errors="coerce")
wc["soc"] = wc["O*NET-SOC Code"].map(soc6)

# --- correct complementarity
g = wc[(wc["Scale ID"] == "CX") & (wc["Element Name"].isin(COMP_VARS))]
piv = g.pivot_table(index="soc", columns="Element Name", values="cv")
piv = (piv - piv.min()) / (piv.max() - piv.min())
GOOD = pd.DataFrame({"comp_good": piv.mean(axis=1)}).reset_index()

# --- broken complementarity (what cps_panel_did.py used)
B = wc.dropna(subset=["soc","cv"]).groupby("soc", as_index=False)["cv"].mean()
B["comp_bad"] = (B.cv - B.cv.min()) / (B.cv.max() - B.cv.min())

R = EL.merge(GOOD, on="soc", how="left").merge(B[["soc","comp_bad"]], on="soc", how="left")
R["comp_good"] = R.comp_good.fillna(R.comp_good.median())
R["comp_bad"]  = R.comp_bad.fillna(R.comp_bad.median())
R["en_mm"] = (R.en_raw - R.en_raw.min()) / (R.en_raw.max() - R.en_raw.min())
R["rep_good"] = R.en_mm * (1 - R.comp_good)
R["rep_bad"]  = R.en_dv * (1 - R.comp_bad)

XW = pd.read_csv(DATA + "occ2010_soc_crosswalk.csv")
COLS = ["rep_good","rep_bad","en_raw","comp_good"]
def lookup(soc):
    hit = R[R.soc == soc]
    if len(hit): return [hit[c].iloc[0] for c in COLS]
    for n in (5, 2):
        hit = R[R.soc.str.startswith(soc[:n])]
        if len(hit): return [hit[c].mean() for c in COLS]
    return [np.nan]*len(COLS)
got = np.array([lookup(s) for s in XW.soc])
for i,c in enumerate(COLS): XW[c] = got[:,i]
OCC = XW[["occ","title"]+COLS].dropna(subset=["rep_good"]).drop_duplicates("occ")

P = pd.read_csv(os.path.join(HERE, "cps_panel.csv"))
W = P.pivot_table(index=["occ","year"], columns="band", values="emp",
                  aggfunc="sum").fillna(0.0).reset_index()
W = W.merge(OCC, on="occ", how="left")
D = W[(W.year >= 2016) & W.rep_good.notna()].copy()
D["tot"] = D[["a20_24","a25_34","a35p"]].sum(axis=1)
D = D[(D.a20_24 > 0) & (D.tot > 0)].copy()
D["ly"] = np.log(D.a20_24); D["l2534"] = np.log(D.a25_34.clip(lower=1))
D["lo"] = np.log(D.a35p.clip(lower=1)); D["ltot"] = np.log(D.tot)
D["share"] = 100 * D.a20_24 / D.tot
for c in COLS: D[c+"_rk"] = D[c].rank(pct=True)

def fe_did(df, ycol, xcol, wcol="tot", post_from=2023, yr_lo=2016, yr_hi=9999):
    d = df[(df.year>=yr_lo)&(df.year<=yr_hi)].copy()
    d["post"] = (d.year >= post_from).astype(float)
    z = (d[xcol] - d[xcol].mean()) / d[xcol].std()
    od = pd.get_dummies(d.occ, prefix="o", drop_first=True).astype(float)
    yd = pd.get_dummies(d.year, prefix="y", drop_first=True).astype(float)
    X = np.column_stack([np.ones(len(d)), (z*d.post).to_numpy(), od.to_numpy(), yd.to_numpy()])
    y = d[ycol].to_numpy()
    w = np.ones(len(d)) if wcol is None else d[wcol].to_numpy()
    sw = np.sqrt(w/w.mean()); Xw, yw = X*sw[:,None], y*sw
    b,*_ = np.linalg.lstsq(Xw, yw, rcond=None); r = yw - Xw@b
    XtX = np.linalg.pinv(Xw.T@Xw); meat = np.zeros((X.shape[1],)*2)
    for _, idx in d.groupby("occ").indices.items():
        s = Xw[idx].T@r[idx]; meat += np.outer(s,s)
    G = d.occ.nunique(); V = XtX@meat@XtX*(G/max(G-1,1))
    se = float(np.sqrt(max(V[1,1],0))); t = b[1]/se
    return b[1], se, t, 2*(1-sp.norm.cdf(abs(t))), G, len(d)

OUTCOMES = [("log emp 20-24","ly"),("log emp 25-34","l2534"),
            ("log emp 35+  [PLACEBO]","lo"),("log TOTAL emp","ltot"),
            ("young SHARE (pp)","share")]
MEASURES = [("A  rep, correct CX + 5 elements","rep_good"),
            ("B  rep correct, rank transformed","rep_good_rk"),
            ("C  raw Eloundou exposure","en_raw"),
            ("D  raw exposure, rank transformed","en_raw_rk"),
            ("E  rep BROKEN (as in cps_panel_did)","rep_bad")]

print("="*100)
print("AGE-BAND PANEL RE-RUN WITH A DEFENSIBLE EXPOSURE MEASURE")
print("employment-weighted, occupation + year FE, clustered on occupation, 2016-2026, post = 2023+")
print("="*100)
for mlab, mcol in MEASURES:
    print(f"\n{mlab}")
    print(f"  {'outcome':<26}{'coef':>10}{'se':>9}{'t':>7}{'p':>9}")
    for olab, ocol in OUTCOMES:
        b,se,t,p,G,N = fe_did(D, ocol, mcol)
        star = " ***" if p<0.01 else " **" if p<0.05 else " *" if p<0.10 else ""
        print(f"  {olab:<26}{b:>+10.4f}{se:>9.4f}{t:>+7.2f}{p:>9.4f}{star}")
print(f"\n  clusters {G}, cells {N}")

print("\n" + "="*100)
print("PRE-AI PLACEBO: same design, 2016-2019 only, fake post = 2018+")
print("="*100)
for mlab, mcol in MEASURES[:4]:
    print(f"\n{mlab}")
    for olab, ocol in OUTCOMES:
        b,se,t,p,G,N = fe_did(D, ocol, mcol, post_from=2018, yr_lo=2016, yr_hi=2019)
        print(f"  {olab:<26}{b:>+10.4f}{se:>9.4f}{t:>+7.2f}{p:>9.4f}")
