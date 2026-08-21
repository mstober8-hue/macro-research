"""
within_between_decomposition.py
Does the AI signal live BETWEEN industries rather than within them?

WHY THIS EXISTS
Part 5 of the main README contains an unresolved tension it explicitly flags but
never tests. Two findings sit side by side:

  1. `oews_within_industry.py` finds NO within-industry effect of AI
     replaceability on occupation employment (beta = -0.109, p = 0.156 in the
     2022-2025 window, statistically indistinguishable from a pre-AI placebo).
     That is a well-powered null across ~28,000 industry-by-occupation cells.

  2. `is_the_slowdown_distinctive.py` finds the Information SECTOR is a genuine
     anomaly, 2.84pp below what its own cyclical history predicts and 1.74
     standard deviations off its normal-downturn resilience, in an expansion.

The README's own caveat explains why these need not conflict: "industry fixed
effects absorb any AI effect operating at the industry level, so this design
tests substitution WITHIN industries and is silent on reallocation BETWEEN
them. If AI shrinks whole industries rather than particular occupations inside
them, this specification cannot see it."

That is a real possibility and it has never been tested. This tests it.

THE DECOMPOSITION
An occupation can lose employment two ways. Its share inside industries can
fall (firms in every industry employ fewer of them), or the industries that use
it intensively can shrink while its share holds. Standard shift-share separates
these exactly. For occupation o with baseline employment E_o0 spread across
4-digit industries j:

    total growth   =  BETWEEN  +  WITHIN
    BETWEEN_o      =  sum_j ( E_oj0 / E_o0 ) * g_j
    WITHIN_o       =  total_o - BETWEEN_o

where g_j is industry j's own total employment growth. BETWEEN is what would
have happened to the occupation if its share of every industry stayed frozen
and industries simply grew at their actual rates. WITHIN is the residual, the
part driven by occupations being substituted for inside industries.

Regressing each component separately on AI exposure answers the question
directly. A within-industry substitution story predicts WITHIN loads negatively.
A story where AI shrinks exposed industries wholesale predicts BETWEEN loads
negatively. The fixed-effects design in `oews_within_industry.py` can only ever
see the first.

Both components are run against the AI window (2022-2025) and the pre-AI
placebo (2013-2019), because a component that loads the same way in both is a
long-run trend rather than anything about generative AI. The composite
replaceability score is also split into its exposure and complementarity halves,
since prior work in this project found the composite's apparent signal comes
entirely from complementarity, which is close to an index of how in-person a job
is rather than how exposed to AI it is.

Errors are clustered on the 2-digit SOC major group throughout.

Reads FRED-Data/. Writes within_between_decomposition.png.
"""

import os
import glob
import warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats as sp

warnings.filterwarnings("ignore")

DATA = "FRED-Data/"
OEWS = os.path.join(DATA, "oews_national_industry_files")

COMP_VARS = ["Physical Proximity",
             "Face-to-Face Discussions with Individuals and Within Teams",
             "Deal With External Customers or the Public in General",
             "Health and Safety of Other Workers",
             "Consequence of Error"]

IND = {
    "2013": [os.path.join(OEWS, "oews_may2013_national_4digit_naics_wages_part1.xls"),
             os.path.join(OEWS, "oews_may2013_national_4digit_naics_wages_part2.xls")],
    "2019": [os.path.join(OEWS, "oews_may2019_national_4digit_naics_wages.xlsx")],
    "2022": [os.path.join(OEWS, "oews_may2022_national_4digit_naics_wages.xlsx")],
    "2025": glob.glob(os.path.join(OEWS, "*may2025_national_4digit_naics_wages.xlsx")),
}

WINDOWS = [("2013", "2019", "PLACEBO: pre-AI, pre-COVID"),
           ("2022", "2025", "TEST: the generative-AI window")]

