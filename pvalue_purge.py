"""
pvalue_purge.py
Recompute every load-bearing p-value in this project with inference that is valid
for the data it is computed on.

THE PROBLEM, QUANTIFIED
Simulating two GENUINELY INDEPENDENT AR(1) series and asking how often each
method rejects a true null at the 5% level:

    persistence      naive      HAC   bootstrap
      rho = 0.00      7.3%     8.0%       7.3%
      rho = 0.70     30.0%    14.0%       5.3%
      rho = 0.90     53.0%    27.0%       6.7%
      rho = 0.95     57.7%    36.0%       6.0%

Year-over-year macro growth rates have persistence around 0.9. At that level a
naive p-value rejects a true null MORE THAN HALF THE TIME. Newey-West helps but
is still badly oversized at 27%. Only the circular-shift bootstrap, which
preserves each series' own autocorrelation while destroying the relationship
between them, holds its nominal size.

That is why this project produced five separate false findings from p-values, and
it is why any correlation between two persistent series here needs the bootstrap.

WHAT NEEDS FIXING AND WHAT DOES NOT
Not every p-value in this repository is wrong, and the distinction is sharp.

  CROSS-SECTIONAL claims, one observation per sector or industry, are VALID as
  computed. Nine sectors really are nine units and there is no serial correlation
  between them. The problem there is power, not bias, so those claims are
  reported with a confidence interval and a minimum detectable effect rather than
  being recomputed.

  TIME-SERIES claims, correlations between two persistent series or anything
  built from overlapping windows, are the ones that need the bootstrap. Those are
  recomputed here.

Every number this script prints is what belongs in the README.
"""

import os
import glob
import sys
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import stats_inference as si

HERE  = os.path.dirname(os.path.abspath(__file__))
DATA  = os.path.join(HERE, "FRED-Data") + os.sep
COVID = pd.date_range("2020-04-01", "2021-10-01", freq="QS")


def rd(n):
    p = DATA + n if os.path.exists(DATA + n) else glob.glob(DATA + "*" + n)[0]
    d = pd.read_csv(p)
    d.columns = [c.strip() for c in d.columns]
    d[d.columns[0]] = pd.to_datetime(d[d.columns[0]])
    d = d.set_index(d.columns[0])
    return pd.to_numeric(d.iloc[:, 0], errors="coerce").dropna()


def esum(fs):
    s = None
    for f in fs:
        x = rd(f).resample("QS").mean()
        s = x if s is None else s.add(x, fill_value=np.nan)
    return s


print("=" * 98)
print("P-VALUE PURGE: recomputing load-bearing claims with valid inference")
print("=" * 98)

# =========================================================================
print("\n" + "=" * 98)
print("PART A  TIME-SERIES CLAIMS. These were computed wrong and are recomputed.")
print("=" * 98)

SEC9 = {
    "Construction": ["construction_employment_USCONS.csv"],
    "Manufacturing": ["manufacturing_employment_MANEMP.csv"],
    "Transportation": ["transportation_warehousing_employment_CES4300000001.csv",
                       "utilities_employment_CES4422000001.csv"],
    "Leisure": ["leisure_hospitality_employment_USLAH.csv"],
    "Wholesale": ["wholesale_trade_employment_USWTRADE.csv"],
    "ProfBus": ["professional_business_services_employment_USPBS.csv"],
    "EducHealth": ["education_health_employment_USEHS.csv"],
    "Information": ["information_sector_employment_USINFO.csv"],
    "Finance": ["finance_insurance_employment_CES5552000001.csv"],
}
ffr = rd("fed_funds_rate_FEDFUNDS.csv").resample("QS").mean()
G = pd.DataFrame({n: (esum(f).pct_change(4) * 100) for n, f in SEC9.items()}).dropna()

rows = []

# A1: the headline rate-lag correlation, on the sample the project actually uses
avg06 = G[G.index >= "2006-01-01"].mean(axis=1)
j = pd.DataFrame({"g": avg06, "f": ffr.shift(9)}).dropna()
j = j[~j.index.isin(COVID)]
r1 = si.timeseries_corr(j["f"], j["g"], seed=1)
rows.append(("9-sector hiring vs FFR lag 9, 2006+", "p < 0.0001", r1))

# A2: the same on all available history
avg_all = G.mean(axis=1)
j2 = pd.DataFrame({"g": avg_all, "f": ffr.shift(9)}).dropna()
j2 = j2[~j2.index.isin(COVID)]
r2 = si.timeseries_corr(j2["f"], j2["g"], seed=2)
rows.append(("same, full available history", "(not previously quoted)", r2))

