"""
finance_real_bracket.py
Settle the finance decoupling by fixing the two problems in the earlier version:

  (1) DEFLATOR. The BEA finance value-added deflator is FISIM-contaminated and
      runs ~4.8%/yr (vs ~2-3%/yr economy-wide), which understates real finance
      output in exactly the rate-hike years. We re-deflate the nominal series
      with a general price index (GDP deflator) and show the result next to the
      official finance deflator, as a bracket.

  (2) NAICS MISMATCH. Output is Finance & Insurance (NAICS 52). USFIRE
      employment is Financial Activities (52 + 53 Real Estate). We add
      Finance-&-Insurance-only employment (CES5552000001) so numerator and
      denominator cover the same industry.

Inputs (../FRED-Data/):
  financial_activities_value_added_VAFI.csv                 nominal VA, Finance & Insurance (have)
  finance_value_added_deflator_A795RG3A027NBEA.csv          official finance VA deflator (have)
  gdp_deflator_GDPDEF.csv                                   general price index (DOWNLOAD)
  financial_activities_employment_USFIRE.csv                employment 52+53 (have)
  finance_insurance_employment_CES5552000001.csv            employment 52 only (DOWNLOAD)

Outputs finance_real_bracket.png and a bracket table.
"""

import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE     = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(HERE, "..", "FRED-Data") + os.sep

GDPDEF_FILE = "gdp_deflator_GDPDEF.csv"
EMP52_FILE  = "finance_insurance_employment_CES5552000001.csv"


def load(filename, label):
    df = pd.read_csv(os.path.join(DATA_DIR, filename))
    df.columns = [c.strip() for c in df.columns]
    df[df.columns[0]] = pd.to_datetime(df[df.columns[0]])
    df = df.set_index(df.columns[0])
    df[df.columns[0]] = pd.to_numeric(df[df.columns[0]], errors="coerce")
    return df.iloc[:, 0].rename(label).dropna()


missing = [f for f in (GDPDEF_FILE, EMP52_FILE) if not os.path.exists(os.path.join(DATA_DIR, f))]
if missing:
    print("Download these into ../FRED-Data/ first:")
    if GDPDEF_FILE in missing:
        print(f"  {GDPDEF_FILE}   https://fred.stlouisfed.org/graph/fredgraph.csv?id=GDPDEF")
    if EMP52_FILE in missing:
        print(f"  {EMP52_FILE}   https://fred.stlouisfed.org/graph/fredgraph.csv?id=CES5552000001")
    raise SystemExit(0)

nom      = load("financial_activities_value_added_VAFI.csv", "nom").resample("YS").mean()
fin_defl = load("finance_value_added_deflator_A795RG3A027NBEA.csv", "fdefl")            # annual
gdp_defl = load(GDPDEF_FILE, "gdefl").resample("YS").mean()                             # -> annual
emp_all  = load("financial_activities_employment_USFIRE.csv", "e_all").resample("YS").mean()   # 52+53
emp_52   = load(EMP52_FILE, "e_52").resample("YS").mean()                               # 52 only


def cagr(s):
    s = s[s.index >= "2013-01-01"].dropna()
    yrs = (s.index[-1] - s.index[0]).days / 365.25
    return ((s.iloc[-1] / s.iloc[0]) ** (1 / yrs) - 1) * 100


# real output under each deflator (index cancels; growth is what matters)
real_fin = (nom / fin_defl).dropna()          # official finance deflator
real_gdp = (nom / gdp_defl).dropna()          # general GDP deflator

print("=" * 74)
print("FINANCE REAL DECOUPLING — deflator bracket x NAICS-consistent employment")
print("=" * 74)
print(f"\nNominal output CAGR 2013-25: {cagr(nom):.1f}%/yr")
print(f"Employment CAGR: Financial Activities (52+53) {cagr(emp_all):.1f}%/yr | "
      f"Finance & Insurance (52) {cagr(emp_52):.1f}%/yr\n")

print(f"Real OUTPUT growth:  finance deflator {cagr(real_fin):.1f}%/yr   |   GDP deflator {cagr(real_gdp):.1f}%/yr\n")

print("Real PRODUCTIVITY (output/worker) CAGR, %/yr:")
print(f"  {'':<26}{'emp 52+53 (USFIRE)':>20}{'emp 52 only':>14}")
for lab, real in [("official finance deflator", real_fin), ("general GDP deflator", real_gdp)]:
    p_all = cagr((real / emp_all).dropna())
    p_52  = cagr((real / emp_52).dropna())
    print(f"  {lab:<26}{p_all:>18.1f}{p_52:>14.1f}")
print("\n(US-average labor productivity growth ~1.5%/yr)")

# ---- chart ----
fig, ax = plt.subplots(figsize=(12, 6))
def idx(s):
    s = s[s.index >= "2013-01-01"]; return s / s.iloc[0] * 100
ax.plot(idx(nom).index,      idx(nom),      color="#c0392b", lw=2.4, label="Nominal output")
ax.plot(idx(real_fin).index, idx(real_fin), color="#7f8c8d", lw=2.4, ls="--",
        label="Real (official finance deflator) — what I used")
ax.plot(idx(real_gdp).index, idx(real_gdp), color="#1f4e79", lw=2.6,
        label="Real (general GDP deflator) — honest version")
ax.plot(idx(emp_52).index,   idx(emp_52),   color="#2e7d32", lw=2.2, label="Employment, Finance & Insurance (52)")
ax.set_ylabel("Index (2013 = 100)", fontsize=11)
ax.set_title("Financial Activities: real output depends entirely on the deflator\n"
             "Gap between blue and green = the genuine decoupling the finance deflator hides",
             fontsize=12, fontweight="bold")
ax.legend(fontsize=9); ax.grid(True, ls="--", alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(HERE, "finance_real_bracket.png"), dpi=150, bbox_inches="tight")
print("\nChart saved: finance_real_bracket.png")
