"""
cf_style_comparison.py
Does the Cleveland Fed's actual specification explain the goods-sector inversion?

identification_check.py found that this project's own mechanism (unemployment
responds to the Fed funds rate ~1.7-3 quarters faster than output does) does not
survive proper identification: the gap is statistically indistinguishable from
zero under a local projection with Newey-West errors and under a moving-block
bootstrap at two block lengths.

The Cleveland Fed's Jacobs & Krolikowski (EC 2026-06) reconcile the AGGREGATE
version of this same puzzle with a much simpler device: they lag OUTPUT itself
relative to unemployment by about two quarters,

    U_t  compared to  Y_(t-2)

not a differential response to a common third variable (the policy rate). This
script asks the direct question this project has not yet asked: does THEIR
specification, applied to the three physical sectors, resolve the inversion
better than, worse than, or about the same as this project's FFR-lag story?

METHOD
For each sector, and for the aggregate as a check against their published
result, find the lag L on real value-added growth that maximizes |corr| with
the change in the unemployment rate, contemporaneous vs lagged output:

    du_t  vs  dy_(t-L),   L = 0..6

Then compare the 2024-2025 rolling correlation using GDP lagged 2 quarters
(their number) against the unlagged Okun correlation already documented in
rolling_okun_inversion.py, to see whether their simple fix moves the
correlation back toward its historical, negative range.

Reads FRED CSVs from ../FRED-Data/. Writes cf_style_comparison.png.
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
WINDOW   = 12
CF_LAG   = 2      # the Cleveland Fed's output lag, in quarters

SECTORS = {
    "Construction":   ("construction_value_added_RVAC.csv",
                       "construction_unemployment_rate_LNU04032231.csv"),
    "Manufacturing":  ("manufacturing_value_added_RVAMA.csv",
                       "manufacturing_unemployment_rate_LNU04032232.csv"),
    "Transportation": ("transportation_warehousing_value_added_RVAT.csv",
                       "transportation_utilities_unemployment_rate_LNU04032236.csv"),
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


def series(of, uf):
    y = (load(of).pct_change(4) * 100).dropna()
    u = load(uf).resample("QS").mean().diff(4).dropna()
    return y, u


def lag_scan(y, u, maxlag=6, start="1991-01-01"):
    rows = []
    for L in range(maxlag + 1):
        j = pd.DataFrame({"y": y.shift(L), "u": u}).dropna()
        j = j[j.index >= start]
        j = j[~j.index.isin(COVID_Q)]
        if len(j) < 25:
            continue
        r, p = sp_stats.pearsonr(j["y"], j["u"])
        rows.append((L, r, p, len(j)))
    return pd.DataFrame(rows, columns=["lag", "r", "p", "n"])


def rolling_corr(y, u, y_lag=0):
    d = pd.DataFrame({"y": y.shift(y_lag), "u": u}).dropna()
    idx = d.index.tolist()
    out = {}
    for i in range(WINDOW, len(idx) + 1):
        w = d.iloc[i - WINDOW:i]
        if np.std(w["y"]) > 1e-9:
            out[idx[i - 1]] = np.corrcoef(w["y"], w["u"])[0, 1]
    return pd.Series(out)


print("=" * 92)
print("DOES THE CLEVELAND FED'S SPECIFICATION (U_t vs Y_(t-2)) EXPLAIN THE SECTOR INVERSION?")
print("=" * 92)
print(f"\nTheir mechanism: lag output 2 quarters relative to unemployment, no policy-rate")
print(f"channel. This project's mechanism: unemployment and output both respond to the")
print(f"Fed funds rate, but (it claimed) at different lags. Testing both on the same data.\n")

print(f"{'sector':<16}{'best lag':>10}{'r at best':>11}{'p':>9}{'r at CF lag=2':>15}{'p':>9}"
      f"{'r at lag=0':>12}{'p':>9}")
results = {}
for name, (of, uf) in SECTORS.items():
    y, u = series(of, uf)
    scan = lag_scan(y, u)
    results[name] = (y, u, scan)
    best = scan.iloc[scan["r"].abs().idxmax()]
    cf = scan[scan["lag"] == CF_LAG].iloc[0]
    z = scan[scan["lag"] == 0].iloc[0]
    print(f"{name:<16}{int(best['lag']):>9}q{best['r']:>+11.3f}{best['p']:>9.3f}"
          f"{cf['r']:>+15.3f}{cf['p']:>9.3f}{z['r']:>+12.3f}{z['p']:>9.3f}")

print("\n" + "-" * 92)
print("DOES A 2-QUARTER OUTPUT LAG PULL THE 2024-2025 ROLLING CORRELATION BACK NEGATIVE?")
print("-" * 92)
print(f"\n{'sector':<16}{'peak r, lag=0 (original)':>26}{'peak r, lag=2 (CF-style)':>26}"
      f"{'improvement':>14}")
for name, (of, uf) in SECTORS.items():
    y, u = series(of, uf)
    r0 = rolling_corr(y, u, y_lag=0)
    r2 = rolling_corr(y, u, y_lag=CF_LAG)
    w0 = r0[r0.index >= "2023-01-01"]
    w2 = r2[r2.index >= "2023-01-01"]
    pk0 = w0.max() if len(w0) else np.nan
    pk2 = w2.max() if len(w2) else np.nan
    print(f"{name:<16}{pk0:>+26.3f}{pk2:>+26.3f}{pk0-pk2:>+14.3f}")

print("\n  If the CF-style lag were the whole story, the lag=2 peak correlation should")
print("  drop close to zero or negative. It is reported above without interpretation")
print("  spin: read the 'improvement' column directly.")

# ---------------------------------------------------------------------------
# aggregate check: does the well-known aggregate Okun relationship reproduce
# the Cleveland Fed's own headline number as a sanity check on the method
# ---------------------------------------------------------------------------
print("\n" + "-" * 92)
print("SANITY CHECK: aggregate GDP vs UNRATE, same method, to compare against their result")
print("-" * 92)
gdp = load("real_gdp_GDPC1.csv").resample("QS").mean()
unr = load("unemployment_rate_UNRATE.csv").resample("QS").mean()
gy  = (gdp.pct_change(4) * 100).dropna()
du  = unr.diff(4).dropna()
agg_scan = lag_scan(gy, du, maxlag=6, start="1990-01-01")
print(f"\n  {'lag':>5}{'r':>9}{'p':>10}")
for _, row in agg_scan.iterrows():
    print(f"  {int(row['lag']):>4}q{row['r']:>+9.3f}{row['p']:>10.4f}")
best_agg = agg_scan.iloc[agg_scan["r"].abs().idxmax()]
print(f"\n  Best aggregate lag: {int(best_agg['lag'])}q (r={best_agg['r']:+.3f}). "
      f"CF report ~2q on their sample; compare directly.")

# ---- chart -------------------------------------------------------------------
fig, axes = plt.subplots(1, 3, figsize=(18.5, 6.2))
for i, (name, (y, u, scan)) in enumerate(results.items()):
    ax = axes[i]
    ax.axhline(0, color="black", lw=1, ls="--")
    ax.bar(scan["lag"], scan["r"], color=["#c0392b" if L == CF_LAG else "#1f4e79"
                                          for L in scan["lag"]])
    ax.set_title(f"{name}\ncorr(du, dy lagged L quarters)", fontsize=11, fontweight="bold")
    ax.set_xlabel("lag L on output growth (quarters)", fontsize=9.5)
    if i == 0:
        ax.set_ylabel("correlation", fontsize=9.5)
    ax.grid(True, axis="y", ls="--", alpha=0.3)
fig.suptitle("Testing the Cleveland Fed's own specification (red bar = their 2-quarter lag) "
             "on the three physical sectors", fontsize=13, fontweight="bold", y=1.02)
plt.tight_layout()
out = os.path.join(HERE, "cf_style_comparison.png")
plt.savefig(out, dpi=150, bbox_inches="tight")
print(f"\nChart saved: {out}")
