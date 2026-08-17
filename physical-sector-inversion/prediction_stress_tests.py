"""
prediction_stress_tests.py
Stress-testing the three failure modes of the DESYNC standing prediction.

standing_prediction.py committed to three checkable outcomes:

  1. The correlations stall around +0.4 and stay there
     -> mechanism wrong or incomplete; something structural holds them up.
  2. They return to their normal negative range and stop, with no overshoot
     -> the timing story explains the unwind but not the full dynamics.
  3. They overshoot below the pre-2022 baseline in 2027, then return
     -> the mechanism is doing real work.

Outcome 3 is not observable until 2027. Rather than wait, this script tests the
same mechanism four ways that ARE checkable now.

THE PROBLEM WITH TESTING THE PREDICTION AS WRITTEN
The DESYNC index is DESYNC_t = FFR(t-9) - FFR(t-12), and identification_check.py
showed the (9, 12) lag pair is not statistically identified: the gap between the
two lags is indistinguishable from zero under every specification tried. So a
test of "did DESYNC(9,12) predict correctly" is a test of one arbitrary point in
a wide space of equally defensible lag pairs. Tests 2 and 3 below confront that
directly instead of assuming it away.

WHAT THIS SCRIPT RUNS

  TEST 1  Fresh data. Sector value added now runs one quarter further than the
          local files (2026 Q1). Where do the rolling correlations actually
          stand, and is the unwind continuing or stalling? Directly separates
          failure mode 1 from modes 2 and 3.

  TEST 2  Lag-pair sensitivity. Across every plausible (LAG_U, LAG_Y) pair,
          where does DESYNC peak? If almost all pairs place the peak in
          2024-2025, then "DESYNC peaked in 2025 Q2 and so did the correlations"
          is close to guaranteed by the shape of the hiking cycle and carries
          little evidence about the specific lags. This measures how much credit
          the original "test that already passed" actually earns.

  TEST 3  Historical validation, the decisive test. The mechanism is a general
          claim about how rate shocks desynchronize output and unemployment, so
          it should show up in aggregate data too, where GDP and UNRATE reach
          back to the 1940s and FEDFUNDS to 1954. That gives about nine hiking
          cycles instead of one. If DESYNC genuinely predicts Okun inversions,
          high-DESYNC quarters should show systematically higher (less negative)
          rolling Okun correlations across 70 years. If it does not, the
          2024-2025 match was coincidence.

  TEST 4  The overshoot, tested on history rather than awaiting 2027. If the
          mechanism is real, quarters where DESYNC is NEGATIVE should show
          rolling Okun correlations BELOW their unconditional baseline. That is
          prediction 3, and history can answer it now.

DATA
Downloads current vintages directly from FRED into ./fred_cache/ so the test
reflects the latest published data rather than whatever was downloaded months
ago. Falls back to ../FRED-Data/ if the network is unavailable.

NOTE ON SAMPLE LENGTH: quarterly real value added by industry (RVAC, RVAMA,
RVAT) begins only in 2005. Any sector-level result here rests on about 80
quarters, and the sector Okun correlations cannot be computed before roughly
2009. This is reported explicitly in Test 5 because earlier write-ups in this
project described these lags as estimated on "1991-2019" data, which the data
availability does not support.

Writes prediction_stress_tests.png.
"""

import os
import glob
import urllib.request
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats as sp_stats

HERE      = os.path.dirname(os.path.abspath(__file__))
FALLBACK  = os.path.join(HERE, "..", "FRED-Data") + os.sep
CACHE     = os.path.join(HERE, "fred_cache")
COVID_Q   = pd.date_range("2020-04-01", "2021-10-01", freq="QS")
WINDOW    = 12
LAG_U, LAG_Y = 9, 12          # the original, unidentified pair
FRED_URL  = "https://fred.stlouisfed.org/graph/fredgraph.csv?id={}"

