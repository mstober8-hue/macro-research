"""
entry_level_measure_reaudit.py
The exposure-measure audit was applied to only half the result it invalidated.

WHAT THIS FINDS
exposure_measure_audit.py correctly showed that cps_panel_did.py's exposure score
is broken. It then retracted the POSITIVE result that score produced (log total
occupation employment, p = 0.004) and left standing the NULL the same score
produced in the same regression run: "every age band falls by nearly the same
amount and the young share does not move," which the README treats as the
refutation of the entry-level hypothesis.

A null from a broken regressor is not evidence of absence. Re-running the age
bands with any defensible measure moves the young-share coefficient from
-0.025 (p = 0.31) to about -0.48 (p < 0.001), a twentyfold change. The README's
"uniform shrinkage" claim does not survive.

HOW BROKEN THE MEASURE IS
cps_panel_did.py averages the Data Value column of the O*NET work-context file
across every row. That file mixes four incompatible scales:

    CXP  241,450 rows (81%)  category percentages, 0-100, mean exactly 20.00
    CX    49,170 rows        the actual context rating, 1-5
    CTP    5,268 rows        category percentages, 0-100, mean exactly 33.33
    CT     1,788 rows        1-3

The CXP and CTP rows are shares of respondents per answer category, so they sum
to 100 within an element and their mean is fixed by how many categories the
element has. They carry no cross-occupation information, and they are 83% of the
file. The resulting complementarity term correlates with a correctly built one at
r = +0.045. ai_replaceability_score.py, already in this repository, builds it
correctly: Scale ID == "CX" filtered to five named complementarity elements.
cps_panel_did.py re-implemented it and dropped both filters.

BUT THE CORRECTED RESULT IS NOT AN AI FINDING EITHER, AND THIS IS THE POINT
The corrected young-share effect is large, survives leave-one-out across all 458
occupations, and has randomization-inference p = 0.0002. It still should not be
written up as AI displacement:

  1. The event study has significant pre-trends. Four of six pre-2022 years are
     individually significant, all positive, declining monotonically from 2018.
  2. A trend-break test finds no slope change at 2022 in any specification,
     while PLACEBO knots at 2019 and 2020 produce significant slope changes
     (p = 0.004 and p = 0.015). The design fires harder on fake dates.
  3. Unweighted it is insignificant (p = 0.139).
  4. The raw levels show the comparison group moved, not the treated group. The
     young share of high-exposure occupations is flat across the decade
     (6.90% in 2016, 6.45% in 2025). The young share of LOW-exposure occupations
     rises (12.17% to 13.06%). The gap widens from the manual-work side.

That fourth point is the substantive finding: young workers are increasingly
concentrated in low-exposure manual and service work, and the movement is in
where they went, not in what they were pushed out of.

Run: python3 entry_level_measure_reaudit.py
Requires cps_panel.csv (build_cps_panel.py), the Eloundou scores, the O*NET
work-context file, and occ2010_soc_crosswalk.csv.
"""

import os
import re
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats as sp

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "FRED-Data") + os.sep

# The five complementarity elements ai_replaceability_score.py uses.
COMP_VARS = ["Physical Proximity",
             "Face-to-Face Discussions with Individuals and Within Teams",
             "Deal With External Customers or the Public in General",
             "Health and Safety of Other Workers",
             "Consequence of Error"]


def soc6(c):
    m = re.match(r"(\d{2}-\d{4})", str(c))
    return m.group(1) if m else None


# --------------------------------------------------------------------------
# Two exposure scores: the broken one, and the repository's own correct one.
# --------------------------------------------------------------------------
el = pd.read_csv(DATA + "eloundou_gpt_occupational_exposure_scores.csv")
el.columns = [c.strip() for c in el.columns]
el["soc"] = el["O*NET-SOC Code"].map(soc6)
el["en_raw"] = el[["human_rating_beta", "dv_rating_beta"]].mean(axis=1)
el["en_dv"] = pd.to_numeric(el["dv_rating_beta"], errors="coerce")
EL = el.dropna(subset=["soc"]).groupby("soc", as_index=False)[["en_raw", "en_dv"]].mean()

wc = pd.read_csv(DATA + "onet_work_context_ratings.csv")
wc.columns = [c.strip() for c in wc.columns]
wc["cv"] = pd.to_numeric(wc["Data Value"], errors="coerce")
wc["soc"] = wc["O*NET-SOC Code"].map(soc6)

