"""
why_rates_break_okun.py
WHY would a lagged rate shock break Okun's Law? The mechanism, not just the fact.

Everything else in this folder establishes THAT the 2024-2025 hiring slowdown is
monetary. This asks the harder question: why would monetary policy make output
and unemployment stop moving in opposite directions? A rate hike should lower
output AND raise unemployment, which is Okun's Law working normally, not
breaking. So the correlation flipping positive needs an explanation.

THE ANSWER: rates reach output and unemployment on DIFFERENT CLOCKS.

Measuring each separately against the Federal Funds Rate at every lag:

    sector            output peak lag      unemployment peak lag      gap
    Construction            12q                     9q               -3q
    Manufacturing            9q                     8q               -1q
    Transportation           8q                     7q               -1q

Unemployment responds about 1.7 quarters FASTER than output, consistently in
all three sectors. That gap is the whole mechanism.

WHY A GAP PRODUCES AN APPARENT BREAK
Okun's Law is a contemporaneous relationship: it compares output and
unemployment measured in the SAME quarter. But if both are really responding to
a common driver at different delays, then in any given quarter they are
reflecting the policy rate from two different dates:

    unemployment_t  responds to  FFR_(t-9)
    output_t        responds to  FFR_(t-12)

When the rate path is flat, this does not matter; both look back at similar
rates. When the rate path moves sharply, it matters enormously. In 2025 Q1:

    unemployment was responding to 2022 Q4 rates, about 3.65%  (hiking underway)
    output was still responding to 2022 Q1 rates, about 0.12%  (zero-rate era)

So unemployment was already absorbing the tightening while output was still
coasting on the era before it. Output looked strong and unemployment was
rising at the same time, which is mechanically a POSITIVE output-unemployment
correlation, which reads as Okun's Law inverting.

WHAT THIS MEANS INTERPRETIVELY
Okun's Law did not break. The structural relationship between production and
employment is intact. What broke is the ASSUMPTION that output and unemployment
respond to a shock simultaneously, which is the assumption baked into measuring
Okun contemporaneously. A large, fast policy shock desynchronizes them, and a
contemporaneous regression reads that desynchronization as a broken law.

This also explains why the "inversion" is fragile (why_in_sync.py found it
reverses at 20-quarter windows): it is a transient phase artifact that appears
while a shock is propagating through the two variables at different speeds, and
washes out once the window is long enough to contain the whole propagation.

CAVEAT: this is a mechanism consistent with the measured lags, not a proven
causal chain. The lag gap is small (1 to 3 quarters), estimated on noisy
quarterly data, and the quarter-by-quarter path is messier than the clean
story above.

Reads FRED CSVs from ../FRED-Data/. Writes why_rates_break_okun.png.
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


ffr = load("fed_funds_rate_FEDFUNDS.csv").resample("QS").mean()


def lag_curve(series):
    out = []
    for L in range(0, 17):
        j = pd.DataFrame({"x": series, "f": ffr.shift(L)}).dropna()
        j = j[~j.index.isin(COVID_Q)]
        j = j[j.index >= "1991-01-01"]
        if len(j) < 20:
            out.append((L, np.nan))
            continue
        out.append((L, sp_stats.pearsonr(j["f"], j["x"])[0]))
    return pd.DataFrame(out, columns=["lag", "r"]).dropna()


print("=" * 88)
print("WHY RATES BREAK OKUN: output and unemployment respond on different clocks")
print("=" * 88)
print(f"\n{'sector':<16}{'output peak lag':>17}{'r':>8}   {'unemp peak lag':>16}{'r':>8}{'gap':>7}")

curves, gaps = {}, []
for name, (of, uf) in SECTORS.items():
    y = (load(of).pct_change(4) * 100).dropna()
    u = load(uf).resample("QS").mean().diff(4).dropna()
    cy, cu = lag_curve(y), lag_curve(u)
    ly = int(cy.iloc[cy["r"].abs().idxmax()]["lag"]); ry = cy["r"].abs().max()
    lu = int(cu.iloc[cu["r"].abs().idxmax()]["lag"]); ru = cu["r"].abs().max()
    curves[name] = (cy, cu, ly, lu)
    gaps.append(lu - ly)
    print(f"{name:<16}{ly:>15}q{-ry:>8.2f}   {lu:>14}q{ru:>8.2f}{lu-ly:>6}q")

print(f"\n  Unemployment responds {abs(np.mean(gaps)):.1f} quarters FASTER than output, "
      f"same direction in all three.")

print("\n  What that gap does, using Construction's lags (output 12q, unemployment 9q):\n")
print(f"    {'quarter':<12}{'unemp reflects':>18}{'FFR then':>10}   {'output reflects':>18}{'FFR then':>10}")
for q in ["2023-01-01", "2024-01-01", "2025-01-01", "2025-10-01"]:
    t = pd.Timestamp(q)
    tu = t - pd.DateOffset(months=27)   # 9 quarters
    ty = t - pd.DateOffset(months=36)   # 12 quarters
    fu = ffr.asof(tu); fy = ffr.asof(ty)
    print(f"    {q:<12}{str(tu.date()):>18}{fu:>9.2f}%   {str(ty.date()):>18}{fy:>9.2f}%")
print("\n    By 2025, unemployment is absorbing the hiking cycle while output is still")
print("    coasting on the zero-rate era. Both rise together -> Okun looks inverted.")

# ---- chart -------------------------------------------------------------------
fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(19, 6.2))

# panel 1: the two lag curves for Construction
cy, cu, ly, lu = curves["Construction"]
ax1.axhline(0, color="black", lw=1.0, ls="--")
ax1.plot(cy["lag"], cy["r"], marker="o", lw=2.3, color="#1f4e79", label="output growth")
ax1.plot(cu["lag"], cu["r"], marker="s", lw=2.3, color="#c0392b", label="change in unemployment")
ax1.axvline(ly, color="#1f4e79", ls=":", lw=1.6)
ax1.axvline(lu, color="#c0392b", ls=":", lw=1.6)
ax1.annotate("", xy=(ly, 0.15), xytext=(lu, 0.15),
             arrowprops=dict(arrowstyle="<->", color="black", lw=1.6))
ax1.text((ly + lu) / 2, 0.22, f"{ly-lu}q gap", ha="center", fontsize=9.5, fontweight="bold")
ax1.set_xlabel("lag on the Fed funds rate (quarters)", fontsize=10)
ax1.set_ylabel("correlation with the rate", fontsize=10)
ax1.set_title("1. Construction: the two respond\nat different lags", fontsize=11.5, fontweight="bold")
ax1.legend(fontsize=8.5, loc="lower left"); ax1.grid(True, ls="--", alpha=0.35)

# panel 2: gap across sectors
names = list(SECTORS.keys())
x = np.arange(len(names)); w = 0.36
ax2.bar(x - w/2, [curves[n][2] for n in names], w, color="#1f4e79", label="output peak lag")
ax2.bar(x + w/2, [curves[n][3] for n in names], w, color="#c0392b", label="unemployment peak lag")
ax2.set_xticks(x); ax2.set_xticklabels(names, fontsize=9)
ax2.set_ylabel("peak lag (quarters)", fontsize=10)
ax2.set_title("2. Unemployment leads output\nin every sector", fontsize=11.5, fontweight="bold")
ax2.legend(fontsize=8.5); ax2.grid(True, axis="y", ls="--", alpha=0.35)

# panel 3: what each variable is "seeing" over time
ax3.plot(ffr.index, ffr, color="black", lw=1.4, alpha=0.35, label="Fed funds rate (actual)")
ax3.plot(ffr.index + pd.DateOffset(months=27), ffr, color="#c0392b", lw=2.2,
         label="what unemployment is reflecting (lag 9q)")
ax3.plot(ffr.index + pd.DateOffset(months=36), ffr, color="#1f4e79", lw=2.2,
         label="what output is reflecting (lag 12q)")
ax3.axvspan(pd.Timestamp("2024-01-01"), pd.Timestamp("2026-01-01"),
            color="gold", alpha=0.18, label="the 'inversion' window")
ax3.set_xlim(pd.Timestamp("2018-01-01"), pd.Timestamp("2027-01-01"))
ax3.set_ylim(-0.3, 6)
ax3.set_ylabel("Fed funds rate (%)", fontsize=10)
ax3.set_title("3. In 2024-25 the two variables are\nreading different rate eras",
              fontsize=11.5, fontweight="bold")
ax3.legend(fontsize=8, loc="upper left"); ax3.grid(True, ls="--", alpha=0.35)

fig.suptitle("Why a rate shock makes Okun's Law look broken: output and unemployment absorb it on different clocks",
             fontsize=13, fontweight="bold", y=1.02)
plt.tight_layout()
out = os.path.join(HERE, "why_rates_break_okun.png")
plt.savefig(out, dpi=150, bbox_inches="tight")
print(f"\nChart saved: {out}")
