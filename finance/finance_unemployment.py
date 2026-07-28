"""
finance_unemployment.py
Financial Activities unemployment rate, on its own.

This is the plain picture that motivates the whole finance sub-analysis: the
unemployment rate is pinned near its floor and barely moves, which is exactly
why an unemployment-based Okun test cannot see anything happening in Finance
and why the employment-elasticity chart exists alongside it.

Reads from ../FRED-Data/. Writes finance_unemployment.png.
"""

import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE     = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(HERE, "..", "FRED-Data") + os.sep
COVID    = (pd.Timestamp("2020-04-01"), pd.Timestamp("2021-10-01"))
AI_CUT   = pd.Timestamp("2022-10-01")


def load(filename, label):
    df = pd.read_csv(os.path.join(DATA_DIR, filename))
    df.columns = [c.strip() for c in df.columns]
    df[df.columns[0]] = pd.to_datetime(df[df.columns[0]])
    df = df.set_index(df.columns[0])
    df[df.columns[0]] = pd.to_numeric(df[df.columns[0]], errors="coerce")
    return df.iloc[:, 0].rename(label)


u = load("financial_activities_unemployment_rate_LNU04032238.csv", "u").resample("QS").mean().dropna()

# floor reference: the low, stable band it sits in outside recessions
floor_band = u[(u.index >= "2013-01-01") & (u.index < "2020-01-01")]
lo, hi = floor_band.quantile(0.10), floor_band.quantile(0.90)

fig, ax = plt.subplots(figsize=(12, 5.5))
ax.axvspan(*COVID, color="crimson", alpha=0.10, label="COVID")
ax.axvspan(AI_CUT, u.index[-1], color="gold", alpha=0.10, label="post-Q4 2022")
ax.axhspan(lo, hi, color="steelblue", alpha=0.10, label=f"2013-2019 floor band ({lo:.1f}-{hi:.1f}%)")
ax.plot(u.index, u.values, color="#1f4e79", linewidth=2.2)
ax.axhline(u[u.index >= "2013-01-01"].min(), color="gray", linewidth=1.0, linestyle=":",
           label=f"post-2013 floor = {u[u.index>='2013-01-01'].min():.1f}%")

ax.set_ylabel("Unemployment rate (%)", fontsize=11)
ax.set_xlabel("Quarter", fontsize=11)
ax.set_title("Financial Activities unemployment rate\n"
             "Welded to a ~2% floor since 2013 (outside the COVID spike): nothing for an Okun test to read",
             fontsize=12, fontweight="bold")
ax.set_ylim(0, max(u.max() * 1.1, 6))
ax.legend(fontsize=9, loc="upper right")
ax.grid(True, linestyle="--", alpha=0.35)
plt.tight_layout()
plt.savefig(os.path.join(HERE, "finance_unemployment.png"), dpi=150, bbox_inches="tight")

print("Financial Activities unemployment rate")
print(f"  2013-2019 mean: {floor_band.mean():.2f}%   std: {floor_band.std():.2f}")
print(f"  2023-2025 mean: {u[u.index>='2023-01-01'].mean():.2f}%   std: {u[u.index>='2023-01-01'].std():.2f}")
covid_peak = u[(u.index >= COVID[0]) & (u.index <= COVID[1])].max()
print(f"  COVID-window peak: {covid_peak:.2f}%   (series peak {u.max():.2f}% was the 2010 recession)")
print("Chart saved: finance_unemployment.png")
