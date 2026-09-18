"""
spec_checks_vs_canaries.py
Three specification checks aligning this project's entry-level result with
Brynjolfsson, Chandar & Chen (2026), "Canaries in the Coal Mine?" (August 2026).

WHY THESE THREE
Canaries' PRIMARY exposure measure is the Eloundou et al. GPT-4 beta rating, the
same family this project uses; the Anthropic Economic Index is their SECONDARY
measure, used to split automation from augmentation. So this project replicates
their primary specification rather than contradicting it. Three differences remain
and each is a live referee objection:

  1. AGE BAND. This project uses 20-24. Canaries uses 22-25. The 20-21 year olds
     are disproportionately students and part-time workers.
  2. FUNCTIONAL FORM. Canaries buckets occupations into exposure QUINTILES and
     compares the two most exposed against the three least exposed. This project
     uses a continuous z-scored regressor.
  3. EDUCATION. Canaries' abstract concedes their patterns "attenuate when
     controlling for education". This project's do not. That contrast is the
     single strongest claim available here, so it has to be airtight.

Reads cps_panel_bands.csv (build_cps_panel_bands.py) and FRED-Data/.
"""
import os, re, sys, numpy as np, pandas as pd
from scipy import stats as sp
sys.path.insert(0, "/Users/maxstober/Developer/Macro-Research")
from fastfe import _demean

HERE = "/Users/maxstober/Developer/Macro-Research"; DATA = HERE + "/FRED-Data/"
OEWS = DATA + "oews_national_industry_files/"
COMP_VARS = ["Physical Proximity",
             "Face-to-Face Discussions with Individuals and Within Teams",
             "Deal With External Customers or the Public in General",
             "Health and Safety of Other Workers", "Consequence of Error"]

def soc6(c):
    m = re.match(r"(\d{2}-\d{4})", str(c)); return m.group(1) if m else None

# ---- exposure -----------------------------------------------------------------
el = pd.read_csv(DATA + "eloundou_gpt_occupational_exposure_scores.csv")
el.columns = [c.strip() for c in el.columns]
el["soc"] = el["O*NET-SOC Code"].map(soc6)
el["en_raw"] = el[["human_rating_beta", "dv_rating_beta"]].mean(axis=1)
EL = el.dropna(subset=["soc"]).groupby("soc", as_index=False)["en_raw"].mean()
wc = pd.read_csv(DATA + "onet_work_context_ratings.csv"); wc.columns = [c.strip() for c in wc.columns]
wc["cv"] = pd.to_numeric(wc["Data Value"], errors="coerce"); wc["soc"] = wc["O*NET-SOC Code"].map(soc6)
g = wc[(wc["Scale ID"] == "CX") & (wc["Element Name"].isin(COMP_VARS))]
piv = g.pivot_table(index="soc", columns="Element Name", values="cv")
piv = (piv - piv.min()) / (piv.max() - piv.min())
R = EL.merge(pd.DataFrame({"comp": piv.mean(axis=1)}).reset_index(), on="soc", how="left")
R["comp"] = R.comp.fillna(R.comp.median())
R["en_mm"] = (R.en_raw - R.en_raw.min()) / (R.en_raw.max() - R.en_raw.min())
R["rep_good"] = R.en_mm * (1 - R.comp)

# ---- controls: Job Zone (education/preparation) and OEWS median wage -----------
jz = pd.read_csv(DATA + "onet_job_zones.txt", sep="\t"); jz.columns = [c.strip() for c in jz.columns]
jz["soc"] = jz["O*NET-SOC Code"].map(soc6)
JZ = jz.dropna(subset=["soc"]).groupby("soc", as_index=False)["Job Zone"].mean().rename(columns={"Job Zone": "jobzone"})
ow = pd.read_excel(OEWS + "oews_may2022_national_occupations.xlsx")
ow.columns = [c.strip().upper() for c in ow.columns]
gg = "O_GROUP" if "O_GROUP" in ow.columns else "OCC_GROUP"
ow = ow[ow[gg].astype(str).str.strip() == "detailed"].copy()
ow["soc"] = ow["OCC_CODE"].astype(str).map(soc6)
ow["wage"] = pd.to_numeric(ow["A_MEDIAN"], errors="coerce")
WG = ow.dropna(subset=["soc", "wage"]).groupby("soc", as_index=False)["wage"].mean()
CTL = JZ.merge(WG, on="soc", how="outer"); CTL["lwage"] = np.log(CTL.wage)
R = R.merge(CTL[["soc", "jobzone", "lwage"]], on="soc", how="left")