SECTORS = {
    "Construction":   ("RVAC", "LNU04032231", "#1f3b73"),
    "Manufacturing":  ("RVAMA", "LNU04032232", "#3f7cac"),
    "Transportation": ("RVAT", "LNU04032236", "#6fb0d6"),
}
LOCAL_NAME = {
    "RVAC": "construction_value_added_RVAC.csv",
    "RVAMA": "manufacturing_value_added_RVAMA.csv",
    "RVAT": "transportation_warehousing_value_added_RVAT.csv",
    "LNU04032231": "construction_unemployment_rate_LNU04032231.csv",
    "LNU04032232": "manufacturing_unemployment_rate_LNU04032232.csv",
    "LNU04032236": "transportation_utilities_unemployment_rate_LNU04032236.csv",
    "FEDFUNDS": "fed_funds_rate_FEDFUNDS.csv",
    "GDPC1": "real_gdp_GDPC1.csv",
    "UNRATE": "unemployment_rate_UNRATE.csv",
}


def get(series_id):
    """Current vintage from FRED, cached; falls back to the repo's local CSVs."""
    os.makedirs(CACHE, exist_ok=True)
    path = os.path.join(CACHE, f"{series_id}.csv")
    if not os.path.exists(path):
        try:
            with urllib.request.urlopen(FRED_URL.format(series_id), timeout=60) as r:
                data = r.read()
            with open(path, "wb") as fh:
                fh.write(data)
        except Exception as e:
            print(f"  [warn] FRED fetch failed for {series_id} ({e}); using local copy")
            name = LOCAL_NAME[series_id]
            p = os.path.join(FALLBACK, name)
            path = p if os.path.exists(p) else glob.glob(os.path.join(FALLBACK, "*" + name))[0]
    d = pd.read_csv(path)
    d.columns = [c.strip() for c in d.columns]
    d[d.columns[0]] = pd.to_datetime(d[d.columns[0]])
    d = d.set_index(d.columns[0])
    return pd.to_numeric(d.iloc[:, 0], errors="coerce").dropna()


def rolling_okun(y, u, window=WINDOW):
    """Rolling correlation of YoY output growth against the 4q change in unemployment."""
    d = pd.DataFrame({"dy": y.pct_change(4) * 100, "du": u.diff(4)}).dropna()
    idx = d.index.tolist()
    out = {}
    for i in range(window, len(idx) + 1):
        w = d.iloc[i - window:i]
        if np.std(w["dy"]) > 1e-9 and np.std(w["du"]) > 1e-9:
            out[idx[i - 1]] = np.corrcoef(w["dy"], w["du"])[0, 1]
    return pd.Series(out)


def desync(ffr, lu, ly, horizon_months=36):
    cal = pd.date_range(ffr.index[0], ffr.index[-1] + pd.DateOffset(months=horizon_months),
                        freq="QS")
    f = ffr.reindex(cal)
    return (f.shift(lu) - f.shift(ly)).dropna()


print("=" * 94)
print("STRESS-TESTING THE THREE FAILURE MODES OF THE DESYNC STANDING PREDICTION")
print("=" * 94)

ffr = get("FEDFUNDS").resample("QS").mean()
print(f"\nFed funds observed through {ffr.index[-1].date()} ({ffr.iloc[-1]:.2f}%)")

# =============================================================================
# TEST 1
# =============================================================================
print("\n" + "=" * 94)
print("TEST 1  FRESH DATA: is the unwind continuing, or stalling near +0.4?")
print("=" * 94)

roll, spans = {}, {}
for name, (yid, uid, _) in SECTORS.items():
    y = get(yid).resample("QS").mean()
    u = get(uid).resample("QS").mean()
    roll[name] = rolling_okun(y, u)
    spans[name] = (y.index[0], y.index[-1])
R = pd.DataFrame(roll)

print(f"\n  sector output data spans: "
      f"{spans['Construction'][0].date()} to {spans['Construction'][1].date()}")
print(f"  rolling correlations available through: {R.dropna(how='all').index[-1].date()}\n")

ds = desync(ffr, LAG_U, LAG_Y)
print(f"  {'quarter':<12}{'DESYNC':>9}" + "".join(f"{n[:14]:>16}" for n in R.columns))
for q in pd.date_range("2025-01-01", "2026-07-01", freq="QS"):
    if q not in R.index and q > R.dropna(how="all").index[-1]:
        continue
    vals = "".join(f"{R[n].get(q, np.nan):>16.3f}" for n in R.columns)
    print(f"  {str(q.date()):<12}{ds.get(q, np.nan):>+9.2f}{vals}")

