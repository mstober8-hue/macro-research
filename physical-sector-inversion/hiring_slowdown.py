"""
hiring_slowdown.py
Why did hiring slow? The lead analysis for this sub-project.

what_actually_inverted.py established that the goods-sector "Okun inversion" is
a small sign flip sitting on top of an economy-wide hiring slowdown that hit 8
of 9 sectors in 2024-2025 and that AI exposure does not predict. This script
asks the obvious next question: what caused the slowdown?

It tests the three standard candidates, and produces the chart that should lead
this sub-project, replacing the three-sector rolling-Okun panels that framed
the finding as goods-specific.

TEST A - Is it a post-pandemic over-hiring correction?
    No. Sectors that surged hardest in the 2021-2023 rebound are NOT the ones
    that slowed most (r=-0.22, p=0.57). And 8 of 9 sectors now sit BELOW their
    extrapolated 2013-2019 employment trend, by 1% to 13%. A correction from
    over-hiring would leave them above trend, not below.

TEST B - Is it sector characteristics (AI exposure, prior pace)?
    No. Neither AI exposure (r=+0.19, p=0.63) nor pre-COVID hiring pace
    (r=-0.21, p=0.59) predicts which sectors slowed.

TEST C - Is it a single common macro force?
    Yes. One principal component explains 72% of the variance in sector
    employment growth, and it is essentially the simple 9-sector average
    (corr 0.992). That factor sat at +1.04 in 2013-2019, spiked to +3.24 in
    the 2021-2023 rebound, and fell to -0.75 in 2024-2025.

    Scanning lags against the Federal Funds Rate, the common hiring factor
    tracks the policy rate with a long lag that peaks at 8-9 quarters:
    r=-0.52 over the full sample, r=-0.74 excluding COVID quarters
    (p<0.0001, n=75). The 2022-2023 hiking cycle plus a ~2 year transmission
    lag lands exactly on the 2024-2025 hiring slowdown.

WHY THE ROOT STUDY MISSED THIS: okun_phase2_3.py tests rate controls at lags
of 0, 2 and 4 quarters only (`for lag in [0, 2, 4]`). The peak effect is at
8-9 quarters, so every rate control in the main analysis was roughly half as
long as it needed to be to capture the channel.

Reads FRED CSVs from ../FRED-Data/. Writes hiring_slowdown.png.
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

# employment file(s), AIIE, group
SECTORS = {
    "Construction":            (["construction_employment_USCONS.csv"], -0.997, "goods"),
    "Manufacturing":           (["manufacturing_employment_MANEMP.csv"], -0.484, "goods"),
    "Transportation & Util":   (["transportation_warehousing_employment_CES4300000001.csv",
                                 "utilities_employment_CES4422000001.csv"], -0.342, "goods"),
    "Leisure & Hospitality":   (["leisure_hospitality_employment_USLAH.csv"], -0.315, "other"),
    "Wholesale":               (["wholesale_trade_employment_USWTRADE.csv"], 0.264, "goods"),
    "Professional & Business": (["professional_business_services_employment_USPBS.csv"], 0.654, "high-AI"),
    "Education & Health":      (["education_health_employment_USEHS.csv"], 0.775, "other"),
    "Information":             (["information_sector_employment_USINFO.csv"], 1.268, "high-AI"),
    "Financial Activities":    (["finance_insurance_employment_CES5552000001.csv"], 1.538, "high-AI"),
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


def emp_sum(files):
    s = None
    for f in files:
        x = load(f).resample("QS").mean()
        s = x if s is None else s.add(x, fill_value=np.nan)
    return s


EMP = {n: emp_sum(fs) for n, (fs, _, _) in SECTORS.items()}
G = pd.DataFrame({n: (e.pct_change(4) * 100) for n, e in EMP.items()}).dropna()
G = G[G.index >= "2006-01-01"]

# ---- per-sector summary + trend gap -----------------------------------------
rows = []
for name, (fs, aiie, grp) in SECTORS.items():
    e = EMP[name]
    g = (e.pct_change(4) * 100).dropna()
    pre   = g.loc["2013-01-01":"2019-12-31"].mean()
    surge = g.loc["2021-07-01":"2023-06-30"].mean()
    post  = g.loc["2024-01-01":"2026-12-31"].mean()
    tr = e.loc["2013-01-01":"2019-12-31"]
    m, b = np.polyfit(np.arange(len(tr)), tr.values, 1)
    xf = np.array([(d - tr.index[0]).days / 91.3125 for d in e.index])
    trend = pd.Series(b + m * xf, index=e.index)
    rows.append(dict(sector=name, aiie=aiie, grp=grp, pre=pre, surge=surge, post=post,
                     slowdown=post - pre, surge_excess=surge - pre,
                     gap=(e.iloc[-1] / trend.iloc[-1] - 1) * 100))
R = pd.DataFrame(rows)

print("=" * 88)
print("WHY DID HIRING SLOW?  (employment growth, avg YoY %)")
print("=" * 88)
print(f"\n{'sector':<24}{'pre 13-19':>10}{'rebound 21-23':>14}{'post 24-25':>11}{'slowdown':>10}{'vs trend':>10}")
for _, r in R.sort_values("slowdown").iterrows():
    print(f"{r.sector:<24}{r.pre:>+10.2f}{r.surge:>+14.2f}{r.post:>+11.2f}{r.slowdown:>+10.2f}{r.gap:>+9.1f}%")

print("\nTEST A - over-hiring correction?")
sl, ic, rA, pA, se = sp_stats.linregress(R["surge_excess"], R["slowdown"])
print(f"  slowdown ~ size of 2021-23 rebound : r={rA:+.3f}  p={pA:.3f}   -> no relationship")
print(f"  sectors now BELOW their 2013-19 trend: {int((R.gap < 0).sum())} of 9  "
      f"(a correction would leave them above)")

print("\nTEST B - sector characteristics?")
for col, lbl in [("aiie", "AI exposure"), ("pre", "pre-COVID hiring pace")]:
    sl, ic, r_, p_, se = sp_stats.linregress(R[col], R["slowdown"])
    print(f"  slowdown ~ {lbl:<24} r={r_:+.3f}  p={p_:.3f}")

# ---- common factor ----------------------------------------------------------
X = (G - G.mean()) / G.std()
u, s, vt = np.linalg.svd(X.values, full_matrices=False)
pc1 = pd.Series(u[:, 0] * s[0], index=G.index)
if np.corrcoef(pc1, G.mean(axis=1))[0, 1] < 0:
    pc1 = -pc1
var1 = s[0] ** 2 / np.sum(s ** 2) * 100
avg = G.mean(axis=1)

print("\nTEST C - one common macro force?")
print(f"  PC1 explains {var1:.0f}% of variance in sector employment growth")
print(f"  PC1 vs simple 9-sector average: corr {np.corrcoef(pc1, avg)[0,1]:+.3f}")
for lbl, a, b_ in [("2013-2019", "2013-01-01", "2019-12-31"),
                   ("2021-2023 rebound", "2021-07-01", "2023-06-30"),
                   ("2024-2025", "2024-01-01", "2026-12-31")]:
    print(f"    common factor, {lbl:<18} {pc1.loc[a:b_].mean():+.2f}")

ffr = load("fed_funds_rate_FEDFUNDS.csv").resample("QS").mean()
print("\n  Lag scan: corr(avg sector hiring growth, FFR lagged k quarters)")
best = (None, 0, 1)
lags, rs = [], []
for lag in range(0, 13):
    j = pd.DataFrame({"h": avg, "f": ffr.shift(lag)}).dropna()
    r_, p_ = sp_stats.pearsonr(j["f"], j["h"])
    lags.append(lag); rs.append(r_)
    if abs(r_) > abs(best[1]):
        best = (lag, r_, p_)
    print(f"    lag {lag:>2}q ({lag*3:>2} mo): r={r_:+.3f}  p={p_:.4f}")
bl, br, bp = best
jx = pd.DataFrame({"h": avg, "f": ffr.shift(bl)}).dropna()
jx = jx[~jx.index.isin(COVID_Q)]
rx, px = sp_stats.pearsonr(jx["f"], jx["h"])
print(f"\n  Peak at lag {bl}q ({bl*3} months): r={br:+.3f} (p={bp:.4f})")
print(f"  Excluding COVID quarters:            r={rx:+.3f} (p={px:.4f}, n={len(jx)})")
print("\n  The root study's rate controls test lags of 0, 2 and 4 quarters only.")
print("  The channel peaks at 8-9 quarters, so those controls were far too short.")

# ---- chart ------------------------------------------------------------------
fig = plt.figure(figsize=(19, 6.4))
gs = fig.add_gridspec(1, 3, width_ratios=[1.15, 1, 1.05], wspace=0.28)
ax1, ax2, ax3 = [fig.add_subplot(gs[0, i]) for i in range(3)]
COL = {"goods": "#1f4e79", "high-AI": "#c0392b", "other": "gray"}

# panel 1: every sector slowed
Rs = R.sort_values("slowdown")
y = np.arange(len(Rs))
ax1.barh(y, Rs["slowdown"], color=[COL[g] for g in Rs["grp"]])
ax1.axvline(0, color="black", lw=1.0)
ax1.set_yticks(y); ax1.set_yticklabels(Rs["sector"], fontsize=9)
ax1.set_xlabel("change in employment growth, 2024-25 vs 2013-19 (pp)", fontsize=9.5)
ax1.set_title("1. Hiring slowed almost everywhere\n"
              "8 of 9 sectors, goods and services alike", fontsize=11, fontweight="bold")
h = [plt.Rectangle((0, 0), 1, 1, color=c) for c in [COL["goods"], COL["high-AI"], COL["other"]]]
ax1.legend(h, ["goods (low AI)", "high AI", "other"], fontsize=8, loc="lower left")
ax1.grid(True, axis="x", ls="--", alpha=0.35)

# panel 2: it is one common factor
ax2.axvspan(pd.Timestamp("2024-01-01"), G.index[-1], color="gold", alpha=0.13)
for n in G.columns:
    ax2.plot(G.index, G[n], color="lightgray", lw=1.0, zorder=1)
ax2.plot(avg.index, avg, color="black", lw=2.6, zorder=3,
         label=f"common factor ({var1:.0f}% of variance)")
ax2.axhline(0, color="black", lw=0.9, ls="--")
ax2.set_ylabel("employment growth, YoY %", fontsize=9.5)
ax2.set_title("2. The sectors are one story\n"
              "A single factor explains 72% of hiring", fontsize=11, fontweight="bold")
ax2.legend(fontsize=8.5, loc="lower left"); ax2.grid(True, ls="--", alpha=0.35)
ax2.set_ylim(-15, 15)

# panel 3: rates lead hiring. COVID quarters are blanked so the pandemic spike
# does not compress the axis and hide the normal-times relationship.
ax3b = ax3.twinx()
avg_p = avg.copy(); avg_p.loc[avg_p.index.isin(COVID_Q)] = np.nan
ffr_sh = ffr.shift(bl)
ffr_p = ffr_sh.copy(); ffr_p.loc[ffr_p.index.isin(COVID_Q)] = np.nan
ax3.axvspan(COVID_Q[0], COVID_Q[-1], color="crimson", alpha=0.08)
ax3.plot(avg_p.index, avg_p, color="black", lw=2.4, label="hiring growth (9-sector avg)")
ax3.axhline(0, color="black", lw=0.8, ls="--")
ax3b.plot(ffr_p.index, ffr_p, color="#c0392b", lw=2.2, ls="--",
          label=f"Fed funds rate, lagged {bl}q")
ax3b.invert_yaxis()
ax3.set_xlim(pd.Timestamp("2006-01-01"), avg.index[-1])
ax3.set_ylim(-4, 5)
ax3.set_ylabel("hiring growth, YoY %", fontsize=9.5)
ax3b.set_ylabel("Fed funds rate (%), inverted axis", color="#c0392b", fontsize=9.5)
ax3.set_title(f"3. Rates lead hiring by ~2 years\n"
              f"r={rx:+.2f} excluding COVID (p<0.001)", fontsize=11, fontweight="bold")
ax3.text(0.52, 0.93, "COVID quarters blanked", transform=ax3.transAxes,
         fontsize=7.5, color="crimson", ha="center")
l1, la1 = ax3.get_legend_handles_labels()
l2, la2 = ax3b.get_legend_handles_labels()
ax3.legend(l1 + l2, la1 + la2, fontsize=8, loc="lower left")
ax3.grid(True, ls="--", alpha=0.35)

fig.suptitle("The 2024-2025 hiring slowdown: economy-wide, one common factor, and it follows the rate hikes",
             fontsize=13, fontweight="bold", y=1.02)
out = os.path.join(HERE, "hiring_slowdown.png")
plt.savefig(out, dpi=150, bbox_inches="tight")
print(f"\nChart saved: {out}")
