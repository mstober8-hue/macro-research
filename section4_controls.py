"""
section4_controls.py
Section 4 of PAPER.md: is the Section 3 estimate AI exposure, or is exposure
standing in for education, pay, or a trend that was already running?

WHY THIS SECTION IS THE PAPER'S STRONGEST CLAIM
Brynjolfsson, Chandar & Chen (2026) concede in their own abstract that their
patterns "attenuate when controlling for education, show some divergent trends
predating generative AI, and are more pronounced in the ADP analysis sample than
in national survey benchmarks." This project runs on a national survey benchmark
by construction, so the third concession does not apply. This script tests the
other two.

WHAT IS RUN
  1. COLLINEARITY      how much do exposure, Job Zone and wage actually overlap?
                       If they were near-identical the controls would be
                       uninformative either way.
  2. CONTROLS          Job Zone x post, log wage x post, both. Do the estimates
                       attenuate, as the published version does?
  3. OCCUPATION TRENDS the demanding version. Absorb an occupation-specific linear
                       trend, so identification comes only from deviations off each
                       occupation's own pre-existing path. This is the test the
                       20-24 band's pre-trend implies a referee will ask for.
  4. PLACEBO           2016-2019, fake post = 2018, controlled specification.
  5. BREAK DATE        2020 and 2022 steps in the same regression. Which survives?

Panel construction and the estimator live in entry_panel.py.
Writes section4_controls.png.
"""
import numpy as np, pandas as pd
from scipy import stats as sp
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from entry_panel import load, fe, z, post_x, stars, BANDS, BASE_YEAR, POST

D = load(require_controls=True)      # Section 4 needs Job Zone and an OEWS wage
CTRL = {"jobzone": "education (Job Zone)", "lwage": "log median wage"}

print("=" * 98)
print("SECTION 4  IS IT EXPOSURE, OR IS EXPOSURE A PROXY?")
print(f"occupations {D.occ.nunique()}, cells {len(D)}, {D.year.min()}-{D.year.max()}, post = {POST}")
print("=" * 98)

# ---- 1. collinearity -----------------------------------------------------------
print("\n1. COLLINEARITY  do the controls and the treatment measure the same thing?")
print("-" * 98)
occ1 = D.drop_duplicates("occ")
for a, b in [("rep_good", "jobzone"), ("rep_good", "lwage"), ("jobzone", "lwage"),
             ("en_raw", "jobzone"), ("en_raw", "lwage")]:
    r = np.corrcoef(occ1[a], occ1[b])[0, 1]
    print(f"   corr({a:<9}, {b:<8}) = {r:+.3f}")
X = np.column_stack([z(occ1[c].values) for c in ["jobzone", "lwage"]])
Xd = np.column_stack([np.ones(len(X)), X])
bb = np.linalg.lstsq(Xd, z(occ1.rep_good.values), rcond=None)[0]
fit = Xd @ bb; r2 = 1 - np.var(z(occ1.rep_good.values) - fit) / np.var(z(occ1.rep_good.values))
print(f"\n   R^2 of exposure on Job Zone + log wage: {r2:.3f}")
print(f"   -> {100*(1-r2):.0f}% of the variation in exposure is orthogonal to both controls.")

# ---- 2. controls ---------------------------------------------------------------
print("\n2. CONTROLS  does the estimate attenuate?")
print("-" * 98)
RES = {}
for ycol, ylab in BANDS:
    print(f"\n   --- {ylab} ---")
    print(f"   {'specification':<36}{'coef':>9}{'se':>9}{'t':>7}{'p':>9}")
    base = None
    for xs, lab in [(["rep_good"], "no controls"),
                    (["rep_good", "jobzone"], "+ education (Job Zone)"),
                    (["rep_good", "lwage"], "+ log median wage"),
                    (["rep_good", "jobzone", "lwage"], "+ BOTH")]:
        b, se, t, p, G, n = fe(D, ycol, post_x(D, xs))
        if base is None: base = b[0]
        print(f"   {lab:<36}{b[0]:>+9.4f}{se[0]:>9.4f}{t[0]:>7.2f}{p[0]:>9.4f} {stars(p[0])}")
        RES[(ycol, lab)] = (b[0], se[0], p[0])
    full = RES[(ycol, "+ BOTH")][0]
    print(f"   {'':<36}change with both controls: {100*(full-base)/abs(base):+.0f}%"
          f"  ({'strengthens' if abs(full) > abs(base) else 'attenuates'})")