XW = pd.read_csv(DATA + "occ2010_soc_crosswalk.csv")
CS = ["rep_good", "en_raw", "jobzone", "lwage"]
def lookup(soc):
    h = R[R.soc == soc]
    if len(h): return [h[c].iloc[0] for c in CS]
    for n in (5, 2):
        h = R[R.soc.astype(str).str.startswith(str(soc)[:n])]
        if len(h): return [h[c].mean() for c in CS]
    return [np.nan] * len(CS)
got = np.array([lookup(s) for s in XW.soc])
for i, c in enumerate(CS): XW[c] = got[:, i]
OCC = XW[["occ"] + CS].dropna(subset=["rep_good"]).drop_duplicates("occ")

# ---- panel --------------------------------------------------------------------
P = pd.read_csv("cps_panel_bands.csv")
W = P.pivot_table(index=["occ", "year"], columns="band", values="emp", aggfunc="sum").fillna(0.0).reset_index()
W = W.merge(OCC, on="occ", how="inner")
# Total employment 16-64, reconstructed from the NON-OVERLAPPING bands only.
# a25 is a singleton band and it has to be here: u20, a20_24, a26_30, a31_34 and
# a35p leave a hole at exactly age 25, and an earlier version of this line dropped
# every 25-year-old from the denominator. That understated tot by ~2% and, worse,
# made share_2225 a ratio whose numerator (22-25) included people its denominator
# did not. a22_25 itself is excluded because it overlaps a20_24 by construction.
NONOVERLAP = ["u20", "a20_24", "a25", "a26_30", "a31_34", "a35p"]
missing = [c for c in NONOVERLAP if c not in W.columns]
assert not missing, f"rebuild cps_panel_bands.csv: missing {missing}"
W["tot"] = W[NONOVERLAP].sum(axis=1)
D = W[(W.year >= 2016)].copy()
D = D[(D.tot > 0) & (D.a20_24 > 0) & (D.a22_25 > 0)].copy()
D["share_2024"] = 100 * D.a20_24 / D.tot
D["share_2225"] = 100 * D.a22_25 / D.tot
D = D.dropna(subset=["jobzone", "lwage"])

def fe_multi(d, ycol, xcols, wcol="tot", post_from=2023):
    post = (d.year.values >= post_from).astype(float)
    X = np.column_stack([((d[c].values - d[c].values.mean()) / d[c].values.std()) * post for c in xcols])
    y = d[ycol].values.astype(float); w = d[wcol].values.astype(float); w = w / w.mean()
    oc, ou = pd.factorize(d.occ.values); yc, yu = pd.factorize(d.year.values)
    M = _demean(np.hstack([X, y.reshape(-1, 1)]), oc, yc, w, len(ou), len(yu))
    Xt, yt = M[:, :-1], M[:, -1]
    inv = np.linalg.pinv(Xt.T @ (w[:, None] * Xt)); b = inv @ (Xt.T @ (w * yt))
    r = yt - Xt @ b; meat = np.zeros((Xt.shape[1],) * 2)
    for gi in range(len(ou)):
        m = oc == gi
        if m.any():
            s = Xt[m].T @ (w[m] * r[m]); meat += np.outer(s, s)
    G = len(ou); V = inv @ (meat * (G / max(G - 1, 1))) @ inv
    se = np.sqrt(np.maximum(np.diag(V), 0)); t = b / se
    return b, se, t, 2 * (1 - sp.norm.cdf(np.abs(t))), G, len(d)

def line(lab, d, y, xs):
    b, se, t, p, G, n = fe_multi(d, y, xs)
    st = "***" if p[0] < .01 else ("**" if p[0] < .05 else ("*" if p[0] < .10 else ""))
    print(f"  {lab:<44}{b[0]:>+9.4f}{se[0]:>9.4f}{t[0]:>7.2f}{p[0]:>9.4f} {st}")
    return b, se, p