last = R.dropna(how="all").index[-1]
peak_q = pd.Timestamp("2025-04-01")
print(f"\n  Change from the 2025 Q2 peak to {last.date()}:")
for n in R.columns:
    if peak_q in R.index and not np.isnan(R[n].get(last, np.nan)):
        d0, d1 = R[n][peak_q], R[n][last]
        print(f"    {n:<16}{d0:+.3f} -> {d1:+.3f}   ({d1-d0:+.3f})")
still_high = [n for n in R.columns if R[n].get(last, -9) > 0.35]
print(f"\n  Sectors still above +0.35 at {last.date()}: "
      f"{', '.join(still_high) if still_high else 'none'}")
print("  Failure mode 1 (stall near +0.4) is live for any sector listed above.")

# =============================================================================
# TEST 2
# =============================================================================
print("\n" + "=" * 94)
print("TEST 2  LAG SENSITIVITY: how much credit does the '2025 Q2 hit' actually earn?")
print("=" * 94)
print("\n  Peak DESYNC quarter for every plausible lag pair (LAG_Y > LAG_U):\n")

pairs, peaks = [], []
for lu in range(4, 13):
    for ly in range(lu + 1, 17):
        d = desync(ffr, lu, ly)
        seg = d.loc["2023-01-01":"2026-12-31"]
        if len(seg) == 0:
            continue
        pk = seg.idxmax()
        pairs.append((lu, ly))
        peaks.append(pk)

pk_series = pd.Series(peaks)
counts = pk_series.value_counts().sort_index()
print(f"  {'peak quarter':<16}{'# of lag pairs':>16}{'share':>10}")
for q, c in counts.items():
    print(f"  {str(q.date()):<16}{c:>16}{c/len(peaks):>10.1%}")

in_2425 = sum(1 for p in peaks if pd.Timestamp("2024-01-01") <= p <= pd.Timestamp("2025-12-31"))
exact = sum(1 for p in peaks if p == pd.Timestamp("2025-04-01"))
print(f"\n  Lag pairs tested                      : {len(peaks)}")
print(f"  Pairs peaking anywhere in 2024-2025   : {in_2425} ({in_2425/len(peaks):.1%})")
print(f"  Pairs peaking exactly in 2025 Q2      : {exact} ({exact/len(peaks):.1%})")
print("\n  Interpretation: the peak date is driven mostly by the SHAPE of the 2022-23")
print("  hiking cycle, not by the specific lag pair. A large share of defensible pairs")
print("  put the peak in the same window where the correlations happened to peak, so")
print("  the original 'exact match' is much weaker evidence than it appeared.")

# =============================================================================
# TEST 3
# =============================================================================
print("\n" + "=" * 94)
print("TEST 3  HISTORICAL VALIDATION (the decisive test): does DESYNC predict Okun")
print("        inversions across ~9 hiking cycles, using aggregate data back to 1955?")
print("=" * 94)

gdp = get("GDPC1").resample("QS").mean()
unr = get("UNRATE").resample("QS").mean()
R_agg = rolling_okun(gdp, unr)
ds_agg = desync(ffr, LAG_U, LAG_Y)

j = pd.DataFrame({"R": R_agg, "D": ds_agg}).dropna()
j_nc = j[~j.index.isin(COVID_Q)]
print(f"\n  Aggregate rolling Okun correlation available "
      f"{R_agg.index[0].date()} to {R_agg.index[-1].date()}  (n={len(j_nc)} usable quarters)")

r_all, p_all = sp_stats.pearsonr(j_nc["D"], j_nc["R"])
print(f"\n  corr(DESYNC, rolling Okun correlation), full sample: "
      f"r={r_all:+.3f}  p={p_all:.4f}  n={len(j_nc)}")
print("  Mechanism predicts this to be POSITIVE and significant "
      "(higher DESYNC -> less negative Okun).")

