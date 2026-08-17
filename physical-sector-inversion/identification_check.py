"""
identification_check.py
Does "unemployment responds to rates FASTER than output" survive better identification?

WHY THIS EXISTS
why_rates_break_okun.py is the mechanism behind this whole sub-project. It claims
that in the goods sectors, unemployment absorbs a rate shock about 9 quarters out
while output absorbs it about 12 quarters out, and that the 2-3 quarter gap is what
makes contemporaneous Okun's Law look broken during a sharp rate move.

That claim has two problems that a referee would raise immediately.

  PROBLEM 1: it contradicts the standard monetary literature. Identified-shock
  work (Christiano-Eichenbaum-Evans style VARs, and the RBA's 2020 survey of US
  and Australian estimates) generally puts the output response at roughly 4-6
  quarters and the unemployment response at roughly 6 quarters, i.e. unemployment
  lagging output or roughly coincident with it. Never leading it by 3 quarters.

  PROBLEM 2: the original estimate is not an impulse response at all. It is
      corr( YoY growth_t , FFR_LEVEL_(t-L) )
  maximized over L. The Fed funds LEVEL is enormously persistent, so this
  correlation is a phase alignment between two slow-moving series, not a causal
  timing estimate. The peak L can be driven by the shape of the rate cycle rather
  than by how fast each variable responds.

So this script re-estimates the same timing three ways, from weakest to strongest
identification, and reports whether the ordering survives:

  SPEC A  corr with the FFR level          (the original; reported for comparison)
  SPEC B  corr with the 4-quarter CHANGE in FFR   (removes the level's persistence)
  SPEC C  local projection on the rate change, controlling for 4 own lags and
          4 lags of the rate change, Newey-West standard errors
              g_(t+h) = a_h + b_h * dFFR_t + controls_t + e_(t+h)
          The horizon h that maximizes |b_h| is the response peak. This is the
          closest thing to an impulse response that this dataset supports.

It also does what the original never did: puts a STANDARD ERROR on the gap.
The 2-3 quarter gap was read off two point estimates with no uncertainty
attached. A moving-block bootstrap here resamples the joint series and re-runs
the whole peak-picking procedure, so the reported interval includes the
peak-selection step itself.

READ THE OUTPUT BEFORE CITING THE MECHANISM. If the ordering flips or the gap's
bootstrap interval covers zero, the timing mechanism is not established and the
write-up must say so.

Reads FRED CSVs from ../FRED-Data/. Writes identification_check.png.
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
START    = "1991-01-01"
MAXLAG   = 16
NLAGS    = 4       # own lags and rate lags used as controls in the local projection
NBOOT    = 2000
# Block length matters and is reported both ways. A block shorter than MAXLAG
# destroys the very dependence the lag scan is trying to measure, so a short
# block would find "no identification" by construction. BLOCKS[1] is longer than
# MAXLAG and preserves the full lag structure inside each block.
BLOCKS   = [8, 24]
RNG      = np.random.default_rng(20260812)

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


# ---------------------------------------------------------------------------
# OLS with Newey-West standard errors. Written out because statsmodels is not a
# dependency of this repo and the HAC correction is not optional here: local
# projections at horizon h have MA(h) errors by construction, so plain OLS
# standard errors are badly understated.
# ---------------------------------------------------------------------------
def ols_hac(y, X, nw_lags):
    n, k = X.shape
    XtX_inv = np.linalg.pinv(X.T @ X)
    beta = XtX_inv @ X.T @ y
    resid = y - X @ beta
    S = (X * resid[:, None]).T @ (X * resid[:, None])
    for L in range(1, nw_lags + 1):
        w = 1.0 - L / (nw_lags + 1.0)          # Bartlett kernel
        G = (X[L:] * resid[L:, None]).T @ (X[:-L] * resid[:-L, None])
        S += w * (G + G.T)
    V = XtX_inv @ S @ XtX_inv
    se = np.sqrt(np.maximum(np.diag(V), 0))
    return beta, se


def build_panel(out_file, unemp_file):
    """YoY output growth, YoY change in the unemployment rate, FFR level and change."""
    y = (load(out_file).pct_change(4) * 100).rename("y")
    u = load(unemp_file).resample("QS").mean().diff(4).rename("u")
    f = load("fed_funds_rate_FEDFUNDS.csv").resample("QS").mean().rename("f")
    d = pd.concat([y, u, f], axis=1)
    d["df"] = d["f"].diff(4)
    d = d[d.index >= START]
    return d


def peak_corr(d, col, rate_col):
    """SPEC A / SPEC B: lag at which |corr(variable, rate at lag L)| is largest."""
    rows = []
    for L in range(MAXLAG + 1):
        j = pd.DataFrame({"x": d[col], "r": d[rate_col].shift(L)}).dropna()
        j = j[~j.index.isin(COVID_Q)]
        if len(j) < 25:
            continue
        r, p = sp_stats.pearsonr(j["r"], j["x"])
        rows.append((L, r, p, len(j)))
    c = pd.DataFrame(rows, columns=["lag", "r", "p", "n"])
    return c, int(c.iloc[c["r"].abs().idxmax()]["lag"])


def local_projection(d, col, hmax=MAXLAG):
    """
    SPEC C. For each horizon h, regress the variable h quarters ahead on the
    current 4-quarter rate change, controlling for NLAGS own lags and NLAGS lags
    of the rate change. Newey-West with h+1 lags.
    """
    rows = []
    for h in range(hmax + 1):
        parts = {"dep": d[col].shift(-h), "shock": d["df"]}
        for L in range(1, NLAGS + 1):
            parts[f"own{L}"] = d[col].shift(L)
            parts[f"df{L}"]  = d["df"].shift(L)
        j = pd.DataFrame(parts).dropna()
        j = j[~j.index.isin(COVID_Q)]
        if len(j) < 30:
            continue
        yv = j["dep"].to_numpy()
        Xv = np.column_stack([np.ones(len(j))] + [j[c].to_numpy()
                                                  for c in j.columns if c != "dep"])
        beta, se = ols_hac(yv, Xv, nw_lags=h + 1)
        b, s = beta[1], se[1]
        t = b / s if s > 0 else np.nan
        rows.append((h, b, s, t, 2 * (1 - sp_stats.norm.cdf(abs(t))), len(j)))
    c = pd.DataFrame(rows, columns=["h", "b", "se", "t", "p", "n"])
    return c, int(c.iloc[c["b"].abs().idxmax()]["h"])


def boot_gap(d, spec, block):
    """
    Moving-block bootstrap on the gap (unemployment peak minus output peak).
    The whole peak-picking procedure is re-run inside each replicate, so the
    interval reflects the uncertainty in choosing a peak, not just in one
    correlation.
    """
    base = d.dropna(subset=["y", "u", "df", "f"])
    base = base[~base.index.isin(COVID_Q)]
    n = len(base)
    if n < 60:
        return np.array([])
    BLOCK = block
    nblocks = int(np.ceil(n / BLOCK))
    gaps = []
    for _ in range(NBOOT):
        starts = RNG.integers(0, n - BLOCK, size=nblocks)
        idx = np.concatenate([np.arange(s, s + BLOCK) for s in starts])[:n]
        b = base.iloc[idx].reset_index(drop=True)
        b.index = pd.date_range("1991-01-01", periods=n, freq="QS")
        try:
            if spec == "level":
                _, ly = peak_corr(b, "y", "f")
                _, lu = peak_corr(b, "u", "f")
            elif spec == "change":
                _, ly = peak_corr(b, "y", "df")
                _, lu = peak_corr(b, "u", "df")
            else:
                _, ly = local_projection(b, "y")
                _, lu = local_projection(b, "u")
            gaps.append(lu - ly)
        except Exception:
            continue
    return np.array(gaps)


print("=" * 92)
print("IDENTIFICATION CHECK: does 'unemployment leads output' survive better identification?")
print("=" * 92)
print(f"\nSample {START} onward, COVID quarters excluded, {NBOOT} bootstrap replicates,")
print(f"moving blocks of {BLOCKS} quarters.\n")
print("Gap = unemployment peak lag minus output peak lag. NEGATIVE means unemployment")
print("responds FIRST, which is what the mechanism requires.\n")

panels, results = {}, []
for name, (of, uf) in SECTORS.items():
    d = build_panel(of, uf)
    panels[name] = d

    cA_y, lA_y = peak_corr(d, "y", "f")
    cA_u, lA_u = peak_corr(d, "u", "f")
    cB_y, lB_y = peak_corr(d, "y", "df")
    cB_u, lB_u = peak_corr(d, "u", "df")
    cC_y, lC_y = local_projection(d, "y")
    cC_u, lC_u = local_projection(d, "u")

    results.append(dict(sector=name,
                        A_y=lA_y, A_u=lA_u, A_gap=lA_u - lA_y,
                        B_y=lB_y, B_u=lB_u, B_gap=lB_u - lB_y,
                        C_y=lC_y, C_u=lC_u, C_gap=lC_u - lC_y,
                        cA_y=cA_y, cA_u=cA_u, cB_y=cB_y, cB_u=cB_u,
                        cC_y=cC_y, cC_u=cC_u))

R = pd.DataFrame(results)

print(f"{'sector':<16}"
      f"{'A: FFR level':>26}{'B: FFR change':>26}{'C: local projection':>28}")
print(f"{'':<16}" + ("".join([f"{'out':>8}{'unemp':>8}{'gap':>10}"] * 3)))
for _, r in R.iterrows():
    print(f"{r.sector:<16}"
          f"{r.A_y:>7}q{r.A_u:>7}q{r.A_gap:>+9}q"
          f"{r.B_y:>7}q{r.B_u:>7}q{r.B_gap:>+9}q"
          f"{r.C_y:>7}q{r.C_u:>7}q{r.C_gap:>+9}q")

print(f"\n{'mean gap':<16}{R.A_gap.mean():>+23.1f}q{R.B_gap.mean():>+25.1f}q"
      f"{R.C_gap.mean():>+27.1f}q")

print("\n" + "-" * 92)
print("IS THE RESPONSE EVEN SIGNIFICANT AT ITS PEAK? (local projection, Newey-West)")
print("-" * 92)
print(f"\n{'sector':<16}{'variable':<14}{'peak h':>8}{'coef':>9}{'t':>8}{'p':>9}"
      f"{'n':>6}   note")
for _, r in R.iterrows():
    for lbl, prof, pk in [("output", r.cC_y, r.C_y), ("unemployment", r.cC_u, r.C_u)]:
        row = prof[prof["h"] == pk].iloc[0]
        note = "AT GRID EDGE: no interior peak" if pk in (0, MAXLAG) else (
            "" if row["p"] < 0.05 else "peak not significant")
        print(f"{r.sector:<16}{lbl:<14}{pk:>7}q{row['b']:>+9.3f}{row['t']:>+8.2f}"
              f"{row['p']:>9.3f}{int(row['n']):>6}   {note}")

print("\n" + "-" * 92)
print("BOOTSTRAP INTERVALS ON THE GAP (the number the original never reported)")
print("-" * 92)
print("\nReported at two block lengths. Block 8 is shorter than the 16-quarter lag grid")
print("and so destroys long-lag dependence by construction; block 24 preserves it.")
print("If the gap is real, the longer block is where it should show up.\n")
boot_store = {}
for block in BLOCKS:
    print(f"  --- moving block = {block} quarters ---")
    print(f"  {'sector':<16}{'spec':<20}{'point':>8}{'2.5%':>8}{'97.5%':>8}"
          f"{'P(gap<0)':>11}   verdict")
    for _, r in R.iterrows():
        for spec, key in [("A: FFR level", "A_gap"), ("B: FFR change", "B_gap"),
                          ("C: local projection", "C_gap")]:
            tag = {"A: FFR level": "level", "B: FFR change": "change",
                   "C: local projection": "lp"}[spec]
            g = boot_gap(panels[r.sector], tag, block)
            if len(g) == 0:
                continue
            lo, hi = np.percentile(g, [2.5, 97.5])
            pneg = float((g < 0).mean())
            if block == BLOCKS[-1]:
                boot_store[(r.sector, spec)] = g
            v = ("supports U-leads-Y" if hi < 0 else
                 "INCONCLUSIVE: interval covers 0" if lo <= 0 <= hi else
                 "CONTRADICTS: Y leads U")
            print(f"  {r.sector:<16}{spec:<20}{r[key]:>+7}q{lo:>+8.1f}{hi:>+8.1f}"
                  f"{pneg:>11.2f}   {v}")
    print()

# ---------------------------------------------------------------------------
# The persistence problem, shown directly rather than asserted.
# ---------------------------------------------------------------------------
ffr = load("fed_funds_rate_FEDFUNDS.csv").resample("QS").mean()
ffr = ffr[ffr.index >= START]
dffr = ffr.diff(4).dropna()
print("\n" + "-" * 92)
print("WHY SPEC A IS WEAK: the FFR level is far too persistent to date a response")
print("-" * 92)
ac_lvl = [ffr.autocorr(L) for L in range(1, 13)]
ac_chg = [dffr.autocorr(L) for L in range(1, 13)]
print(f"\n  autocorrelation of the FFR LEVEL  at lag 4/8/12: "
      f"{ac_lvl[3]:.2f} / {ac_lvl[7]:.2f} / {ac_lvl[11]:.2f}")
print(f"  autocorrelation of the FFR CHANGE at lag 4/8/12: "
      f"{ac_chg[3]:.2f} / {ac_chg[7]:.2f} / {ac_chg[11]:.2f}")
print("\n  A series with autocorrelation near 1 at lag 12 carries almost no information")
print("  about WHICH lag matters. Correlating against it can locate a peak anywhere in")
print("  the cycle. That is why Spec A's peak lags are long and Spec C's are shorter.")

# ---- chart -------------------------------------------------------------------
fig, axes = plt.subplots(2, 3, figsize=(18.5, 10))

for i, (_, r) in enumerate(R.iterrows()):
    # top row: the three specifications' response profiles for this sector
    ax = axes[0, i]
    ax.axhline(0, color="black", lw=1.0, ls="--")
    ax.plot(r.cA_y["lag"], r.cA_y["r"] / r.cA_y["r"].abs().max(),
            color="#1f4e79", lw=1.4, alpha=0.45, ls=":", label="output, Spec A (level)")
    ax.plot(r.cA_u["lag"], r.cA_u["r"] / r.cA_u["r"].abs().max(),
            color="#c0392b", lw=1.4, alpha=0.45, ls=":", label="unemp, Spec A (level)")
    ax.plot(r.cC_y["h"], r.cC_y["b"] / r.cC_y["b"].abs().max(),
            color="#1f4e79", lw=2.6, marker="o", ms=4, label="output, Spec C (LP)")
    ax.plot(r.cC_u["h"], r.cC_u["b"] / r.cC_u["b"].abs().max(),
            color="#c0392b", lw=2.6, marker="s", ms=4, label="unemp, Spec C (LP)")
    ax.axvline(r.C_y, color="#1f4e79", ls="--", lw=1.4)
    ax.axvline(r.C_u, color="#c0392b", ls="--", lw=1.4)
    ax.set_title(f"{r.sector}\nLP peaks: output {r.C_y}q, unemp {r.C_u}q "
                 f"(gap {r.C_gap:+d}q)", fontsize=11, fontweight="bold")
    ax.set_xlabel("quarters after the rate move", fontsize=9.5)
    if i == 0:
        ax.set_ylabel("response, scaled to its own peak", fontsize=9.5)
        ax.legend(fontsize=7.5, loc="lower left")
    ax.grid(True, ls="--", alpha=0.3)

    # bottom row: bootstrap distribution of the gap under each spec
    ax = axes[1, i]
    for spec, col in [("A: FFR level", "#7f8c8d"), ("B: FFR change", "#e67e22"),
                      ("C: local projection", "#2c3e50")]:
        g = boot_store.get((r.sector, spec))
        if g is None or len(g) == 0:
            continue
        ax.hist(g, bins=np.arange(-MAXLAG - 0.5, MAXLAG + 1.5), alpha=0.5,
                color=col, label=f"{spec}  (P(gap<0)={float((g<0).mean()):.2f})")
    ax.axvline(0, color="red", lw=2.0)
    ax.set_xlabel("bootstrapped gap: unemp peak minus output peak (q)", fontsize=9.5)
    if i == 0:
        ax.set_ylabel("bootstrap replicates", fontsize=9.5)
    ax.set_title("Left of the red line = unemployment leads", fontsize=10.5)
    ax.legend(fontsize=7)
    ax.grid(True, axis="y", ls="--", alpha=0.3)

fig.suptitle("Identification check: the 'unemployment leads output' gap under three "
             "specifications, with bootstrap uncertainty on the gap itself",
             fontsize=13.5, fontweight="bold", y=1.0)
plt.tight_layout()
out = os.path.join(HERE, "identification_check.png")
plt.savefig(out, dpi=150, bbox_inches="tight")
print(f"\nChart saved: {out}")
