"""
does_okun_break_in_every_hike.py
Does Okun's Law break during every rate-hiking cycle? No. It never did before 1994.

WHY THIS EXISTS
The deflating objection to this sub-project, in its sharpest form: the goods
sectors' Okun inversion in 2024-2025 is unremarkable because Okun's Law comes
apart in every monetary tightening. If that is true, the long rate lag documented
in this folder is an elaborate answer to a non-puzzle.

A companion file, `does_okun_break_in_recessions.py`, already tested the
RECESSION version of this objection at sector level and found the opposite: in
the GFC and COVID, not one of 51 sector-quarters showed a positive correlation.
Okun works BETTER in downturns, because a sharp shock drives output and
unemployment hard in opposite directions at once.

Hiking cycles are a different question, and this file tests that one. It has to
be done on the aggregate, because BEA real value added by industry begins in 2005
and only one full hiking cycle has occurred since.

METHOD
Rolling 12-quarter correlation between year-over-year real GDP growth and the
year-over-year change in the unemployment rate. Okun working means a NEGATIVE
correlation. "Breaking" means it turns positive. For each of the nine hiking
cycles since 1954, the maximum the correlation reached in the four years from the
first hike. Full-history GDPC1 and UNRATE are used rather than the repo's
2000-onward copies, which is what makes nine cycles testable instead of six.

RESULT: FOUR OF NINE, AND THE SPLIT IS BY ERA, NOT BY SIZE

    cycle      FFR rise   peak Okun corr   broke?
    1972-74      +7.01%          -0.659      no
    1977-80      +5.41%          -0.384      no
    1983-84      +3.47%          -0.800      no
    1988-89      +3.06%          -0.134      no
    1994-95      +2.81%          +0.151     YES
    1999-00      +3.02%          +0.320     YES
    2004-06      +3.81%          +0.360     YES
    2015-18      +1.04%          -0.163      no
    2022-23      +4.56%          +0.548     YES

Every cycle from 1994 onward broke Okun except 2015-18, which was by far the
smallest hike in the sample (+1.04pp). No cycle before 1994 broke it, including
the two largest tightenings on record (+7.01pp and +5.41pp). Hike size does not
explain the pattern; across all nine cycles the correlation between the size of
the tightening and the peak Okun correlation is NEGATIVE (r = -0.30, p = 0.44).

So the objection is half right, and the half that is right is the important half.
"Okun always breaks when the Fed hikes" is false as stated. "Okun has broken in
every meaningful hiking cycle of the modern era, and 2022-23 is the fourth" is
true, and it does deflate the 2024-2025 inversion considerably.

The era boundary is itself informative and lines up with two things already in
this project: the rate-to-hiring transmission lag roughly doubled between the
mid-century and the modern era (4 quarters pre-1986, 8-9 quarters after, see
`historical_lag_validation.py`), and the jobless-recovery era in the US labor
economics literature is conventionally dated to the 1990-91 recession. A longer
lag between the policy shock and the labor-market response is exactly what would
desynchronize output from unemployment enough to flip a contemporaneous
correlation, so the modern-era clustering is what the rate story predicts.

Reads FRED CSVs from ../FRED-Data/. Writes does_okun_break_in_every_hike.png.
"""

import os
import glob
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats as sp

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "FRED-Data") + os.sep
COVID = pd.date_range("2020-04-01", "2021-10-01", freq="QS")
WINDOW = 12
HORIZON = 4          # years after the first hike to look for a break

# first sustained increase of each cycle, same dating as historical_lag_validation.py
CYCLES = {"1972-74": "1972-01-01", "1977-80": "1977-01-01", "1983-84": "1983-04-01",
          "1988-89": "1988-01-01", "1994-95": "1994-01-01", "1999-00": "1999-07-01",
          "2004-06": "2004-07-01", "2015-18": "2015-10-01", "2022-23": "2022-04-01"}


def load(f):
    p = DATA + f if os.path.exists(DATA + f) else (glob.glob(DATA + "*" + f) +
                                                   glob.glob(DATA + "*" + f + "*"))[0]
    d = pd.read_csv(p)
    d.columns = [c.strip() for c in d.columns]
    d[d.columns[0]] = pd.to_datetime(d[d.columns[0]])
    d = d.set_index(d.columns[0])
    return pd.to_numeric(d.iloc[:, 0], errors="coerce").dropna()


gdp = load("real_gdp_full_history_GDPC1.csv")
unr = load("unemployment_rate_full_history_UNRATE.csv").resample("QS").mean()
ffr = load("fed_funds_rate_FEDFUNDS.csv").resample("QS").mean()

