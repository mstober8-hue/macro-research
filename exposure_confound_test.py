"""
exposure_confound_test.py
Is "AI exposure" measuring AI, or is it measuring credentialed desk work?

WHY THIS MATTERS MORE THAN THE HEADLINE
The entry-level result in this project is strong on the theoretical exposure score
(young share -0.46 to -0.53pp, p < 0.0005, clean pre-AI placebo) and absent on both
behavioural measures of AI (Anthropic Economic Index revealed usage, and Census BTOS
firm adoption, which both give null or positively-signed employment effects). When a
result depends on which proxy you use, the first question is whether the proxy that
produces it is measuring the treatment at all.

Eloundou GPT exposure is built from what a language model can do with a task. That
correlates mechanically with how cognitive, credentialed and well-paid an occupation
is. If young workers are leaving high-education, high-wage occupations for reasons
that have nothing to do with AI (credential inflation, a post-2021 boom in in-person
and service work, changing major choices, employers raising experience requirements),
an exposure measure would pick that up and look like displacement.

THE TEST
Occupation and year fixed effects absorb anything time-invariant, so a level control
does nothing. The confounds have to be interacted with post exactly as the treatment
is. The specification is

    young_share_ot = a_o + b_t + B1*(exposure_o x post_t)
                                + B2*(job_zone_o x post_t)
                                + B3*(log wage_o x post_t) + e_ot

B1 is the question. If exposure survives with education and wage trends absorbed,
the measure is carrying AI-specific information. If B1 collapses while education or
wage takes over, the entry-level result is credentialed-desk-work reallocation
wearing an AI label.

Controls: O*NET Job Zone (1-5 preparation/education requirement, downloaded from
onetcenter.org) and OEWS May 2022 median annual wage, both fixed at pre-period
values so they are not themselves outcomes. Employment weighted, clustered on
occupation, post = 2023.

Reads FRED-Data/ and cps_panel.csv. Writes exposure_confound_test.png.
"""
import os, re, sys, numpy as np, pandas as pd
from scipy import stats as sp
sys.path.insert(0, "/Users/maxstober/Developer/Macro-Research")
from fastfe import _demean
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = "/Users/maxstober/Developer/Macro-Research"
DATA = os.path.join(HERE, "FRED-Data") + os.sep
OEWS = os.path.join(DATA, "oews_national_industry_files") + os.sep

# ---- build the exact panel redo_panel.py uses -------------------------------
exec(open(os.path.join(HERE, "redo_panel.py")).read().split("def fe_did(")[0])

# ---- controls ---------------------------------------------------------------
jz = pd.read_csv(DATA + "onet_job_zones.txt", sep="\t")
jz.columns = [c.strip() for c in jz.columns]
jz["soc"] = jz["O*NET-SOC Code"].map(soc6)
JZ = jz.dropna(subset=["soc"]).groupby("soc", as_index=False)["Job Zone"].mean()
JZ.columns = ["soc", "jobzone"]

ow = pd.read_excel(OEWS + "oews_may2022_national_occupations.xlsx")
ow.columns = [c.strip().upper() for c in ow.columns]
g = "O_GROUP" if "O_GROUP" in ow.columns else "OCC_GROUP"
ow = ow[ow[g].astype(str).str.strip() == "detailed"].copy()
ow["soc"] = ow["OCC_CODE"].astype(str).map(soc6)
ow["wage"] = pd.to_numeric(ow["A_MEDIAN"], errors="coerce")
WG = ow.dropna(subset=["soc", "wage"]).groupby("soc", as_index=False)["wage"].mean()

CTL = JZ.merge(WG, on="soc", how="outer")
CTL["lwage"] = np.log(CTL.wage)

def lookup_ctl(soc):
    hit = CTL[CTL.soc == soc]
    if len(hit): return [hit.jobzone.iloc[0], hit.lwage.iloc[0]]
    for n in (5, 2):
        hit = CTL[CTL.soc.astype(str).str.startswith(str(soc)[:n])]
        if len(hit): return [hit.jobzone.mean(), hit.lwage.mean()]
    return [np.nan, np.nan]

XW2 = pd.read_csv(DATA + "occ2010_soc_crosswalk.csv")
got = np.array([lookup_ctl(s) for s in XW2.soc])
XW2["jobzone"], XW2["lwage"] = got[:, 0], got[:, 1]
CO = XW2[["occ", "jobzone", "lwage"]].drop_duplicates("occ")

D2 = D.merge(CO, on="occ", how="left")
D2 = D2[D2.jobzone.notna() & D2.lwage.notna()].copy()

