"""
desync_dynamics.py
Re-testing the DESYNC mechanism as a DYNAMIC relationship, not a static one.

WHY THIS EXISTS
prediction_stress_tests.py concluded the DESYNC mechanism has no support in 70
years of data. That conclusion rested on a pooled, contemporaneous, level-on-
level correlation, and three things about that test were unfair to the mechanism.

  ERROR 1  WINDOW MISMATCH. The rolling Okun correlation at quarter t is
  computed over the window [t-11, t]. It is a backward-looking average. The test
  compared it against a POINT value DESYNC_t. The correct comparison is against
  the AVERAGE of DESYNC over the same window the correlation is measured on.

  ERROR 2  IGNORING THE MECHANISM'S OWN SCOPE CONDITION. The mechanism says
  explicitly that when the rate path is flat, the desynchronization "does not
  matter", and that it "matters enormously" only when rates move sharply. Pooling
  in every quiet quarter, where the mechanism predicts nothing, adds noise and
  biases a pooled correlation toward zero. The mechanism should be tested where
  it claims to operate.

  ERROR 3  WRONG LAGS FOR THE WRONG ERA. historical_lag_validation.py found the
  rate-to-hiring transmission lag was about 4 quarters in 1955-1985 and about 9
  in the modern era. The previous test applied the modern (9, 12) pair to the
  whole 70 years, including three decades where the transmission speed was known
  to be roughly twice as fast. Failing with knowingly wrong parameters is not
  evidence against a mechanism.

There is also a conceptual point. The mechanism is a claim about DYNAMICS: as
DESYNC rises the correlation should be pushed up, and as it falls the correlation
should come back down. A contemporaneous correlation of two highly persistent
levels is a weak instrument for detecting that. Changes, leads and lags, and the
shape of the path around episodes are all more sensitive.

WHAT THIS RUNS

  TEST 1  Window-matched levels. Same test as before, but DESYNC averaged over
          the same 12-quarter window the correlation is measured on.

  TEST 2  Dynamics. Does the CHANGE in DESYNC track the CHANGE in the Okun
          correlation? This is what the mechanism actually asserts.

  TEST 3  Lead-lag structure. Does DESYNC LEAD the correlation? A common driver
          arriving on different clocks implies DESYNC should carry predictive
          content for where the correlation goes next, not merely coincide.

  TEST 4  Scope condition. Restrict to quarters where the rate path is actually
          moving (top tercile of |DESYNC|), which is where the mechanism claims
          to operate, and re-run the directional test.

  TEST 5  Era-appropriate lags. Rebuild DESYNC per era using that era's own
          measured transmission speed rather than imposing the modern pair.

  TEST 6  Event study. Align every historical DESYNC surge and average the path
          of the Okun correlation around it. If the mechanism is real, the
          correlation should rise into the surge and fall out of it, a shape a
          pooled correlation can easily miss.

This script is a genuine attempt to give the mechanism its best fair hearing.
Whatever it finds is reported, in either direction.

Reads cached FRED data from ./fred_cache/ (created by prediction_stress_tests.py)
or falls back to ../FRED-Data/. Writes desync_dynamics.png.
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
CACHE    = os.path.join(HERE, "fred_cache")
FALLBACK = os.path.join(HERE, "..", "FRED-Data") + os.sep
COVID_Q  = pd.date_range("2020-04-01", "2021-10-01", freq="QS")
WINDOW   = 12

LOCAL_NAME = {
    "FEDFUNDS": "fed_funds_rate_FEDFUNDS.csv",
    "GDPC1": "real_gdp_GDPC1.csv",
    "UNRATE": "unemployment_rate_UNRATE.csv",
}

# Era transmission speeds measured independently in historical_lag_validation.py.
# LAG_Y is scaled to preserve the modern era's 12/9 output-to-unemployment ratio,
# rather than being chosen to fit anything here.
ERAS = {
    "1955-1985": ("1955-01-01", "1985-12-31", 4,  5),
    "1986-2007": ("1986-01-01", "2007-12-31", 9, 12),
    "2008-2026": ("2008-01-01", "2026-12-31", 9, 12),
}


def load(series_id):
    p = os.path.join(CACHE, f"{series_id}.csv")
    if not os.path.exists(p):
        name = LOCAL_NAME[series_id]
        q = os.path.join(FALLBACK, name)
        p = q if os.path.exists(q) else glob.glob(os.path.join(FALLBACK, "*" + name))[0]
    d = pd.read_csv(p)
    d.columns = [c.strip() for c in d.columns]
    d[d.columns[0]] = pd.to_datetime(d[d.columns[0]])
    d = d.set_index(d.columns[0])
    return pd.to_numeric(d.iloc[:, 0], errors="coerce").dropna()


def ols_hac(y, X, nw):
    n, k = X.shape
    XtX = np.linalg.pinv(X.T @ X)
    b = XtX @ X.T @ y
    e = y - X @ b
    S = (X * e[:, None]).T @ (X * e[:, None])
    for L in range(1, nw + 1):
        w = 1.0 - L / (nw + 1.0)
        G = (X[L:] * e[L:, None]).T @ (X[:-L] * e[:-L, None])
        S += w * (G + G.T)
    V = XtX @ S @ XtX
    return b, np.sqrt(np.maximum(np.diag(V), 0))


def report(nm, b, se, extra=""):
    t = b / se if se > 0 else np.nan
    p = 2 * (1 - sp_stats.norm.cdf(abs(t)))
    star = "  <-- significant" if p < 0.05 else ""
    print(f"    {nm:<34}{b:>+9.4f}  se={se:.4f}  t={t:>+6.2f}  p={p:.4f}{star}{extra}")
    return p


ffr = load("FEDFUNDS").resample("QS").mean()
gdp = load("GDPC1").resample("QS").mean()
unr = load("UNRATE").resample("QS").mean()

d = pd.DataFrame({"dy": gdp.pct_change(4) * 100, "du": unr.diff(4)}).dropna()
idx = d.index.tolist()
roll = {}
for i in range(WINDOW, len(idx) + 1):
    w = d.iloc[i - WINDOW:i]
    if np.std(w["dy"]) > 1e-9 and np.std(w["du"]) > 1e-9:
        roll[idx[i - 1]] = np.corrcoef(w["dy"], w["du"])[0, 1]
R = pd.Series(roll).rename("R")


def build_desync(lu, ly, window_matched=True):
    cal = pd.date_range(ffr.index[0], ffr.index[-1] + pd.DateOffset(months=36), freq="QS")
    f = ffr.reindex(cal)
    ds = (f.shift(lu) - f.shift(ly)).dropna()
    if window_matched:
        ds = ds.rolling(WINDOW).mean().dropna()
    return ds.rename("D")


print("=" * 94)
print("DESYNC AS A DYNAMIC RELATIONSHIP: re-testing with the specification errors fixed")
print("=" * 94)

# =============================================================================
print("\n" + "=" * 94)
print("TEST 1  WINDOW-MATCHED LEVELS (fixes the point-vs-window mismatch)")
print("=" * 94)
D_pt  = build_desync(9, 12, window_matched=False)
D_win = build_desync(9, 12, window_matched=True)

for lbl, D in [("point DESYNC (the old, mismatched test)", D_pt),
               ("window-matched DESYNC (correct)", D_win)]:
    j = pd.DataFrame({"R": R, "D": D}).dropna()
    j = j[~j.index.isin(COVID_Q)]
    r, p = sp_stats.pearsonr(j["D"], j["R"])
    print(f"\n  {lbl}")
    print(f"    corr(DESYNC, Okun r) = {r:+.3f}   p={p:.4f}   n={len(j)}")

# =============================================================================
print("\n" + "=" * 94)
print("TEST 2  DYNAMICS: does the CHANGE in DESYNC track the CHANGE in the correlation?")
print("=" * 94)
j = pd.DataFrame({"R": R, "D": D_win}).dropna()
j = j[~j.index.isin(COVID_Q)]
j["dR"] = j["R"].diff()
j["dD"] = j["D"].diff()
jj = j.dropna()
r2, p2 = sp_stats.pearsonr(jj["dD"], jj["dR"])
print(f"\n  corr(change in DESYNC, change in Okun r) = {r2:+.3f}  p={p2:.4f}  n={len(jj)}")
print("  Mechanism predicts POSITIVE: rising desynchronization pushes the correlation up.\n")
X = np.column_stack([np.ones(len(jj)), jj["dD"].to_numpy()])
b, se = ols_hac(jj["dR"].to_numpy(), X, nw=8)
report("slope on change in DESYNC", b[1], se[1])

# =============================================================================
print("\n" + "=" * 94)
print("TEST 3  LEAD-LAG: does DESYNC LEAD the correlation, or merely coincide?")
print("=" * 94)
print("\n  Positive k means DESYNC leads the Okun correlation by k quarters.\n")
print(f"    {'k':>4}{'corr(levels)':>16}{'corr(changes)':>16}{'n':>7}")
best_k, best_r = None, 0
for k in range(-4, 13):
    Dk = D_win.shift(k)
    jk = pd.DataFrame({"R": R, "D": Dk}).dropna()
    jk = jk[~jk.index.isin(COVID_Q)]
    if len(jk) < 40:
        continue
    rl, _ = sp_stats.pearsonr(jk["D"], jk["R"])
    jk["dR"] = jk["R"].diff(); jk["dD"] = jk["D"].diff()
    jk2 = jk.dropna()
    rc, _ = sp_stats.pearsonr(jk2["dD"], jk2["dR"])
    mark = ""
    if rc > best_r:
        best_r, best_k, mark = rc, k, ""
    print(f"    {k:>4}{rl:>+16.3f}{rc:>+16.3f}{len(jk):>7}")
print(f"\n  Strongest change-on-change relationship at k = {best_k} quarters "
      f"(r = {best_r:+.3f})")

# =============================================================================
print("\n" + "=" * 94)
print("TEST 4  SCOPE CONDITION: test where the mechanism claims to operate")
print("=" * 94)
print("\n  The mechanism says a flat rate path produces no effect. Restricting to")
print("  quarters where the path is actually moving (top tercile of |DESYNC|):\n")
j4 = pd.DataFrame({"R": R, "D": D_win}).dropna()
j4 = j4[~j4.index.isin(COVID_Q)]
thr = j4["D"].abs().quantile(2 / 3)
act = j4[j4["D"].abs() >= thr]
qui = j4[j4["D"].abs() < thr]
print(f"    |DESYNC| threshold (top tercile): {thr:.2f}pp")
for lbl, s in [("active rate path", act), ("quiet rate path", qui)]:
    r4, p4 = sp_stats.pearsonr(s["D"], s["R"])
    print(f"    {lbl:<22}corr = {r4:+.3f}   p={p4:.4f}   n={len(s)}")

print("\n  Directional vs magnitude, restricted to the active subsample:")
Xa = np.column_stack([np.ones(len(act)), act["D"].to_numpy(),
                      np.abs(act["D"].to_numpy())])
ba, sea = ols_hac(act["R"].to_numpy(), Xa, nw=8)
p_dir = report("b  (DESYNC, directional)", ba[1], sea[1])
p_mag = report("c  (|DESYNC|, magnitude)", ba[2], sea[2])

# =============================================================================
print("\n" + "=" * 94)
print("TEST 5  ERA-APPROPRIATE LAGS (the previous test used modern lags on all eras)")
print("=" * 94)
print("\n  Transmission lag per era from historical_lag_validation.py; the output lag")
print("  is scaled to preserve the modern 12/9 ratio, not fitted here.\n")
print(f"    {'era':<14}{'lags':>10}{'corr levels':>14}{'p':>9}"
      f"{'corr changes':>15}{'p':>9}{'n':>6}")
era_rows = []
for lbl, (a, b_, lu, ly) in ERAS.items():
    D_e = build_desync(lu, ly, window_matched=True)
    je = pd.DataFrame({"R": R, "D": D_e}).dropna()
    je = je[~je.index.isin(COVID_Q)].loc[a:b_]
    if len(je) < 30:
        continue
    rl, pl = sp_stats.pearsonr(je["D"], je["R"])
    je["dR"] = je["R"].diff(); je["dD"] = je["D"].diff()
    je2 = je.dropna()
    rc, pc = sp_stats.pearsonr(je2["dD"], je2["dR"])
    era_rows.append((lbl, rl, pl, rc, pc, len(je)))
    print(f"    {lbl:<14}{f'({lu},{ly})':>10}{rl:>+14.3f}{pl:>9.4f}"
          f"{rc:>+15.3f}{pc:>9.4f}{len(je):>6}")

print("\n  Compare against the previous run, which forced (9,12) on every era and got")
print("  +0.180 / -0.083 / +0.602 on levels for these three periods respectively.")

# =============================================================================
print("\n" + "=" * 94)
print("TEST 6  EVENT STUDY: the average path of the Okun correlation around DESYNC surges")
print("=" * 94)

D_ev = build_desync(9, 12, window_matched=True)
je = pd.DataFrame({"R": R, "D": D_ev}).dropna()
thr_ev = je["D"].quantile(0.85)
peaks = []
for i in range(4, len(je) - 4):
    w = je["D"].iloc[i - 4:i + 5]
    if je["D"].iloc[i] == w.max() and je["D"].iloc[i] >= thr_ev:
        if not peaks or (je.index[i] - peaks[-1]).days > 365 * 3:
            peaks.append(je.index[i])
print(f"\n  DESYNC surge episodes identified (local maxima above the 85th percentile,")
print(f"  at least 3 years apart): {len(peaks)}")
for p_ in peaks:
    print(f"    {p_.date()}   DESYNC={je['D'][p_]:+.2f}   Okun r={je['R'][p_]:+.3f}")

H = 8
paths = []
for p_ in peaks:
    i = je.index.get_loc(p_)
    if i - H < 0 or i + H >= len(je):
        continue
    seg = je["R"].iloc[i - H:i + H + 1].to_numpy()
    paths.append(seg - seg[H])          # normalise so the peak quarter is zero
if paths:
    P = np.vstack(paths)
    mean_path = P.mean(axis=0)
    se_path = P.std(axis=0, ddof=1) / np.sqrt(len(P))
    print(f"\n  Average deviation of the Okun correlation, relative to its value at the")
    print(f"  DESYNC peak, across {len(P)} episodes:\n")
    print(f"    {'quarters from peak':>20}{'mean dev':>11}{'se':>8}")
    for h in range(-H, H + 1):
        star = "   <- peak" if h == 0 else ""
        print(f"    {h:>20}{mean_path[h + H]:>+11.3f}{se_path[h + H]:>8.3f}{star}")
    rise = mean_path[H] - mean_path[0]
    fall = mean_path[-1] - mean_path[H]
    print(f"\n    Rise into the peak (t-8 to t=0): {-rise:+.3f}")
    print(f"    Fall out of the peak (t=0 to t+8): {fall:+.3f}")
    print("    Mechanism predicts the correlation rises INTO a DESYNC surge and falls after.")

# ---- chart -------------------------------------------------------------------
fig, axes = plt.subplots(2, 3, figsize=(18.5, 10.5))

ax = axes[0, 0]
for lbl, D, c in [("point (old)", D_pt, "#7f8c8d"), ("window-matched", D_win, "#1f4e79")]:
    jx = pd.DataFrame({"R": R, "D": D}).dropna()
    jx = jx[~jx.index.isin(COVID_Q)]
    ax.scatter(jx["D"], jx["R"], s=12, alpha=0.35, color=c, label=lbl)
    sl, ic, rr, _, _ = sp_stats.linregress(jx["D"], jx["R"])
    xs = np.linspace(jx["D"].min(), jx["D"].max(), 40)
    ax.plot(xs, ic + sl * xs, color=c, lw=2.2)
ax.set_title("1. Window matching the DESYNC measure\nto the correlation window",
             fontsize=11, fontweight="bold")
ax.set_xlabel("DESYNC (pp)", fontsize=9.5); ax.set_ylabel("Okun correlation", fontsize=9.5)
ax.legend(fontsize=8); ax.grid(True, ls="--", alpha=0.3)

ax = axes[0, 1]
ax.scatter(jj["dD"], jj["dR"], s=16, alpha=0.45, color="#c0392b")
sl, ic, rr, _, _ = sp_stats.linregress(jj["dD"], jj["dR"])
xs = np.linspace(jj["dD"].min(), jj["dD"].max(), 40)
ax.plot(xs, ic + sl * xs, color="black", lw=2.2)
ax.axhline(0, color="black", lw=0.8, ls="--"); ax.axvline(0, color="black", lw=0.8, ls="--")
ax.set_title(f"2. Dynamics: changes vs changes\nr={r2:+.3f}, p={p2:.4f}",
             fontsize=11, fontweight="bold")
ax.set_xlabel("change in DESYNC", fontsize=9.5)
ax.set_ylabel("change in Okun correlation", fontsize=9.5)
ax.grid(True, ls="--", alpha=0.3)

ax = axes[0, 2]
ks, rls, rcs = [], [], []
for k in range(-4, 13):
    Dk = D_win.shift(k)
    jk = pd.DataFrame({"R": R, "D": Dk}).dropna()
    jk = jk[~jk.index.isin(COVID_Q)]
    if len(jk) < 40:
        continue
    ks.append(k)
    rls.append(sp_stats.pearsonr(jk["D"], jk["R"])[0])
    jk["dR"] = jk["R"].diff(); jk["dD"] = jk["D"].diff()
    jk2 = jk.dropna()
    rcs.append(sp_stats.pearsonr(jk2["dD"], jk2["dR"])[0])
ax.axhline(0, color="black", lw=0.9, ls="--")
ax.plot(ks, rls, marker="o", lw=2.2, color="#1f4e79", label="levels")
ax.plot(ks, rcs, marker="s", lw=2.2, color="#c0392b", label="changes")
ax.set_title("3. Lead-lag structure\npositive k = DESYNC leads", fontsize=11, fontweight="bold")
ax.set_xlabel("k (quarters DESYNC leads)", fontsize=9.5)
ax.set_ylabel("correlation", fontsize=9.5)
ax.legend(fontsize=8.5); ax.grid(True, ls="--", alpha=0.3)

ax = axes[1, 0]
ax.scatter(qui["D"], qui["R"], s=14, alpha=0.3, color="#95a5a6", label="quiet path")
ax.scatter(act["D"], act["R"], s=22, alpha=0.6, color="#c0392b", label="active path")
sl, ic, rr, _, _ = sp_stats.linregress(act["D"], act["R"])
xs = np.linspace(act["D"].min(), act["D"].max(), 40)
ax.plot(xs, ic + sl * xs, color="black", lw=2.2)
ax.set_title("4. Restricting to an actively moving\nrate path (the mechanism's own scope)",
             fontsize=11, fontweight="bold")
ax.set_xlabel("DESYNC (pp)", fontsize=9.5); ax.set_ylabel("Okun correlation", fontsize=9.5)
ax.legend(fontsize=8); ax.grid(True, ls="--", alpha=0.3)

ax = axes[1, 1]
if era_rows:
    xlab = [e[0] for e in era_rows]
    xi = np.arange(len(xlab)); w = 0.36
    ax.bar(xi - w/2, [e[1] for e in era_rows], w, color="#1f4e79", label="levels")
    ax.bar(xi + w/2, [e[3] for e in era_rows], w, color="#c0392b", label="changes")
    ax.axhline(0, color="black", lw=1.0)
    ax.set_xticks(xi); ax.set_xticklabels(xlab, fontsize=9)
ax.set_title("5. Era-appropriate lags\n(1955-85 uses its own 4q transmission)",
             fontsize=11, fontweight="bold")
ax.set_ylabel("correlation with Okun r", fontsize=9.5)
ax.legend(fontsize=8.5); ax.grid(True, axis="y", ls="--", alpha=0.3)

ax = axes[1, 2]
if paths:
    hs = np.arange(-H, H + 1)
    ax.plot(hs, mean_path, marker="o", lw=2.6, color="#1f4e79")
    ax.fill_between(hs, mean_path - 1.96 * se_path, mean_path + 1.96 * se_path,
                    color="#1f4e79", alpha=0.18)
    ax.axvline(0, color="#c0392b", lw=2.0, ls="--")
    ax.axhline(0, color="black", lw=0.9, ls="--")
ax.set_title(f"6. Event study: path around {len(paths) if paths else 0} DESYNC surges\n"
             "mechanism predicts a hump peaking at 0", fontsize=11, fontweight="bold")
ax.set_xlabel("quarters from DESYNC peak", fontsize=9.5)
ax.set_ylabel("Okun correlation, relative to peak quarter", fontsize=9.5)
ax.grid(True, ls="--", alpha=0.3)

fig.suptitle("Giving the DESYNC mechanism its best fair hearing: window matching, dynamics, "
             "lead-lag, scope conditions, era-specific lags, and an event study",
             fontsize=13, fontweight="bold", y=1.0)
plt.tight_layout()
out = os.path.join(HERE, "desync_dynamics.png")
plt.savefig(out, dpi=150, bbox_inches="tight")
print(f"\nChart saved: {out}")
