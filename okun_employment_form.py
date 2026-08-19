"""
okun_employment_form.py
Okun's Law measured on EMPLOYMENT rather than unemployment, and what the
unemployment form has been hiding.

THE PROBLEM
Every Okun test in this project measures the relationship between sector output
and the sector UNEMPLOYMENT RATE. The unemployment rate is

    unemployed / labor force

so it only moves when a displaced worker stays in the labor force and searches.
A worker who is displaced and EXITS the labor force, through retirement,
discouragement, or emigration, leaves employment but never enters the numerator.
Unemployment can therefore be flat or falling while employment is falling, and an
unemployment-based Okun measure registers nothing.

This is not hypothetical here. immigration_confound.py found construction
unemployment FELL 2.20pp between 2013-2019 and 2024-2025 while hiring collapsed
and each job posting yielded a third fewer hires. The unemployment rate said the
sector was fine. Employment said it was not.

The project already uses the employment form in places, in hiring_slowdown.py and
does_the_lag_solve_it.py, but every Okun-coefficient test uses the unemployment
form. Those are the tests reporting nulls.

THE TWO FORMS
  UNEMPLOYMENT FORM   d(unemployment rate)  against  output growth
                      the textbook version, and what this project has used

  EMPLOYMENT FORM     employment growth     against  output growth
                      the employment elasticity of output. Falls when output is
                      produced with less labor, which is what displacement means.

The wedge between output growth and employment growth is labor productivity
growth, so a widening wedge is output rising without the employment to match.

WHY AVERAGES RATHER THAN REGRESSION SLOPES
The previous test estimated slopes on 8-quarter episode windows of 4-quarter
differenced data, where consecutive observations share 3 of 4 quarters. Only 1 of
9 sector slopes differed significantly from zero, so those rankings were noise.
Differences in window MEANS are far more robust at this sample size, so the
headline measures here are mean-based, with the regression version reported
alongside for comparison rather than relied on.

THE TEST
For each sector and episode, compute the change from the pre-window to the
episode window in:
  (a) the unemployment response
  (b) employment growth
  (c) the output-employment wedge, that is productivity growth
and ask which of the three lines up with AI exposure, and whether (a) and (c)
disagree in the direction the labor-force-exit story predicts.

Reads FRED CSVs from FRED-Data/. Writes okun_employment_form.png.
"""

import os
import glob
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats as sp_stats

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "FRED-Data") + os.sep

EPISODES = [
    ("2008-09 GFC",        ("2005", "2007"), ("2008", "2010"), "financial crisis"),
    ("2015-16 industrial", ("2012", "2014"), ("2015", "2016"), "oil bust"),
    ("2020 COVID",         ("2017", "2019"), ("2020", "2021"), "pandemic"),
    ("2024-26 current",    ("2013", "2019"), ("2024", "2026"), "THE TEST EPISODE"),
]
CURRENT = "2024-26 current"

