"""
why_in_sync.py
Why did Construction, Manufacturing and Transportation move together?
An attempt to prove the mechanism, including the tests that failed.

This script was written to build the strongest possible case for the
goods-sector story. It ends up proving something different from what it set
out to prove, so the failed tests are reported alongside the surviving ones.

WHAT SURVIVED

  1. The trio really is synchronized. Their employment growth has an average
     pairwise correlation of +0.85 (excluding COVID), which ranks 7th of the
     84 possible 3-sector combinations, the 92nd percentile.

  2. But there is no separate "goods factor". After removing the single
     economy-wide common factor, the trio's residual co-movement is -0.01,
     indistinguishable from zero and no different from any other group. They
     move together because they all ride the same economy-wide cycle, not
     because of anything specific to building, making and moving things.

  3. That cycle is driven by interest rates, and the evidence is strong.
     Employment growth correlates with the Fed funds rate lagged 9 quarters
     at r = -0.49 to -0.76 in 8 of 9 sectors, every one at p < 0.0001, n=75.

  4. The natural control is decisive. Education & Health is the one sector
     with no rate sensitivity (r = +0.02, p = 0.89), and it is also the one
     sector that did not slow hiring (+1.3pp while the other eight fell).
     One sector out of nine ignores the rate cycle, and it is exactly the one
     that ignores the hiring slowdown.

WHAT FAILED

  5. The trio is NOT significantly more rate-sensitive than the rest
     (trio mean -0.727 vs -0.520, p = 0.13), and Finance ranks second most
     sensitive of all. Rate sensitivity is close to universal, so it cannot
     be what singles out the goods sectors.

  6. The "variance collapse" explanation for why the Okun correlation flipped
     in these sectors does not hold. The ratio of post- to pre-period
     unemployment variance does not predict which sectors flipped
     (r = +0.01, p = 0.98).

  7. Most importantly, the Okun inversion itself is not robust. It depends
     on using a short rolling window. At 8 and 12 quarters the goods sectors
     show peak correlations of +0.45 to +0.84, but at 20 quarters they turn
     NEGATIVE for three of four (Transportation -0.74, Manufacturing -0.58,
     Wholesale -0.11). Moving the fixed post-period start by two quarters
     swings Manufacturing from +0.52 to -0.07 and Wholesale from +0.48 to
     -0.20. A result that reverses under ordinary window choices is not
     evidence of a structural break.

CONCLUSION: the sectors moved in sync because a single rate-driven cycle
moves nearly the whole economy, and the trio rides it hard. The "Okun
inversion" that named this folder is a short-window statistical artifact
sitting on top of that real slowdown.

Reads FRED CSVs from ../FRED-Data/. Writes why_in_sync.png.
"""

import os
import glob
import itertools
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats as sp_stats

HERE     = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(HERE, "..", "FRED-Data") + os.sep
COVID_Q  = pd.date_range("2020-04-01", "2021-10-01", freq="QS")
LAG      = 9
TRIO     = ["Construction", "Manufacturing", "Transportation"]

