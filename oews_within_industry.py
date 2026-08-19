"""
oews_within_industry.py
The AI test at the occupation level, with industry fixed effects.

WHY THIS EXISTS
Every AI result in this project is a nine-industry cross-section. At n = 9 the
critical |r| for p < 0.05 is 0.666, so only the very largest effect can ever be
detected, and the project has now shown that by exhaustion: AIIE, the O*NET
replaceability score, AEI revealed usage, five acceleration windows, and a
rate-orthogonalized acceleration all land between r = +0.42 and +0.56 and none
clear the bar. Better measurement was never the binding constraint. Sample size
was.

There is a second, deeper problem that more industries would not fix. A sector
is the unit at which the confounds live. Interest rates, tariffs, immigration,
fiscal flows and demand shocks all hit an industry as a whole, so any
industry-level regression of AI exposure on labor outcomes is a race between AI
and everything else that varies across industries. The physical-sector
sub-project spent most of its effort on exactly one of those confounds.

This specification removes all of them at once. The unit of observation is the
(4-digit NAICS industry x detailed SOC occupation) cell, and the regression
carries industry fixed effects:

    dlog(employment)_ij  =  a_j  +  b * replaceability_i  +  e_ij

Because a_j absorbs everything common to an industry, b is identified purely by
comparing a MORE replaceable occupation against a LESS replaceable occupation
INSIDE THE SAME INDUSTRY. Construction's interest-rate shock hits every
occupation in construction, so it lands entirely in a_j and cannot contaminate
b. The same holds for tariffs, immigration enforcement, sectoral demand and
fiscal policy. Sample size goes from 9 to roughly twenty thousand cells.

THREE WINDOWS, BECAUSE ONE WINDOW CANNOT SEPARATE AI FROM COVID
The replaceability score is exposure x (1 - complementarity), where
complementarity is built from five O*NET work-context variables: physical
proximity, face-to-face discussion, dealing with the public, responsibility for
others' safety, consequence of error. That index is close to a measure of how
in-person a job is, and 2020-2022 was the largest shock to in-person work in
modern history. A single 2019-2025 regression cannot tell "AI displaced
replaceable work" apart from "in-person work recomposed after COVID". So the
same regression runs on three windows:

    2013-2019   pre-AI and pre-COVID. A placebo. Any effect here is a long-run
                automation trend that has nothing to do with generative AI.
    2019-2025   spans both COVID and AI. Reported for continuity, but it is the
                least interpretable of the three.
    2022-2025   post-reopening and squarely inside the generative-AI era. This
                is the preferred specification.

Each window also reports the exposure and complementarity components separately,
so it is visible which half of the measure is carrying the result. If the whole
effect runs through complementarity in every window including the placebo, the
finding is about physical work rather than about AI, and the write-up has to say
so.

STANDARD ERRORS
Replaceability varies at the occupation level and is constant across every
industry employing that occupation, so residuals are correlated within
occupation and ordinary standard errors would be badly understated (the Moulton
problem). Errors are clustered by occupation, with a two-way industry and
occupation variant reported alongside.

DATA CAVEAT
BLS advises against treating OEWS as a time series: estimation methodology,
industry classification (NAICS 2012 / 2017 / 2022) and occupational coding (SOC
2010 / 2018) all change between vintages. Cells are matched on exact NAICS and
SOC codes and the match rate is printed for every window, so the reader can see
how much of the sample survives. Treat magnitudes as indicative, and the sign
and the across-window contrast as the result.

Reads FRED-Data/. Writes oews_within_industry.png.
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

VINTAGE = {
    "2013": [os.path.join(OEWS, "oews_may2013_national_4digit_naics_wages_part1.xls"),
             os.path.join(OEWS, "oews_may2013_national_4digit_naics_wages_part2.xls")],
    "2019": [os.path.join(OEWS, "oews_may2019_national_4digit_naics_wages.xlsx")],
    "2022": [os.path.join(OEWS, "oews_may2022_national_4digit_naics_wages.xlsx")],
    "2025": glob.glob(os.path.join(OEWS, "*may2025_national_4digit_naics_wages.xlsx")),
}

WINDOWS = [("2013", "2019", "PLACEBO: pre-AI, pre-COVID"),
           ("2019", "2025", "spans COVID and AI"),
           ("2022", "2025", "PREFERRED: post-reopening AI window")]

# NAICS 2-digit prefix -> the project's nine sectors, for the by-sector breakdown
SECTOR_OF = {"23": "Construction", "31": "Manufacturing", "32": "Manufacturing",
             "33": "Manufacturing", "42": "Wholesale Trade", "48": "Transportation & Utilities",
             "49": "Transportation & Utilities", "22": "Transportation & Utilities",
             "51": "Information", "52": "Financial Activities", "53": "Financial Activities",
             "54": "Professional & Business", "55": "Professional & Business",
             "56": "Professional & Business", "61": "Education & Health",
             "62": "Education & Health", "71": "Leisure & Hospitality",
             "72": "Leisure & Hospitality"}


def find(f):
    if os.path.exists(DATA + f):
        return DATA + f
    return (glob.glob(DATA + "*" + f + "*") + glob.glob(DATA + "*" + f))[0]


# --------------------------------------------------------------------------
# occupation-level replaceability, identical construction to
# ai_replaceability_score.py so the two are directly comparable
# --------------------------------------------------------------------------
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


def load_oews(paths):
    """Load one or more OEWS national industry-by-occupation files into one frame.

    May 2013 ships as two .xls parts split by NAICS range, so this takes a list.
    """
    if isinstance(paths, str):
        paths = [paths]
    d = pd.concat([pd.read_excel(p) for p in paths], ignore_index=True)
    d.columns = [c.strip().upper() for c in d.columns]
    # Column names drift across vintages: May 2013 calls the occupation-level
    # column OCC_GROUP and omits I_GROUP entirely (that file is 4-digit only),
    # while May 2019 onward use O_GROUP and I_GROUP.
    ocol = "O_GROUP" if "O_GROUP" in d.columns else "OCC_GROUP"
    keep = d[ocol].astype(str).str.strip() == "detailed"
    if "I_GROUP" in d.columns:
        keep &= d["I_GROUP"].astype(str).str.strip() == "4-digit"
    d = d[keep].copy()
    d["naics"] = d["NAICS"].astype(str).str.strip().str.replace(r"\.0$", "", regex=True)
    d["soc"] = d["OCC_CODE"].astype(str).str.strip()
    d["emp"] = pd.to_numeric(d["TOT_EMP"], errors="coerce")
    d["wage"] = pd.to_numeric(d["A_MEAN"], errors="coerce")
    d = d.dropna(subset=["emp"])
    d = d[d["emp"] > 0]
    return d.groupby(["naics", "soc"], as_index=False).agg(
        emp=("emp", "sum"),
        wage=("wage", lambda s: np.nan if s.isna().all() else s.mean()))


# --------------------------------------------------------------------------
# weighted OLS with fixed effects by within-transformation, cluster-robust SEs
# --------------------------------------------------------------------------
def wdemean(df, col, group, w):
    """Weighted within-group demeaning. Absorbs the group fixed effect."""
    gm = df.groupby(group).apply(lambda g: np.average(g[col], weights=g[w]))
    return df[col] - df[group].map(gm)


def wls_cluster(y, x, w, clusters):
    """Weighted OLS of y on x (already demeaned, so no intercept), cluster-robust SE.

    clusters is a list of cluster-id arrays. One array gives one-way clustering;
    two arrays give the two-way (Cameron-Gelbach-Miller) variance V1 + V2 - V12,
    where V12 clusters on the intersection of the two.
    """
    y, x, w = np.asarray(y, float), np.asarray(x, float), np.asarray(w, float)
    XtWX = float((w * x * x).sum())
    if XtWX <= 0:
        return np.nan, np.nan, np.nan, np.nan
    beta = float((w * x * y).sum()) / XtWX
    e = y - x * beta
    n, k = len(y), 1

    def meat(ids):
        s = pd.Series(w * x * e).groupby(pd.Series(ids).values).sum()
        G = len(s)
        return float((s ** 2).sum()) * (G / max(G - 1, 1)) * ((n - 1) / max(n - k, 1))

    if len(clusters) == 1:
        V = meat(clusters[0]) / (XtWX ** 2)
    else:
        both = pd.Series(clusters[0]).astype(str) + "|" + pd.Series(clusters[1]).astype(str)
        V = (meat(clusters[0]) + meat(clusters[1]) - meat(both.values)) / (XtWX ** 2)
    se = np.sqrt(max(V, 0))
    t = beta / se if se > 0 else np.nan
    p = 2 * (1 - sp.norm.cdf(abs(t))) if se > 0 else np.nan
    return beta, se, t, p


def run_spec(panel, ycol, xcol="rep", label="", fe=True):
    d = panel.dropna(subset=[ycol, xcol, "w"]).copy()
    if fe:
        d = d.groupby("naics").filter(lambda g: len(g) >= 2)   # FE needs within variation
        yy = wdemean(d, ycol, "naics", "w")
        xx = wdemean(d, xcol, "naics", "w")
    else:
        yy = d[ycol] - np.average(d[ycol], weights=d["w"])
        xx = d[xcol] - np.average(d[xcol], weights=d["w"])
    b, se, t, p = wls_cluster(yy, xx, d["w"], [d["soc"].values])
    _, se2, _, p2 = wls_cluster(yy, xx, d["w"], [d["soc"].values, d["naics"].values])
    return dict(label=label, beta=b, se=se, t=t, p=p, se2=se2, p2=p2,
                n=len(d), n_ind=d["naics"].nunique(), n_occ=d["soc"].nunique())


def build_panel(y0, y1, occ, cache):
    for y in (y0, y1):
        if y not in cache:
            cache[y] = load_oews(VINTAGE[y])
    a, b = cache[y0], cache[y1]
    P = a.merge(b, on=["naics", "soc"], suffixes=("_0", "_1"))
    match = len(P) / min(len(a), len(b))
    P = P.merge(occ, on="soc", how="inner")
    P["dlog_emp"] = np.log(P["emp_1"]) - np.log(P["emp_0"])
    P["dlog_wage"] = np.log(P["wage_1"]) - np.log(P["wage_0"])
    P["w"] = P["emp_0"]
    P["sector"] = P["naics"].str[:2].map(SECTOR_OF)
    return P, match


# --------------------------------------------------------------------------
print("Building occupation replaceability score...")
occ = build_replaceability()
print(f"  {len(occ)} occupations scored\n")

cache = {}
panels = {}
print("=" * 104)
print("THE THREE WINDOWS")
print("=" * 104)
print("\nWithin-industry coefficient on replaceability. Employment-weighted, industry fixed")
print("effects, standard errors clustered by occupation. Both outcomes are six-year (or")
print("three-year) log changes, so coefficients across windows of different length are not")
print("directly comparable in magnitude; compare signs and significance.\n")
print(f"{'window':<12}{'what it is':<36}{'yrs':>4}{'cells':>8}{'Δlog EMP':>11}{'p':>8}"
      f"{'Δlog WAGE':>12}{'p':>8}")
summary = []
for y0, y1, desc in WINDOWS:
    P, match = build_panel(y0, y1, occ, cache)
    panels[(y0, y1)] = P
    e = run_spec(P, "dlog_emp", label=f"{y0}-{y1}")
    wg = run_spec(P, "dlog_wage", label=f"{y0}-{y1}")
    summary.append(dict(win=f"{y0}-{y1}", desc=desc, yrs=int(y1) - int(y0), match=match,
                        be=e["beta"], pe=e["p"], se=e["se"],
                        bw=wg["beta"], pw=wg["p"], sw=wg["se"], n=e["n"],
                        n_ind=e["n_ind"], n_occ=e["n_occ"]))
    print(f"{y0 + '-' + y1:<12}{desc:<36}{int(y1)-int(y0):>4}{e['n']:>8,}"
          f"{e['beta']:>+11.3f}{e['p']:>8.4f}{wg['beta']:>+12.3f}{wg['p']:>8.4f}")
S = pd.DataFrame(summary)
print("\nCell match rate on exact NAICS x SOC (code revisions cost the rest):")
for _, r in S.iterrows():
    print(f"  {r.win}: {r.match:.0%}   {r.n:,} cells, {r.n_ind} industries, {r.n_occ} occupations")

print("\n" + "=" * 104)
print("WHICH HALF OF THE MEASURE IS DOING THE WORK?")
print("=" * 104)
print("\nreplaceability = exposure x (1 - complementarity). If the result runs entirely")
print("through complementarity, and does so in the pre-COVID placebo too, then the finding")
print("is about physical and in-person work rather than about AI.\n")
print(f"{'window':<12}{'replaceability':>16}{'p':>8}{'exposure only':>16}{'p':>8}"
      f"{'complementarity':>18}{'p':>8}")
for y0, y1, _ in WINDOWS:
    P = panels[(y0, y1)]
    r_ = run_spec(P, "dlog_emp", "rep")
    e_ = run_spec(P, "dlog_emp", "en")
    c_ = run_spec(P, "dlog_emp", "comp")
    print(f"{y0 + '-' + y1:<12}{r_['beta']:>+16.3f}{r_['p']:>8.4f}"
          f"{e_['beta']:>+16.3f}{e_['p']:>8.4f}{c_['beta']:>+18.3f}{c_['p']:>8.4f}")

PREF = panels[("2022", "2025")]
print("\n" + "=" * 104)
print("PREFERRED SPECIFICATION IN DETAIL: May 2022 to May 2025")
print("=" * 104 + "\n")
print(f"{'specification':<42}{'beta':>9}{'SE':>8}{'t':>7}{'p':>9}{'2-way p':>10}{'cells':>9}")
detail = [
    run_spec(PREF, "dlog_emp", label="employment, NO industry FE (pooled)", fe=False),
    run_spec(PREF, "dlog_emp", label="employment, WITH industry FE", fe=True),
    run_spec(PREF, "dlog_wage", label="mean wage, NO industry FE (pooled)", fe=False),
    run_spec(PREF, "dlog_wage", label="mean wage, WITH industry FE", fe=True),
]
for s in detail:
    print(f"{s['label']:<42}{s['beta']:>+9.3f}{s['se']:>8.3f}{s['t']:>7.2f}"
          f"{s['p']:>9.4f}{s['p2']:>10.4f}{s['n']:>9,}")
fe_emp = detail[1]
print(f"\n  Identified from {fe_emp['n']:,} cells across {fe_emp['n_ind']} industries and "
      f"{fe_emp['n_occ']} occupations.")
print(f"  Moving from the least to the most replaceable occupation WITHIN THE SAME INDUSTRY")
print(f"  goes with a {fe_emp['beta']*100:+.1f}% employment change over three years "
      f"(p = {fe_emp['p']:.4f}).")

print("\n" + "-" * 104)
print("BY SECTOR, 2022-2025: within-industry coefficient estimated separately inside each")
print("-" * 104 + "\n")
print(f"{'sector':<28}{'beta':>9}{'SE':>8}{'p':>9}{'cells':>9}{'industries':>12}")
rows = []
for sec in sorted(PREF["sector"].dropna().unique()):
    sub = PREF[PREF["sector"] == sec]
    if sub["naics"].nunique() < 3:
        continue
    r = run_spec(sub, "dlog_emp", label=sec)
    rows.append(r)
    print(f"{sec:<28}{r['beta']:>+9.3f}{r['se']:>8.3f}{r['p']:>9.4f}{r['n']:>9,}{r['n_ind']:>12}")
BY = pd.DataFrame(rows)
print("\n  Nine sector-level tests, so Bonferroni asks for p < 0.0056 before calling any of")
print("  them individually significant.")

print("\n" + "-" * 104)
print("ROBUSTNESS, 2022-2025 employment")
print("-" * 104 + "\n")
d = PREF.copy(); d["w"] = 1.0
print(f"  unweighted (each cell counts equally)     beta={run_spec(d,'dlog_emp')['beta']:+.3f}"
      f"  p={run_spec(d,'dlog_emp')['p']:.4f}")
for cut in (100, 1000):
    r = run_spec(PREF[PREF["emp_0"] >= cut], "dlog_emp")
    print(f"  cells with >= {cut:<5} baseline jobs        beta={r['beta']:+.3f}  p={r['p']:.4f}"
          f"  n={r['n']:,}")
d = PREF.dropna(subset=["dlog_emp", "rep"]).copy()
lo, hi = d["dlog_emp"].quantile([0.01, 0.99]); d["dlog_emp"] = d["dlog_emp"].clip(lo, hi)
r = run_spec(d, "dlog_emp")
print(f"  outcome winsorized at 1st/99th pct        beta={r['beta']:+.3f}  p={r['p']:.4f}")

# ---- chart -------------------------------------------------------------------
fig, axes = plt.subplots(1, 3, figsize=(19, 6.3))

ax = axes[0]
x = np.arange(len(S)); w = 0.38
ax.bar(x - w/2, S["be"], w, yerr=1.96 * S["se"], label="Δ log employment",
       color="#1f4e79", error_kw=dict(lw=1.2, capsize=3))
ax.bar(x + w/2, S["bw"], w, yerr=1.96 * S["sw"], label="Δ log mean wage",
       color="#c0392b", error_kw=dict(lw=1.2, capsize=3))
ax.axhline(0, color="black", lw=1.1)
ax.set_xticks(x)
ax.set_xticklabels([f"{r.win}\n{'placebo' if i == 0 else ('spans COVID' if i == 1 else 'AI window')}"
                    for i, r in S.iterrows()], fontsize=9)
ax.set_ylabel("within-industry coefficient on replaceability", fontsize=10)
ax.set_title("1. The placebo is the test\nIf the effect is AI, it should be weak on the left",
             fontsize=11.5, fontweight="bold")
ax.legend(fontsize=8.5); ax.grid(True, axis="y", ls="--", alpha=0.35)

ax = axes[1]
comps = []
for y0, y1, _ in WINDOWS:
    P = panels[(y0, y1)]
    comps.append([run_spec(P, "dlog_emp", "rep")["beta"],
                  run_spec(P, "dlog_emp", "en")["beta"],
                  run_spec(P, "dlog_emp", "comp")["beta"]])
C = np.array(comps)
x = np.arange(len(WINDOWS)); w = 0.27
for i, (lab, col) in enumerate([("replaceability", "#1f4e79"), ("exposure only", "#27ae60"),
                                ("complementarity only", "#c0392b")]):
    ax.bar(x + (i - 1) * w, C[:, i], w, label=lab, color=col)
ax.axhline(0, color="black", lw=1.1)
ax.set_xticks(x); ax.set_xticklabels([f"{a}-{b}" for a, b, _ in WINDOWS], fontsize=9.5)
ax.set_ylabel("within-industry coefficient", fontsize=10)
ax.set_title("2. Which half carries the result?\nComplementarity is a physical-work index",
             fontsize=11.5, fontweight="bold")
ax.legend(fontsize=8); ax.grid(True, axis="y", ls="--", alpha=0.35)

ax = axes[2]
BYs = BY.sort_values("beta")
y = np.arange(len(BYs))
ax.barh(y, BYs["beta"], xerr=1.96 * BYs["se"],
        color=["#c0392b" if p < 0.05 else "#95a5a6" for p in BYs["p"]],
        error_kw=dict(lw=1.2, capsize=3))
ax.axvline(0, color="black", lw=1.1)
ax.axvline(fe_emp["beta"], color="#1f4e79", ls="--", lw=1.8, label="pooled 2022-2025")
ax.set_yticks(y); ax.set_yticklabels(BYs["label"], fontsize=9)
ax.set_xlabel("within-industry coefficient, 2022-2025", fontsize=10)
ax.set_title("3. Inside each sector separately\nRed = p < 0.05 uncorrected. Bars are 95% CI.",
             fontsize=11.5, fontweight="bold")
ax.legend(fontsize=8.5); ax.grid(True, axis="x", ls="--", alpha=0.35)

fig.suptitle("AI replaceability and occupation employment, identified WITHIN industry, "
             "against a pre-AI placebo", fontsize=13, fontweight="bold", y=1.02)
plt.tight_layout()
plt.savefig("oews_within_industry.png", dpi=150, bbox_inches="tight")
print("\nChart saved: oews_within_industry.png")