S = {
    "Information":    (["information_sector_employment_USINFO.csv"],
                       "information_sector_value_added_RVAI.csv",
                       "information_sector_unemployment_rate_LNU04032237.csv", 1.268),
    "Finance":        (["finance_insurance_employment_CES5552000001.csv"],
                       "GDPDEFLATE:financial_activities_value_added_VAFI.csv",
                       "financial_activities_unemployment_rate_LNU04032238.csv", 1.538),
    "ProfBus":        (["professional_business_services_employment_USPBS.csv"],
                       "professional_business_services_value_added_RVAPBS.csv",
                       "professional_business_services_unemployment_rate_LNU04032239.csv", 0.654),
    "Wholesale":      (["wholesale_trade_employment_USWTRADE.csv"],
                       "wholesale_trade_value_added_RVAW.csv",
                       "wholesale_retail_trade_unemployment_rate_LNU04032235.csv", 0.264),
    "EducHealth":     (["education_health_employment_USEHS.csv"],
                       "health_care_social_assistance_value_added_RVAHCSA.csv",
                       "education_health_unemployment_rate_LNU04032240.csv", 0.775),
    "Manufacturing":  (["manufacturing_employment_MANEMP.csv"],
                       "manufacturing_value_added_RVAMA.csv",
                       "manufacturing_unemployment_rate_LNU04032232.csv", -0.484),
    "Transportation": (["transportation_warehousing_employment_CES4300000001.csv",
                        "utilities_employment_CES4422000001.csv"],
                       "transportation_warehousing_value_added_RVAT.csv",
                       "transportation_utilities_unemployment_rate_LNU04032236.csv", -0.342),
    "Construction":   (["construction_employment_USCONS.csv"],
                       "construction_value_added_RVAC.csv",
                       "construction_unemployment_rate_LNU04032231.csv", -0.997),
    "Leisure":        (["leisure_hospitality_employment_USLAH.csv"],
                       "leisure_hospitality_value_added_RVAAERAF.csv",
                       "leisure_hospitality_unemployment_rate_LNU04032241.csv", -0.315),
}


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


def avg(series, y0, y1):
    x = series.loc[f"{y0}-01-01":f"{y1}-12-31"]
    return x.mean() if len(x) >= 4 else np.nan


EG, OG, DU, UL, AI = {}, {}, {}, {}, {}
for name, (efs, ospec, ufile, aiie) in S.items():
    AI[name] = aiie
    EG[name] = (esum(efs).pct_change(4) * 100).dropna()
    OG[name] = (real_output(ospec).pct_change(4) * 100).dropna()
    UL[name] = load(ufile).resample("QS").mean()          # LEVEL of the rate
    DU[name] = UL[name].diff(4).dropna()                  # YoY change in the rate

rows = []
for label, (p0, p1), (e0, e1), what in EPISODES:
    for name in S:
        d_u = avg(DU[name], e0, e1) - avg(DU[name], p0, p1)
        d_ul = avg(UL[name], e0, e1) - avg(UL[name], p0, p1)   # change in LEVEL
        d_e = avg(EG[name], e0, e1) - avg(EG[name], p0, p1)
        d_o = avg(OG[name], e0, e1) - avg(OG[name], p0, p1)
        rows.append(dict(episode=label, what=what, sector=name, aiie=AI[name],
                         d_unemp=d_u, d_ulevel=d_ul, d_emp=d_e, d_out=d_o,
                         d_wedge=d_o - d_e))
R = pd.DataFrame(rows)

print("=" * 100)
print("OKUN IN EMPLOYMENT FORM: what the unemployment form has been hiding")
print("=" * 100)

cur = R[R.episode == CURRENT].set_index("sector")
print("\n[1] THE CURRENT EPISODE, ALL THREE MEASURES SIDE BY SIDE")
print("    Change from the 2013-2019 baseline to 2024-2026.\n")
print(f"  {'sector':<16}{'AIIE':>7}{'d output':>10}{'d employment':>14}"
      f"{'d unemployment':>16}{'d wedge':>10}")
for s in cur.sort_values("aiie", ascending=False).index:
    r = cur.loc[s]
    print(f"  {s:<16}{r.aiie:>+7.2f}{r.d_out:>+10.2f}{r.d_emp:>+14.2f}"
          f"{r.d_unemp:>+16.2f}{r.d_wedge:>+10.2f}")

print("\n[2] THE BLIND SPOT, MEASURED DIRECTLY")
print("    Sectors where employment fell but unemployment did NOT rise are exactly")
print("    the cases the unemployment form cannot see.\n")
print("    NOTE: this uses the change in the unemployment rate LEVEL, not the change")
print("    in its year-over-year change. The level is the quantity the blind-spot")
print("    argument is about.\n")
print(f"  {'sector':<16}{'employment':>12}{'unemp level':>14}   interpretation")
hidden = []
for s in cur.index:
    r = cur.loc[s]
    if r.d_emp < 0 and r.d_ulevel <= 0:
        tag = "HIDDEN: jobs lost, no unemployment signal"
        hidden.append(s)
    elif r.d_emp < 0 and r.d_ulevel > 0:
        tag = "visible to both forms"
    else:
        tag = "employment held up"
    print(f"  {s:<16}{r.d_emp:>+12.2f}{r.d_ulevel:>+14.2f}   {tag}")
