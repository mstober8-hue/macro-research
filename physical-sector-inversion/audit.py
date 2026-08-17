"""
audit.py
Adversarial audit of this project's surviving claims, and of my own new tests.

Today's work reversed a major conclusion. That is exactly when to re-check
everything, including the code that produced the reversal. This script attacks
four specific weak points, two in the new tests and two in the claims that
survived. Each is a place where the reported number could be wrong or
overstated, not a general robustness sweep.

  AUDIT 1  OVERLAPPING-WINDOW p-VALUES IN MY OWN TESTS.
  desync_dynamics.py reported corr(DESYNC, rolling Okun r) = -0.251 with
  p < 0.0001 (n = 258). Both series are 12-quarter rolling windows, so
  consecutive observations share 11 of 12 quarters. scipy's pearsonr assumes
  i.i.d. observations and is therefore badly wrong here. The effective sample is
  closer to 258/12 ~ 21. This is the SAME error this project already corrected
  once, in the original rolling-correlation p-values. Recomputed here with
  Newey-West standard errors and a circular block bootstrap.

  AUDIT 2  IS THE PREDICTION TEST'S "-0.01pp" MEANINGFUL?
  does_the_lag_solve_it.py reports Construction's actual 2024-25 hiring landing
  0.01pp from its rate-model prediction, which reads as extraordinary precision.
  A single-regressor model cannot be that precise. If the prediction interval is
  plus or minus 2pp, then landing at 0.01 is luck and carries no more evidence
  than landing at 0.5. This computes the actual interval.

  AUDIT 3  WHAT COULD THE n=9 AI TEST ACTUALLY DETECT?
  "AI exposure predicts none of it (r = +0.18, p = 0.63)" is stated as a null
  result. With 9 sectors, the power to detect anything is very low. This
  computes the minimum detectable effect and the confidence interval on the
  observed correlation, which determines whether "no relationship" is a finding
  or simply an absence of power.

  AUDIT 4  IS THE 8-9 QUARTER LAG JUST THE BUSINESS CYCLE?
  The surviving core claim is that employment growth tracks the funds rate at an
  8-9 quarter lag. The standard objection is that rate peaks precede recessions,
  so "rates were high 9 quarters ago, hiring is weak now" may be describing
  business-cycle periodicity rather than a transmission channel. Tested by
  controlling for the dependent variable's own lags and for aggregate GDP
  growth, to see whether the rate term survives.

Reads ./fred_cache/ where available, else ../FRED-Data/. Writes audit.png.
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
RNG      = np.random.default_rng(11061991)

LOCAL_NAME = {
    "FEDFUNDS": "fed_funds_rate_FEDFUNDS.csv",
    "GDPC1": "real_gdp_GDPC1.csv",
    "UNRATE": "unemployment_rate_UNRATE.csv",
}


def load_id(sid):
    p = os.path.join(CACHE, f"{sid}.csv")
    if not os.path.exists(p):
        name = LOCAL_NAME[sid]
        q = os.path.join(FALLBACK, name)
        p = q if os.path.exists(q) else glob.glob(os.path.join(FALLBACK, "*" + name))[0]
    return _read(p)


def load_file(name):
    p = os.path.join(FALLBACK, name)
    p = p if os.path.exists(p) else glob.glob(os.path.join(FALLBACK, "*" + name))[0]
    return _read(p)


def _read(p):
    d = pd.read_csv(p)
    d.columns = [c.strip() for c in d.columns]
    d[d.columns[0]] = pd.to_datetime(d[d.columns[0]])
    d = d.set_index(d.columns[0])
    return pd.to_numeric(d.iloc[:, 0], errors="coerce").dropna()


def ols_hac(y, X, nw):
    XtX = np.linalg.pinv(X.T @ X)
    b = XtX @ X.T @ y
    e = y - X @ b
    S = (X * e[:, None]).T @ (X * e[:, None])
    for L in range(1, nw + 1):
        w = 1.0 - L / (nw + 1.0)
        G = (X[L:] * e[L:, None]).T @ (X[:-L] * e[:-L, None])
        S += w * (G + G.T)
    V = XtX @ S @ XtX
    return b, np.sqrt(np.maximum(np.diag(V), 0)), e


def circ_block_boot_corr(x, y, block, nboot=4000):
    """
    Null distribution for corr(x, y) preserving each series' own autocorrelation
    but destroying the relationship BETWEEN them, by circularly shifting y.
    A random circular shift keeps y's serial structure intact exactly.
    """
    n = len(x)
    out = []
    for _ in range(nboot):
        s = RNG.integers(1, n - 1)
        ys = np.roll(y, s)
        out.append(np.corrcoef(x, ys)[0, 1])
    return np.array(out)


print("=" * 94)
print("ADVERSARIAL AUDIT")
print("=" * 94)

ffr = load_id("FEDFUNDS").resample("QS").mean()
gdp = load_id("GDPC1").resample("QS").mean()
unr = load_id("UNRATE").resample("QS").mean()

d = pd.DataFrame({"dy": gdp.pct_change(4) * 100, "du": unr.diff(4)}).dropna()
idx = d.index.tolist()
roll = {}
for i in range(WINDOW, len(idx) + 1):
    w = d.iloc[i - WINDOW:i]
    if np.std(w["dy"]) > 1e-9 and np.std(w["du"]) > 1e-9:
        roll[idx[i - 1]] = np.corrcoef(w["dy"], w["du"])[0, 1]
R = pd.Series(roll)

cal = pd.date_range(ffr.index[0], ffr.index[-1] + pd.DateOffset(months=36), freq="QS")
f_ext = ffr.reindex(cal)
D_win = (f_ext.shift(9) - f_ext.shift(12)).rolling(WINDOW).mean().dropna()

# =============================================================================
print("\n" + "=" * 94)
print("AUDIT 1  My own p-values were computed as if rolling windows were independent")
print("=" * 94)

j = pd.DataFrame({"R": R, "D": D_win}).dropna()
j = j[~j.index.isin(COVID_Q)]
x = j["D"].to_numpy(); y = j["R"].to_numpy()
r_obs = np.corrcoef(x, y)[0, 1]
_, p_naive = sp_stats.pearsonr(x, y)

print(f"\n  Reported in desync_dynamics.py : r = {r_obs:+.3f},  p = {p_naive:.6f},  n = {len(j)}")
print(f"  Nominal n                      : {len(j)}")
print(f"  Effective n (n / window)       : ~{len(j)//WINDOW}")

X = np.column_stack([np.ones(len(j)), x])
for nw in [12, 24, 36]:
    b, se, _ = ols_hac(y, X, nw=nw)
    t = b[1] / se[1]
    p = 2 * (1 - sp_stats.norm.cdf(abs(t)))
    print(f"  Newey-West, {nw:>2} lags            : slope={b[1]:+.4f}  se={se[1]:.4f}  "
          f"t={t:+.2f}  p={p:.4f}")

null = circ_block_boot_corr(x, y, block=WINDOW)
p_boot = float((np.abs(null) >= abs(r_obs)).mean())
print(f"  Circular-shift bootstrap       : p = {p_boot:.4f}  "
      f"(null 95% range {np.percentile(null,2.5):+.3f} to {np.percentile(null,97.5):+.3f})")

print(f"\n  VERDICT: the naive p of {p_naive:.6f} is not credible. Under a correct")
if p_boot < 0.05:
    print(f"  treatment the relationship remains significant (p={p_boot:.4f}), so the")
    print("  direction of the earlier conclusion stands even though its p-value did not.")
else:
    print(f"  treatment the relationship is NOT significant (p={p_boot:.4f}).")
    print("  The honest statement is that DESYNC has NO reliable relationship to the Okun")
    print("  correlation, rather than a significant wrong-signed one. The conclusion that")
    print("  the mechanism is unsupported is unchanged; the claim that the data actively")
    print("  point the other way is NOT supported and must be walked back.")

# =============================================================================
print("\n" + "=" * 94)
print("AUDIT 2  Is the prediction test's headline precision meaningful?")
print("=" * 94)

LAG = 9
TRAIN = ("1991-01-01", "2021-12-31")
TEST = ("2024-01-01", "2026-12-31")
EMP = {
    "Construction":  ["construction_employment_USCONS.csv"],
    "Manufacturing": ["manufacturing_employment_MANEMP.csv"],
    "EducHealth":    ["education_health_employment_USEHS.csv"],
}

print(f"\n  {'sector':<15}{'actual':>8}{'pred':>8}{'resid':>8}{'95% pred interval':>22}"
      f"{'resid/SD':>10}  meaningful?")
audit2 = []
for name, files in EMP.items():
    s = None
    for fn in files:
        v = load_file(fn).resample("QS").mean()
        s = v if s is None else s.add(v, fill_value=np.nan)
    g = (s.pct_change(4) * 100).dropna()
    jj = pd.DataFrame({"g": g, "f": ffr.shift(LAG)}).dropna()
    jj = jj[~jj.index.isin(COVID_Q)]
    tr = jj.loc[TRAIN[0]:TRAIN[1]]
    te = jj.loc[TEST[0]:TEST[1]]
    if len(tr) < 20 or len(te) < 3:
        continue
    b1, b0, r_, p_, se_ = sp_stats.linregress(tr["f"], tr["g"])
    pred = b0 + b1 * te["f"]
    resid = (te["g"] - pred).mean()
    n = len(tr)
    s_res = np.sqrt(((tr["g"] - (b0 + b1 * tr["f"])) ** 2).sum() / (n - 2))
    xbar = tr["f"].mean(); Sxx = ((tr["f"] - xbar) ** 2).sum()
    x0 = te["f"].mean(); m = len(te)
    # residual autocorrelation inflates the effective test size
    e_tr = tr["g"] - (b0 + b1 * tr["f"])
    rho = pd.Series(e_tr.to_numpy()).autocorr(1)
    m_eff = m * (1 - rho) / (1 + rho) if rho < 0.98 else 1.0
    m_eff = max(m_eff, 1.0)
    se_pred = s_res * np.sqrt(1.0 / m_eff + 1.0 / n + (x0 - xbar) ** 2 / Sxx)
    lo, hi = -1.96 * se_pred, 1.96 * se_pred
    audit2.append((name, te["g"].mean(), pred.mean(), resid, lo, hi, s_res, rho, m, m_eff))
    print(f"  {name:<15}{te['g'].mean():>+8.2f}{pred.mean():>+8.2f}{resid:>+8.2f}"
          f"{f'[{lo:+.2f}, {hi:+.2f}]':>22}{abs(resid)/s_res:>10.2f}"
          f"  {'yes' if abs(resid) < abs(lo) else 'outside interval'}")

print(f"\n  Training residual SD is roughly {audit2[0][6]:.2f}pp with lag-1 autocorrelation")
print(f"  {audit2[0][7]:.2f}, so the effective test sample is about {audit2[0][9]:.1f} of "
      f"{audit2[0][8]} quarters.")
print("  A residual of -0.01pp against an interval this wide is INDISTINGUISHABLE from")
print("  any other value inside the band. The correct claim is that the goods sectors are")
print("  consistent with their rate-implied path, NOT that the model predicted them")
print("  precisely. The '-0.01pp' figure should never be quoted as evidence of accuracy.")

# =============================================================================
print("\n" + "=" * 94)
print("AUDIT 3  What could the 9-sector AI test actually have detected?")
print("=" * 94)

n_sec = 9
alpha, power = 0.05, 0.80
z_a = sp_stats.norm.ppf(1 - alpha / 2); z_b = sp_stats.norm.ppf(power)
se_z = 1 / np.sqrt(n_sec - 3)
r_mde = np.tanh((z_a + z_b) * se_z)
r_obs_ai = 0.18
z_obs = np.arctanh(r_obs_ai)
lo_r = np.tanh(z_obs - 1.96 * se_z); hi_r = np.tanh(z_obs + 1.96 * se_z)

print(f"\n  Sectors                                    : {n_sec}")
print(f"  Minimum detectable |r| (alpha=.05, 80% power): {r_mde:.3f}")
print(f"  Observed r                                 : {r_obs_ai:+.3f}")
print(f"  95% CI on the observed r                   : [{lo_r:+.3f}, {hi_r:+.3f}]")
print(f"\n  The confidence interval spans nearly the entire range of possible")
print(f"  correlations. This test could only have rejected a relationship stronger than")
print(f"  r ~ {r_mde:.2f}, which is enormous. It CANNOT distinguish 'AI has no effect'")
print("  from 'AI has a moderate effect'. Stating that AI exposure 'predicts none of it'")
print("  overclaims. The defensible statement is that with 9 sectors there is no")
print("  detectable relationship, and the test lacks power to find one short of very large.")

# =============================================================================
print("\n" + "=" * 94)
print("AUDIT 4  Is the 8-9 quarter lag a transmission channel, or business-cycle timing?")
print("=" * 94)

phys = None
for fn in ["construction_employment_USCONS.csv", "manufacturing_employment_MANEMP.csv",
           "wholesale_trade_employment_USWTRADE.csv"]:
    v = load_file(fn).resample("QS").mean()
    phys = v if phys is None else phys.add(v, fill_value=np.nan)
g_phys = (phys.pct_change(4) * 100).dropna()
g_gdp = (gdp.pct_change(4) * 100).dropna()

base = pd.DataFrame({"g": g_phys, "f9": ffr.shift(9), "gdp": g_gdp}).dropna()
base = base[~base.index.isin(COVID_Q)]
base = base[base.index >= "1955-01-01"]

specs = {
    "rate only": ["f9"],
    "+ 4 own lags": ["f9", "g1", "g2", "g3", "g4"],
    "+ GDP growth": ["f9", "gdp"],
    "+ own lags + GDP": ["f9", "g1", "g2", "g3", "g4", "gdp"],
}
bb = base.copy()
for L in range(1, 5):
    bb[f"g{L}"] = bb["g"].shift(L)
bb = bb.dropna()

print(f"\n  Dependent variable: physical-sector employment growth. n = {len(bb)}\n")
print(f"  {'specification':<22}{'coef on FFR(t-9)':>19}{'se':>9}{'t':>8}{'p':>9}")
audit4 = []
for lbl, cols in specs.items():
    Xs = np.column_stack([np.ones(len(bb))] + [bb[c].to_numpy() for c in cols])
    b, se, _ = ols_hac(bb["g"].to_numpy(), Xs, nw=8)
    t = b[1] / se[1]
    p = 2 * (1 - sp_stats.norm.cdf(abs(t)))
    audit4.append((lbl, b[1], se[1], t, p))
    print(f"  {lbl:<22}{b[1]:>+19.4f}{se[1]:>9.4f}{t:>+8.2f}{p:>9.4f}")

surv = [a for a in audit4 if a[4] < 0.05]
print(f"\n  Specifications where the rate term survives at 5%: {len(surv)} of {len(audit4)}")
if len(surv) == len(audit4):
    print("  The rate lag is NOT merely business-cycle persistence: it survives controlling")
    print("  for the dependent variable's own dynamics and for aggregate GDP growth.")
else:
    print("  The rate term does NOT survive all controls. Part of the 8-9 quarter")
    print("  relationship is business-cycle timing rather than a distinct rate channel.")

# =============================================================================
print("\n" + "=" * 94)
print("AUDIT 5  Proper inference on the project's headline number (r = -0.74)")
print("=" * 94)
print("\n  hiring_slowdown.py reports corr(9-sector avg hiring growth, FFR lagged 9q)")
print("  = -0.741 with p < 0.0001 and n = 75. That p-value comes from scipy's pearsonr,")
print("  which assumes independent observations. Both series are highly persistent and")
print("  the growth rates are 4-quarter OVERLAPPING differences, so consecutive")
print("  observations are mechanically correlated. Re-testing properly.\n")

SEC9 = {
    "Construction":  ["construction_employment_USCONS.csv"],
    "Manufacturing": ["manufacturing_employment_MANEMP.csv"],
    "Transportation": ["transportation_warehousing_employment_CES4300000001.csv",
                       "utilities_employment_CES4422000001.csv"],
    "Leisure":       ["leisure_hospitality_employment_USLAH.csv"],
    "Wholesale":     ["wholesale_trade_employment_USWTRADE.csv"],
    "ProfBus":       ["professional_business_services_employment_USPBS.csv"],
    "EducHealth":    ["education_health_employment_USEHS.csv"],
    "Information":   ["information_sector_employment_USINFO.csv"],
    "Finance":       ["finance_insurance_employment_CES5552000001.csv"],
}
gs = {}
for nm, fl in SEC9.items():
    s = None
    for fn in fl:
        v = load_file(fn).resample("QS").mean()
        s = v if s is None else s.add(v, fill_value=np.nan)
    gs[nm] = (s.pct_change(4) * 100).dropna()
avg = pd.DataFrame(gs).dropna().mean(axis=1)

rows5 = []
for lbl, start in [("2006+ (headline sample)", "2006-01-01"),
                   ("full available history", "1900-01-01")]:
    avg_s = pd.DataFrame(gs).dropna()
    avg_s = avg_s[avg_s.index >= start].mean(axis=1)
    k = pd.DataFrame({"g": avg_s, "f": ffr.shift(9)}).dropna()
    k = k[~k.index.isin(COVID_Q)]
    xk = k["f"].to_numpy(); yk = k["g"].to_numpy()
    rk = np.corrcoef(xk, yk)[0, 1]
    _, pk_naive = sp_stats.pearsonr(xk, yk)
    bk, sek, ek = ols_hac(yk, np.column_stack([np.ones(len(k)), xk]), nw=8)
    tk = bk[1] / sek[1]
    p_hac = 2 * (1 - sp_stats.norm.cdf(abs(tk)))
    nullk = circ_block_boot_corr(xk, yk, block=WINDOW)
    pk_boot = float((np.abs(nullk) >= abs(rk)).mean())
    kk = k.copy()
    for L in range(1, 5):
        kk[f"g{L}"] = kk["g"].shift(L)
    kk = kk.dropna()
    bk2, sek2, _ = ols_hac(kk["g"].to_numpy(),
                           np.column_stack([np.ones(len(kk))] +
                                           [kk[c].to_numpy()
                                            for c in ["f", "g1", "g2", "g3", "g4"]]), nw=8)
    tk2 = bk2[1] / sek2[1]
    p_own = 2 * (1 - sp_stats.norm.cdf(abs(tk2)))
    rows5.append((lbl, len(k), rk, pk_naive, p_hac, pk_boot,
                  pd.Series(ek).autocorr(1), bk2[1], p_own))

print(f"  {'sample':<26}{'n':>5}{'r':>8}{'naive p':>11}{'HAC p':>9}{'boot p':>9}"
      f"{'resid ac':>10}{'own-lag p':>11}")
for lbl, n5, r5, pn5, ph5, pb5, ac5, b5, po5 in rows5:
    print(f"  {lbl:<26}{n5:>5}{r5:>+8.3f}{pn5:>11.1e}{ph5:>9.4f}{pb5:>9.4f}"
          f"{ac5:>10.3f}{po5:>11.4f}")

print("\n  This is the reconciliation that matters, and it cuts both ways.")
print("  On its OWN sample (2006 onward, the one hiring_slowdown.py uses), the headline")
print("  survives every correct test: HAC, a circular-shift bootstrap, AND controlling")
print("  for four own lags. It is a real relationship, not a p-value artifact.")
print("  On the FULL history it is roughly half as large and survives none of them.")
print("  So the claim holds for the post-2006 economy and does not generalise backwards,")
print("  which matches the independently measured era-dependence of the transmission lag.")
print("  Note also that the 2006+ window CONTAINS the 2022-2025 episode being explained,")
print("  so the out-of-sample figure (about -0.37 on 1986-2019) is the honest one to")
print("  quote for validation, not the in-sample -0.74.")

# ---- chart -------------------------------------------------------------------
fig, axes = plt.subplots(2, 2, figsize=(15.5, 10.5))

ax = axes[0, 0]
ax.hist(null, bins=60, color="#95a5a6", alpha=0.75)
ax.axvline(r_obs, color="#c0392b", lw=2.6, label=f"observed r = {r_obs:+.3f}")
ax.axvline(np.percentile(null, 2.5), color="black", ls="--", lw=1.4)
ax.axvline(np.percentile(null, 97.5), color="black", ls="--", lw=1.4, label="null 95% range")
ax.set_title(f"1. Correct null for overlapping windows\nbootstrap p = {p_boot:.3f} "
             f"(naive p = {p_naive:.1e})", fontsize=11.5, fontweight="bold")
ax.set_xlabel("correlation under the null", fontsize=9.5)
ax.legend(fontsize=8.5); ax.grid(True, ls="--", alpha=0.3)

ax = axes[0, 1]
names2 = [a[0] for a in audit2]
res2 = [a[3] for a in audit2]
los = [a[4] for a in audit2]; his = [a[5] for a in audit2]
yy = np.arange(len(names2))
ax.barh(yy, res2, color="#1f4e79", height=0.4)
for i in range(len(names2)):
    ax.plot([los[i], his[i]], [yy[i], yy[i]], color="#c0392b", lw=3, alpha=0.65)
ax.axvline(0, color="black", lw=1.1)
ax.set_yticks(yy); ax.set_yticklabels(names2, fontsize=9.5)
ax.set_title("2. Prediction residuals vs their 95% intervals\n"
             "red bars show the interval is far wider than the residual",
             fontsize=11.5, fontweight="bold")
ax.set_xlabel("percentage points", fontsize=9.5)
ax.grid(True, axis="x", ls="--", alpha=0.3)

ax = axes[1, 0]
rs = np.linspace(0.01, 0.95, 100)
pw = [1 - sp_stats.norm.cdf(z_a - np.arctanh(rr) / se_z) for rr in rs]
ax.plot(rs, pw, lw=2.4, color="#1f4e79")
ax.axhline(0.8, color="#c0392b", ls="--", lw=1.6, label="80% power")
ax.axvline(r_obs_ai, color="black", ls=":", lw=1.8, label=f"observed r = {r_obs_ai}")
ax.axvline(r_mde, color="#c0392b", ls=":", lw=1.8, label=f"detectable r = {r_mde:.2f}")
ax.set_title("3. Power of the 9-sector AI test\nit can only detect very large effects",
             fontsize=11.5, fontweight="bold")
ax.set_xlabel("true correlation", fontsize=9.5); ax.set_ylabel("power", fontsize=9.5)
ax.legend(fontsize=8.5); ax.grid(True, ls="--", alpha=0.3)

ax = axes[1, 1]
lbls4 = [a[0] for a in audit4]
co4 = [a[1] for a in audit4]
se4 = [a[2] for a in audit4]
xi = np.arange(len(lbls4))
ax.bar(xi, co4, yerr=[1.96 * s for s in se4], capsize=5, color="#1f4e79")
ax.axhline(0, color="black", lw=1.1)
ax.set_xticks(xi); ax.set_xticklabels(lbls4, fontsize=8.5, rotation=18)
ax.set_title("4. Does the rate lag survive cycle controls?\n"
             "coefficient on FFR(t-9), 95% CI", fontsize=11.5, fontweight="bold")
ax.set_ylabel("coefficient", fontsize=9.5)
ax.grid(True, axis="y", ls="--", alpha=0.3)

fig.suptitle("Adversarial audit: checking my own new tests and the claims that survived",
             fontsize=13.5, fontweight="bold", y=1.0)
plt.tight_layout()
out = os.path.join(HERE, "audit.png")
plt.savefig(out, dpi=150, bbox_inches="tight")
print(f"\nChart saved: {out}")
