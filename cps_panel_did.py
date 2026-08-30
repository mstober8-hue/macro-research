"""
cps_panel_did.py
The entry-level result re-estimated as an occupation panel with fixed effects.

WHAT THIS CHANGES AND WHY IT IS THE RIGHT TEST
The published-table version of this result is a triple difference across two
disjoint windows, and entry_level_inference_audit.py showed it is marginal:
randomization inference gives one-sided p = 0.056, agreeing with the
occupation-level bootstrap, while the cluster bootstrap that produced the
reported p = 0.011 is unreliable at roughly 12 effective clusters.

That audit also found something that determines what to do next. The null spread
does NOT shrink when the analysis is restricted to larger, better-measured
occupations (8.11 -> 8.43 -> 9.47pp). The noise is genuine cross-occupation
heterogeneity in young-employment growth, not CPS sampling error. So more
observations per occupation cannot help. The heterogeneity has to be removed, not
measured more precisely.

Occupation fixed effects remove it. In a panel of occupation-by-year cells,

    log(young employment)_it = a_i + b_t + beta * (exposure_i x post_t) + e_it

the occupation effect a_i absorbs every permanent difference between occupations,
which is exactly the 8.26pp of dispersion that was drowning the cross-sectional
estimate. Identification comes from movement WITHIN an occupation over time.

This is what the microdata buys, and specifically what OCC2010 buys. Plain OCC
recodes in 2020, mid-window, which is why the published-table design had to use
two windows that cannot be directly compared. OCC2010 is harmonized across that
break, so 2016-2026 runs continuously and an event study can show whether a
pre-trend exists. A pre-trend would mean exposed occupations were already losing
young workers before AI, which no before-and-after design can detect.

THE PANEL
473 occupations, 2016-2026, from 6.0 million CPS person-month records, weighted by
WTFINL and averaged to monthly-equivalent levels.

WHAT WOULD FALSIFY THE FINDING
A significant pre-trend, or a post-2022 coefficient that vanishes once occupation
fixed effects absorb the cross-sectional heterogeneity. The second outcome would
mean the published result was driven by WHICH occupations are exposed rather than
by what happened inside them, and it is a live possibility.

Requires cps_panel.csv from build_cps_panel.py.
"""

import os
import re
import sys
import glob
import numpy as np
import pandas as pd
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import stats_inference as si

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "FRED-Data") + os.sep
DDI  = os.path.expanduser("~/Downloads/cps_00001.xml")
RNG  = np.random.default_rng(606)


def find(stub):
    p = glob.glob(DATA + "*" + stub + "*")
    if not p:
        raise FileNotFoundError(stub)
    return p[0]


def norm(t):
    t = str(t).lower()
    t = re.sub(r"[^a-z0-9 ]", " ", t)
    t = re.sub(r"\b(occupations?|workers?|all other|other|misc|miscellaneous|nec)\b", " ", t)
    return re.sub(r"\s+", " ", t).strip()


# ---- replaceability score, same construction as the published-table analysis ----
el = pd.read_csv(find("eloundou_gpt_occupational_exposure_scores"))
el.columns = [c.strip().lower() for c in el.columns]
tcol = [c for c in el.columns if "title" in c][0]
ecol = [c for c in el.columns if any(k in c for k in ("exposure", "beta", "zeta", "alpha"))][0]
el["nt"] = el[tcol].map(norm)
el["en"] = pd.to_numeric(el[ecol], errors="coerce")
el = el.dropna(subset=["en"]).groupby("nt", as_index=False)["en"].mean()

wc = pd.read_csv(find("onet_work_context_ratings"))
wc.columns = [c.strip().lower() for c in wc.columns]
wt = [c for c in wc.columns if "title" in c][0]
wv = [c for c in wc.columns if "value" in c or "rating" in c][0]
wc["nt"] = wc[wt].map(norm)
wc["cv"] = pd.to_numeric(wc[wv], errors="coerce")
comp = wc.dropna(subset=["cv"]).groupby("nt", as_index=False)["cv"].mean()
comp["comp"] = (comp.cv - comp.cv.min()) / (comp.cv.max() - comp.cv.min())

