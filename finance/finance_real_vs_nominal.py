"""
finance_real_vs_nominal.py
How much of the Finance "output doubled / productivity up 79%" story is real,
and how much is just inflation?

Context: the finance sub-analysis used financial_activities_value_added_VAFI.csv
as "output." That series is NOMINAL (current-dollar) value added for Finance &
Insurance. Using nominal output means every finding on the output side (output
growth, productivity, the employment elasticity) is inflated by prices. This
script re-does the output side in REAL terms and reports how much of each
headline survives deflation.

Inputs (drop into ../FRED-Data/):
  financial_activities_value_added_VAFI.csv                 nominal VA (quarterly, have it)
  finance_value_added_real_A795RX1A027NBEA.csv              real VA, chained $ (annual)
  finance_value_added_deflator_A795RG3A027NBEA.csv          VA price deflator (annual)
  financial_activities_employment_USFIRE.csv                headcount (have it)

The real and deflator series are ANNUAL. For the level/productivity comparison
we work annually. For the quarterly employment-elasticity recompute we deflate
the quarterly nominal series with the annual deflator interpolated to quarters.

Outputs finance_real_vs_nominal.png and a console summary.
"""

import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE     = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(HERE, "..", "FRED-Data") + os.sep
CUT      = pd.Timestamp("2022-10-01")

REAL_FILE = "finance_value_added_real_A795RX1A027NBEA.csv"
DEFL_FILE = "finance_value_added_deflator_A795RG3A027NBEA.csv"


def load(filename, label):
    df = pd.read_csv(os.path.join(DATA_DIR, filename))
    df.columns = [c.strip() for c in df.columns]
    df[df.columns[0]] = pd.to_datetime(df[df.columns[0]])
    df = df.set_index(df.columns[0])
    df[df.columns[0]] = pd.to_numeric(df[df.columns[0]], errors="coerce")
    return df.iloc[:, 0].rename(label).dropna()


nominal = load("financial_activities_value_added_VAFI.csv", "nominal")          # quarterly
emp_q   = load("financial_activities_employment_USFIRE.csv", "emp").resample("QS").mean()

have_real = os.path.exists(os.path.join(DATA_DIR, REAL_FILE))
have_defl = os.path.exists(os.path.join(DATA_DIR, DEFL_FILE))
if not (have_real or have_defl):
    print("MISSING the real series and/or deflator. Download into ../FRED-Data/:")
    print(f"  {REAL_FILE}   from  https://fred.stlouisfed.org/graph/fredgraph.csv?id=A795RX1A027NBEA")
    print(f"  {DEFL_FILE}   from  https://fred.stlouisfed.org/graph/fredgraph.csv?id=A795RG3A027NBEA")
    raise SystemExit(0)

# Build a quarterly REAL output series two ways, use whichever is available.
if have_defl:
    defl = load(DEFL_FILE, "defl")                       # annual price index
    # interpolate annual deflator to quarterly, base to 2017=100 if it is not already
    defl_q = defl.resample("QS").interpolate("linear").reindex(nominal.index).interpolate("linear")
    real_q = (nominal / defl_q * 100.0).rename("real")   # deflate nominal -> real, quarterly
    real_src = "deflated nominal with the VA price index"
else:
    real_a = load(REAL_FILE, "real")                     # annual real level
    real_q = real_a.resample("QS").interpolate("linear").reindex(nominal.index).interpolate("linear").rename("real")
    real_src = "annual real series interpolated to quarters"

def idx(s, base="2013-01-01"):
    b = s[s.index >= base].iloc[0]
    return s / b * 100

def cagr(s, a, b):
    s2 = s[(s.index >= a) & (s.index <= b)]
    yrs = (s2.index[-1] - s2.index[0]).days / 365.25
    return ((s2.iloc[-1] / s2.iloc[0]) ** (1 / yrs) - 1) * 100

print("=" * 68)
print("FINANCE OUTPUT: NOMINAL vs REAL  (real =", real_src + ")")
print("=" * 68)
ni, ri = idx(nominal), idx(real_q)
print(f"  output index 2013=100 -> latest:   nominal {ni.iloc[-1]:.0f}   real {ri.iloc[-1]:.0f}")
print(f"  output CAGR 2013-latest:           nominal {cagr(nominal,'2013-01-01',str(nominal.index[-1].date())):.1f}%/yr"
      f"   real {cagr(real_q,'2013-01-01',str(real_q.index[-1].date())):.1f}%/yr")

# productivity = output per worker, nominal vs real
df = pd.DataFrame({"nominal": nominal, "real": real_q, "emp": emp_q}).dropna()
prod_nom = cagr(df["nominal"]/df["emp"], "2013-01-01", str(df.index[-1].date()))
prod_real = cagr(df["real"]/df["emp"], "2013-01-01", str(df.index[-1].date()))
print(f"  productivity (output/worker) CAGR: nominal {prod_nom:.1f}%/yr   real {prod_real:.1f}%/yr")

# employment elasticity, nominal vs real output
def elasticity(out):
    d = pd.DataFrame({"o": out, "e": emp_q}).dropna()
    d["dy"] = d["o"].pct_change(4) * 100
    d["de"] = d["e"].pct_change(4) * 100
    d = d.dropna()
    pre, post = d[d.index < CUT], d[d.index >= CUT]
    return (np.polyfit(pre["dy"], pre["de"], 1)[0],
            np.polyfit(post["dy"], post["de"], 1)[0])
gnp, gnq = elasticity(df["nominal"]); grp, grq = elasticity(df["real"])
print(f"  employment elasticity pre/post:    nominal {gnp:+.2f}/{gnq:+.2f}   real {grp:+.2f}/{grq:+.2f}")

# ---- chart ----
fig, ax = plt.subplots(figsize=(12, 6))
s = df[df.index >= "2013-01-01"]
ax.plot(s.index, idx(s["nominal"]), color="#c0392b", lw=2.5, label="Nominal output (what we used)")
ax.plot(s.index, idx(s["real"]),    color="#1f4e79", lw=2.5, label="Real output (inflation removed)")
ax.plot(s.index, idx(s["emp"]),     color="#2e7d32", lw=2.2, label="Employment (headcount)")
ax.set_ylabel("Index (2013 = 100)", fontsize=11)
ax.set_title("Financial Activities: how much of the 'output doubled' is real vs inflation\n"
             "The gap between the red and blue lines is pure prices",
             fontsize=12, fontweight="bold")
ax.legend(fontsize=10); ax.grid(True, ls="--", alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(HERE, "finance_real_vs_nominal.png"), dpi=150, bbox_inches="tight")
print("\nChart saved: finance_real_vs_nominal.png")