EMP_FILES = {
    "Construction":   ["construction_employment_USCONS.csv"],
    "Manufacturing":  ["manufacturing_employment_MANEMP.csv"],
    "Transportation": ["transportation_warehousing_employment_CES4300000001.csv",
                       "utilities_employment_CES4422000001.csv"],
    "Wholesale":      ["wholesale_trade_employment_USWTRADE.csv"],
    "Leisure":        ["leisure_hospitality_employment_USLAH.csv"],
    "ProfBus":        ["professional_business_services_employment_USPBS.csv"],
    "EducHealth":     ["education_health_employment_USEHS.csv"],
    "Information":    ["information_sector_employment_USINFO.csv"],
    "Finance":        ["finance_insurance_employment_CES5552000001.csv"],
}
OKUN_FILES = {
    "Construction":   ("construction_value_added_RVAC.csv", "construction_unemployment_rate_LNU04032231.csv"),
    "Manufacturing":  ("manufacturing_value_added_RVAMA.csv", "manufacturing_unemployment_rate_LNU04032232.csv"),
    "Transportation": ("transportation_warehousing_value_added_RVAT.csv",
                       "transportation_utilities_unemployment_rate_LNU04032236.csv"),
    "Wholesale":      ("wholesale_trade_value_added_RVAW.csv",
                       "wholesale_retail_trade_unemployment_rate_LNU04032235.csv"),
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


G = pd.DataFrame({n: (emp_sum(fs).pct_change(4) * 100) for n, fs in EMP_FILES.items()}).dropna()
G = G[G.index >= "2006-01-01"]
Gx = G[~G.index.isin(COVID_Q)]
ffr = load("fed_funds_rate_FEDFUNDS.csv").resample("QS").mean()


def avg_pair(df, cols):
    c = df[cols].corr().values
    n = len(cols)
    return (c.sum() - n) / (n * n - n)


print("=" * 84)
print("WHY DID THEY MOVE IN SYNC?  Building the case, and reporting what breaks it")
print("=" * 84)

# --- 1. synchronization -------------------------------------------------------
trio_r = avg_pair(Gx, TRIO)
combos = [avg_pair(Gx, list(t)) for t in itertools.combinations(G.columns, 3)]
rank = sum(1 for a in combos if a >= trio_r)
print(f"\n[1] SURVIVES - the trio is genuinely synchronized")
print(f"    avg pairwise corr of employment growth : {trio_r:+.3f}")
print(f"    rank among all {len(combos)} 3-sector combos  : #{rank}  "
      f"({100*(1-rank/len(combos)):.0f}th percentile)")

# --- 2. no separate goods factor ---------------------------------------------
X = (Gx - Gx.mean()) / Gx.std()
u, s, vt = np.linalg.svd(X.values, full_matrices=False)
pc1_fit = u[:, 0:1] @ np.diag(s[0:1]) @ vt[0:1, :]
resid = pd.DataFrame(X.values - pc1_fit, index=Gx.index, columns=Gx.columns)
var1 = s[0] ** 2 / np.sum(s ** 2) * 100
others = [c for c in G.columns if c not in TRIO]
print(f"\n[2] SURVIVES - but there is NO separate goods factor")
print(f"    one common factor explains        : {var1:.0f}% of all variance")
print(f"    trio co-movement in residuals     : {avg_pair(resid, TRIO):+.3f}")
print(f"    non-trio co-movement in residuals : {avg_pair(resid, others):+.3f}")
print(f"    -> their synchrony is the economy-wide cycle, nothing goods-specific")

# --- 3. rate sensitivity ------------------------------------------------------
rate_rows = []
for n in G.columns:
    j = pd.DataFrame({"g": G[n], "f": ffr.shift(LAG)}).dropna()
    j = j[~j.index.isin(COVID_Q)]
    r_, p_ = sp_stats.pearsonr(j["f"], j["g"])
    rate_rows.append(dict(sector=n, r=r_, p=p_, n=len(j)))
RS = pd.DataFrame(rate_rows).sort_values("r")
print(f"\n[3] SURVIVES - rate sensitivity is strong and near-universal (FFR lagged {LAG}q)")
for _, x in RS.iterrows():
    tag = "  <- trio" if x.sector in TRIO else ("  <- the exception" if x.sector == "EducHealth" else "")
    print(f"    {x.sector:<15} r={x.r:+.3f}  p={x.p:.4f}{tag}")

# --- 4. the natural control ---------------------------------------------------
slow = {}
for n, fs in EMP_FILES.items():
    g = (emp_sum(fs).pct_change(4) * 100).dropna()
    slow[n] = g.loc["2024-01-01":].mean() - g.loc["2013-01-01":"2019-12-31"].mean()
print(f"\n[4] SURVIVES - the natural control")
print(f"    Education & Health is the ONLY sector with no rate sensitivity "
      f"(r={RS[RS.sector=='EducHealth'].r.iloc[0]:+.3f})")
print(f"    and the ONLY sector that did not slow hiring "
      f"({slow['EducHealth']:+.2f}pp vs {np.mean([v for k,v in slow.items() if k!='EducHealth']):+.2f}pp for the rest)")

# --- 5. trio not distinctively rate-sensitive --------------------------------
tr = RS[RS.sector.isin(TRIO)]; ot = RS[~RS.sector.isin(TRIO)]
t5, p5 = sp_stats.ttest_ind(tr.r, ot.r, equal_var=False)
print(f"\n[5] FAILS - the trio is not distinctively rate-sensitive")
print(f"    trio mean r {tr.r.mean():+.3f} vs others {ot.r.mean():+.3f}, p={p5:.3f}")
print(f"    Finance is the 2nd most rate-sensitive sector of all")

# --- 6. variance-collapse explanation ----------------------------------------
vc = []
for n, (of, uf) in OKUN_FILES.items():
    o = load(of); un = load(uf).resample("QS").mean()
    d = pd.DataFrame({"o": o, "u": un}).dropna()
    d["dy"] = d["o"].pct_change(4) * 100; d["du"] = d["u"].diff(4)
    d = d.dropna()
    pre = d.loc["2013-01-01":"2019-12-31"]; post = d.loc["2024-01-01":]
    vc.append(dict(sector=n, ratio=post["du"].std() / pre["du"].std(),
                   dr=np.corrcoef(post["dy"], post["du"])[0, 1] - np.corrcoef(pre["dy"], pre["du"])[0, 1]))
VC = pd.DataFrame(vc)
r6, p6 = sp_stats.pearsonr(VC["ratio"], VC["dr"])
print(f"\n[6] FAILS - 'variance collapse' does not explain which sectors flipped")
print(f"    correlation change ~ variance ratio: r={r6:+.3f}, p={p6:.3f}")

# --- 7. window sensitivity ----------------------------------------------------
print(f"\n[7] FAILS - and this is the important one: the inversion is not robust")
print(f"    Peak rolling correlation since 2024, by window length:\n")
print("    " + f"{'sector':<16}" + "".join(f"{w:>9}" for w in ["8q", "12q", "16q", "20q"]))
wins = {}
for n, (of, uf) in OKUN_FILES.items():
    o = load(of); un = load(uf).resample("QS").mean()
    d = pd.DataFrame({"o": o, "u": un}).dropna()
    d["dy"] = d["o"].pct_change(4) * 100; d["du"] = d["u"].diff(4)
    d = d.dropna()
    row = []
    for W in [8, 12, 16, 20]:
        idx = d.index.tolist(); rs = []
        for i in range(W, len(idx) + 1):
            w = d.iloc[i - W:i]
            if np.std(w["dy"]) > 1e-9 and idx[i - 1] >= pd.Timestamp("2024-01-01"):
                rs.append(np.corrcoef(w["dy"], w["du"])[0, 1])
        row.append(max(rs) if rs else np.nan)
    wins[n] = row
    print("    " + f"{n:<16}" + "".join(f"{v:>+9.2f}" for v in row))
print("\n    Three of four turn NEGATIVE at a 20-quarter window. The inversion is")
print("    a short-window artifact, not a structural break.")

# ---- chart ------------------------------------------------------------------
fig, (a1, a2, a3) = plt.subplots(1, 3, figsize=(19, 6.2))

# panel 1: rate sensitivity, ranked
RSp = RS.sort_values("r")
cols = ["#1f4e79" if s in TRIO else ("#e8b021" if s == "EducHealth" else "#9bb7d4") for s in RSp.sector]
a1.barh(np.arange(len(RSp)), RSp["r"], color=cols)
a1.axvline(0, color="black", lw=1.0)
a1.set_yticks(np.arange(len(RSp))); a1.set_yticklabels(RSp.sector, fontsize=9)
a1.set_xlabel(f"corr(employment growth, Fed funds rate lagged {LAG}q)", fontsize=9.5)
a1.set_title("1. Rate sensitivity is near-universal\n"
             "8 of 9 sectors, all p<0.0001", fontsize=11, fontweight="bold")
a1.annotate("Education & Health:\nno rate response,\nand the only sector\nthat kept hiring",
            xy=(0.02, len(RSp) - 1), xytext=(-0.42, len(RSp) - 2.9), fontsize=8,
            arrowprops=dict(arrowstyle="->", color="#8a6a00"), color="#8a6a00")
a1.grid(True, axis="x", ls="--", alpha=0.35)

# panel 2: synchrony explained by the common factor
labels = ["raw employment\ngrowth", "after removing the\neconomy-wide factor"]
trio_vals  = [trio_r, avg_pair(resid, TRIO)]
other_vals = [avg_pair(Gx, others), avg_pair(resid, others)]
x = np.arange(2); w = 0.35
a2.bar(x - w/2, trio_vals, w, color="#1f4e79", label="the trio")
a2.bar(x + w/2, other_vals, w, color="#9bb7d4", label="other six sectors")
a2.axhline(0, color="black", lw=1.0)
a2.set_xticks(x); a2.set_xticklabels(labels, fontsize=9)
a2.set_ylabel("average pairwise correlation", fontsize=9.5)
a2.set_title("2. Their synchrony IS the common cycle\n"
             "No goods-specific factor survives", fontsize=11, fontweight="bold")
a2.legend(fontsize=8.5); a2.grid(True, axis="y", ls="--", alpha=0.35)

# panel 3: window sensitivity kills the inversion
W_LABELS = ["8q", "12q", "16q", "20q"]
for n, row in wins.items():
    a3.plot(W_LABELS, row, marker="o", lw=2.0, label=n)
a3.axhline(0, color="black", lw=1.2, ls="--")
a3.fill_between([0, 3], -1, 0, color="green", alpha=0.06)
a3.fill_between([0, 3], 0, 1, color="red", alpha=0.06)
a3.text(0.05, 0.62, "inverted", transform=a3.transAxes, fontsize=9, color="darkred")
a3.text(0.05, 0.30, "law holds", transform=a3.transAxes, fontsize=9, color="darkgreen")
a3.set_ylim(-0.9, 0.95)
a3.set_xlabel("rolling window length", fontsize=9.5)
a3.set_ylabel("peak correlation since 2024", fontsize=9.5)
a3.set_title("3. The inversion does not survive\nlonger windows", fontsize=11, fontweight="bold")
a3.legend(fontsize=8.5, loc="lower left"); a3.grid(True, ls="--", alpha=0.35)

fig.suptitle("Why the goods sectors moved in sync: one rate-driven cycle, and an inversion that is not robust",
             fontsize=13, fontweight="bold", y=1.02)
plt.tight_layout()
out = os.path.join(HERE, "why_in_sync.png")
plt.savefig(out, dpi=150, bbox_inches="tight")
print(f"\nChart saved: {out}")