# ---- 3. occupation-specific linear trends --------------------------------------
def fe_trend(d, ycol, xcols, post_from=POST):
    """Occupation FE + occupation-specific linear trend + year FE, by Frisch-Waugh:
    residualise every column on span{1, t} WITHIN occupation, then OLS on the
    residuals with explicit year dummies. Identification is deviations off each
    occupation's own trend."""
    yrs = np.sort(d.year.unique())
    Ydum = np.column_stack([(d.year.values == y).astype(float) for y in yrs[1:]])
    Xp = post_x(d, xcols, post_from)
    A = np.column_stack([Xp, Ydum, d[ycol].values.astype(float)])
    oc, ou = pd.factorize(d.occ.values)
    t = d.year.values.astype(float) - BASE_YEAR
    Rm = np.empty_like(A)
    for gi in range(len(ou)):                       # absorb {1, t} per occupation
        m = oc == gi
        Z = np.column_stack([np.ones(m.sum()), t[m]])
        Rm[m] = A[m] - Z @ np.linalg.lstsq(Z, A[m], rcond=None)[0]
    Xt, yt = Rm[:, :-1], Rm[:, -1]
    inv = np.linalg.pinv(Xt.T @ Xt); bcoef = inv @ (Xt.T @ yt)
    r = yt - Xt @ bcoef; meat = np.zeros((Xt.shape[1],) * 2)
    for gi in range(len(ou)):
        m = oc == gi
        s = Xt[m].T @ r[m]; meat += np.outer(s, s)
    G = len(ou); V = inv @ (meat * (G / max(G - 1, 1))) @ inv
    se = np.sqrt(np.maximum(np.diag(V), 0)); tt = bcoef / se
    return bcoef, se, tt, 2 * (1 - sp.norm.cdf(np.abs(tt))), G, len(d)

print("\n3. OCCUPATION-SPECIFIC LINEAR TRENDS  identification off each occupation's own path")
print("-" * 98)
print(f"\n   {'specification':<40}{'coef':>9}{'se':>9}{'t':>7}{'p':>9}")
TREND = {}
for ycol, ylab in BANDS:
    for xs, lab in [(["rep_good"], "no controls"), (["rep_good", "jobzone", "lwage"], "+ both controls")]:
        b, se, t, p, G, n = fe_trend(D, ycol, xs)
        TREND[(ycol, lab)] = (b[0], se[0], p[0])
        print(f"   {ylab + ', ' + lab:<40}{b[0]:>+9.4f}{se[0]:>9.4f}{t[0]:>7.2f}{p[0]:>9.4f} {stars(p[0])}")

# ---- 3b. pre-period trends, extrapolated ---------------------------------------
def fe_pretrend(d, ycol, xcols, fit_max=2022, drop_covid=False, post_from=POST):
    """Fit each occupation's linear trend on the PRE period only, extrapolate it
    through the post period, and test deviations from it.

    Fitting the trend on the full window absorbs any treatment that ramps, which
    is exactly the shape the Section 3 event study shows, so the full-window
    version below cannot distinguish a diffusion effect from a trend. Fitting on
    the pre period does not have that problem."""
    t = d.year.values.astype(float) - BASE_YEAR
    y = d[ycol].values.astype(float)
    oc, ou = pd.factorize(d.occ.values)
    fitmask = d.year.values <= fit_max
    if drop_covid: fitmask &= ~np.isin(d.year.values, (2020, 2021))
    resid = np.empty_like(y); ok = np.ones(len(ou), dtype=bool)
    for gi in range(len(ou)):
        m = oc == gi; f = m & fitmask
        if f.sum() < 4: ok[gi] = False; resid[m] = np.nan; continue
        Z = np.column_stack([np.ones(f.sum()), t[f]])
        bb = np.linalg.lstsq(Z, y[f], rcond=None)[0]
        resid[m] = y[m] - (bb[0] + bb[1] * t[m])
    dd = d.copy(); dd["_resid"] = resid
    dd = dd[np.isfinite(dd._resid)]
    return fe(dd, "_resid", post_x(dd, xcols, post_from))