g = wc[(wc["Scale ID"] == "CX") & (wc["Element Name"].isin(COMP_VARS))]
piv = g.pivot_table(index="soc", columns="Element Name", values="cv")
piv = (piv - piv.min()) / (piv.max() - piv.min())
GOOD = pd.DataFrame({"comp_good": piv.mean(axis=1)}).reset_index()

B = wc.dropna(subset=["soc", "cv"]).groupby("soc", as_index=False)["cv"].mean()
B["comp_bad"] = (B.cv - B.cv.min()) / (B.cv.max() - B.cv.min())

R = EL.merge(GOOD, on="soc", how="left").merge(B[["soc", "comp_bad"]], on="soc", how="left")
R["comp_good"] = R.comp_good.fillna(R.comp_good.median())
R["comp_bad"] = R.comp_bad.fillna(R.comp_bad.median())
R["en_mm"] = (R.en_raw - R.en_raw.min()) / (R.en_raw.max() - R.en_raw.min())
R["rep_good"] = R.en_mm * (1 - R.comp_good)
R["rep_bad"] = R.en_dv * (1 - R.comp_bad)

XW = pd.read_csv(DATA + "occ2010_soc_crosswalk.csv")
COLS = ["rep_good", "rep_bad", "en_raw"]


def lookup(soc):
    hit = R[R.soc == soc]
    if len(hit):
        return [hit[c].iloc[0] for c in COLS]
    for n in (5, 2):
        hit = R[R.soc.str.startswith(soc[:n])]
        if len(hit):
            return [hit[c].mean() for c in COLS]
    return [np.nan] * len(COLS)


got = np.array([lookup(s) for s in XW.soc])
for i, c in enumerate(COLS):
    XW[c] = got[:, i]
OCC = XW[["occ", "title"] + COLS].dropna(subset=["rep_good"]).drop_duplicates("occ")

P = pd.read_csv(os.path.join(HERE, "cps_panel.csv"))
W = P.pivot_table(index=["occ", "year"], columns="band", values="emp",
                  aggfunc="sum").fillna(0.0).reset_index()
W = W.merge(OCC, on="occ", how="left")
D = W[(W.year >= 2016) & W.rep_good.notna()].copy()
D["tot"] = D[["a20_24", "a25_34", "a35p"]].sum(axis=1)
D = D[(D.a20_24 > 0) & (D.tot > 0)].copy()
D["ly"] = np.log(D.a20_24)
D["l2534"] = np.log(D.a25_34.clip(lower=1))
D["lo"] = np.log(D.a35p.clip(lower=1))
D["ltot"] = np.log(D.tot)
D["share"] = 100 * D.a20_24 / D.tot
for c in COLS:
    D[c + "_rk"] = D[c].rank(pct=True)


# --------------------------------------------------------------------------
# Two-way FE via weighted alternating projections. Reproduces the dummy-variable
# estimates in cps_panel_did.py exactly and runs fast enough for 5,000 permutations.
# --------------------------------------------------------------------------
def _demean(M, oc, yc, w, n_o, n_y, iters=60, tol=1e-11):
    M = M.astype(float).copy()
    so = np.bincount(oc, weights=w, minlength=n_o)
    sy = np.bincount(yc, weights=w, minlength=n_y)
    for _ in range(iters):
        prev = M.copy()
        for j in range(M.shape[1]):
            M[:, j] -= (np.bincount(oc, weights=w * M[:, j], minlength=n_o) / so)[oc]
        for j in range(M.shape[1]):
            M[:, j] -= (np.bincount(yc, weights=w * M[:, j], minlength=n_y) / sy)[yc]
        if np.max(np.abs(M - prev)) < tol:
            break
    return M


