"""
section3_core.py
The core specification for Section 3 of PAPER.md, plus the choices that could be
doing the work.

THE CLAIM
The young-worker share of employment falls in AI-exposed occupations after 2022,
within occupation, relative to less-exposed occupations.

    share_it = a_i + d_t + B * ( z(exposure_i) x post_t ) + e_it

share is the age band as a percent of the occupation's 16-64 employment, a_i and
d_t are occupation and year fixed effects, exposure is z-scored across occupations,
post = 1{year >= 2023}, cells are weighted by occupation employment, and standard
errors cluster on occupation.

WHAT IS CHECKED HERE
A referee will ask what happens if you move the cut-off, drop the weights, or let
a few huge occupations carry it. Section 5 already had a claim collapse because a
benchmark was doing the work unexamined, so every discretionary choice in the
baseline is varied here rather than asserted.

  1. EVENT STUDY     year-by-year, 2022 omitted. Is the pre-period flat, and does
                     the effect arrive when generative AI did?
  2. POST CUT-OFF    2022 vs 2023 vs 2024.
  3. WEIGHTS         employment weighted vs unweighted.
  4. INFLUENCE       drop the 10 and 25 largest occupations.

Reads cps_panel_bands.csv (build_cps_panel_bands.py) and FRED-Data/.
Writes section3_core.png.
"""
import os, re, sys, numpy as np, pandas as pd
from scipy import stats as sp
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fastfe import _demean
from datapaths import dp

HERE = os.path.dirname(os.path.abspath(__file__)); DATA = os.path.join(HERE, "FRED-Data") + os.sep
COMP_VARS = ["Physical Proximity",
             "Face-to-Face Discussions with Individuals and Within Teams",
             "Deal With External Customers or the Public in General",
             "Health and Safety of Other Workers", "Consequence of Error"]
BASE_YEAR, POST = 2022, 2023

def soc6(c):
    m = re.match(r"(\d{2}-\d{4})", str(c)); return m.group(1) if m else None

# ---- exposure: raw Eloundou GPT-4 beta, and the complementarity-adjusted composite
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

XW = pd.read_csv(DATA + "occ2010_soc_crosswalk.csv")
CS = ["rep_good", "en_raw"]
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

# ---- panel: shares off the non-overlapping bands, which must tile 16-64 ---------
P = pd.read_csv(os.path.join(HERE, "cps_panel_bands.csv"))
W = P.pivot_table(index=["occ", "year"], columns="band", values="emp",
                  aggfunc="sum").fillna(0.0).reset_index().merge(OCC, on="occ", how="inner")
NONOVERLAP = ["u20", "a20_24", "a25", "a26_30", "a31_34", "a35p"]
missing = [c for c in NONOVERLAP if c not in W.columns]
assert not missing, f"rebuild cps_panel_bands.csv: missing {missing}"
W["tot"] = W[NONOVERLAP].sum(axis=1)          # a22_25 excluded: it overlaps a20_24
D = W[(W.year >= 2016) & (W.tot > 0) & (W.a20_24 > 0) & (W.a22_25 > 0)].copy()
D["share_2024"] = 100 * D.a20_24 / D.tot
D["share_2225"] = 100 * D.a22_25 / D.tot

def fe(d, ycol, xmat, wcol="tot"):
    """Two-way FE with occupation-clustered SEs. xmat is already built."""
    y = d[ycol].values.astype(float)
    w = (d[wcol].values.astype(float) if wcol else np.ones(len(d))); w = w / w.mean()
    oc, ou = pd.factorize(d.occ.values); yc, yu = pd.factorize(d.year.values)
    M = _demean(np.hstack([xmat, y.reshape(-1, 1)]), oc, yc, w, len(ou), len(yu))
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

def z(v): return (v - v.mean()) / v.std()

def baseline(d, ycol, xcol, post_from=POST, wcol="tot"):
    X = (z(d[xcol].values) * (d.year.values >= post_from)).reshape(-1, 1)
    return fe(d, ycol, X, wcol)

def stars(p): return "***" if p < .01 else ("**" if p < .05 else ("*" if p < .10 else ""))

BANDS = [("share_2225", "22-25 (primary)"), ("share_2024", "20-24 (robustness)")]
MEAS  = [("rep_good", "composite"), ("en_raw", "raw GPT-4 beta")]

print("=" * 96)
print("SECTION 3  THE CORE RESULT")
print(f"occupations {D.occ.nunique()}, cells {len(D)}, {D.year.min()}-{D.year.max()}, post = {POST}")
print("=" * 96)
print(f"\n  {'specification':<40}{'coef':>9}{'se':>9}{'t':>7}{'p':>9}")
CORE = {}
for yc, yl in BANDS:
    for xc, xl in MEAS:
        b, se, t, p, G, n = baseline(D, yc, xc)
        CORE[(yc, xc)] = (b[0], se[0], p[0])
        print(f"  {yl + ', ' + xl:<40}{b[0]:>+9.4f}{se[0]:>9.4f}{t[0]:>7.2f}{p[0]:>9.4f} {stars(p[0])}")

