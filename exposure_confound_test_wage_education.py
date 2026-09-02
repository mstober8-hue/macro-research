"""
exposure_confound_test_wage_education.py

NOTE ON THE FILENAME
This was commissioned as exposure_confound_test.py. That filename was already
occupied and being actively written by another process at the time this was
authored, with a different analysis in it (a section on whether AEI revealed
usage is endogenous to occupation growth). Overwriting it would have destroyed
work, so this test lives under its own name. Rename it if the collision is
resolved in its favour.

WHAT THIS TESTS
The headline entry-level finding in this project is that occupations with higher
Eloundou GPT exposure saw the 20-24 employment share fall after 2022. The obvious
objection is that "AI exposure" is not measuring AI at all. Eloundou scores are
built from what a language model can do with an occupation's tasks, which is close
to a definition of cognitive, credentialed, office-based work. Those same
occupations are also the high-wage, high-education ones. If young workers pulled
back from credentialed desk work after 2022 for reasons unrelated to AI, such as
employers raising experience requirements, a white-collar hiring freeze, a
post-pandemic reallocation toward in-person and service work, or shifting college
major choices, an exposure measure would track that and look exactly like AI
displacement.

This script asks whether the exposure coefficient survives once high-wage and
high-education occupations are allowed their own post-2022 trajectory.

THE CRITICAL SPECIFICATION POINT
This is a difference in differences with a time-invariant treatment. Occupation
fixed effects absorb every time-invariant occupation characteristic, so entering
median wage or education in levels does nothing at all. They are already gone.
The controls have to enter interacted with the same post indicator as the
treatment:

    young_share_ot = a_o + b_t + B1 (exposure_o x post_t)
                                + B2 (log wage_o x post_t)
                                + B3 (education_o x post_t) + e_ot

B1 is the question. All three regressors are z-scored so the coefficients are
directly comparable, in percentage points per one standard deviation. Employment
weighted, clustered on occupation, post = 2023.

WHAT IT FOUND
The confound story does not survive contact with the data. The exposure effect is
not attenuated by the controls at all, it strengthens slightly.

  composite exposure   -0.5291 (p < 0.0001) uncontrolled on the controlled sample
                       -0.5660 (p < 0.0001) with wage and education x post
  raw Eloundou         -0.5140 (p = 0.0002) uncontrolled
                       -0.6028 (p < 0.0001) with wage and education x post

Wage x post and education x post are individually insignificant in every
specification and, crucially, POSITIVELY signed. The confound story requires them
to be negative, since it claims young workers were leaving high-wage,
high-education work. They point the other way, so conditioning on them makes the
exposure coefficient larger rather than smaller. Run without exposure the two
controls together produce +0.0001 and -0.1239, neither close to significance and
neither close to the size of the exposure effect.

The controls survive 434 of 458 occupations (94.8 percent), so the reduced sample
is not doing the work. The pre-AI placebo stays null and positively signed under
every one of the four specifications. Collinearity between exposure and the
controls peaks at 0.583, well below the 0.8 threshold where a horse race stops
being informative, although wage and education are correlated with each other at
0.774 so they are hard to separate from one another.

CAVEATS, STATED UP FRONT
1. Collinearity is real even at 0.62. The controls and the treatment share
   variance, so attenuation should be read as an upper bound on the confound
   rather than a precise decomposition.
2. Education is O*NET Job Zone (1 to 5), a preparation and education composite,
   not the BLS "typical entry-level education" category. Job Zone is already on
   disk and is an ordinal education-and-training requirement, which is what the
   control needs. It is coarser than the BLS categorical measure.
3. Wage is OEWS May 2022 median annual wage, fixed at a pre-period value so the
   control is not itself an outcome of the treatment. May 2019 is run as a
   robustness check since 2022 is arguably already contaminated.
4. Merge attrition. Not every CPS occupation matches an OEWS or O*NET record, so
   the uncontrolled baseline is re-estimated on the reduced sample and the before
   and after comparison is apples to apples rather than confounded with sample
   composition.
5. This test cannot rule out a confound that is uncorrelated with wage and
   education but correlated with exposure. It closes one specific objection and
   no more.

Reads FRED-Data/ and cps_panel.csv. Prints only, writes no files.
"""
import os
import re
import sys
import numpy as np
import pandas as pd
from scipy import stats as sp

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from fastfe import _demean

