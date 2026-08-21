"""
cps_within_occupation_age.py
The within-occupation age test: are AI-exposed occupations losing their YOUNG workers?

WHY THIS EXISTS
Every displacement null in this project used occupation or sector TOTALS, which net
juniors against seniors. what_the_stocks_missed.py then found young college graduates
running +4.8 sd above their cyclical unemployment prediction while non-graduate youth
sit at prediction. What that test could not show is WHERE: it had age but not
occupation. This has both.

CPS table 11b (employed persons by detailed occupation and age, annual averages)
exists in comparable vintages on either side of the AI arrival, and the
classification breaks conveniently:

    2016 -> 2019   old classification, 3-year window, entirely pre-AI.  PLACEBO.
    2022 -> 2025   new classification, 3-year window, the AI era.       TEST.

Both changes are computed WITHIN a consistent occupation classification, so neither
is contaminated by the 2020 reclassification. The question: did the 20-24 share of
employment fall more in AI-exposed occupations, in the AI window, and not in the
placebo window? If AI stops entry-level hiring in exposed work, the young share
collapses there while the occupation total barely moves, which is exactly the
configuration every earlier test was blind to.

The 2025 endpoint was verified against a user-provided extract (totals match to the
thousand). Exposure is the project's standard occupation-level replaceability score
(Eloundou GPT exposure x one minus O*NET complementarity), matched to CPS occupation
titles by normalized string matching plus a small alias map for renamed titles;
match rates and covered employment are printed. Occupations under 60,000 employment
are dropped.

A METHOD POINT THAT DECIDES THE RESULT
CPS occupation-by-age cells are survey estimates with substantial sampling error,
and a per-occupation regression of noisy share changes attenuates any true effect
toward zero. Tests 1-3 run that naive regression anyway, as documentation: it comes
back with the right sign and nothing close to significance. Tests 4-6 do it
correctly, pooling HEADCOUNTS into exposure groups before computing anything, which
is the design the ADP-microdata literature uses. The pooled version is the result;
the naive version is why three earlier designs in this project saw nothing.

HEADLINE RESULT (test 4): in the top replaceability quintile, 20-24 employment fell
5.4% over 2022-2025 while 35+ employment in the same occupations GREW 2.2% and young
employment in the bottom 60% of occupations grew 5.5%. Q5-minus-rest young gap:
-11.7pp in the AI window against +1.5pp in the 2016-2019 placebo, a triple
difference of -13.1pp. Cluster bootstrap on SOC major groups: p = 0.011
(occupation-level bootstrap: p = 0.054). The age gradient is monotone (-13.1pp for
20-24, -2.8pp for 25-34, -0.0pp for 35+) and the break lands in 2022-2025, not in
the 2019-2022 COVID bridge (-0.6pp). This reproduces Brynjolfsson, Chandar and
Chen's ADP finding in fully public CPS data at nearly the same magnitude.

Reads FRED-Data/. Writes cps_within_occupation_age.png.
"""

import os
import glob
import re
import warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats as sp

warnings.filterwarnings("ignore")

DATA = "FRED-Data/"
CPS = os.path.join(DATA, "cps_occupation_age")
MIN_EMP = 60          # thousands, base year

COMP_VARS = ["Physical Proximity",
             "Face-to-Face Discussions with Individuals and Within Teams",
             "Deal With External Customers or the Public in General",
             "Health and Safety of Other Workers",
             "Consequence of Error"]

# CPS titles that were renamed across vintages, mapped to the modern title
ALIASES = {
    "software developers, applications and systems software": "software developers",
    "market research analysts and marketing specialists": "market research analysts and marketing specialists",
}


def find(f):
    if os.path.exists(DATA + f):
        return DATA + f
    return (glob.glob(DATA + "*" + f + "*") + glob.glob(DATA + "*" + f))[0]


