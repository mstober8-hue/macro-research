"""
productivity_acceleration.py
Is the RATE of productivity growth increasing, or just the level?

Productivity (output per worker) always rises, so its level says nothing. The
sharper question is whether its growth RATE is speeding up, especially recently.
This script measures year-over-year productivity growth for the two most
AI-exposed sectors (Financial Activities and Information) and decomposes each
sector's recent acceleration into its two possible sources:

    productivity growth  =  output growth  -  employment growth

That decomposition matters because a productivity acceleration can come from
two very different places:
  - output growing faster with flat hiring (an output/demand story), or
  - employment being cut while output holds up (a labor-shedding story).

Finding: both sectors show productivity growth roughly doubling in 2024-2025,
but for opposite reasons. Finance accelerates because output re-accelerates
while hiring freezes. Tech accelerates because it cuts jobs while output growth
actually slows. Only the tech pattern looks like "producing the same with fewer
people," the signature you would expect from labor-substituting AI.

Reads FRED CSVs from ../FRED-Data/. Writes productivity_acceleration.png.
"""

import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE     = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(HERE, "..", "FRED-Data") + os.sep

SECTORS = {
    "Financial Activities": ("FnceservcGDP.csv", "USFIRE.csv", "#1f4e79"),
    "Information (tech)":    ("RVAI.csv",         "USINFO.csv", "#c0392b"),
}
PERIODS = [("2013-2019", "2013-01-01", "2019-12-31"),
           ("2022-2023", "2022-01-01", "2023-12-31"),
           ("2024-2025", "2024-01-01", "2026-12-31")]


def load(f, l):
    d = pd.read_csv(os.path.join(DATA_DIR, f), parse_dates=["observation_date"]).set_index("observation_date")
    c = d.columns[0]
    d[c] = pd.to_numeric(d[c], errors="coerce")
    return d[c].rename(l)


def build(out_f, emp_f):
    out = load(out_f, "out")
    emp = load(emp_f, "emp").resample("QS").mean()
    df = pd.DataFrame({"out": out, "emp": emp}).dropna()
    df["prod_g"] = (df["out"] / df["emp"]).pct_change(4) * 100
    df["out_g"]  = df["out"].pct_change(4) * 100
    df["emp_g"]  = df["emp"].pct_change(4) * 100
    return df.dropna()


data = {name: build(of, ef) for name, (of, ef, _) in SECTORS.items()}

print("Productivity growth = output growth - employment growth (avg YoY, %/yr)\n")
print(f"  {'sector':<22}{'period':<12}{'prod':>8}{'output':>9}{'emp':>8}")
for name, df in data.items():
    for lbl, a, z in PERIODS:
        s = df.loc[a:z]
        print(f"  {name:<22}{lbl:<12}{s['prod_g'].mean():>+8.2f}{s['out_g'].mean():>+9.2f}{s['emp_g'].mean():>+8.2f}")
    print()

# ---- chart -------------------------------------------------------------------
fig, (axL, axR) = plt.subplots(1, 2, figsize=(17, 6.5), gridspec_kw={"width_ratios": [1.25, 1]})

# left: rolling 4q-smoothed YoY productivity growth over time
for name, (of, ef, color) in SECTORS.items():
    df = data[name]
    sm = df["prod_g"].rolling(4, min_periods=2).mean()
    axL.plot(df.index, sm, color=color, lw=2.3, label=name)
axL.axhline(0, color="black", lw=0.8, ls="--")
axL.axvspan(pd.Timestamp("2024-01-01"), data["Financial Activities"].index[-1],
            color="gold", alpha=0.12, label="2024-2025")
axL.set_ylabel("YoY productivity growth (%, 4q smoothed)", fontsize=11)
axL.set_title("The rate of productivity growth is accelerating\n"
              "Both sectors roughly double their pace in 2024-2025", fontsize=12, fontweight="bold")
axL.legend(fontsize=9, loc="upper left"); axL.grid(True, ls="--", alpha=0.35)

# right: decomposition bars, 2013-2019 vs 2024-2025
labels = list(SECTORS.keys())
x = np.arange(len(labels)); w = 0.35
for k, (lbl, a, z) in enumerate([PERIODS[0], PERIODS[2]]):
    outg = [data[n].loc[a:z]["out_g"].mean() for n in labels]
    empg = [data[n].loc[a:z]["emp_g"].mean() for n in labels]
    off = -w/2 if k == 0 else w/2
    hatch = "" if k == 0 else "//"
    axR.bar(x + off, outg, w, color="#4c8fb3", hatch=hatch, edgecolor="white",
            label=f"output growth {lbl}")
    axR.bar(x + off, empg, w, color="#e08e45", hatch=hatch, edgecolor="white",
            label=f"employment growth {lbl}")
axR.axhline(0, color="black", lw=0.9)
axR.set_xticks(x); axR.set_xticklabels(labels, fontsize=9)
axR.set_ylabel("Avg YoY growth (%/yr)", fontsize=11)
axR.set_title("Same acceleration, opposite mechanism\n"
              "Finance: output speeds up, hiring freezes.  Tech: output slows, jobs cut.",
              fontsize=11, fontweight="bold")
axR.legend(fontsize=8, ncol=1, loc="upper right"); axR.grid(True, axis="y", ls="--", alpha=0.35)

fig.suptitle("Productivity acceleration in the two most AI-exposed sectors (2024-2025)",
             fontsize=13, fontweight="bold", y=1.02)
plt.tight_layout()
out = os.path.join(HERE, "productivity_acceleration.png")
plt.savefig(out, dpi=150, bbox_inches="tight")
print(f"Chart saved: {out}")