R = el.merge(comp[["nt", "comp"]], on="nt", how="left")
R["comp"] = R["comp"].fillna(R["comp"].median())
R["rep"] = R["en"] * (1 - R["comp"])

# ---- OCC2010 labels from the DDI, matched to the score by normalised title ----
ns = {"d": "ddi:codebook:2_5"}
root = ET.parse(DDI).getroot()
labs = []
for v in root.findall(".//d:var", ns):
    if v.get("name") == "OCC2010":
        for c in v.findall("d:catgry", ns):
            labs.append((int(c.find("d:catValu", ns).text),
                         c.find("d:labl", ns).text))
        break
OCC = pd.DataFrame(labs, columns=["occ", "title"])
OCC["nt"] = OCC.title.map(norm)
OCC = OCC.merge(R[["nt", "rep", "en"]], on="nt", how="left")

P = pd.read_csv(os.path.join(HERE, "cps_panel.csv"))
W = P.pivot_table(index=["occ", "year"], columns="band", values="emp",
                  aggfunc="sum").fillna(0.0).reset_index()
W = W.merge(OCC[["occ", "title", "rep"]], on="occ", how="left")

matched = W.dropna(subset=["rep"])
cov = matched[matched.year == 2024][["a20_24", "a25_34", "a35p"]].sum().sum()
tot = W[W.year == 2024][["a20_24", "a25_34", "a35p"]].sum().sum()
print("=" * 96)
print("CPS OCCUPATION PANEL WITH FIXED EFFECTS")
print("=" * 96)
print(f"\n  occupations in panel         : {W.occ.nunique()}")
print(f"  matched to exposure score    : {matched.occ.nunique()}")
print(f"  employment coverage of match : {100*cov/tot:.1f}%")

D = matched[matched.year >= 2016].copy()
D["tot"] = D[["a20_24", "a25_34", "a35p"]].sum(axis=1)
D = D[(D.a20_24 > 0) & (D.tot > 0)]
D["ly"] = np.log(D.a20_24)
D["lo"] = np.log(D.a35p.clip(lower=1))
D["share"] = 100 * D.a20_24 / D.tot
D["z"] = (D.rep - D.rep.mean()) / D.rep.std()

# ---------------------------------------------------------------------------
def fe_did(df, ycol, wcol=None, post_from=2023):
    """
    Two-way fixed effects, occupation and year, with exposure x post.
    Weighting matters here: the published-table analysis noted that
    per-occupation regressions are attenuated by CPS sampling noise, which falls
    hardest on small occupations. Weighting by employment is the standard remedy
    and is reported alongside the unweighted version rather than instead of it.
    """
    d = df.copy()
    d["post"] = (d.year >= post_from).astype(float)
    occ_d = pd.get_dummies(d.occ, prefix="o", drop_first=True).astype(float)
    yr_d = pd.get_dummies(d.year, prefix="y", drop_first=True).astype(float)
    X = np.column_stack([np.ones(len(d)), (d.z * d.post).to_numpy(),
                         occ_d.to_numpy(), yr_d.to_numpy()])
    y = d[ycol].to_numpy()
    w = np.ones(len(d)) if wcol is None else d[wcol].to_numpy()
    sw = np.sqrt(w / w.mean())
    Xw, yw = X * sw[:, None], y * sw
    b, *_ = np.linalg.lstsq(Xw, yw, rcond=None)
    resid = yw - Xw @ b
    XtX = np.linalg.pinv(Xw.T @ Xw)
    meat = np.zeros((X.shape[1], X.shape[1]))
    for _, idx in d.groupby("occ").indices.items():
        s = Xw[idx].T @ resid[idx]
        meat += np.outer(s, s)
    G = d.occ.nunique()
    V = XtX @ meat @ XtX * (G / max(G - 1, 1))
    return b[1], float(np.sqrt(max(V[1, 1], 0))), G, len(d)


