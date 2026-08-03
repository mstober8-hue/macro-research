"""
standing_prediction.py
A falsifiable forward prediction from the timing mechanism.

why_rates_break_okun.py argues the goods-sector "Okun inversion" is a timing
artifact: unemployment absorbs a rate shock about 9 quarters out while output
absorbs it about 12 quarters out, so during a sharp rate move the two variables
are reflecting different rate eras and appear to move together.

That story implies a specific, computable quantity. At any quarter t:

    unemployment_t  is reflecting  FFR_(t-9)
    output_t        is reflecting  FFR_(t-12)

so the size of the desynchronization is simply

    DESYNC_t  =  FFR_(t-9) - FFR_(t-12)

When DESYNC is large and positive, unemployment is absorbing a much higher rate
than output is, and the measured Okun correlation should be pushed positive.
When DESYNC returns to zero the artifact should vanish. When DESYNC goes
negative the correlation should overshoot MORE negative than normal.

THE TEST THAT ALREADY PASSED
DESYNC peaks at +3.75pp in 2025 Q2. The observed rolling Okun correlation peaks
in 2025 Q2 in Construction (+0.816), Manufacturing (+0.677) and Transportation
(+0.602). All three, same quarter, matching the prediction exactly. Note this
was not fitted: the lags come from 1991-2019 data and the rate path is
exogenous, so the predicted peak date uses no information from the correlations.

THE STANDING PREDICTIONS (not yet testable, stated in advance)
Because DESYNC_t only needs rates through t-9, and rates are observed through
2026 Q2, the index is already known through 2028 Q3. That yields dated,
falsifiable predictions:

  1. The inversion keeps unwinding through 2026. DESYNC falls from +1.61
     (2025 Q4) to +0.34 (2026 Q2) to +0.07 (2026 Q3).
  2. By 2026 Q3-Q4 the artifact is gone. The goods sectors' rolling Okun
     correlations should be back near or below zero, i.e. the law "works" again.
  3. In 2027 the correlation should OVERSHOOT negative. DESYNC turns negative
     and reaches -1.00 in 2027 Q2, meaning output will then be reflecting
     higher rates than unemployment, which pushes the measured correlation
     further negative than its historical baseline.

Prediction 3 is the one worth watching. A structural-break story predicts
nothing of the kind; a timing-artifact story requires it. If the goods sectors'
Okun correlations simply return to their normal negative range and stop, the
mechanism is incomplete. If they overshoot below the pre-2022 baseline around
2027 and then return, the mechanism is doing real work.

CAVEATS
  - Uses Construction's lag pair (9, 12) for all sectors. Manufacturing and
    Transportation have shorter output lags (9q, 8q), so their DESYNC peaks
    should be slightly earlier and smaller. They were not, which the mechanism
    does not explain.
  - A 12-quarter rolling window imposes its own smoothing, so "the quarter" is
    only resolvable to within about a quarter either way.
  - Rates after 2026 Q2 are unknown, so predictions past 2028 Q3 would require
    assuming a policy path. Nothing here does that.

Reads FRED CSVs from ../FRED-Data/. Writes standing_prediction.png.
"""

import os
import glob
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE     = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(HERE, "..", "FRED-Data") + os.sep
LAG_U, LAG_Y = 9, 12     # unemployment and output response lags (Construction)
WINDOW = 12

