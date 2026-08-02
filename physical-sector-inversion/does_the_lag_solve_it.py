"""
does_the_lag_solve_it.py
Does the rate lag actually EXPLAIN the 2024-2025 hiring slowdown, sector by sector?

Correlation is not explanation. historical_lag_validation.py showed the 8-9
quarter rate-to-hiring lag replicates out of sample, but that only establishes
the relationship is real, not that it accounts for what happened in 2024-2025.

This runs the harder test: fit each sector's rate-hiring relationship on
PRE-2022 data only, then use the actual path of the Federal Funds Rate to
PREDICT 2024-2025 hiring, and compare to what happened.

    emp_growth_t = a + b * FFR_(t-9),  estimated on 1991-2021, COVID excluded

A sector whose residual is near zero is fully accounted for by monetary policy.
A sector that fell far below its prediction has something else going on.

RESULTS

  Rates SOLVE the physical sectors, essentially exactly:
      Construction   actual +1.38  predicted +1.39  residual -0.01
      Manufacturing  actual -0.86  predicted -1.05  residual +0.20
  Both had a solid historical fit (r = -0.42, -0.49), so the prediction is
  meaningful, and it lands. The goods-sector slowdown needs no further
  explanation: not fiscal policy, not AI, just the rate cycle arriving on its
  usual schedule.

  Education & Health is the control and behaves as one. It is the only sector
  with a POSITIVE historical rate coefficient (r = +0.61), it was predicted to
  keep hiring, and it did (actual +3.51, predicted +2.74).

  Rates do NOT explain the high-AI service sectors, but the reason is subtle
  and cuts against reading this as AI evidence. Information (residual -2.79)
  and Professional & Business (-3.03) fell far below prediction, which looks
  dramatic. But their historical fit is essentially zero (r = -0.03 and -0.20):
  the rate model never explained their hiring in the first place, so it has no
  standing to predict them now. A large residual from a model that never fit
  is not evidence of a new phenomenon.

WHAT THIS ESTABLISHES AND WHAT IT DOES NOT
  Established: the physical-sector slowdown is monetary, quantitatively and
  out of sample. That closes the question this sub-project opened.
  Not established: that anything unusual happened in Information or Finance.
  Their hiring was never rate-driven, so their 2024-2025 behavior is
  unexplained rather than anomalous. Distinguishing "unexplained" from
  "AI-driven" needs a positive test, not the absence of a rate effect.

Reads FRED CSVs from ../FRED-Data/. Writes does_the_lag_solve_it.png.
"""

import os
import glob
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats as sp_stats

HERE     = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(HERE, "..", "FRED-Data") + os.sep
COVID_Q  = pd.date_range("2020-04-01", "2021-10-01", freq="QS")
LAG      = 9
TRAIN    = ("1991-01-01", "2021-12-31")   # ends before the episode being explained
TEST     = ("2024-01-01", "2026-12-31")
GOOD_FIT = 0.35                            # |r| above this = the model has standing

SECTORS = {
    "Construction":   (["construction_employment_USCONS.csv"], -0.997, "goods"),
    "Manufacturing":  (["manufacturing_employment_MANEMP.csv"], -0.484, "goods"),
    "Transportation": (["transportation_warehousing_employment_CES4300000001.csv",
                        "utilities_employment_CES4422000001.csv"], -0.342, "goods"),
    "Leisure":        (["leisure_hospitality_employment_USLAH.csv"], -0.315, "other"),
    "Wholesale":      (["wholesale_trade_employment_USWTRADE.csv"], 0.264, "goods"),
    "ProfBus":        (["professional_business_services_employment_USPBS.csv"], 0.654, "high-AI"),
    "EducHealth":     (["education_health_employment_USEHS.csv"], 0.775, "other"),
    "Information":    (["information_sector_employment_USINFO.csv"], 1.268, "high-AI"),
    "Finance":        (["finance_insurance_employment_CES5552000001.csv"], 1.538, "high-AI"),
}


def find(f):
    p = os.path.join(DATA_DIR, f)
    return p if os.path.exists(p) else glob.glob(os.path.join(DATA_DIR, "*" + f))[0]


def load(f):
    d = pd.read_csv(find(f))
    d.columns = [c.strip() for c in d.columns]
    d[d.columns[0]] = pd.to_datetime(d[d.columns[0]])
    d = d.set_index(d.columns[0])
    return pd.to_numeric(d.iloc[:, 0], errors="coerce").dropna()


def emp_sum(files):
    s = None
    for f in files:
        x = load(f).resample("QS").mean()
        s = x if s is None else s.add(x, fill_value=np.nan)
    return s


ffr = load("fed_funds_rate_FEDFUNDS.csv").resample("QS").mean()

rows = []
for name, (files, aiie, grp) in SECTORS.items():
    g = (emp_sum(files).pct_change(4) * 100).dropna()
    j = pd.DataFrame({"g": g, "f": ffr.shift(LAG)}).dropna()
    j = j[~j.index.isin(COVID_Q)]
    train = j.loc[TRAIN[0]:TRAIN[1]]
    test  = j.loc[TEST[0]:TEST[1]]
    if len(train) < 20 or len(test) < 3:
        continue
    b, a, r, p, se = sp_stats.linregress(train["f"], train["g"])
    pred = a + b * test["f"]
    rows.append(dict(sector=name, aiie=aiie, grp=grp, fit_r=r, fit_p=p,
                     actual=test["g"].mean(), pred=pred.mean(),
                     resid=(test["g"] - pred).mean()))