print("\n" + "=" * 96)
print("[1] TWO-WAY FIXED EFFECTS: does exposure predict young-employment loss")
print("    once permanent occupation differences are absorbed?")
print("=" * 96)
print("\n  Outcome is log young (20-24) employment. Coefficient is the effect of a")
print("  ONE STANDARD DEVIATION increase in exposure, post-2022, in log points.\n")
from scipy import stats as _sp
print(f"  {'specification':<44}{'coef':>10}{'se':>9}{'t':>7}{'p':>9}")
SPECS = [("log young emp, unweighted", "ly", None),
         ("log young emp, weighted by employment", "ly", "tot"),
         ("young SHARE of occupation (pp), weighted", "share", "tot"),
         ("log incumbent 35+ emp, weighted [PLACEBO]", "lo", "tot")]
for lbl, col, wc in SPECS:
    b, se, G, N = fe_did(D, col, wc)
    t = b / se if se > 0 else np.nan
    p = 2 * (1 - _sp.norm.cdf(abs(t)))
    print(f"  {lbl:<44}{b:>+10.4f}{se:>9.4f}{t:>+7.2f}{p:>9.4f}")
print(f"\n  clusters (occupations): {G}    cells: {N}")

print("\n  The incumbent row is the placebo within the same design. Displacement at")
print("  the hiring margin should hit the young and leave incumbents alone.")

# ---------------------------------------------------------------------------
print("\n" + "=" * 96)
print("[2] EVENT STUDY: is there a pre-trend? This is what two windows cannot show.")
print("=" * 96)
d = D[D.year >= 2016].copy()
occ_d = pd.get_dummies(d.occ, prefix="o", drop_first=True).astype(float)
yrs = sorted(d.year.unique())
base = 2022
inter = {}
for y in yrs:
    if y == base:
        continue
    inter[f"x{y}"] = (d.z * (d.year == y)).to_numpy()
yr_d = pd.get_dummies(d.year, prefix="y", drop_first=True).astype(float)
X = np.column_stack([np.ones(len(d))] + [inter[k] for k in inter]
                    + [occ_d.to_numpy(), yr_d.to_numpy()])
y = d["ly"].to_numpy()
b, *_ = np.linalg.lstsq(X, y, rcond=None)
resid = y - X @ b
XtX = np.linalg.pinv(X.T @ X)
meat = np.zeros((X.shape[1], X.shape[1]))
for _, idx in d.groupby("occ").indices.items():
    s = X[idx].T @ resid[idx]
    meat += np.outer(s, s)
G = d.occ.nunique()
V = XtX @ meat @ XtX * (G / max(G - 1, 1))
se_all = np.sqrt(np.maximum(np.diag(V), 0))

print(f"\n  Coefficients on exposure x year, relative to {base}. Occupation and year")
print("  fixed effects throughout, clustered on occupation.\n")
print(f"  {'year':<8}{'coef':>10}{'se':>9}{'t':>8}   {'':<4}")
for i, k in enumerate(inter, start=1):
    yv = int(k[1:])
    tag = "pre " if yv < base else "post"
    star = " *" if abs(b[i] / se_all[i]) > 1.96 else ""
    print(f"  {yv:<8}{b[i]:>+10.4f}{se_all[i]:>9.4f}{b[i]/se_all[i]:>+8.2f}   {tag}{star}")

pre = [b[i] for i, k in enumerate(inter, start=1) if int(k[1:]) < base]
pre_t = [abs(b[i] / se_all[i]) for i, k in enumerate(inter, start=1) if int(k[1:]) < base]
post = [b[i] for i, k in enumerate(inter, start=1) if int(k[1:]) > base]
print(f"\n  mean pre-period coefficient  : {np.mean(pre):+.4f}   "
      f"(significant in {sum(1 for t in pre_t if t > 1.96)} of {len(pre)} years)")
print(f"  mean post-period coefficient : {np.mean(post):+.4f}")
print("\n  A clean design needs the pre-period coefficients flat and insignificant.")
print("  If they trend, exposed occupations were already shedding young workers")
print("  before AI and the post-2022 estimate is not attributable to it.")