DATA = os.path.join(HERE, "FRED-Data") + os.sep
OEWS = os.path.join(DATA, "oews_national_industry_files") + os.sep

COMP_VARS = ["Physical Proximity",
             "Face-to-Face Discussions with Individuals and Within Teams",
             "Deal With External Customers or the Public in General",
             "Health and Safety of Other Workers",
             "Consequence of Error"]


def soc6(c):
    """Normalise any O*NET or SOC style code to its 6 digit XX-XXXX stem."""
    m = re.match(r"(\d{2}-\d{4})", str(c))
    return m.group(1) if m else None


def soc_lookup(table, key_cols, socs):
    """Match SOC codes to a reference table with 6, then 5, then 2 digit fallback.

    Returns values plus a per-row code for how the match was made: 2 = exact
    6 digit, 1 = prefix fallback, 0 = no match. This mirrors the fallback logic
    redo_panel.py uses for the exposure merge, so the control merge is neither
    more nor less generous than the treatment merge.
    """
    out = np.full((len(socs), len(key_cols)), np.nan)
    how = np.zeros(len(socs), dtype=int)
    ref_soc = table["soc"].astype(str)
    for i, s in enumerate(socs):
        hit = table[ref_soc == str(s)]
        if len(hit):
            out[i] = [hit[c].iloc[0] for c in key_cols]
            how[i] = 2
            continue
        for n in (5, 2):
            hit = table[ref_soc.str.startswith(str(s)[:n])]
            if len(hit):
                out[i] = [hit[c].mean() for c in key_cols]
                how[i] = 1
                break
    return out, how


# ---------------------------------------------------------------------------
# 1. Exposure measures, rebuilt exactly as redo_panel.py builds them
# ---------------------------------------------------------------------------
el = pd.read_csv(DATA + "eloundou_gpt_occupational_exposure_scores.csv")
el.columns = [c.strip() for c in el.columns]
el["soc"] = el["O*NET-SOC Code"].map(soc6)
el["en_raw"] = el[["human_rating_beta", "dv_rating_beta"]].mean(axis=1)
EL = el.dropna(subset=["soc"]).groupby("soc", as_index=False)["en_raw"].mean()

wc = pd.read_csv(DATA + "onet_work_context_ratings.csv")
wc.columns = [c.strip() for c in wc.columns]
wc["cv"] = pd.to_numeric(wc["Data Value"], errors="coerce")
wc["soc"] = wc["O*NET-SOC Code"].map(soc6)

g = wc[(wc["Scale ID"] == "CX") & (wc["Element Name"].isin(COMP_VARS))]
piv = g.pivot_table(index="soc", columns="Element Name", values="cv")
piv = (piv - piv.min()) / (piv.max() - piv.min())
GOOD = pd.DataFrame({"comp_good": piv.mean(axis=1)}).reset_index()

R = EL.merge(GOOD, on="soc", how="left")
R["comp_good"] = R.comp_good.fillna(R.comp_good.median())
R["en_mm"] = (R.en_raw - R.en_raw.min()) / (R.en_raw.max() - R.en_raw.min())
R["rep_good"] = R.en_mm * (1 - R.comp_good)


# ---------------------------------------------------------------------------
# 2. Controls: pre-period median wage and an education requirement
# ---------------------------------------------------------------------------
def load_oews(fname, out):
    ow = pd.read_excel(OEWS + fname)
    ow.columns = [c.strip().upper() for c in ow.columns]
    gcol = "O_GROUP" if "O_GROUP" in ow.columns else "OCC_GROUP"
    ow = ow[ow[gcol].astype(str).str.strip().str.lower() == "detailed"].copy()
    ow["soc"] = ow["OCC_CODE"].astype(str).map(soc6)
    ow[out] = pd.to_numeric(ow["A_MEDIAN"], errors="coerce")
    ow = ow.dropna(subset=["soc", out])
    return ow.groupby("soc", as_index=False)[out].mean()