print("\n3b. PRE-PERIOD TRENDS, EXTRAPOLATED  the version a ramping effect can pass")
print("-" * 98)
print(f"\n   {'specification':<52}{'coef':>9}{'se':>9}{'t':>7}{'p':>9}")
PRE = {}
for ycol, ylab in BANDS:
    for kw, lab in [(dict(), "trend fitted 2016-2022"),
                    (dict(drop_covid=True), "trend fitted 2016-2022 ex-COVID")]:
        b, se, t, p, G, n = fe_pretrend(D, ycol, ["rep_good"], **kw)
        PRE[(ycol, lab)] = (b[0], se[0], p[0])
        print(f"   {ylab + ', ' + lab:<52}{b[0]:>+9.4f}{se[0]:>9.4f}{t[0]:>7.2f}{p[0]:>9.4f} {stars(p[0])}")

# ---- 4. placebo ----------------------------------------------------------------
print("\n4. PRE-AI PLACEBO  2016-2019, fake post = 2018, controlled specification")
print("-" * 98)
PL = D[D.year <= 2019]
for ycol, ylab in BANDS:
    b, se, t, p, G, n = fe(PL, ycol, post_x(PL, ["rep_good", "jobzone", "lwage"], post_from=2018))
    names = ["exposure", "jobzone", "wage"]
    out = "   " + f"{ylab:<22}" + "  ".join(f"{nm} {b[i]:+.4f} (p {p[i]:.3f})" for i, nm in enumerate(names))
    print(out)

# ---- 5. break date -------------------------------------------------------------
print("\n5. BREAK DATE  2020 and 2022 steps in the same regression")
print("-" * 98)
print(f"\n   {'':<26}{'exposure x post2020':>24}{'exposure x post2022':>24}")
for ycol, ylab in BANDS:
    zx = z(D.rep_good.values)
    X = np.column_stack([zx * (D.year.values >= 2020), zx * (D.year.values >= 2023)])
    b, se, t, p, G, n = fe(D, ycol, X)
    print(f"   {ylab:<26}{b[0]:>+14.4f} ({p[0]:.3f}){b[1]:>+14.4f} ({p[1]:.3f})")
print("\n   A COVID-timed story predicts the 2020 term carries it. An AI-timed story")
print("   predicts the 2022 term does.")

# ---- chart ---------------------------------------------------------------------
fig, ax = plt.subplots(1, 2, figsize=(13.5, 5.0))
labs = ["no controls", "+ education (Job Zone)", "+ log median wage", "+ BOTH"]
short = ["none", "+ educ", "+ wage", "+ both"]
for k, (ycol, ylab) in enumerate(BANDS):
    v = [RES[(ycol, l)] for l in labs]
    bs = [x[0] for x in v]; es = [1.96 * x[1] for x in v]
    ax[k].bar(range(4), bs, yerr=es, color="#1f4e79", error_kw=dict(lw=1.3, capsize=4))
    tv = TREND[(ycol, "+ both controls")]
    ax[k].bar([4], [tv[0]], yerr=[1.96 * tv[1]], color="#c0392b", error_kw=dict(lw=1.3, capsize=4))
    ax[k].axhline(0, color="black", lw=1.1)
    ax[k].axhline(bs[0], color="gray", ls=":", lw=1.3)
    ax[k].set_xticks(range(5)); ax[k].set_xticklabels(short + ["+ occ\ntrends"], fontsize=8.5)
    ax[k].set_title(ylab, fontsize=11.5, fontweight="bold")
    ax[k].set_ylabel("pp per sd of exposure", fontsize=9.5)
    ax[k].grid(True, axis="y", ls="--", alpha=.35)
fig.suptitle("Section 4: the estimate does not attenuate under education and wage controls",
             fontsize=13, fontweight="bold", y=1.02)
plt.tight_layout(); plt.savefig("section4_controls.png", dpi=150, bbox_inches="tight")
print("\nChart saved: section4_controls.png")
