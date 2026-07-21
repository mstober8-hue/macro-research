"""
comovement.py
Do the inverting sectors move together, and does any other industry repeat it?

Part of the physical-sector-inversion sub-project (separate from the root AI
analysis). Two questions:

  1. Are Construction, Manufacturing, and Transportation & Utilities actually
     co-moving, or do their rolling-Okun charts just look similar by chance?
  2. Does any of the other six industries repeat the same pattern (co-move with
     the cluster AND invert recently)?

Approach:
  - Build each industry's rolling 12-quarter Okun beta and correlation r
    (difference form, YoY, COVID included, same as rolling_okun_inversion.py).
  - Correlate the rolling-beta series across all nine industries. This measures
    whether the CHART SHAPES move together.
  - Flag "recent inverters": industries whose rolling r is positive in 2025.
  - The industries that both co-move with the cluster and invert recently are
    the ones that repeat the phenomenon.

Output: comovement.png (correlation heatmap + goods-sector overlay) and a
console table. Reads FRED CSVs from ../FRED-Data/.
"""

import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE     = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(HERE, "..", "FRED-Data") + os.sep
WINDOW   = 12
COVID    = (pd.Timestamp("2020-04-01"), pd.Timestamp("2021-10-01"))

# Ordered goods sectors first (the candidate cluster), then service sectors.
IND = {
    "Construction":       ("CnstGDP.csv", "ConstUrate .csv"),
    "Manufacturing":      ("MnfctGDP.csv", "MnfctUrate.csv"),
    "Transport & Util":   ("RVAT.csv",     "LNU04032236.csv"),
    "Wholesale":          ("RVAW.csv",     "LNU04032235.csv"),
    "Information":        ("RVAI.csv",     "LNU04032237.csv"),
    "Prof & Bus":         ("RVAPBS.csv",   "LNU04032239.csv"),
    "Leisure & Hosp":     ("RVAAERAF.csv", "LNU04032241.csv"),
    "Financial":          ("FnceservcGDP.csv", "LNU04032238.csv"),
    "Educ & Health":      ("RVAHCSA.csv",  "LNU04032240.csv"),
}
GOODS = ["Construction", "Manufacturing", "Transport & Util", "Wholesale"]


def load_series(filename, label):
    df = pd.read_csv(DATA_DIR + filename, parse_dates=["observation_date"]).set_index("observation_date")
    col = df.columns[0]
    df[col] = pd.to_numeric(df[col], errors="coerce")
    return df[col].rename(label)


def rolling_beta_r(output_file, unemp_file):
    y = load_series(output_file, "y")
    u = load_series(unemp_file, "u").resample("QS").mean()
    df = pd.DataFrame({"y": y, "u": u}).dropna()
    df["pct_dy"]  = df["y"].pct_change(4) * 100
    df["delta_u"] = df["u"].diff(4)
    df = df.dropna(subset=["pct_dy", "delta_u"])
    idx = df.index.tolist()
    beta, corr = {}, {}
    for i in range(WINDOW, len(idx) + 1):
        w = df.iloc[i - WINDOW : i]
        if np.std(w["pct_dy"].values) < 1e-9:
            continue
        beta[idx[i - 1]] = np.polyfit(w["pct_dy"], w["delta_u"], 1)[0]
        corr[idx[i - 1]] = np.corrcoef(w["pct_dy"], w["delta_u"])[0, 1]
    return pd.Series(beta), pd.Series(corr)


BETA, R = {}, {}
for name, (of, uf) in IND.items():
    BETA[name], R[name] = rolling_beta_r(of, uf)
BETA = pd.DataFrame(BETA)
R    = pd.DataFrame(R)
corr = BETA.corr()

# ---- console -----------------------------------------------------------------
print("Rolling-beta correlation to the 3-sector cluster (non-members), plus 2025 r:")
cluster3 = ["Construction", "Manufacturing", "Transport & Util"]
mean_to_cluster = corr[cluster3].mean(axis=1)
last_r = R[R.index >= "2025-01-01"].iloc[-1] if (R.index >= "2025-01-01").any() else R.iloc[-1]
for name in IND:
    flag = " [cluster]" if name in cluster3 else (" <-- REPEATS IT" if (name not in cluster3 and mean_to_cluster[name] > 0.6 and last_r[name] > 0) else "")
    print(f"  {name:<18} corr_to_cluster={mean_to_cluster[name]:+.2f}  latest_r={last_r[name]:+.2f}{flag}")

# ---- chart -------------------------------------------------------------------
fig, (axh, axr) = plt.subplots(1, 2, figsize=(18, 7.5),
                               gridspec_kw={"width_ratios": [1.05, 1]})

# (a) heatmap of rolling-beta correlations
names = list(IND.keys())
M = corr.loc[names, names].values
im = axh.imshow(M, cmap="RdYlBu_r", vmin=-0.2, vmax=1.0)
axh.set_xticks(range(len(names))); axh.set_xticklabels(names, rotation=45, ha="right", fontsize=9)
axh.set_yticks(range(len(names))); axh.set_yticklabels(names, fontsize=9)
for i in range(len(names)):
    for j in range(len(names)):
        axh.text(j, i, f"{M[i,j]:.2f}", ha="center", va="center", fontsize=7.5,
                 color="black" if M[i,j] < 0.75 else "white")
# box the 4 goods sectors (they sit in the top-left 4x4)
axh.add_patch(plt.Rectangle((-0.5, -0.5), 4, 4, fill=False, edgecolor="black", linewidth=2.5))
axh.set_title("Rolling-Okun-β correlation across industries\n"
              "Black box = the goods-producing cluster (build / make / move / distribute)",
              fontsize=11, fontweight="bold")
fig.colorbar(im, ax=axh, fraction=0.046, pad=0.04)

# (b) overlay the four goods sectors' rolling r
axr.axvspan(COVID[0], COVID[1], color="crimson", alpha=0.10, label="COVID (kept)")
colors = {"Construction":"#1f3b73","Manufacturing":"#3f7cac","Transport & Util":"#6fb0d6","Wholesale":"#c0392b"}
for name in GOODS:
    axr.plot(R.index, R[name], linewidth=2.0, color=colors[name], label=name)
axr.axhline(0, color="black", linewidth=0.9, linestyle="--")
axr.set_ylim(-1.05, 1.05)
axr.set_title("The four goods sectors move together and invert together (2024-2025)\n"
              "Rolling 12-quarter correlation r  (r > 0 = Okun inverted)",
              fontsize=11, fontweight="bold")
axr.set_xlabel("Quarter (end of 12-quarter window)", fontsize=10)
axr.set_ylabel("Rolling correlation r", fontsize=10)
axr.legend(fontsize=9, loc="lower right")
axr.grid(True, linestyle="--", alpha=0.35)

plt.tight_layout()
out = os.path.join(HERE, "comovement.png")
plt.savefig(out, dpi=150, bbox_inches="tight")
print(f"\nChart saved: {out}")