def fe_did(d, ycol, xvals, wcol="tot", post_from=2023):
    post = (d["year"].values >= post_from).astype(float)
    z = (xvals - xvals.mean()) / xvals.std()
    X = (z * post).reshape(-1, 1)
    y = d[ycol].values.reshape(-1, 1)
    w = np.ones(len(d)) if wcol is None else d[wcol].values.astype(float)
    w = w / w.mean()
    oc, ou = pd.factorize(d["occ"].values)
    yc, yu = pd.factorize(d["year"].values)
    M = _demean(np.hstack([X, y]), oc, yc, w, len(ou), len(yu))
    xt, yt = M[:, 0], M[:, 1]
    sxx = (w * xt * xt).sum()
    b = (w * xt * yt).sum() / sxx
    r = yt - b * xt
    s = np.bincount(oc, weights=w * xt * r, minlength=len(ou))
    G = len(ou)
    se = float(np.sqrt(max((s ** 2).sum() / sxx ** 2 * (G / (G - 1)), 0)))
    t = b / se
    return b, se, t, 2 * (1 - sp.norm.cdf(abs(t))), G, len(d)


def line(lbl, b, se, t, p):
    star = " ***" if p < 0.01 else " **" if p < 0.05 else " *" if p < 0.10 else ""
    print(f"  {lbl:<40}{b:>+10.4f}{se:>9.4f}{t:>+7.2f}{p:>9.4f}{star}")


print("=" * 100)
print("[0] HOW BROKEN IS THE MEASURE cps_panel_did.py USED?")
print("=" * 100)
print("\n  O*NET work-context rows by scale (all of these were averaged together):")
print(wc.groupby("Scale ID")["cv"].agg(["count", "min", "max", "mean"]).round(2).to_string())
M = B[["soc", "comp_bad"]].merge(GOOD, on="soc")
print(f"\n  correlation, broken complementarity vs correct: r = {M.comp_bad.corr(M.comp_good):+.3f} "
      f"(Spearman {M.comp_bad.corr(M.comp_good, method='spearman'):+.3f}), n = {len(M)}")
o = OCC.drop_duplicates("occ")
print(f"\n  corrected score: skew {o.rep_good.skew():.2f}, "
      f"{100*(o.rep_good < 0.01).mean():.1f}% below 0.01, max {o.rep_good.max():.3f}")
print(f"  broken score   : skew {o.rep_bad.skew():.2f}, "
      f"{100*(o.rep_bad < 0.01).mean():.1f}% below 0.01, max {o.rep_bad.max():.3f}")
print("\n  top 6 occupations, corrected score:")
for _, x in o.nlargest(6, "rep_good").iterrows():
    print(f"    {x.rep_good:.3f}  {x.title}")
print("  top 6 occupations, broken score (the audit's farmers problem):")
for _, x in o.nlargest(6, "rep_bad").iterrows():
    print(f"    {x.rep_bad:.3f}  {x.title}")

print("\n" + "=" * 100)
print("[1] THE AGE BANDS, RE-RUN. Employment-weighted, occupation + year FE,")
print("    clustered on occupation, 2016-2026, post = 2023+.")
print("=" * 100)
OUTCOMES = [("log emp 20-24", "ly"), ("log emp 25-34", "l2534"),
            ("log emp 35+", "lo"), ("log TOTAL emp", "ltot"),
            ("young SHARE of occupation (pp)", "share")]
MEASURES = [("A  corrected (CX + 5 elements)", "rep_good"),
            ("B  corrected, rank transformed", "rep_good_rk"),
            ("C  raw Eloundou exposure", "en_raw"),
            ("D  raw exposure, rank transformed", "en_raw_rk"),
            ("E  BROKEN, as in cps_panel_did.py", "rep_bad")]
for mlab, mcol in MEASURES:
    print(f"\n{mlab}")
    print(f"  {'outcome':<40}{'coef':>10}{'se':>9}{'t':>7}{'p':>9}")
    for olab, ocol in OUTCOMES:
        line(olab, *fe_did(D, ocol, D[mcol].values)[:4])
print("\n  Row E reproduces the published table exactly. Every other row shows the")
print("  young share moving by roughly twenty times as much, at p < 0.001.")

print("\n" + "=" * 100)
print("[2] IS THE CORRECTED RESULT ROBUST? (the previous one died on 2 occupations)")
print("=" * 100)
b0 = fe_did(D, "share", D.rep_good.values)[0]
top = o.nlargest(20, "rep_good").occ.tolist()
print(f"\n  {'dropped':<16}{'occs':>7}{'coef':>10}{'t':>8}{'p':>9}")
for k in [0, 2, 5, 12, 20]:
    s = D[~D.occ.isin(top[:k])]
    bb, _, t, p, GG, _ = fe_did(s, "share", s.rep_good.values)
    print(f"  top {k:<12}{GG:>7}{bb:>+10.4f}{t:>+8.2f}{p:>9.4f}")