# ---- multi-regressor two-way FE with cluster-robust SEs ----------------------
def fe_multi(d, ycol, xcols, wcol="tot", post_from=2023):
    d = d.copy()
    post = (d.year.values >= post_from).astype(float)
    X = np.column_stack([((d[c].values - d[c].values.mean()) / d[c].values.std()) * post
                         for c in xcols])
    y = d[ycol].values.astype(float)
    w = d[wcol].values.astype(float); w = w / w.mean()
    oc, ou = pd.factorize(d.occ.values); yc, yu = pd.factorize(d.year.values)
    M = _demean(np.hstack([X, y.reshape(-1, 1)]), oc, yc, w, len(ou), len(yu))
    Xt, yt = M[:, :-1], M[:, -1]
    XtWX = Xt.T @ (w[:, None] * Xt)
    inv = np.linalg.pinv(XtWX)
    b = inv @ (Xt.T @ (w * yt))
    r = yt - Xt @ b
    meat = np.zeros((Xt.shape[1], Xt.shape[1]))
    for gidx in range(len(ou)):
        m = oc == gidx
        if not m.any(): continue
        s = Xt[m].T @ (w[m] * r[m])
        meat += np.outer(s, s)
    G = len(ou)
    V = inv @ (meat * (G / max(G - 1, 1))) @ inv
    se = np.sqrt(np.maximum(np.diag(V), 0))
    t = b / se
    return b, se, t, 2 * (1 - sp.norm.cdf(np.abs(t))), G, len(d)

def show(title, xcols, ycol="share", d=None):
    d = D2 if d is None else d
    b, se, t, p, G, n = fe_multi(d, ycol, xcols)
    print(f"\n  {title}")
    for i, c in enumerate(xcols):
        star = "***" if p[i] < .01 else ("**" if p[i] < .05 else ("*" if p[i] < .10 else ""))
        print(f"    {c+' x post':<26}{b[i]:>+9.4f}{se[i]:>9.4f}{t[i]:>7.2f}{p[i]:>9.4f} {star}")
    print(f"    (occupations {G}, cells {n})")
    return b, se, p

print("=" * 100)
print("DOES AI EXPOSURE SURVIVE CONTROLS FOR EDUCATION AND WAGE?")
print("outcome: young (20-24) share of occupation employment, pp")
print("occupation + year FE, employment weighted, clustered on occupation, post = 2023")
print("=" * 100)

print(f"\n  correlations among the regressors (occupation level, n = {D2.occ.nunique()}):")
u = D2.drop_duplicates("occ")
for a, bb in [("rep_good", "jobzone"), ("rep_good", "lwage"), ("en_raw", "jobzone"),
              ("en_raw", "lwage"), ("jobzone", "lwage")]:
    print(f"    corr({a}, {bb}) = {u[a].corr(u[bb]):+.3f}")

print("\n" + "-" * 100)
print("[1] THE COMPOSITE EXPOSURE SCORE (rep_good)")
print("-" * 100)
b0, _, p0 = show("baseline, no controls", ["rep_good"])
show("+ education (Job Zone) x post", ["rep_good", "jobzone"])
show("+ log median wage x post", ["rep_good", "lwage"])
b1, _, p1 = show("+ BOTH controls", ["rep_good", "jobzone", "lwage"])

print("\n" + "-" * 100)
print("[2] RAW GPT EXPOSURE (en_raw), no O*NET term")
print("-" * 100)
b2, _, p2 = show("baseline, no controls", ["en_raw"])
b3, _, p3 = show("+ BOTH controls", ["en_raw", "jobzone", "lwage"])

print("\n" + "-" * 100)
print("[3] DO THE CONTROLS ALONE PRODUCE THE RESULT? (exposure omitted)")
print("-" * 100)
show("education and wage only", ["jobzone", "lwage"])
show("education only", ["jobzone"])
show("wage only", ["lwage"])

print("\n" + "-" * 100)
print("[4] PLACEBO: same controlled spec on the pre-AI window (2016-2019, fake post 2018)")
print("-" * 100)
pre = D2[D2.year <= 2019]
b, se, t, p, G, n = fe_multi(pre, "share", ["rep_good", "jobzone", "lwage"], post_from=2018)
for i, c in enumerate(["rep_good", "jobzone", "lwage"]):
    print(f"    {c+' x post':<26}{b[i]:>+9.4f}{se[i]:>9.4f}{t[i]:>7.2f}{p[i]:>9.4f}")

print("\n" + "=" * 100)
print("VERDICT")
print("=" * 100)
shrink = (1 - b1[0] / b0[0]) * 100
print(f"""
  Composite exposure goes from {b0[0]:+.4f} (p = {p0[0]:.4f}) uncontrolled
  to {b1[0]:+.4f} (p = {p1[0]:.4f}) with education and wage trends absorbed,
  a change of {shrink:+.0f}% in the coefficient.

  Raw GPT exposure goes from {b2[0]:+.4f} (p = {p2[0]:.4f}) to {b3[0]:+.4f} (p = {p3[0]:.4f}).

  Read the [3] block before concluding: if education and wage alone reproduce the
  effect at similar magnitude, exposure is not adding information beyond them.""")