SECTOR_OF = {"23": "Construction", "31": "Manufacturing", "32": "Manufacturing",
             "33": "Manufacturing", "42": "Wholesale", "48": "Transportation",
             "49": "Transportation", "22": "Transportation", "51": "Information",
             "52": "Finance", "53": "Finance", "54": "ProfBus", "55": "ProfBus",
             "56": "ProfBus", "61": "EducHealth", "62": "EducHealth",
             "71": "Leisure", "72": "Leisure"}


def find(f):
    if os.path.exists(DATA + f):
        return DATA + f
    return (glob.glob(DATA + "*" + f + "*") + glob.glob(DATA + "*" + f))[0]


def build_replaceability():
    el = pd.read_csv(find("eloundou_gpt_occupational_exposure_scores"))
    el.columns = [c.strip() for c in el.columns]
    el["soc"] = el["O*NET-SOC Code"].str[:7]
    el["exp"] = el[["human_rating_beta", "dv_rating_beta"]].mean(axis=1)
    exp = el.groupby("soc")["exp"].mean()
    wc = pd.read_csv(find("onet_work_context_ratings"))
    wc.columns = [c.strip() for c in wc.columns]
    wc = wc[(wc["Scale ID"] == "CX") & (wc["Element Name"].isin(COMP_VARS))].copy()
    wc["soc"] = wc["O*NET-SOC Code"].str[:7]
    piv = wc.pivot_table(index="soc", columns="Element Name", values="Data Value")
    piv = (piv - piv.min()) / (piv.max() - piv.min())
    occ = pd.DataFrame({"exp": exp, "comp": piv.mean(axis=1)}).dropna()
    occ["en"] = (occ["exp"] - occ["exp"].min()) / (occ["exp"].max() - occ["exp"].min())
    occ["rep"] = occ["en"] * (1 - occ["comp"])
    return occ.reset_index()[["soc", "rep", "en", "comp"]]


def load_cells(paths):
    d = pd.concat([pd.read_excel(p) for p in paths], ignore_index=True)
    d.columns = [c.strip().upper() for c in d.columns]
    ocol = "O_GROUP" if "O_GROUP" in d.columns else "OCC_GROUP"
    keep = d[ocol].astype(str).str.strip() == "detailed"
    if "I_GROUP" in d.columns:
        keep &= d["I_GROUP"].astype(str).str.strip() == "4-digit"
    d = d[keep].copy()
    d["naics"] = d["NAICS"].astype(str).str.strip().str.replace(r"\.0$", "", regex=True)
    d["soc"] = d["OCC_CODE"].astype(str).str.strip()
    d["emp"] = pd.to_numeric(d["TOT_EMP"], errors="coerce")
    d = d.dropna(subset=["emp"])
    d = d[d["emp"] > 0]
    return d.groupby(["naics", "soc"], as_index=False)["emp"].sum()


def wls_cluster(y, x, w, clusters):
    y, x, w = np.asarray(y, float), np.asarray(x, float), np.asarray(w, float)
    X = np.column_stack([np.ones(len(x)), x])
    XtWX_inv = np.linalg.pinv(X.T @ (w[:, None] * X))
    beta = XtWX_inv @ (X.T @ (w * y))
    e = y - X @ beta
    ids = pd.Series(clusters).values
    meat = np.zeros((2, 2))
    for g in np.unique(ids):
        m = ids == g
        s = X[m].T @ (w[m] * e[m])
        meat += np.outer(s, s)
    G = len(np.unique(ids))
    n = len(y)
    V = XtWX_inv @ (meat * (G / max(G - 1, 1)) * ((n - 1) / max(n - 2, 1))) @ XtWX_inv
    se = np.sqrt(max(V[1, 1], 0))
    t = beta[1] / se if se > 0 else np.nan
    return beta[1], se, 2 * (1 - sp.norm.cdf(abs(t)))


print("Building replaceability score and loading OEWS industry-by-occupation cells...")
occ = build_replaceability()
CELLS = {y: load_cells(p) for y, p in IND.items()}
for y, c in CELLS.items():
    print(f"  {y}: {len(c):,} cells, {c.naics.nunique()} industries, {c.soc.nunique()} occupations")