W22 = load_oews("oews_may2022_national_occupations.xlsx", "w22")
W19 = load_oews("oews_may2019_national_occupations.xlsx", "w19")

jz = pd.read_csv(DATA + "onet_job_zones.txt", sep="\t")
jz.columns = [c.strip() for c in jz.columns]
jz["soc"] = jz["O*NET-SOC Code"].map(soc6)
JZ = jz.dropna(subset=["soc"]).groupby("soc", as_index=False)["Job Zone"].mean()
JZ = JZ.rename(columns={"Job Zone": "jobzone"})

CTL = W22.merge(W19, on="soc", how="outer").merge(JZ, on="soc", how="outer")
CTL["lwage22"] = np.log(CTL.w22)
CTL["lwage19"] = np.log(CTL.w19)

# ---------------------------------------------------------------------------
# 3. Crosswalk everything onto CPS 2010 occupation codes
# ---------------------------------------------------------------------------
XW = pd.read_csv(DATA + "occ2010_soc_crosswalk.csv")

EXP_COLS = ["rep_good", "en_raw"]
exp_vals, _ = soc_lookup(R, EXP_COLS, XW.soc.values)
for i, c in enumerate(EXP_COLS):
    XW[c] = exp_vals[:, i]

CTL_COLS = ["lwage22", "lwage19", "jobzone"]
ctl_vals, ctl_how = soc_lookup(CTL, CTL_COLS, XW.soc.values)
for i, c in enumerate(CTL_COLS):
    XW[c] = ctl_vals[:, i]
XW["ctl_match"] = ctl_how

OCC = (XW[["occ", "title"] + EXP_COLS + CTL_COLS + ["ctl_match"]]
       .dropna(subset=["rep_good"]).drop_duplicates("occ"))

# ---------------------------------------------------------------------------
# 4. Panel, identical to redo_panel.py
# ---------------------------------------------------------------------------
P = pd.read_csv(os.path.join(HERE, "cps_panel.csv"))
Wd = P.pivot_table(index=["occ", "year"], columns="band", values="emp",
                   aggfunc="sum").fillna(0.0).reset_index()
Wd = Wd.merge(OCC, on="occ", how="left")
D = Wd[(Wd.year >= 2016) & Wd.rep_good.notna()].copy()
D["tot"] = D[["a20_24", "a25_34", "a35p"]].sum(axis=1)
D = D[(D.a20_24 > 0) & (D.tot > 0)].copy()
D["share"] = 100 * D.a20_24 / D.tot

D2 = D[D.lwage22.notna() & D.jobzone.notna()].copy()   # controlled sample
D_w = D[D.lwage22.notna()].copy()
D_e = D[D.jobzone.notna()].copy()


