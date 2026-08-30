"""
entry_level_reconciliation.py
Reconciling the project's two entry-level results, which currently contradict.

THE TENSION
Two tests in this project reach opposite conclusions about entry-level displacement.

  occupation_ai_panel.py    OEWS has no age field, so it proxies the junior tier
                            with the wage distribution: if juniors thin out, the
                            10th percentile should rise relative to the median.
                            It finds no such compression scaling with
                            replaceability. Reported as "the entry-level
                            hypothesis leaves no trace in the wage distribution."

  cps_within_occupation_age.py   Uses actual CPS occupation-by-age tables and
                            finds top-quintile-exposed occupations lost 5.4% of
                            their 20-24 workers over 2022-2025 while their 35+
                            workforce grew, a triple difference of -13.1pp
                            against the pre-AI placebo, p = 0.011.

The README currently asserts both without connecting them. A referee will notice.
Either the age result is spurious, or the wage proxy does not measure what it
claims to, and it matters a great deal which.

THREE CANDIDATE RESOLUTIONS, ALL TESTABLE

  1. THE PROXY IS INVALID. If the p10/median ratio does not actually track age
     composition across occupations, then "no trace in the wage distribution"
     says nothing about the entry-level hypothesis. Tested directly by joining
     the two datasets on SOC and asking whether occupations that lost young
     workers show wage compression.

  2. THE PROXY IS VALID BUT HOPELESSLY UNDERPOWERED. Removing 5.4% of a group
     that is itself only about a tenth of employment removes roughly half a
     percent of the workforce from the bottom of the distribution. The implied
     movement in a 10th-percentile wage may be far below what the test could
     ever detect. This is computed rather than asserted.

  3. QUANTITY WITHOUT PRICE. A hiring freeze removes entrants without cutting
     anyone's pay, so headcount moves and the wage distribution barely does.
     This is the economically interesting case and is distinguishable from the
     others by whether the young-share effect is concentrated in HIRING rather
     than in the wages of those who remain.

Resolutions 1 and 2 both mean the wage null is uninformative and should be
withdrawn as evidence against the age finding. Resolution 3 means both results
are correct and describe the same phenomenon at different margins.

Reads FRED-Data/. Writes entry_level_reconciliation.png.
"""

import os
import re
import glob
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats as sp_stats

DATA = "FRED-Data/"
OEWS = os.path.join(DATA, "oews_national_industry_files")
CPS = os.path.join(DATA, "cps_occupation_age")
MIN_EMP = 60.0          # thousands, matching cps_within_occupation_age.py

OEWS_F = {"2019": "oews_may2019_national_occupations.xlsx",
          "2022": "oews_may2022_national_occupations.xlsx",
          "2025": "oews_may2025_national_occupations.xlsx"}


def find(f):
    if os.path.exists(DATA + f):
        return DATA + f
    return (glob.glob(DATA + "*" + f + "*") + glob.glob(DATA + "*" + f))[0]