print(f"\n  Sectors invisible to the unemployment form: {len(hidden)} of 9  "
      f"({', '.join(hidden)})")

print("\n[3] WHICH MEASURE LINES UP WITH AI EXPOSURE?")
print("    Spearman across the nine sectors, current episode.\n")
print(f"  {'measure':<34}{'Spearman':>10}{'p':>9}   what a positive/negative means")
tests = [
    ("change in unemployment (2nd diff)", "d_unemp", "+ = exposed sectors' unemployment rose more"),
    ("change in unemployment LEVEL", "d_ulevel", "+ = exposed sectors' unemployment rose more"),
    ("change in employment growth", "d_emp", "- = exposed sectors lost more jobs"),
    ("change in output-emp wedge", "d_wedge", "+ = exposed sectors shed labor per unit output"),
]
for lbl, col, meaning in tests:
    sr, sp_ = sp_stats.spearmanr(cur.aiie, cur[col])
    print(f"  {lbl:<34}{sr:>+10.3f}{sp_:>9.3f}   {meaning}")

print("\n[4] THE SAME THREE MEASURES ACROSS EPISODES")
print("    If the employment form is picking up something real and technology-linked,")
print("    it should behave differently in the current episode than in the others.\n")
print(f"  {'episode':<22}{'d_unemp vs AI':>15}{'d_emp vs AI':>14}{'d_wedge vs AI':>16}")
for label, _, _, what in EPISODES:
    sub = R[R.episode == label].dropna(subset=["d_emp", "d_unemp", "d_wedge"])
    if len(sub) < 5:
        continue
    a = sp_stats.spearmanr(sub.aiie, sub.d_unemp)[0]
    b = sp_stats.spearmanr(sub.aiie, sub.d_emp)[0]
    c = sp_stats.spearmanr(sub.aiie, sub.d_wedge)[0]
    print(f"  {label:<22}{a:>+15.3f}{b:>+14.3f}{c:>+16.3f}")

print("\n[5] DOES THE LABOR FORCE ACTUALLY EXPLAIN THE GAP?")
print("    Implied sector labor force is not directly published, but the mechanism")
print("    leaves a signature: employment falling while unemployment also falls.\n")
both_down = cur[(cur.d_emp < 0) & (cur.d_ulevel < 0)]
print(f"  Sectors with employment growth DOWN and unemployment ALSO DOWN: "
      f"{len(both_down)} of 9")
for s in both_down.index:
    print(f"    {s:<16}employment {both_down.loc[s, 'd_emp']:+.2f}, "
          f"unemployment level {both_down.loc[s, 'd_ulevel']:+.2f}")
print("\n  That combination is arithmetically impossible without the labor force")
print("  shrinking, workers exiting the industry, or both. It is the fingerprint of")
print("  a measure that cannot see what happened.")

# ---- chart -----------------------------------------------------------------
fig, axes = plt.subplots(2, 2, figsize=(15.5, 10.5))

ax = axes[0, 0]
xs = np.arange(len(cur))
srt = cur.sort_values("aiie")
w = 0.38
ax.bar(xs - w/2, srt.d_emp, w, color="#c0392b", label="change in employment growth")
ax.bar(xs + w/2, srt.d_unemp, w, color="#1f4e79", label="change in unemployment")
ax.axhline(0, color="black", lw=1.1)
ax.set_xticks(xs); ax.set_xticklabels(srt.index, fontsize=7.5, rotation=30, ha="right")
ax.set_title("1. The two forms disagree\nemployment fell where unemployment did not rise",
             fontsize=11.5, fontweight="bold")