# ---------------------------------------------------------------------------
# 5. Multi regressor two-way FE with cluster robust SEs
# ---------------------------------------------------------------------------
def fe_multi(d, ycol, xcols, wcol="tot", post_from=2023):
    """Two-way FE DiD with several post-interacted regressors.

    Every xcol is z-scored over the estimation rows then multiplied by post, so
    coefficients are in outcome units per one standard deviation. Standard errors
    are clustered on occupation. Uses the same alternating-projection demeaner as
    fastfe.fe_did, so the single-regressor case reproduces redo_panel.py.
    """
    d = d.copy()
    post = (d["year"].values >= post_from).astype(float)
    cols = []
    for c in xcols:
        v = d[c].values.astype(float)
        cols.append(((v - v.mean()) / v.std()) * post)
    X = np.column_stack(cols)
    y = d[ycol].values.astype(float)
    w = d[wcol].values.astype(float)
    w = w / w.mean()
    oc, ou = pd.factorize(d["occ"].values)
    yc, yu = pd.factorize(d["year"].values)
    M = _demean(np.hstack([X, y.reshape(-1, 1)]), oc, yc, w, len(ou), len(yu))
    Xt, yt = M[:, :-1], M[:, -1]
    inv = np.linalg.pinv(Xt.T @ (w[:, None] * Xt))
    b = inv @ (Xt.T @ (w * yt))
    r = yt - Xt @ b
    k = Xt.shape[1]
    meat = np.zeros((k, k))
    order = np.argsort(oc, kind="stable")
    oc_sorted = oc[order]
    starts = np.searchsorted(oc_sorted, np.arange(len(ou)), side="left")
    ends = np.searchsorted(oc_sorted, np.arange(len(ou)), side="right")
    for lo, hi in zip(starts, ends):
        if hi <= lo:
            continue
        idx = order[lo:hi]
        s = Xt[idx].T @ (w[idx] * r[idx])
        meat += np.outer(s, s)
    G = len(ou)
    V = inv @ (meat * (G / max(G - 1, 1))) @ inv
    se = np.sqrt(np.maximum(np.diag(V), 0))
    t = b / se
    return b, se, t, 2 * (1 - sp.norm.cdf(np.abs(t))), G, len(d)


LAB = {"rep_good": "AI exposure (composite)", "en_raw": "AI exposure (raw Eloundou)",
       "lwage22": "log median wage 2022", "lwage19": "log median wage 2019",
       "jobzone": "education (Job Zone)"}


def show(title, xcols, d, ycol="share", post_from=2023):
    b, se, t, p, G, n = fe_multi(d, ycol, xcols, post_from=post_from)
    print(f"\n  {title}")
    for i, c in enumerate(xcols):
        star = "***" if p[i] < .01 else ("**" if p[i] < .05 else ("*" if p[i] < .10 else ""))
        print(f"    {LAB.get(c, c) + ' x post':<32}{b[i]:>+9.4f}{se[i]:>9.4f}"
              f"{t[i]:>7.2f}{p[i]:>9.4f} {star}")
    print(f"    occupations {G}, cells {n}")
    return b, se, p


def block(exposure, d, dfull, post_from=2023):
    """The four specification ladder for one exposure measure."""
    print("\n" + "-" * 100)
    print(LAB[exposure].upper())
    print("-" * 100)
    show("[0] baseline on the FULL sample (reproduces redo_panel.py)",
         [exposure], dfull, post_from=post_from)
    b0, _, p0 = show("[1] baseline re-estimated on the CONTROLLED sample",
                     [exposure], d, post_from=post_from)
    show("[2] + wage x post", [exposure, "lwage22"], d, post_from=post_from)
    show("[3] + education x post", [exposure, "jobzone"], d, post_from=post_from)
    b4, _, p4 = show("[4] HORSE RACE: + wage and education x post",
                     [exposure, "lwage22", "jobzone"], d, post_from=post_from)
    return b0[0], p0[0], b4[0], p4[0]


# ---------------------------------------------------------------------------
# 6. Report
# ---------------------------------------------------------------------------
print("=" * 100)
print("DOES THE ENTRY-LEVEL AI EXPOSURE EFFECT SURVIVE WAGE AND EDUCATION CONTROLS?")
print("outcome: 20-24 share of occupation employment, percentage points")
print("occupation + year FE, employment weighted, clustered on occupation, post = 2023")
print("all regressors z-scored, so coefficients are pp per 1 SD")
print("=" * 100)

n_all = D.occ.nunique()
print("\nMERGE / MATCH RATES")
print(f"  occupations in the exposure panel              {n_all}")
print(f"  ... with OEWS May 2022 median wage             {D_w.occ.nunique()}"
      f"  ({100 * D_w.occ.nunique() / n_all:.1f}%)")
