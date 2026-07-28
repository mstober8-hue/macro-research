"""
real_productivity_ai_crosssection.py
The corrected Phase 3: does AI exposure predict the output-labor decoupling?

The original Phase 3 measured Okun's law with the UNEMPLOYMENT rate and found
AI exposure predicts LESS breakdown (r=-0.61), the project's "contradicts AI"
headline. But unemployment is saturated for the high-AI service sectors, which
sit at their unemployment floor. Re-measured on REAL PRODUCTIVITY (real output
per worker, the variable AI actually targets), the sign flips and becomes
significant.

Two corrections make this honest:
  - Finance output (VAFI) is NOMINAL and its BEA deflator is FISIM-broken, so
    finance is deflated with the neutral GDP deflator. The other eight sectors
    use their BEA real value added (RVA*), whose deflators are fine.
  - Employment is each sector's headcount; finance uses Finance & Insurance
    (NAICS 52) to match its Finance & Insurance output.

Outputs real_productivity_ai_crosssection.png and a console table.
Reads from FRED-Data/. Run from the repo root.
"""

import os, glob
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats as sp

DATA = "FRED-Data/"
CUT  = pd.Timestamp("2022-10-01")
EXC  = pd.date_range("2020-04-01", "2022-01-01", freq="QS")


def find(f):
    if os.path.exists(DATA + f):
        return DATA + f
    m = glob.glob(DATA + "*" + f)
    return m[0]


def load(f):
    d = pd.read_csv(find(f)); d.columns = [c.strip() for c in d.columns]
    d[d.columns[0]] = pd.to_datetime(d[d.columns[0]]); d = d.set_index(d.columns[0])
    return pd.to_numeric(d.iloc[:, 0], errors="coerce").dropna()


def esum(fs):
    s = None
    for f in fs:
        x = load(f).resample("QS").mean(); s = x if s is None else s.add(x, fill_value=np.nan)
    return s


def cagr(s):
    s = s[s.index >= "2013-01-01"].dropna(); yrs = (s.index[-1] - s.index[0]).days / 365.25
    return ((s.iloc[-1] / s.iloc[0]) ** (1 / yrs) - 1) * 100


gdpdef = load("gdp_deflator_GDPDEF.csv")
vn = load("financial_activities_value_added_VAFI.csv")
fin_real = vn / gdpdef.reindex(vn.index).interpolate() * 100

# name: (real output, employment files, unemployment file, AIIE)
S = {
 "Financial Activities":       (fin_real, ["finance_insurance_employment_CES5552000001.csv"], "financial_activities_unemployment_rate_LNU04032238.csv", 1.538),
 "Information":                (load("information_sector_value_added_RVAI.csv"), ["information_sector_employment_USINFO.csv"], "information_sector_unemployment_rate_LNU04032237.csv", 1.268),
 "Education & Health":         (load("health_care_social_assistance_value_added_RVAHCSA.csv"), ["education_health_employment_USEHS.csv"], "education_health_unemployment_rate_LNU04032240.csv", 0.775),
 "Professional & Business":    (load("professional_business_services_value_added_RVAPBS.csv"), ["professional_business_services_employment_USPBS.csv"], "professional_business_services_unemployment_rate_LNU04032239.csv", 0.654),
 "Wholesale Trade":           (load("wholesale_trade_value_added_RVAW.csv"), ["wholesale_trade_employment_USWTRADE.csv"], "wholesale_retail_trade_unemployment_rate_LNU04032235.csv", 0.264),
 "Leisure & Hospitality":     (load("leisure_hospitality_value_added_RVAAERAF.csv"), ["leisure_hospitality_employment_USLAH.csv"], "leisure_hospitality_unemployment_rate_LNU04032241.csv", -0.315),
 "Transportation & Utilities":(load("transportation_warehousing_value_added_RVAT.csv"), ["transportation_warehousing_employment_CES4300000001.csv", "utilities_employment_CES4422000001.csv"], "transportation_utilities_unemployment_rate_LNU04032236.csv", -0.342),
 "Manufacturing":             (load("manufacturing_value_added_RVAMA.csv"), ["manufacturing_employment_MANEMP.csv"], "manufacturing_unemployment_rate_LNU04032232.csv", -0.484),
 "Construction":              (load("construction_value_added_RVAC.csv"), ["construction_employment_USCONS.csv"], "construction_unemployment_rate_LNU04032231.csv", -0.997),
}

rows = []
for name, (out, efs, uf, aiie) in S.items():
    emp = esum(efs)
    prod = cagr((out / emp).dropna())
    # original unemployment difference-form delta-beta (COVID excluded)
    u = load(uf).resample("QS").mean()
    d = pd.DataFrame({"o": out, "u": u}).dropna()
    d["dy"] = d["o"].pct_change(4) * 100; d["du"] = d["u"].diff(4)
    d = d[~d.index.isin(EXC)].dropna()
    bpre = np.polyfit(d[d.index < CUT]["dy"], d[d.index < CUT]["du"], 1)[0]
    bpost = np.polyfit(d[d.index >= CUT]["dy"], d[d.index >= CUT]["du"], 1)[0]
    rows.append(dict(sector=name, aiie=aiie, prod=prod, dbeta=bpost - bpre))
R = pd.DataFrame(rows)

print(R.sort_values("aiie", ascending=False)[["sector", "aiie", "dbeta", "prod"]].round(3).to_string(index=False))

fig, axes = plt.subplots(1, 2, figsize=(15, 6.3))
for ax, col, ylab, title in [
    (axes[0], "dbeta", "Unemployment Δβ  (higher = law weakened)",
     "Measured on UNEMPLOYMENT\n(the original Phase 3)"),
    (axes[1], "prod", "Real productivity growth 2013-25 (%/yr)",
     "Measured on REAL PRODUCTIVITY\n(finance GDP-deflated)")]:
    sl, ic, r, p, se = sp.linregress(R["aiie"], R[col])
    ax.scatter(R["aiie"], R[col], s=95, color="steelblue", zorder=3)
    for _, rw in R.iterrows():
        ax.annotate(rw["sector"].replace(" & ", "&\n"), (rw["aiie"], rw[col]),
                    xytext=(4, 3), textcoords="offset points", fontsize=7)
    xs = np.linspace(R["aiie"].min() - 0.2, R["aiie"].max() + 0.2, 50)
    ax.plot(xs, ic + sl * xs, "--", color="firebrick", lw=1.7)
    verdict = "CONTRADICTS AI" if (r < 0 and p < 0.15) else ("SUPPORTS AI" if (r > 0 and p < 0.10) else "no relationship")
    ax.text(0.04, 0.96, f"r={r:+.2f}  p={p:.3f}\n{verdict}", transform=ax.transAxes, va="top",
            fontsize=11, bbox=dict(boxstyle="round", fc="white", alpha=0.85))
    ax.axhline(0, color="black", lw=0.7, ls=":")
    ax.set_xlabel("AI exposure (AIIE)", fontsize=10); ax.set_ylabel(ylab, fontsize=10)
    ax.set_title(title, fontsize=12, fontweight="bold"); ax.grid(True, ls="--", alpha=0.3)

fig.suptitle("Same nine industries, same question, two labor variables: the headline reverses\n"
             "Unemployment is floored for the high-AI service sectors and cannot see their decoupling; real productivity can",
             fontsize=13, fontweight="bold")
plt.tight_layout(rect=[0, 0, 1, 0.92])
plt.savefig("real_productivity_ai_crosssection.png", dpi=150, bbox_inches="tight")
print("\nChart saved: real_productivity_ai_crosssection.png")