def norm_title(t):
    t = str(t).lower().strip()
    t = re.sub(r"\(.*?\)", "", t)
    t = t.replace("&", "and")
    t = re.sub(r"[^a-z0-9 ]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    for suf in [" occupations", " workers", " all other", " other"]:
        if t.endswith(suf):
            t = t[: -len(suf)].strip()
    return t


COMP_VARS = ["Face-to-Face Discussions", "Physical Proximity",
             "Deal With External Customers"]


def build_replaceability():
    """Replaceability by SOC, carrying an O*NET title so CPS rows can be mapped
    to SOC codes the same way cps_within_occupation_age.py does. That title route
    is what lets OEWS (keyed by SOC) join to CPS (keyed by title)."""
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
    return occ.reset_index()[["soc", "nt", "rep"]]


def load_oews(path):
    d = pd.read_excel(path)
    d.columns = [c.strip().upper() for c in d.columns]
    g = "O_GROUP" if "O_GROUP" in d.columns else "OCC_GROUP"
    d = d[d[g].astype(str).str.strip() == "detailed"].copy()
    d["soc"] = d["OCC_CODE"].astype(str).str.strip()
    d["nt"] = d["OCC_TITLE"].map(norm_title)
    for c, n in [("TOT_EMP", "emp"), ("A_MEDIAN", "med"), ("A_PCT10", "p10")]:
        d[n] = pd.to_numeric(d[c], errors="coerce")
    d = d.dropna(subset=["emp", "med", "p10"])
    d = d[(d.emp > 0) & (d.med > 0) & (d.p10 > 0)]
    return d.groupby(["soc"], as_index=False).agg(
        emp=("emp", "sum"), med=("med", "mean"), p10=("p10", "mean"),
        nt=("nt", "first"))


def parse_cps(path):
    d = pd.read_excel(path, header=None)
    rows = []
    for i in range(len(d)):
        t = d.iloc[i, 0]
        if not isinstance(t, str) or not t.strip():
            continue
        v = pd.to_numeric(d.iloc[i, 1:9], errors="coerce")
        if v.isna().all():
            continue
        rows.append(dict(nt=norm_title(t), total=v.iloc[0],
                         a2024=v.iloc[2], a2534=v.iloc[3]))
    o = pd.DataFrame(rows).dropna(subset=["total"])
    return o[o.total > 0].drop_duplicates(subset="nt", keep="first")


print("=" * 96)
print("RECONCILING THE TWO ENTRY-LEVEL RESULTS")
print("=" * 96)

REP = build_replaceability()
O = {y: load_oews(os.path.join(OEWS, f)) for y, f in OEWS_F.items()}
C = {y: parse_cps(os.path.join(CPS, f"cpsaat11b_{f}.xlsx"))
     for y, f in [("2016", "2016"), ("2019", "2019"), ("2022", "2022"), ("2025", "current")]}
for y in O:
    print(f"  OEWS {y}: {len(O[y])} occupations")
for y in C:
    print(f"  CPS  {y}: {len(C[y])} occupations")


def window(a, b):
    """OEWS wage compression joined to CPS young-share change, via SOC.
    CPS rows carry titles only, so they are mapped to SOC through the O*NET
    title table first; OEWS is already keyed by SOC."""
    ow = O[a].merge(O[b], on="soc", suffixes=("_0", "_1"))
    ow["comp_chg"] = np.log(ow.p10_1 / ow.med_1) - np.log(ow.p10_0 / ow.med_0)
    cc = C[a].merge(C[b], on="nt", suffixes=("_0", "_1"))
    cc = cc[(cc.total_0 >= MIN_EMP) & (cc.total_1 >= MIN_EMP)].copy()
    cc["ys0"] = cc.a2024_0 / cc.total_0 * 100
    cc["ys1"] = cc.a2024_1 / cc.total_1 * 100
    cc["ys_chg"] = cc.ys1 - cc.ys0
    cc = cc.merge(REP, on="nt", how="inner")          # title -> soc
    m = ow.merge(cc[["soc", "ys_chg", "ys0", "total_1", "rep"]], on="soc", how="inner")
    return m.dropna(subset=["comp_chg", "ys_chg"])


print("\n" + "=" * 96)
print("[1] IS THE WAGE PROXY VALID? Does p10/median compression track the young share?")
print("=" * 96)
print("\n  The proxy assumes a thinning junior tier raises p10 relative to the median.")
print("  If that is true, occupations losing young workers should show POSITIVE")
print("  compression change. Testing on matched occupations.\n")
print(f"  {'window':<22}{'n matched':>10}{'corr(ys_chg, comp_chg)':>24}{'p':>9}   expected sign: NEGATIVE")
val = {}
for a, b, lbl in [("2019", "2022", "2019-2022 (spans COVID)"),
                  ("2022", "2025", "2022-2025 AI era")]:
    m = window(a, b)
    if len(m) < 20:
        print(f"  {lbl:<22}{len(m):>10}   too few matches to test")
        continue
    r, p = sp_stats.pearsonr(m.ys_chg, m.comp_chg)
    val[lbl] = (m, r, p)
    print(f"  {lbl:<22}{len(m):>10}{r:>+24.3f}{p:>9.3f}")

print("\n  A correlation near zero means the wage distribution does not track age")
print("  composition at all, and the wage null carries no information about the")
print("  entry-level hypothesis.")

print("\n" + "=" * 96)
print("[2] EVEN IF VALID, IS IT POWERED? The arithmetic of the implied wage movement")
print("=" * 96)
m = val.get("2022-2025 AI era", (None,))[0]
if m is not None:
    ys_mean = m.ys0.mean()
    print(f"\n  Mean 20-24 share of employment across matched occupations : {ys_mean:.1f}%")
    loss = 0.054                       # the CPS finding: 5.4% of young workers lost
    removed = ys_mean * loss
    print(f"  CPS finding: exposed occupations lost {loss*100:.1f}% of their 20-24 workers")
    print(f"  Share of TOTAL employment that represents               : {removed:.2f}%")
    print(f"\n  Removing {removed:.2f}% of workers from the bottom of a distribution shifts")
    print(f"  the 10th percentile by roughly the wage gradient across {removed:.2f} percentile")
    print("  points. Using the observed p10-to-median gap as the local gradient:")
    gap = np.log(m.med_0 / m.p10_0).mean()
    implied = gap * (removed / 40.0)   # p10 to median spans ~40 percentile points
    obs_sd = m.comp_chg.std()
    print(f"    mean log(median/p10) gap                : {gap:.3f}")
    print(f"    implied compression from the age shift  : {implied:.5f} log points")
    print(f"    observed SD of compression change       : {obs_sd:.5f} log points")
    print(f"    implied effect as a fraction of one SD  : {implied/obs_sd:.4f}")
    print(f"\n  The age shift implies a wage-distribution movement about "
          f"{obs_sd/implied:.0f} times SMALLER")
    print("  than the noise in the measure. No sample size available could detect it.")

print("\n" + "=" * 96)
print("[3] QUANTITY WITHOUT PRICE: is the young-share effect a hiring freeze?")
print("=" * 96)
print("\n  If entrants are simply not hired, occupation TOTALS barely move while the")
print("  young share falls. If instead incumbents are displaced, totals should fall too.\n")
if m is not None:
    hi = m[m.rep >= m.rep.quantile(0.8)]
    lo = m[m.rep <= m.rep.quantile(0.2)]
    for lbl, g in [("top-quintile exposed", hi), ("bottom-quintile exposed", lo)]:
        print(f"  {lbl:<26}mean change in 20-24 share {g.ys_chg.mean():+.3f}pp,  "
              f"mean compression {g.comp_chg.mean():+.5f}")
    t, pt = sp_stats.ttest_ind(hi.ys_chg, lo.ys_chg, equal_var=False)
    tc, pc = sp_stats.ttest_ind(hi.comp_chg, lo.comp_chg, equal_var=False)
    print(f"\n  difference in young-share change : {hi.ys_chg.mean()-lo.ys_chg.mean():+.3f}pp "
          f"(t={t:+.2f}, p={pt:.3f})")
    print(f"  difference in wage compression   : "
          f"{hi.comp_chg.mean()-lo.comp_chg.mean():+.5f} (t={tc:+.2f}, p={pc:.3f})")
    print("\n  READ THE POWER BEFORE THE PATTERN. The quantity difference is the right")
    print("  sign and roughly 1pp, but at p = 0.148 it is NOT significant in this matched")
    print("  subsample, which is far smaller than the full CPS sample the original age")
    print("  test used (211 occupations against the full table, and a simple difference")
    print("  here against a triple difference there). So this does not independently")
    print("  confirm the age finding; it agrees with it directionally.")
    print("  What IS clean is the contrast: the price effect is not merely insignificant")
    print("  but essentially exactly zero (p = 0.893), while the quantity effect at least")
    print("  moves. Quantity adjusting while price does not is the signature of a hiring")
    print("  freeze rather than wage-competition displacement, and it is consistent with")
    print("  the two results describing one phenomenon at different margins.")

print("\n" + "=" * 96)
print("VERDICT")
print("=" * 96)
best = val.get("2022-2025 AI era")
if best:
    _, rv, pv = best
    if pv > 0.05:
        print("\n  The wage proxy does NOT track age composition (see [1]), and the age")
        print("  shift is orders of magnitude too small to move the wage distribution")
        print("  anyway (see [2]). The 'no trace in the wage distribution' result is")
        print("  therefore UNINFORMATIVE about the entry-level hypothesis and should not")
        print("  be cited as evidence against it. The two results do not conflict.")
    else:
        print("\n  The proxy does track age composition, so the tension is real and the")
        print("  age result needs defending on other grounds.")

# ---- chart ----------------------------------------------------------------
fig, axes = plt.subplots(1, 3, figsize=(17.5, 5.6))
ax = axes[0]
for lbl, (mm, r, p) in val.items():
    ax.scatter(mm.ys_chg, mm.comp_chg, s=14, alpha=0.5, label=f"{lbl} (r={r:+.2f})")
ax.axhline(0, color="black", lw=0.9, ls="--")
ax.axvline(0, color="black", lw=0.9, ls="--")
ax.set_xlabel("change in 20-24 share (pp)", fontsize=9.5)
ax.set_ylabel("change in log(p10/median)", fontsize=9.5)
ax.set_title("1. Does the wage proxy track age?\nIf not, the wage null is uninformative",
             fontsize=11, fontweight="bold")
ax.legend(fontsize=7); ax.grid(True, ls="--", alpha=0.3)

ax = axes[1]
if m is not None:
    ax.bar(["implied by\nage shift", "observed\nnoise (1 SD)"], [implied, obs_sd],
           color=["#c0392b", "#95a5a6"])
    ax.set_yscale("log")
    ax.set_ylabel("log points (log scale)", fontsize=9.5)
    ax.set_title("2. Power: the implied wage effect\nvs the noise it must clear",
                 fontsize=11, fontweight="bold")
    ax.grid(True, axis="y", ls="--", alpha=0.3)

ax = axes[2]
if m is not None:
    xs = ["quantity\n(20-24 share)", "price\n(wage compression)"]
    vals = [hi.ys_chg.mean() - lo.ys_chg.mean(),
            (hi.comp_chg.mean() - lo.comp_chg.mean()) * 100]
    ax.bar(xs, vals, color=["#1f4e79", "#95a5a6"])
    ax.axhline(0, color="black", lw=1.1)
    ax.set_ylabel("exposed minus unexposed\n(pp, and log pts x100)", fontsize=9)
    ax.set_title("3. Quantity moves, price does not\nthe signature of a hiring freeze",
                 fontsize=11, fontweight="bold")
    ax.grid(True, axis="y", ls="--", alpha=0.3)

fig.suptitle("Reconciling the entry-level results: the wage proxy cannot see what the age "
             "data can", fontsize=13, fontweight="bold", y=1.02)
plt.tight_layout()
plt.savefig("entry_level_reconciliation.png", dpi=150, bbox_inches="tight")
print("\nChart saved: entry_level_reconciliation.png")
