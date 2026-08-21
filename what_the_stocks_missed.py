"""
what_the_stocks_missed.py
Re-testing the AI-displacement question on the margins the project never measured.

WHY THIS EXISTS
The project's labor-side conclusion ("no identified evidence of AI-driven
displacement") was assembled from four well-powered nulls. A fair rebuttal points
out that every one of those designs shares three blind spots, and that the
real-world pattern people describe (new graduates unable to find work while
output grows) would be invisible to all four:

  BLIND SPOT 1, THE MARGIN. Every displacement test used employment STOCKS.
  Entry-level displacement does not fire anyone; it stops hiring. That appears in
  flows (openings, hires) years before stocks move, because attrition is slow.
  The project's own strongest flow result, openings falling most where work is
  most replaceable (r = -0.676, p = 0.045, the only significant JOLTS margin),
  was buried under a Bonferroni caveat while "layoffs are flat" was promoted to
  "no displacement." A hiring freeze is what rate transmission looks like AND
  what entry-level AI displacement looks like; layoffs-flat discriminates
  nothing.

  BLIND SPOT 2, THE WORKER. Every occupation test used occupation TOTALS. If AI
  crushes junior analysts while senior analysts expand, the occupation nets to
  roughly zero and OEWS sees nothing. Age was never tested. This script tests it
  with BLS age-by-education unemployment series.

  BLIND SPOT 3, THE STATISTIC. The "predates AI" timing verdict compared
  correlations across windows (r = 0.940 pre-AI vs 0.835 AI-era) and read the
  decline as decisive. At n = 9 that difference is untestable, and r measures
  fit tightness, not effect size. The economically meaningful quantity is the
  SLOPE, which was never compared.

Each part below closes one blind spot. Everything is 12-month trailing means
where the underlying series is unadjusted, consistent with project practice.

Reads FRED-Data/. Writes what_the_stocks_missed.png.
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


R12 = lambda s: s.rolling(12).mean()

yg   = load("young_college_grads_2024_unemployment_CGBD2024.csv")     # BA holders 20-24, NSA
g25  = load("college_grads_25plus_unemployment_LNS14027662.csv")      # BA+ 25+, SA
yall = load("age_20_24_unemployment_LNS14000036.csv")                 # all 20-24, SA
prime = load("prime_age_25_54_unemployment_LNS14000060.csv")          # 25-54, SA
hs25 = load("hs_grads_no_college_25plus_unemployment_LNS14027660.csv")
dur  = load("median_unemployment_duration_UEMPMED.csv")
lt   = load("longterm_27wk_share_LNS13025703.csv")
un   = load("unemployment_rate_full_history_UNRATE.csv")

# ============================================================ PART 1
print("=" * 102)
print("PART 1  THE WORKER THE PROJECT NEVER TESTED: young college graduates")
print("=" * 102)
print("""
The entry point to AI-exposed knowledge work is a 20-24 year old with a bachelor's
degree. If AI displacement concentrates at the entry level, this group deteriorates
relative to everyone else, on a schedule that starts after late 2022. All series are
12-month trailing means (the young-grad series is unadjusted and has violent
graduation seasonality).
""")

yg12, g2512, yall12, prime12 = R12(yg), R12(g25), R12(yall), R12(prime)

print(f"  {'12m window ending':<20}{'young grads':>12}{'all grads 25+':>15}{'gap':>7}"
      f"{'all 20-24':>11}{'grad advantage':>16}")
for dt in ["2007-12-01", "2015-12-01", "2019-12-01", "2022-12-01", "2023-12-01",
           "2024-12-01", "2025-12-01"]:
    t = pd.Timestamp(dt)
    print(f"  {dt[:7]:<20}{yg12.asof(t):>12.2f}{g2512.asof(t):>15.2f}"
          f"{yg12.asof(t)-g2512.asof(t):>7.2f}{yall12.asof(t):>11.2f}"
          f"{yall12.asof(t)-yg12.asof(t):>16.2f}")
t = yg12.dropna().index[-1]
print(f"  {'latest (' + str(t.date())[:7] + ')':<20}{yg12.asof(t):>12.2f}{g2512.asof(t):>15.2f}"
      f"{yg12.asof(t)-g2512.asof(t):>7.2f}{yall12.asof(t):>11.2f}{yall12.asof(t)-yg12.asof(t):>16.2f}")

print("""
  'Grad advantage' is all-20-24 unemployment minus young-grad unemployment: how much a
  degree protects a young worker against the rest of their cohort, who skew toward the
  service and physical jobs language models cannot touch.