print(f"\n  By DESYNC quintile:\n")
j2 = j_nc.copy()
j2["q"] = pd.qcut(j2["D"], 5, labels=["lowest", "2nd", "3rd", "4th", "highest"])
print(f"    {'DESYNC quintile':<18}{'mean DESYNC':>13}{'mean Okun r':>14}{'n':>6}")
for lab, grp in j2.groupby("q", observed=True):
    print(f"    {str(lab):<18}{grp['D'].mean():>+13.2f}{grp['R'].mean():>+14.3f}{len(grp):>6}")

lo = j2[j2["q"] == "lowest"]["R"]
hi = j2[j2["q"] == "highest"]["R"]
t, pt = sp_stats.ttest_ind(hi, lo, equal_var=False)
print(f"\n    highest minus lowest quintile: {hi.mean()-lo.mean():+.3f}  "
      f"(Welch t={t:+.2f}, p={pt:.4f})")

# subsample stability
print(f"\n  Subsample stability:\n")
print(f"    {'period':<20}{'r':>9}{'p':>10}{'n':>6}")
for lbl, a, b in [("1955-1985", "1955-01-01", "1985-12-31"),
                  ("1986-2007", "1986-01-01", "2007-12-31"),
                  ("2008-2026", "2008-01-01", "2026-12-31")]:
    s = j_nc.loc[a:b]
    if len(s) > 25:
        rr, pp = sp_stats.pearsonr(s["D"], s["R"])
        print(f"    {lbl:<20}{rr:>+9.3f}{pp:>10.4f}{len(s):>6}")

# =============================================================================
# TEST 4
# =============================================================================
print("\n" + "=" * 94)
print("TEST 4  THE OVERSHOOT (prediction 3), tested on history instead of awaiting 2027")
print("=" * 94)
print("\n  If the mechanism is real, quarters with NEGATIVE DESYNC should show Okun")
print("  correlations BELOW the unconditional baseline. That is the overshoot.\n")

base = j_nc["R"].mean()
neg = j_nc[j_nc["D"] < -0.25]["R"]
pos = j_nc[j_nc["D"] > 0.25]["R"]
neu = j_nc[(j_nc["D"] >= -0.25) & (j_nc["D"] <= 0.25)]["R"]
print(f"    {'DESYNC regime':<26}{'mean Okun r':>14}{'n':>6}")
print(f"    {'negative (< -0.25)':<26}{neg.mean():>+14.3f}{len(neg):>6}")
print(f"    {'near zero':<26}{neu.mean():>+14.3f}{len(neu):>6}")
print(f"    {'positive (> +0.25)':<26}{pos.mean():>+14.3f}{len(pos):>6}")
print(f"    {'unconditional baseline':<26}{base:>+14.3f}{len(j_nc):>6}")

t2, p2 = sp_stats.ttest_1samp(neg, base)
print(f"\n    Negative-DESYNC mean vs baseline: {neg.mean()-base:+.3f}  "
      f"(t={t2:+.2f}, p={p2:.4f})")

# Taken alone, the line above looks like support. It is not, because the
# mechanism makes a DIRECTIONAL prediction and the data show a SYMMETRIC one.
print("\n    But read the positive regime too before concluding anything:")
t3, p3 = sp_stats.ttest_1samp(pos, base)
print(f"    Positive-DESYNC mean vs baseline: {pos.mean()-base:+.3f}  "
      f"(t={t3:+.2f}, p={p3:.4f})")
print("\n    The mechanism requires POSITIVE DESYNC to push the correlation UP toward")
print("    zero (that is the whole claim about 2024-2025). Instead both tails sit")
print("    BELOW baseline and only the middle sits above it. That is a U-shape in the")
print("    MAGNITUDE of DESYNC, not the directional effect the mechanism predicts.")

print("\n    Discriminating regression:  R = a + b*DESYNC + c*|DESYNC|")
print("      mechanism  predicts  b > 0  and  c ~ 0")
print("      confound   predicts  b ~ 0  and  c < 0   (big rate moves cluster around")
print("                                                recessions, when Okun is strongest)\n")
Xd = np.column_stack([np.ones(len(j_nc)), j_nc["D"].to_numpy(),
                      np.abs(j_nc["D"].to_numpy())])