SECTORS = {
    "Construction":   ("construction_value_added_RVAC.csv",
                       "construction_unemployment_rate_LNU04032231.csv", "#1f3b73"),
    "Manufacturing":  ("manufacturing_value_added_RVAMA.csv",
                       "manufacturing_unemployment_rate_LNU04032232.csv", "#3f7cac"),
    "Transportation": ("transportation_warehousing_value_added_RVAT.csv",
                       "transportation_utilities_unemployment_rate_LNU04032236.csv", "#6fb0d6"),
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

# Extend the calendar so DESYNC can be computed as far as observed rates allow.
cal = pd.date_range(ffr.index[0], ffr.index[-1] + pd.DateOffset(months=36), freq="QS")
f_ext = ffr.reindex(cal)
desync = (f_ext.shift(LAG_U) - f_ext.shift(LAG_Y)).dropna()

# Observed rolling Okun correlations
roll = {}
for name, (of, uf, _) in SECTORS.items():
    y = load(of); u = load(uf).resample("QS").mean()
    d = pd.DataFrame({"y": y, "u": u}).dropna()
    d["dy"] = d["y"].pct_change(4) * 100
    d["du"] = d["u"].diff(4)
    d = d.dropna()
    idx = d.index.tolist(); rs = {}
    for i in range(WINDOW, len(idx) + 1):
        w = d.iloc[i - WINDOW:i]
        if np.std(w["dy"]) > 1e-9:
            rs[idx[i - 1]] = np.corrcoef(w["dy"], w["du"])[0, 1]
    roll[name] = pd.Series(rs)
R = pd.DataFrame(roll)

print("=" * 84)
print("STANDING PREDICTION FROM THE TIMING MECHANISM")
print("=" * 84)
print(f"\nDESYNC_t = FFR(t-{LAG_U}) - FFR(t-{LAG_Y}).  Rates observed through "
      f"{ffr.index[-1].date()} ({ffr.iloc[-1]:.2f}%),")
print(f"so DESYNC is already determined through {desync.index[-1].date()}.\n")

print("[1] THE TEST THAT ALREADY PASSED\n")
pk = desync.loc["2023-01-01":"2026-12-31"].idxmax()
print(f"    predicted peak of the artifact : {pk.date()}  (DESYNC = {desync[pk]:+.2f}pp)")
for n in R.columns:
    s = R[n].dropna(); s = s[s.index >= "2023-01-01"]
    print(f"    observed peak, {n:<15}: {s.idxmax().date()}  (r = {s.max():+.3f})")
print("\n    Lags estimated on 1991-2019; rate path exogenous. The predicted date")
print("    uses no information from the correlation series.")

print("\n[2] WHERE THINGS STAND NOW\n")
print(f"    {'quarter':<12}{'DESYNC':>9}   " + "".join(f"{n[:12]:>14}" for n in R.columns))
for q in pd.date_range("2025-01-01", "2025-10-01", freq="QS"):
    vals = "".join(f"{R[n].get(q, np.nan):>14.3f}" for n in R.columns)
    print(f"    {str(q.date()):<12}{desync.get(q, np.nan):>+9.2f}   {vals}")

print("\n[3] STANDING PREDICTIONS, stated in advance\n")
fwd = desync.loc["2026-01-01":"2027-10-01"]
print(f"    {'quarter':<12}{'DESYNC':>9}   expectation")
for q, v in fwd.items():
    if v > 0.5:      exp = "still inverted, unwinding"
    elif v > -0.2:   exp = "artifact gone; correlation back near/below zero"
    else:            exp = "OVERSHOOT: correlation more negative than baseline"
    print(f"    {str(q.date()):<12}{v:>+9.2f}   {exp}")
print("\n    Prediction 3 (the 2027 overshoot) is the discriminating one. A structural")
print("    break predicts nothing like it; a timing artifact requires it.")

# ---- chart -------------------------------------------------------------------
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(13.5, 9.5), sharex=True,
                               gridspec_kw={"height_ratios": [1, 1.15]})
X0, X1 = pd.Timestamp("2018-01-01"), pd.Timestamp("2028-10-01")
NOW = R.dropna(how="all").index[-1]

# top: the desync index
ax1.axhline(0, color="black", lw=1.0)
d_plot = desync.loc[X0:X1]
ax1.fill_between(d_plot.index, 0, d_plot.values, where=d_plot.values > 0,
                 color="#c0392b", alpha=0.28, label="unemployment sees higher rates (pushes r positive)")
ax1.fill_between(d_plot.index, 0, d_plot.values, where=d_plot.values <= 0,
                 color="#1f4e79", alpha=0.28, label="output sees higher rates (pushes r negative)")
ax1.plot(d_plot.index, d_plot.values, color="black", lw=2.0)
ax1.axvline(NOW, color="black", ls="--", lw=1.5)
ax1.text(NOW, ax1.get_ylim()[1] * 0.86, "  data ends", fontsize=9)
ax1.annotate(f"predicted peak\n{pk.date()}", xy=(pk, desync[pk]), xytext=(-95, -8),
             textcoords="offset points", fontsize=9, fontweight="bold",
             arrowprops=dict(arrowstyle="->", color="black"))
ax1.set_ylabel("DESYNC  =  FFR(t−9) − FFR(t−12),  pp", fontsize=10)
ax1.set_title("The timing artifact, computed from the rate path alone\n"
              "Already determined through 2028 Q3, because it only needs rates up to t−9",
              fontsize=12, fontweight="bold")
ax1.legend(fontsize=8.5, loc="upper left"); ax1.grid(True, ls="--", alpha=0.35)

# bottom: observed correlations
ax2.axhline(0, color="black", lw=1.0)
for n, (_, _, c) in SECTORS.items():
    s = R[n].dropna(); s = s.loc[X0:]
    ax2.plot(s.index, s.values, color=c, lw=2.2, label=n)
ax2.axvline(NOW, color="black", ls="--", lw=1.5)
ax2.axvspan(NOW, X1, color="gold", alpha=0.13)
ax2.text(NOW + pd.DateOffset(months=4), 0.80, "PREDICTED:\nkeep falling through 2026,\n"
         "cross zero ~2026 Q3-Q4,\novershoot negative in 2027",
         fontsize=9.5, va="top",
         bbox=dict(boxstyle="round,pad=0.45", fc="white", alpha=0.9))
ax2.set_ylim(-1.02, 1.02)
ax2.set_xlim(X0, X1)
ax2.set_ylabel("rolling 12q Okun correlation", fontsize=10)
ax2.set_xlabel("quarter", fontsize=10)
ax2.set_title("Observed goods-sector Okun correlations, and what the mechanism commits to next",
              fontsize=12, fontweight="bold")
ax2.legend(fontsize=9, loc="lower left"); ax2.grid(True, ls="--", alpha=0.35)

fig.suptitle("A falsifiable forward test: if this is a timing artifact, the inversion must unwind and then overshoot",
             fontsize=13, fontweight="bold", y=0.985)
plt.tight_layout()
out = os.path.join(HERE, "standing_prediction.png")
plt.savefig(out, dpi=150, bbox_inches="tight")
print(f"\nChart saved: {out}")
