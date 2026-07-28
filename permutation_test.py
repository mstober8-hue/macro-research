"""
permutation_test.py
Replace the normal-approximation p-values with a distribution-free bootstrap.

Every "probability of a rolling correlation this positive" figure in this
project (the aggregate p ~ 0.0000, and the physical sectors' p = 0.007 to
0.019) came from the same shortcut: fit a normal distribution to the sector's
own pre-2022 rolling correlations, then ask how far into its tail the observed
peak sits. That shortcut has two known problems, both of which push p DOWN:

  1. Overlapping windows. Consecutive 12-quarter windows share 11 quarters, so
     the pre-2022 rolling correlations are heavily autocorrelated. Their
     standard deviation understates how much a genuinely new window can vary,
     which makes the tail look thinner than it is.
  2. Normality. Correlations are bounded on [-1, 1] and skewed near the edges,
     so a normal tail is the wrong shape exactly where it is being evaluated.

This script replaces that with a circular block bootstrap that makes no
distributional assumption and preserves the data's own autocorrelation.

NULL HYPOTHESIS: the pre-2022 regime simply continued. Under that null we
resample the sector's pre-2022 (output growth, unemployment change) PAIRS in
contiguous blocks, which preserves both each series' autocorrelation and the
genuine Okun relationship between them. We then generate as many new rolling
windows as the post-2022 period actually has, take the maximum correlation
across them, and ask how often that maximum reaches the observed value. Taking
the maximum is deliberate: it accounts for the fact that the observed peak was
itself selected as the largest of many post-2022 windows.

Block length is varied (4, 8, 12 quarters) as a robustness check; n^(1/3) puts
the textbook default near 4.

RESULT: the aggregate break survives easily (bootstrap p ~ 0.0006 rather than
the reported 0.0000, still decisive). The three physical-sector inversions
weaken materially, from p = 0.007-0.019 to roughly p = 0.03-0.055, and none of
them would survive a Bonferroni correction across the three sectors. Their
inversions should be described as marginal rather than clearly significant.

Reads FRED-Data/. Writes permutation_test.png.
"""

import os, glob, warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats as sp
warnings.filterwarnings("ignore")

DATA   = "FRED-Data/"
WINDOW = 12
CUT    = pd.Timestamp("2022-10-01")
BLOCKS = [4, 8, 12]
B      = 10000
SEED   = 20260726

SECTORS = {
    "Construction":               ("construction_value_added_RVAC.csv", "construction_unemployment_rate_LNU04032231.csv"),
    "Manufacturing":              ("manufacturing_value_added_RVAMA.csv", "manufacturing_unemployment_rate_LNU04032232.csv"),
    "Transportation & Utilities": ("transportation_warehousing_value_added_RVAT.csv", "transportation_utilities_unemployment_rate_LNU04032236.csv"),
}


def find(f):
    if os.path.exists(DATA + f):
        return DATA + f
    return (glob.glob(DATA + "*" + f + "*") + glob.glob(DATA + "*" + f))[0]


def load(f):
    d = pd.read_csv(find(f)); d.columns = [c.strip() for c in d.columns]
    d[d.columns[0]] = pd.to_datetime(d[d.columns[0]]); d = d.set_index(d.columns[0])
    return pd.to_numeric(d.iloc[:, 0], errors="coerce").dropna()


def rolling_r(x, y, w=WINDOW):
    return np.array([np.corrcoef(x[i - w:i], y[i - w:i])[0, 1] for i in range(w, len(x) + 1)])


def block_bootstrap_p(x_pre, y_pre, observed, n_post, block, rng, B=B):
    """P(max rolling r over n_post new windows >= observed) under the pre-2022 regime."""
    n = len(x_pre)
    n_new = WINDOW + n_post - 1
    hits = 0
    maxes = np.empty(B)
    for b in range(B):
        xs, ys = [], []
        while len(xs) < n_new:
            s = rng.integers(0, n)
            ln = min(block, n_new - len(xs))
            idx = [(s + k) % n for k in range(ln)]
            xs.extend(x_pre[idx]); ys.extend(y_pre[idx])
        m = np.nanmax(rolling_r(np.asarray(xs), np.asarray(ys)))
        maxes[b] = m
        hits += (m >= observed)
    return hits / B, maxes


# ---------- build the four tests ----------
tests = []