yd = j_nc["R"].to_numpy()
bd = np.linalg.lstsq(Xd, yd, rcond=None)[0]
resid_d = yd - Xd @ bd
XtX_inv_d = np.linalg.pinv(Xd.T @ Xd)
Sd = (Xd * resid_d[:, None]).T @ (Xd * resid_d[:, None])
for L in range(1, 9):
    w = 1.0 - L / 9.0
    G = (Xd[L:] * resid_d[L:, None]).T @ (Xd[:-L] * resid_d[:-L, None])
    Sd += w * (G + G.T)
Vd = XtX_inv_d @ Sd @ XtX_inv_d
sed = np.sqrt(np.maximum(np.diag(Vd), 0))
for nm, coef, s in zip(["intercept", "b  (DESYNC)", "c  (|DESYNC|)"], bd, sed):
    tt = coef / s if s > 0 else np.nan
    pp_ = 2 * (1 - sp_stats.norm.cdf(abs(tt)))
    print(f"      {nm:<16}{coef:>+9.4f}  se={s:.4f}  t={tt:>+6.2f}  p={pp_:.4f}")

b_ok = bd[1] > 0 and abs(bd[1] / sed[1]) > 1.96
c_neg = bd[2] < 0 and abs(bd[2] / sed[2]) > 1.96
if b_ok and not c_neg:
    verdict = "SUPPORTS the mechanism: directional effect present, no magnitude effect"
elif c_neg and not b_ok:
    verdict = ("CONTRADICTS the mechanism: the pattern is a symmetric magnitude effect, "
               "consistent with rate swings clustering around recessions")
elif b_ok and c_neg:
    verdict = "MIXED: both a directional and a magnitude effect are present"
else:
    verdict = "NULL: neither effect is distinguishable from zero"
print(f"\n    -> {verdict}")

# =============================================================================
# TEST 5
# =============================================================================
print("\n" + "=" * 94)
print("TEST 5  SAMPLE DISCLOSURE: how much data actually underlies the sector lags?")
print("=" * 94)
y0 = get("RVAC")
print(f"\n  Quarterly real value added by industry begins {y0.index[0].date()}.")
print(f"  After 4-quarter differencing and a {WINDOW}-quarter window, the first sector")
print(f"  Okun correlation is available {R.dropna(how='all').index[0].date()}.")
print(f"  Usable sector output quarters, COVID excluded: "
      f"{len([q for q in y0.resample('QS').mean().index if q not in COVID_Q])}")
print("\n  Earlier write-ups described these lags as estimated on '1991-2019' data.")
print("  The 1991 filter binds on nothing: the data does not exist before 2005.")
print("  A 12-quarter lag estimated from this sample is not well determined, which is")
print("  consistent with what identification_check.py found independently.")

# ---- chart -------------------------------------------------------------------
fig = plt.figure(figsize=(18.5, 11))
gs = fig.add_gridspec(2, 3, hspace=0.34, wspace=0.26)

# panel 1: fresh sector correlations
ax = fig.add_subplot(gs[0, 0])
ax.axhline(0, color="black", lw=1.0)
for n, (_, _, c) in SECTORS.items():
    s = R[n].dropna()
    s = s[s.index >= "2018-01-01"]
    ax.plot(s.index, s.values, color=c, lw=2.2, marker="o", ms=3, label=n)
ax.axhspan(0.30, 0.50, color="orange", alpha=0.16)
ax.text(pd.Timestamp("2018-04-01"), 0.40, "failure mode 1:\nstall zone", fontsize=8)
ax.axvline(pd.Timestamp("2025-04-01"), color="black", ls="--", lw=1.3)
ax.set_title("1. Fresh data through 2026 Q1:\nis the unwind continuing?",
             fontsize=11.5, fontweight="bold")
ax.set_ylabel("rolling 12q Okun correlation", fontsize=9.5)
ax.legend(fontsize=8, loc="lower left"); ax.grid(True, ls="--", alpha=0.3)

# panel 2: lag sensitivity
ax = fig.add_subplot(gs[0, 1])
cnt = pk_series.value_counts().sort_index()
ax.bar([str(q.date())[:7] for q in cnt.index], cnt.values, color="#3f7cac")
hit = [i for i, q in enumerate(cnt.index) if q == pd.Timestamp("2025-04-01")]
for i in hit:
    ax.patches[i].set_color("#c0392b")