# A3: the out-of-sample physical-sector composite, 1986-2019
phys = esum(["construction_employment_USCONS.csv",
             "manufacturing_employment_MANEMP.csv",
             "wholesale_trade_employment_USWTRADE.csv"])
gp = (phys.pct_change(4) * 100).dropna()
j3 = pd.DataFrame({"g": gp, "f": ffr.shift(9)}).dropna()
j3 = j3[(j3.index >= "1986-01-01") & (j3.index <= "2019-12-31")]
r3 = si.timeseries_corr(j3["f"], j3["g"], seed=3)
rows.append(("physical composite vs FFR lag 9, 1986-2019", "p < 0.0001", r3))

print(f"\n  {'claim':<44}{'as published':>16}{'r':>8}{'naive':>9}{'HAC':>9}{'BOOTSTRAP':>11}")
for lbl, pub, r in rows:
    print(f"  {lbl:<44}{pub:>16}{r['r']:>+8.3f}{r['p_naive']:>9.4f}"
          f"{r['p_hac']:>9.4f}{r['p_boot']:>11.4f}")

print("\n  The bootstrap column is the one to quote. Where it disagrees with the")
print("  published value, the published value was produced by the method shown above")
print("  to reject a true null more than half the time.")

# =========================================================================
print("\n" + "=" * 98)
print("PART B  CROSS-SECTIONAL CLAIMS. Valid as computed, but power-limited.")
print("=" * 98)
print("\n  Nine sectors are nine independent units, so these p-values are NOT biased.")
print("  What they lack is precision. Reporting the confidence interval and the")
print("  minimum detectable effect alongside is what makes them honest.\n")

CS = [
    ("real productivity decoupling vs AI exposure", 0.77, 9),
    ("real productivity decoupling vs replaceability", 0.90, 9),
    ("same, rebuilt from observed Claude usage", 0.76, 9),
    ("hiring slowdown vs AI exposure", 0.19, 9),
    ("productivity acceleration vs AI exposure", 0.26, 9),
    ("acceleration vs replaceability", 0.45, 9),
    ("AI exposure vs slowdown, 3-digit NAICS", -0.22, 65),
]
print(f"  {'claim':<46}{'r':>7}{'n':>5}{'95% CI':>20}{'MDE':>7}   reading")
for lbl, r, n in CS:
    lo, hi = si.fisher_ci(r, n)
    mde = si.mde_correlation(n)
    if abs(r) >= mde:
        note = "clears its own detection threshold"
    elif lo <= 0 <= hi:
        note = "CI spans zero; uninformative"
    else:
        note = "significant but below MDE; fragile"
    print(f"  {lbl:<46}{r:>+7.2f}{n:>5}{f'[{lo:+.2f}, {hi:+.2f}]':>20}{mde:>7.2f}   {note}")

print("\n  A correlation below its own minimum detectable effect is not evidence of")
print("  absence. That is the distinction the project previously collapsed.")

# =========================================================================
print("\n" + "=" * 98)
print("PART C  ROLLING-WINDOW CLAIMS. Nominal n must be divided by the window.")
print("=" * 98)
print("\n  Two 12-quarter windows one quarter apart share 11 quarters. Any n quoted")
print("  from a rolling statistic overstates the evidence by roughly the window length.\n")
print(f"  {'claim':<50}{'nominal n':>11}{'window':>8}{'effective n':>13}")
for lbl, n, w in [("DESYNC vs rolling Okun correlation", 258, 12),
                  ("rolling tau trend, 20-year windows", 16, 20),
                  ("sector rolling Okun break, 12q", 75, 12),
                  ("aggregate rolling Okun, full history", 269, 12)]:
    print(f"  {lbl:<50}{n:>11}{w:>8}{si.effective_n(n, w):>13.1f}")

print("\n  None of these should ever be quoted with their nominal n.")

print("\n" + "=" * 98)
print("SUMMARY OF WHAT CHANGES IN THE READMEs")
print("=" * 98)
surv = [l for l, _, r in rows if r["p_boot"] < 0.05]
died = [l for l, _, r in rows if r["p_boot"] >= 0.05]
print(f"\n  Time-series claims surviving the bootstrap : {len(surv)} of {len(rows)}")
for l in surv:
    print(f"    SURVIVES  {l}")
for l in died:
    print(f"    FAILS     {l}")
uninf = [l for l, r, n in CS if abs(r) < si.mde_correlation(n)]
print(f"\n  Cross-sectional claims below their own MDE : {len(uninf)} of {len(CS)}")
for l in uninf:
    print(f"    UNDERPOWERED  {l}")