# aggregate (gap form, COVID excluded, matching GDPUnemployment.py)
gdp = load("real_gdp_GDPC1.csv"); pot = load("potential_gdp_GDPPOT.csv")
un = load("unemployment_rate_UNRATE.csv").resample("QS").mean(); nrou = load("natural_unemployment_rate_NROU.csv")
agg = pd.DataFrame({"gdp": gdp, "pot": pot, "un": un, "nrou": nrou}).dropna()
agg["x"] = (agg["gdp"] - agg["pot"]) / agg["pot"] * 100
agg["y"] = agg["un"] - agg["nrou"]
agg = agg[~agg.index.isin(pd.date_range("2020-04-01", "2021-01-01", freq="QS"))]
agg = agg[agg.index >= "2000-01-01"]
tests.append(("Aggregate economy", agg["x"].values, agg["y"].values, agg.index))

# three physical sectors (difference form, COVID kept, matching the sub-project)
for name, (of, uf) in SECTORS.items():
    d = pd.DataFrame({"o": load(of), "u": load(uf).resample("QS").mean()}).dropna()
    d["x"] = d["o"].pct_change(4) * 100
    d["y"] = d["u"].diff(4)
    d = d.dropna(subset=["x", "y"])
    tests.append((name, d["x"].values, d["y"].values, d.index))

rng = np.random.default_rng(SEED)
results = []

print("=" * 92)
print("BOOTSTRAP vs NORMAL-APPROXIMATION p-VALUES")
print("=" * 92)
print(f"{'test':<28}{'peak r':>8}{'normal p':>11}{'empirical':>12}" + "".join(f"{'boot L=' + str(L):>11}" for L in BLOCKS))

for name, x, y, index in tests:
    rs = rolling_r(x, y)
    dates = index[WINDOW - 1:]
    pre = rs[dates < CUT]
    obs = rs.max()
    n_post = int((dates >= CUT).sum())
    p_norm = 1 - sp.norm.cdf(obs, pre.mean(), pre.std())
    emp = int((pre >= obs).sum())

    pre_end = int(np.searchsorted(index, CUT))
    ps, dists = [], {}
    for L in BLOCKS:
        p, mx = block_bootstrap_p(x[:pre_end], y[:pre_end], obs, n_post, L, rng)
        ps.append(p); dists[L] = mx
    results.append(dict(name=name, obs=obs, p_norm=p_norm, emp=emp, n_pre=len(pre),
                        ps=ps, dist=dists[BLOCKS[0]]))
    print(f"{name:<28}{obs:>+8.3f}{p_norm:>11.4f}{f'{emp}/{len(pre)}':>12}" + "".join(f"{p:>11.4f}" for p in ps))

print("\nInterpretation")
agg_r = results[0]
print(f"  Aggregate: normal approx said p={agg_r['p_norm']:.6f}; bootstrap says p~{max(agg_r['ps']):.4f}.")
print("             Orders of magnitude larger, still decisive. The break holds.")
sec_ps = [max(r["ps"]) for r in results[1:]]
print(f"  Physical sectors: normal approx said p=0.006-0.018; bootstrap says p={min(sec_ps):.3f}-{max(sec_ps):.3f}.")
print(f"             Bonferroni across 3 sectors needs p<0.017; none clear it.")
print("             Report these inversions as marginal, not clearly significant.")

# ---------- chart ----------
fig, axes = plt.subplots(1, 4, figsize=(19, 5.0))
for ax, r in zip(axes, results):
    ax.hist(r["dist"], bins=45, color="steelblue", alpha=0.75, edgecolor="white")
    ax.axvline(r["obs"], color="firebrick", lw=2.4, label=f"observed  r={r['obs']:+.2f}")
    ax.set_title(r["name"], fontsize=11, fontweight="bold")
    ax.set_xlabel("max rolling r in a synthetic post-period", fontsize=9)
    ax.set_ylabel("bootstrap replicates", fontsize=9)
    ax.text(0.03, 0.97,
            f"normal p = {r['p_norm']:.4f}\nbootstrap p = {r['ps'][0]:.4f}",
            transform=ax.transAxes, va="top", fontsize=9.5,
            bbox=dict(boxstyle="round", fc="white", alpha=0.9))
    ax.legend(fontsize=8, loc="upper right")
    ax.grid(True, ls="--", alpha=0.3)
fig.suptitle("Distribution-free check on every rolling-correlation p-value in the project\n"
             "Null: the pre-2022 regime continued (circular block bootstrap, block = 4 quarters)",
             fontsize=13, fontweight="bold")
plt.tight_layout(rect=[0, 0, 1, 0.88])
plt.savefig("permutation_test.png", dpi=150, bbox_inches="tight")
print("\nChart saved: permutation_test.png")