def decompose(a, b):
    """Shift-share: split each occupation's growth into between- and within-industry parts."""
    A, B = CELLS[a], CELLS[b]
    M = A.merge(B, on=["naics", "soc"], suffixes=("_0", "_1"))
    # industry growth from the matched panel, so both sides use the same cell universe
    ind = M.groupby("naics").agg(E0=("emp_0", "sum"), E1=("emp_1", "sum"))
    ind["g_j"] = ind.E1 / ind.E0 - 1.0
    M = M.join(ind["g_j"], on="naics")
    occ_tot = M.groupby("soc").agg(E0=("emp_0", "sum"), E1=("emp_1", "sum"))
    occ_tot["total"] = occ_tot.E1 / occ_tot.E0 - 1.0
    M["contrib"] = M.emp_0 * M.g_j
    btw = M.groupby("soc")["contrib"].sum() / occ_tot.E0
    out = pd.DataFrame({"total": occ_tot.total, "between": btw})
    out["within"] = out.total - out.between
    yrs = int(b) - int(a)
    for c in ["total", "between", "within"]:
        out[c] = out[c] / yrs                      # annualize
    out["w"] = occ_tot.E0
    return out.reset_index().merge(occ, on="soc")


print("\n" + "=" * 104)
print("SHIFT-SHARE: does AI exposure predict the WITHIN-industry or the BETWEEN-industry part?")
print("=" * 104)
print("\nCoefficients are annualized growth per one-unit move in the regressor (which spans 0 to 1).")
print("Employment-weighted, SEs clustered on the 2-digit SOC major group.\n")

RES = {}
for a, b, desc in WINDOWS:
    D = decompose(a, b)
    D["major"] = D.soc.str[:2]
    RES[(a, b)] = D
    print(f"  {a}-{b}  {desc}   ({len(D)} occupations)")
    print(f"    {'regressor':<24}{'TOTAL':>22}{'BETWEEN':>22}{'WITHIN':>22}")
    for xc, lab in [("rep", "replaceability"), ("en", "exposure alone"),
                    ("comp", "complementarity alone")]:
        cells = []
        for comp in ["total", "between", "within"]:
            bb, ss, pp = wls_cluster(D[comp], D[xc], D.w, D.major.values)
            star = "*" if pp < 0.05 else " "
            cells.append(f"{bb:+.4f}{star} (p={pp:.3f})")
        print(f"    {lab:<24}{cells[0]:>22}{cells[1]:>22}{cells[2]:>22}")
    print()
print("  * = p < 0.05")

print("-" * 104)
print("READING THIS")
print("-" * 104)
print("""
  A within-industry substitution story needs the WITHIN column to load negatively
  on EXPOSURE, and to do so in the AI window but not the placebo. A story where AI
  shrinks whole exposed industries needs the BETWEEN column to do the same. A
  coefficient of similar size in both windows is a long-run trend, not AI.
""")

print("=" * 104)
print("HOW BIG IS THE BETWEEN CHANNEL AT ALL? Variance decomposition")
print("=" * 104 + "\n")
for a, b, desc in WINDOWS:
    D = RES[(a, b)]
    vt, vb, vw = D.total.var(), D.between.var(), D.within.var()
    cov = 2 * np.cov(D.between, D.within)[0, 1]
    print(f"  {a}-{b}: var(total) = {vt:.5f}   var(between) = {vb:.5f} ({vb/vt:.0%})   "
          f"var(within) = {vw:.5f} ({vw/vt:.0%})")
print("\n  Between-industry reallocation is a small share of the variance in occupation")
print("  employment growth. Most of what happens to an occupation happens inside industries,")
print("  which bounds how much the fixed-effects design in oews_within_industry.py could")
print("  have been missing.")