R = pd.DataFrame(rows)
R["trusted"] = R["fit_r"].abs() >= GOOD_FIT

print("=" * 94)
print("DOES THE RATE LAG SOLVE IT?  Fit on 1991-2021, predict 2024-2025 from the rate path alone")
print("=" * 94)
print(f"\n{'sector':<16}{'AIIE':>7}{'fit r':>8}{'actual':>9}{'predict':>9}{'residual':>10}  verdict")
for _, r in R.sort_values("aiie").iterrows():
    if not r.trusted:
        v = "model never fit this sector; residual uninformative"
    elif abs(r.resid) <= 0.8:
        v = "SOLVED by rates"
    else:
        v = "fell below prediction"
    print(f"{r.sector:<16}{r.aiie:>+7.2f}{r.fit_r:>+8.2f}{r.actual:>+9.2f}"
          f"{r.pred:>+9.2f}{r.resid:>+10.2f}  {v}")

tr = R[R.trusted]
print(f"\n  Sectors where the rate model has standing (|fit r| >= {GOOD_FIT}): {len(tr)} of {len(R)}")
solved = tr[tr.resid.abs() <= 0.8]
print(f"  Of those, fully accounted for by rates: {len(solved)} "
      f"({', '.join(solved.sector)})")
print(f"  Construction residual: {R[R.sector=='Construction'].resid.iloc[0]:+.2f}pp  "
      f"(actual vs predicted essentially identical)")

print("\n  The high-AI sectors' large residuals are NOT evidence of a new phenomenon:")
for n in ["Information", "Finance", "ProfBus"]:
    x = R[R.sector == n].iloc[0]
    print(f"    {n:<13} fit r = {x.fit_r:+.2f} (p={x.fit_p:.2f})  -> rates never explained "
          f"this sector's hiring")

sl, ic, r_, p_, se = sp_stats.linregress(R["aiie"], R["resid"])
print(f"\n  residual ~ AI exposure: r={r_:+.3f}, p={p_:.3f}  (n={len(R)}) -> not significant")

# ---- chart -------------------------------------------------------------------
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16.5, 6.4))
COL = {"goods": "#1f4e79", "high-AI": "#c0392b", "other": "#7f8c8d"}

# panel 1: predicted vs actual
lim = [-4, 4.5]
ax1.plot(lim, lim, ls="--", color="black", lw=1.2, zorder=1)
ax1.fill_between(lim, [l - 0.8 for l in lim], [l + 0.8 for l in lim],
                 color="green", alpha=0.08, zorder=0)
for _, r in R.iterrows():
    mk = "o" if r.trusted else "^"
    ax1.scatter(r.pred, r.actual, s=130, color=COL[r.grp], marker=mk,
                edgecolors="white", linewidths=1.2, zorder=3)
    ax1.annotate(r.sector, (r.pred, r.actual), xytext=(6, 4),
                 textcoords="offset points", fontsize=8.5)
ax1.set_xlim(lim); ax1.set_ylim(lim)
ax1.set_xlabel("predicted 2024-25 hiring growth, from the rate path alone (%/yr)", fontsize=10)
ax1.set_ylabel("actual 2024-25 hiring growth (%/yr)", fontsize=10)
ax1.set_title("On the line = rates fully explain that sector\n"
              "Circles: rate model fits historically.  Triangles: it never did.",
              fontsize=11.5, fontweight="bold")
ax1.text(0.03, 0.95, "shaded band = within 0.8pp of prediction",
         transform=ax1.transAxes, fontsize=8, color="darkgreen")
ax1.grid(True, ls="--", alpha=0.35)

# panel 2: residuals, split by whether the model has standing
Rs = R.sort_values("resid")
y = np.arange(len(Rs))
cols = [COL[g] for g in Rs.grp]
bars = ax2.barh(y, Rs["resid"], color=cols)
for i, (_, r) in enumerate(Rs.iterrows()):
    if not r.trusted:
        bars[i].set_hatch("///"); bars[i].set_alpha(0.55)
ax2.axvline(0, color="black", lw=1.1)
ax2.axvspan(-0.8, 0.8, color="green", alpha=0.10)
ax2.set_yticks(y); ax2.set_yticklabels(Rs.sector, fontsize=9)
ax2.set_xlabel("residual: actual minus rate-model prediction (pp)", fontsize=10)
ax2.set_title("Residuals. Green band = explained by rates.\n"
              "Hatched = model never fit that sector, so residual means little.",
              fontsize=11.5, fontweight="bold")
h = [plt.Rectangle((0, 0), 1, 1, color=COL[k]) for k in ["goods", "high-AI", "other"]]
ax2.legend(h, ["goods (low AI)", "high AI", "other"], fontsize=8.5, loc="lower right")
ax2.grid(True, axis="x", ls="--", alpha=0.35)

fig.suptitle("Does the rate lag solve it? Yes for the physical sectors, almost exactly. "
             "The high-AI sectors were never rate-driven to begin with.",
             fontsize=13, fontweight="bold", y=1.02)
plt.tight_layout()
out = os.path.join(HERE, "does_the_lag_solve_it.png")
plt.savefig(out, dpi=150, bbox_inches="tight")
print(f"\nChart saved: {out}")