ax.legend(fontsize=8); ax.grid(True, axis="y", ls="--", alpha=0.3)

ax = axes[0, 1]
ax.scatter(cur.aiie, cur.d_unemp, s=80, color="#1f4e79", label="unemployment form")
sl, ic, _, _, _ = sp_stats.linregress(cur.aiie, cur.d_unemp)
xr = np.linspace(cur.aiie.min(), cur.aiie.max(), 30)
ax.plot(xr, ic + sl * xr, color="#1f4e79", lw=2.0)
ax.axhline(0, color="black", lw=1.0, ls="--")
ax.set_xlabel("AI exposure", fontsize=9.5)
ax.set_ylabel("change in unemployment response", fontsize=9.5)
ax.set_title(f"2. Unemployment form vs AI exposure\n"
             f"Spearman {sp_stats.spearmanr(cur.aiie, cur.d_unemp)[0]:+.2f}",
             fontsize=11.5, fontweight="bold")
ax.grid(True, ls="--", alpha=0.3)

ax = axes[1, 0]
ax.scatter(cur.aiie, cur.d_wedge, s=80, color="#c0392b")
for s in cur.index:
    ax.annotate(s[:11], (cur.loc[s, "aiie"], cur.loc[s, "d_wedge"]), xytext=(5, 4),
                textcoords="offset points", fontsize=7.5)
sl2, ic2, _, _, _ = sp_stats.linregress(cur.aiie, cur.d_wedge)
ax.plot(xr, ic2 + sl2 * xr, color="#c0392b", lw=2.2)
ax.axhline(0, color="black", lw=1.0, ls="--")
ax.set_xlabel("AI exposure", fontsize=9.5)
ax.set_ylabel("change in output-employment wedge (pp)", fontsize=9.5)
ax.set_title(f"3. Employment form vs AI exposure\n"
             f"Spearman {sp_stats.spearmanr(cur.aiie, cur.d_wedge)[0]:+.2f}",
             fontsize=11.5, fontweight="bold")
ax.grid(True, ls="--", alpha=0.3)

ax = axes[1, 1]
eps, uu, ee, ww = [], [], [], []
for label, _, _, _ in EPISODES:
    sub = R[R.episode == label].dropna(subset=["d_emp", "d_unemp", "d_wedge"])
    if len(sub) < 5:
        continue
    eps.append(label[:16])
    uu.append(sp_stats.spearmanr(sub.aiie, sub.d_unemp)[0])
    ee.append(sp_stats.spearmanr(sub.aiie, sub.d_emp)[0])
    ww.append(sp_stats.spearmanr(sub.aiie, sub.d_wedge)[0])
xi = np.arange(len(eps)); bw = 0.27
ax.bar(xi - bw, uu, bw, color="#1f4e79", label="unemployment form")
ax.bar(xi, ee, bw, color="#c0392b", label="employment growth")
ax.bar(xi + bw, ww, bw, color="#2e8b57", label="output-emp wedge")
ax.axhline(0, color="black", lw=1.1)
ax.set_xticks(xi); ax.set_xticklabels(eps, fontsize=7.5, rotation=25, ha="right")
ax.set_ylabel("Spearman with AI exposure", fontsize=9.5)
ax.set_title("4. All three measures, every episode", fontsize=11.5, fontweight="bold")
ax.legend(fontsize=7.5); ax.grid(True, axis="y", ls="--", alpha=0.3)

fig.suptitle("Okun in employment form: the unemployment rate cannot see displacement "
             "that ends in labor-force exit", fontsize=13, fontweight="bold", y=1.0)
plt.tight_layout()
out = os.path.join(HERE, "okun_employment_form.png")
plt.savefig(out, dpi=150, bbox_inches="tight")
print(f"\nChart saved: {out}")
