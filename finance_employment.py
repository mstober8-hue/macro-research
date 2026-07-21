"""
finance_employment.py
Finance measured on EMPLOYMENT, not unemployment.

The nine-industry cross-section (industry_okun_pipeline.py) measures Okun's law
with the unemployment rate. That instrument is blind to a full-employment
sector: when unemployment is pinned at its structural floor (~2% for Finance),
output growth cannot pull it down any further, so the estimated Okun slope is
~0 and the sector looks like "the law held."

This script re-measures Finance on the variable that can actually show a
decoupling: employment (headcount). It computes:

  - output, employment, and output-per-worker indexed to 2013 = 100
  - the output-elasticity of employment  (%ΔEmployment = γ · %ΔOutput),
    pre vs post Q4 2022 and as a 12-quarter rolling series
  - a JOLTS read (hires and openings) on whether hiring slowed while output grew

Finding: Finance real output more than doubled (index 209 by 2025) while
headcount grew only 17% and output-per-worker rose ~79%. The employment
elasticity was already near zero before 2022 (a long automation-era trend) and
fell to negative by 2025. The decoupling is real and large; the unemployment
test simply could not see it.

Data series (FRED / BLS), placed in FRED-Data/:
  USFIRE.csv          All Employees, Financial Activities (thousands, headcount)
  CEU5500000002.csv   Average Weekly Hours, Financial Activities
  FnceservcGDP.csv    Real value added, Finance & Insurance (output)
  LNU04032238.csv     Unemployment rate, Financial Activities
  JTU510099HIR.csv    JOLTS hires rate, Financial Activities
  JTU510099JOR.csv    JOLTS job openings rate, Financial Activities
"""

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

DATA_DIR  = "FRED-Data/"
AI_CUTOFF = pd.Timestamp("2022-10-01")


def load(filename, label):
    df = pd.read_csv(DATA_DIR + filename)
    df.columns = [c.strip() for c in df.columns]
    df[df.columns[0]] = pd.to_datetime(df[df.columns[0]])
    df = df.set_index(df.columns[0])
    df[df.columns[0]] = pd.to_numeric(df[df.columns[0]], errors="coerce")
    return df.iloc[:, 0].rename(label)


emp = load("USFIRE.csv", "emp").resample("QS").mean()          # headcount, thousands
out = load("FnceservcGDP.csv", "out")                          # real output
u   = load("LNU04032238.csv", "u").resample("QS").mean()       # unemployment rate
hrs = load("CEU5500000002.csv", "hrs").resample("QS").mean()   # avg weekly hours
hir = load("JTU510099HIR.csv", "hires").resample("QS").mean()  # JOLTS hires rate
jor = load("JTU510099JOR.csv", "openings").resample("QS").mean()

df = pd.DataFrame({"emp": emp, "out": out, "u": u, "hrs": hrs}).dropna()
df["opw"] = df["out"] / df["emp"]
df["de"]  = df["emp"].pct_change(4) * 100
df["dy"]  = df["out"].pct_change(4) * 100

# ---- headline index table ----------------------------------------------------
base = df[df.index >= "2013-01-01"].iloc[0]
print("Financial Activities, indexed to 2013 = 100")
print(f"  {'year':<6}{'output':>8}{'employment':>12}{'out/worker':>12}{'unemp %':>9}")
for yr in [2013, 2016, 2019, 2022, 2025]:
    r = df[df.index >= f"{yr}-01-01"].iloc[0]
    print(f"  {yr:<6}{r['out']/base['out']*100:>8.0f}"
          f"{r['emp']/base['emp']*100:>12.0f}"
          f"{r['opw']/base['opw']*100:>12.0f}{r['u']:>9.1f}")

# ---- employment elasticity ---------------------------------------------------
d = df.dropna(subset=["de", "dy"])
print("\nOutput-elasticity of employment  (%ΔEmp = γ · %ΔOutput), YoY")
for lab, a, z in [("pre-2022", "2006-01-01", "2022-09-30"),
                  ("post-2022", "2022-10-01", "2026-12-31")]:
    seg = d[(d.index >= a) & (d.index <= z)]
    g = np.polyfit(seg["dy"], seg["de"], 1)[0]
    r = np.corrcoef(seg["dy"], seg["de"])[0, 1]
    print(f"  {lab:<10} γ = {g:+.3f}  (r={r:+.2f}, n={len(seg)})   classic Okun γ ≈ +0.5 to +0.7")

print("\nJOLTS Financial Activities (monthly rates, quarterly avg)")
for lab, a, z in [("2015-2019", "2015-01-01", "2019-12-31"),
                  ("2023-2026", "2023-01-01", "2026-12-31")]:
    print(f"  {lab}: hires {hir[a:z].mean():.1f}%   openings {jor[a:z].mean():.1f}%")

# ---- rolling elasticity ------------------------------------------------------
idx = d.index.tolist()
roll = []
for i in range(12, len(idx) + 1):
    w = d.iloc[i - 12 : i]
    if np.std(w["dy"]) > 1e-9:
        roll.append((idx[i - 1], np.polyfit(w["dy"], w["de"], 1)[0]))
roll = pd.DataFrame(roll, columns=["date", "gamma"]).set_index("date")

# ---- chart -------------------------------------------------------------------
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 9))
s = df[df.index >= "2013-01-01"]
ax1.plot(s.index, s["out"]/base["out"]*100, color="#c0392b", lw=2.5, label="Real output")
ax1.plot(s.index, s["opw"]/base["opw"]*100, color="#8e44ad", lw=2.2, label="Output per worker (productivity)")
ax1.plot(s.index, s["emp"]/base["emp"]*100, color="#1f4e79", lw=2.5, label="Employment (headcount)")
ax1b = ax1.twinx()
ax1b.plot(s.index, s["u"], color="gray", lw=1.4, ls=":", label="Unemployment (right)")
ax1b.set_ylabel("Unemployment %", color="gray", fontsize=10); ax1b.set_ylim(0, 7)
ax1.set_ylabel("Index (2013 = 100)", fontsize=11)
ax1.set_title("Financial Activities: output doubled, headcount barely moved\n"
              "The decoupling the unemployment-based Okun test could not see",
              fontsize=12, fontweight="bold")
ax1.legend(loc="upper left", fontsize=9); ax1.grid(True, ls="--", alpha=0.3)

ax2.axhspan(0.5, 0.7, color="green", alpha=0.08, label="classic Okun γ (0.5-0.7)")
ax2.plot(roll.index, roll["gamma"], color="black", lw=2.2)
ax2.axhline(0, color="black", lw=0.8, ls="--")
ax2.axvspan(AI_CUTOFF, roll.index[-1], color="gold", alpha=0.10, label="post-Q4 2022")
ax2.set_ylabel("Employment elasticity γ\n(%ΔEmployment per 1% output growth)", fontsize=10)
ax2.set_title("Output-elasticity of Finance employment fell from ~0.5 to negative by 2025",
              fontsize=12, fontweight="bold")
ax2.set_xlabel("Quarter", fontsize=11); ax2.legend(fontsize=9); ax2.grid(True, ls="--", alpha=0.3)
plt.tight_layout()
plt.savefig("finance_employment.png", dpi=150, bbox_inches="tight")
print("\nChart saved: finance_employment.png")