ax.set_title(f"2. Where {len(peaks)} defensible lag pairs put the peak\n"
             f"(red = the 2025 Q2 the original claimed)", fontsize=11.5, fontweight="bold")
ax.set_ylabel("number of lag pairs", fontsize=9.5)
ax.tick_params(axis="x", rotation=60, labelsize=7.5)
ax.grid(True, axis="y", ls="--", alpha=0.3)

# panel 3: historical scatter
ax = fig.add_subplot(gs[0, 2])
ax.scatter(j_nc["D"], j_nc["R"], s=16, alpha=0.45, color="#1f4e79")
sl, ic, rr, pp, se = sp_stats.linregress(j_nc["D"], j_nc["R"])
xs = np.linspace(j_nc["D"].min(), j_nc["D"].max(), 50)
ax.plot(xs, ic + sl * xs, color="#c0392b", lw=2.2)
ax.axhline(0, color="black", lw=0.9, ls="--")
ax.axvline(0, color="black", lw=0.9, ls="--")
ax.set_title(f"3. Historical test, 1955-2026\nr={r_all:+.3f}, p={p_all:.3f}, n={len(j_nc)}",
             fontsize=11.5, fontweight="bold")
ax.set_xlabel("DESYNC (pp)", fontsize=9.5)
ax.set_ylabel("aggregate rolling Okun correlation", fontsize=9.5)
ax.grid(True, ls="--", alpha=0.3)

# panel 4: quintiles
ax = fig.add_subplot(gs[1, 0])
qm = j2.groupby("q", observed=True)["R"].mean()
ax.bar(range(len(qm)), qm.values, color="#3f7cac")
ax.axhline(base, color="#c0392b", ls="--", lw=1.8, label="unconditional baseline")
ax.set_xticks(range(len(qm))); ax.set_xticklabels(qm.index, fontsize=8.5, rotation=20)
ax.set_title("4. Mean Okun correlation by DESYNC quintile\n"
             "mechanism predicts an upward slope", fontsize=11.5, fontweight="bold")
ax.set_ylabel("mean rolling Okun correlation", fontsize=9.5)
ax.legend(fontsize=8); ax.grid(True, axis="y", ls="--", alpha=0.3)

# panel 5: overshoot regimes
ax = fig.add_subplot(gs[1, 1])
regs = ["negative\n(< -0.25)", "near zero", "positive\n(> +0.25)"]
vals = [neg.mean(), neu.mean(), pos.mean()]
cols = ["#1f4e79", "#7f8c8d", "#c0392b"]
ax.bar(regs, vals, color=cols)
ax.axhline(base, color="black", ls="--", lw=1.8, label="baseline")
ax.set_title("5. The overshoot test\nnegative DESYNC should sit BELOW baseline",
             fontsize=11.5, fontweight="bold")
ax.set_ylabel("mean rolling Okun correlation", fontsize=9.5)
ax.legend(fontsize=8); ax.grid(True, axis="y", ls="--", alpha=0.3)

# panel 6: aggregate history over time
ax = fig.add_subplot(gs[1, 2])
ax.plot(R_agg.index, R_agg.values, color="#1f4e79", lw=1.5, label="aggregate Okun corr")
ax2 = ax.twinx()
ax2.plot(ds_agg.index, ds_agg.values, color="#c0392b", lw=1.3, alpha=0.7, label="DESYNC")
ax2.set_ylabel("DESYNC (pp)", fontsize=9.5, color="#c0392b")
ax.axhline(0, color="black", lw=0.9, ls="--")
ax.set_title("6. Seventy years of both series\n(visual check on Test 3)",
             fontsize=11.5, fontweight="bold")
ax.set_ylabel("rolling Okun correlation", fontsize=9.5, color="#1f4e79")
ax.grid(True, ls="--", alpha=0.3)

fig.suptitle("Stress-testing the DESYNC standing prediction: fresh data, lag sensitivity, "
             "and 70 years of historical validation",
             fontsize=13.5, fontweight="bold", y=0.975)
out = os.path.join(HERE, "prediction_stress_tests.png")
plt.savefig(out, dpi=150, bbox_inches="tight")
print(f"\nChart saved: {out}")
