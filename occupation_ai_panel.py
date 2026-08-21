"""
occupation_ai_panel.py
The acceleration test, finally run with power: ~700 occupations instead of 9 sectors.

WHY THIS EXISTS
The single biggest admitted weakness of this project's AI arm is the recency
failure. The productivity level result is strong (replaceability predicts real
productivity growth at r = +0.90), but the test of whether replaceable sectors
ACCELERATED after generative AI arrived comes back null every way it has been
tried: r = +0.45 (p = 0.22) on the theoretical replaceability score, +0.26 on
AIIE, +0.41 on the AEI revealed-usage score, and positive-but-insignificant
across five different baseline and post-window choices. The project's honest
summary is that the AI claim "rests on levels rather than on a discontinuity
timed to AI's arrival."

Every one of those attempts had n = 9. The critical |r| for significance at
n = 9 is 0.666, so a real acceleration effect of moderate size was never
detectable. The failure has been reported as a substantive limitation when it
may only ever have been a power problem. This runs the identical test where the
sample size can actually settle it.

THE DESIGN
BLS OEWS publishes national employment for roughly 800 detailed SOC occupations.
Four vintages give three windows:

    2013 -> 2019   pre-AI, pre-COVID. The PLACEBO.
    2019 -> 2022   spans COVID.
    2022 -> 2025   post-reopening, squarely the generative-AI era. The TEST.

All growth is annualized log change, so windows of different length compare
directly. The acceleration measure is exactly the project's own, moved to the
occupation level:

    acceleration_o = annualized dlog(E_o) 2022-2025  -  annualized dlog(E_o) 2013-2019

If AI is displacing replaceable work, acceleration should be more negative where
replaceability is higher. That is a single cross-sectional regression with
n in the hundreds rather than 9.

A stacked difference-in-differences is reported alongside it. Stacking the three
windows with occupation fixed effects absorbs each occupation's own long-run
trend entirely, so the coefficient on (replaceability x AI-window) is identified
only from how an occupation's growth in 2022-2025 differs from its own history.
That is a strictly stronger design than the cross-sectional acceleration
regression, because it cannot be driven by occupations that were always
shrinking.

STANDARD ERRORS
Occupations are not independent draws. Everything that hits "computer and
mathematical occupations" hits all of them together, and replaceability is
strongly clustered within major groups. Errors are clustered on the 2-digit SOC
major group (about 22 clusters), which is the conservative choice and the reason
the p-values here are larger than a naive n = 700 would give.

THE ENTRY-LEVEL TEST
Part 3 of this script tests a hypothesis this project has never examined and
which is currently the leading finding in the AI-labor literature (Brynjolfsson,
Chandar and Chen 2025): that AI displacement shows up first in entry-level work
and is invisible in occupation totals. OEWS carries no age or tenure variable,
so this uses the wage distribution as a proxy. If the junior end of an
occupation is being hollowed out, the surviving workforce is more senior, and
the 10th percentile wage should rise RELATIVE to the median. The test is whether
that within-occupation compression is larger where replaceability is higher, in
the AI window and not in the placebo window. This is a proxy and is labeled as
one throughout; a rising p10/median ratio is consistent with a thinning junior
tier but also with several other things.

DATA CAVEAT
BLS advises against using OEWS as a time series. Occupational coding changes
between vintages (SOC 2010 through 2013, SOC 2018 from 2019), so the 2013-2019
placebo matches fewer occupations than the 2022-2025 test window. Match rates
are printed. Treat the sign and the across-window contrast as the result.

Reads FRED-Data/. Writes occupation_ai_panel.png.
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
    "2013": os.path.join(OEWS, "oews_may2013_national_occupations.xls"),
    "2019": os.path.join(OEWS, "oews_may2019_national_occupations.xlsx"),
    "2022": os.path.join(OEWS, "oews_may2022_national_occupations.xlsx"),
    "2025": os.path.join(OEWS, "oews_may2025_national_occupations.xlsx"),
}

WINDOWS = [("2013", "2019", "PLACEBO: pre-AI, pre-COVID"),
           ("2019", "2022", "spans COVID"),
           ("2022", "2025", "TEST: the generative-AI window")]


def find(f):
    if os.path.exists(DATA + f):
        return DATA + f
    return (glob.glob(DATA + "*" + f + "*") + glob.glob(DATA + "*" + f))[0]


def build_replaceability():
    """Identical construction to ai_replaceability_score.py, so results compare."""
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


def load_nat(path):
    """National occupation totals for one OEWS vintage."""
    d = pd.read_excel(path)
    d.columns = [c.strip().upper() for c in d.columns]
    gcol = "O_GROUP" if "O_GROUP" in d.columns else "OCC_GROUP"
    d = d[d[gcol].astype(str).str.strip() == "detailed"].copy()
    d["soc"] = d["OCC_CODE"].astype(str).str.strip()
    d["emp"] = pd.to_numeric(d["TOT_EMP"], errors="coerce")
    for c, name in [("A_MEDIAN", "med"), ("A_PCT10", "p10"), ("A_PCT90", "p90")]:
        d[name] = pd.to_numeric(d[c], errors="coerce")
    d = d.dropna(subset=["emp"])
    d = d[d["emp"] > 0]
    return d.groupby("soc", as_index=False).agg(
        emp=("emp", "sum"), med=("med", "mean"), p10=("p10", "mean"), p90=("p90", "mean"))


def wls_cluster(y, x, w, clusters, add_const=True):
    """Weighted OLS with cluster-robust standard errors."""
    y, x, w = np.asarray(y, float), np.asarray(x, float), np.asarray(w, float)
    X = np.column_stack([np.ones(len(x)), x]) if add_const else x[:, None]
    W = np.diag(w) if False else None
    XtWX = X.T @ (w[:, None] * X)
    XtWX_inv = np.linalg.pinv(XtWX)
    beta = XtWX_inv @ (X.T @ (w * y))
    e = y - X @ beta
    meat = np.zeros((X.shape[1], X.shape[1]))
    ids = pd.Series(clusters)
    for _, idx in ids.groupby(ids).groups.items():
        idx = np.asarray([ids.index.get_loc(i) for i in idx]) if False else np.where(ids.values == ids.loc[idx[0]])[0]
        s = X[idx].T @ (w[idx] * e[idx])
        meat += np.outer(s, s)
    G = ids.nunique()
    n, k = len(y), X.shape[1]
    scale = (G / max(G - 1, 1)) * ((n - 1) / max(n - k, 1))
    V = XtWX_inv @ (meat * scale) @ XtWX_inv
    se = np.sqrt(np.maximum(np.diag(V), 0))
    t = beta / se
    p = 2 * (1 - sp.norm.cdf(np.abs(t)))
    return beta[-1], se[-1], t[-1], p[-1], G


print("Building occupation replaceability score...")
occ = build_replaceability()
print(f"  {len(occ)} occupations scored\n")

V = {}
for y, path in VINTAGE.items():
    V[y] = load_nat(path)
    print(f"  OEWS {y}: {len(V[y])} detailed occupations, {V[y].emp.sum()/1e6:.1f}M jobs")

# ---------------------------------------------------------------- part 1
print("\n" + "=" * 100)
print("PART 1  ANNUALIZED GROWTH BY WINDOW, against replaceability")
print("=" * 100)
print("\nCoefficient is the change in annualized log employment growth for a one-unit move")
print("in replaceability (which spans 0 to 1). Employment-weighted, SEs clustered on the")
print("2-digit SOC major group.\n")
print(f"{'window':<12}{'what it is':<34}{'occ':>6}{'match':>7}{'beta':>9}{'SE':>8}{'p':>9}")

panels, rows = {}, []
for a, b, desc in WINDOWS:
    m = V[a].merge(V[b], on="soc", suffixes=("_0", "_1")).merge(occ, on="soc")
    yrs = int(b) - int(a)
    m["g"] = (np.log(m.emp_1) - np.log(m.emp_0)) / yrs
    m["w"] = m.emp_0
    m["major"] = m.soc.str[:2]
    panels[(a, b)] = m
    beta, se, t, p, G = wls_cluster(m.g, m.rep, m.w, m.major.values)
    rows.append(dict(win=f"{a}-{b}", desc=desc, beta=beta, se=se, p=p, n=len(m), G=G))
    match = len(m) / min(len(V[a]), len(V[b]))
    print(f"{a + '-' + b:<12}{desc:<34}{len(m):>6}{match:>6.0%}{beta:>+9.4f}{se:>8.4f}{p:>9.4f}")
P1 = pd.DataFrame(rows)
print(f"\n  Clusters (SOC major groups): {rows[0]['G']}")

# ---------------------------------------------------------------- part 2
print("\n" + "=" * 100)
print("PART 2  THE ACCELERATION TEST: AI window minus placebo window")
print("=" * 100)
print("\nThis is the project's n=9 acceleration test, moved to the occupation level.\n")

A = panels[("2022", "2025")].merge(
    panels[("2013", "2019")][["soc", "g"]].rename(columns={"g": "g_pre"}), on="soc")
A["accel"] = A.g - A.g_pre
beta, se, t, p, G = wls_cluster(A.accel, A.rep, A.w, A.major.values)
print(f"  acceleration ~ replaceability   beta = {beta:+.4f}  SE {se:.4f}  p = {p:.4f}  "
      f"n = {len(A)} occupations, {G} clusters")
bu, seu, tu, pu, _ = wls_cluster(A.accel, A.rep, np.ones(len(A)), A.major.values)
print(f"  unweighted                      beta = {bu:+.4f}  SE {seu:.4f}  p = {pu:.4f}")
rp, pp = sp.spearmanr(A.rep, A.accel)
print(f"  Spearman (unclustered, for reference) rho = {rp:+.3f}, p = {pp:.4f}")
print(f"\n  For comparison, the nine-sector version of this same test: r = +0.45, p = 0.22.")

# quintile view, which is robust to the linearity assumption
A["q"] = pd.qcut(A.rep, 5, labels=False, duplicates="drop")
print(f"\n  {'replaceability quintile':<26}{'mean accel (pp/yr)':>20}{'occupations':>13}")
for q, sub in A.groupby("q"):
    print(f"  Q{int(q)+1} ({sub.rep.min():.2f}-{sub.rep.max():.2f}){'':<12}"
          f"{np.average(sub.accel, weights=sub.w)*100:>+19.2f}{len(sub):>13}")

# ---------------------------------------------------------------- part 3
print("\n" + "=" * 100)
print("PART 3  STACKED DIFFERENCE-IN-DIFFERENCES with occupation fixed effects")
print("=" * 100)
print("\nStacking all three windows and absorbing an occupation fixed effect removes each")
print("occupation's own long-run trend. The coefficient below is identified only from how")
print("2022-2025 growth deviates from that occupation's own history, so it cannot be driven")
print("by occupations that were always shrinking.\n")

st = []
for (a, b), m in panels.items():
    t_ = m[["soc", "g", "w", "rep", "major"]].copy()
    t_["win"] = f"{a}-{b}"
    t_["ai"] = 1.0 if (a, b) == ("2022", "2025") else 0.0
    st.append(t_)
S = pd.concat(st, ignore_index=True)
S = S.groupby("soc").filter(lambda g: len(g) == 3)      # balanced panel only

# within-transform on occupation, then regress g on (rep x ai) plus window dummies
S["wt"] = S.groupby("soc")["w"].transform("first")
S["x"] = S.rep * S.ai
for c in ["g", "x", "ai"]:
    gm = S.groupby("soc").apply(lambda d: np.average(d[c], weights=d["wt"]))
    S[c + "_d"] = S[c] - S["soc"].map(gm)
# partial the window main effect out of both sides so x_d carries only the interaction
for c in ["g_d", "x_d"]:
    wm = S.groupby("win").apply(lambda d: np.average(d[c], weights=d["wt"]))
    S[c] = S[c] - S["win"].map(wm)
beta, se, t, p, G = wls_cluster(S.g_d, S.x_d, S.wt, S.major.values, add_const=False)
print(f"  replaceability x AI-window   beta = {beta:+.4f}  SE {se:.4f}  p = {p:.4f}")
print(f"  balanced panel: {S.soc.nunique()} occupations x 3 windows = {len(S)} observations, "
      f"{G} clusters")

# ---------------------------------------------------------------- part 4
print("\n" + "=" * 100)
print("PART 4  THE ENTRY-LEVEL PROXY: is the bottom of the wage distribution thinning?")
print("=" * 100)
print("\nOEWS has no age or tenure field. If junior work is being displaced, the surviving")
print("workforce is more senior and the 10th percentile wage RISES relative to the median.")
print("Testing whether that compression is larger where replaceability is higher.\n")
print(f"{'window':<12}{'what it is':<34}{'beta on p10/median':>21}{'SE':>8}{'p':>9}")
for a, b, desc in WINDOWS:
    m = V[a].merge(V[b], on="soc", suffixes=("_0", "_1")).merge(occ, on="soc")
    m = m.dropna(subset=["p10_0", "p10_1", "med_0", "med_1"])
    m = m[(m.p10_0 > 0) & (m.p10_1 > 0) & (m.med_0 > 0) & (m.med_1 > 0)]
    yrs = int(b) - int(a)
    m["comp_chg"] = ((np.log(m.p10_1 / m.med_1) - np.log(m.p10_0 / m.med_0))) / yrs
    m["major"] = m.soc.str[:2]
    beta, se, t, p, G = wls_cluster(m.comp_chg, m.rep, m.emp_0, m.major.values)
    print(f"{a + '-' + b:<12}{desc:<34}{beta:>+21.5f}{se:>8.5f}{p:>9.4f}")
print("\n  Positive means the bottom of the distribution rose relative to the median, which")
print("  is what a thinning junior tier would produce. Compare the AI window against the")
print("  placebo; a level that is similar in both is a long-run trend, not an AI effect.")

# ---- chart -------------------------------------------------------------------
fig, axes = plt.subplots(1, 3, figsize=(19, 6.2))

ax = axes[0]
x = np.arange(len(P1))
cols = ["#95a5a6", "#7f8c8d", "#c0392b"]
ax.bar(x, P1.beta, yerr=1.96 * P1.se, color=cols, error_kw=dict(lw=1.3, capsize=4))
ax.axhline(0, color="black", lw=1.1)
ax.set_xticks(x)
ax.set_xticklabels([f"{r.win}\n{'placebo' if i==0 else ('COVID' if i==1 else 'AI window')}"
                    for i, r in P1.iterrows()], fontsize=9)
ax.set_ylabel("coefficient on replaceability", fontsize=10)
ax.set_title("1. Annualized employment growth\nby window, n ~ 700 occupations",
             fontsize=11.5, fontweight="bold")
ax.grid(True, axis="y", ls="--", alpha=0.35)

ax = axes[1]
qs = A.groupby("q").apply(lambda d: np.average(d.accel, weights=d.w) * 100)
ax.bar(np.arange(len(qs)), qs.values, color="#1f4e79")
ax.axhline(0, color="black", lw=1.1)
ax.set_xticks(np.arange(len(qs)))
ax.set_xticklabels([f"Q{i+1}" for i in range(len(qs))], fontsize=9.5)
ax.set_xlabel("replaceability quintile (Q5 = most replaceable)", fontsize=10)
ax.set_ylabel("acceleration, pp/yr", fontsize=10)
ax.set_title("2. Acceleration by quintile\n(AI window minus pre-AI placebo)",
             fontsize=11.5, fontweight="bold")
ax.grid(True, axis="y", ls="--", alpha=0.35)

ax = axes[2]
A["bin"] = pd.qcut(A.rep, 20, duplicates="drop")
b20 = A.groupby("bin").apply(lambda d: pd.Series({
    "x": np.average(d.rep, weights=d.w), "y": np.average(d.accel, weights=d.w) * 100}))
ax.axhline(0, color="black", lw=1.0)
ax.scatter(b20.x, b20.y, s=70, color="#c0392b", edgecolors="white", zorder=3)
sl, ic, r_, p_, _ = sp.linregress(b20.x, b20.y)
xs = np.linspace(b20.x.min(), b20.x.max(), 50)
ax.plot(xs, ic + sl * xs, color="#1f4e79", lw=2.2)
ax.set_xlabel("AI replaceability (20 employment-weighted bins)", fontsize=10)
ax.set_ylabel("acceleration, pp/yr", fontsize=10)
ax.set_title("3. Binned scatter of the acceleration test\nthe n=9 version of this was r=+0.45, p=0.22",
             fontsize=11.5, fontweight="bold")
ax.grid(True, ls="--", alpha=0.35)

fig.suptitle("The acceleration test at the occupation level: does AI exposure predict a post-2022 break?",
             fontsize=13, fontweight="bold", y=1.02)
plt.tight_layout()
plt.savefig("occupation_ai_panel.png", dpi=150, bbox_inches="tight")
print("\nChart saved: occupation_ai_panel.png")