loo = np.array([fe_did(D[D.occ != oc], "share", D[D.occ != oc].rep_good.values)[0]
                for oc in D.occ.unique()])
print(f"\n  leave-one-out over all {len(loo)} occupations: "
      f"[{loo.min():+.4f}, {loo.max():+.4f}], sign flips {(loo > 0).sum()}")
rng = np.random.default_rng(11)
ux = D.drop_duplicates("occ").set_index("occ").rep_good
idx = D.occ.map({oc: i for i, oc in enumerate(ux.index)}).values
vals = ux.values
null = np.array([fe_did(D, "share", rng.permutation(vals)[idx])[0] for _ in range(5000)])
print(f"  randomization inference, 5000 draws: {abs(b0)/null.std():.2f} null SDs, "
      f"one-sided p {(null <= b0).mean():.4f}, two-sided p {(np.abs(null) >= abs(b0)).mean():.4f}")

print("\n" + "=" * 100)
print("[3] WHY IT IS STILL NOT AN AI FINDING")
print("=" * 100)
d = D.copy()
w = d.tot.values / d.tot.mean()
z = ((d.rep_good - d.rep_good.mean()) / d.rep_good.std()).values
yrs = [y for y in sorted(d.year.unique()) if y != 2022]
X = np.column_stack([z * (d.year.values == y) for y in yrs])
y = d["share"].values.reshape(-1, 1)
oc, ou = pd.factorize(d.occ.values)
yc, yu = pd.factorize(d.year.values)
Md = _demean(np.hstack([X, y]), oc, yc, w, len(ou), len(yu))
Xt, yt = Md[:, :-1], Md[:, -1]
sw = np.sqrt(w)
bb, *_ = np.linalg.lstsq(Xt * sw[:, None], yt * sw, rcond=None)
res = yt - Xt @ bb
XtX = np.linalg.pinv((Xt * w[:, None]).T @ Xt)
meat = np.zeros((Xt.shape[1],) * 2)
for gg in np.unique(oc):
    gi = np.where(oc == gg)[0]
    s = (Xt[gi] * w[gi, None]).T @ res[gi]
    meat += np.outer(s, s)
G = len(ou)
se_all = np.sqrt(np.maximum(np.diag(XtX @ meat @ XtX * (G / (G - 1))), 0))
print("\n  Event study on the young share, base year 2022:")
print(f"  {'year':<8}{'coef':>10}{'se':>9}{'t':>8}   period")
npre = 0
for i, yv in enumerate(yrs):
    tt = bb[i] / se_all[i]
    if yv < 2022 and abs(tt) > 1.96:
        npre += 1
    print(f"  {yv:<8}{bb[i]:>+10.4f}{se_all[i]:>9.4f}{tt:>+8.2f}   "
          f"{'pre ' if yv < 2022 else 'post'}{' *' if abs(tt) > 1.96 else ''}")
print(f"\n  {npre} of {sum(1 for y in yrs if y < 2022)} pre-period years individually significant,")
print("  all positive and declining from 2018. That is a pre-trend, not a break.")


def seg(dd, knot, label):
    ww = dd.tot.values / dd.tot.mean()
    zz = ((dd.rep_good - dd.rep_good.mean()) / dd.rep_good.std()).values
    t = dd.year.values.astype(float) - knot
    Xs = np.column_stack([zz * t, zz * np.maximum(t, 0)])
    ys = dd["share"].values.reshape(-1, 1)
    o_, ou_ = pd.factorize(dd.occ.values)
    y_, yu_ = pd.factorize(dd.year.values)
    Ms = _demean(np.hstack([Xs, ys]), o_, y_, ww, len(ou_), len(yu_))
    Xt_, yt_ = Ms[:, :-1], Ms[:, -1]
    sw_ = np.sqrt(ww)
    b_, *_ = np.linalg.lstsq(Xt_ * sw_[:, None], yt_ * sw_, rcond=None)
    r_ = yt_ - Xt_ @ b_
    XtX_ = np.linalg.pinv((Xt_ * ww[:, None]).T @ Xt_)
    mt = np.zeros((Xt_.shape[1],) * 2)
    for gg in np.unique(o_):
        gi = np.where(o_ == gg)[0]
        s = (Xt_[gi] * ww[gi, None]).T @ r_[gi]
        mt += np.outer(s, s)
    Gn = len(ou_)
    sev = np.sqrt(np.maximum(np.diag(XtX_ @ mt @ XtX_ * (Gn / (Gn - 1))), 0))
    tc = b_[1] / sev[1]
    print(f"  {label:<38} pre-slope {b_[0]:>+7.4f} (t {b_[0]/sev[0]:>+5.2f})   "
          f"slope CHANGE {b_[1]:>+7.4f} (t {tc:>+5.2f}, p {2*(1-sp.norm.cdf(abs(tc))):.3f})")


