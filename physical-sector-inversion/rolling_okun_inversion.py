"""
rolling_okun_inversion.py
Physical-sector Okun inversion — COVID INCLUDED.

This is a SEPARATE analysis from the AI-exposure work in the repository root.
It does not use the AI cutoff or exposure scores. It asks one narrow question
about three low-AI, goods-producing / rate-sensitive sectors:

    Construction, Manufacturing, Transportation & Utilities

    When did each sector's Okun relationship (output growth vs. change in
    unemployment) actually invert, and how unusual is that inversion?

KEY DIFFERENCE FROM THE ROOT ANALYSIS: COVID is INCLUDED here, not excluded.
The point of this analysis is precisely to see the full path through the
pandemic. With COVID in, the three sectors held Okun's law hardest during
2020-2021 (output and jobs collapsed together, rolling r near -0.9), and only
inverted in 2024-2025. Excluding COVID hides that COVID itself was the most
Okun-consistent episode in the sample.

Method:
  - Difference form: ΔU = beta * %ΔY, both as 4-quarter (YoY) differences to
    cancel seasonality in the not-seasonally-adjusted unemployment series.
  - YoY differences computed on the intact series (no rows dropped).
  - 12-quarter rolling window for beta and the correlation r.
  - Probability test: how likely is the recent peak correlation under the
    distribution of the sector's own pre-2022 rolling correlations (the same
    normal-approximation test used in the aggregate root analysis). The
    pre-2022 baseline itself includes the COVID windows.

Run from anywhere: `python3 rolling_okun_inversion.py`
Reads FRED CSVs from ../FRED-Data/ relative to this file.
"""

import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats as sp_stats

HERE     = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(HERE, "..", "FRED-Data") + os.sep
WINDOW   = 12
REF_CUT  = pd.Timestamp("2022-10-01")   # baseline / recent split for the prob. test
COVID    = (pd.Timestamp("2020-04-01"), pd.Timestamp("2021-10-01"))  # for shading only

# output_file, unemployment_file, AIIE score (context only, not used in the test)
SECTORS = {
    "Construction":                ("CnstGDP.csv", "ConstUrate .csv", -0.997),
    "Manufacturing":               ("MnfctGDP.csv", "MnfctUrate.csv",  -0.484),
    "Transportation & Utilities":  ("RVAT.csv",     "LNU04032236.csv", -0.342),
}


def load_series(filename, label):
    df = pd.read_csv(DATA_DIR + filename, parse_dates=["observation_date"])
    df = df.set_index("observation_date")
    col = df.columns[0]
    df[col] = pd.to_numeric(df[col], errors="coerce")
    return df[col].rename(label)


def build_df(output_file, unemp_file):
    """YoY difference-form Okun variables. COVID is KEPT."""
    y = load_series(output_file, "output")
    u = load_series(unemp_file, "unemp").resample("QS").mean()
    df = pd.DataFrame({"output": y, "unemp": u}).dropna()
    df["pct_dy"]  = df["output"].pct_change(periods=4) * 100
    df["delta_u"] = df["unemp"].diff(periods=4)
    return df.dropna(subset=["pct_dy", "delta_u"])


def rolling(df):
    idx = df.index.tolist()
    dates, slopes, rs = [], [], []
    for i in range(WINDOW, len(idx) + 1):
        w = df.iloc[i - WINDOW : i]
        x, y = w["pct_dy"].values, w["delta_u"].values
        if np.std(x) < 1e-9:
            continue
        dates.append(idx[i - 1])
        slopes.append(np.polyfit(x, y, 1)[0])
        rs.append(np.corrcoef(x, y)[0, 1])
    return pd.DataFrame({"slope": slopes, "r": rs}, index=dates)


def inversion_onset(roll):
    """First quarter where rolling r turns positive and mostly stays positive."""
    for dt in roll.index:
        if roll.loc[dt, "r"] > 0 and (roll.loc[dt:, "r"] > 0).mean() > 0.7:
            return dt
    return None