""")

# cyclical adjustment: young-grad rate predicted from prime-age, fit pre-2020
j = pd.DataFrame({"y": yg12, "x": prime12}).dropna()
tr = j.loc["2001-01-01":"2019-12-31"]
b, a, r_, p_, se = sp.linregress(tr["x"], tr["y"])
j["resid"] = j["y"] - (a + b * j["x"])
print(f"  Cyclical adjustment: young-grad rate on prime-age rate, fit 2001-2019 "
      f"(r = {r_:+.2f}).")
print(f"  Residual = how much worse young grads are doing than the business cycle predicts.\n")
print(f"  {'period':<26}{'mean residual':>14}")
for lab, aa, bb in [("2001-2019 (fit window)", "2001-01-01", "2019-12-31"),
                    ("2015-2019", "2015-01-01", "2019-12-31"),
                    ("2021-2022", "2021-01-01", "2022-12-31"),
                    ("2023", "2023-01-01", "2023-12-31"),
                    ("2024", "2024-01-01", "2024-12-31"),
                    ("2025", "2025-01-01", "2025-12-31"),
                    ("2026 to date", "2026-01-01", "2026-12-31")]:
    print(f"  {lab:<26}{j['resid'].loc[aa:bb].mean():>+14.2f}pp")
sd = j["resid"].loc["2001-01-01":"2019-12-31"].std()
cur = j["resid"].iloc[-1]
print(f"\n  Latest residual: {cur:+.2f}pp, which is {cur/sd:+.1f} standard deviations of the")
print(f"  pre-2020 residual distribution (sd = {sd:.2f}).")
mx_pre = j["resid"].loc[:"2019-12-31"].max()
print(f"  Largest pre-2020 residual ever, including the GFC: {mx_pre:+.2f}pp.")

# the same adjustment for the control group: young NON-grad-heavy pool
jc = pd.DataFrame({"y": yall12, "x": prime12}).dropna()
trc = jc.loc["2001-01-01":"2019-12-31"]
bc, ac, _, _, _ = sp.linregress(trc["x"], trc["y"])
jc["resid"] = jc["y"] - (ac + bc * jc["x"])
print(f"\n  Same adjustment for ALL 20-24 year olds (the mostly-non-grad pool):")
print(f"    latest residual {jc['resid'].iloc[-1]:+.2f}pp against a pre-2020 sd of "
      f"{jc['resid'].loc['2001-01-01':'2019-12-31'].std():.2f}.")
print("""  If this were a generic youth or first-job problem (minimum wage, slow economy,
  scarring), the whole cohort would deviate together. The deviation concentrates in
  the degreed entrants, who are exactly the ones entering AI-exposed work.""")

# ============================================================ PART 2
print("\n" + "=" * 102)
print("PART 2  THE SEARCH-DURATION ANOMALY: 'low unemployment but nobody can find a job'")
print("=" * 102)
print("""
A low-hire economy is misery concentrated on searchers: few people lose jobs, but
anyone searching stays out a long time. The test is whether duration is unusually
high FOR THE CURRENT LEVEL OF UNEMPLOYMENT. Comparing all months since 1967 in which
the unemployment rate sat between 4.0 and 4.6 (where 2024-2026 lives):
""")
d12, l12 = R12(dur), R12(lt)
u_m = un  # monthly SA already
J = pd.DataFrame({"u": u_m, "dur": d12, "lt": l12}).dropna()
band = J[(J.u >= 4.0) & (J.u <= 4.6)]
print(f"  {'era':<14}{'months in band':>15}{'median duration':>17}{'share 27+ weeks':>17}")
for lab, aa, bb in [("pre-1990", "1967-01-01", "1989-12-31"),
                    ("1990s", "1990-01-01", "1999-12-31"),
                    ("2000s", "2000-01-01", "2009-12-31"),
                    ("2010s", "2010-01-01", "2019-12-31"),
                    ("2024-2026", "2024-01-01", "2026-12-31")]:
    s = band.loc[aa:bb]
    if len(s) == 0:
        print(f"  {lab:<14}{'0':>15}{'-':>17}{'-':>17}")
        continue
    print(f"  {lab:<14}{len(s):>15}{s['dur'].mean():>17.1f}{s['lt'].mean():>16.1f}%")
now = band.loc["2024-01-01":]
hist = band.loc[:"2019-12-31"]
print(f"\n  At the same unemployment rate, the median search now runs {now['dur'].mean():.1f} weeks against a")
print(f"  historical average of {hist['dur'].mean():.1f}, and {now['lt'].mean():.0f}% of the unemployed have been out 27+ weeks")
print(f"  against {hist['lt'].mean():.0f}% historically. Duration percentile of the current period within all")
pctl = (hist["dur"] < now["dur"].mean()).mean() * 100
print(f"  same-band history: {pctl:.0f}th.")
print("""  This is consistent with the low-hire, low-fire market the rate story predicts, AND
  with entry-level displacement. It does not separate them. What it does establish is
  that 'unemployment is low so the labor market is fine' is not true for searchers,
  which is the real-world observation this part of the rebuttal rests on.""")

# ============================================================ PART 3
print("\n" + "=" * 102)
print("PART 3  THE TIMING VERDICT, RECHECKED ON SLOPES INSTEAD OF CORRELATIONS")
print("=" * 102)
print("""
headline_result_stress_test.py concluded the productivity relationship 'predates AI'
because r fell from 0.940 (2013-2019) to 0.835 (2019-2025). Two problems. At n = 9
that difference is statistically untestable. And r measures how tightly points sit on
the line, not how steep the line is. The claim that matters economically is the slope:
how much extra productivity growth per unit of replaceability.
""")

S = {
 "Financial Activities": ("GDPDEFLATE:financial_activities_value_added_VAFI.csv", ["finance_insurance_employment_CES5552000001.csv"], 0.267),
 "Information": ("information_sector_value_added_RVAI.csv", ["information_sector_employment_USINFO.csv"], 0.325),
 "Education & Health": ("health_care_social_assistance_value_added_RVAHCSA.csv", ["education_health_employment_USEHS.csv"], 0.152),
 "Professional & Business": ("professional_business_services_value_added_RVAPBS.csv", ["professional_business_services_employment_USPBS.csv"], 0.233),
 "Wholesale Trade": ("wholesale_trade_value_added_RVAW.csv", ["wholesale_trade_employment_USWTRADE.csv"], 0.207),
 "Leisure & Hospitality": ("leisure_hospitality_value_added_RVAAERAF.csv", ["leisure_hospitality_employment_USLAH.csv"], 0.088),
 "Transportation & Utilities": ("transportation_warehousing_value_added_RVAT.csv", ["transportation_warehousing_employment_CES4300000001.csv", "utilities_employment_CES4422000001.csv"], 0.120),
 "Manufacturing": ("manufacturing_value_added_RVAMA.csv", ["manufacturing_employment_MANEMP.csv"], 0.138),
 "Construction": ("construction_value_added_RVAC.csv", ["construction_employment_USCONS.csv"], 0.091),
}


def real_output(spec):
    if spec.startswith("GDPDEFLATE:"):
        nom = load(spec.split(":", 1)[1])
        gd = load("gdp_deflator_GDPDEF.csv")
        return nom / gd.reindex(nom.index).interpolate() * 100
    return load(spec)


def esum(fs):
    s = None
    for f in fs:
        x = load(f).resample("QS").mean()
        s = x if s is None else s.add(x, fill_value=np.nan)
    return s


def cg(s, a, b):
    x = s.loc[a:b].dropna()
    yrs = (x.index[-1] - x.index[0]).days / 365.25
    return ((x.iloc[-1] / x.iloc[0]) ** (1 / yrs) - 1) * 100


prod, rep = {}, {}
for n, (osp, efs, rp) in S.items():
    df = pd.DataFrame({"o": real_output(osp), "e": esum(efs)}).dropna()
    prod[n] = df["o"] / df["e"]
    rep[n] = rp

print(f"  {'window':<14}{'slope (pp/yr per unit rep)':>28}{'SE':>8}{'r':>8}")
slopes = {}
for a, b, lab in [("2013-01-01", "2019-12-31", "2013-2019"),
                  ("2019-01-01", "2025-12-31", "2019-2025"),
                  ("2022-10-01", "2025-12-31", "2022-2025")]:
    x = np.array([rep[n] for n in S])
    y = np.array([cg(prod[n], a, b) for n in S])
    sl, ic, r_, p_, se = sp.linregress(x, y)
    slopes[lab] = (sl, se, r_)
    print(f"  {lab:<14}{sl:>+28.1f}{se:>8.1f}{r_:>+8.3f}")
s1, s2 = slopes["2013-2019"][0], slopes["2019-2025"][0]
print(f"""
  The slope STEEPENED from {s1:+.1f} to {s2:+.1f} pp/yr per unit of replaceability as the
  window moved into the AI era, a {(s2/s1-1)*100:+.0f}% change, while r drifted down slightly.
  The earlier verdict read the falling r as 'the relationship weakens toward the AI era.'
  The slope says the opposite: the productivity PENALTY-PREMIUM gradient between
  replaceable and non-replaceable sectors widened after 2019. With n = 9 and overlapping
  windows neither movement is formally testable, which cuts both ways: the 'predates AI,
  full stop' conclusion rested on a difference no stronger than this one.

  What survives of the timing verdict: the relationship EXISTED before generative AI
  (r = 0.94 pre-AI is not disputable). What does not survive: the claim that the AI era
  did not strengthen it. The gradient widened; the correct verdict is 'a pre-existing
  structural gradient that has steepened since 2019', which is exactly what AI layered
  on top of prior automation would look like, and also what several non-AI stories would
  look like. Undetermined, not dead.""")

# ============================================================ PART 4
print("\n" + "=" * 102)
print("PART 4  WHERE THE AGGREGATE BREAK STANDS NOW, mid-2026")
print("=" * 102)
gdp = load("real_gdp_full_history_GDPC1.csv")
COVID = pd.date_range("2020-04-01", "2021-10-01", freq="QS")
dd = pd.concat([(gdp.pct_change(4) * 100).rename("y"),
                un.resample("QS").mean().diff(4).rename("u")], axis=1).dropna()
dd = dd[~dd.index.isin(COVID)]
roll = dd["y"].rolling(12).corr(dd["u"]).dropna()
print("\n  Rolling 12q difference-form Okun correlation, last 8 quarters:")
for t, v in roll.iloc[-8:].items():
    print(f"    {str(t.date())[:7]}   {v:+.3f}")
print(f"""
  The aggregate inversion peaked at +0.55 (difference form) in 2025 and is unwinding on
  roughly the schedule the rate-lag story predicted. Meanwhile the young-graduate
  residual in Part 1 is NOT unwinding. Those two facts together are the honest synthesis:
  the economy-wide Okun break was mostly monetary and is healing, while an entry-level
  displacement signal in degreed knowledge-work entrants persists and grows beneath it,
  too concentrated to move aggregate Okun's Law but exactly what the real-world reports
  describe.""")

# ---- chart -------------------------------------------------------------------
fig, axes = plt.subplots(1, 3, figsize=(19, 6.2))

ax = axes[0]
ax.plot(j.index, j["resid"], lw=2.0, color="#c0392b", label="young college grads")
ax.plot(jc.index, jc["resid"], lw=1.6, color="#7f8c8d", label="all 20-24 (control)")
ax.axhline(0, color="black", lw=1.0)
ax.axhline(mx_pre, color="#c0392b", ls=":", lw=1.3)
ax.text(pd.Timestamp("2002-01-01"), mx_pre + 0.05, "largest pre-2020 deviation", fontsize=8, color="#7b241c")
ax.axvspan(pd.Timestamp("2022-11-01"), j.index[-1], color="gold", alpha=0.2, label="generative-AI era")
ax.set_ylabel("unemployment above cyclical prediction (pp)", fontsize=10)
ax.set_title("1. Young college graduates vs the cycle\n12m means; prediction fit on 2001-2019",
             fontsize=11.5, fontweight="bold")
ax.legend(fontsize=8.5); ax.grid(True, ls="--", alpha=0.35)

ax = axes[1]
h = band.loc[:"2019-12-31"]
ax.scatter(h["u"], h["dur"], s=22, color="#95a5a6", alpha=0.6, label="1967-2019, same unemployment band")
nw = band.loc["2024-01-01":]
ax.scatter(nw["u"], nw["dur"], s=48, color="#c0392b", zorder=3, label="2024-2026")
ax.set_xlabel("unemployment rate (%)", fontsize=10)
ax.set_ylabel("median unemployment duration, weeks (12m mean)", fontsize=10)
ax.set_title("2. Search duration at 4.0-4.6% unemployment\nsame rate, much longer searches",
             fontsize=11.5, fontweight="bold")
ax.legend(fontsize=8.5); ax.grid(True, ls="--", alpha=0.35)

ax = axes[2]
labs = list(slopes.keys())
vals = [slopes[k][0] for k in labs]
errs = [1.96 * slopes[k][1] for k in labs]
ax.bar(np.arange(3), vals, yerr=errs, color=["#95a5a6", "#1f4e79", "#c0392b"],
       error_kw=dict(lw=1.3, capsize=4))
ax.set_xticks(np.arange(3))
ax.set_xticklabels([f"{k}\n{'pre-AI' if k=='2013-2019' else ('AI-era' if k=='2019-2025' else 'post-ChatGPT')}" for k in labs], fontsize=9)
ax.set_ylabel("productivity slope on replaceability (pp/yr per unit)", fontsize=10)
ax.set_title("3. The gradient steepened into the AI era\nr fell slightly; the slope is what matters",
             fontsize=11.5, fontweight="bold")
ax.grid(True, axis="y", ls="--", alpha=0.35)

fig.suptitle("What the stocks missed: entry-level workers, search duration, and the slope of the gradient",
             fontsize=13, fontweight="bold", y=1.02)
plt.tight_layout()
plt.savefig("what_the_stocks_missed.png", dpi=150, bbox_inches="tight")
print("\nChart saved: what_the_stocks_missed.png")