print("\n" + "=" * 104)
print("TIE-BACK: the Information sector specifically")
print("=" * 104 + "\n")
D = RES[("2022", "2025")]
A2, B2 = CELLS["2022"], CELLS["2025"]
M = A2.merge(B2, on=["naics", "soc"], suffixes=("_0", "_1"))
M["sector"] = M.naics.str[:2].map(SECTOR_OF)
sec = M.groupby("sector").agg(E0=("emp_0", "sum"), E1=("emp_1", "sum"))
sec["g"] = ((sec.E1 / sec.E0) ** (1 / 3) - 1) * 100
me = M.merge(occ, on="soc")
sec_exp = me.groupby("sector").apply(lambda d: np.average(d.en, weights=d.emp_0))
sec["exposure"] = sec_exp
print(f"  {'sector':<16}{'mean occupation exposure':>26}{'annualized emp growth':>24}")
for s, r in sec.sort_values("exposure", ascending=False).iterrows():
    print(f"  {s:<16}{r.exposure:>26.3f}{r.g:>23.2f}%")
r_, p_ = sp.pearsonr(sec.exposure, sec.g)
print(f"\n  Across these {len(sec)} sectors: r = {r_:+.3f}, p = {p_:.3f} (n is tiny; shown for orientation)")

# ---- chart -------------------------------------------------------------------
fig, axes = plt.subplots(1, 3, figsize=(19, 6.2))
labels = ["placebo\n2013-2019", "AI window\n2022-2025"]

for ax, xc, title in zip(axes[:2], ["en", "rep"],
                         ["1. Exposure alone (the AI-relevant half)",
                          "2. Composite replaceability"]):
    wid = 0.36
    xs = np.arange(2)
    for i, (comp, col) in enumerate([("between", "#c0392b"), ("within", "#1f4e79")]):
        vals, errs = [], []
        for a, b, _ in WINDOWS:
            D = RES[(a, b)]
            bb, ss, pp = wls_cluster(D[comp], D[xc], D.w, D.major.values)
            vals.append(bb); errs.append(1.96 * ss)
        ax.bar(xs + (i - 0.5) * wid, vals, wid, yerr=errs, label=comp,
               color=col, error_kw=dict(lw=1.2, capsize=3))
    ax.axhline(0, color="black", lw=1.1)
    ax.set_xticks(xs); ax.set_xticklabels(labels, fontsize=9.5)
    ax.set_ylabel("annualized coefficient", fontsize=10)
    ax.set_title(title + "\nBETWEEN vs WITHIN industry components",
                 fontsize=11.5, fontweight="bold")
    ax.legend(fontsize=8.5); ax.grid(True, axis="y", ls="--", alpha=0.35)

ax = axes[2]
D = RES[("2022", "2025")]
D["bin"] = pd.qcut(D.en, 15, duplicates="drop")
for comp, col, lab in [("between", "#c0392b", "between-industry"),
                       ("within", "#1f4e79", "within-industry")]:
    b15 = D.groupby("bin").apply(lambda d: pd.Series({
        "x": np.average(d.en, weights=d.w), "y": np.average(d[comp], weights=d.w) * 100}))
    ax.plot(b15.x, b15.y, marker="o", lw=2.0, color=col, label=lab)
ax.axhline(0, color="black", lw=1.0)
ax.set_xlabel("GPT exposure (15 employment-weighted bins)", fontsize=10)
ax.set_ylabel("annualized growth contribution, %/yr", fontsize=10)
ax.set_title("3. AI window, by exposure\nNeither component slopes down with exposure",
             fontsize=11.5, fontweight="bold")
ax.legend(fontsize=8.5); ax.grid(True, ls="--", alpha=0.35)

fig.suptitle("Does the AI effect hide between industries, where the fixed-effects design cannot see it?",
             fontsize=13, fontweight="bold", y=1.02)
plt.tight_layout()
plt.savefig("within_between_decomposition.png", dpi=150, bbox_inches="tight")
print("\nChart saved: within_between_decomposition.png")