print("\n  Trend-break test, pp/year per 1 SD of exposure.")
print("  A step dummy cannot separate a break from a trend already underway.\n")
seg(D, 2022, "knot 2022, full 2016-2026")
seg(D[D.year <= 2025], 2022, "knot 2022, excl. partial 2026")
seg(D[D.year >= 2018], 2022, "knot 2022, from 2018")
seg(D[~D.year.isin([2020, 2021])], 2022, "knot 2022, drop COVID years")
print()
seg(D[D.year <= 2025], 2019, "PLACEBO knot 2019")
seg(D[D.year <= 2025], 2020, "PLACEBO knot 2020")
print("\n  No specification finds a slope change at 2022. Both placebo knots do.")

bu, seu, tu, pu, _, _ = fe_did(D, "share", D.rep_good.values, wcol=None)
print()
line("unweighted young share", bu, seu, tu, pu)

print("\n" + "=" * 100)
print("[4] WHERE THE MOVEMENT ACTUALLY IS: young share by exposure tercile")
print("=" * 100)
q = D.drop_duplicates("occ")[["occ", "rep_good"]]
cut = q.rep_good.quantile([1 / 3, 2 / 3]).values
D["terc"] = np.where(D.rep_good >= cut[1], "high",
                     np.where(D.rep_good <= cut[0], "low", "mid"))
T = (D[D.terc != "mid"].groupby(["year", "terc"])
     .apply(lambda gg: np.average(gg.share, weights=gg.tot), include_groups=False)
     .unstack())
T["gap"] = T["high"] - T["low"]
print("\n  Employment-weighted young (20-24) share of employment, percent\n")
print(T.rename(columns={"high": "high exposure", "low": "low exposure",
                        "gap": "gap (high-low)"}).round(2).to_string())
print(f"\n  high-exposure young share 2016 -> 2025: {T.loc[2016,'high']:.2f} -> {T.loc[2025,'high']:.2f}  "
      f"({T.loc[2025,'high']-T.loc[2016,'high']:+.2f}pp)")
print(f"  low-exposure  young share 2016 -> 2025: {T.loc[2016,'low']:.2f} -> {T.loc[2025,'low']:.2f}  "
      f"({T.loc[2025,'low']-T.loc[2016,'low']:+.2f}pp)")
print("\n  The gap widens because the comparison group moved. The treated group is flat.")

fig, ax = plt.subplots(1, 2, figsize=(13, 5))
ax[0].plot(T.index, T["high"], "o-", color="#c1440e", label="High AI exposure")
ax[0].plot(T.index, T["low"], "o-", color="#2b6a8f", label="Low AI exposure")
ax[0].axvline(2022.9, ls="--", c="grey", lw=1)
ax[0].text(2022.98, ax[0].get_ylim()[1] * 0.98, " ChatGPT", fontsize=8, color="grey", va="top")
ax[0].set_title("Young (20-24) share of employment, by AI exposure tercile", fontsize=11)
ax[0].set_ylabel("percent of occupation employment")
ax[0].legend(fontsize=9)
ax[0].grid(alpha=.3)
ax[1].plot(T.index, T["gap"], "o-", color="#444")
ax[1].axvline(2022.9, ls="--", c="grey", lw=1)
ax[1].set_title("Gap (high minus low). Widening is driven by the low-exposure side.", fontsize=11)
ax[1].set_ylabel("percentage points")
ax[1].grid(alpha=.3)
fig.suptitle("The corrected entry-level result: a decade-long trend, not a 2022 break",
             fontsize=12.5, weight="bold")
fig.tight_layout()
out = os.path.join(HERE, "entry_level_measure_reaudit.png")
fig.savefig(out, dpi=130)
print(f"\n  chart written: {out}")