d = pd.concat([(gdp.pct_change(4) * 100).rename("y"), unr.diff(4).rename("u")], axis=1).dropna()
d = d[~d.index.isin(COVID)]
roll = d["y"].rolling(WINDOW).corr(d["u"]).dropna()

print("=" * 96)
print("DOES OKUN'S LAW BREAK IN EVERY RATE-HIKING CYCLE?")
print("=" * 96)
print(f"\nRolling {WINDOW}-quarter corr(real GDP growth, change in unemployment). Normally")
print("strongly negative; 'breaking' means turning positive. Sample "
      f"{roll.index[0].date()} to {roll.index[-1].date()}.")
print(f"Unconditional: mean {roll.mean():+.3f}, sd {roll.std():.3f}, "
      f"{100*(roll>0).mean():.0f}% of all quarters positive.\n")

print(f"{'cycle':<10}{'FFR rise':>10}{'peak Okun corr':>16}{'when':>12}{'broke?':>9}")
rows = []
for c, s in CYCLES.items():
    a = pd.Timestamp(s)
    seg = ffr.loc[a:a + pd.DateOffset(years=2)]
    w = roll.loc[a:a + pd.DateOffset(years=HORIZON)]
    if not len(w):
        continue
    rise = seg.max() - seg.min()
    rows.append(dict(cycle=c, rise=rise, mx=w.max(), when=w.idxmax(), broke=w.max() > 0,
                     era="modern" if int(c[:4]) >= 1994 else "pre-1994"))
    print(f"{c:<10}{rise:>+9.2f}%{w.max():>+16.3f}{str(w.idxmax().date()):>12}"
          f"{('YES' if w.max() > 0 else 'no'):>9}")
R = pd.DataFrame(rows)

r_, p_ = sp.pearsonr(R.rise, R.mx)
print(f"\n  Broke in {int(R.broke.sum())} of {len(R)} cycles.")
print(f"  Size of tightening vs peak Okun correlation: r = {r_:+.3f}, p = {p_:.3f}. "
      f"Size does not explain it.")
for era, sub in R.groupby("era"):
    print(f"  {era:<9}: {int(sub.broke.sum())} of {len(sub)} broke, "
          f"mean peak {sub.mx.mean():+.3f}, mean hike {sub.rise.mean():+.2f}pp")
mod, pre = R[R.era == "modern"], R[R.era == "pre-1994"]
print(f"\n  The pre-1994 cycles average a LARGER hike ({pre.rise.mean():+.2f}pp against "
      f"{mod.rise.mean():+.2f}pp) and")
print("  never break Okun. The split is by era, not by magnitude. 'Okun always breaks when")
print("  the Fed hikes' is false; 'Okun has broken in every meaningful modern hiking cycle,")
print("  and 2022-23 is the fourth' is true, and that is the version that deflates the")
print("  2024-2025 sector inversion.")

# ---- chart -------------------------------------------------------------------
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16.5, 6.3))

ax1.axhline(0, color="black", lw=1.2)
ax1.plot(roll.index, roll.values, lw=1.6, color="#1f4e79")
for c, s in CYCLES.items():
    a = pd.Timestamp(s)
    ax1.axvspan(a, a + pd.DateOffset(years=2), color="gold", alpha=0.25)
ax1.set_ylabel(f"rolling {WINDOW}q corr(GDP growth, Δunemployment)", fontsize=10)
ax1.set_title("Shaded = hiking cycles. Okun turns positive only\nin the modern ones",
              fontsize=11.5, fontweight="bold")
ax1.grid(True, ls="--", alpha=0.35)

col = ["#c0392b" if b else "#95a5a6" for b in R.broke]
ax2.scatter(R.rise, R.mx, s=150, c=col, edgecolors="white", linewidths=1.3, zorder=3)
for _, x in R.iterrows():
    ax2.annotate(x.cycle, (x.rise, x.mx), xytext=(7, 4), textcoords="offset points", fontsize=8.5)
ax2.axhline(0, color="black", lw=1.2)
ax2.set_xlabel("size of the tightening (pp)", fontsize=10)
ax2.set_ylabel("peak Okun correlation within 4 years", fontsize=10)
ax2.set_title("Bigger hikes do not break Okun harder\nRed = broke. The two largest hikes did not.",
              fontsize=11.5, fontweight="bold")
ax2.grid(True, ls="--", alpha=0.35)

fig.suptitle("Okun's Law and monetary tightening: four of nine cycles, all of them modern",
             fontsize=13, fontweight="bold", y=1.02)
plt.tight_layout()
plt.savefig(os.path.join(HERE, "does_okun_break_in_every_hike.png"), dpi=150, bbox_inches="tight")
print("\nChart saved: does_okun_break_in_every_hike.png")