print("=" * 100)
print("CHECK 1  AGE BAND: this project's 20-24 against Canaries' 22-25")
print("=" * 100)
print(f"\n  occupations {D.occ.nunique()}, cells {len(D)}, 2016-2026, post = 2023")
print(f"\n  {'specification':<44}{'coef':>9}{'se':>9}{'t':>7}{'p':>9}")
for ycol, lab in [("share_2024", "20-24 share  (this project)"),
                  ("share_2225", "22-25 share  (Canaries band)")]:
    line(lab + ", composite exposure", D, ycol, ["rep_good"])
for ycol, lab in [("share_2024", "20-24 share  (this project)"),
                  ("share_2225", "22-25 share  (Canaries band)")]:
    line(lab + ", raw GPT-4 beta", D, ycol, ["en_raw"])

print("\n" + "=" * 100)
print("CHECK 2  QUINTILES: Canaries compare the 2 most exposed against the 3 least")
print("=" * 100)
u = D.drop_duplicates("occ")[["occ", "en_raw"]].copy()
u["q"] = pd.qcut(u.en_raw, 5, labels=False, duplicates="drop")
D2 = D.merge(u[["occ", "q"]], on="occ", how="left")
print("\n  Levels: employment index by exposure group, base year 2022 = 100")
print(f"  {'year':<8}{'top 2 quintiles':>18}{'bottom 3 quintiles':>21}{'gap':>10}")
base = {}
for grp, lab in [(D2.q >= 3, "top2"), (D2.q <= 2, "bot3")]:
    s = D2[grp].groupby("year").a22_25.sum()
    base[lab] = s
idx_t = 100 * base["top2"] / base["top2"].loc[2022]
idx_b = 100 * base["bot3"] / base["bot3"].loc[2022]
for y in sorted(set(idx_t.index) & set(idx_b.index)):
    print(f"  {y:<8}{idx_t.loc[y]:>18.1f}{idx_b.loc[y]:>21.1f}{idx_t.loc[y]-idx_b.loc[y]:>10.1f}")
print(f"\n  Canaries report 22-25 employment in the 2 most exposed quintiles fell ~11%")
print(f"  and rose ~10% in the 3 least exposed, Nov 2022 to Jun 2026.")
last = max(set(idx_t.index) & set(idx_b.index))
print(f"  Here, 2022 to {last}: top2 {idx_t.loc[last]-100:+.1f}%, bot3 {idx_b.loc[last]-100:+.1f}%")

print("\n  Regression form: binary top-2-quintile indicator x post")
D2["hi"] = (D2.q >= 3).astype(float)
for ycol, lab in [("share_2024", "20-24 share"), ("share_2225", "22-25 share")]:
    line(lab + ", top-2-quintile dummy", D2, ycol, ["hi"])

print("\n" + "=" * 100)
print("CHECK 3  EDUCATION: Canaries say their patterns attenuate. Do these?")
print("=" * 100)
print(f"\n  {'specification':<44}{'coef':>9}{'se':>9}{'t':>7}{'p':>9}")
for ycol, lab in [("share_2024", "20-24"), ("share_2225", "22-25")]:
    print(f"\n  --- {lab} share ---")
    b0, _, p0 = line("composite, no controls", D, ycol, ["rep_good"])
    line("  + education (Job Zone) x post", D, ycol, ["rep_good", "jobzone"])
    line("  + log median wage x post", D, ycol, ["rep_good", "lwage"])
    b1, _, p1 = line("  + BOTH", D, ycol, ["rep_good", "jobzone", "lwage"])
    print(f"      attenuation: {100*(1 - b1[0]/b0[0]):+.0f}% change in coefficient")

print("\n  Pre-AI placebo, same controlled spec, 2016-2019, fake post = 2018")
pre = D[D.year <= 2019]
for ycol, lab in [("share_2024", "20-24"), ("share_2225", "22-25")]:
    b, se, t, p, G, n = fe_multi(pre, ycol, ["rep_good", "jobzone", "lwage"], post_from=2018)
    print(f"    {lab} share: exposure {b[0]:+.4f} (p {p[0]:.4f}), "
          f"jobzone {b[1]:+.4f} (p {p[1]:.4f}), wage {b[2]:+.4f} (p {p[2]:.4f})")
