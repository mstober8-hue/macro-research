"""
historical_lag_validation.py
Does the rate-to-hiring lag replicate in previous hiking cycles?

WHY THIS TEST MATTERS
hiring_slowdown.py found that sector employment growth tracks the Federal Funds
Rate with a lag peaking at 8-9 quarters, and used that to argue the 2024-2025
hiring slowdown is monetary. But that lag was found by scanning 0-12 quarters on
a sample that INCLUDES the very episode it explains. That is circular, and a lag
scan that tries 13 candidates and reports the best one can overfit.

The fix is out-of-sample validation: estimate the lag on historical data that
excludes 2022-2026 entirely, and see whether the same lag appears. Employment
data for Construction, Manufacturing and Wholesale runs back to 1939 and
FEDFUNDS to 1954, so there is plenty of history to test against.

RESULTS

  CONFIRMED for the modern era. On 1986-2019 data, which contains none of the
  episode being explained, the physical-sector lag profile peaks at exactly
  9 quarters (r = -0.366, p < 0.0001) with the same smooth monotonic shape:
  it climbs steadily from +0.19 at lag 0, crosses zero around lag 3, and
  decays after 9. The 9-sector aggregate on pre-2020 data peaks at 10 quarters
  (r = -0.349, p = 0.0001). Both bracket the 8-9 quarters found in-sample.

  NOT a structural constant. The same estimate on 1955-1985 peaks at only
  4 quarters (r = -0.479), and on the full pre-2000 sample at 4 quarters.
  The transmission lag appears to have roughly doubled between the mid-century
  and the modern era. So "rates hit hiring after about two years" is a fact
  about the recent economy, not a timeless one.

  The naive event study does NOT work, and is reported here so the failure is
  visible. Measuring the gap from each hiking cycle's start to the following
  trough in physical-sector hiring gives a median of 13 quarters but a range of
  0 to 20, because several troughs are the NEXT recession rather than a rate
  effect: the 2004-06 cycle's trough lands in 2009 (GFC) and the 2015-18
  cycle's in 2020 (COVID). Cycle-by-cycle event studies cannot separate the
  rate channel from whatever recession followed.

WHAT THIS BUYS
The lag used to explain 2024-2025 was not fitted to 2024-2025. It reproduces on
three decades of independent data. That answers the overfitting objection
directly. It does not make the relationship causal, and the era-dependence
should be reported alongside it.

Reads FRED CSVs from ../FRED-Data/. Writes historical_lag_validation.png.
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
MAXLAG   = 16

# Hiking cycles, dated from the first sustained increase to the peak rate.
CYCLES = {
    "1972-74": ("1972-01-01", "1974-07-01"),
    "1977-80": ("1977-01-01", "1980-04-01"),
    "1983-84": ("1983-04-01", "1984-10-01"),
    "1988-89": ("1988-01-01", "1989-04-01"),
    "1994-95": ("1994-01-01", "1995-04-01"),
    "1999-00": ("1999-07-01", "2000-07-01"),
    "2004-06": ("2004-07-01", "2006-07-01"),
    "2015-18": ("2015-10-01", "2018-10-01"),
    "2022-23": ("2022-04-01", "2023-07-01"),
}
# Cycles whose following hiring trough is contaminated by an unrelated recession.
CONTAMINATED = {"2004-06": "trough is the 2009 GFC", "2015-18": "trough is COVID 2020"}

SAMPLES = {
    "1955-1985":                    ("1955-01-01", "1985-12-31"),
    "pre-2000":                     ("1955-01-01", "1999-12-31"),
    "1986-2019 (out-of-sample)":    ("1986-01-01", "2019-12-31"),
    "pre-2020 (out-of-sample)":     ("1955-01-01", "2019-12-31"),
    "full 1955-2026":               ("1955-01-01", "2026-12-31"),
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


ffr = load("fed_funds_rate_FEDFUNDS.csv").resample("QS").mean()

# Physical-sector composite: the three goods series that reach back to 1939.
phys = (load("construction_employment_USCONS.csv").resample("QS").mean()
        + load("manufacturing_employment_MANEMP.csv").resample("QS").mean()
        + load("wholesale_trade_employment_USWTRADE.csv").resample("QS").mean()).dropna()
g_phys = (phys.pct_change(4) * 100).dropna()


def lag_profile(series, start, end):
    out = []
    for L in range(0, MAXLAG + 1):
        j = pd.DataFrame({"g": series, "f": ffr.shift(L)}).dropna()
        j = j[(j.index >= start) & (j.index <= end)]
        j = j[~j.index.isin(COVID_Q)]
        if len(j) < 20:
            out.append((L, np.nan, np.nan, len(j)))
            continue
        r, p = sp_stats.pearsonr(j["f"], j["g"])
        out.append((L, r, p, len(j)))
    return pd.DataFrame(out, columns=["lag", "r", "p", "n"])


print("=" * 86)
print("HISTORICAL VALIDATION: does the ~9 quarter rate-to-hiring lag replicate?")
print("=" * 86)

print("\n[1] Peak lag by sample period (physical-sector composite)\n")
print(f"  {'sample':<30}{'peak lag':>10}{'r':>9}{'p':>10}{'n':>6}")
profiles = {}
for lbl, (a, b) in SAMPLES.items():
    prof = lag_profile(g_phys, a, b).dropna(subset=["r"])
    profiles[lbl] = prof
    best = prof.iloc[prof["r"].abs().idxmax()]
    print(f"  {lbl:<30}{int(best['lag']):>8}q{best['r']:>+9.3f}{best['p']:>10.4f}{int(best['n']):>6}")

print("\n[2] Full lag profile, 1986-2019 (contains none of the 2022-2026 episode)\n")
oos = profiles["1986-2019 (out-of-sample)"]
print(f"  {'lag':>5}{'r':>9}{'p':>10}")
for _, row in oos.iterrows():
    star = "   <- peak" if int(row["lag"]) == int(oos.iloc[oos["r"].abs().idxmax()]["lag"]) else ""
    print(f"  {int(row['lag']):>4}q{row['r']:>+9.3f}{row['p']:>10.4f}{star}")

print("\n[3] The naive event study, and why it fails\n")
print(f"  {'cycle':<10}{'hike start':>13}{'FFR rise':>10}{'hiring trough':>15}{'lag':>7}   note")
ev = []
for name, (a, b) in CYCLES.items():
    a, b = pd.Timestamp(a), pd.Timestamp(b)
    seg = ffr.loc[a:b]
    win = g_phys.loc[a:a + pd.DateOffset(years=5)]
    if len(seg) == 0 or len(win) == 0:
        continue
    tro = win.idxmin()
    lag = round((tro - a).days / 91.3125)
    ev.append(dict(cycle=name, lag=lag, rise=seg.max() - seg.min(), trough=tro))
    note = CONTAMINATED.get(name, "")
    print(f"  {name:<10}{str(a.date()):>13}{seg.max()-seg.min():>+10.2f}"
          f"{str(tro.date()):>15}{lag:>6}q   {note}")
EV = pd.DataFrame(ev)
clean = EV[~EV.cycle.isin(CONTAMINATED)]
print(f"\n  all cycles      : median {EV.lag.median():.0f}q, range {EV.lag.min()}-{EV.lag.max()}q")
print(f"  dropping the two contaminated: median {clean.lag.median():.0f}q, "
      f"range {clean.lag.min()}-{clean.lag.max()}q")
print("  The spread is too wide to be informative. Cycle-level event studies cannot")
print("  separate the rate channel from the recession that happened to follow.")

# ---- chart -------------------------------------------------------------------
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16.5, 6.3))

# panel 1: out-of-sample profile vs in-sample
ax1.axhline(0, color="black", lw=1.0, ls="--")
ax1.axvspan(8, 9, color="gold", alpha=0.22, label="the 8-9q lag used in the main finding")
insample = lag_profile(g_phys, "2006-01-01", "2026-12-31")
ax1.plot(oos["lag"], oos["r"], marker="o", lw=2.4, color="#1f4e79",
         label="1986-2019 (out-of-sample)")
ax1.plot(insample["lag"], insample["r"], marker="s", lw=2.0, color="#c0392b", alpha=0.85,
         label="2006-2026 (in-sample, the original)")
ax1.set_xlabel("lag on the Fed funds rate (quarters)", fontsize=10)
ax1.set_ylabel("corr(physical-sector hiring growth, FFR)", fontsize=10)
ax1.set_title("The lag replicates out-of-sample\n"
              "1986-2019 peaks at 9 quarters, same smooth shape",
              fontsize=11.5, fontweight="bold")
ax1.legend(fontsize=8.5, loc="lower left"); ax1.grid(True, ls="--", alpha=0.35)

# panel 2: peak lag by era
era_order = ["1955-1985", "pre-2000", "1986-2019 (out-of-sample)",
             "pre-2020 (out-of-sample)", "full 1955-2026"]
peaks = [int(profiles[e].iloc[profiles[e]["r"].abs().idxmax()]["lag"]) for e in era_order]
cols = ["#9bb7d4", "#9bb7d4", "#1f4e79", "#1f4e79", "#c0392b"]
ax2.barh(np.arange(len(era_order)), peaks, color=cols)
ax2.axvline(9, color="gold", lw=2.4, label="the 8-9q finding")
ax2.set_yticks(np.arange(len(era_order)))
ax2.set_yticklabels([e.replace(" (out-of-sample)", "\n(out-of-sample)") for e in era_order], fontsize=9)
ax2.set_xlabel("peak lag (quarters)", fontsize=10)
ax2.set_title("But the lag is era-dependent, not a constant\n"
              "It roughly doubled between mid-century and the modern era",
              fontsize=11.5, fontweight="bold")
ax2.legend(fontsize=8.5, loc="lower right"); ax2.grid(True, axis="x", ls="--", alpha=0.35)

fig.suptitle("Out-of-sample validation: the rate-to-hiring lag was not fitted to the episode it explains",
             fontsize=13, fontweight="bold", y=1.02)
plt.tight_layout()
out = os.path.join(HERE, "historical_lag_validation.png")
plt.savefig(out, dpi=150, bbox_inches="tight")
print(f"\nChart saved: {out}")