def analyze(name, output_file, unemp_file):
    df   = build_df(output_file, unemp_file)
    roll = rolling(df)

    pre_r = roll[roll.index < REF_CUT]["r"]          # baseline (COVID included)
    hist_mean, hist_std = pre_r.mean(), pre_r.std()

    peak_r  = roll["r"].max()
    peak_dt = roll["r"].idxmax()
    p_peak  = 1 - sp_stats.norm.cdf(peak_r, loc=hist_mean, scale=hist_std)

    covid_r = roll.loc[COVID[0]:COVID[1], "r"]

    d_pre  = df[df.index < REF_CUT]
    d_post = df[df.index >= REF_CUT]
    b_pre  = np.polyfit(d_pre["pct_dy"],  d_pre["delta_u"],  1)[0]
    b_post = np.polyfit(d_post["pct_dy"], d_post["delta_u"], 1)[0]

    return {
        "name": name, "df": df, "roll": roll,
        "hist_mean": hist_mean, "hist_std": hist_std,
        "peak_r": peak_r, "peak_dt": peak_dt, "p_peak": p_peak,
        "onset": inversion_onset(roll),
        "covid_r_min": covid_r.min(), "covid_r_max": covid_r.max(),
        "b_pre": b_pre, "b_post": b_post, "d_beta": b_post - b_pre,
    }


results = {name: analyze(name, of, uf) for name, (of, uf, _) in SECTORS.items()}

# ---- console report ---------------------------------------------------------
print("=" * 80)
print("PHYSICAL-SECTOR OKUN INVERSION  (COVID INCLUDED)")
print("=" * 80)
for name, (_, _, aiie) in SECTORS.items():
    r = results[name]
    onset = r["onset"].date() if r["onset"] is not None else "n/a"
    print(f"\n{name}  (AIIE = {aiie:+.2f})")
    print(f"  held through COVID:  rolling r {r['covid_r_min']:+.2f} to {r['covid_r_max']:+.2f}")
    print(f"  inversion onset:     {onset}")
    print(f"  single regression:   beta_pre={r['b_pre']:+.3f}  beta_post={r['b_post']:+.3f}  "
          f"delta_beta={r['d_beta']:+.3f}")
    print(f"  pre-2022 rolling r:  mean={r['hist_mean']:+.3f}  std={r['hist_std']:.3f}")
    print(f"  peak r:              {r['peak_r']:+.3f} ({r['peak_dt'].date()})  "
          f"p(r >= peak) = {r['p_peak']:.4f}")

# ---- chart: one clean panel per sector, COVID shaded ------------------------
order = list(SECTORS.keys())
fig, axes = plt.subplots(len(order), 1, figsize=(12, 3.8 * len(order)), sharex=True)

for ax, name in zip(axes, order):
    r    = results[name]
    roll = r["roll"]
    aiie = SECTORS[name][2]

    # COVID shading (kept in the data, shaded only for context)
    ax.axvspan(COVID[0], COVID[1], color="crimson", alpha=0.10, label="COVID (kept in data)")
    ax.plot(roll.index, roll["r"],     color="firebrick", linewidth=2.3, label="Rolling correlation r")
    ax.plot(roll.index, roll["slope"], color="steelblue", linewidth=1.4, alpha=0.85,
            label="Rolling Okun beta")
    ax.axhline(0, color="black", linewidth=0.9, linestyle="--")
    ax.axhline(r["hist_mean"], color="gray", linewidth=1.0, linestyle=":",
               label=f"pre-2022 mean r = {r['hist_mean']:+.2f}")
    if r["onset"] is not None:
        ax.axvline(r["onset"], color="darkgreen", linewidth=1.4, linestyle="-.",
                   label=f"inversion onset {r['onset'].date()}")

    ann = (f"Δβ = {r['d_beta']:+.2f}\n"
           f"peak r = {r['peak_r']:+.2f}\n"
           f"p(r ≥ peak) = {r['p_peak']:.3f}")
    ax.text(0.015, 0.04, ann, transform=ax.transAxes, fontsize=9, va="bottom",
            bbox=dict(boxstyle="round,pad=0.4", fc="white", alpha=0.85))

    ax.set_ylim(-1.05, 1.05)
    ax.set_ylabel("coefficient / r", fontsize=10)
    ax.set_title(f"{name}   (AIIE = {aiie:+.2f})", fontsize=12, fontweight="bold")
    ax.legend(fontsize=8, loc="upper left", ncol=2)
    ax.grid(True, linestyle="--", alpha=0.35)

axes[-1].set_xlabel("Quarter (end of 12-quarter window)", fontsize=11)
fig.suptitle(
    "Physical-Sector Okun Inversion (COVID Included)\n"
    "All three held the law hardest during COVID, then inverted in 2024-2025",
    fontsize=13, fontweight="bold", y=1.004)
plt.tight_layout()
out = os.path.join(HERE, "rolling_okun_inversion.png")
plt.savefig(out, dpi=150, bbox_inches="tight")
print(f"\nChart saved: {out}")