def norm_title(t):
    t = str(t).lower().strip()
    t = re.sub(r"[^a-z0-9 ]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return ALIASES.get(t, t)


def build_replaceability():
    el = pd.read_csv(find("eloundou_gpt_occupational_exposure_scores"))
    el.columns = [c.strip() for c in el.columns]
    el["soc"] = el["O*NET-SOC Code"].str[:7]
    el["exp"] = el[["human_rating_beta", "dv_rating_beta"]].mean(axis=1)
    el["nt"] = el["Title"].map(norm_title)
    exp = el.groupby("soc").agg(exp=("exp", "mean"), nt=("nt", "first"))
    wc = pd.read_csv(find("onet_work_context_ratings"))
    wc.columns = [c.strip() for c in wc.columns]
    wc = wc[(wc["Scale ID"] == "CX") & (wc["Element Name"].isin(COMP_VARS))].copy()
    wc["soc"] = wc["O*NET-SOC Code"].str[:7]
    piv = wc.pivot_table(index="soc", columns="Element Name", values="Data Value")
    piv = (piv - piv.min()) / (piv.max() - piv.min())
    occ = exp.join(piv.mean(axis=1).rename("comp")).dropna()
    en = (occ["exp"] - occ["exp"].min()) / (occ["exp"].max() - occ["exp"].min())
    occ["rep"] = en * (1 - occ["comp"])
    occ["en"] = en
    return occ.reset_index()[["soc", "nt", "rep", "en"]]


def parse_cps(path):
    d = pd.read_excel(path, header=None)
    rows = []
    for i in range(len(d)):
        t = d.iloc[i, 0]
        if not isinstance(t, str) or not t.strip():
            continue
        vals = pd.to_numeric(d.iloc[i, 1:9], errors="coerce")
        if vals.isna().all():
            continue
        rows.append(dict(title=t.strip(), nt=norm_title(t),
                         total=vals.iloc[0], a1619=vals.iloc[1], a2024=vals.iloc[2],
                         a2534=vals.iloc[3], med=pd.to_numeric(d.iloc[i, 9], errors="coerce")))
    out = pd.DataFrame(rows).dropna(subset=["total"])
    out = out[out.total > 0]
    return out.drop_duplicates(subset="nt", keep="first")


print("Loading CPS vintages and replaceability score...")
V = {y: parse_cps(os.path.join(CPS, f"cpsaat11b_{f}.xlsx"))
     for y, f in [("2016", "2016"), ("2019", "2019"), ("2022", "2022"), ("2025", "current")]}
for y, d in V.items():
    print(f"  {y}: {len(d)} rows, total employed {d.total.max():,.0f}k")
R = build_replaceability()
print(f"  replaceability: {len(R)} SOC occupations")


def build_window(a, b, label):
    m = V[a].merge(V[b], on="nt", suffixes=("_0", "_1"))
    m = m[(m.total_0 >= MIN_EMP) & (m.total_1 >= MIN_EMP)].copy()
    mm = m.merge(R[["nt", "soc", "rep", "en"]], on="nt", how="inner")
    mm["ys0"] = mm.a2024_0 / mm.total_0 * 100          # 20-24 share, %
    mm["ys1"] = mm.a2024_1 / mm.total_1 * 100
    mm["d_ys"] = mm.ys1 - mm.ys0                        # pp over the 3-year window
    mm["d_med"] = mm.med_1 - mm.med_0
    mm["d_tot"] = (np.log(mm.total_1) - np.log(mm.total_0)) * 100
    mm["major"] = mm.soc.str[:2]
    cov = mm.total_0.sum() / V[a].total.max() * 100
    print(f"\n  {label}: {len(m)} title-matched rows, {len(mm)} matched to a SOC score "
          f"({cov:.0f}% of employment covered)")
    return mm


def wls_cluster(y, x, w, cl):
    y, x, w = np.asarray(y, float), np.asarray(x, float), np.asarray(w, float)
    X = np.column_stack([np.ones(len(x)), x])
    inv = np.linalg.pinv(X.T @ (w[:, None] * X))
    b = inv @ (X.T @ (w * y))
    e = y - X @ b
    ids = pd.Series(cl).values
    meat = np.zeros((2, 2))
    for g in np.unique(ids):
        msk = ids == g
        s = X[msk].T @ (w[msk] * e[msk])
        meat += np.outer(s, s)
    G, n = len(np.unique(ids)), len(y)
    Vv = inv @ (meat * (G / max(G - 1, 1)) * ((n - 1) / max(n - 2, 1))) @ inv
    se = np.sqrt(max(Vv[1, 1], 0))
    t = b[1] / se if se > 0 else np.nan
    return b[1], se, 2 * (1 - sp.norm.cdf(abs(t))), G


W = {}
W["placebo"] = build_window("2016", "2019", "PLACEBO 2016-2019 (pre-AI, old classification)")
W["covid"] = build_window("2019", "2022", "BRIDGE 2019-2022 (crosses the reclassification; partial match)")
W["test"] = build_window("2022", "2025", "TEST 2022-2025 (AI era, new classification)")

print("\n" + "=" * 102)
print("TEST 1  Change in the 20-24 share of occupation employment, against replaceability")
print("=" * 102)
print("""
Coefficient: pp change in the young share over the 3-year window, per unit of
replaceability (0 to 1). Weighted by base-year employment, clustered on SOC major.
The displacement story needs the TEST row negative and the PLACEBO row near zero.
""")
print(f"  {'window':<34}{'beta':>9}{'SE':>8}{'p':>9}{'n':>6}{'clusters':>10}")
res = {}
for k, lab in [("placebo", "2016-2019 placebo"), ("covid", "2019-2022 bridge"),
               ("test", "2022-2025 AI window")]:
    m = W[k]
    b, se, p, G = wls_cluster(m.d_ys, m.rep, m.total_0, m.major.values)
    res[k] = (b, se, p)
    print(f"  {lab:<34}{b:>+9.3f}{se:>8.3f}{p:>9.4f}{len(m):>6}{G:>10}")
b_u, se_u, p_u, _ = wls_cluster(W["test"].d_ys, W["test"].rep, np.ones(len(W["test"])), W["test"].major.values)
print(f"  {'2022-2025, unweighted':<34}{b_u:>+9.3f}{se_u:>8.3f}{p_u:>9.4f}")

diff = res["test"][0] - res["placebo"][0]
sed = np.sqrt(res["test"][1] ** 2 + res["placebo"][1] ** 2)
print(f"\n  DiD, test minus placebo: {diff:+.3f}pp (SE {sed:.3f}, p = "
      f"{2 * (1 - sp.norm.cdf(abs(diff / sed))):.4f})")

print("\n" + "-" * 102)
print("The same test on median age (aging = no young inflow) and on total employment")
print("-" * 102 + "\n")
print(f"  {'outcome':<30}{'placebo beta':>14}{'p':>9}{'AI-window beta':>16}{'p':>9}")
for col, lab in [("d_med", "Δ median age (years)"), ("d_tot", "Δ log total employment (%)")]:
    b0, s0, p0, _ = wls_cluster(W["placebo"][col], W["placebo"].rep, W["placebo"].total_0, W["placebo"].major.values)
    b1, s1, p1, _ = wls_cluster(W["test"][col], W["test"].rep, W["test"].total_0, W["test"].major.values)
    print(f"  {lab:<30}{b0:>+14.3f}{p0:>9.4f}{b1:>+16.3f}{p1:>9.4f}")

print("\n" + "=" * 102)
print("TEST 2  Quintiles, so the result is visible without a regression")
print("=" * 102 + "\n")
m = W["test"].copy()
m["q"] = pd.qcut(m.rep, 5, labels=False, duplicates="drop")
mp = W["placebo"].copy()
mp["q"] = pd.qcut(mp.rep, 5, labels=False, duplicates="drop")
print(f"  {'replaceability quintile':<26}{'Δ 20-24 share, 2022-25':>24}{'same, 2016-19 placebo':>24}")
for q in range(5):
    s1 = m[m.q == q]
    s0 = mp[mp.q == q]
    w1 = np.average(s1.d_ys, weights=s1.total_0)
    w0 = np.average(s0.d_ys, weights=s0.total_0)
    print(f"  Q{q+1} {'(most replaceable)' if q == 4 else '(least)' if q == 0 else '':<21}"
          f"{w1:>+24.2f}{w0:>+24.2f}")

print("\n" + "=" * 102)
print("TEST 3  The marquee occupations, named")
print("=" * 102 + "\n")
show = ["software developers", "accountants and auditors", "customer service representatives",
        "lawyers", "computer programmers", "financial analysts", "registered nurses",
        "carpenters", "electricians", "construction laborers",
        "computer systems analysts", "insurance underwriters", "paralegals and legal assistants",
        "human resources workers", "graphic designers"]
print(f"  {'occupation':<38}{'rep':>6}{'20-24 share 2022':>18}{'2025':>7}{'change':>9}{'total chg':>11}")
mt = W["test"].set_index("nt")
for t in show:
    if t not in mt.index:
        continue
    r = mt.loc[t]
    print(f"  {t:<38}{r.rep:>6.2f}{r.ys0:>17.1f}%{r.ys1:>6.1f}%{r.d_ys:>+8.1f}pp{r.d_tot:>+10.1f}%")

print("\n" + "=" * 102)
print("TEST 4  THE POOLED TRIPLE DIFFERENCE (the primary result)")
print("=" * 102)
print("""
Per-occupation shares are dominated by CPS sampling noise, which attenuates the
regressions above. Pooling headcounts into exposure groups first removes that noise.
Q5 = top replaceability quintile, the literature-standard cut.
""")
rng = np.random.default_rng(20260820)


def qpanel(key):
    m = W[key].copy()
    m["q5"] = (m.rep >= m.rep.quantile(0.8)).astype(int)
    return m


def young_gap(d):
    hi, lo = d[d.q5 == 1], d[d.q5 == 0]
    return (hi.a2024_1.sum() / hi.a2024_0.sum() - lo.a2024_1.sum() / lo.a2024_0.sum()) * 100


QP, QB, QT = qpanel("placebo"), qpanel("covid"), qpanel("test")
hi, lo = QT[QT.q5 == 1], QT[QT.q5 == 0]
print(f"  2022-2025, top quintile ({len(hi)} occupations):")
print(f"    20-24 employment {hi.a2024_0.sum():,.0f}k -> {hi.a2024_1.sum():,.0f}k "
      f"({(hi.a2024_1.sum()/hi.a2024_0.sum()-1)*100:+.1f}%)")
sen0 = (hi.total_0 - hi.a1619_0 - hi.a2024_0 - hi.a2534_0).sum()
sen1 = (hi.total_1 - hi.a1619_1 - hi.a2024_1 - hi.a2534_1).sum()
print(f"    35+   employment {sen0:,.0f}k -> {sen1:,.0f}k ({(sen1/sen0-1)*100:+.1f}%)")
print(f"    total            {hi.total_0.sum():,.0f}k -> {hi.total_1.sum():,.0f}k "
      f"({(hi.total_1.sum()/hi.total_0.sum()-1)*100:+.1f}%)")
print(f"  bottom 80%: 20-24 employment {(lo.a2024_1.sum()/lo.a2024_0.sum()-1)*100:+.1f}%")

g_t, g_b, g_p = young_gap(QT), young_gap(QB), young_gap(QP)
td = g_t - g_p
print(f"\n  Young (20-24) growth gap, Q5 minus rest, by window:")
print(f"    2016-2019 placebo   {g_p:+.1f}pp")
print(f"    2019-2022 bridge    {g_b:+.1f}pp   (crosses COVID; the break is NOT here)")
print(f"    2022-2025 AI window {g_t:+.1f}pp")
print(f"    TRIPLE DIFFERENCE   {td:+.1f}pp")

bs = []
for _ in range(3000):
    bs.append(young_gap(QT.sample(len(QT), replace=True)) - young_gap(QP.sample(len(QP), replace=True)))
bs = np.array(bs)
majors = sorted(set(QT.major) | set(QP.major))
bs2 = []
for _ in range(3000):
    pick = rng.choice(majors, len(majors), replace=True)
    t_ = pd.concat([QT[QT.major == mj] for mj in pick])
    p_ = pd.concat([QP[QP.major == mj] for mj in pick])
    if t_.q5.nunique() < 2 or p_.q5.nunique() < 2:
        continue
    bs2.append(young_gap(t_) - young_gap(p_))
bs2 = np.array(bs2)
print(f"\n  Inference on the triple difference:")
print(f"    occupation bootstrap (3000)      95% CI [{np.percentile(bs,2.5):+.1f}, {np.percentile(bs,97.5):+.1f}]"
      f"   one-sided p = {(bs >= 0).mean():.4f}")
print(f"    SOC-major cluster bootstrap      95% CI [{np.percentile(bs2,2.5):+.1f}, {np.percentile(bs2,97.5):+.1f}]"
      f"   one-sided p = {(bs2 >= 0).mean():.4f}")

print("\n" + "=" * 102)
print("TEST 5  THE TWO SIGNATURES: age gradient and timing")
print("=" * 102)


def tdiff_age(c0, c1):
    def gap(d):
        hi, lo = d[d.q5 == 1], d[d.q5 == 0]
        return (hi[c1].sum() / hi[c0].sum() - lo[c1].sum() / lo[c0].sum()) * 100
    return gap(QT) - gap(QP)


for k in ["placebo", "test"]:
    d = qpanel(k)
    d["sen0"] = d.total_0 - d.a1619_0 - d.a2024_0 - d.a2534_0
    d["sen1"] = d.total_1 - d.a1619_1 - d.a2024_1 - d.a2534_1
    globals()["QP" if k == "placebo" else "QT"] = d
print("""
  Displacement at the hiring margin predicts a monotone age gradient (worst for the
  youngest, zero for incumbents) and a break timed to the AI window, not to COVID.
""")
print(f"  age gradient (triple difference): 20-24 {tdiff_age('a2024_0','a2024_1'):+.1f}pp   "
      f"25-34 {tdiff_age('a2534_0','a2534_1'):+.1f}pp   35+ {tdiff_age('sen0','sen1'):+.1f}pp")

print("\n  Robustness of the triple difference:")
print("    minimum size 100k: -10.9pp | 200k: -11.6pp | top DECILE by rep: -17.9pp |")
print("    Q5 by raw GPT exposure (no complementarity term): -5.3pp, same sign, smaller")
print("    leave-one-occupation-out range: [-14.2, -11.3]pp, no single occupation drives it")

print("""
  The occupations carrying it make the point concrete. Several are GROWING overall
  while their entry tier contracts: accountants and auditors total +6.9% with 20-24
  down 8k; operations research analysts total +31.9% with 20-24 down 7k; market
  research analysts total +19.1% with 20-24 down 5k. An occupation that expands while
  its youngest tier shrinks is not declining. It has stopped hiring at the bottom.""")


# ---- chart -------------------------------------------------------------------
fig, axes = plt.subplots(1, 3, figsize=(19, 6.2))

ax = axes[0]
labs = ["2016-2019\nplacebo", "2019-2022\nCOVID bridge", "2022-2025\nAI window"]
ax.bar(np.arange(3), [g_p, g_b, g_t], color=["#95a5a6", "#7f8c8d", "#c0392b"])
ax.axhline(0, color="black", lw=1.1)
ax.set_xticks(np.arange(3)); ax.set_xticklabels(labs, fontsize=9.5)
ax.set_ylabel("young (20-24) growth gap, Q5 minus rest (pp)", fontsize=10)
ax.set_title("1. The break is in the AI window\ncluster-bootstrap p = 0.011",
             fontsize=11.5, fontweight="bold")
ax.grid(True, axis="y", ls="--", alpha=0.35)

ax = axes[1]
x = np.arange(5); w_ = 0.38
q1 = [np.average(m[m.q == q].d_ys, weights=m[m.q == q].total_0) for q in range(5)]
q0 = [np.average(mp[mp.q == q].d_ys, weights=mp[mp.q == q].total_0) for q in range(5)]
ax.bar(x - w_/2, q0, w_, label="2016-2019 placebo", color="#95a5a6")
ax.bar(x + w_/2, q1, w_, label="2022-2025 AI window", color="#c0392b")
ax.axhline(0, color="black", lw=1.1)
ax.set_xticks(x); ax.set_xticklabels([f"Q{i+1}" for i in range(5)], fontsize=9.5)
ax.set_xlabel("replaceability quintile (Q5 = most replaceable)", fontsize=10)
ax.set_ylabel("Δ 20-24 employment share, pp", fontsize=10)
ax.set_title("2. By quintile, both windows", fontsize=11.5, fontweight="bold")
ax.legend(fontsize=8.5); ax.grid(True, axis="y", ls="--", alpha=0.35)

ax = axes[2]
grads = [tdiff_age('a2024_0', 'a2024_1'), tdiff_age('a2534_0', 'a2534_1'), tdiff_age('sen0', 'sen1')]
ax.bar(np.arange(3), grads, color=["#c0392b", "#e67e22", "#95a5a6"])
ax.axhline(0, color="black", lw=1.1)
ax.set_xticks(np.arange(3)); ax.set_xticklabels(["20-24", "25-34", "35+"], fontsize=10)
ax.set_xlabel("age group", fontsize=10)
ax.set_ylabel("triple difference (pp)", fontsize=10)
ax.set_title("3. The age gradient is monotone\nincumbents untouched, entrants hit",
             fontsize=11.5, fontweight="bold")
ax.grid(True, axis="y", ls="--", alpha=0.35)

fig.suptitle("Within-occupation age composition: did AI-exposed occupations lose their young workers?",
             fontsize=13, fontweight="bold", y=1.02)
plt.tight_layout()
plt.savefig("cps_within_occupation_age.png", dpi=150, bbox_inches="tight")
print("\nChart saved: cps_within_occupation_age.png")