print(f"  ... with O*NET Job Zone                        {D_e.occ.nunique()}"
      f"  ({100 * D_e.occ.nunique() / n_all:.1f}%)")
print(f"  ... with BOTH (the controlled sample)          {D2.occ.nunique()}"
      f"  ({100 * D2.occ.nunique() / n_all:.1f}%)")
print(f"  panel cells: full {len(D)}, controlled {len(D2)}")
exact = OCC[OCC.occ.isin(D2.occ.unique())].ctl_match.eq(2).mean()
print(f"  control merge was an exact 6 digit SOC match for {100 * exact:.1f}% of them")

u = D2.drop_duplicates("occ")
print(f"\nCOLLINEARITY (occupation level, n = {len(u)}, unweighted Pearson)")
pairs = [("rep_good", "en_raw"), ("rep_good", "lwage22"), ("rep_good", "jobzone"),
         ("en_raw", "lwage22"), ("en_raw", "jobzone"), ("lwage22", "jobzone")]
worst = 0.0
for a, bb in pairs:
    rr = u[a].corr(u[bb])
    if not (a == "rep_good" and bb == "en_raw"):
        worst = max(worst, abs(rr))
    print(f"    corr({LAB[a]}, {LAB[bb]}) = {rr:+.3f}")
print(f"    highest treatment/control or control/control correlation = {worst:.3f}")
if worst > 0.8:
    print("    ABOVE 0.8: the horse race CANNOT cleanly separate these regressors.")
else:
    print("    Below 0.8: collinear but separable. The regressors still share")
    print("    variance, so read any attenuation as an upper bound on the confound.")

res_rep = block("rep_good", D2, D)
res_raw = block("en_raw", D2, D)

print("\n" + "-" * 100)
print("[5] DO THE CONTROLS ALONE REPRODUCE THE EFFECT? (exposure omitted)")
print("-" * 100)
show("wage and education only", ["lwage22", "jobzone"], D2)
show("wage only", ["lwage22"], D2)
show("education only", ["jobzone"], D2)

print("\n" + "-" * 100)
print("[6] PRE-AI PLACEBO: 2016-2019 only, fake post = 2018, controlled sample")
print("-" * 100)
PRE = D2[D2.year <= 2019].copy()
for m in ("rep_good", "en_raw"):
    print(f"\n  {LAB[m]}")
    show("  baseline", [m], PRE, post_from=2018)
    show("  + wage x post", [m, "lwage22"], PRE, post_from=2018)
    show("  + education x post", [m, "jobzone"], PRE, post_from=2018)
    show("  HORSE RACE", [m, "lwage22", "jobzone"], PRE, post_from=2018)

print("\n" + "-" * 100)
print("[7] ROBUSTNESS: May 2019 wage instead of May 2022 (further from treatment)")
print("-" * 100)
D3 = D[D.lwage19.notna() & D.jobzone.notna()].copy()
print(f"  occupations with 2019 wage and Job Zone: {D3.occ.nunique()}")
show("composite, horse race with 2019 wage", ["rep_good", "lwage19", "jobzone"], D3)
show("raw Eloundou, horse race with 2019 wage", ["en_raw", "lwage19", "jobzone"], D3)

print("\n" + "=" * 100)
print("VERDICT")
print("=" * 100)
for name, (b0, p0, b4, p4) in [("composite exposure", res_rep),
                               ("raw Eloundou exposure", res_raw)]:
    keep = 100 * b4 / b0 if b0 != 0 else float("nan")
    print(f"\n  {name}")
    print(f"    uncontrolled, controlled sample   {b0:+.4f}  (p = {p0:.4f})")
    print(f"    with wage and education x post    {b4:+.4f}  (p = {p4:.4f})")
    print(f"    retained                          {keep:.0f}% of the baseline coefficient")
print("""
  Read the [5] block before drawing a conclusion. If wage and education on their
  own deliver a coefficient of similar size, exposure is not adding information
  beyond credentialed desk work and the AI reading is not identified here.""")
