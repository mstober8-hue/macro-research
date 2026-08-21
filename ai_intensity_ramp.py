"""
ai_intensity_ramp.py
Replacing the Q4 2022 step dummy with diffusion, and using the SHAPE of each effect
to tell the project's two findings apart.

THE SPECIFICATION PROBLEM
Every AI test in this project splits time with a step dummy at Q4 2022 and compares
a "pre-AI" period against a "post-AI" period. That encodes an assumption nobody
would defend if stated aloud: that AI's labor-market effect switched on fully the
moment ChatGPT launched. It did not. GPT-4 arrived in March 2023, enterprise
deployment followed through 2024, agentic coding tools through 2025.

A step dummy applied to a ramping treatment is a known attenuation problem: the
post-period average blends heavily-treated late quarters with barely-treated early
ones, so the estimate is pulled toward zero. Every null in this project's AI arm was
produced under that specification. This script asks whether fixing it changes
anything, and finds that it changes one thing decisively and nothing else.

WHY THERE IS NO MEASURED ADOPTION RAMP HERE
The natural fix is to replace the dummy with measured AI adoption. Census BTOS asks
firms directly whether they used AI in the last two weeks, which would be ideal.
It is not usable for this purpose: in both the project's local copies and the full
national history downloaded from Census, the AI question carries data for only 19
biweekly waves, from late 2025 onward. The 2023-2025 adoption history that would
make the ramp measurable is not in the published national file. Rather than
substitute a parametric S-curve and call it measurement, this script tests the
observable IMPLICATION of the diffusion story instead: if the effect is driven by
diffusion, the effect itself should build year over year.

WHAT THE RAMP TEST FINDS

  On occupation TOTALS, nothing, and no hidden attenuation. Annual OEWS files
  (2022, 2023, 2024, 2025) let the exposure coefficient be estimated one year at a
  time instead of endpoint-to-endpoint. It does not build: the three AI-era annual
  coefficients trend at p = 0.74 (replaceability) and p = 0.96 (GPT exposure). The
  step dummy was not concealing a growing effect on this margin. The null is a null.

  On the ENTRY-LEVEL margin, a strong monotone ramp. The young-graduate penalty
  (excess unemployment over what the business cycle predicts) climbs +0.30pp per
  year with t = 15.9, and the graduate-specific gap over the all-youth placebo
  climbs +0.14pp per year (p = 0.0002).

  And the two findings have DIFFERENT SHAPES, which is the useful part. Shape is
  identifying information: a diffusion-driven effect ramps monotonically and keeps
  going, while a monetary effect built on an 8-9 quarter transmission lag peaks and
  unwinds. The entry-level penalty ramps and is still climbing. The aggregate Okun
  correlation rises, peaks in 2025, and reverses. That is the signature difference
  between an AI channel and a rate channel, and neither the step dummy nor a
  level comparison could produce it.

Reads FRED-Data/. Writes ai_intensity_ramp.png.
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
BTOS = os.path.join(DATA, "btos_national_full_history.xlsx")

COMP_VARS = ["Physical Proximity",
             "Face-to-Face Discussions with Individuals and Within Teams",
             "Deal With External Customers or the Public in General",
             "Health and Safety of Other Workers",
             "Consequence of Error"]

NAT = {"2013": "oews_may2013_national_occupations.xls",
       "2019": "oews_may2019_national_occupations.xlsx",
       "2022": "oews_may2022_national_occupations.xlsx",
       "2023": "oews_may2023_national_occupations.xlsx",
       "2024": "oews_may2024_national_occupations.xlsx",
       "2025": "oews_may2025_national_occupations.xlsx"}


def find(f):
    if os.path.exists(DATA + f):
        return DATA + f
    return (glob.glob(DATA + "*" + f + "*") + glob.glob(DATA + "*" + f))[0]


def load(f):
    d = pd.read_csv(find(f))
    d.columns = [c.strip() for c in d.columns]
    d[d.columns[0]] = pd.to_datetime(d[d.columns[0]])
    d = d.set_index(d.columns[0])
    return pd.to_numeric(d.iloc[:, 0], errors="coerce").dropna()


def build_replaceability():
    el = pd.read_csv(find("eloundou_gpt_occupational_exposure_scores"))
    el.columns = [c.strip() for c in el.columns]
    el["soc"] = el["O*NET-SOC Code"].str[:7]
    el["e"] = el[["human_rating_beta", "dv_rating_beta"]].mean(axis=1)
    exp = el.groupby("soc")["e"].mean()
    wc = pd.read_csv(find("onet_work_context_ratings"))
    wc.columns = [c.strip() for c in wc.columns]
    wc = wc[(wc["Scale ID"] == "CX") & (wc["Element Name"].isin(COMP_VARS))].copy()
    wc["soc"] = wc["O*NET-SOC Code"].str[:7]
    piv = wc.pivot_table(index="soc", columns="Element Name", values="Data Value")
    piv = (piv - piv.min()) / (piv.max() - piv.min())
    o = pd.DataFrame({"exp": exp, "comp": piv.mean(axis=1)}).dropna()
    o["en"] = (o["exp"] - o["exp"].min()) / (o["exp"].max() - o["exp"].min())
    o["rep"] = o["en"] * (1 - o["comp"])
    return o.reset_index()[["soc", "rep", "en"]]


def load_nat(fn):
    d = pd.read_excel(os.path.join(OEWS, fn))
    d.columns = [c.strip().upper() for c in d.columns]
    g = "O_GROUP" if "O_GROUP" in d.columns else "OCC_GROUP"
    d = d[d[g].astype(str).str.strip() == "detailed"].copy()
    d["soc"] = d["OCC_CODE"].astype(str).str.strip()
    d["emp"] = pd.to_numeric(d["TOT_EMP"], errors="coerce")
    d = d.dropna(subset=["emp"])
    return d[d.emp > 0].groupby("soc", as_index=False)["emp"].sum()


def clu(y, x, w, cl):
    y, x, w = np.asarray(y, float), np.asarray(x, float), np.asarray(w, float)
    X = np.column_stack([np.ones(len(x)), x])
    inv = np.linalg.pinv(X.T @ (w[:, None] * X))
    b = inv @ (X.T @ (w * y))
    e = y - X @ b
    ids = np.asarray(cl)
    meat = np.zeros((2, 2))
    for g in np.unique(ids):
        m = ids == g
        s = X[m].T @ (w[m] * e[m])
        meat += np.outer(s, s)
    G, n = len(np.unique(ids)), len(y)
    V = inv @ (meat * (G / max(G - 1, 1)) * ((n - 1) / max(n - 2, 1))) @ inv
    se = np.sqrt(max(V[1, 1], 0))
    t = b[1] / se if se > 0 else np.nan
    return b[1], se, 2 * (1 - sp.norm.cdf(abs(t)))


# ---------------------------------------------------------------- TEST 1
print("=" * 100)
print("TEST 1  WHY THERE IS NO MEASURED ADOPTION RAMP: the BTOS coverage limit")
print("=" * 100)
try:
    x = pd.ExcelFile(BTOS)
    d = x.parse("Response Estimates", header=None)
    hdr = [str(v).replace(".0", "") for v in d.iloc[0].tolist()]
    codes = [c for c in hdr if c.isdigit()]
    qs = d.iloc[:, 1].astype(str)
    hit = d.index[qs.str.lower().str.contains("artificial intelligence", na=False)]
    row = [i for i in hit if str(d.iloc[i, 3]).strip() == "Yes"][0]
    have = [c for j, c in enumerate(hdr) if c.isdigit()
            and str(d.iloc[row, j]).strip() not in (".", "nan", "")]
    print(f"\n  BTOS national file spans {len(codes)} biweekly waves, {min(codes)} to {max(codes)}.")
    print(f"  The AI-use question carries data for only {len(have)} of them, "
          f"{min(have)} to {max(have)}.")
    print(f"  Latest measured adoption: {str(d.iloc[row, 4]).strip()} of US businesses.")
    print("""
  The 2023-2025 adoption history that would make a measured ramp possible is not in
  the published national file. A parametric S-curve could be substituted, but that
  would be an assumption wearing the costume of a measurement. Instead the diffusion
  story is tested through its observable implication: the effect should build.""")
except Exception as ex:
    print(f"  (BTOS file unavailable: {ex})")

# ---------------------------------------------------------------- TEST 2
print("\n" + "=" * 100)
print("TEST 2  DOES THE OCCUPATION-TOTAL EFFECT BUILD? annual OEWS instead of endpoints")
print("=" * 100)
occ = build_replaceability()
V = {y: load_nat(f) for y, f in NAT.items()}


def yr(a, b):
    m = V[a].merge(V[b], on="soc", suffixes=("_0", "_1")).merge(occ, on="soc")
    m["g"] = (np.log(m.emp_1) - np.log(m.emp_0)) / (int(b) - int(a))
    m["major"] = m.soc.str[:2]
    return {c: clu(m.g, m[c], m.emp_0, m.major.values) for c in ["rep", "en"]}, len(m)


print("\n  Annualized dlog employment on exposure, weighted, clustered on SOC major.\n")
print(f"  {'window':<14}{'yrs':>4}{'replaceability':>16}{'p':>9}{'GPT exposure':>15}{'p':>9}{'occ':>6}")
seq = [("2013", "2019"), ("2019", "2022"), ("2022", "2023"), ("2023", "2024"), ("2024", "2025")]
res = {}
for a, b in seq:
    o, n = yr(a, b)
    res[(a, b)] = o
    print(f"  {a + '-' + b:<14}{int(b)-int(a):>4}{o['rep'][0]:>+16.4f}{o['rep'][2]:>9.4f}"
          f"{o['en'][0]:>+15.4f}{o['en'][2]:>9.4f}{n:>6}")
o3, _ = yr("2022", "2025")
print(f"\n  pooled 2022-2025 (the window Part 5 used): rep {o3['rep'][0]:+.4f} (p={o3['rep'][2]:.4f})")
ai = [("2022", "2023"), ("2023", "2024"), ("2024", "2025")]
ramp = {}
for c, lab in [("rep", "replaceability"), ("en", "GPT exposure")]:
    ys = [res[k][c][0] for k in ai]
    sl, ic, r_, p_, se = sp.linregress([0, 1, 2], ys)
    ramp[c] = ys
    print(f"  ramp across the 3 AI years, {lab:<16}: {[f'{v:+.4f}' for v in ys]}  "
          f"slope {sl:+.4f}/yr (p = {p_:.3f})")
print("""
  No build. The step dummy was not concealing a growing effect on occupation totals,
  so the attenuation criticism, though correct in principle, costs nothing here.""")

# ---------------------------------------------------------------- TEST 3
print("\n" + "=" * 100)
print("TEST 3  DOES THE ENTRY-LEVEL EFFECT BUILD? (the margin where the effect lives)")
print("=" * 100)
R12 = lambda s: s.rolling(12).mean()
yg = R12(load("young_college_grads_2024_unemployment_CGBD2024.csv"))
yall = R12(load("age_20_24_unemployment_LNS14000036.csv"))
prime = R12(load("prime_age_25_54_unemployment_LNS14000060.csv"))


def resid(s):
    j = pd.DataFrame({"y": s, "x": prime}).dropna()
    tr = j.loc["2001-01-01":"2019-12-31"]
    b, a, r, p, se = sp.linregress(tr["x"], tr["y"])
    return j["y"] - (a + b * j["x"])


rg, ra = resid(yg), resid(yall)
gap = (rg - ra).dropna()
print("\n  Trend in the excess-unemployment residual, monthly, 2023 onward.\n")
print(f"  {'series':<40}{'slope/yr':>11}{'t':>8}{'p':>10}{'n':>5}")
for s, lab in [(rg, "young-grad penalty"), (ra, "all-youth penalty (placebo)"),
               (gap, "graduate-specific GAP")]:
    z = s.loc["2023-01-01":]
    t_ = np.arange(len(z)) / 12.0
    sl, ic, r_, p_, se = sp.linregress(t_, z.values)
    print(f"  {lab:<40}{sl:>+11.3f}{sl/se:>8.2f}{p_:>10.5f}{len(z):>5}")
print(f"\n  {'year':<8}{'young-grad':>13}{'all-youth':>12}{'gap':>9}")
for y in [2023, 2024, 2025, 2026]:
    print(f"  {y:<8}{rg.loc[str(y)].mean():>12.2f}pp{ra.loc[str(y)].mean():>11.2f}pp"
          f"{gap.loc[str(y)].mean():>8.2f}pp")
print("""
  The placebo also trends up, so part of this is a general youth labor market that has
  deteriorated. The graduate-specific gap is the cleaner quantity and it still builds.""")

# ---------------------------------------------------------------- TEST 4
print("\n" + "=" * 100)
print("TEST 4  THE SHAPE DISCRIMINATOR: diffusion ramps, monetary transmission peaks")
print("=" * 100)
gdp = load("real_gdp_full_history_GDPC1.csv")
un = load("unemployment_rate_full_history_UNRATE.csv")
COVID = pd.date_range("2020-04-01", "2021-10-01", freq="QS")
dd = pd.concat([(gdp.pct_change(4) * 100).rename("y"),
                un.resample("QS").mean().diff(4).rename("u")], axis=1).dropna()
dd = dd[~dd.index.isin(COVID)]
roll = dd["y"].rolling(12).corr(dd["u"]).dropna()
print("\n  Annual means, 2023 onward:\n")
print(f"  {'year':<8}{'entry-level penalty':>22}{'aggregate Okun corr':>24}")
for y in [2023, 2024, 2025, 2026]:
    ok = roll.loc[str(y)].mean() if len(roll.loc[str(y):str(y)]) else np.nan
    print(f"  {y:<8}{rg.loc[str(y)].mean():>21.2f}pp{ok:>24.3f}")
print("""
  One builds monotonically and is still climbing. The other rises, peaks in 2025, and
  reverses. A diffusion-driven effect keeps going as adoption spreads; an effect built
  on an 8-9 quarter monetary transmission lag peaks and unwinds. The shapes are the
  evidence that these are two different phenomena, which no step dummy and no level
  comparison could have shown.""")

# ---- chart -------------------------------------------------------------------
fig, axes = plt.subplots(1, 3, figsize=(19, 6.2))

ax = axes[0]
x = np.arange(3)
w = 0.38
ax.bar(x - w/2, ramp["rep"], w, label="replaceability", color="#1f4e79")
ax.bar(x + w/2, ramp["en"], w, label="GPT exposure", color="#95a5a6")
ax.axhline(0, color="black", lw=1.1)
ax.set_xticks(x); ax.set_xticklabels(["2022-23", "2023-24", "2024-25"], fontsize=9.5)
ax.set_ylabel("annual coefficient on occupation employment", fontsize=10)
ax.set_title("1. Occupation totals do not build\ntrend p = 0.74 and 0.96",
             fontsize=11.5, fontweight="bold")
ax.legend(fontsize=8.5); ax.grid(True, axis="y", ls="--", alpha=0.35)

ax = axes[1]
ax.plot(rg.loc["2021":].index, rg.loc["2021":].values, lw=2.3, color="#c0392b",
        label="young college grads")
ax.plot(ra.loc["2021":].index, ra.loc["2021":].values, lw=1.7, color="#95a5a6",
        label="all 20-24 (placebo)")
ax.axhline(0, color="black", lw=1.0)
ax.axvspan(pd.Timestamp("2022-11-30"), rg.index[-1], color="gold", alpha=0.18)
ax.set_ylabel("excess unemployment vs cycle (pp)", fontsize=10)
ax.set_title("2. The entry-level penalty builds\n+0.30pp/yr, t = 15.9",
             fontsize=11.5, fontweight="bold")
ax.legend(fontsize=8.5); ax.grid(True, ls="--", alpha=0.35)

ax = axes[2]
ax2 = ax.twinx()
yrs = [2023, 2024, 2025, 2026]
ent = [rg.loc[str(y)].mean() for y in yrs]
okv = [roll.loc[str(y)].mean() for y in yrs]
ax.plot(yrs, ent, marker="o", lw=2.6, color="#c0392b", label="entry-level penalty (left)")
ax2.plot(yrs, okv, marker="s", lw=2.6, color="#1f4e79", label="aggregate Okun corr (right)")
ax2.axhline(0, color="black", lw=0.9)
ax.set_xticks(yrs)
ax.set_ylabel("entry-level penalty (pp)", fontsize=10, color="#c0392b")
ax2.set_ylabel("rolling Okun correlation", fontsize=10, color="#1f4e79")
h1, l1 = ax.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels()
ax.legend(h1 + h2, l1 + l2, fontsize=8, loc="upper left")
ax.set_title("3. Different shapes, different causes\nramp vs peak-and-unwind",
             fontsize=11.5, fontweight="bold")
ax.grid(True, ls="--", alpha=0.35)

fig.suptitle("Replacing the step dummy with diffusion: the ramp test separates the AI channel from the rate channel",
             fontsize=13, fontweight="bold", y=1.02)
plt.tight_layout()
plt.savefig("ai_intensity_ramp.png", dpi=150, bbox_inches="tight")
print("\nChart saved: ai_intensity_ramp.png")