print("\n" + "=" * 96)
print("1. EVENT STUDY  year-by-year exposure coefficient, 2022 omitted")
print("=" * 96)
ES = {}
for yc, yl in BANDS:
    yrs = sorted(y for y in D.year.unique() if y != BASE_YEAR)
    zx = z(D["rep_good"].values)
    X = np.column_stack([zx * (D.year.values == y) for y in yrs])
    b, se, t, p, G, n = fe(D, yc, X)
    ES[yc] = (yrs, b, se)
    print(f"\n  {yl}")
    print(f"    {'year':<8}{'coef':>10}{'se':>9}{'95% CI':>20}")
    for i, y in enumerate(yrs):
        mark = "  <- pre" if y < BASE_YEAR else ""
        print(f"    {y:<8}{b[i]:>+10.4f}{se[i]:>9.4f}"
              f"   [{b[i]-1.96*se[i]:+6.3f}, {b[i]+1.96*se[i]:+6.3f}]{mark}")
    pre = [i for i, y in enumerate(yrs) if y < BASE_YEAR]
    wald = sum(abs(b[i] / se[i]) > 1.96 for i in pre)
    print(f"    pre-2022 coefficients significant at 5%: {wald} of {len(pre)}")

print("\n" + "=" * 96)
print("2. POST CUT-OFF  does the result depend on calling 2023 the first AI year?")
print("=" * 96)
print(f"\n  {'':<24}{'22-25':>22}{'20-24':>22}")
for pf in (2022, 2023, 2024):
    row = f"  post from {pf}{'':<12}"
    for yc, _ in BANDS:
        b, se, t, p, G, n = baseline(D, yc, "rep_good", post_from=pf)
        row += f"{b[0]:>+11.4f} ({p[0]:.4f})"
    print(row)

print("\n" + "=" * 96)
print("3. WEIGHTS  employment weighted vs unweighted")
print("=" * 96)
print(f"\n  {'':<24}{'22-25':>22}{'20-24':>22}")
for wcol, lab in [("tot", "employment weighted"), (None, "unweighted")]:
    row = f"  {lab:<24}"
    for yc, _ in BANDS:
        b, se, t, p, G, n = baseline(D, yc, "rep_good", wcol=wcol)
        row += f"{b[0]:>+11.4f} ({p[0]:.4f})"
    print(row)

print("\n" + "=" * 96)
print("4. INFLUENCE  drop the largest occupations")
print("=" * 96)
size = D[D.year == BASE_YEAR].set_index("occ").tot.sort_values(ascending=False)
print(f"\n  {'':<24}{'22-25':>22}{'20-24':>22}")
for k in (0, 10, 25):
    sub = D[~D.occ.isin(size.index[:k])] if k else D
    row = f"  drop top {k:<16}" if k else f"  {'full sample':<24}"
    for yc, _ in BANDS:
        b, se, t, p, G, n = baseline(sub, yc, "rep_good")
        row += f"{b[0]:>+11.4f} ({p[0]:.4f})"
    print(row + f"   [{sub.occ.nunique()} occ]")

# ---- chart ---------------------------------------------------------------------
fig, ax = plt.subplots(1, 2, figsize=(13.5, 5.2))
for k, (yc, yl) in enumerate(BANDS):
    yrs, b, se = ES[yc]
    xs = list(yrs) + [BASE_YEAR]; bs = list(b) + [0.0]; ss = list(se) + [0.0]
    o = np.argsort(xs); xs = np.array(xs)[o]; bs = np.array(bs)[o]; ss = np.array(ss)[o]
    ax[k].axhspan(-99, 99, xmin=0, xmax=0, color="none")
    ax[k].fill_between(xs, bs - 1.96 * ss, bs + 1.96 * ss, color="#c0392b", alpha=.16)
    ax[k].plot(xs, bs, marker="o", lw=2.2, color="#c0392b")
    ax[k].axhline(0, color="black", lw=1.1)
    ax[k].axvline(BASE_YEAR, color="gray", ls=":", lw=1.4)
    ax[k].set_title(f"{yl}\nexposure x year, {BASE_YEAR} omitted", fontsize=11.5, fontweight="bold")
    ax[k].set_ylabel("pp change in young share per sd of exposure", fontsize=9.5)
    ax[k].grid(True, ls="--", alpha=.35)
    ax[k].set_ylim(min(bs - 1.96 * ss) - .1, max(bs + 1.96 * ss) + .1)
fig.suptitle("Section 3: the young-employment share falls in AI-exposed occupations after 2022",
             fontsize=13, fontweight="bold", y=1.02)
plt.tight_layout(); plt.savefig("section3_core.png", dpi=150, bbox_inches="tight")
print("\nChart saved: section3_core.png")