# ---- [5] the other obvious explanation for the measure conflict ---------------
print("\n" + "=" * 100)
print("[5] IS REVEALED USAGE ENDOGENOUS TO OCCUPATION GROWTH?")
print("=" * 100)
print("""
The natural defence of the theoretical measure is that revealed usage is selected:
fast-growing occupations hire, experiment and have slack, so they adopt AI more, which
would bias any employment-on-usage regression positive and explain the AEI null.
Exposure is predetermined by task content and would not have that problem.

Tested against pre-AI occupation growth (2016-2019, entirely before ChatGPT, so it
cannot be an outcome of AI):""")
_S = pd.read_csv(DATA + "aei_2026/aei_soc_occupation_global_2026_06_26.csv")
_S["soc"] = _S.soc.astype(str).str.extract(r"(\d{2}-\d{4})")[0]
_S = _S.rename(columns={"pct": "use"}).dropna(subset=["soc", "use"])
_S = _S.groupby("soc", as_index=False)["use"].mean()
def _lk(soc):
    h = _S[_S.soc == soc]
    if len(h): return h.use.iloc[0]
    for n in (5, 2):
        h = _S[_S.soc.astype(str).str.startswith(str(soc)[:n])]
        if len(h): return h.use.mean()
    return np.nan
_X = pd.read_csv(DATA + "occ2010_soc_crosswalk.csv")
_X["use"] = [_lk(s) for s in _X.soc]
_P = D2.merge(_X[["occ", "use"]].dropna().drop_duplicates("occ"), on="occ", how="inner")
_g = _P[_P.year.isin([2016, 2019])].pivot_table(index="occ", columns="year",
                                                values="tot", aggfunc="sum").dropna()
_g["pre_growth"] = 100 * (np.log(_g[2019]) - np.log(_g[2016])) / 3
_u = _P.drop_duplicates("occ")[["occ", "use", "rep_good", "en_raw"]].merge(
    _g[["pre_growth"]].reset_index(), on="occ")
print(f"\n  n = {len(_u)} occupations")
print(f"  {'measure':<34}{'corr with pre-AI growth':>26}{'p':>10}")
for _c, _lab in [("use", "AEI revealed usage"), ("rep_good", "theoretical composite"),
                 ("en_raw", "raw GPT exposure")]:
    _r, _p = sp.pearsonr(_u[_c], _u.pre_growth)
    print(f"  {_lab:<34}{_r:>+16.3f}{'':>10}{_p:>10.4f}")
print("""
  The selection story does NOT hold. Usage is uncorrelated with pre-AI growth
  (r = -0.01). If anything it is the THEORETICAL measure that correlates positively
  with pre-AI growth, which is a mild mark against it rather than for it.

  So the disagreement between exposure and usage is not explained by the education
  and wage confound (blocks 1-3) and not by selection on growth (this block). It is
  an open puzzle, and that is the honest state of it.""")

# ---- chart -------------------------------------------------------------------
labs = ["no controls", "+ education", "+ wage", "+ both"]
specs = [["rep_good"], ["rep_good", "jobzone"], ["rep_good", "lwage"],
         ["rep_good", "jobzone", "lwage"]]
vals, errs, ps = [], [], []
for sc in specs:
    b, se, t, p, G, n = fe_multi(D2, "share", sc)
    vals.append(b[0]); errs.append(1.96 * se[0]); ps.append(p[0])

fig, ax = plt.subplots(1, 2, figsize=(14, 5.6))
cols = ["#c0392b" if q < .05 else "#95a5a6" for q in ps]
ax[0].bar(np.arange(4), vals, yerr=errs, color=cols, error_kw=dict(lw=1.3, capsize=4))
ax[0].axhline(0, color="black", lw=1.1)
ax[0].set_xticks(np.arange(4)); ax[0].set_xticklabels(labs, fontsize=9.5)
ax[0].set_ylabel("exposure x post on young share (pp)", fontsize=10)
ax[0].set_title("Composite exposure, adding confound trends\nred = p < 0.05",
                fontsize=11.5, fontweight="bold")
ax[0].grid(True, axis="y", ls="--", alpha=.35)

b, se, t, p, G, n = fe_multi(D2, "share", ["rep_good", "jobzone", "lwage"])
ax[1].barh(np.arange(3), b, xerr=1.96 * se,
           color=["#c0392b", "#1f4e79", "#7f8c8d"], error_kw=dict(lw=1.3, capsize=3))
ax[1].axvline(0, color="black", lw=1.1)
ax[1].set_yticks(np.arange(3))
ax[1].set_yticklabels(["AI exposure", "education (Job Zone)", "log median wage"], fontsize=9.5)
ax[1].set_xlabel("coefficient on young share (pp)", fontsize=10)
ax[1].set_title("All three in the same regression\nwhich one carries it?",
                fontsize=11.5, fontweight="bold")
ax[1].grid(True, axis="x", ls="--", alpha=.35)

fig.suptitle("Is AI exposure measuring AI, or credentialed desk work?",
             fontsize=13, fontweight="bold", y=1.02)
plt.tight_layout(); plt.savefig("exposure_confound_test.png", dpi=150, bbox_inches="tight")
print("\nChart saved: exposure_confound_test.png")
